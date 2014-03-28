#!/usr/bin/env python
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
#
# This module can be included in a project and used as a library, in that case it
#   will provide a class named msgp2p with methods to send messages to any remoteUID
#   and with a notification system of received messages.
# It can also be run from command line in order to send, receive or act as an HTTP 
#   daemon that exposes a ReST API to send msgp2p messages.
#

import sys
import os
import time
import ConfigParser
from flask import Flask
from flask import request
from threading import Thread

class msgp2p:

  # Base folder inside which peer folders are created.
  basepath = "/var/msgp2p/"
  
  # Path to our folder where peers will communicate with us.
  ourpath = ""
  
  # The UID assigned to us to which we can receive messages.
  localUID = ""
  
  # If set will cause the listening thread to terminate.
  stoplistening = False
  
  # User function to be called when a message is received.
  received_data_callback = None
  
  # The BitTorrent client instance.
  # Node we do not create an instance here, and in fact we don't even import
  #   btclient library until it is needed. This is because importing the library
  #   and initializing seems to take a rather long time (about 15s). We do not need
  #   this library most of the times, just when we work on new UIDs.
  btclient = None
  
  #
  # Initialize the BitTorrent Sync Client. This is called only if the current operation
  #  requires interaction with the BTSync server.
  def initbtclient(self):
    # Get from the config file our settings
    config = ConfigParser.RawConfigParser()
    
    # Generally msgp2p should be configured from etc folder, we allow
    #   to have also a local configuration in the current folder
    #   expecially to aid during development. If a config is present
    #   in etc it has precedence.
    if os.path.exists('/etc/msgp2p/configuration.conf'):
      config.read('/etc/msgp2p/configuration.conf')
    else:
      config.read('./configuration.conf')
    
    btclienthost = config.get("[btsync]", 'host')
    btclientport = config.get("[btsync]", 'port')
    btclientusername = config.get("[btsync]", 'username')
    btclientpassword = config.get("[btsync]", 'password')

    import btsync
    self.btclient = btsync.Client( host=btclienthost, port=btclientport, username=btclientusername, password=btclientpassword)
 
  # Constructor.
  # Can be called parameterless for sending only operations. If receive is required both the localUID and the callback 
  #   function must be supplied.
  def __init__(self, localUID = "0000", received_data_callback = None):
      
      self.received_data_callback = received_data_callback
      
      # If we are not going to listen for incoming traffic there is no point
      # in binding the local folder. We also change localUID to "0000"
      # so that outgoing messages are not replied by peers.
      if received_data_callback == None:
        self.localUID = "0000"
        return
      
      self.localUID = localUID
            
      self.ourpath = self.basepath + self.localUID + "/"
      
      self.ensureBTSMonitoringForUID(localUID)
          
      # Monitor our folder
      thread = Thread( target = self.monitorFolder )
      thread.start()      

  # 
  # Internal function, makes sure that the local folder for a give UID is present
  # and that BTSync is monitoring that UID.
  def ensureBTSMonitoringForUID(self, uid):
    # If this is the first time we use this UID we need to create the 
    #   folder and map it to the UID in Bit Torrent Sync.
    localpath = self.basepath + uid + "/"
      
    if not os.path.exists(localpath):
      os.makedirs(localpath)           
      # Acquire our own folder in BTSync
      try:
        if self.btclient == None:
          self.initbtclient()
        self.btclient.add_sync_folder(localpath, uid)
      except:
        # Exception while adding folder. This is normal if the folder exists already, we could check but then we would hit
        #   the time penalty of importing btclient lib at every operation.
        pass
    
  #
  # Keeps watching the folder where the messages for our localUID will come and
  #   notifies the host on any incoming message. "stoplistening" needs to be set
  #   for the monitoring to end.
  def monitorFolder(self):
    while(not self.stoplistening):
      for file in os.listdir(self.ourpath):
        # We react only to .msgp2p files.
        if file.endswith(".msgp2p"):
        
          # We remove here the extension to simplify parsing.
          filename = file.translate(None, ".msgp2p")
          
          # Tokenize the filename on "_" and get needed elements
          tokens = filename.split("_")
          remoteUID = tokens[0]
          logicalchannel = tokens[1]
          f = open(self.ourpath + file, 'r')
          message = f.readline()
          f.close()
          
          # ACK the message by deleting it
          os.remove(self.ourpath + file)
          
          # Notify the new data
          self.received_data_callback(self.localUID, remoteUID, message, logicalchannel)
  
  #
  # Peeks a message for the specified localUID.
  # Note that first call to this function for a certain UID will not return messages
  #   as the folder will be mapped new. Host application must call peek repeatedly
  #   until a message is received.
  def peekMessage(self, localUID):
    peerpath = self.basepath + remoteUID
    
    # Make sure BTSync is monitoring the UID so our message goes out.
    self.ensureBTSMonitoringForUID(remoteUID)

    for file in os.listdir(peerpath):
      # We react only to .msgp2p files.
      if file.endswith(".msgp2p"):
      
        # We remove here the extension to simplify parsing.
        filename = file.translate(None, ".msgp2p")
        
        # Tokenize the filename on "_" and get needed elements
        tokens = filename.split("_")
        remoteUID = tokens[0]
        logicalchannel = tokens[1]
        f = open(self.ourpath + file, 'r')
        message = f.readline()
        f.close()
        
        # Notify the new data
        return (remoteUID, message, logicalchannel)
    
  
  #
  # Sends a message to the given remoteUID on the specified logical channel.
  def sendMessage(self, remoteUID, message, logicalchannel="msg"):
    peerpath = self.basepath + remoteUID
    
    # Make sure BTSync is monitoring the UID so our message goes out.
    ensureBTSMonitoringForUID(remoteUID)
    
    peerfile = self.localUID + "_" + logicalchannel + "_" + str(int(time.time())) + ".msgp2p"
    f = open(peerpath + "/" + peerfile, 'w')
    f.write(message)
    f.close()
 
