import logging
import logging.config

# handlers set to lowest level: DEBUG, allowing all messages
# The logger may have a higher level
console_handler = {
    'class': 'logging.StreamHandler',
    'formatter': 'precise',
    'level': logging.DEBUG
}

null_handler = {
    'class': 'logging.NullHandler'
}

# this is default logging dict. It is modified before being activated
log_config = dict(
    version=1,
    disable_existing_loggers=False,
    formatters={
        'precise': {
            'format': u'%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] (%(threadName)s) %(message)s'
        }
    },
    handlers={
        'console': console_handler
    },
    loggers={
        'book_service': {
            'handlers': ['console'],
            'level': logging.info,
            'propagate': False,
        },
    },
    root={
        'handlers': ['console'],
        'level': logging.DEBUG,
        'propagate': True,
    }
)

def _configure_log_levels(loglevel):
    if not loglevel:
        return

    level_mapping = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL}
    level = level_mapping[loglevel]
    log_config['root']['level'] = level

    for logger in log_config['loggers']:
        log_config['loggers'][logger]['level'] = level

def set_log_level(program_mode, loglevel=None):
    if program_mode == 'prod':
        loglevel = 'info'
    else:
        loglevel = 'debug'

    _configure_log_levels(loglevel)

    logging.config.dictConfig(log_config)
