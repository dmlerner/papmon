import argparse
import pathlib
import logging
import datetime
import contextlib

from .papmonitor import PAPMonitor


def get_args(arg_str=None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--log',
            help='debug|info|warning|error|critical',
            default='debug',
            nargs='?',
            )
    argparser.add_argument('--logfile',
            help='stdout|timestamp',
            default='timestamp',
            nargs='?',
            )
    argparser.add_argument('--start',
            help='hours:minutes in military',
            default='23:00',
            nargs='?',
            )
    argparser.add_argument('--stop',
            help='hours:minutes in military',
            default='7:00',
            nargs='?',
            )
    argparser.add_argument('--window',
            default='120s',
            nargs='?',
            )
    argparser.add_argument('--grace',
            default='8m',
            nargs='?',
            )
    argparser.add_argument('--test',
            action='store_true',
            )
    argparser.add_argument('--chromecast_name',
            default='bedroom speaker',
            nargs='?',
            )
    argparser.add_argument('--media_path',
            nargs='?',
            )
    argparser.add_argument('--kill',
            action='store_true',
            )
    args = argparser.parse_args(arg_str) 
    if args.test == True:
        # be armed always
        args.start = datetime.datetime.now().strftime('%H:%M')
        args.stop = (datetime.datetime.now() - datetime.timedelta(minutes=2)).strftime('%H:%M')
        args.window = '10s'
        args.grace = '2s'
        args.log = 'debug'
        args.media_path = 'file:///C:/Users/david/google-drive/coding/papmonitor/papmonitor/alarm/audio.mp3'
    return args

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
    global pm
    args = get_args(arg_str)
    init_logging(args)
    logger = logging.getLogger('papmonitor')
    for handler in logging.root.handlers:
        handler.addFilter(logging.Filter('papmonitor'))
    logger.debug('main')
    logger.debug(args)
    if args.kill:
        logger.debug('killing')
        import pdb
        #pdb.set_trace()
        from .utils import kill
        kill.main()
        return
    with contextlib.closing(PAPMonitor.build(args.start, args.stop, args.window, args.grace, args.chromecast_name, args.media_path)) as pm:
        pm.poll_monitor()

if __name__ == '__main__':
    main()
