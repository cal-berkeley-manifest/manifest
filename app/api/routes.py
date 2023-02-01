from fastapi import FastAPI
from functools import lru_cache
import uuid
from fastapi_pagination import Page, add_pagination, paginate

from api.config import Settings
from api.datastore import Dynamodb
from api.schemas import CreateService, Service, CreateTeam, Team, GetService, GetTeam, CreateModel

app = FastAPI()

set = Settings()


##########################
#       Core Routes
##########################

@app.post('/create_service', response_model=CreateModel)
async def create_service(service:CreateService):
    cm = CreateModel()

    #Generate UUID for service
    id = str(uuid.uuid4().hex)
    service.__dict__.update({"service_id" : id})

    # Store Service Data
    ds = Dynamodb()
    response_mod = ds.store_service(service.__dict__, response_model=cm)

    return response_mod

@app.post('/create_team',response_model=CreateModel)
async def create_team(team:CreateTeam):
    cm = CreateModel()

    #Generate UUID for team
    id = str(uuid.uuid4().hex)
    team.__dict__.update({"team_id" : id})

    # Store Team Data
    ds = Dynamodb()
    response_mod = ds.store_team(team.__dict__, response_model=cm)

    return response_mod

@app.get("/get_team",response_model=Team)
async def get_team(team_data: GetTeam):
    query_params = team_data.dict()
    team=Team()
    ds = Dynamodb()
    return ds.get_team(query_params, response_model=team)

@app.get("/get_service",response_model=Service)
async def get_service(service_data: GetService ):
    query_params = service_data.dict()
    service=Service()
    ds = Dynamodb()
    return ds.get_service(query_params, response_model=service)

@app.get("/delete_service",response_model=Service)
async def delete_service(service_data: GetService ):
    pass

@app.get("/delete_team",response_model=Service)
async def delete_team(service_data: GetService ):
    pass