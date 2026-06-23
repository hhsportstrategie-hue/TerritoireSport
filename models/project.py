from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ProjectStatus(str, Enum):
    idea     = "idea"
    planning = "planning"
    active   = "active"
    done     = "done"

class ClubProjectCreate(BaseModel):
    club_id:    str
    project_id: str
    notes:      Optional[str] = None

class ClubProjectUpdate(BaseModel):
    status: Optional[ProjectStatus] = None
    notes:  Optional[str]           = None

class ClubProjectOut(BaseModel):
    id:         str
    club_id:    str
    project_id: str
    status:     str
    notes:      Optional[str]
    started_at: Optional[str]
    updated_at: str
