""" A server class for scorpion to handle communication to external devices."""
#--------------------------------------------------------------------
# Administration Details
#--------------------------------------------------------------------
__author__ = "Sebastian Dransfeld"
__copyright__ = "Sintef Raufoss Manufacturing 2015"
__credits__ = ["Mats Larsen", "Olivier Roulet-Dubonnet", "Alvaro Capelan"]
__license__ = "Sintef Raufoss Manufacturing 2015"
__status__ = "Development"
#--------------------------------------------------------------------
# Hardware Details
#--------------------------------------------------------------------
"""
-  Scorpion 11.0
"""
#--------------------------------------------------------------------
# Dependices Details
#--------------------------------------------------------------------
"""
"""
#--------------------------------------------------------------------
# Version Details
#--------------------------------------------------------------------
"""
Version -> 1.0
OS -> Windows 7
Complier -> Python 2.7
"""
#--------------------------------------------------------------------
# Import
#--------------------------------------------------------------------
import clr
import json
import tordivel_client as client  # Client to send data to the connected device
reload(client)
import __main__
from time import time
import os

from System.Reflection import Assembly
scorpionDir = __main__.GetValue('System.ScorpionDir')
Assembly.LoadFrom(scorpionDir + r'\OverlayPanel.dll')
Assembly.LoadFrom(scorpionDir + r'\RawTcpMessenger.dll')
from Tordivel import RawTcpMessenger, OverlayPanel
import traceback

# Load custom assemblies
from System.Text import Encoding

#--------------------------------------------------------------------
# CONSTANTS
#--------------------------------------------------------------------
LOG_LEVEL = 2


class TordivelServer:

    '''
    The Scproion 11 server to handle communication with external control device. Scorpion has a speciel socket wraped aroaund a normal socket. This is why RawTCPMessenger is used.
    '''

    def _log(self, msg, log_level=LOG_LEVEL):
        '''
        Print a message, and track, where the log is invoked
        Input:
        -msg: message to be printed, ''
        -log_level: information level, i
        '''
        global LOG_LEVEL
        if log_level <= LOG_LEVEL:
            print(str(log_level) + ' : ' + __file__ + '.py ::' + traceback.extract_stack()[-2][2] + ' : \n' + str(self) + '\nMsg-> ' + msg + '\n')

    def __repr__(self):
        """
        Printing of properties of the instance.
        """
        return "<ClassName-> %s , Name-> %s>" % (self.__class__.__name__, self._name)

    def __init__(self, port, **kwargs):
        '''
        '''
        self._name = kwargs.get('name', 'Invalid')
        # Create an overlaypanel
        self.panel = OverlayPanel(__main__.GetResultPanel().handle)
        #self.panel.ShowTrace = 1
        # Create the RawTcpMessenger component
        self.messenger = RawTcpMessenger(self.panel)
        # Register handler for rawTcpMessenger.Receive event
        self.messenger.Receive += self.ReceiveHandler
        # Register handler for rawTcpMessenger.RemoteConnect event
        self.messenger.RemoteConnect += self.RemoteConnectHandler
        # Register handler for rawTcpMessenger.RemoteDisconnect event
        self.messenger.RemoteDisconnect += self.RemoteDisconnectHandler
        # Register handler for rawTcpMessenger.SendError event
        self.messenger.SendError += self.SendErrorHandler

        if not self.messenger.StartListen("", 9000 + port):
            print "Could not listen to port %d" % (9000 + port)
        else:
            print "Listening to port %d" % (9000 + port)

    def RemoteConnectHandler(self, sender, args):
        print str(args.remoteAddress) + ":" + str(args.remotePort) + " Connected " + str(time())
        __main__.client = client.Client(sender, args)
        __main__.SetIntValue(':RobotID.Value', 0)
        cameras = __main__.GetCameras()
        for i in xrange(cameras.count):
            cam = cameras.getCamera(i)
            if not cam.open:
                cam.open = 1
        __main__.ExecuteCmd('Start', '')

    def RemoteDisconnectHandler(self, sender, args):
        print str(args.remoteAddress) + ":" + str(args.remotePort) + " Disconnected"
        __main__.client = None
        __main__.SetIntValue(':RobotID.Value', 0)
        __main__.ExecuteCmd('Stop', '')

    def SendErrorHandler(self, sender, args):
        print str(args.remoteAddress) + ":" + str(args.remotePort) + " SendError: " + args.errorDescription
        __main__.client = None


class ServerJSON(TordivelServer):

    '''
    JSONRPC protocol server
    we use JSONRPC V2 to avoid re-implemented my own format,
    but we re-implement in order not to rely on third party
    libraries that may not be installed on scorpion
    '''

    def __init__(self, port, **kwargs):
        TordivelServer.__init__(self, port, **kwargs)

    def ReceiveHandler(self, sender, args):
        start = time()
        # try:
        msg = Encoding.ASCII.GetString(args.message, 0, args.message.Length)
        # print "recv: " + str(args.senderAddress) + ":" + str(args.senderPort) + " " + msg + " " + str(time())
        msg = json.loads(msg)
        method = msg['method']
        rpcid = msg['id']
        answer = {}
        answer['id'] = rpcid
        answer['jsonrpc'] = "2.0"

        if "params" in msg:
            params = msg["params"]

            #print("sending: ", answer)

        try:
            self.execute_method(msg, rpcid, method, params, answer)
            print "method executed in : ", (time() - start)
        except Exception as e:
            print ('exception happened', e)
            answer["error"] = {"error": -100, "message": "Scorpion JSON-RPC Server: Exception {}".format(e)}

        __main__.client.send_json(answer)

    def execute_method(self, msg, rpcid, method, params, answer):

        if method == 'execute_command':
            __main__.ExecuteCmd(params["command"], params["parameters"])
            answer['result'] = [0]

        elif method == 'get_values':
            print("Values to be read: {0}".format(params["names"]))
            values = []
            for name in params["names"]:
                values.append(__main__.GetValue(name))
            answer['result'] = values

        elif method == 'set_values':
            print("Values to be set: {0}".format(params["values"]))
            for valuename, val in params["values"].items():
                #print("it ", valuename, val)
                if isinstance(val, float):
                    #print ('Setting float: ', valuename, val)
                    __main__.SetFloatValue(valuename, val)
                elif isinstance(val, int):
                    __main__.SetIntValue(valuename, val)
                else:
                    __main__.SetValue(valuename, val)
            answer['result'] = [0]

        elif method == 'toolbox':
            name = params["name"]
            print("Executing toolbox: {0}".format(name))
            img = __main__.GetImageMatr('Image1')
            tool = __main__.GetTool(name)

            tool.execute(img)

            if "results" in params:
                answer['result'] = []
                results = params["results"]
                for resname in results:
                    print("Getting value: {0}".format(resname))
                    value = __main__.GetValue(resname)
                    print ('Value:', value)
                    answer['result'].append(value)
        else:
            raise Exception("Unknown json-rpc method")
