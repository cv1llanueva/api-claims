from pydantic import BaseModel, constr
from datetime import date, datetime 
from typing import Optional

class Policy(BaseModel):
    policyNumber: str
    policyType: str
    startDate: date
    endDate: date
    premiumAmount: float

class PolicyInput(BaseModel):
    policyNumber: str
    policyType: str
    startDate: date
    endDate: date
    premiumAmount: float

class ClaimInput(BaseModel):
    policy: PolicyInput
    accidentDate: date
    description: str
    lossAmount: float
    isFiledByCustomer: bool

class ClaimOutput(BaseModel):
    claimNumber: str
    policy: Policy
    accidentDate: date
    description: str
    lossAmount: float
    isFiledByCustomer: bool
    claimDate: datetime