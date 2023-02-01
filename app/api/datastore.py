import boto3
from boto3.dynamodb.conditions import Key
from api.config import Settings

set = Settings()

class Dynamodb:
    # For dev needs to be removed VVV
    session = boto3.Session(profile_name="gess")
    ddb = session.client("dynamodb")

    def normalize_data(self, data):
        nd = {}
        for k, v in data.items():
            nd.update({k: {"S": v}})
        return nd

    def curate_response_model(self, input_params, response_model):
        input_dict = {}
        if len(input_params["Items"]) != 0:
            items = input_params["Items"][0]
            for item,iv in items.items():
                for k,v in iv.items():
                    input_dict.update({item : v})

            response_model = response_model.parse_obj(input_dict)
        return response_model

    def store_team(self, item_dict, response_model):
        # normalize data to all strings and prep for dynamo item format
        
        resp = self.get_team({"name" : item_dict["team_name"], "id" : "none"})
        if len(resp["Items"]) > 0:
            response_model.__dict__.update({"description" : "Team Exists", "success" : False})
            return response_model
        
        data = self.normalize_data(item_dict)
        # store data in dynamo table
        try:
            self.ddb.put_item(TableName=set.TEAMS_DYNAMO_TABLE, Item=data)
            response_model.__dict__.update({ "id" : item_dict["team_id"]})
            return response_model
        except Exception as e:
            response_model.__dict__.update({"description" : "Internal Error", "success" : False})
            return response_model
        
            
    def store_service(self, item_dict, response_model):

        service_resp = self.get_service({"name" : item_dict["service_name"], "id" : "none"})
        team_resp = self.get_team({"id" : item_dict["team_id"], "name" : "none"})
        
        if len(service_resp["Items"]) > 0:
            response_model.__dict__.update({"description" : "Service Exists", "success" : False })
            return response_model

        if  len(team_resp["Items"]) != 1:
            response_model.__dict__.update({"description" : "Team Doesn't Exist", "success" : False })
            return response_model

        #normalize data to all strings and prep for dynamo item format
        data = self.normalize_data(item_dict)
        try:
            # store data in dynamo table
            self.ddb.put_item(TableName=set.SERVICES_DYNAMO_TABLE, Item=data)
            response_model.__dict__.update({ "id" : item_dict["service_id"]})
            return response_model

        except Exception as e:
            response_model.__dict__.update({"description" : "Internal Error", "success" : False })
            return response_model
            

    def get_team(self, input_model, response_model=None):
        # retrieve data from dynamo table
        results = None

        if input_model["id"] != "none":
            results = self.ddb.query(
            TableName=set.TEAMS_DYNAMO_TABLE,
            Select="ALL_ATTRIBUTES",
            KeyConditionExpression="team_id = :team_id",
                ExpressionAttributeValues={
                    ":team_id": {"S": input_model["id"]}
                }
            )
        else:
            results = self.ddb.scan(
                TableName=set.TEAMS_DYNAMO_TABLE,
                Select="ALL_ATTRIBUTES",
                FilterExpression="team_name = :team_name",
                ExpressionAttributeValues={
                    ":team_name" : {"S" : input_model["name"]}
                } 
            )

        if response_model != None:
            curated_response = self.curate_response_model(results, response_model)
            if len(results["Items"]) == 0:
                response_model.__dict__.update({"description" : "Team Doesnt Exists", "success" : False })
            return curated_response

        else:
            return results

        
    def get_service(self, input_model, response_model=None):
         # retrieve data from dynamo table
        results = None

        if input_model["id"] != "none":
            results = self.ddb.query(
            TableName=set.SERVICES_DYNAMO_TABLE,
            Select="ALL_ATTRIBUTES",
            KeyConditionExpression="service_id = :service_id",
                ExpressionAttributeValues={
                    ":service_id": {"S": input_model["id"]}
                }
            )

        else:
            results = self.ddb.scan(
                TableName=set.SERVICES_DYNAMO_TABLE,
                Select="ALL_ATTRIBUTES",
                FilterExpression="service_name = :service_name",
                ExpressionAttributeValues={
                    ":service_name" : {"S" : input_model["name"]}
                } 
            )  


        if response_model != None:
            curated_response = self.curate_response_model(results, response_model)
            if len(results["Items"]) == 0:
                response_model.__dict__.update({"description" : "Service Doesnt Exists", "success" : False })
            return curated_response

        else:
            return results