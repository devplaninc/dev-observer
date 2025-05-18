from typing import Optional, Dict, Protocol
import os

from dev_observer.ai import PromptsProvider, FormattedPrompt
from dev_observer.api.devplan.observer.types.ai_pb2 import PromptTemplate


class PromptTemplateParser(Protocol):
    def parse(self, template_body: bytes) -> PromptTemplate:
        ...


class JSONPromptTemplateParser(PromptTemplateParser):
    def parse(self, template_body: bytes) -> PromptTemplate:
        return PromptTemplate.FromString(template_body)


class LocalPromptsProvider(PromptsProvider):
    prompts_path: str
    extension: str
    parser: PromptTemplateParser

    def __init__(self, prompts_path: str, extension: str, parser: PromptTemplateParser):
        self.prompts_path = prompts_path
        self.extension = extension
        self.parser = parser

    def get_formatted(self, name: str, params: Optional[Dict[str, str]] = None) -> FormattedPrompt:
        file_path = os.path.join(self.prompts_path, f"{name}{self.extension}")
        with open(file_path, 'rb') as f:
            content = f.read()

        template = self.parser.parse(content)

        if params:
            if template.system:
                template.system.text = template.system.text.format(**params)

            if template.user and template.user.text:
                template.user.text = template.user.text.format(**params)

        return FormattedPrompt(system=template.system, user=template.user, model_config=template.model)
