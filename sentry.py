import os
import logging

import sentry_sdk
import sentry_sdk.utils


logger = logging.getLogger("community_analyzer")
# Configure the logging format to also include file, linenum.
logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)


def initialize() -> None:
    """Initialize sentry."""
    sentry_sdk.init(
        os.getenv("SENTRY_DSN"), integrations=[], default_integrations=False
    )
    sentry_sdk.init = lambda *_, **__: None  # type: ignore
    sentry_sdk.utils.DEFAULT_MAX_VALUE_LENGTH = 8192  # type: ignore


def raise_error(err: Exception) -> None:
    """Raise a sentry error."""
    sentry_sdk.capture_exception(err)


def raise_info(message: str, context: dict[str, object] | None = None) -> None:
    """
    Capture a message and show in sentry as Info.

    Additionaly, set extra contexts sent in context.
    Context would be a dict with context name as key, value is context_value.
    """
    with sentry_sdk.configure_scope() as scope:
        scope.level = "info"
        if context:
            for context_name, context_value in context.items():
                scope.set_extra(context_name, context_value)
        # Capture the message
        sentry_sdk.capture_message(message)

    # Add a log for this
    logger.info(message, extra=context)
