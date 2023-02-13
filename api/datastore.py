from api.config import Settings
import motor.motor_asyncio

set = Settings()

class Mongodb:
    
    client = motor.motor_asyncio.AsyncIOMotorClient(set.mongodb_url)
    db = client["manifest-dev"]

    async def list_services(self):
        services = await self.db["services"].find().to_list(1000)
        return services

    async def create_team(self, item, response_model):
        
        try:
            team_found = await self.get_team("",item["team_name"])
            if team_found:
                response_model.__dict__.update({"description" : "Team name already exists", "success" : False, "id" : ""})
                return response_model
            else:
                new_team = await self.db["teams"].insert_one(item)
                team_id = item["id"]
                created_team = await self.db["teams"].find_one({"id": team_id})
                response_model.__dict__.update({"description" : "Team Created", "success" : True, "id" : str(team_id)})
                return response_model

        except Exception as e:
            response_model.__dict__.update({"description" : "Could not create team", "success" : False, "id" : ""})
            raise e
            return response_model

    async def create_service(self, item, response_model):   
        try:
            service_found = await self.get_service("",item["service_name"])
            if service_found:
                response_model.__dict__.update({"description" : "Service name already exists", "success" : False, "id" : ""})
                return response_model
            else:
                new_service = await self.db["services"].insert_one(item)
                service_id = item["id"]
                created_service = await self.db["services"].find_one({"id": service_id})
                response_model.__dict__.update({"description" : "Service Created", "success" : True, "id" : str(service_id)})
                return response_model

        except Exception as e:
            response_model.__dict__.update({"description" : "Could not create service", "success" : False, "id" : ""})
            raise e
            return response_model
        
    async def get_team(self, team_id, team_name, response_model=None):
        if team_id:
            key = "id"
            value = team_id
        else:
            key = "team_name"
            value = team_name
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

    async def get_service(self, service_id, service_name, response_model=None):
        if service_id:
            key = "id"
            value = service_id
        else:
            key = "service_name"
            value = service_name
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
