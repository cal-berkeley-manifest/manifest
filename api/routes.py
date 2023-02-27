from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Union
from functools import lru_cache
from uuid import uuid4
from fastapi_pagination import Page, add_pagination, paginate
from api.config import Settings
from api.datastore import Mongodb
from api.schemas import *
from fastapi.encoders import jsonable_encoder

app = FastAPI()
set = Settings()

##########################
#       Core Routes
##########################

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
async def get_team(id: str=None, name: str=None):
    #t = GetModel
    team_data = {
        "id": id,
        "name": name
    }

    # Get Team Data
    client = Mongodb()
    response_mod = await client.get_team(
        id=team_data["id"],
        name=team_data["name"],
        response_model=Team
    )

    if response_mod:
        return response_mod
    raise HTTPException(status_code=404, detail=f"Team not found")

@app.get("/get_service", response_model=Service)
async def get_service(id: str=None, name: str=None):
    service_data = {
        "id": id,
        "name": name
    }

    client = Mongodb()
    response_mod = await client.get_service(
        id=service_data["id"],
        name=service_data["name"],
        response_model=Service
    )

    if response_mod:
        return response_mod
    raise HTTPException(status_code=404, detail=f"Service not found")


@app.put("/update_team", response_model=UpdateModel)
async def update_team(id: str, updated_team: UpdateTeam):
    updated_team = {k: v for k, v in updated_team.dict().items() if v is not None}
    client = Mongodb()
    response_mod = await client.update_team(
        id=id,
        update_info=updated_team,
        response_model=UpdateModel()
        )

    if response_mod:
        return response_mod

@app.put("/update_service", response_model=UpdateModel)
async def update_service(id: str, updated_service: UpdateService):
    updated_service = {k: v for k, v in updated_service.dict().items() if v is not None}
    client = Mongodb()
    response_mod = await client.update_service(
        id=id,
        update_info=updated_service,
        response_model=UpdateModel()
    )

    if response_mod:
        return response_mod

@app.delete("/delete_team",response_model=DeleteModel)
async def delete_team(id: str):
    dm = DeleteModel()
    client = Mongodb()
    response_mod = await client.delete_team(
        id=id,
        response_model=dm
    )

    if response_mod.success == True:
        return response_mod
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(response_mod)
            )

@app.delete("/delete_service",response_model=DeleteModel)
async def delete_service(id: str):
    dm = DeleteModel()
    client = Mongodb()
    response_mod = await client.delete_service(
        id=id,
        response_model=dm
    )

    if response_mod.success == True:
        return response_mod
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(response_mod)
            )

@app.get("/list_teams", response_model=List[Team])
async def list_teams(query: str=None):
    client = Mongodb()
    if query:
        response_mod = await client.query_teams(
            query=query,
            response_model=UpdateModel()
        )
        if response_mod:
            return response_mod
        
    response_mod = await client.list_teams()
    return response_mod

@app.get("/list_services", response_model=Union[List[Service],UpdateModel])
async def list_services(query: str=None):
    client = Mongodb()
    if query:
        response_mod = await client.query_services(
            query=query,
            response_model=UpdateModel()
        )
        if response_mod:
            return response_mod
        
    response_mod = await client.list_services()
    return response_mod
