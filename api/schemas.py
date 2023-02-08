from pydantic import BaseModel, Field, EmailStr
from typing import Optional

##################
#   DEFINE BaseModels
##################
class CreateService(BaseModel):
    service_name: str
    pager_duty_link: str
    team_id: str

class CreateTeam(BaseModel):
    team_name: str
    operator_group: str
    admin_group: str
    slack_channel: str
    
class Service(BaseModel):
    id: str = ""
    service_name: str = ""
    pager_duty_link: str = ""
    team_id: Optional[str] = ""

class Team(BaseModel):
    id: str = ""
    team_name: str = ""
    operator_group: str = ""
    admin_group: str = ""
    slack_channel: str = ""

class CreateModel(BaseModel):
    id: str = "none"
    success: bool = True
    description: str = ""

class ServiceNoID(BaseModel):
    service_name: str = ""
    pager_duty_link: str = ""
    team_id: Optional[str] = ""
