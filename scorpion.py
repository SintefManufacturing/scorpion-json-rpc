from IPython import embed
import time
import socket
import json
import logging

class Scorpion(object):
    """
    Generic class to connection to scorpion
    and communicate using json-rpc
    this requires the json-rpc sintef server class
    this class implements the json-rpc form in order not to 
    rely on third party library
    """
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.sock = None
        self._data = b""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._rpc_count = 0

    def __str__(self):
        return "Vision(ip={}, port={})".format(self.hostname, self.port)
    __repr__ = __str__

    def _create_msg(self, method=None, params=None):
        """
        return a dict containing the minimum tags required by json-rpc
        add what you want and use send_msg
        """
        s = {}
        s["jsonrpc"] = "2.0"
        self._rpc_count += 1
        s["id"] = self._rpc_count
        if method:
            s["method"] = method
        if params:
            s["params"] = params
        return s

    def _recv(self):
        """
        The simple _recv method. It may receive incomplete messages,
        or tow messages together.
        """
        data = self.sock.recv(1024)
        if not data:
            raise Exception("No data received")
        return data

    def _recv_complex(self):
        """
        BROKEN
        """
        while True:
            msg, self._data = self._find_packet(self._data)
            if msg:
                return msg
            data = self.sock.recv(1024)
            print("received data on socket ", data)
            if not data:
                raise Exception("Connection closed")
            self._data += data 

    def _find_packet(self, data):
        """
        fing a json packet in a string
        """
        self.logger.debug("looking for packet in buffer of length %s and data %s", len(data), data)
        while data and not data.startswith(b"{"):
            self.logger.info("data does not start with { %s", data)
            data = data[1:]
        count = 0
        #in_string = None
        for idx, c in enumerate(data):
            #if in_string:
                #if in_string == c:
                    #in_string = None
                    #continue
            #if c in (b'"', b"'"):
                #in_string = c
            if c == b"{":
                count += 1
            elif c == b"}":
                count -= 1
            if count == 0:
                self.logger.debug("RETURN idx %s, data %s and rest %s", idx, data[:idx+1], data[idx+1:]) 
                return data[:idx+1], data[idx+1:]
        self.logger.debug("no packet founs in data %s", data)
        return b"", data

    def recv_msg(self):
        """
        """
        s = self._recv().decode()
        self.logger.info("received data: %s", s)
        msg = json.loads(s)
        return msg

    def recv_result(self):
        msg = self.recv_msg()
        if "error" in msg:
            raise Exception(msg["error"])
        elif "result" in msg:
            return msg["result"]
        else:
            return None

    def send_msg(self, msg):
        """
        send msg to scorpion
        msg is a dict containing the keys required by json-rpc
        """
        self.logger.info("sending: %s", msg)
        self.sock.sendall(json.dumps(msg).encode())

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.hostname, self.port))

    def disconnect(self):
        self.sock.close()

    def execute_command(self, cmd, parameters=""):
        """
        send an execute_command json.rpc message to scropion
        and wait for result
        """
        s = self._create_msg()
        s["method"] = "execute_command" 
        s["params"] = {}
        s["params"]["command"] = cmd
        s["params"]["parameters"] = parameters
        self.send_msg(s)
        return self.recv_result()

    def trigger(self):
        """
        helper method to run CameraTrigger command on scorpion
        """
        return self.execute_command("CameraTrigger")

    def run_tool(self, name, results=None, arguments=None, ):
        """
        run a scorpion toolbox, optionaly set scorpion values
        before running and return result of toolbox

        results is the name of the scorpion value the method will return
        arguments is a dict of scorpion_value: value
        if execute is True the toolbox is run
        """
        s = self._create_msg()
        s["method"] = "toolbox"
        s["params"] = {}
        s["params"]["name"] = name
        if results is not None:
            s["params"]["results"] = results
        if arguments is not None:
            s["params"]["arguments"] = results

        self.send_msg(s)

        return self.recv_result()

    def find_parts(self, toolboxname):
        """
        helper method, run a toolbox and return the data
        of 'toolboxname'.results.results
        """
        msg = self.run_tool(toolboxname, results=['{}.{}.{}'.format(toolboxname, 'results', 'results')])
        res = msg[0]
        return json.loads(res)


    def set_value(self, name, value):
        """
        set a scorpion value
        name is the path to the scorpion variable: mytoolbox.myvariable
        """
        return self.set_values({name:value})

    def set_values(self, values):
        """
        set several scorpion values at once. takes a dict as argument of        scorpion value name and value
        """
        params = {}
        params["values"] = values

        s = self._create_msg("set_values", params)

        self.send_msg(s)
        return self.recv_msg()

    def get_value(self, name):
        """
        read a value from scorpion
        """
        return self.get_values([name])

    def get_values(self, names):
        """
        read many value from scorpion
        names is a list of strings
        """
        params = {}
        params["names"] = names

        s = self._create_msg("get_values", params)

        self.send_msg(s)
        return self.recv_result()


