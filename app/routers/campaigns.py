import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.database.db_manager import DatabaseManager
from app.models.schemas import (
    CampaignMetrics,
    CampaignScheduleRequest,
    CampaignScheduleResponse,
    CustomerResult,
)
from app.services.campaign_service import CampaignService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["campaigns"])


def get_campaign_service() -> CampaignService:
    db_manager = DatabaseManager()
    return CampaignService(db_manager)


# ------------------------------------------------------------------ #
# Endpoints
# ------------------------------------------------------------------ #


@router.post(
    "/campaigns/schedule",
    response_model=CampaignScheduleResponse,
    status_code=201,
    summary="Schedule a new email campaign",
    description="Schedule an email campaign for a list of customers. "
    "Metrics are calculated immediately (simulated).",
)
def schedule_campaign(
    request: CampaignScheduleRequest,
    service: CampaignService = Depends(get_campaign_service),
) -> CampaignScheduleResponse:
    if not request.customer_ids:
        raise HTTPException(status_code=400, detail="customer_ids must not be empty")
    if not request.subject.strip():
        raise HTTPException(status_code=400, detail="subject must not be empty")
    if not request.body.strip():
        raise HTTPException(status_code=400, detail="body must not be empty")

    logger.info("Scheduling campaign for %d customers", len(request.customer_ids))
    return service.schedule_campaign(request)


@router.get(
    "/campaigns/{campaign_id}/metrics",
    response_model=CampaignMetrics,
    summary="Get campaign performance metrics",
    description="Retrieve aggregated open/click metrics for a campaign",
)
def get_campaign_metrics(
    campaign_id: str,
    service: CampaignService = Depends(get_campaign_service),
) -> CampaignMetrics:
    return service.get_campaign_metrics(campaign_id)


@router.get(
    "/campaigns/{campaign_id}",
    summary="Get campaign details",
    description="Retrieve full campaign object including subject, body, customer list, "
    "scheduled time, and metrics (if available)",
)
def get_campaign_details(
    campaign_id: str,
    service: CampaignService = Depends(get_campaign_service),
) -> dict:
    return service.get_campaign_details(campaign_id)


@router.get(
    "/campaigns/{campaign_id}/results",
    response_model=List[CustomerResult],
    summary="Get individual customer results",
    description="Return per-customer open/click outcomes for debugging and analysis",
)
def get_campaign_results(
    campaign_id: str,
    limit: int = 100,
    service: CampaignService = Depends(get_campaign_service),
) -> List[CustomerResult]:
    campaign = service.db_manager.get_campaign(campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")

    results = service.db_manager.get_campaign_results(campaign_id)
    return results[:limit]
