import fastapi
import sqlite3

app = fastapi.FastAPI()

@app.post("/create-travel-project")
def create_travel_project():


