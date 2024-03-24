import logging
import os
from datetime import datetime

from src.fileUtils import get_log_filename


def setup_logger(user_config, author: str, number: int):
    # add up time to formatter
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.uptime = datetime.fromtimestamp(record.relativeCreated / 1000).strftime('%Mm%Ss')
        return record

    logging.setLogRecordFactory(record_factory)

    filename = get_log_filename(user_config.username, author, number)
    os.makedirs(filename.parent, exist_ok=True)
    logging.basicConfig(filename=filename, level=logging.INFO, format='%(uptime)s %(message)s')