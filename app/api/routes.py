from fastapi import FastAPI
from functools import lru_cache
import uuid
from fastapi_pagination import Page, add_pagination, paginate

from api.config import Settings
from api.datastore import Mongodb
from api.schemas import CreateService, Service, CreateTeam, Team, GetService, GetTeam, CreateModel
from fastapi.encoders import jsonable_encoder

app = FastAPI()

set = Settings()


##########################
#       Core Routes
##########################

@app.post('/create_service', response_model=CreateModel)
async def create_service(service:CreateService):
    pass
    # cm = CreateModel()

    # #Generate UUID for service
    # id = str(uuid.uuid4().hex)
    # service.__dict__.update({"service_id" : id})

    # # Store Service Data
    # ds = Dynamodb()
    # response_mod = ds.store_service(service.__dict__, response_model=cm)

    # return response_mod

@app.post('/create_team',response_model=CreateModel)
async def create_team(requested_team:CreateTeam):
    cm = CreateModel()
    team = Team.parse_obj(requested_team)
    team.__dict__.update({"id" : str(uuid.uuid4().hex)})

    # Store Team Data
    client = Mongodb()
    response_mod = await client.create_team(jsonable_encoder(team),response_model=cm)
    
    return response_mod

@app.get("/get_team",response_model=Team)
async def get_team(team_data: GetTeam):
    t = Team()
    team_data = jsonable_encoder(team_data)

    # Get Team Data
    client = Mongodb()
    response_mod = await client.get_team(team_id=team_data["id"],team_name=team_data["name"],response_model=t)

    return response_mod

@app.get("/get_service",response_model=Service)
async def get_service(service_data: GetService ):
    pass
    # query_params = service_data.dict()
    # service=Service()
    # ds = Dynamodb()
    # return ds.get_service(query_params, response_model=service)
    

@app.get("/delete_service",response_model=Service)
async def delete_service(service_data: GetService ):
    pass

@app.get("/delete_team",response_model=Service)
async def delete_team(service_data: GetService ):
    pass