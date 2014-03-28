msgp2p is a lightweight messaging system that allows peers located anywhere on the network to exchange messages with each other without any prior knowledge other than an arbitrary long unique identified assigned to the peer they want to send a message to.

msgp2p is fully distributed and operates without a central server and behind various types of firewalls and NAT devices without the need for the user to configure them nor have knowledge about them.

msgp2p defines a simple paradigm to send messages (strings of characters) to a peer with a given unique id. It also allows to optionally create logical channels so that different information types can be conveyed to an appropriate sub-system of the peer.

In the current state msgp2p uses Bit Torrent Sync as a bearer, so it in fact encapsulates messages into files. The diagram below shows the overall concept. More detailed information is available in the [wiki] (https://github.com/nicolacimmino/msgp2p/wiki). 

![Basic Flow](https://github.com/nicolacimmino/msgp2p/wiki/diagrams/iotp2p_btsync.png)

While this satisfies all the original requirements it has the downside of introducing a considerable lag which is, usally, in the order of some tens of seconds.

msgp2p can be used either as a connand in a Linux shell or as a python library to be included in a larger project.

##Shell Usage

You can use msgp2p as follows to send a message:

    msgp2p send address message


To receive:

    msgp2p receive address

For instance on one shell you could run:

    msgp2p send ADTPPHNFX6U6QIW72P7GYB5CAEOBNN7CM This is a test message

and in another run:

    msgp2p receive ADTPPHNFX6U6QIW72P7GYB5CAEOBNN7CM
    
When the message is received msgp2p will terminate after printing the message content.


##Python Usage

You can include msgp2p in your python script and use it to programmatically send and receive messages. And example application that sends and receives messages is included in the "excamples" folder.
