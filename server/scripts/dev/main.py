import os

from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
_ = load_dotenv(f"{script_dir}/../../.env")
_ = load_dotenv(f"{script_dir}/../../.env.local")
_ = load_dotenv(f"{script_dir}/../../.env.local.secrets")


os.environ["DEV_OBSERVER_CONFIG_FILE"]=f"{script_dir}/config.toml"

if __name__ == "__main__":
    from dev_observer.server.main import start_all

    start_all()
