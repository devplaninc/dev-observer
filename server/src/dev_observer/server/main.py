import asyncio
import logging
import subprocess

from fastapi import FastAPI, Request

import dev_observer.log
from dev_observer.api.web.observations_pb2 import GetObservationsResponse, AddGithubRepositoryRequest, \
    AddGithubRepositoryResponse
from dev_observer.env_detection import detect_server_env
from dev_observer.server.env import ServerEnv
from dev_observer.settings import Settings
from dev_observer.util import pb_to_json, parse_dict_pb

dev_observer.log.encoder = dev_observer.log.PlainTextEncoder()
logging.basicConfig(level=logging.DEBUG)
from dev_observer.log import s_

_log = logging.getLogger(__name__)
Settings.model_config["toml_file"] = "default_config.toml"
env: ServerEnv = detect_server_env(Settings())

app = FastAPI()


@app.get("/api/v1/observations/{kind}")
async def get_observations(kind: str):
    keys = await env.observations.list(kind=kind)
    return pb_to_json(GetObservationsResponse(keys=keys))


@app.post("/api/v1/repositories")
async def add_repo(req: Request):
    request = parse_dict_pb(await req.json(), AddGithubRepositoryRequest())
    _log.debug(s_("Adding repository", request=request))
    await env.storage.add_github_repo(request.repo)

    return pb_to_json(AddGithubRepositoryResponse())


async def start_fastapi_server():
    import uvicorn
    port = 8090
    uvicorn_config = uvicorn.Config("dev_observer.server.main:app", host="0.0.0.0", port=port, log_level="info")
    uvicorn_server = uvicorn.Server(uvicorn_config)
    _log.info(s_("Starting FastAPI server...", port=port))
    await uvicorn_server.serve()


if __name__ == "__main__":
    async def start():
        await asyncio.gather(
            env.periodic_processor.run(),
            start_fastapi_server(),
        )

    asyncio.run(start())


def _get_git_root() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout.strip()