#
# This callback function is used when msgp2p is used from command line to receive messages.
def dataReceived(localUID, remoteUID, message, logicalchannel):
 print "Remote UID: " + remoteUID
 print "LCH: " + logicalchannel
 print "Message: " + message
 msgp2p.stoplistening = True
 exit(0)
 
# HTTP ReSTful API for the HTTP gateway
app = Flask(__name__)

#
# HTTP ReSTful API.

# Resource: peer/UID
# Method: POST
# Action: Send a message to peer UID
# Parameters:
#   message = message to send
@app.route("/peer/<uid>", methods=['POST'])
def _res_resources_peer_post(uid, message):
  message = request.args.get('message')
  msgp2p.sendMessage(uid, message)
  return "OK"
  
# Resource: peer/UID
# Method: GET
# Action: Reads a message for UID
# Parameters:
#   localUID = receiving peer UID
@app.route("/peer/<uid>", methods=['GET'])
def _res_resources_peer_get(uid, message):
  localUID = request.args.get('localUID')
  (remoteUID, message, logicalchannel) = msgp2p.peekMessage(localUID)
  return message
  
#
# Starts a flask server.
def startFlaskServer():
    app.run( host = "0.0.0.0", port=4000, debug = False )
    
def printUsage():
    print "Usage: msgp2p send|receive|httpd localUID remoteUID [message]"
    
# If we are run in command line and not included as module we will behave
#  according to supplied args, if we are imported as a lib this section won't run.
if __name__ == "__main__":
  # Get command line parameters
  if not len(sys.argv) > 1:
    printUsage()
    exit(1)

  # Get the arguments.
  operation = sys.argv[1]
  
  # Send operation syntax is:
  # msgp2p send RemoteUID message body
  if operation == "send" and len(sys.argv) > 3:
    remoteUID = sys.argv[2]
    message = " ".join(sys.argv[3:])
    msgp2p = msgp2p(localUID, None)
    msgp2p.sendMessage(remoteUID, message)
    msgp2p.stoplistening = True
    exit(0)
  
  # Receive operation syntax is:
  # msgp2p receive LocalUID
  if operation == "receive" and len(sys.argv) > 2:
    localUID = sys.argv[2]
    msgp2p = msgp2p(localUID, dataReceived)
    exit(0)
    
  # HTTPD operation syntax is:
  # msgp2p httpd
  if operation == "httpd":
    thread = Thread( target = startFlaskServer  )
    thread.start()
    exit(0)
  
  # No valid command print usage an exit.  
  printUsage()
  exit(1)
