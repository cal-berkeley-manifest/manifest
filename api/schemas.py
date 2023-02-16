from pydantic import BaseModel, Field, EmailStr
from typing import Optional

##################
#   DEFINE BaseModels
##################
class CreateService(BaseModel):
    name: str
    pager_duty_link: str
    team_id: str

class CreateTeam(BaseModel):
    name: str
    operator_group: str
    admin_group: str
    slack_channel: str
    
class Service(BaseModel):
    id: str = ""
    name: str = ""
    pager_duty_link: str = ""
    team_id = ""

class Team(BaseModel):
    id: str = ""
    name: str = ""
    operator_group: str = ""
    admin_group: str = ""
    slack_channel: str = ""

class CreateModel(BaseModel):
    id: str = "none"
    success: bool = True
    description: str = ""

class DeleteModel(BaseModel):
    id: str = ""
    success: bool = True
    description: str = ""