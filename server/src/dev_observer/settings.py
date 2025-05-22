import logging
from typing import Optional, Tuple, Literal, ClassVar

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, TomlConfigSettingsSource

from dev_observer.log import s_

_log = logging.getLogger(__name__)


class Github(BaseModel):
    auth_type: Literal["token"]
    personal_token: Optional[str] = None


class LangfuseAuth(BaseModel):
    secret_key: str
    public_key: str


class LangfusePrompts(BaseModel):
    auth: LangfuseAuth
    host: str
    default_label: Optional[str] = None


class LocalPrompts(BaseModel):
    dir: str
    parser: Literal["toml", "json"] = "toml"


class Prompts(BaseModel):
    provider: Literal["langfuse", "local"]
    langfuse: Optional[LangfusePrompts] = None
    local: Optional[LocalPrompts] = None


class Analysis(BaseModel):
    provider: Literal["langgraph"]


class SettingsProps(BaseModel):
    toml_file: Optional[str] = None


class Settings(BaseSettings):
    props: ClassVar[SettingsProps] = SettingsProps()

    github: Optional[Github] = None
    prompts: Optional[Prompts] = None
    analysis: Optional[Analysis] = None

    def __init__(self) -> None:
        toml_file = Settings.model_config.get("toml_file", None)
        Settings.model_config = SettingsConfigDict(
            env_prefix='dev_observer__',
            env_nested_delimiter='__',
            toml_file=toml_file,
        )
        super().__init__()

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        toml_file = Settings.model_config.get("toml_file", None)
        _log.debug(s_("Loading settings", toml_file=toml_file))
        if toml_file is not None:
            toml_provider = TomlConfigSettingsSource(Settings, toml_file)
            return init_settings, toml_provider, env_settings, dotenv_settings, file_secret_settings
        return init_settings, env_settings, dotenv_settings, file_secret_settings
