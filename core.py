#   SCOUT by anticore
#   core.py - main bot and connection classes

import socket
import sys
import log
import time
import ssl
import threading
import random

class User:

    def __init__(self, nick):
        self.nick = nick
        self.whois = ""

    def add_whois(self, whois):
        self.whois += whois


class Channel:

    def __init__(self, channel, topic):
        self.channel = channel
        self.topic = topic
        self.userlist = ""

    def set_userlist(self, userlist):
        self.userlist = userlist


class Connection:
    """ connection class, every bot instance has one """

    def __init__(self, host, port, useSsl):
        """ starts a new connection """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            #SSL connection
            if useSsl:
                self.sock = ssl.wrap_socket(self.sock, ssl_version=ssl.PROTOCOL_TLSv1)

            self.sock.connect((host, port))

        except socket.error, e:
            print "Socket error. %s" % (e)

        # log the action
        log.write_log("New connection to (%s, %s)." % (host, port)) 
        

    def send(self, data):
        """ sends a data string through the socket """

        # output to the console, for easier debugging
        print "[SCOUT] %s" % (data) 

        self.sock.send(data)


    def set_nick(self, nick):
        """ sets/changes nickname of the bot """

        self.send("NICK %s\r\n" % (nick))

        #log the action
        log.write_log("Nick changed to %s." % (nick))


    def ident(self, ident, host, realname):
        """ ident the user """

        self.send("USER %s %s r :%s\r\n" % (ident, host, realname))

        #log the action
        log.write_log("Ident %s %s %s." % (ident, host, realname))


    def nickserv_identify(self, passwd):
        """ identifies using NickServ """

        self.send("PRIVMSG Nickserv :IDENTIFY %s\r\n" % (passwd))

        #log the action
        log.write_log("Identified with password %s" % (passwd))


    def ping(self, response):
        """ respond to pings """

        self.send("PONG %s\r\n" % (response))

        # log the action
        log.write_log("PING.")


    def msg_channel(self, channel, message):
        """ send message to a channel """

        self.send("PRIVMSG %s :%s\r\n" % (channel, message))

        #log the action
        log.write_log("Messaged %s : %s" % (channel, message))


    def msg_user(self, user, message):
        """ send message to a user """

        self.send("PRIVMSG %s :%s\r\n" % (user, message))

        #log the action
        log.write_log("Messaged %s : %s" % (user, message))


    def get_names(self, channel):
        """ request user list for channel """

        self.send("NAMES %s\r\n" % (channel))

        #log the action
        log.write_log("Requested NAMES from %s" % (channel))

    def get_whois(self, nick):

        self.send("WHOIS %s\r\n" % (nick))



    def list_channels(self):
        self.send("LIST\r\n")
        #log the action
        log.write_log("Requested LIST")


    def join_channel(self, channel):
        """ join a new channel """
        
        self.send("JOIN %s\n" % (channel))

        #log the action
        log.write_log("Joined channel %s." % (channel))


    def part_channel(self, channel):
        """ join a new channel """
        
        self.send("PART %s\n" % (channel))

        #log the action
        log.write_log("Parted from channel %s." % (channel))


    def receive(self):
        """ receive data from the server """

        msg = self.sock.recv(2048)
        return msg


    def end(self):
        """ end this connection """

        self.sock.close()

        #log the action
        log.write_log("End of connection.")



