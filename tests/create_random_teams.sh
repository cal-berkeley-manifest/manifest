#!/bin/bash

NUMBER_OF_TEAMS=10

for x in $(seq 1 $NUMBER_OF_TEAMS); do
    curl -X 'POST' \
    'http://127.0.0.1:8000/create_team' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "name": "TEAM_'${RANDOM}'", 
    "operator_group": "string",
    "admin_group": "string",
    "slack_channel": "string"
    }'
done