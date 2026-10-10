from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    role: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    role: Optional[str] = "USER"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdate(BaseModel):
    college: Optional[str] = None
    graduation_year: Optional[int] = None
    preferred_language: Optional[str] = "cpp"
    programming_experience: Optional[str] = "INTERMEDIATE"
    cp_experience: Optional[str] = "BEGINNER"
    daily_available_hours: Optional[float] = 2.0
    preferred_study_time: Optional[str] = "EVENING"
    target_competition: Optional[str] = "TCS CodeVita"
    target_date: Optional[datetime] = None
    skill_level: Optional[str] = "BEGINNER"
    preparation_goal: Optional[str] = "Crack CodeVita Round 1 & 2"
    onboarding_completed: Optional[bool] = None
    diagnostic_completed: Optional[bool] = None

class ProfileResponse(BaseModel):
    id: str
    user_id: str
    college: Optional[str] = None
    graduation_year: Optional[int] = None
    preferred_language: str
    programming_experience: str
    cp_experience: str
    daily_available_hours: float
    preferred_study_time: str
    target_competition: str
    target_date: Optional[datetime] = None
    skill_level: str
    preparation_goal: str
    onboarding_completed: bool
    diagnostic_completed: bool

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    xp: int
    level: int
    created_at: datetime
    profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True
