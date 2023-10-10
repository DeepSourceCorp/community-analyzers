import logging
import os

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def initialize(disable_logging_exceptions=False):
    """Initialize sentry."""
    sentry_integrations = []
    if disable_logging_exceptions:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=None,
        )
        sentry_integrations.append(sentry_logging)
    sentry_sdk.init(
        os.getenv("SENTRY_DSN"),
        integrations=sentry_integrations,
        default_integrations=False,
    )
    sentry_sdk.init = lambda *_, **__: None
    sentry_sdk.utils.MAX_STRING_LENGTH = 8192  # undocumented truncation length


def raise_error(err):
    """Raise a sentry error."""
    sentry_sdk.capture_exception(err)


def raise_info(message, context=None):
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
