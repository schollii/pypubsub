from pubsub import pub

def listener1(msg):
    print "The listener received the message : %s" % (msg, )

pub.subscribe(listener1, 'test.pubsub')

def sender():
    pub.sendMessage('test.pubsub', msg="Hola! this is a test message")

if __name__ == "__main__":
    sender()

