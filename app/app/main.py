"""
Module to run FastAPI application, where API routers are connecting application to API modules.
In other words it is an entry point of the application.
"""
import uvicorn
from fastapi import FastAPI
from api import buk_is_auth

app = FastAPI()

app.include_router(buk_is_auth.router)


def main():
    uvicorn.run(app, host="10.0.52.106", port=8000,
                ssl_keyfile="certification/key.pem", ssl_certfile="certification/cert.pem")


if __name__ == "__main__":
    main()
