#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       ircd.py
#
#       Copyright 2010 Curtis (Programble) <programble@gmail.com>
#       Copyright 2015-2017 Bruno Bord <bruno@jehaisleprintemps.net>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import socket
import time
import logging
import argparse
import configparser
from select import select
from os import environ

try:
    from omgircd3 import __version__
except ImportError:
    import importlib.util
    from os.path import dirname, join
    fullpath = join(dirname(__file__), '__init__.py')
    spec = importlib.util.spec_from_file_location("omgircd3", fullpath)
    omgircd3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(omgircd3)
    __version__ = omgircd3.__version__


# If logging level is set via the env variable
logging_level = environ.get('LOGGING_LEVEL', 'INFO')
logging_level = getattr(logging, logging_level, logging.INFO)

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging_level,
    datefmt='%Y-%m-%d %H:%M:%S %Z',
)


def load_args():
    """
    Load command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='Path to the configuration file')
    args = parser.parse_args()
    return args


def load_configuration(config_path=None):
    """
    Load configuration file
    """
    config = configparser.ConfigParser(
        default_section='server',
        defaults={
            'hostname': 'localhost',
            'name': 'omgircd3',
            'creation': 2017,
            'bind_host': '',
            'bind_port': 6667,
            'motd': 'Hello and welcome to this IRC server',
            'ping_timeout': 250.
        },
        interpolation=None,
    )
    if config_path:
        config.read(config_path)
    return config


def find_channel(channel_name, source):
    """
    Search for channel by name on the given object
    """
    name = channel_name.lower()
    for channel in source.channels:
        if channel.name.lower() == name:
            return channel
    return None


def find_user(user_name, source):
    """
    Search for a user by name on the given object
    """
    name = user_name.lower()
    for user in source.users:
        if user.nickname.lower() == name:
            return user
    return None


def is_valid_channel_name(name):
    """
    Return True if the given name is a valid channel name.
    """
    # Check channel name length
    if len(name) == 0 or len(name) > 50:
        return False

    # Check if channel name is valid
    valid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~!@#$%^&*()-=_+[]{}\\|;':\"./<>?"  # noqa
    invalid = set(name) - set(valid)
    return not bool(invalid)


def is_valid_nickname(nick):
    """
    Return True if the given name is a valid nickname.
    """
    # Check nick length
    if len(nick) == 0 or len(nick) > 16:
        return False

    valid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`^-_[]{}|\\"  # noqa
    invalid = set(nick) - set(valid)
    return not bool(invalid)


class User(object):

    NORMAL_COMMANDS = (
        "PING", "NICK", "USER", "MOTD", "PRIVMSG", "NOTICE", "JOIN",
        "PART", "NAMES", "TOPIC", "ISON", "AWAY", "MODE", "WHOIS", "WHO",
        "KICK", "VERSION", "LIST", "INVITE", "USERHOST", "QUIT",)

    def __init__(self, server, sock, address):
        self.socket = sock
        self.addr = address
        self.ip = self.addr[0]
        self.port = self.addr[1]

        self.server = server

        self.server.users.append(self)

        self.recvbuffer = ""
        self.sendbuffer = ""

        self.ping = time.time()
        self.signon = int(time.time())

        self.nickname = "*"
        self.username = "unknown"
        self.realname = "Unknown"

        if self.ip in self.server.hostcache:
            self.hostname = self.server.hostcache[self.ip]
        else:
            try:
                self.hostname = socket.gethostbyaddr(self.ip)[0]
            except Exception:
                self.hostname = self.ip
            self.server.hostcache[self.ip] = self.hostname

        self.away = False

        self.channels = []

        # Max connections per ip
        connections = [u for u in self.server.users if u.ip == self.ip]
        if len(connections) > 3:
            self.quit("Too many connections from %s" % self.ip)

        self.oper = False

    def __repr__(self):
        return "<User '%s'>" % self.fullname()

    def find_channel(self, target_name):
        return find_channel(target_name, self)

    def fileno(self):
        return self.socket.fileno()

    def fullname(self):
        return "%s!%s@%s" % (self.nickname, self.username, self.hostname)

    def parse_command(self, data):
        xwords = data.split(' ')
        words = []
        for i in range(len(xwords)):
            word = xwords[i]
            if word.startswith(':'):
                words.append(' '.join([word[1:]] + xwords[i + 1:]))
                break
            words.append(word)
        return words

    def _send(self, data):
        self.sendbuffer += data + "\r\n"

    def send(self, command, data):
        self._send(":%s %s %s %s" %
                   (self.server.hostname, command, self.nickname, data))

    def send_numeric(self, numeric, data):
        self.send(str(numeric).rjust(3, "0"), data)

    def broadcast(self, users, data):
        for user in users:
            user._send(":%s %s" % (self.fullname(), data))

    def welcome(self):
        logging.info("New User: {}".format(self.nickname))

        self.send_numeric(1, ":Welcome to %s, %s" %
                          (self.server.name, self.fullname()))
        self.send_numeric(2, ":Your host is %s, running version %s" % (
            self.server.hostname, self.server.version))
        self.send_numeric(3, ":This server was created %s" %
                          self.server.creationtime)
        self.send_numeric(4, "%s %s  bov" %
                          (self.server.hostname, self.server.version))
        # http://www.irc.org/tech_docs/005.html
        self.send_numeric(
            5, ("CHANTYPES=# PREFIX=(ov)@+ CHANMODES=b,,,mnt"
                " NICKLEN=16 CHANNELLEN=50 TOPICLEN=300 AWAYLEN=160"
                " NETWORK=%s :Are supported by this server") % self.server.name
        )
        # MOTD
        self.handle_MOTD(("MOTD",))

    def quit(self, reason):
        # Send error to user
        try:
            message = "ERROR :Closing link: (%s) [%s]\r\n" % (
                self.fullname(), reason)
            self.socket.send(bytes(message, 'utf-8'))
        except socket.error:
            pass

        # Close socket
        self.socket.close()

        # Send quit to all users in channels user is in
        users = []
        for channel in self.channels:
            for user in channel.users:
                if user not in users:
                    users.append(user)
        self.broadcast(users, "QUIT :%s" % reason)

        # Remove user from all channels
        _channels = [channel for channel in self.server.channels
                     if self in channel.users]
        for channel in _channels:
            channel.remove_user(self)
            if self in channel.usermodes.keys():
                channel.usermodes.pop(self)

        # Remove user from server users
        if self in self.server.users:
            self.server.users.remove(self)
        logging.info("{} has quit".format(self.nickname))

    def handle_recv(self):
        """
        Main handler for received messages.
        """
        while self.recvbuffer.find("\n") != -1:
            recv = self.recvbuffer[:self.recvbuffer.find("\n")]
            self.recvbuffer = self.recvbuffer[self.recvbuffer.find("\n") + 1:]

            self.ping = time.time()

            recv = recv.strip()

            if recv == '':
                continue

            parsed = self.parse_command(recv)
            command = parsed[0]
            if command.upper() in self.NORMAL_COMMANDS:
                func = getattr(self, "handle_{}".format(command.upper()))
                func(parsed)
            # Special cases
            elif command.upper() == "PONG":
                pass
            elif self.nickname == '*' or self.username == 'unknown':
                self.send_numeric(451, "%s :You have not registered" % command)
            else:
                self.send_numeric(421, "%s :Unknown command" % command)

    def handle_PING(self, recv):
        logging.debug("PING:User:%s", self)
        if len(recv) < 2:
            self.send_numeric(461, "PING :Not enough parameters")
            return
        self._send(":%s PONG %s :%s" %
                   (self.server.hostname, self.server.hostname, recv[1]))

    def handle_MOTD(self, recv):
        logging.debug("MOTD:User:%s", self)
        self.send_numeric(375, ":%s message of the day" % self.server.hostname)
        for line in self.server.motd.split("\n"):
            self.send_numeric(372, ":- %s" % line)
        self.send_numeric(376, ":End of message of the day.")

    def handle_VERSION(self, recv):
        logging.debug("VERSION:User:%s", self)
        self.send_numeric(351, "%s. %s :http://github.com/programble/omgircd" %
                          (self.server.version, self.server.hostname))

    def handle_NICK(self, recv):
        logging.debug("NICK:User:%s", self)
        if len(recv) < 2:
            # No nickname given
            self.send_numeric(431, ":No nickname given")
            return

        nick = recv[1]
        if nick.strip() == '':
            # No nickname given
            self.send_numeric(431, ":No nickname given")
            return

        # Check if nick is valid
        if not is_valid_nickname(nick):
            self.send_numeric(432, "%s :Erroneous Nickname" % nick)
            return

        # Check if nick is already in use
        _nicks = [user.nickname.lower() for user in self.server.users]
        if nick.lower() in _nicks:
            self.send_numeric(433, "%s :Nickname is already in use" % nick)
            return

        # Nick is AWWW RIGHT
        self.broadcast([self], "NICK :%s" % nick)
        # Broadcast to all channels user is in
        users = []
        for channel in self.channels:
            for user in channel.users:
                if user not in users and user != self:
                    users.append(user)
        self.broadcast(users, "NICK :%s" % nick)
        old = self.nickname
        self.nickname = nick

        if old == "*" and self.username != "unknown":
            self.welcome()

    def handle_USER(self, recv):
        logging.debug("USER:User:%s", self)
        if len(recv) < 5:
            self.send_numeric(461, "USER :Not enough parameters")
            return

        # Make sure user is not already registered
        if self.username != "unknown":
            self.send_numeric(462, ":You may not register")
            return

        username = recv[1]
        realname = recv[4]

        self.username = username
        self.realname = realname

        if self.nickname != '*':
            self.welcome()

    def handle_PRIVMSG(self, recv):
        logging.debug("PRIVMSG:User:%s", self)
        if len(recv) < 2:
            self.send_numeric(411, ":No recipient given (PRIVMSG)")
            return
        elif len(recv) < 3:
            self.send_numeric(412, ":No text to send")
            return

        target = recv[1]
        msg = recv[2]

        # Send message to channel
        if target.startswith('#'):
            # Find channel
            channel = [
                channel for channel in self.server.channels
                if channel.name.lower() == target.lower()]

            if channel == []:
                self.send_numeric(401, "%s :No such nick/channel" % target)
                return

            channel = channel[0]

            if self not in channel.users and 'n' in channel.modes:
                self.send_numeric(
                    404, "%s :Cannot send to channel" % channel.name)
                return

            if 'm' in channel.modes and channel.usermodes[self] == '':
                self.send_numeric(
                    404, "%s :Cannot send to channel" % channel.name)
                return

            # Broadcast message
            channel_users = [user for user in channel.users if user != self]
            self.broadcast(channel_users, "PRIVMSG %s :%s" % (target, msg))
        # PM to user
        else:
            # Find user
            user = [
                user for user in self.server.users
                if user.nickname.lower() == target.lower()
            ]
            # User does not exist
            if user == []:
                self.send_numeric(401, "%s :No such nick/channel" % target)
                return
            user = user[0]
            if user.away:
                self.send_numeric(301, "%s :%s" %
                                  (user.nickname, user.away))

            # Broadcast message
            self.broadcast([user], "PRIVMSG %s :%s" % (target, msg))

    def handle_NOTICE(self, recv):
        logging.debug("NOTICE:User:%s", self)
        if len(recv) < 2:
            self.send_numeric(411, ":No recipient given (NOTICE)")
            return
        elif len(recv) < 3:
            self.send_numeric(412, ":No text to send")
            return

        target = recv[1]
        msg = recv[2]

        # Notice to channel
        if target.startswith('#'):
            # Find eventual channel
            channel = self.server.find_channel(target)

            if not channel:
                self.send_numeric(401, "%s :No such nick/channel" % target)
                return

            # Broadcast message
            self.broadcast(
                [user for user in channel.users if user != self],
                "NOTICE %s :%s" % (target, msg)
            )
        # Notice to user
        else:
            # Find eventual user
            user = self.server.find_user(target)

            # User does not exist
            if not user:
                self.send_numeric(401, "%s :No such nick/channel" % target)
                return

            # Broadcast message
            self.broadcast([user], "NOTICE %s :%s" % (target, msg))

    def handle_JOIN(self, recv):
        logging.debug("JOIN:User:%s", self)
        if len(recv) < 2:
            self.send_numeric(461, "JOIN :Not enough parameters")
            return

        if ',' in recv[1]:
            for channel in recv[1].split(','):
                self.handle_JOIN(("JOIN", channel))
            return

        channel_name = recv[1]

        # Channels must begin with #
        if channel_name[0] != '#' and channel_name != "0":
            self.send_numeric(403, "%s :No such channel" % channel_name)
            return
        elif channel_name == "0":
            # Part all channels
            for channel in self.channels:
                self.handle_PART(("PART", channel.name))
            return

        if not is_valid_channel_name(channel_name):
            self.send_numeric(479, "%s :Illegal channel name" % channel_name)
            return

        channel = self.server.find_channel(channel_name)

        # Create non-existent channel
        if not channel:
            channel = Channel(channel_name)
            self.server.add_channel(channel)
            logging.info("Channel created: {}".format(channel_name))

        # Drop if already on channel
        if channel in self.channels:
            return

        if channel.users == []:
            channel.usermodes[self] = 'o'
        else:
            channel.usermodes[self] = ''

        channel.add_user(self)
        self.channels.append(channel)

        self.broadcast(channel.users, "JOIN :%s" % channel.name)
        if channel.topic_time != 0:
            self.handle_TOPIC(("TOPIC", channel.name))
        self.handle_NAMES(("NAMES", channel.name))
        if channel.users == [self]:
            channel.usermodes[self] = 'o'
            channel.modes = "nt"
            self._send(":%s MODE %s +nt" %
                       (self.server.hostname, channel.name))
            self._send(":%s MODE %s +o %s" %
                       (self.server.hostname, channel.name, self.nickname))

    def handle_PART(self, recv):
        logging.debug("PART:User:%s", self)
        if len(recv) < 2:
            self.send_numeric(461, "PART :Not enough parameters")
            return

        target = recv[1]
        if len(recv) > 2:
            reason = recv[2]
        else:
            reason = ""

        channel = self.find_channel(target)

        if not channel:
            self.send_numeric(442, "%s :You're not on that channel" % target)
            return

        self.broadcast(channel.users, "PART %s :%s" % (channel.name, reason))
        self.channels.remove(channel)
        channel.remove_user(self)
        channel.usermodes.pop(self)

    def handle_NAMES(self, recv):
        logging.debug("NAMES:User:%s", self)
        if len(recv) < 2:
            self.send_numeric(461, "NAMES :Not enough parameters")
            return

        target = recv[1]
        channel = self.server.find_channel(target)

        if not channel:
            self.send_numeric(401, "%s :No such nick/channel" % recv[1])
            return

        users = []

        for user in channel.users:
            if 'o' in channel.usermodes[user]:
                users.append('@' + user.nickname)
            elif 'v' in channel.usermodes[user]:
                users.append('+' + user.nickname)
            else:
                users.append(user.nickname)

        self.send_numeric(353, "@ %s :%s" % (channel.name, " ".join(users)))
        self.send_numeric(366, "%s :End of /NAMES list." % channel.name)

    def handle_TOPIC(self, recv):
        logging.debug("TOPIC:User:%s", self)
        if len(recv) < 2:
            self.send_numeric(461, "TOPIC :Not enough parameters")
            return

        target = recv[1]
        channel = self.server.find_channel(target)
        if not channel:
            self.send_numeric(401, "%s :No such nick/channel" % recv[1])
            return

        if len(recv) < 3:
            # Send back topic
            if channel.topic == '':
                self.send_numeric(331, "%s :No topic is set." % channel.name)
                return

            self.send_numeric(332, "%s :%s" % (channel.name, channel.topic))
            self.send_numeric(333, "%s %s %d" % (
                channel.name, channel.topic_author, channel.topic_time))
        else:
            # Set topic if you're on the channel & operator
            if self not in channel.users:
                self.send_numeric(
                    442, "%s :You're not on that channel" % channel.name)
                return

            if 't' in channel.modes and 'o' not in channel.usermodes[self]:
                self.send_numeric(
                    482, "%s :You're not a channel operator" % channel.name)
                return

            channel.topic = recv[2][:300]
            channel.topic_author = self.fullname()
            channel.topic_time = int(time.time())

            self.broadcast(channel.users, "TOPIC %s :%s" %
                           (channel.name, channel.topic))

    def handle_ISON(self, recv):
        logging.debug("ISON:User:%s", self)
        if len(recv) < 2:
            self.send_numeric(461, "ISON :Not enough parameters")
            return

        nicks = recv[1:]

        _nicks = [user.nickname.lower() for user in self.server.users]
        online = [nick for nick in nicks if nick.lower() in _nicks]

        self.send_numeric(303, ":%s" % " ".join(online))

    def handle_AWAY(self, recv):
        logging.debug("AWAY:User:%s", self)
        if len(recv) < 2:
            self.away = False
            self.send_numeric(305, ":You are no longer marked as being away")
        else:
            self.away = recv[1][:160]
            self.send_numeric(306, ":You have been marked as being away")

    def handle_MODE(self, recv):
        logging.debug("MODE:User:%s", self)
        # TODO: Handle "mode b" (mode b should return the banlist)
        if len(recv) < 2:
            self.send_numeric(461, "MODE :Not enough parameters")
            return

        channel_name = recv[1]
        channel = self.server.find_channel(channel_name)
        if not channel:
            self.send_numeric(401, "%s :No such nick/channel" % recv[1])
            return

        if len(recv) == 2:
            # /mode #channel, send back channel modes
            self.send_numeric(324, "%s +%s" % (channel.name, channel.modes))
            self.send_numeric(329, "%s %d" % (channel.name, channel.creation))

        elif len(recv) == 3:
            # /mode #channel +mnt
            if self not in channel.users or 'o' not in channel.usermodes[self]:
                self.send_numeric(
                    482, "%s :You're not a channel operator" % channel.name)
                return

            action = ''
            for m in recv[2]:
                if m == '+':
                    action = '+'
                elif m == '-':
                    action = '-'
                else:
                    if action == '+':
                        if m not in channel.modes:
                            channel.modes += m
                    elif action == '-':
                        channel.modes = channel.modes.replace(m, '')

            self.broadcast(channel.users, "MODE %s %s" %
                           (channel.name, recv[2]))
        else:
            # /mode #channel +o-v user1 user2
            if self not in channel.users or 'o' not in channel.usermodes[self]:
                self.send_numeric(
                    482, "%s :You're not a channel operator" % channel.name)
                return

            modes = []
            action = ''
            for m in recv[2]:
                if m == '+':
                    action = '+'
                elif m == '-':
                    action = '-'
                elif m in "ov":
                    modes.append(action + m)
            modes = zip(recv[3:], modes)

            for nick, mode in modes:
                user = channel.find_user(nick)
                if user:
                    if mode[0] == '+':
                        channel.usermodes[user] += mode[1]
                    else:
                        channel.usermodes[user] = channel.usermodes[
                            user].replace(mode[1], "")

            self.broadcast(channel.users, "MODE %s %s %s" %
                           (channel.name, recv[2], ' '.join(recv[3:])))

    def handle_WHOIS(self, recv):
        logging.debug("WHOIS:User:%s", self)
        if len(recv) < 2:
            self.send_numeric(461, "WHOIS :Not enough parameters")
            return

        nickname = recv[1]
        user = self.server.find_user(nickname)

        if not user:
            self.send_numeric(401, "%s :No such nick/channel" % recv[1])
            self.send_numeric(318, "%s :End of /WHOIS list." % recv[1])
            return

        self.send_numeric(311, "%s %s %s * :%s" % (
            user.nickname, user.username, user.hostname, user.realname))
        if user.channels != []:
            channels = []
            for channel in user.channels:
                if 'o' in channel.usermodes[user]:
                    channels.append('@' + channel.name)
                elif 'v' in channel.usermodes[user]:
                    channels.append('+' + channel.name)
                else:
                    channels.append(channel.name)
            self.send_numeric(319, "%s :%s" %
                              (user.nickname, " ".join(channels)))
        self.send_numeric(312, "%s %s :%s" % (
            user.nickname, self.server.hostname, self.server.name))
        if user.away:
            self.send_numeric(301, "%s :%s" % (user.nickname, user.away))
        self.send_numeric(317, "%s %d %d :seconds idle, signon time" % (
            user.nickname, int(time.time()) - int(user.ping), user.signon))
        self.send_numeric(318, "%s :End of /WHOIS list." % user.nickname)

    def handle_WHO(self, recv):
        logging.debug("WHO:User:%s", self)
        if len(recv) < 2:
            self.send_numeric(461, "WHO :Not enough parameters")
            return

        target = recv[1]
        channel = self.server.find_channel(target)
        if not channel:
            self.send_numeric(401, "%s :No such channel" % recv[1])
            self.send_numeric(315, "%s :End of /WHO list." % recv[1])
            return

        for user in channel.users:
            modes = ''.join([{'o': '@', 'v': '+'}[x]
                             for x in channel.usermodes[user]])
            if user.away:
                away = 'G'
            else:
                away = 'H'
            self.send_numeric(
                352,
                "%s %s %s %s %s %s%s :0 %s" % (
                    channel.name, user.username,
                    user.hostname, self.server.hostname,
                    user.nickname, away, modes, user.realname))
        self.send_numeric(315, "%s :End of /WHO list." % channel.name)

    def handle_KICK(self, recv):
        logging.debug("KICK:User:%s", self)
        if len(recv) < 3:
            self.send_numeric(461, "KICK :Not enough parameters")
            return
        if len(recv) == 3:
            reason = recv[2]
        else:
            reason = recv[3]

        channel_name = recv[1]
        channel = self.find_channel(recv[1])

        if not channel:
            self.send_numeric(401, "%s :No such nick/channel" % channel_name)
            return

        # Find user on channel
        nickname = recv[2]
        user = channel.find_user(recv[2])

        if not user:
            self.send_numeric(401, "%s :No such nick/channel" % nickname)
            return

        if 'o' not in channel.usermodes[self]:
            self.send_numeric(
                482, "%s :You're not a channel operator" % channel.name)
            return

        self.broadcast(channel.users, "KICK %s %s :%s" %
                       (channel.name, user.nickname, reason))

        user.channels.remove(channel)
        channel.remove_user(user)
        channel.usermodes.pop(user)

    def handle_LIST(self, recv):
        logging.debug("LIST:User:%s", self)
        self.send_numeric(321, "Channel :Users  Name")
        for channel in self.server.channels:
            self.send_numeric(322, "%s %d :%s" % (
                channel.name, len(channel.users), channel.topic))
        self.send_numeric(323, ":End of /LIST")

    def handle_INVITE(self, recv):
        logging.debug("INVITE:User:%s", self)
        if len(recv) < 3:
            self.send_numeric(461, "INVITE :Not enough parameters")
            return

        # Find server user
        nickname = recv[1]
        user = self.server.find_user(nickname)

        if not user:
            self.send_numeric(401, "%s :No such nick/channel" % nickname)
            return

        target = recv[2]
        channel = self.find_channel(target)

        if not channel:
            self.send_numeric(401, "%s :No such nick/channel" % recv[2])
            return

        if self not in channel.users:
            self.send_numeric(401, "%s :No such nick/channel" % channel.name)
            return

        if user in channel.users:
            self.send_numeric(443, "%s %s :is already on channel" %
                              (user.nickname, channel.name))
            return

        # Send invite to user
        self.broadcast([user], "INVITE %s %s" % (user.nickname, channel.name))

        # Notify self that invite was successful
        self.send_numeric(341, "%s %s" % (user.nickname, channel.name))

    def handle_USERHOST(self, recv):
        logging.debug("USERHOST:User:%s", self)
        if len(recv) < 2:
            self.send_numeric(461, "USERHOST :Not enough parameters")
            return

        for nick in recv[1:]:
            user = self.server.find_user(nick)

            if not user:
                self.send_numeric(401, "%s :No such nick/channel" % nick)
                continue

            self.send_numeric(
                302, "%s=%s%s@%s" % (
                    user.nickname, {True: '-', False: '+'}[bool(user.away)],
                    user.username, user.hostname)
            )

    def handle_QUIT(self, recv):
        logging.debug("QUIT:User:%s", self)
        if len(recv) > 1:
            reason = recv[1]
        else:
            reason = self.nickname

        self.quit("Quit: " + reason)


class Channel(object):

    def __init__(self, name):
        self.name = name
        self.users = []
        self.modes = ''
        self.usermodes = {}
        self.topic = ""
        self.topic_author = ""
        self.topic_time = 0
        self.creation = int(time.time())

    def __repr__(self):
        return "<Channel '%s'>" % self.name

    def find_user(self, user_name):
        return find_user(user_name, self)

    def add_user(self, user):
        self.users.append(user)

    def remove_user(self, user):
        self.users.remove(user)


class Server(socket.socket):

    def __init__(self, config):
        super(Server, self).__init__(socket.AF_INET, socket.SOCK_STREAM)

        self.config = config
        self.users = []
        self.channels = []

        self.hostcache = {}

        self.hostname = self.config.get('server', 'hostname')
        self.name = self.config.get('server', 'name')
        self.creationtime = self.config.getint('server', 'creation')
        self.version = "omgircd3-{}".format(__version__)
        self.motd = self.config.get('server', 'motd')
        self.ping_timeout = self.config.getfloat('server', 'ping_timeout')

    def run(self):
        # Bind port and listen
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((
            self.config.get('server', 'bind_host'),
            self.config.getint('server', 'bind_port')
        ))
        self.listen(5)

        # Main select loop (this is where the magic happens)
        while True:
            # Find users with pending send data
            sendable = [user for user in self.users if user.sendbuffer]

            read, write, error = select(
                [self] + self.users, sendable, self.users, 25.0)

            for user in error:
                user.quit("Error: Connection reset by peer")

            # Is there a new connection to accept?
            if self in read:
                # Accept connection and create new user object
                sock, address = self.accept()
                User(self, sock, address)

            # Read from each user
            for user in [user for user in read if user != self]:
                try:
                    recv = user.socket.recv(4096)
                    recv = recv.decode()
                except socket.error:
                    user.quit("Read error: Connection reset by peer")
                if recv == '':
                    user.quit("Remote host closed the connection")
                user.recvbuffer += recv

                # Excess Flood
                if len(user.recvbuffer) > 1024:
                    user.quit("Excess Flood")
                    continue

                user.handle_recv()

            # Send to each user
            for user in write:
                try:
                    message = bytes(user.sendbuffer, 'utf-8')
                    sent = user.socket.send(message)
                    user.sendbuffer = user.sendbuffer[sent:]
                except socket.error:
                    user.quit("Write error: Connection reset by peer")

            # Garbage collection (Empty Channels)
            _channels = [channel for channel in self.channels
                         if len(channel.users) == 0]
            for channel in _channels:
                logging.info("Removing channel %s", channel)
                self.remove_channel(channel)

            # Ping timeouts
            _users = [user for user in self.users
                      if (time.time() - user.ping) > self.ping_timeout]
            for user in _users:
                user.quit("Ping timeout: %d seconds" %
                          int(time.time() - user.ping))

            # Send out pings to not-so old users
            half_timeout = self.ping_timeout / 2.0
            _users = [user for user in self.users
                      if (time.time() - user.ping) > half_timeout]
            for user in _users:
                try:
                    message = "PING :%s\r\n" % self.hostname
                    user.socket.send(bytes(message, 'utf-8'))
                except socket.error:
                    user.quit("Write error: Connection reset by peer")

    def shutdown(self):
        for user in self.users:
            user.quit("Server shutdown")
        self.close()
        logging.info("Server shutdown")

    def find_channel(self, channel_name):
        """
        Search for channel by name on the server
        """
        return find_channel(channel_name, self)

    def find_user(self, user_name):
        """
        Search for a user on the server
        """
        return find_user(user_name, self)

    def add_channel(self, channel):
        """
        Add a channel to the server
        """
        self.channels.append(channel)

    def remove_channel(self, channel):
        """
        Remove the channel from the server
        """
        self.channels.remove(channel)


def run():
    """
    Run omgircd3 IRC server
    """
    args = load_args()
    config = load_configuration(args.config)

    server = Server(config)
    logging.info("Starting server")
    try:
        server.run()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()


if __name__ == "__main__":
    run()
