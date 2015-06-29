import clr
import __main__
import json
from time import time
import xml.etree.ElementTree as et

# Load custom assemblies
from System.Text import Encoding

class Client:
    def __init__(self, messenger, args):
        self.messenger = messenger
        self.address = args.remoteAddress
        self.port = args.remotePort

    def send(self, msg):
        if not msg.endswith('\r'): print "wrong format msg: %s" % msg
        if __main__.GetValue('System.Running'):
            print "send: " + self.address + ":" + str(self.port) + " " + msg + " " + str(time())
            self.messenger.Send(self.address, self.port, Encoding.ASCII.GetBytes(msg))
        else:
            print "msg: %s" % msg

    def sendXml(self, data):
        if __main__.GetValue('System.Running'):
            msg = et.Element('resp')
            for key, value in data.iteritems():
                et.SubElement(msg, key).text = str(value)
            self.messenger.Send(self.address, self.port, Encoding.ASCII.GetBytes(et.tostring(msg)+'\n'))
            print "send: " + self.address + ":" + str(self.port) + " " + et.tostring(msg) + " " + str(time())
        else:
            print "msg: %s" % data
    
    def send_json(self, msg):
        data = json.dumps(msg)
        #print("sending: ", type(data), data)
        if __main__.GetValue('System.Running'):
            #print "send: " + self.address + ":" + str(self.port) + " " + msg + " " + str(time())
            #self.messenger.Send(self.address, self.port, Encoding.ASCII.GetBytes(data))
            self.messenger.Send(self.address, self.port, data)
        else:
            print "System not running cannot send: ",  msg