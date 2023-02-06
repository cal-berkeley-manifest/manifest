from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Optional, List
from functools import lru_cache
import uuid
from fastapi_pagination import Page, add_pagination, paginate

from app.api.config import Settings
from app.api.datastore import Mongodb
from app.api.schemas import ServiceModel, CreateTeam, Team, GetTeam, CreateModel
from fastapi.encoders import jsonable_encoder

app = FastAPI()
set = Settings()

##########################
#       Core Routes
##########################

@app.post("/create_service", response_description="Add new service", response_model=ServiceModel)
async def create_service(service: ServiceModel = Body(...)):
    service = jsonable_encoder(service)
    new_service = await Mongodb.db2["services"].insert_one(service)
    created_service = await Mongodb.db2["services"].find_one({"_id": new_service.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_service)

@app.get("/get_service", response_description="Get a single service", response_model=ServiceModel)
async def get_service(id: str):
    if (service := await Mongodb.db2["services"].find_one({"_id": id})) is not None:
        return service
    raise HTTPException(status_code=404, detail=f"Service {id} not found")
    
@app.get("/services", response_description="List all services", response_model=List[ServiceModel])
async def list_services():
    services = await Mongodb.db2["services"].find().to_list(1000)
    return services

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


'''
@app.get("/delete_service",response_model=Service)
async def delete_service(service_data: GetService ):
    pass

@app.get("/delete_team",response_model=Service)
async def delete_team(service_data: GetService ):
    pass
'''