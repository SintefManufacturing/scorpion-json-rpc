"""
This module start when the Scproion starts. So here it has to create a server.
"""
#--------------------------------------------------------------------
#Administration Details
#--------------------------------------------------------------------
__author__ = "Sebastian Dransfeld"
__copyright__ = "Sintef Raufoss Manufacturing 2015"
__credits__ = ["Mats Larsen"]
__license__ = "Sintef Raufoss Manufacturing 2015"
__maintainer__ = "Mats Larsen"
__email__ = "Mats.Larsen@sintef.com"
__status__ = "Development"
__projectNR__ = "MultiMat"
__date__ = "20042015"
#--------------------------------------------------------------------
#Hardware Details
#--------------------------------------------------------------------
"""
-  Scorpion 11.0
"""
#--------------------------------------------------------------------
#Dependices Details
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
#Import
#--------------------------------------------------------------------
import sys
sys.path.append(r'C:\\repos\tordivel\code')
import tordivel_server
reload(tordivel_server)
from tordivel_server import *
sys.path.append(r'C:\Python26\Lib\site-packages')
#--------------------------------------------------------------------
#CONSTANTS
#--------------------------------------------------------------------
PORT = 1 # The server scorpion is listing on plus 9000.
#--------------------------------------------------------------------
#METHODS
#--------------------------------------------------------------------
# try to close existing RawTcpMessenger
try:
  if server: server.messenger.Close()
  server = None
except:
  print 'Dispose Failed'

# Create global instance of server
client = None
server = tordivel_server.ServerJSON(PORT) # create a Json server