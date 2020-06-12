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
            default='info',
            nargs='?'
            )
    return argparser.parse_args(arg_str) 

def init_logging(args):
    package_folder = pathlib.Path(__file__).parent.absolute()
    now = datetime.datetime.now().isoformat()
    logging.basicConfig(
            filename='%s/logs/%s.log' % (package_folder, now),
            level=getattr(logging, args.log.upper(), None),
            format=f'%(asctime)-25s:%(levelname)-10s:%(message)s',
            datefmt="%Y-%m-%dT%H:%M:%S%z",
            )

def main(arg_str=None):
    args = get_args(arg_str)
    init_logging(args)
    logger = logging.getLogger(__name__)
    logger.debug('main')
    foo
    with contextlib.closing(PAPMonitor.build('../data/resmed', '23:00', '6:00')) as pm:
        pm.poll_monitor()

if __name__ == '__main__':
    main()
