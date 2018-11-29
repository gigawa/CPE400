This is a TCP/UDP socket client/server node that will communicate with it's neighbors to see if they are alive or not. Each
node will accept between 0-4 connections, and a network of any size can be built. The initial network topology is determined
by the itc.txt file. In sample-node.py, a node will only forward a message to its immediate neighbors.The idea
is to use this for a project wherein students will implement a routing algorithm that will forward traffic through a network of any size, propagating routing information across the network in a dynamic fashion.
Once built, nodes can be taken off line to see if the routing algorithm is actually working properly.

Three options are available by GUI; info, send_tcp, send_udp, and quit.
info: shows the current status of the node, including name, address, topology, neighbors
send_tcp/send_udp:   once running, the node will be able to send a text message to any other directly connected neighbor. To send a message to a non directly connected neighbor, a routing algorithm will be required (implemented by student).
quit:   this terminates the program.

To use, clone the 'Sockets' repo to a local file system. Open one terminal for each node in the network (they are all 'localhost' if you run them in your machine; if you run them on separate computers, an actual IP address (hostname) should be used in the itc.txt file).

Enter the following at the command line:

python3 sample-node.py <node-id> itc(x).txt

for example:

python network_node.py 1 itc3.txt

The node name for each node must be unique, i.e. 1, 2, 3,......9, 10.
