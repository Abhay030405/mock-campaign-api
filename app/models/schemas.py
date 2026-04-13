from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class Customer(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str
    Full_name: str
    email: str
    Age: int
    Gender: str
    Marital_Status: str
    Family_Size: int
    Dependent_count: int = Field(alias="Dependent count")
    Occupation: str
    Occupation_type: str = Field(alias="Occupation type")
    Monthly_Income: int
    KYC_status: str = Field(alias="KYC status")
    City: str
    Kids_in_Household: int
    App_Installed: str
    Existing_Customer: str = Field(alias="Existing Customer")
    Credit_score: int = Field(alias="Credit score")
    Social_Media_Active: str


class CampaignScheduleRequest(BaseModel):
    customer_ids: List[str]
    subject: str = Field(max_length=200)
    body: str = Field(max_length=5000)
    scheduled_time: datetime
    segment_name: Optional[str] = None
    variant_id: Optional[str] = None
    campaign_metadata: Optional[dict] = None


class CampaignScheduleResponse(BaseModel):
    campaign_id: str = Field(default_factory=lambda: str(uuid4()))
    status: str = "scheduled"
    total_customers: int
    scheduled_time: datetime
    message: str


class CampaignMetrics(BaseModel):
    campaign_id: str
    total_sent: int
    unique_opens: int
    unique_clicks: int
    open_rate: float = Field(ge=0.0, le=1.0)
    click_rate: float = Field(ge=0.0, le=1.0)
    click_through_rate: float = Field(ge=0.0, description="clicks / opens")
    calculated_at: datetime


class CustomerResult(BaseModel):
    campaign_id: str
    customer_id: str
    opened: bool
    clicked: bool
    open_probability: float
    click_probability: float
