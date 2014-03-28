msgp2p is a lightweight messaging system that allows peers located anywhere on the network to exchance messages with each other without any prior knowledge other than an arbitrary long unique identified assigned to the peer they want to send a message to.

msgp2p is fully distributed and operates without a central server and behind various types of firewalls and NAT devices without the need for the user to configure them nor have knowledge about them.

msgp2p defines a simple paradigm to send messages (strings of characters) to a peer with a given unique id. It also allows to optionally create logical channels so that different information types can be conveyed to an appropriate sub-system of the peer.

At the current state msgp2p uses Bit Torrent Sync as a bearer, so it in fact encapsulates messages into files. The diagram below shows the overall concept. More detailed information is available in the wiki|https://github.com/nicolacimmino/msgp2p/wiki 

![Basic Flow](https://github.com/nicolacimmino/msgp2p/wiki/diagrams/iotp2p_btsync.png)
