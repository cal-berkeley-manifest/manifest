import boto3
from boto3.dynamodb.conditions import Key
from api.config import Settings
import motor.motor_asyncio
from bson import ObjectId
from fastapi.encoders import jsonable_encoder


set = Settings()


class Mongodb:
    
    client = motor.motor_asyncio.AsyncIOMotorClient(set.mongodb_url)
    db = client["manifest-dev"]

    async def create_team(self, item, response_model):
        
        try:
            team_found = await self.get_team("",item["team_name"])
            if team_found:
                response_model.__dict__.update({"description" : "Could not create team, team name exists", "success" : False, "id" : ""})
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
        
        
    async def get_team(self,team_id, team_name, response_model=None):

        if team_id == "" and team_name == "":
            return response_model
        elif team_id :
            key = "id"
            value = team_id
        else:
            key = "team_name"
            value = team_name
        try:
            found_team = await self.db["teams"].find_one({key: value})
        
            if response_model != None:
                response_model = response_model.parse_obj(found_team)
        
                return response_model
            else:
                return found_team

        except Exception as e:
            return response_model
            raise e

# class Dynamodb:
#     # For dev needs to be removed VVV
#     session = boto3.Session(profile_name="gess")
#     ddb = session.client("dynamodb")

#     def normalize_data(self, data):
#         nd = {}
#         for k, v in data.items():
#             nd.update({k: {"S": v}})
#         return nd

#     def curate_response_model(self, input_params, response_model):
#         input_dict = {}
#         if len(input_params["Items"]) != 0:
#             items = input_params["Items"][0]
#             for item,iv in items.items():
#                 for k,v in iv.items():
#                     input_dict.update({item : v})

#             response_model = response_model.parse_obj(input_dict)
#         return response_model

#     def store_team(self, item_dict, response_model):
#         # normalize data to all strings and prep for dynamo item format
        
#         resp = self.get_team({"name" : item_dict["team_name"], "id" : "none"})
#         if len(resp["Items"]) > 0:
#             response_model.__dict__.update({"description" : "Team Exists", "success" : False})
#             return response_model
        
#         data = self.normalize_data(item_dict)
#         # store data in dynamo table
#         try:
#             self.ddb.put_item(TableName=set.TEAMS_DYNAMO_TABLE, Item=data)
#             response_model.__dict__.update({ "id" : item_dict["team_id"]})
#             return response_model
#         except Exception as e:
#             response_model.__dict__.update({"description" : "Internal Error", "success" : False})
#             return response_model
        


            
#     def store_service(self, item_dict, response_model):

#         service_resp = self.get_service({"name" : item_dict["service_name"], "id" : "none"})
#         team_resp = self.get_team({"id" : item_dict["team_id"], "name" : "none"})
        
#         if len(service_resp["Items"]) > 0:
#             response_model.__dict__.update({"description" : "Service Exists", "success" : False })
#             return response_model

#         if  len(team_resp["Items"]) != 1:
#             response_model.__dict__.update({"description" : "Team Doesn't Exist", "success" : False })
#             return response_model

#         #normalize data to all strings and prep for dynamo item format
#         data = self.normalize_data(item_dict)
#         try:
#             # store data in dynamo table
#             self.ddb.put_item(TableName=set.SERVICES_DYNAMO_TABLE, Item=data)
#             response_model.__dict__.update({ "id" : item_dict["service_id"]})
#             return response_model

#         except Exception as e:
#             response_model.__dict__.update({"description" : "Internal Error", "success" : False })
#             return response_model
            

#     def get_team(self, input_model, response_model=None):
#         # retrieve data from dynamo table
#         results = None

#         if input_model["id"] != "none":
#             results = self.ddb.query(
#             TableName=set.TEAMS_DYNAMO_TABLE,
#             Select="ALL_ATTRIBUTES",
#             KeyConditionExpression="team_id = :team_id",
#                 ExpressionAttributeValues={
#                     ":team_id": {"S": input_model["id"]}
#                 }
#             )
#         else:
#             results = self.ddb.scan(
#                 TableName=set.TEAMS_DYNAMO_TABLE,
#                 Select="ALL_ATTRIBUTES",
#                 FilterExpression="team_name = :team_name",
#                 ExpressionAttributeValues={
#                     ":team_name" : {"S" : input_model["name"]}
#                 } 
#             )

#         if response_model != None:
#             curated_response = self.curate_response_model(results, response_model)
#             if len(results["Items"]) == 0:
#                 response_model.__dict__.update({"description" : "Team Doesnt Exists", "success" : False })
#             return curated_response

#         else:
#             return results

        
#     def get_service(self, input_model, response_model=None):
#          # retrieve data from dynamo table
#         results = None

#         if input_model["id"] != "none":
#             results = self.ddb.query(
#             TableName=set.SERVICES_DYNAMO_TABLE,
#             Select="ALL_ATTRIBUTES",
#             KeyConditionExpression="service_id = :service_id",
#                 ExpressionAttributeValues={
#                     ":service_id": {"S": input_model["id"]}
#                 }
#             )

#         else:
#             results = self.ddb.scan(
#                 TableName=set.SERVICES_DYNAMO_TABLE,
#                 Select="ALL_ATTRIBUTES",
#                 FilterExpression="service_name = :service_name",
#                 ExpressionAttributeValues={
#                     ":service_name" : {"S" : input_model["name"]}
#                 } 
#             )  


#         if response_model != None:
#             curated_response = self.curate_response_model(results, response_model)
#             if len(results["Items"]) == 0:
#                 response_model.__dict__.update({"description" : "Service Doesnt Exists", "success" : False })
#             return curated_response

#         else:
#             return results