import json
import logging
from pathlib import Path
from threading import Lock
from typing import List, Optional

import pandas as pd

from app.models.schemas import Customer, CustomerResult

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
CUSTOMERS_CSV = BASE_DIR / "customers.csv"
CAMPAIGNS_JSON = BASE_DIR / "campaigns.json"
RESULTS_JSON = BASE_DIR / "results.json"


class DatabaseManager:
    _instance: Optional["DatabaseManager"] = None
    _lock = Lock()

    def __new__(cls) -> "DatabaseManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._customers_cache: Optional[List[Customer]] = None
        self._file_lock = Lock()
        logger.info("DatabaseManager initialized")

    # ------------------------------------------------------------------
    # JSON helpers
    # ------------------------------------------------------------------

    def initialize_json_files(self) -> None:
        """Create campaigns.json and results.json with empty lists if missing."""
        for path in (CAMPAIGNS_JSON, RESULTS_JSON):
            if not path.exists():
                self._write_json(path, [])
                logger.info("Created %s", path.name)

    @staticmethod
    def _read_json(path: Path) -> list:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("Could not read %s – returning empty list", path)
            return []

    def _write_json(self, path: Path, data: list) -> None:
        tmp = path.with_suffix(".tmp")
        with self._file_lock:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            tmp.replace(path)

    # ------------------------------------------------------------------
    # Customers (CSV)
    # ------------------------------------------------------------------

    def load_customers(self) -> List[Customer]:
        if self._customers_cache is not None:
            return self._customers_cache

        try:
            df = pd.read_csv(CUSTOMERS_CSV)
            logger.info("Loaded %d rows from customers.csv", len(df))
        except FileNotFoundError:
            logger.error("customers.csv not found at %s", CUSTOMERS_CSV)
            self._customers_cache = []
            return self._customers_cache

        customers: List[Customer] = []
        for _, row in df.iterrows():
            try:
                customers.append(Customer.model_validate(row.to_dict()))
            except Exception as exc:
                logger.warning("Skipping invalid row: %s", exc)

        self._customers_cache = customers
        return self._customers_cache

    def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        for customer in self.load_customers():
            if customer.customer_id == customer_id:
                return customer
        return None

    # ------------------------------------------------------------------
    # Campaigns (JSON)
    # ------------------------------------------------------------------

    def save_campaign(self, campaign_data: dict) -> str:
        campaigns = self._read_json(CAMPAIGNS_JSON)
        campaigns.append(campaign_data)
        self._write_json(CAMPAIGNS_JSON, campaigns)
        campaign_id = campaign_data.get("campaign_id", "")
        logger.info("Saved campaign %s", campaign_id)
        return campaign_id

    def get_campaign(self, campaign_id: str) -> Optional[dict]:
        for campaign in self._read_json(CAMPAIGNS_JSON):
            if campaign.get("campaign_id") == campaign_id:
                return campaign
        return None

    # ------------------------------------------------------------------
    # Results (JSON)
    # ------------------------------------------------------------------

    def save_campaign_results(self, results: List[CustomerResult]) -> None:
        existing = self._read_json(RESULTS_JSON)
        existing.extend([r.model_dump() for r in results])
        self._write_json(RESULTS_JSON, existing)
        logger.info("Saved %d campaign results", len(results))

    def get_campaign_results(self, campaign_id: str) -> List[CustomerResult]:
        all_results = self._read_json(RESULTS_JSON)
        return [
            CustomerResult.model_validate(r)
            for r in all_results
            if r.get("campaign_id") == campaign_id
        ]
