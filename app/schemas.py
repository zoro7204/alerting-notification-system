from pydantic import BaseModel, EmailStr
from typing import List, Optional
import datetime

# Visibility Schemas
class AlertVisibilityBase(BaseModel):
    visibility_type: str
    ref_id: Optional[int] = None

class AlertVisibilityCreate(AlertVisibilityBase):
    pass

class AlertVisibility(AlertVisibilityBase):
    id: int
    alert_id: int

    class Config:
        from_attributes = True

# Alert Schemas
class AlertBase(BaseModel):
    title: str
    message: str
    severity: str
    reminders_enabled: bool = True
    start_time: Optional[datetime.datetime] = None
    expiry_time: Optional[datetime.datetime] = None

class AlertCreate(AlertBase):
    visibility: List[AlertVisibilityCreate]

class AlertUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[str] = None
    reminders_enabled: Optional[bool] = None
    expiry_time: Optional[datetime.datetime] = None
    archived: Optional[bool] = None    

class Alert(AlertBase):
    id: int
    archived: bool
    visibility: List[AlertVisibility] = []

    class Config:
        from_attributes = True

# Team Schemas
class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    id: int

    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    team_id: Optional[int] = None

class User(UserBase):
    id: int
    team_id: Optional[int] = None

    class Config:
        from_attributes = True

# UserAlertPreference Schemas
class UserAlertPreference(BaseModel):
    state: str
    snoozed_until: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class UserAlert(Alert):
    user_state: str = "UNREAD"
    snoozed_until: Optional[datetime.datetime] = None

class TriggerResponse(BaseModel):
    status: str
    message: str            