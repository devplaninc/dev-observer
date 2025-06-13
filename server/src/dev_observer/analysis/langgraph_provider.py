import asyncio
import dataclasses
import logging
from typing import Optional, List, Union

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langfuse.callback import CallbackHandler
from langgraph.constants import END
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.store.memory import InMemoryStore
from langgraph.utils.config import ensure_config
from pydantic import BaseModel

from dev_observer.analysis.provider import AnalysisProvider, AnalysisResult
from dev_observer.api.types.ai_pb2 import ModelConfig
from dev_observer.log import s_
from dev_observer.prompts.provider import FormattedPrompt

_log = logging.getLogger(__name__)


@dataclasses.dataclass
class AnalysisInfo:
    prompt: FormattedPrompt

    def append(self, config: RunnableConfig) -> RunnableConfig:
        md = config.get("metadata", {})
        md[AnalysisInfo.get_key()] = self
        config["metadata"] = md
        return config

    @classmethod
    def get_key(cls):
        return "dev_observer:analysis_info"

    @classmethod
    def from_config(cls, config: RunnableConfig) -> "AnalysisInfo":
        metadata = config.get("metadata", {})
        info = metadata.get(AnalysisInfo.get_key())
        if info is None:
            _log.warning(s_("No analysis info in metadata", metadata=metadata))
            raise ValueError("No analysis info in metadata")
        return info


class LanggraphAnalysisProvider(AnalysisProvider):
    async def analyze(self, prompt: FormattedPrompt) -> AnalysisResult:
        g = await _get_graph()
        info = AnalysisInfo(prompt=prompt)
        config = info.append(ensure_config())
        callbacks = [CallbackHandler()]
        config["callbacks"] = callbacks
        result = await g.ainvoke({}, config, output_keys=["response"])
        analysis = result.get("response", "")
        _log.debug(s_("Content analyzed", anaysis_len=len(analysis)))
        return AnalysisResult(analysis=analysis)


_in_memory_store = InMemoryStore()

_lock = asyncio.Lock()
_graph: Optional[CompiledStateGraph] = None


async def _get_graph() -> CompiledStateGraph:
    global _lock
    async with _lock:
        global _graph
        if _graph is not None:
            return _graph

        nodes = AnalysisNodes()
        workflow = StateGraph(AnalysisNodes)
        workflow.add_node("analyze", nodes.analyze)
        workflow.add_edge("analyze", END)
        workflow.set_entry_point("analyze")

        _graph = workflow.compile()
        return _graph


class AnalysisState(BaseModel):
    response: Optional[str] = None


class AnalysisNodes:
    async def analyze(self, _: AnalysisState, config: RunnableConfig):
        info = AnalysisInfo.from_config(config)
        prompt = info.prompt
        prompt_config = prompt.config
        if prompt_config is None or prompt_config.model is None:
            raise ValueError("Missing model in prompt config")

        messages: List[BaseMessage] = []
        if prompt.system is not None:
            messages.append(SystemMessage(content=prompt.system.text))
        if prompt.user is not None:
            contents: List[Union[str, dict]] = []
            text = prompt.user.text
            image_url = prompt.user.image_url
            if text is not None and len(text) > 0:
                contents.append({"type": "text", "text": text})
            if image_url is not None and len(image_url) > 0:
                contents.append({"type": "image_url", "image_url": {"url": image_url}})
            messages.append(HumanMessage(content=contents))

        model = _model_from_config(prompt_config.model)
        _log.debug(s_("Calling model", prompt_config=prompt_config))
        response = await model.ainvoke(messages)
        _log.debug(s_("Model replied", prompt_config=prompt_config))
        return {"response": f"{response.content}"}


def _model_from_config(config: ModelConfig) -> BaseChatModel:
    return init_chat_model(f"{config.provider}:{config.model_name}")
