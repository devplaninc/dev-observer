import asyncio
import logging
import os
import subprocess
import threading
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

import dev_observer.log
from dev_observer.env_detection import detect_server_env
from dev_observer.server.env import ServerEnv
from dev_observer.server.middleware.auth import AuthMiddleware
from dev_observer.server.services.config import ConfigService
from dev_observer.server.services.observations import ObservationsService
from dev_observer.server.services.repositories import RepositoriesService
from dev_observer.server.services.sites import WebSitesService
from dev_observer.settings import Settings

secrets_file = os.environ.get("DEV_OBSERVER_SECRETS_FILE", None)
if secrets_file is not None and len(secrets_file.strip()) > 0 and os.path.exists(secrets_file) and os.path.isfile(secrets_file):
    load_dotenv(secrets_file)

env_file = os.environ.get("DEV_OBSERVER_ENV_FILE", None)
if env_file is not None and len(env_file.strip()) > 0 and os.path.exists(env_file) and os.path.isfile(env_file):
    load_dotenv(env_file)

dev_observer.log.encoder = dev_observer.log.PlainTextEncoder()
logging.basicConfig(level=logging.DEBUG)
from dev_observer.log import s_

_log = logging.getLogger(__name__)
Settings.model_config["toml_file"] = os.environ.get("DEV_OBSERVER_CONFIG_FILE", None)
env: ServerEnv = detect_server_env(Settings())


def start_bg_processing():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(env.periodic_processor.run())


@asynccontextmanager
async def lifespan(_: FastAPI):
    thread = threading.Thread(target=start_bg_processing, daemon=True)
    thread.start()
    yield


app = FastAPI(lifespan=lifespan)

# Create auth middleware
auth_middleware = AuthMiddleware(env.users, env.api_keys)

# Create services
config_service = ConfigService(env.storage, env.users)
repos_service = RepositoriesService(env.storage)
observations_service = ObservationsService(env.observations)
websites_service = WebSitesService(env.storage)

# Include routers with authentication
app.include_router(
    config_service.router,
    prefix="/api/v1",
    dependencies=[Depends(auth_middleware.verify_token)]
)
app.include_router(
    repos_service.router,
    prefix="/api/v1",
    dependencies=[Depends(auth_middleware.verify_token)]
)
app.include_router(
    observations_service.router,
    prefix="/api/v1",
    dependencies=[Depends(auth_middleware.verify_token)]
)
app.include_router(
    websites_service.router,
    prefix="/api/v1",
    dependencies=[Depends(auth_middleware.verify_token)]
)

origins = [
    "http://localhost:5173",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all origins (not recommended for prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def start_fastapi_server():
    import uvicorn
    port = 8090
    uvicorn_config = uvicorn.Config("dev_observer.server.main:app", host="0.0.0.0", port=port, log_level="debug")
    uvicorn_server = uvicorn.Server(uvicorn_config)
    _log.info(s_("Starting FastAPI server...", port=port))
    await uvicorn_server.serve()

def start_all():
    async def start():
        await start_fastapi_server()

    asyncio.run(start())


if __name__ == "__main__":
    start_all()


def _get_git_root() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout.strip()
