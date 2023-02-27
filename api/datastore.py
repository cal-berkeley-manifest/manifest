from api.config import Settings
import motor.motor_asyncio
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from api.schemas import *
from json import loads
from json.decoder import JSONDecodeError

set = Settings()

class Mongodb:
    
    client = motor.motor_asyncio.AsyncIOMotorClient(set.mongodb_url)
    db = client["manifest-dev"]

    async def create_team(self, item, response_model):
        
        try:
            team_found = await self.get_team("",item["name"])
            if team_found:
                response_model.__dict__.update({"description" : "Team name already exists", "success" : False, "id" : ""})
                return response_model
            else:
                new_team = await self.db["teams"].insert_one(item)
                id = item["id"]
                created_team = await self.db["teams"].find_one({"id": id})
                response_model.__dict__.update({"description" : "Team Created", "success" : True, "id" : str(id)})
                return response_model

        except Exception as e:
            response_model.__dict__.update({"description" : "Could not create team", "success" : False, "id" : ""})
            raise e
            return response_model

    async def create_service(self, item, response_model):   
        try:
            service_found = await self.get_service("",item["name"])
            if service_found:
                response_model.__dict__.update({"description" : "Service name already exists", "success" : False, "id" : ""})
                return response_model
            else:
                team_found = await self.get_team(item["team_id"], "")
                if team_found is None:
                    response_model.__dict__.update({"description" : "Invalid team_id assigned to service", "success" : False, "id" : ""})
                    return response_model
                new_service = await self.db["services"].insert_one(item)
                id = item["id"]
                created_service = await self.db["services"].find_one({"id": id})
                response_model.__dict__.update({"description" : "Service Created", "success" : True, "id" : str(id)})
                return response_model

        except Exception as e:
            response_model.__dict__.update({"description" : "Could not create service", "success" : False, "id" : ""})
            raise e
            return response_model
        
    async def get_team(self, id, name, response_model=None):
        if id:
            key = "id"
            value = id
        else:
            key = "name"
            value = name
        try:
            found_team = await self.db["teams"].find_one({key: value})
            if response_model != None and (found_team):
                response_model = response_model.parse_obj(found_team)
                return response_model
            else:
                return found_team

        except Exception as e:
            return response_model
            raise e

    async def get_service(self, id, name, response_model=None):
        if id:
            key = "id"
            value = id
        else:
            key = "name"
            value = name
        try:
            found_service = await self.db["services"].find_one({key: value})
        
            if (response_model != None) and (found_service):
                response_model = response_model.parse_obj(found_service)
                return response_model
            else:
                return found_service

        except Exception as e:
            return response_model
            raise e

    async def update_team(self, id, update_info, response_model=None):
        try:
            found_team = await self.db["teams"].find_one({"id": id})
            if found_team:
                updated_team = await self.db["teams"].update_one({"id": id}, {"$set": update_info})
                if updated_team:
                    response_model.__dict__.update(
                        {
                            "description": "Team successfully updated",
                            "success": True,
                            "id": id
                        }
                    )
                    return response_model
                else:
                    response_model.__dict__.update(
                        {
                            "description": "Could not update team",
                            "success": False,
                        }
                    )
                    return JSONResponse(
                        status_code=status.HTTP_304_NOT_MODIFIED,
                        content=jsonable_encoder(response_model)
                    )
            else:
                response_model.__dict__.update(
                    {
                        "description": "Could not find team to update",
                        "success": False
                    }
                )
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=jsonable_encoder(response_model)
                )

        except Exception as e:
            return response_model
            raise e

    async def update_service(self, id, update_info, response_model=None):
        try:
            found_service = await self.db["services"].find_one({"id": id})
            if found_service:
                if 'team_id' in update_info:
                    team_found = await self.get_team(update_info["team_id"], "")
                    if team_found is None:
                        response_model.__dict__.update(
                            {"description" : "Invalid team_id assigned to service", 
                            "success" : False, 
                            "id" : ""
                            }
                        )
                        return JSONResponse(
                            status_code=status.HTTP_412_PRECONDITION_FAILED,
                            content=jsonable_encoder(response_model)
                        )
                if 'add_tag' in update_info:
                    updated_tags = await self.db["services"].update_one(
                                {"id": id},
                                {"$addToSet": {"tags": {"$each": update_info['add_tag']}}}
                            )
                    if not updated_tags:
                        response_model.__dict__.update(
                            {
                                "description": "Tag could not be added",
                                "success": False
                            }
                        )
                        return JSONResponse(
                            status_code=status.HTTP_412_PRECONDITION_FAILED,
                            content=jsonable_encoder(response_model)
                        )
                if 'delete_tag' in update_info:
                    deleted_tags = await self.db["services"].update_one(
                        {"id": id},
                        {"$pull": {"tags": {"$in": update_info['delete_tag']}}}
                    )
                    if not deleted_tags:
                        response_model.__dict__.update(
                            {
                                "description": "Tag could not be deleted",
                                "success": False
                            }
                        )
                        return JSONResponse(
                            status_code=status.HTTP_412_PRECONDITION_FAILED,
                            content=jsonable_encoder(response_model)
                        )

                updated_service = await self.db["services"].update_one({"id": id}, {"$set": update_info})
                if updated_service:
                    response_model.__dict__.update(
                        {
                            "description": "Service successfully updated",
                            "success": True,
                            "id": id
                        }
                    )
                    return response_model
                else:
                    response_model.__dict__.update(
                        {
                            "description": "Could not update service",
                            "success": False,
                        }
                    )
                    return JSONResponse(
                        status_code=status.HTTP_304_NOT_MODIFIED,
                        content=jsonable_encoder(response_model)
                    )
            else:
                response_model.__dict__.update(
                    {
                        "description": "Could not find service to update",
                        "success": False
                    }
                )
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=jsonable_encoder(response_model)
                )

