greeting = """
 /$$   /$$           /$$ /$$                
| $$  | $$          | $$| $$                
| $$  | $$  /$$$$$$ | $$| $$  /$$$$$$       
| $$$$$$$$ /$$__  $$| $$| $$ /$$__  $$      
| $$__  $$| $$$$$$$$| $$| $$| $$  \ $$      
| $$  | $$| $$_____/| $$| $$| $$  | $$      
| $$  | $$|  $$$$$$$| $$| $$|  $$$$$$/      
|__/  |__/ \_______/|__/|__/ \______/       
                                            
                                            
                                            
 /$$      /$$                               
| $$$    /$$$                               
| $$$$  /$$$$ /$$   /$$ /$$$$$$/$$$$        
| $$ $$/$$ $$| $$  | $$| $$_  $$_  $$       
| $$  $$$| $$| $$  | $$| $$ \ $$ \ $$       
| $$\  $ | $$| $$  | $$| $$ | $$ | $$       
| $$ \/  | $$|  $$$$$$/| $$ | $$ | $$       
|__/     |__/ \______/ |__/ |__/ |__/
"""

import logging
import sys
import os
from dotenv import load_dotenv

from irc.bot import SingleServerIRCBot

load_dotenv()


# config



def _get_logger():
    logger_name = 'vbot'
    logger_level = logging.DEBUG
    log_line_format = '%(asctime)s | %(name)s - %(levelname)s : %(message)s'
    log_line_date_format = '%Y-%m-%dT%H:%M:%SZ'
    logger_ = logging.getLogger(logger_name)
    logger_.setLevel(logger_level)
    logging_handler = logging.StreamHandler(stream=sys.stdout)
    logging_handler.setLevel(logger_level)
    logging_formatter = logging.Formatter(log_line_format, datefmt=log_line_date_format)
    logging_handler.setFormatter(logging_formatter)
    logger_.addHandler(logging_handler)
    return logger_

logger = _get_logger()


class VBot(SingleServerIRCBot):
    VERSION = '1.0.0'

    def __init__(self, host, port, nickname, password, channel):
        logger.debug('VBot.__init__ (VERSION = %r)', self.VERSION)
        SingleServerIRCBot.__init__(self, [(host, port, password)], nickname, nickname)
        self.channel = channel
        self.viewers = []

    def on_welcome(self, connection, event):
        connection.join(self.channel)
        connection.privmsg(event.target, "YOUR MUM IS LOADING")

    def on_join(self, connection, event):
        nickname = self._parse_nickname_from_twitch_user_id(event.source)
        self.viewers.append(nickname)

        if nickname.lower() == connection.get_nickname().lower():
            connection.privmsg(event.target, '<BOT LOADING SUCCESSFULL>')

    def on_part(self, connection, event):
        nickname = self._parse_nickname_from_twitch_user_id(event.source)
        self.viewers.remove(nickname)

    def on_pubmsg(self, connection, event):
        message = event.arguments[0]
        logger.debug('message = %r', message)
        # Respond to messages starting with !
        if message.startswith("!"):
            self.do_command(event, connection, message[1:])

    def do_command(self, event, connection, message):
        message_parts = message.split()
        command = message_parts[0]
        
        logger.debug('VBot.do_command (command = %r)', command)

        if command == "version":
            version_message = 'Version: %s' % self.VERSION
            self.connection.privmsg(event.target, version_message)
        if command == "count_viewers":
            num_viewers = len(self.viewers)
            num_viewers_message = 'Viewer count: %d' % num_viewers
            self.connection.privmsg(event.target, num_viewers_message)
        elif command == 'die':
            connection.privmsg(event.target, '*** crying in pain ***')
            self.die(msg="the guy was killed")
        else:
            logger.error('Unrecognized command: %r', command)

    @staticmethod
    def _parse_nickname_from_twitch_user_id(user_id):
        # nickname!username@nickname.tmi.twitch.tv
        return user_id.split('!', 1)[0]


def main():
    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    CHANNEL = os.getenv("CHANNEL")
    my_bot = VBot(HOST, PORT, USERNAME, PASSWORD, CHANNEL)
    my_bot.start()


if __name__ == '__main__':
    print(greeting)
    main()
