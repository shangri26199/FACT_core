# -*- coding: utf-8 -*-
import argparse
import configparser
import logging

from common_helper_files import create_dir_for_file

from helperFunctions.config import get_config_dir
from version import __VERSION__


def _setup_argparser(name, description):
    parser = argparse.ArgumentParser(description="{} - {}".format(name, description))
    parser.add_argument('-V', '--version', action='version', version="{} {}".format(name, __VERSION__))
    parser.add_argument("-l", "--log_file", help="path to log file", default=None)
    parser.add_argument("-L", "--log_level", help="define the log level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default=None)
    parser.add_argument("-d", "--debug", action="store_true", default=False, help="print debug messages")
    parser.add_argument("-s", "--silent", action="store_true", default=False, help="don't log to command line")
    parser.add_argument("-C", "--config_file", help="set path to config File", default="{}/main.cfg".format(get_config_dir()))
    return parser.parse_args()


def _get_console_output_level(debug_flag):
    if debug_flag:
        return logging.DEBUG
    else:
        return logging.INFO


def _setup_logging(config, args):
    log_level = getattr(logging, config['Logging']['logLevel'], None)
    log_format = logging.Formatter(fmt="[%(asctime)s][%(module)s][%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    create_dir_for_file(config['Logging']['logFile'])
    file_log = logging.FileHandler(config['Logging']['logFile'])
    file_log.setLevel(log_level)
    file_log.setFormatter(log_format)
    logger.addHandler(file_log)

    if not args.silent:
        console_log = logging.StreamHandler()
        console_log.setLevel(_get_console_output_level(args.debug))
        console_log.setFormatter(log_format)
        logger.addHandler(console_log)


def _load_config(args):
    config = configparser.ConfigParser()
    config.read(args.config_file)
    if args.log_file is not None:
        config['Logging']['logFile'] = args.log_file
    if args.log_level is not None:
        config['Logging']['logLevel'] = args.log_level
    return config