# Using this for except block for debugging, but not sure final app should return this info.
        except Exception as e:
            response_model.__dict__.update({
                "description": str(e),
                "success": False
            })
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder(response_model)
            )

    async def delete_team(self, id, response_model=None):
        try:
            found_team = await self.db["teams"].find_one({"id": id})
            if found_team != None:
                team_model = Team.parse_obj(found_team)
                services = await self.list_services()
                if services != None and len(services) > 0:
                    for service in services:
                        service_model = Service.parse_obj(service)
                        if service_model.team_id == team_model.id:
                            response_model.__dict__.update({"description" : "Cannot delete team with active services", "success" : False})
                            return response_model
                await self.db["teams"].delete_one({"id": id})

            if response_model != None:
                if found_team:
                    response_model.__dict__.update({"description" : "Team successfully deleted", "success" : True, "id": id})
                else:
                    response_model.__dict__.update({"description" : "Could not find team to delete", "success" : False})
                return response_model
            else:
                return

        except Exception as e:
            return response_model
            raise e

    async def delete_service(self, id, response_model=None):
        try:
            found_service = await self.db["services"].find_one({"id": id})
            if found_service:
                # TODO: figure this out
                await self.db["services"].delete_one({"id": id})
                
            if response_model != None:
                if found_service:
                    response_model.__dict__.update({"description" : "Service successfully deleted", "success" : True, "id": id})
                else:
                    response_model.__dict__.update({"description" : "Could not find service to delete", "success" : False})
                return response_model
            else:
                return

        except Exception as e:
            return response_model
            raise e

    async def list_teams(self):
            teams = await self.db["teams"].find().to_list(1000)
            return teams

    async def list_services(self):
        services = await self.db["services"].find().to_list(1000)
        return services
    
    async def query_teams(self, query, response_model=None):
        try:
            encoded = loads(query)
            if encoded:
                query_success = await self.db["teams"].find(encoded).to_list(1000)
                if query_success:
                    return query_success
                else:
                    response_model.__dict__.update({
                        "description": "Could not find teams using provided query",
                        "success": False
                    })
                    return JSONResponse(
                        status_code=status.HTTP_404_NOT_FOUND,
                        content=jsonable_encoder(response_model)
                    )
        except JSONDecodeError as e:
           response_model.__dict__.update({
                "description": "Could not decode provided query",
                "success": False
            })
           return JSONResponse(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                content=jsonable_encoder(response_model)
            )
        except Exception as e:
            response_model.__dict__.update({
                "description": str(e),
                "success": False
            })
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder(response_model)
            )

    async def query_services(self, query, response_model=None):
        try:
            encoded = loads(query)
            if encoded:
                query_success = await self.db["services"].find(encoded).to_list(1000)
                if query_success:
                    return query_success
                else:
                    response_model.__dict__.update({
                        "description": "Could not find services using provided query",
                        "success": False
                    })
                    return JSONResponse(
                        status_code=status.HTTP_404_NOT_FOUND,
                        content=jsonable_encoder(response_model)
                    )
        except JSONDecodeError as e:
            response_model.__dict__.update({
                "description": "Could not decode provided query",
                "success": False
            })
            return JSONResponse(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                content=jsonable_encoder(response_model)
            )
        except Exception as e:
            response_model.__dict__.update({
                "description": str(e),
                "success": False
            })
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder(response_model)
            )