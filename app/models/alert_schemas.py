from pydantic import BaseModel
from typing import Optional, Dict, Generic, TypeVar, List
from datetime import datetime

T = TypeVar("T")

class AlertRuleOut(BaseModel):
    id: int
    name: str
    promql: str
    condition: str
    level: str
    suppress: Optional[str]
    repeat: int
    enabled: bool
    notify_template_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True
        from_attributes = True

class AlertNotifyTemplateOut(BaseModel):
    id: int
    name: str
    type: str
    params: Dict
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True
        from_attributes = True

class AlertHistoryOut(BaseModel):
    id: int
    rule_id: int
    status: str
    message: str
    notified: bool
    notified_at: Optional[datetime]
    created_at: datetime
    class Config:
        orm_mode = True
        from_attributes = True

class CommonResponse(BaseModel, Generic[T]):
    code: int
    data: Optional[T]
    msg: str
    class Config:
        from_attributes = True