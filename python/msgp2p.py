# msgp2p provides provides decentralized messaging with unique global addressing.
#   Copyright (C) 2014 Nicola Cimmino
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
# This service expects a LoPNode connected on serial port ttyUSB0 and set
#   to access point mode already (ATAP1). In due time autodiscovery and
#   configuration will be built.
#
# We don't really lease addressed from a DHCP server here. Instead our box has 
#   a pool of IP address aliases that are for us to distribute to our client.
# This has the benefit of not requiring to modify on the fly our network config
#   since in the end we always would need to have the addresses assigned to
#   this box in oder to get the traffic. This has the disavantage to require
#   a range of private IPs to be reserved for out use.

import sys
import os
import time
from threading import Thread

class msgp2p:

  # Base folder inside which peer folders are created.
  basepath = "/var/msgp2p/"
  
  # Path to our folder where peers will communicate with us.
  ourpath = ""
  
  localUID = ""
  
  stoplistening = False
  
  received_data_callback = None
  
  # This info must come from a config file.
  btclient = None
  
  def initbtclient(self):
    import btsync
    self.btclient = btsync.Client( host='127.0.0.1', port='8888', username='admin', password='password')
 
  def __init__(self, localUID, received_data_callback):
      self.localUID = localUID
      self.received_data_callback = received_data_callback
      
      self.ourpath = self.basepath + self.localUID + "/"
      
      if not os.path.exists(self.ourpath):
        os.makedirs(self.ourpath)           
        # Acquire our own folder
        try:
          if self.btclient == None:
            self.initbtclient()
          self.btclient.add_sync_folder(self.ourpath, self.localUID)
        except:
          # Exception while adding folder. This is normal if the folder exists already. API doesn't allow to check before adding for now.
          pass
          
      # Monitor our folder
      thread = Thread( target = self.monitorFolder )
      thread.start()      
      
  def monitorFolder(self):
    while(not self.stoplistening):
      for file in os.listdir(self.ourpath):
        if file.endswith(".msgp2p"):
          filename = file.translate(None, ".msgp2p")
          
          # Tokenize the filename
          tokens = filename.split("_")
          remoteUID = tokens[0]
          logicalchannel = tokens[1]
          f = open(self.ourpath + file, 'r')
          message = f.readline()
          f.close()
          
          # ACK the message by deleteting it
          os.remove(self.ourpath + file)
          
          # Notify the new data
          self.received_data_callback(self.localUID, remoteUID, message, logicalchannel)
          
  def sendMessage(self, remoteUID, message, logicalchannel="msg"):
    peerpath = self.basepath + remoteUID
    if not os.path.exists(peerpath):
      os.makedirs(peerpath)   
      # Acquire our own folder
      try:
        if self.btclient == None:
            self.initbtclient()
        self.btclient.add_sync_folder(peerpath, remoteUID)
      except:
        # Exception while adding folder. This is normal if the folder exists already. API doesn't allow to check before adding for now.
        pass

    peerfile = self.localUID + "_" + logicalchannel + "_" + str(int(time.time())) + ".msgp2p"
    f = open(peerpath + "/" + peerfile, 'w')
    f.write(message)
    f.close()
  
def dataReceived(localUID, remoteUID, message, logicalchannel):
 print "Remote UID: " + remoteUID
 print "LCH: " + logicalchannel
 print "Message: " + message
 msgp2p.stoplistening = True
 exit(0)
 
# If we are run in command line and not included as module we will behave
#  according to supplied args
if __name__ == "__main__":
  # Get command line parameters
  if not len(sys.argv) > 4:
    print "Usage: msgp2p send|receive localUID remoteUID [message]"
    exit(1)

  # Get the arguments.
  operation = sys.argv[1]
  localUID = sys.argv[2]
  remoteUID = sys.argv[3]
  
  if len(sys.argv) > 4:
    message = " ".join(sys.argv[4:])
  else:
    message = ""
  
  msgp2p = msgp2p(localUID, dataReceived)
  
  if operation == "send":
    msgp2p.sendMessage(remoteUID, message)
    msgp2p.stoplistening = True
  
