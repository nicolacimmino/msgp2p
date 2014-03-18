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

import btsync
import os
import thread
from threading import Thread

class msgp2p:

  # Base folder inside which peer folders are created.
  basepath = "/var/msgp2p/"
  
  # Path to our folder where peers will communicate with us.
  ourpath = ""
  
  uniqueid = ""
  
  received_data_callback = None
  
  # This info must come from a config file.
  btclient = btsync.Client( host='127.0.0.1', port='8888', username='admin', password='password')

  def __init__(self, uniqueid, received_data_callback):
      self.uniqueid = uniqueid
      self.received_data_callback = received_data_callback
      
      self.ourpath = self.basepath + self.uniqueid + "/"
      
      if not os.path.exists(self.ourpath):
        os.makedirs(self.ourpath)   
        
      # Acquire our own folder
      try:
        self.btclient.add_sync_folder(self.ourpath, self.uniqueid)
      except:
        # Exception while adding folder. This is normal if the folder exists already. API doesn't allow to check before adding for now.
        print "Folder already mapped."
        
      # Monitor our folder
      thread = Thread( target = self.monitorFolder )
      thread.start()      
      
  def monitorFolder(self):
    while(True):
      for file in os.listdir(self.ourpath):
        if file.endswith(".fsbc_oi"):
          # Tokenize the filename
          tokens = file.split("_")
          senderid = tokens[0]
          replyreuested = tokens[1]
          connectiontype = tokens[2][:tokens[2].find(".")]
          f = open(self.ourpath + file, 'r')
          message = f.readline()
          f.close()
          
          # ACK the message by deleteting it
          os.remove(self.ourpath + file)
          
          # Notify the new data
          self.received_data_callback(self.uniqueid, senderid, message, replyreuested, connectiontype)
          
  def sendMessage(self, peerid, message, replyreuested="noreply", connectiontype="permanent"):
    peerpath = self.basepath + peerid
    if not os.path.exists(peerpath):
      os.makedirs(peerpath)   
      # Acquire our own folder
      self.btclient.add_sync_folder(peerpath, peerid)

    peerfile = self.uniqueid + "_" + replyreuested + "_" + connectiontype + ".fsbc_oi"
    f = open(peerpath + "/" + peerfile, 'w')
    f.write(message)
    f.close()
   
   
