import logging
from typing import Dict, List, Optional

from app.database.db_manager import DatabaseManager
from app.models.schemas import Customer

logger = logging.getLogger(__name__)


class CustomerService:
    """Customer-related business operations."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager
        self.db_manager.load_customers()
        logger.info("CustomerService initialized")

    def get_all_customers(self) -> List[Customer]:
        return self.db_manager.load_customers()

    def get_customers_by_ids(self, customer_ids: List[str]) -> List[Customer]:
        customers: List[Customer] = []
        missing: List[str] = []

        for cid in customer_ids:
            customer = self.db_manager.get_customer_by_id(cid)
            if customer is None:
                missing.append(cid)
            else:
                customers.append(customer)

        if missing:
            raise ValueError(f"Customer IDs not found: {missing}")

        return customers

    def filter_customers(self, filters: Dict) -> List[Customer]:
        results = self.get_all_customers()

        age_min: Optional[int] = filters.get("Age_min")
        age_max: Optional[int] = filters.get("Age_max")
        gender: Optional[str] = filters.get("Gender")
        city: Optional[str] = filters.get("City")
        occupation_type: Optional[str] = filters.get("Occupation_type")
        app_installed: Optional[str] = filters.get("App_Installed")
        social_media: Optional[str] = filters.get("Social_Media_Active")

        if age_min is not None:
            results = [c for c in results if c.Age >= age_min]
        if age_max is not None:
            results = [c for c in results if c.Age <= age_max]
        if gender is not None:
            results = [c for c in results if c.Gender == gender]
        if city is not None:
            results = [c for c in results if c.City == city]
        if occupation_type is not None:
            results = [c for c in results if c.Occupation_type == occupation_type]
        if app_installed is not None:
            results = [c for c in results if c.App_Installed == app_installed]
        if social_media is not None:
            results = [c for c in results if c.Social_Media_Active == social_media]

        logger.info("Filtered customers: %d matches", len(results))
        return results

    def get_customer_count(self) -> int:
        return len(self.get_all_customers())
