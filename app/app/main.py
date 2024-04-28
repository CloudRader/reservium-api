"""
Module to run FastAPI application, where API routers are connecting application to API modules.
In other words it is an entry point of the application.
"""
import uvicorn
from fastapi import FastAPI
from api import buk_is_auth, events, grills, study_rooms, club_rooms
from db import init_db

app = FastAPI()

app.include_router(buk_is_auth.router)
app.include_router(events.router)
app.include_router(grills.router)
app.include_router(study_rooms.router)
app.include_router(club_rooms.router)


def main():
    init_db()
    uvicorn.run(app, host="10.0.52.106", port=8000,
                ssl_keyfile="certification/key.pem", ssl_certfile="certification/cert.pem")


if __name__ == "__main__":
    main()
