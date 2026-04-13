import logging
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException

from app.database.db_manager import DatabaseManager
from app.models.schemas import (
    CampaignMetrics,
    CampaignScheduleRequest,
    CampaignScheduleResponse,
    CustomerResult,
)
from app.services.customer_service import CustomerService
from app.services.metrics_calculator import MetricsCalculator

logger = logging.getLogger(__name__)


class CampaignService:
    """Campaign scheduling, metrics retrieval, and detail lookup."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager
        self.customer_service = CustomerService(db_manager)
        self.metrics_calculator = MetricsCalculator()

    # ------------------------------------------------------------------ #
    # Schedule
    # ------------------------------------------------------------------ #

    def schedule_campaign(
        self, request: CampaignScheduleRequest
    ) -> CampaignScheduleResponse:
        # Validate customer IDs
        try:
            self.customer_service.get_customers_by_ids(request.customer_ids)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        campaign_id = str(uuid4())

        campaign_data = {
            "campaign_id": campaign_id,
            "subject": request.subject,
            "body": request.body,
            "customer_ids": request.customer_ids,
            "scheduled_time": request.scheduled_time.isoformat(),
            "segment_name": request.segment_name,
            "variant_id": request.variant_id,
            "campaign_metadata": request.campaign_metadata,
            "created_at": datetime.utcnow().isoformat(),
            "status": "scheduled",
        }

        self.db_manager.save_campaign(campaign_data)
        logger.info("Campaign %s scheduled with %d customers", campaign_id, len(request.customer_ids))

        # Simulate instant results for the hackathon
        self.metrics_calculator.calculate_campaign_metrics(
            campaign_id=campaign_id,
            customer_ids=request.customer_ids,
            subject=request.subject,
            body=request.body,
            scheduled_time=request.scheduled_time,
            db_manager=self.db_manager,
        )

        return CampaignScheduleResponse(
            campaign_id=campaign_id,
            status="scheduled",
            total_customers=len(request.customer_ids),
            scheduled_time=request.scheduled_time,
            message=f"Campaign scheduled successfully. Metrics available at /api/campaigns/{campaign_id}/metrics",
        )

    # ------------------------------------------------------------------ #
    # Metrics
    # ------------------------------------------------------------------ #

    def get_campaign_metrics(self, campaign_id: str) -> CampaignMetrics:
        campaign = self.db_manager.get_campaign(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")

        results = self.db_manager.get_campaign_results(campaign_id)

        if not results:
            # Recalculate if results are missing
            logger.warning("No results for campaign %s — recalculating", campaign_id)
            return self.metrics_calculator.calculate_campaign_metrics(
                campaign_id=campaign_id,
                customer_ids=campaign["customer_ids"],
                subject=campaign["subject"],
                body=campaign["body"],
                scheduled_time=datetime.fromisoformat(campaign["scheduled_time"]),
                db_manager=self.db_manager,
            )

        total_sent = len(campaign["customer_ids"])
        unique_opens = sum(1 for r in results if r.opened)
        unique_clicks = sum(1 for r in results if r.clicked)
        open_rate = unique_opens / total_sent if total_sent > 0 else 0.0
        click_rate = unique_clicks / total_sent if total_sent > 0 else 0.0
        ctr = unique_clicks / unique_opens if unique_opens > 0 else 0.0

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

    # ------------------------------------------------------------------ #
    # Details
    # ------------------------------------------------------------------ #

    def get_campaign_details(self, campaign_id: str) -> dict:
        campaign = self.db_manager.get_campaign(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")

        # Attach metrics if results exist
        results = self.db_manager.get_campaign_results(campaign_id)
        if results:
            total_sent = len(campaign.get("customer_ids", []))
            unique_opens = sum(1 for r in results if r.opened)
            unique_clicks = sum(1 for r in results if r.clicked)
            campaign["metrics"] = {
                "total_sent": total_sent,
                "unique_opens": unique_opens,
                "unique_clicks": unique_clicks,
                "open_rate": round(unique_opens / total_sent, 4) if total_sent else 0,
                "click_rate": round(unique_clicks / total_sent, 4) if total_sent else 0,
                "click_through_rate": round(unique_clicks / unique_opens, 4) if unique_opens else 0,
            }

        return campaign
