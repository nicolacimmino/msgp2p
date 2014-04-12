#!/usr/bin/env python
# send is part of msgp2p and is an example of msgp2p message sending.
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

#
# This callback function is invoked every time we receive a message.
def dataReceived(localUID, remoteUID, message, logicalchannel):
 print "Remote UID: " + remoteUID
 print "LCH: " + logicalchannel
 print "Message: " + message
 msgp2p.stoplistening = True
 exit(0)
 
# Createe an instance with our local address and set "dataReceived" as callback
# function for received messages.
msgp2p = msgp2p("AZVDUR5W2IC4AFZZFRSWZMTSW2HHVUCMY", dataReceived);


