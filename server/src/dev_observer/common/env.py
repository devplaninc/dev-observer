import os


def server_stage() -> str:
    return os.environ.get("SERVER_STAGE", "")


def is_dev() -> bool:
    stage = server_stage()
    print(f"STAGE: {stage}")
    return stage == "dev" or stage == "local"