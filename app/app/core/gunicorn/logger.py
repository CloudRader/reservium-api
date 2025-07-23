"""
Custom Gunicorn logger setup module.
"""

from logging import Formatter
from gunicorn.glogging import Logger
from core import settings


class GunicornLogger(Logger):
    """
    Custom Gunicorn logger that applies application-specific log formatting.
    """

    def setup(self, cfg) -> None:
        """
        Configure access and error log handlers with custom formatting.
        """

        super().setup(cfg)

        self._set_handler(
            log=self.access_log,
            output=cfg.accesslog,
            fmt=Formatter(fmt=settings.LOGGING.LOG_FORMAT),
        )
        self._set_handler(
            log=self.error_log,
            output=cfg.errorlog,
            fmt=Formatter(fmt=settings.LOGGING.LOG_FORMAT),
        )
