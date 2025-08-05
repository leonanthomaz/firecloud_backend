import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.configuration.settings import Configuration
from app.database import init_db
from app.tasks.websockets import routes as websocket_routes
from app.api.routes import register_routes

configuration = Configuration()

def create_app():
    app = FastAPI()

    logging.info("SISTEMA >>> Inicializando o banco de dados...")
    init_db()

    origins = (
        ["https://firecloud.vercel.app", "https://firecloud-dashboard.vercel.app"]
        if configuration.environment == "production"
        else ["http://localhost:3000", "http://localhost:3001"]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_routes(app)
    app.include_router(websocket_routes.router)

    return app
