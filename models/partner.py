from pydantic import BaseModel
from typing import Optional, List

class PartnerCreate(BaseModel):
    name:          str
    type:          str   # 'public' | 'association' | 'company'
    category:      str
    city:          Optional[str] = None
    department:    Optional[str] = None
    contact_email: Optional[str] = None
    contact_url:   Optional[str] = None
    description:   Optional[str] = None
    themes:        List[str]     = []

class PartnerOut(BaseModel):
    id:            str
    name:          str
    type:          str
    category:      str
    city:          Optional[str]
    department:    Optional[str]
    contact_email: Optional[str]
    contact_url:   Optional[str]
    description:   Optional[str]
    themes:        List[str]
