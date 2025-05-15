import logging
from typing import Optional

import colorama
import structlog
from structlog.stdlib import BoundLogger

from dev_observer.common.env import is_dev

LOG_FORMAT = "[agents] [%(asctime)s] %(levelname)s - %(name)s: %(message)s"

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,  # Default log level
    format=LOG_FORMAT,  # Use the defined format
    datefmt="%Y-%m-%d %H:%M:%S"  # Timestamp format
)

logging.getLogger("httpx").setLevel(logging.WARNING)


def add_prefix(logger, method_name, event_dict):
    event_dict["app_name"] = "agents"
    return event_dict


cr = structlog.dev.ConsoleRenderer(
    columns=[
        structlog.dev.Column(
            "app_name",
            structlog.dev.KeyValueColumnFormatter(
                key_style=None,
                value_style=colorama.Style.RESET_ALL,
                reset_style=colorama.Style.RESET_ALL,
                value_repr=lambda v: f"[{v}]",
            ),
        ),
        # Render the timestamp without the key name in yellow.
        structlog.dev.Column(
            "timestamp",
            structlog.dev.KeyValueColumnFormatter(
                key_style=None,
                value_style=colorama.Fore.BLUE,
                reset_style=colorama.Style.RESET_ALL,
                value_repr=lambda v: f"[{v}]",
            ),
        ),
        structlog.dev.Column(
            "level",
            structlog.dev.KeyValueColumnFormatter(
                key_style=None,
                value_style=colorama.Style.RESET_ALL,
                reset_style=colorama.Style.RESET_ALL,
                value_repr=lambda v: f"[{v}]",
            ),
        ),
        structlog.dev.Column(
            "log",
            structlog.dev.KeyValueColumnFormatter(
                key_style=None,
                value_style=colorama.Style.RESET_ALL,
                reset_style=colorama.Style.RESET_ALL,
                value_repr=str,
                postfix=":"
            ),
        ),
        # Render the event without the key name in bright magenta.
        structlog.dev.Column(
            "event",
            structlog.dev.KeyValueColumnFormatter(
                key_style=None,
                value_style=colorama.Style.RESET_ALL,
                reset_style=colorama.Style.RESET_ALL,
                value_repr=str,
            ),
        ),
        # Default formatter for all keys not explicitly mentioned. The key is
        # cyan, the value is green.
        structlog.dev.Column(
            "",
            structlog.dev.KeyValueColumnFormatter(
                key_style=colorama.Fore.GREEN,
                value_style=colorama.Fore.GREEN,
                reset_style=colorama.Style.RESET_ALL,
                value_repr=lambda v: f"[{v}]",
            ),
        ),
    ]
)

IS_DEV = is_dev()

print(f"IS_DEV: {IS_DEV}")


def stackdriver_severity(logger, method_name, event_dict):
    level = event_dict.pop("level", method_name).upper()
    event_dict["severity"] = level
    return event_dict


def rename_event_to_message(logger, method_name, event_dict):
    if "event" in event_dict:
        event_dict["message"] = event_dict.pop("event")
    return event_dict


if IS_DEV:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            add_prefix,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            cr
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False
    )
else:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            add_prefix,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            stackdriver_severity,
            rename_event_to_message,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False
    )


def dynamic_logger(log: Optional[str] = None) -> BoundLogger:
    result = structlog.get_logger().bind()
    result = structlog.wrap_logger(
        result._logger,  # Access underlying stdlib logger
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG if IS_DEV else logging.INFO),
    )
    if log:
        result = result.bind(log=log)
    return result


def setup_log():
    # exists just for side effect
    pass
