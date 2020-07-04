from ..alarm import chromecast
from . import wslprocess

import logging
logger = logging.getLogger('papmonitor')

def main():
    global c
    logger.debug('fuck everything oh god this is good enough')
    c = chromecast.ChromeCast('bedroom speaker') # TODO: args
    logger.debug(dir(c.get_chromecast()))
    logger.debug(c.status())
    logger.debug(c.media_status())
    c.set_volume(0)
    logger.debug(c.status())
    logger.debug(c.media_status())
    c.pause()
    #c.stop()
    logger.debug(c.status())
    logger.debug(c.media_status())
    #c.set_volume(.4)
    logger.debug(c.status())
    logger.debug(c.media_status())
    #c.pause()
    #c.stop()
    #logger.debug(c.status())
    #logger.debug(c.media_status())
    #wslprocess.kill('vlc')

if __name__ == '__main__':
    main()
