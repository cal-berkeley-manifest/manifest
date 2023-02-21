#!/bin/bash

NUMBER_OF_SERVICES=10
DUMMY_TEAM_ID=$(
    curl -X 'POST' \
    'http://127.0.0.1:8000/create_team' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
        "name": "DUMMY_TEAM_ID",
        "operator_group": "string",
        "admin_group": "string",
        "slack_channel": "string"
    }' | \
    python3 -c "import sys, json; \
    team = json.load(sys.stdin); \
    print(team['id'])"
)

for x in $(seq 1 $NUMBER_OF_SERVICES); do
    curl -X 'POST' \
    'http://127.0.0.1:8000/create_service' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "name": "SERVICE_'${RANDOM}'", 
    "pager_duty_link": "string",
    "team_id": "'${DUMMY_TEAM_ID}'"
    }'
done