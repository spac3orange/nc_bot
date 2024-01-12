from data import logger


class BotLocker:
    def __init__(self, status=False):
        self.status = status
        logger.warning('bot locker activated')
        logger.warning('status: unlocked')

    def lock_bot(self):
        self.status = True
        logger.warning('bot locked')


bot_lock = BotLocker()