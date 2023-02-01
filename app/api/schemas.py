from pydantic import BaseModel

##################
#   DEFINE BaseModels
##################
class CreateService(BaseModel):
    service_name: str
    pager_duty_link: str
    team_id: str


class Service(BaseModel):
    service_id: str = ""
    service_name: str = ""
    pager_duty_link: str = ""
    team_id: str = ""
    success: bool  = True
    description: str = ""


class CreateTeam(BaseModel):
    team_name: str
    operator_group: str
    admin_group: str
    slack_channel: str
    

class Team(BaseModel):
    team_name: str = ""
    team_id: str = ""
    operator_group: str = ""
    admin_group: str = ""
    slack_channel: str = ""
    success: bool  = True
    description: str = ""


class GetService(BaseModel):
    id: str = "none"
    name: str = "none"

class GetTeam(BaseModel):
    id: str = "none"
    name: str = "none"

class CreateModel(BaseModel):
    id: str = "none"
    success: bool = True
    description: str = ""

class GetModel(BaseModel):
    id: str = "none"
    success: bool = True
    description: str = ""