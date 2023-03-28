from fastapi import FastAPI, HTTPException, status, File, UploadFile
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
from fastapi.responses import StreamingResponse
from io import BytesIO
import csv
import codecs


app = FastAPI()
settings = Settings()

##########################
#       Core Routes
##########################

@app.post("/create_pagerduty_integration", response_model=Upsert)
async def create_pagerduty_integration(requested_pagerduty_integration: PagerdutyIntegration):    
    cm = Upsert()
    pagerdutyIntegration = PagerdutyIntegration.parse_obj(requested_pagerduty_integration)  
    client = Mongodb()
    await client.create_pagerduty_integration(jsonable_encoder(pagerdutyIntegration))

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(cm)
    )

@app.post("/delete_pagerduty_integration", response_model=Upsert)
async def delete_pagerduty_integration():
    dm = Upsert()
    client = Mongodb()
    await client.delete_pagerduty_integration()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(dm)
    )

@app.post("/sync_pagerduty_integration", response_model=Upsert)
async def sync_pagerduty_integration():    
    cm = Upsert()
    client = Mongodb()
    await client.sync_pagerduty_integration()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(cm)
    )

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

@app.get("/list_teams", response_model=Union[List[Team],UpdateModel])
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

@app.get("/download_teams", response_description='csv')
async def download_teams():
    client = Mongodb()
    csvStr = "id,name,operator_group,admin_group,slack_channel\n"
    teams = await client.list_teams()
    for team in teams:
        csvStr += team["id"]
        csvStr += ","
        csvStr += team["name"]
        csvStr += ","
        csvStr += team["operator_group"]
        csvStr += ","
        csvStr += team["admin_group"]
        csvStr += ","
        csvStr += team["slack_channel"]
        csvStr += "\n"
    csvStrBytes = csvStr.encode('utf-8')
    output = BytesIO(csvStrBytes)

    headers = {
        'Content-Disposition': 'attachment; filename="manifest_teams.csv"'
    }
    return StreamingResponse(iter([output.getvalue()]), headers=headers)

@app.get("/download_services", response_description='csv')
async def download_services():
    client = Mongodb()
    csvStr = "id,name,pager_duty_link,team_id,tags\n"
    teams = await client.list_services()
    for team in teams:
        csvStr += team["id"]
        csvStr += ","
        csvStr += team["name"]
        csvStr += ","
        csvStr += team["pager_duty_link"]
        csvStr += ","
        csvStr += team["team_id"]
        csvStr += ","
        tagsStr = "\""
        tags = team["tags"]
        for i, tag in enumerate(tags):
            tagsStr += tag
            if (i < (len(tags)-1)):
                tagsStr += ","
        tagsStr += "\""
        csvStr += tagsStr
        csvStr += "\n"
    csvStrBytes = csvStr.encode('utf-8')
    output = BytesIO(csvStrBytes)

    headers = {
        'Content-Disposition': 'attachment; filename="manifest_services.csv"'
    }
    return StreamingResponse(iter([output.getvalue()]), headers=headers)

@app.post("/upload_services")
async def upload(file: UploadFile = File(...)):
    csvReader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
    client = Mongodb()
    num_attempted_to_update = 0
    num_updated = 0
    num_attempted_to_create = 0
    num_created = 0
    for rows in csvReader:   
        isUpdate = False          
        tagsStr = rows['tags']
        tagsList = tagsStr.split(",")

        cm = CreateModel()
        
        newService = Service()
        if rows["id"]:
            dm = DeleteModel()
            del_resp_model = await client.delete_service(
                id = rows["id"],
                response_model = dm
            )
            if del_resp_model.success is True:
                isUpdate = True
                num_attempted_to_update += 1
            else:
                num_attempted_to_create += 1
            newService.id = rows["id"]
        else:
            newService.id = str(uuid4().hex)
            num_attempted_to_create += 1

        newService.name = rows["name"]
        newService.pager_duty_link = rows["pager_duty_link"]
        newService.team_id = rows["team_id"]
        newService.tags = set(tagsList)
        response_mod = await client.create_service(
            jsonable_encoder(newService),
            response_model = cm
        )

        if response_mod and hasattr(response_mod, "success") and response_mod.success == True:
            if isUpdate:
                num_updated += 1
            else:
                num_created += 1
    
    file.file.close()
    data = {}
    data["num_attempted_to_update"] = num_attempted_to_update
    data["num_updated"] = num_updated
    data["num_attempted_to_create"] = num_attempted_to_create
    data["num_created"] = num_created
    return data

@app.post("/upload_teams")
async def upload(file: UploadFile = File(...)):
    csvReader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
    client = Mongodb()
    num_attempted_to_update = 0
    num_updated = 0
    num_attempted_to_create = 0
    num_created = 0
    for rows in csvReader:   
        isUpdate = False          

        cm = CreateModel()
        
        newTeam = Team()
        if rows["id"]:
            dm = DeleteModel()
            del_resp_model = await client.delete_team(
                id = rows["id"],
                response_model = dm,
                ignore_service_check=True
            )
            if del_resp_model.success is True:
                print("Successfully deleted...")
                isUpdate = True
            else:
                print("Failed to delete team with id: " + rows["id"])
            newTeam.id = rows["id"]
        else:
            newTeam.id = str(uuid4().hex)

        if isUpdate:
            num_attempted_to_update += 1
        else:
            num_attempted_to_create += 1

        newTeam.name = rows["name"]
        newTeam.operator_group = rows["operator_group"]
        newTeam.admin_group = rows["admin_group"]
        newTeam.slack_channel = rows["slack_channel"]
        response_mod = await client.create_team(
            jsonable_encoder(newTeam),
            response_model = cm
        )

        if response_mod and hasattr(response_mod, "success") and response_mod.success == True:
            print("Successfully created team")
            if isUpdate:
                num_updated += 1
            else:
                num_created += 1
        else:
            print("Failed to create team")
    
    file.file.close()
    data = {}
    data["num_attempted_to_update"] = num_attempted_to_update
    data["num_updated"] = num_updated
    data["num_attempted_to_create"] = num_attempted_to_create
    data["num_created"] = num_created
    return data