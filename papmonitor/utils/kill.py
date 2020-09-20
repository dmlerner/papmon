from ..alarm import chromecast
from . import wslprocess

import logging
logger = logging.getLogger('papmonitor')

def main(name):
    global c
    logger.debug('fuck everything oh god this is good enough')
    c = chromecast.ChromeCast(name) # TODO: args
    _c = c.get_chromecast()
    if not _c:
        return
    logger.debug(dir(_c))
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
