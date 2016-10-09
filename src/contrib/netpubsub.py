"""
Skeleton code (will not load... must be completed):
UDP-based net-centric Pubsub extension so that pubsub can be used over a 
network of pubsub-powered applications. Extending to use TCP wouldn't be 
too difficult. 

Usage: each of your applications that uses pubsub would create a 
suitable AppListener, then call its sendMessage when wanting to 
send a message, or call processMessages whenever it is ready to 
process queued messages from other applications. In addition, one 
of your applications must be the "pubsub server", or the server
could live in its own python program.  For it, you would 
create a PubsubAppServer then call its processMessages() 
in an infinite loop. 

Oliver Schoenborn
"""

from socket import socket, timeout
from pubsub import pub


class Marshaller:
    ...
    depends
    on
    your
    strategy / method...
    ...
    for instance, could use unpickle...
    ... or XML, SOAP, your
    own
    format, etc...

    def pack(self, topic, **args):
        ...
        pack
        topic and args
        into
        a
        data
        string...
        return data

    def unpack(self, data):
        ...
        unpack
        data
        into
        a
        topic and args
        return topic, msgData

    def getTopic(self, data):
        ...
        get
        topic
        from data...
        return topic


class AppListener:
    def __init__(self, server, readPort, maxWait=0.01):
        self.__server = server
        self.__marshaller = Marshaller()
        self.__udpSocket = socket(...
        server...)
        self.__udpSocket.bind(...
        readPort...)
        self.__udpSocket.settimeout(maxWait)  # want limited blocking

    def subscribe(self, topic):
        self.__udpSocket.write('subscribe %s' % topic)

    def processMessages(self):
        bufsize = 4096
        more = True
        while more:
            try:
                data, sender = self.__udpSocket.recvfrom(bufsize)
                if sender == self.__server:
                    self.__publish(data)
            except timeout:
                more = False

    def __publish(self, data):
        topic, argsValues = self.__marshaller.unpack(data)
        pub.sendMessage(topic, **argsValues)

    def sendMessage(topic, **msgData):
        packedData = self.__marshaller.pack(msgData)
        self.server.write(packedData)


class PubsubAppServer:
    SERVER_PORT = 8743  # pick to suit you

    def __init__(self):
        self.__listenerApps = {}  # will be list of sets by topic
        self.__marshaller = Marshaller()
        self.__udpSocket = socket(...)
        self.__udpSocket.bind(...
        SERVER_PORT...)

        def processMessages(self):
            bufsize = 4096
            more = True
            while more:
                try:
                    data, sender = self.__udpSocket.recv(bufsize)
                    if data.startswith('subscribe'):
                        self.__register(sender, data)
                    else:
                        self.__dispatch(data)
                except timeout:
                    more = False

        def __register(self, sender, data):
            topic = data.split(' ')[1]  # second item
            self.__listenerApps.setdefault(topic, set()).add(sender)

        def __dispatch(self, data):
            topic = self.__marshaller.getTopic(data)
            # send to all registered apps for that topic;
            # if no such topic then do nothing:
            for listenerApp in self.__listenerApps.get(topic, []):
                self.__udpSocket.write(data)
