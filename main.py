from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
import httpx
from database_systems import Database

app = FastAPI()
db = Database()

# Schemes

class PlaceCreate(BaseModel):
    place_id: int

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    startdate: Optional[str] = None
    places: Optional[List[int]] = Field(None, max_items=10)

class ProjectUpdate(BaseModel):
    new_name: str
    description: Optional[str] = None
    startdate: Optional[str] = None

class NoteUpdate(BaseModel):
    note: str

# async func
async def validate_place_exists(place_id: int):
    """Checking place existence with API"""
    url = f"https://api.artic.edu/api/v1/places/{place_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Place ID {place_id} not found in Art Institute API"
                )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="External API unavailable")


# Endpoints for projects
@app.post("/projects/", status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate):
    try:
        if project.places:
            for p_id in project.places:
                await validate_place_exists(p_id)

            db.create_project_with_places(
                project.name, project.description, project.startdate, project.places
            )
        else:
            db.create_project(project.name, project.description, project.startdate)

        return {"message": "Project created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=400, detail="Project with this name already exists")


@app.get("/projects/")
def list_projects():
    return db.list_projects()


@app.get("/projects/{name}")
def get_project(name: str):
    project = db.get_project(name)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.put("/projects/{name}")
def update_project(name: str, data: ProjectUpdate):
    db.update_project(name, data.new_name, data.description, data.startdate)
    return {"message": "Project updated"}


@app.delete("/projects/{name}")
def delete_project(name: str):
    try:
        db.delete_project(name)
        return {"message": "Project deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Endpoints for places

@app.post("/projects/{name}/places/")
async def add_place_to_project(name: str, place: PlaceCreate):
    # validate place
    await validate_place_exists(place.place_id)

    # adding to db
    try:
        db.add_place_to_project(name, place.place_id)
        return {"message": "Place added to project"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/projects/{name}/places/")
def get_project_places(name: str):
    return db.list_project_places(name)


@app.patch("/projects/{name}/places/{place_id}/visit")
def mark_as_visited(name: str, place_id: int):
    db.mark_place_visited(name, place_id)
    return {"message": "Place marked as visited"}


@app.put("/places/{place_id}/notes")
def update_note(place_id: int, note_data: NoteUpdate):
    db.update_place_note(place_id, note_data.note)
    return {"message": "Note updated"}
