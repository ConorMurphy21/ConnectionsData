import json
import logging
import logging.config
import os
from datetime import datetime, timedelta
from pathlib import Path

from src.fileUtils import get_logfile_dir

log_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(uptime)s %(message)s',
        },
        'json': {
            '()': 'src.jsonLogFormatter.JsonFormatter',
            'fmt_keys': {
                'uptime': 'uptime',
            }
        }
    },
    'handlers': {
        'human': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'filename': 'WILL BE OVERWRITTEN',
        },
        'machine': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'json',
            'filename': 'WILL BE OVERWRITTEN',
        }
    },
    'loggers': {
        'root': {
            'level': 'DEBUG',
            'handlers': [
                'human',
                'machine'
            ]
        }
    }
}


def _get_last_uptime(logfile: Path):
    if not logfile.exists():
        return timedelta()
    with open(logfile, 'r') as f:
        line = None
        for line in f:
            pass
        if not line:
            return timedelta()
        json_line = json.loads(line)
        if 'uptime' in json_line:
            mins, secs = json_line['uptime'][0:2], json_line['uptime'][3:5]
            return timedelta(minutes=int(mins) + 1, seconds=int(secs))
        else:
            return timedelta()


def setup_logger(user_config, author: str, number: int):
    log_dir = get_logfile_dir(user_config.username, author, number)
    machine_file = log_dir / 'machine.jsonl'
    human_file = log_dir / 'human.log'

    last_uptime = _get_last_uptime(machine_file)

    # add up time to formatter
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.uptime = (datetime.fromtimestamp(record.relativeCreated / 1000) + last_uptime).strftime('%Mm%Ss')
        return record

    logging.setLogRecordFactory(record_factory)

    log_config['handlers']['machine']['filename'] = str(machine_file)
    log_config['handlers']['human']['filename'] = str(human_file)
    os.makedirs(log_dir, exist_ok=True)
    logging.config.dictConfig(log_config)
