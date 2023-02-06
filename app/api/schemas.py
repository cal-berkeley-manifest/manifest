from pydantic import BaseModel, Field, EmailStr
import uuid
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

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
    id: str = ""
    operator_group: str = ""
    admin_group: str = ""
    slack_channel: str = ""

class GetService(BaseModel):
    id: str = "none"
    name: str = "none"

class GetTeam(BaseModel):
    id: str = ""
    name: str = ""

class CreateModel(BaseModel):
    id: str = "none"
    success: bool = True
    description: str = ""

class GetModel(BaseModel):
    id: str = "none"
    success: bool = True
    description: str = ""

class ServiceModel(BaseModel):
    id: PyObjectId = Field (default_factory=PyObjectId, alias="_id")
    service_name: str = Field(...)
    pager_duty_link: str = Field(...)
    team_id: str = Field(...)
    description: str = Field(...)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "service_name": "ExampleService",
                "pager_duty_link": "https://exampleservicepagerlink.com",
                "team_id": "team_id string here.",
                "description": "Example service description here.",
            }
        }

