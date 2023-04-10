from pydantic import BaseModel, Field, EmailStr
from typing import Union, Set, List
from uuid import UUID


##################
#   DEFINE BaseModels
##################

class CreateService(BaseModel):
    name: str
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
    team_id: Union[str, None] = None
    add_tag: List[str] = list()
    delete_tag: List[str] = list()

class PagerdutyIntegration(BaseModel):
    pager_duty_org: str
    api_key: str
    admin_email: str

class Service(BaseModel):
    id: str = ""
    name: str = ""
    pager_duty_link: str = ""
    team_id = ""
    tags: Set[str] = set()

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

class Upsert(BaseModel):
    success: bool = True

############################
#  Auth Schemas
############################
class ServiceAccount(BaseModel):
    id: str = ""
    accountName: str = ""
    hashedPass: str = ""
    role: list = []

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    
class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
    role: list = None

class CreateServiceAccount(BaseModel):
    accountName: str = ""
    password: str = ""
    role: list = []