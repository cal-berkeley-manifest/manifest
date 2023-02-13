from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from functools import lru_cache
from uuid import uuid4
from fastapi_pagination import Page, add_pagination, paginate
from api.config import Settings
from api.datastore import Mongodb
from api.schemas import CreateService, Service, CreateTeam, Team, CreateModel, ServiceNoID
from fastapi.encoders import jsonable_encoder

app = FastAPI()
set = Settings()

##########################
#       Core Routes
##########################

@app.get("/list_services", response_model=List[ServiceNoID])
async def list_services():
    client = Mongodb()
    response_mod = await client.list_services()
    return response_mod

@app.post("/create_service", response_model=CreateModel)
async def create_service(requested_service: CreateService):
    cm = CreateModel()
    service = Service.parse_obj(requested_service)
    service.__dict__.update(
        {
            "id": str(uuid4().hex)
        }
    )
    
    client = Mongodb()
    response_mod = await client.create_service(
        jsonable_encoder(service),
        response_model = cm
    )

    if response_mod.success == True:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(response_mod)
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, 
            content=jsonable_encoder(response_mod)
        )

@app.post('/create_team',response_model=CreateModel)
async def create_team(requested_team: CreateTeam):
    cm = CreateModel()
    team = Team.parse_obj(requested_team)
    team.__dict__.update(
        {
            "id": str(uuid4().hex)
        }
    )

    # Store Team Data
    client = Mongodb()
    response_mod = await client.create_team(jsonable_encoder(team),response_model=cm)
    
    if response_mod.success == True:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(response_mod)
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, 
            content=jsonable_encoder(response_mod)
        )

@app.get("/get_team", response_model=Team)
async def get_team(id: str=None, team_name: str=None):
    #t = GetModel
    team_data = {
        "id": id,
        "team_name": team_name
    }

    # Get Team Data
    client = Mongodb()
    response_mod = await client.get_team(
        team_id=team_data["id"],
        team_name=team_data["team_name"],
        response_model=Team
    )

    if response_mod:
        return response_mod
    raise HTTPException(status_code=404, detail=f"Team not found")

@app.get("/get_service", response_model=Service)
async def get_service(id: str=None, service_name: str=None):
    service_data = {
        "id": id,
        "service_name": service_name
    }

    client = Mongodb()
    response_mod = await client.get_service(
        service_id=service_data["id"],
        service_name=service_data["service_name"],
        response_model=Service
    )

    if response_mod:
        return response_mod
    raise HTTPException(status_code=404, detail=f"Service not found")

'''
@app.get("/delete_service",response_model=Service)
async def delete_service(service_data: GetService ):
    pass

@app.get("/delete_team",response_model=Service)
async def delete_team(service_data: GetService ):
    pass
'''