from api.config import Settings
import motor.motor_asyncio
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from api.schemas import *
from json import loads
from json.decoder import JSONDecodeError
from pdpyras import APISession
from pdpyras import PDClientError

settings = Settings()

class Mongodb:
    
    core_client = motor.motor_asyncio.AsyncIOMotorClient(settings.CORE_MONGO_CONN)
    core_db = core_client["manifest-dev"]

    auth_client = motor.motor_asyncio.AsyncIOMotorClient(settings.AUTH_MONGO_CONN)
    auth_db = auth_client["manifest-auth"]

    async def create_team(self, item, response_model):
        
        try:
            team_found = await self.get_team("",item["name"])
            if team_found:
                response_model.__dict__.update({"description" : "Team name already exists", "success" : False, "id" : ""})
                return response_model
            else:
                new_team = await self.core_db["teams"].insert_one(item)
                id = item["id"]
                created_team = await self.core_db["teams"].find_one({"id": id})
                response_model.__dict__.update({"description" : "Team Created", "success" : True, "id" : str(id)})
                return response_model

        except Exception as e:
            response_model.__dict__.update({"description" : "Could not create team", "success" : False, "id" : ""})
            raise e
            return response_model

    async def create_pagerduty_integration(self, item):   
        try:
            await self.delete_pagerduty_integration()
            await self.core_db["pagerduty_integration"].insert_one(item)

        except Exception as e:
            raise e
        
    async def sync_pagerduty_integration(self):   
        try:
            pagerdutyIntegration = await self.get_pagerduty_integration()
            session = APISession(pagerdutyIntegration.api_key, default_from=pagerdutyIntegration.admin_email)

            pdServiceUrlPrefix = "https://" + pagerdutyIntegration.pager_duty_org + ".pagerduty.com/service-directory/"

            pdServices = session.list_all(
                'services',
                params={}
            )

            pdServiceNameSet = set()

            defaultEscalationPolicy = {}
            pdServiceNameToIDMap = {}
            for pdService in pdServices:
                if pdService["name"] == "Default Service":
                    defaultEscalationPolicy = pdService["escalation_policy"]
                pdServiceNameSet.add(pdService["name"])
                pdServiceNameToIDMap[pdService["name"]] = pdService["id"]

            
            manifestServiceToAddNameSet = set()
            manifestServices = await self.list_services()
            manifestServiceIDToPDID = {}
            nameToManifestID = {}
            for manifestService in manifestServices:
                nameToManifestID[manifestService["name"]] = manifestService["id"]
                if (manifestService["name"] not in pdServiceNameSet):
                    manifestServiceToAddNameSet.add(manifestService["name"])
                else:
                    pdServiceID = pdServiceNameToIDMap[manifestService["name"]]
                    pdServiceLink =  pdServiceUrlPrefix + pdServiceID
                    if pdServiceLink != manifestService["pager_duty_link"]:
                        manifestServiceIDToPDID[manifestService["id"]] = pdServiceID

            for manifestServiceToAddName in manifestServiceToAddNameSet:
                try:
                    updated_service = session.persist('services', 'name', {'name': manifestServiceToAddName, 'escalation_policy': defaultEscalationPolicy}, update=False)
                    print("Successfully added service to pagerduty: " + manifestServiceToAddName + " had id of " + updated_service["id"])
                    pdServiceNameToIDMap[manifestServiceToAddName] = updated_service["id"]
                    manifestID = nameToManifestID[manifestServiceToAddName]
                    manifestServiceIDToPDID[manifestID] = updated_service["id"]
                except PDClientError as e:
                    print("Failed adding service to pagerduty: " + manifestServiceToAddName)
                    print(e)

            for manifestID in manifestServiceIDToPDID:
                pdServiceLink = pdServiceUrlPrefix + manifestServiceIDToPDID[manifestID]
                updated_service = await self.core_db["services"].update_one({"id": manifestID}, {"$set": {'pager_duty_link':pdServiceLink}})
                if updated_service:
                    print("Successfully updated manifest service " + manifestID + " with pd link: " + pdServiceLink)
                else:
                    print("Failed updating manifest service " + manifestID + " with pd link: " + pdServiceLink)
            
        except Exception as e:
            raise e

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
                new_service = await self.core_db["services"].insert_one(item)
                id = item["id"]
                created_service = await self.core_db["services"].find_one({"id": id})
                response_model.__dict__.update({"description" : "Service Created", "success" : True, "id" : str(id)})
                await self.sync_pagerduty_integration()
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
            found_team = await self.core_db["teams"].find_one({key: value})
            if response_model != None and (found_team):
                response_model = response_model.parse_obj(found_team)
                return response_model
            else:
                return found_team

        except Exception as e:
            return response_model
            raise e

    async def get_pagerduty_integration(self):
        try:
            found_pagerduty_integration = await self.core_db["pagerduty_integration"].find_one({})
        
            if found_pagerduty_integration:
                return PagerdutyIntegration.parse_obj(found_pagerduty_integration)
                return response_model
            else:
                return found_pagerduty_integration

        except Exception as e:
            raise e

    async def get_service(self, id, name, response_model=None):
        if id:
            key = "id"
            value = id
        else:
            key = "name"
            value = name
        try:
            found_service = await self.core_db["services"].find_one({key: value})
        
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
            found_team = await self.core_db["teams"].find_one({"id": id})
            if found_team:
                updated_team = await self.core_db["teams"].update_one({"id": id}, {"$set": update_info})
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
            found_service = await self.core_db["services"].find_one({"id": id})
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
                    updated_tags = await self.core_db["services"].update_one(
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
                    deleted_tags = await self.core_db["services"].update_one(
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

                updated_service = await self.core_db["services"].update_one({"id": id}, {"$set": update_info})
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

    async def delete_team(self, id, response_model=None,ignore_service_check=False):
        try:
            found_team = await self.core_db["teams"].find_one({"id": id})
            if found_team != None:
                team_model = Team.parse_obj(found_team)
                if ignore_service_check is False:
                    services = await self.list_services()
                    if services != None and len(services) > 0:
                        for service in services:
                            service_model = Service.parse_obj(service)
                            if service_model.team_id == team_model.id:
                                response_model.__dict__.update({"description" : "Cannot delete team with active services", "success" : False})
                                return response_model
                await self.core_db["teams"].delete_one({"id": id})

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

    async def delete_pagerduty_integration(self):
        try:
            await self.core_db["pagerduty_integration"].delete_many({})
                
            return

        except Exception as e:
            raise e

    async def delete_service(self, id, response_model=None):
        try:
            found_service = await self.core_db["services"].find_one({"id": id})
            if found_service:
                # TODO: figure this out
                await self.core_db["services"].delete_one({"id": id})
                
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
            teams = await self.core_db["teams"].find().to_list(1000)
            return teams

    async def list_services(self):
        services = await self.core_db["services"].find().to_list(1000)
        return services
    
    async def query_teams(self, query, response_model=None):
        try:
            encoded = loads(query)
            if encoded:
                query_success = await self.core_db["teams"].find(encoded).to_list(1000)
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
                query_success = await self.core_db["services"].find(encoded).to_list(1000)
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

    async def getUser(self, accountName, response_model=None):
        try:
            account = await self.auth_db["auth"].find_one({"accountName": accountName})
            
            if response_model:
                if account is not None:
                    response_model = response_model.parse_obj(account)
                    return response_model.__dict__
                else:
                    pass

            else:
                if account is not None:
                    return account
                else:
                    pass

        except JSONDecodeError as e:
            raise(e)

    async def create_serviceaccount(self, serviceAccountobj, response_model=None):

        user_found = await self.getUser(serviceAccountobj.get("accountName", ""))
   
        if not user_found:
            try:
                new_user = await self.auth_db["auth"].insert_one(serviceAccountobj)
                if response_model:
                    response_model.__dict__.update({"description" : "Service Account Created"})

            except Exception as e:
                raise e
        else:
            if response_model:
                response_model.__dict__.update({"success" : False, "description" : "Service Account Already Exists"})
        
        if response_model:
            return response_model
        else:
            return new_user
    
    async def delete_serviceaccount(self, accountName, response_model=None):

        try:
            user_found = await self.getUser(accountName)
            
            if user_found:
                # TODO: figure this out
                deleted_user = await self.auth_db["auth"].delete_one({"accountName": accountName})
                
            if response_model != None:
                if user_found:
                    response_model.__dict__.update({"description" : "User successfully deleted", "success" : True})
                else:
                    response_model.__dict__.update({"description" : "Could Not Delete User", "success" : False})
                
                return response_model
                
            else:
                return

        except Exception as e:
            raise e
            return response_model
            