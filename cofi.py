import argparse
import json
import logging
import os
from logging.handlers import RotatingFileHandler

from cofibot import SlackBot

log = logging.getLogger(__name__)

NO_LOGGING = 100

nameToLoggingLevel = {
    'NONE': NO_LOGGING,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG
}


def _get_logging_level(name):
    if not name:
        return nameToLoggingLevel['NONE']
    return nameToLoggingLevel[name]


def parse_config(config_file):
    log.info('Loading %s', config_file)
    with open(config_file) as f:
        return json.load(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse args')
    parser.add_argument('-c', '--config-file', type=str, default='config/config.json', help='Path to config file')

    # logging levels
    parser.add_argument('-ll', '--log-level',
                        help='Global Logging level (NONE, ERROR, WARNING, INFO, DEBUG). '
                             'Overrides -q and -v')
    parser.add_argument('-fll', '--file-log-level',
                        help='Logging level for file logging. (NONE, ERROR, WARNING, INFO, DEBUG). '
                             'Overrides -q and -v')
    parser.add_argument('-cll', '--console-log-level',
                        help='Logging level for console logging. (NONE, ERROR, WARNING, INFO, DEBUG).'
                             ' Overrides -q and -v')

    # logging verbosity. overridden by above args
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-q', '--quiet', action='store_true', help='Enable quiet logging (Errors only)')
    verbosity.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if args.log_level and (args.file_log_level or args.console_log_level):
        raise RuntimeError("You cannot specify -fll or -cll if -ll is specified")

    args.log_level = _get_logging_level(args.log_level)
    args.console_log_level = _get_logging_level(args.console_log_level)
    args.file_log_level = _get_logging_level(args.file_log_level)

    if args.log_level == NO_LOGGING \
            and args.console_log_level == NO_LOGGING \
            and args.file_log_level == NO_LOGGING:
        if args.quiet:
            args.log_level = logging.ERROR
        elif args.verbose:
            args.log_level = logging.DEBUG
        else:
            args.log_level = logging.INFO

    root = logging.getLogger()
    root.setLevel(logging.WARNING)

    # lowest common logging level determines what we set in the loggers level.
    # Handlers may have a higher logging level.
    lowest_common_logging_level = min(args.file_log_level,
                                      args.console_log_level,
                                      args.log_level)

    formatter = logging.Formatter('%(asctime)s %(levelname)s '
                                  '[%(threadName)s][%(name)s] - %(message)s')

    if args.log_level < NO_LOGGING or args.console_log_level < NO_LOGGING:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        if args.console_log_level < NO_LOGGING:
            console_handler.setLevel(args.console_log_level)
        root.addHandler(console_handler)

    if args.log_level < NO_LOGGING or args.file_log_level < NO_LOGGING:
        # rotating files with 10 mb sized logs, keeping 5 backups
        megabyte = 1024 * 1024
        os.makedirs(name='log', exist_ok=True)
        file_handler = RotatingFileHandler(filename='log/cofi.log', encoding='utf8', maxBytes=10 * megabyte,
                                           backupCount=5)
        file_handler.setFormatter(formatter)
        if args.file_log_level < NO_LOGGING:
            file_handler.setLevel(args.file_log_level)
        root.addHandler(file_handler)

    # Root level, don't set lower than INFO
    logging.getLogger().setLevel(max(logging.INFO, lowest_common_logging_level))

    # Application
    logging.getLogger('cofibot').setLevel(lowest_common_logging_level)

    # SQLAlchemy, don't set lower than INFO
    if lowest_common_logging_level < logging.INFO:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    else:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

    config = parse_config(args.config_file)
    cofi = SlackBot(config)
    cofi.start()
