from pydantic import BaseModel, Field, EmailStr
from typing import Union

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

class UpdateTeam(BaseModel):
    name: Union[str, None] = None
    operator_group: Union[str, None] = None
    admin_group: Union[str, None] = None
    slack_channel: Union[str, None] = None

class UpdateService(BaseModel):
    name: Union[str, None] = None
    pager_duty_link: Union[str, None] = None
    team_id: Union[str, None] = None
    
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

class UpdateModel(BaseModel):
    id: str= ""
    success: bool = True
    description: str = ""