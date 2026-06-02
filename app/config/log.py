import logging.config
from pathlib import Path
import json
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as install_traceback
import logging

Path("logs").mkdir(exist_ok=True)
install_traceback()


class RichHandlerWrapper(RichHandler):
    def __init__(self, **kwargs):
        console = Console(width=160)
        super().__init__(console=console, **kwargs)


def setup_logging():
    config_path = Path(__file__).parent / "log.json"

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    logging.config.dictConfig(config)


logger = logging.getLogger("app")
