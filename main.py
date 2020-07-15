#!/usr/bin/env python

"""
Entry point for python server.
"""
import sys
import logging
import argparse


from app import app_config
from app.server import initialize_app
from app.logging_config import set_log_level

log = logging.getLogger(__name__)

APPLICATION_MODES = {
    'prod': app_config.Config,
    'dev': app_config.DevelopmentConfig,
    'test': app_config.TestingConfig
}


def setup_argparser():
    parser = argparse.ArgumentParser(prog='Python-Server', description='Python Server Component')
    parser.add_argument(
        '--mode', choices=APPLICATION_MODES.keys(), default='prod', help='Application run mode'
    )
    return parser


def main():
    """
    Run the flask app
    """
    parser = setup_argparser()
    args = parser.parse_args()
    config = APPLICATION_MODES[args.mode]

    set_log_level(args.mode)
    flask_app = initialize_app(config)

    if args.mode == 'prod':
        use_reloader = False
    else:
        use_reloader = True

    #flask_app.run(debug=config.FLASK_DEBUG, host=config.SERVER_HOST, port=config.SERVER_PORT, use_reloader=use_reloader)
    flask_app.run(debug=True, host=config.SERVER_HOST, port=config.SERVER_PORT, use_reloader=True)
    return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
