import argparse
import pathlib
import logging
import datetime
import contextlib

from .papmonitor import PAPMonitor


def get_args(arg_str=None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument('log',
            help='debug|info|warning|error|critical',
            default='debug',
            nargs='?',
            )
    argparser.add_argument('logfile',
            help='stdout|timestamp',
            default='timestamp',
            nargs='?',
            )
    argparser.add_argument('start',
            help='hours:minutes in military',
            #default='23:00',
            default='00:01',
            nargs='?',
            )
    argparser.add_argument('stop',
            help='hours:minutes in military',
            #default='6:00',
            default='16:00',
            nargs='?',
            )
    return argparser.parse_args(arg_str) 

def get_log_filename(args):
    if args.logfile == 'stdout':
        return None
    package_folder = pathlib.Path(__file__).parent.absolute()
    now = datetime.datetime.now().isoformat()
    return '%s/logs/%s.log' % (package_folder, now)

def get_log_format(args):
    return '%(relativeCreated)-7d|%(levelname)-7s|%(module)-10s|%(lineno)-4d|%(funcName)-35s|%(message)s'

def init_logging(args):
    logging.basicConfig(
            filename=get_log_filename(args),
            level=getattr(logging, args.log.upper(), None),
            format=get_log_format(args),
            )

def main(arg_str=None):
    args = get_args(arg_str)
    init_logging(args)
    logger = logging.getLogger(__name__)
    logger.debug('main')
    logger.debug(args)
    with contextlib.closing(PAPMonitor.build(args.start, args.stop)) as pm:
        pm.poll_monitor()

if __name__ == '__main__':
    main()
