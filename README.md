# Manifest 
This is a light-weight service catalog meant to enforce attribution of services to teams in an opinionated yet flexible manner
## Table of Contents  
- [Installation](#installation) 
- [Usage](#usage) 
- [Contributors](#contributors) 
- [License](#license) 
## Installation 
In order to leverage Manifest you need to complete the following steps:
1. Create a Docker image or an alternative and ensure the entry point executes at manifest/main:app
2. Spin up 2 MongoDB clusters. One for Auth metadata and one for Service & Team metadata
3. Set 3 environmental variables:
 - `export MONGODB_URL=<Service+Team Collection connection string>`
 - `export AUTH_MONGODB_URL=<Auth Collection connection string>`
 - `export JWT_SECRET_KEY= <private key 4096 bits>`
 - `JWT_REFRESH_SECRET_KEY= <private key 4096 bits>`

***Note:***
Mongodb Clusters must be named in the following manner:

- Service + Team Metadata Cluster Name = `manifest-dev`
- Service + Team Metadata Collection Names = `services, teams`
- Auth Cluster Name = `manifest-auth`
- Auth Collection Name = `auth`

## Usage 
Provide instructions on how to use your project here

## Contributors
 - **Anthony Scheller**: *UC Berkeley*
 - **Nelson Moreno**: *UC Berkeley*
 - **Joe Allen**: *UC Berkeley*
 - **Virginia Gresham**: *UC Berkeley*
 - **Kyle Jaquez**: *UC Berkeley*
 
