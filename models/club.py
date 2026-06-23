from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from enum import Enum

class ClubSize(str, Enum):
    micro  = "micro"    # < 50 licenciés
    small  = "small"    # 50-200
    medium = "medium"   # 200-500
    large  = "large"    # 500+

class ClubCreate(BaseModel):
    name:          str
    email:         str
    password:      str
    sport:         str
    city:          str
    department:    str
    region:        str = "Normandie"
    size:          ClubSize
    members_count: int = 0
    description:   Optional[str] = None
    website:       Optional[str] = None

class ClubUpdate(BaseModel):
    name:          Optional[str]         = None
    sport:         Optional[str]         = None
    city:          Optional[str]         = None
    department:    Optional[str]         = None
    size:          Optional[ClubSize]    = None
    members_count: Optional[int]         = None
    description:   Optional[str]         = None
    website:       Optional[str]         = None

class ClubOut(BaseModel):
    id:            str
    name:          str
    email:         str
    sport:         str
    city:          str
    department:    str
    region:        str
    size:          str
    members_count: int
    description:   Optional[str]
    website:       Optional[str]
    created_at:    str

class ClubLogin(BaseModel):
    email:    str
    password: str