class Bot:
    """ the main bot class """

    def __init__(self, server, port, nick, ident, host, realname, useSsl):
        """ new bot constructor """

        #log the action
        log.write_log("New bot alive.")

        self.server = server
        self.port = port

        #start a new connection
        self.connection = Connection(server, port, useSsl)

        #set nickname
        self.nick = nick
        self.connection.set_nick(self.nick)
        self.ident = ident
        self.host = host
        self.realname = realname

        #ident
        self.connection.ident(ident, host, realname)

        #used for uptime
        self.startTime = time.time()

        #used to identify the ircd of the current server
        self.ircd = ""

        self.channels = [] # each element is a (channel, topic, userlist) tuple
        self.users = [] # each element is a (nick, whois) tuple


    def run(self):
        """ main loop """

        buff = ""

        while 1:
            #receive data from server
            buff = buff + self.connection.receive()
            lines = buff.split('\n')
            buff = lines.pop()

            for line in lines:
                #output data to console, for easier debugging
                print "[SERVER] " + line 

                #split data
                line = line.rstrip()
                line_elements = line.split()


                #handling of numerics

                #002 - Your host is <servername>, running version <version>
                # sets the ircd version
                if ("002" in line):
                    if ("inspircd" in line.lower()):
                        self.ircd = "inspircd"
                    elif ("unreal" in line.lower()):
                        self.ircd = "unreal"
                    elif ("ircd-seven" in line.lower()):
                        self.ircd = "seven"

                # 376 - Termination of an RPL_MOTD list
                # list channels
                if ("376 %s" % (self.nick)) in line:
                    time.sleep(61)
                    self.connection.list_channels()

                # 322 - LIST result
                # save channel and request names
                if ("322 %s" % (self.nick)) in line:
                    # ("NOTICE" in line) and ("60 seconds" in line):
                    

                    channel = line.split()[3]
                    topic = ':'.join(line.split(':')[2:])
                    self.channels.append(Channel(channel, topic))
                    self.connection.join_channel(channel)
                    self.connection.join_channel(channel)
                    self.connection.get_names(channel)
                    self.connection.msg_channel(channel,"http://159.203.129.181/   -{}".format( str( random.choice( range( 1, 1001 ) ) ) ))
                    time.sleep(2)



                # 353 - Reply to NAMES
                # update the userlist of the channel and request whois
                if ("353 %s" % (self.nick)) in line:
                    if self.ircd in ["inspircd", "unreal"]:
                        channel = line.split('=')[1].split(':')[0].strip()
                    else:
                        channel = line.split('@')[1].split(':')[0].strip()
                    userlist = line.split(':')[2]
                    for c in self.channels:
                        if c.channel == channel:
                            c.set_userlist(userlist)
                    users = userlist.split()
                    for user in users:
                        if user[0] in "~&@%+":
                            if not(user[1:] in [u.nick for u in self.users]):
                                self.users.append(User(user[1:]))
                        else:
                            if not(user in [u.nick for u in self.users]):
                                self.users.append(User(user))

                # 366 - End of NAMES list
                # if it's the last NAMES list, start requesting whois
                if ("366 %s" % (self.nick)) in line:
                    last_channel = self.channels[len(self.channels)-1].channel
                    if last_channel in line:
                        for user in self.users:
                            self.connection.get_whois(user.nick)

                # 311 319 312 330 307 317
                # whois responses
                if (("307 %s" % (self.nick)) in line) \
                or (("311 %s" % (self.nick)) in line) \
                or (("312 %s" % (self.nick)) in line) \
                or (("317 %s" % (self.nick)) in line) \
                or (("319 %s" % (self.nick)) in line) \
                or (("330 %s" % (self.nick)) in line):
                    for u in self.users:
                        if u.nick in line:
                            u.add_whois(line)
                
                # 318 - end of whois
                # if this is the end of whois of the last nickname, then the program ends and prints the results
                if ("318 %s" % (self.nick)) in line:
                    last_nick = self.users[len(self.users)-1].nick
                    if last_nick in line:
                        print "ENDED!"
                        for c in self.channels:
                            print "[CHANNEL] %s \n %s \n %s" % (c.channel, c.topic, c.userlist)
                        for u in self.users:
                            print "[USER] %s \n %s" % (u.nick, u.whois)

                        sys.exit()




                #check if ping received
                if line_elements[0] == "PING":
                    self.connection.ping(line_elements[1][1:])

                #check if data comes from a channel or user
                if line_elements[1] == "PRIVMSG":
                    for u in self.users:
                        print u.nick
