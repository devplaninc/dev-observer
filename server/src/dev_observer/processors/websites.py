import dataclasses

from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.flattening import FlatteningProcessor
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.tokenizer.provider import TokenizerProvider
from dev_observer.website.flatten import flatten_website
from dev_observer.website.provider import WebsiteCrawlerProvider


@dataclasses.dataclass
class ObservedWebsite:
    """Information about a website to be observed."""
    url: str


class WebsitesProcessor(FlatteningProcessor[ObservedWebsite]):
    """Processor for websites."""
    
    website_crawler: WebsiteCrawlerProvider
    tokenizer: TokenizerProvider
    
    def __init__(
            self,
            analysis: AnalysisProvider,
            website_crawler: WebsiteCrawlerProvider,
            prompts: PromptsProvider,
            observations: ObservationsProvider,
            tokenizer: TokenizerProvider,
    ):
        super().__init__(analysis, prompts, observations)
        self.website_crawler = website_crawler
        self.tokenizer = tokenizer
    
    async def get_flatten(self, website: ObservedWebsite, config: GlobalConfig):
        result = await flatten_website(website.url, self.website_crawler, self.tokenizer)
        return result.flatten_result