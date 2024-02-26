"""
Module to run FastAPI application, where API routers are connecting application to API modules.
In other words it is an entry point of the application.
"""
import uvicorn
from fastapi import FastAPI

app = FastAPI


def main():
    uvicorn.run(app, host="10.0.52.106", port=8000,
                ssl_keyfile="key.pem", ssl_certfile="cert.pem")


if __name__ == "__main__":
    main()
