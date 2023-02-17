#!/bin/bash

ALL_IDS=$(
    curl -X 'GET' \
    'http://127.0.0.1:8000/list_teams' \
    -H 'accept: application/json' | \
    python3 -c "import sys, json; \
    team_list = json.load(sys.stdin); \
    print([team['id'] for team in team_list])"
)

for id in $ALL_IDS; do
    id=$(echo $id | sed "s/[,']//g" | sed "s/[][]//g")
    curl -X 'DELETE' \
    "http://127.0.0.1:8000/delete_team?id=${id}" \
    -H 'accept: application/json'
done