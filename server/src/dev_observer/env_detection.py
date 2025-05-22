import logging
from typing import Optional, Tuple

from github import Auth

from dev_observer.analysis.langgraph_provider import LanggraphAnalysisProvider
from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.log import s_
from dev_observer.processor.processor import Processor
from dev_observer.prompts.langfuse import LangfusePromptsProvider
from dev_observer.prompts.local import LocalPromptsProvider, PromptTemplateParser, TomlPromptTemplateParser, \
    JSONPromptTemplateParser
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.repository.github import GithubProvider
from dev_observer.settings import Settings, LocalPrompts

_log = logging.getLogger(__name__)


def detect_github_provider(settings: Settings) -> GithubProvider:
    return GithubProvider(detect_github_auth(settings))


def detect_github_auth(settings: Settings) -> Auth:
    gh = settings.github
    if gh is None:
        raise ValueError(f"Github settings are not defined")
    _log.debug(s_("Detected github auth type.", auth_type=gh.auth_type))
    match gh.auth_type:
        case "token":
            return Auth.Token(gh.personal_token)
    raise ValueError(f"Unsupported auth type: {gh.auth_type}")


def detect_analysis_provider(settings: Settings) -> AnalysisProvider:
    a = settings.analysis
    if a is None:
        raise ValueError("Analysis settings are not defined")
    match a.provider:
        case "langgraph":
            return LanggraphAnalysisProvider()
    raise ValueError(f"Unsupported analysis provider: {a.provider}")


def detect_prompts_provider(settings: Settings) -> PromptsProvider:
    p = settings.prompts
    if p is None:
        raise ValueError("Prompts settings are not defined")
    match p.provider:
        case "langfuse":
            lf = p.langfuse
            if lf is None:
                raise ValueError("Missing langfuse config for langfuse prompts provider")
            return LangfusePromptsProvider(lf.auth.secret_key, lf.auth.public_key, lf.host, lf.default_label)
        case "local":
            parser, ext = detect_prompts_parser(p.local)
            return LocalPromptsProvider(p.local.dir, ext, parser)
    raise ValueError(f"Unsupported prompts provider: {p.provider}")


def detect_prompts_parser(loc: LocalPrompts) -> Tuple[PromptTemplateParser, str]:
    match loc.parser:
        case "toml":
            return TomlPromptTemplateParser(), ".toml"
        case "json":
            return JSONPromptTemplateParser(), ".json"
    raise ValueError(f"Unsupported parser type: {loc.parser}")

def detect_processor(settings: Settings) -> Processor:
    return Processor(
        analysis=detect_analysis_provider(settings),
        repository=detect_github_provider(settings),
        prompts=detect_prompts_provider(settings),
    )
