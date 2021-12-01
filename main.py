import logging.handlers
import os
from logging import DEBUG

import telegram.bot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram.ext import (
    Updater,
    MessageHandler,
    Filters,
)
from telegram.ext import messagequeue as mq
from telegram.utils.request import Request

from db_module import Base, User, ImageMessage
from face_detector import FaceDetector

DIR_MAIN = os.getcwd()
DATA_DIR = os.path.join(DIR_MAIN, "data")
LOG_DIR = os.path.join(DIR_MAIN, "log")
IMAGE_DIR = os.path.join(DATA_DIR, "img")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")

FACE_DETECTION_XML_PATH = os.path.join(DIR_MAIN, 'data',
                                       'haarcascade_frontalface_default.xml')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

loggers = ["bot", "face_detector", "audio"]
for log_name in loggers:
    logger = logging.getLogger(log_name)
    logger.setLevel(DEBUG)
    filename = os.path.join(LOG_DIR, f"{log_name}.log")
    print(f"Filename :{filename}")
    fh = logging.handlers.RotatingFileHandler(
        filename, maxBytes=1024 * 1024 * 40, backupCount=2
    )
    formatter = logging.Formatter("%(levelname)s: %(asctime)s %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

logger = logging.getLogger("bot")


class TestBot(telegram.bot.Bot):
    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(TestBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

        engine = create_engine('sqlite:///dbase.db', echo=True, future=True)
        connection = engine.connect()
        session = sessionmaker(bind=engine)
        Base.metadata.create_all(bind=connection.engine)
        self.session = session()
        self.face_detector = FaceDetector(FACE_DETECTION_XML_PATH)

        self.upd = Updater(bot=self, use_context=True)
        self.dp = self.upd.dispatcher
        self.dp.add_handler(MessageHandler(Filters.photo, self.image_handler))
        self.dp.add_handler(MessageHandler(Filters.voice, self.audio_handler))

        self.dp.add_error_handler(self.error)
        self.upd.start_polling()
        self.upd.idle()

    def audio_handler(self, update, context):
        user_id = update.message.chat_id
        username = update.message.from_user.username
        logger.info(f"get voice from user: {user_id}")

        file_id = update.message.voice.file_id
        audio_name = f"{user_id}_{file_id}.ogg"
        audio_path = os.path.join(AUDIO_DIR, audio_name)
        with open(audio_path, "wb") as f:
            context.bot.get_file(file_id).download(out=f)
        logger.info(f"end voice from user: {user_id}")

        self.send_message(user_id, text="end voice")

    def image_handler(self, update, context):
        # import code
        # code.interact(local=locals())
        user_id = update.message.chat_id
        username = update.message.from_user.username
        logger.info(f"get image from user: {user_id}")

        file_id = update.message.photo[-1].file_id
        img_name = f"{user_id}_{file_id}.jpg"
        img_path = os.path.join(IMAGE_DIR, img_name)
        with open(img_path, "wb") as f:
            context.bot.get_file(file_id).download(out=f)
        ret = self.face_detector.is_face_exist(img_path)
        if ret:
            msg = "your image was saved"
            user = self.if_user_exists(user_id)
            if not user:
                user = User(user_id=user_id, username=username)
                self.session.add(user)
            self.session.add(
                ImageMessage(user=user.user_id, img_path=img_path)
            )
            self.session.commit()
            self.send_message(user_id, text=msg)
        else:
            os.remove(img_path)
        # file = context.bot.getFile(update.message.photo[-1].file_id).download(out=f)
        logger.info(f"end image from user: {user_id}")

    def if_user_exists(self, user_id):
        user = self.session.query(User).filter(User.user_id == user_id).first()
        return user

    def error(self, update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            logger.exception("smth strange happen in stop message que")
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments"""
        return super(TestBot, self).send_message(*args, **kwargs)


if __name__ == "__main__":
    token = "2102450191:AAFDknFs1wm0IFfr3EmYbhDGhRUBwFrgx3U"
    q = mq.MessageQueue(all_burst_limit=20, all_time_limit_ms=1500)
    request = Request(con_pool_size=8)
    test_bot = TestBot(token, request=request, mqueue=q)
