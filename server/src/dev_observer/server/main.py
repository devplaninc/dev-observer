import asyncio
import logging
import os
import subprocess
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

import google.cloud.logging as google_logging # Added
import dev_observer.log
from dev_observer.log import StackdriverEncoder # Added
from dev_observer.env_detection import detect_server_env
from dev_observer.server.env import ServerEnv
from dev_observer.server.middleware.auth import AuthMiddleware
from dev_observer.server.services.config import ConfigService
from dev_observer.server.services.observations import ObservationsService
from dev_observer.server.services.repositories import RepositoriesService
from dev_observer.settings import Settings # Already here
# import os # Already here
# import logging # Already here

# Logging configuration will be set up after settings are loaded
from dev_observer.log import s_

_log = logging.getLogger(__name__)
Settings.model_config["toml_file"] = os.environ.get("DEV_OBSERVER_CONFIG_FILE", None)

# Initialize settings once
settings = Settings()

# Configure logging provider
# The dev_observer.log.encoder is already set based on LOGGING_PROVIDER in log.py
# Here, we initialize the Google Cloud Logging client if 'stackdriver' is chosen.

# Determine the effective logging provider
effective_logging_provider = os.environ.get("LOGGING_PROVIDER", "json").lower()
if settings.logging and settings.logging.provider:
    effective_logging_provider = settings.logging.provider.lower()

if effective_logging_provider == "stackdriver":
    try:
        # Ensure that the encoder in log.py is StackdriverEncoder if we are here.
        # This should be guaranteed by the logic in log.py
        if not isinstance(dev_observer.log.encoder, StackdriverEncoder):
            _log.warning(s_("Logging provider is stackdriver, but StackdriverEncoder is not set in log.py. Forcing it."))
            dev_observer.log.encoder = StackdriverEncoder()

        gcp_logging_client = google_logging.Client()
        # Set up Google Cloud Logging python handler
        gcp_logging_client.setup_logging(
            log_level=logging.INFO # TODO: Make this configurable from settings
        )
        _log.info(s_("Stackdriver logging client initialized and handlers configured."))
    except Exception as e:
        # Fallback to basic logging if Stackdriver setup fails
        logging.basicConfig(level=logging.INFO)
        _log.error(s_("Failed to initialize Stackdriver logging. Falling back to basicConfig.", error=str(e)))
else:
    # For other providers like 'json' or 'plaintext', basicConfig is a reasonable default.
    # The actual formatting is handled by the encoder set in dev_observer.log.py
    logging.basicConfig(level=logging.INFO) # TODO: Make this configurable
    _log.info(s_(f"Logging provider: {effective_logging_provider}. Using basicConfig with configured encoder."))

env: ServerEnv = detect_server_env(settings)


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
