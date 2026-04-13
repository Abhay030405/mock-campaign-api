import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.database.db_manager import DatabaseManager
from app.models.schemas import Customer
from app.services.customer_service import CustomerService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["customers"])


def get_customer_service() -> CustomerService:
    db_manager = DatabaseManager()
    return CustomerService(db_manager)


# ------------------------------------------------------------------ #
# Request / Response helpers
# ------------------------------------------------------------------ #


class ValidateIdsRequest(BaseModel):
    customer_ids: List[str]


class ValidateIdsResponse(BaseModel):
    valid: bool
    invalid_ids: List[str]


class CustomerCountResponse(BaseModel):
    total_customers: int


# ------------------------------------------------------------------ #
# Endpoints
# ------------------------------------------------------------------ #


@router.get(
    "/customers/count",
    response_model=CustomerCountResponse,
    summary="Get customer count",
    description="Return total number of customers in the cohort",
)
def get_customer_count(
    service: CustomerService = Depends(get_customer_service),
) -> CustomerCountResponse:
    return CustomerCountResponse(total_customers=service.get_customer_count())


@router.get(
    "/customers/{customer_id}",
    response_model=Customer,
    summary="Get customer by ID",
    description="Retrieve a single customer by their customer_id",
)
def get_customer_by_id(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service),
) -> Customer:
    customer = service.db_manager.get_customer_by_id(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return customer


@router.get(
    "/customers",
    response_model=List[Customer],
    summary="Get customer cohort",
    description="List all customers with optional pagination",
)
def get_all_customers(
    limit: int = 5000,
    offset: int = 0,
    service: CustomerService = Depends(get_customer_service),
) -> List[Customer]:
    customers = service.get_all_customers()
    return customers[offset : offset + limit]


@router.post(
    "/customers/validate",
    response_model=ValidateIdsResponse,
    summary="Validate customer IDs",
    description="Check whether all provided customer IDs exist in the database",
)
def validate_customer_ids(
    body: ValidateIdsRequest,
    service: CustomerService = Depends(get_customer_service),
) -> ValidateIdsResponse:
    invalid_ids: List[str] = []
    for cid in body.customer_ids:
        if service.db_manager.get_customer_by_id(cid) is None:
            invalid_ids.append(cid)
    return ValidateIdsResponse(valid=len(invalid_ids) == 0, invalid_ids=invalid_ids)
