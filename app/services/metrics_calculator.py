import logging
import random
from datetime import datetime
from typing import List

from app.database.db_manager import DatabaseManager
from app.models.schemas import CampaignMetrics, CustomerResult
from app.utils.content_analyzer import ContentAnalyzer
from app.utils.probability_calculator import ProbabilityCalculator

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Simulates campaign metrics by combining content, timing, and customer data."""

    def __init__(self) -> None:
        self.content_analyzer = ContentAnalyzer()
        self.prob_calculator = ProbabilityCalculator()

    def calculate_campaign_metrics(
        self,
        campaign_id: str,
        customer_ids: List[str],
        subject: str,
        body: str,
        scheduled_time: datetime,
        db_manager: DatabaseManager,
    ) -> CampaignMetrics:
        # Analyze content & timing
        subject_modifiers = self.content_analyzer.analyze_subject_line(subject)
        body_modifiers = self.content_analyzer.analyze_body_content(body)
        timing_modifiers = self.content_analyzer.analyze_timing(scheduled_time)

        # Merge subject + body into a single content_modifiers dict
        content_modifiers = {**subject_modifiers, **body_modifiers}

        results: List[CustomerResult] = []

        for cid in customer_ids:
            customer = db_manager.get_customer_by_id(cid)
            if customer is None:
                logger.warning("Customer %s not found – skipping", cid)
                continue

            probs = self.prob_calculator.calculate_customer_probabilities(
                customer, content_modifiers, timing_modifiers
            )

            opened = random.random() < probs["open_probability"]
            clicked = opened and (random.random() < probs["click_probability"])

            results.append(
                CustomerResult(
                    campaign_id=campaign_id,
                    customer_id=cid,
                    opened=opened,
                    clicked=clicked,
                    open_probability=round(probs["open_probability"], 4),
                    click_probability=round(probs["click_probability"], 4),
                )
            )

        # Persist results
        db_manager.save_campaign_results(results)

        # Aggregate metrics
        total_sent = len(customer_ids)
        unique_opens = sum(1 for r in results if r.opened)
        unique_clicks = sum(1 for r in results if r.clicked)
        open_rate = unique_opens / total_sent if total_sent > 0 else 0.0
        click_rate = unique_clicks / total_sent if total_sent > 0 else 0.0
        ctr = unique_clicks / unique_opens if unique_opens > 0 else 0.0

        logger.info(
            "Campaign %s — sent=%d opens=%d clicks=%d open_rate=%.2f click_rate=%.2f ctr=%.2f",
            campaign_id,
            total_sent,
            unique_opens,
            unique_clicks,
            open_rate,
            click_rate,
            ctr,
        )

        return CampaignMetrics(
            campaign_id=campaign_id,
            total_sent=total_sent,
            unique_opens=unique_opens,
            unique_clicks=unique_clicks,
            open_rate=round(open_rate, 4),
            click_rate=round(click_rate, 4),
            click_through_rate=round(ctr, 4),
            calculated_at=datetime.utcnow(),
        )
