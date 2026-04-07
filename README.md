# Travel Planner

This is a REST API for travel planner. I maked it on fastapi.

Project include Dockerfile - you can run API from Docker container

## Container creation

create image

`docker build -t travel-api .`

create container with volume for db with port 8000

`docker run -d --name travel-container -p 8000:8000 -v $(pwd)/data:/app/data travel-api`

## OpenAPI

You can find docs on .../docs page

