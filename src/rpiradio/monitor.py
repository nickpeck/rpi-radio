import logging
from threading import Thread
from time import sleep

logger = logging.getLogger()

class Monitor(Thread):

    def __init__(self, player, interval_sec=5):
        super().__init__()
        self.player = player
        self.interval_sec = interval_sec

    def run(self):
        while True:
            logger.info("Monitor thread - awakened")
            state = self.player.index().get('state', "stopped")
            if state == "playing":
                logger.info("Monitor thread - player is playing")
                if self.player._proc is not None:
                    logger.info("Monitor thread - polling player process")
                    poll = self.player._proc.poll()
                    logger.info("Monitor thread - player process.poll() returned {}".format(poll))
                    if poll is not None:
                        logger.info("Monitor thread - process has exit code, so assumed died")
                        self.player.stop()
                        station = self.player.get_current_station()
                        if len(station) == 0:
                            return
                        self.player.play(station[0]['url'])
                        logger.info("Monitor thread - restarted player")
            sleep(self.interval_sec)
        
