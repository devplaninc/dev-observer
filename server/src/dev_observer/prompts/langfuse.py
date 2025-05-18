import logging
import os
from typing import Optional, Dict

from dev_observer.ai import PromptsProvider, FormattedPrompt
from dev_observer.log import s_

_log = logging.getLogger(__name__)


class LangfusePromptsProvider(PromptsProvider):


    def get_formatted(self, name: str, params: Optional[Dict[str, str]] = None) -> FormattedPrompt:
        label = os.environ.get("LANGFUSE_PROMPT_LABEL")
        _log.debug(s_("Retrieving Langfuse prompt template", template=name, label=label))
        prompt = _fetch_prompt(name)
        model_config: Optional[ModelConfig] = None
        try:
            if prompt.config is not None:
                parsed_config = json_format.ParseDict(prompt.config, ModelConfig())
                if parsed_config.type > 0:
                    model_config = parsed_config
                    _log.debug("Loaded custom model config", model_config=prompt.config)
        except Exception as e:
            _log.warning("Failed to parse model config", exc_info=e, model_config=prompt.config)
        chat_prompt = prompt.compile(**kwargs)
        system: Optional[str] = None
        user: Optional[str] = None
        for p in chat_prompt:
            if p.get("role") == "system":
                system = p.get("content")
            if p.get("role") == "user":
                user = p.get("content")
        return FormattedPrompt(system=system, user=user, model_config=model_config, langfuse_prompt=prompt)