# header files
import socket
import sys
import threading
from threading import Thread
import socketserver
import os
import time
import random
from random import randint

# set global variables
NID = 0
hostname = ' '
udp_port = 0
tcp_port = 0
l1_NID = 0
l2_NID = 0
l3_NID = 0
l4_NID = 0
l1_hostname = ' '
l2_hostname = ' '
l3_hostname = ' '
l4_hostname = ' '
l1_udp_port = 0
l2_udp_port = 0
l3_udp_port = 0
l4_udp_port = 0
l1_tcp_port = 0
l2_tcp_port = 0
l3_tcp_port = 0
l4_tcp_port = 0

# create node object variable
node = None

# function: InitializeTopology
def InitializeTopology (nid, itc):

	# global variables
	global node

	# initialize node object
	node = Node(int(nid))

	# open itc.txt file and read to list
	infile = open(itc)
	list = infile.readlines()

	# initialize lists for hostnames and port numbers
	hostnames = []
	ports = []

	# populate hostname and port lists
	for entry in list:
		temp = entry.split(' ')
		hostnames.append(temp[1])
		ports.append(int(temp[2]))

	# use list to populate LinkTable and PortTable
	for entry in list:
		temp = entry.split(' ')
		node.Set_link_table(int(temp[0]), (int(temp[3]), int(temp[4]), int(temp[5]), int(temp[6])))
		node.Set_address_data_table(int(temp[0]), temp[1], int(temp[2]))

		# set parameters for for this node
		if node.GetNID() == int(temp[0]):
			node.SetHostName(temp[1])
			node.SetPort(int(temp[2]))

			# set starting point
			number_of_nodes = len(temp) - 3
			index = 3

			# iterate through and add all links for this node
			for i in range(number_of_nodes):
				corresponding_hostname = hostnames[int(temp[index+i])-1]
				corresponding_port = ports[int(temp[index+i])-1]
				node.AddLink((int(temp[index+i]), corresponding_hostname, corresponding_port))

	node.routing_table = [16] * len(list)
	node.routing_table[node.GetNID() - 1] = 0
	node.forwarding_table = [0] * len(list)

	# close itc.txt file
	infile.close()

	# return object
	return node

# class: Node
class Node(object):

	# initialize node
	def __init__ (self, nid=0, host_name=None, udp_port=0, links=[], address_data_table = [], link_table={}):
		self.nid = nid
		self.host_name = host_name
		self.udp_port = udp_port

		if links is not None:
			self.links = list(links)

		self.upL1 = False
		self.upL2 = False
		self.upL3 = False
		self.upL4 = False
		self.link_table = {}
		self.address_data_table = {}

		# Grant
		#	List of live Get_Connections
		#	Store routing table
		self.connections = []
		self.routing_table = [[]]

	# get nid
	def GetNID (self):
		return self.nid

	# get hostname
	def GetHostName (self):
		return self.host_name

	# get port number
	def GetPort (self):
		return self.udp_port

	# get list of links
	def GetLinks (self):
		return self.links

	# get link table (all links)
	def Get_link_table (self):
		return self.link_table

	# get port table (all ports)
	def Get_address_data_table (self):
		return self.address_data_table

	# get up flag for neighbor 1
	def GetUpFlagL1 (self):
		return self.upL1

	# get up flag for neighbor 2
	def GetUpFlagL2 (self):
		return self.upL2

	# get up flag for neighbor 1
	def GetUpFlagL3 (self):
		return self.upL3

	# get up flag for neighbor 2
	def GetUpFlagL4 (self):
		return self.upL4

	# set up flag for neighbor 1
	def SetUpFlagL1 (self, flag):
		self.upL1 = flag

	# set up flag for neighbor 2
	def SetUpFlagL2 (self, flag):
		self.upL2 = flag

	# set up flag for neighbor 1
	def SetUpFlagL3 (self, flag):
		self.upL3 = flag

	# set up flag for neighbor 2
	def SetUpFlagL4 (self, flag):
		self.upL4 = flag

	# set nid
	def SetNID (self, nid):
		self.nid = nid

	# set hostname
	def SetHostName (self, host_name):
		self.host_name = host_name

	# set port number
	def SetPort (self, udp_port):
		self.udp_port = udp_port

	# add link to links list
	def AddLink (self, individual_link):
		self.links.append(individual_link)

	# set link table
	def Set_link_table (self, source_nid, neighbor_nid):
		self.link_table[source_nid] = neighbor_nid
		#pass

	# set port table
	def Set_address_data_table (self, nid, hostname, port):
		self.address_data_table[nid] = nid, hostname, port

	# Grant
	#	Gets live neighbors
	def Get_Connections (self):
		self.connections = Update_Connections()
		return self.connections

# class TCP Handler (this receives all TCP messages)
class MyTCPHandler(socketserver.BaseRequestHandler):

	def handle(self):

		# global variables
		global NID, hostname, tcp_port
		global l1_hostname, l2_hostname, l3_hostname, l4_hostname
		global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port
		global l1_NID, l2_NID, l3_NID, l4_NID
		global add_counter, update_counter, remove_counter

		self.data = self.request.recv(1024)
		message = self.data

        # Grant:
		#    Use message with length 0 to check if node is actively connected
		#    Use 0 at front of message to signify traditional message
		#    Use 1 at front of message to signify router table message
		if len(message) > 0:
			message = ''.join(message.decode().split())
			identifier = message[0]
			message = message[1:]

			if identifier == "0":

				#Check destination id, if id is current node print message, otherwise send to next node
				print("Start separating message: " + str(message))
				message_info = eval(message)
				dest_nid = message_info[0]

				if dest_nid == str(NID):
					print(message_info[1])
					os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")
				else:
					send_tcp(dest_nid, message_info[1])

			#table[0] is nid of sender, table[1] is node's routing_table
			elif identifier == "1":
				table = eval(message)
				print("Initial Character not 0: " + str(table))
				Update_Table(table[0], table[1])
		else:
			print("Len = 0: " + str(message))


# Class: MyUDPHandler (this receives all UDP messages)
class MyUDPHandler(socketserver.BaseRequestHandler):

	# interrupt handler for incoming messages
	def handle(self):

		# parse received data
		data = self.request[0].strip()

		# set message and split
		message = data
		message = ''.join(message[1:].decode().split())
		print(message)
		os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")

# Function: sendto()
def send_tcp(dest_nid, message):

	# global variables
	global node, NID, hostname, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port
	global l1_NID, l2_NID, l3_NID, l4_NID

	#Use forwarding table to determine where message should go
	destination = str(node.forwarding_table[int(dest_nid) - 1])

	# look up address information for the destination node
	if destination == str(l1_NID):
		HOST = l1_hostname
		PORT = l1_tcp_port

	elif destination == str(l2_NID):
		HOST = l2_hostname
		PORT = l2_tcp_port

	elif destination == str(l3_NID):
		HOST = l3_hostname
		PORT = l3_tcp_port

	elif destination == str(l4_NID):
		HOST = l4_hostname
		PORT = l4_tcp_port

	else:
	    #   Gary:
	    #       I'm thinking here's what we can do:
	    #       instead of grabbing the links of each linked node from the original node,
	    #       we can just send the message onwards to the linked nodes, but append it with
	    #       a specific format in front of the message like this:
	    #           message = 'x1' + 'x2' + "F" + rest of message
	    #               where x1 is the original node ID
	    #                     x2 is the actual target node ID
	    #                     F is just a symbolic tag to check for to notify a "forwarding"
	    #                     of a message
	    #       Idea is we can send the message out to linked nodes, then when they get it, we check for the
	    #       3rd element, and if it is specifically an 'F', then read the first two elements in as the original node ID
	    #       and the target node ID. If in this new node there exists a link to x2's ID, then send the original message
	    #       which exists from message[3:] (3rd element on), and send back a confirmation message to x1's original ID.
	    #       If no link exists to x2, then send the message to all linked nodes again and repeat until
	    #       the message is received?
		print('no address information for destination')

    #   Grant:
    #       Changed from original to append '0' at the front of the message
	#		Add destination to message as part of list with message
	#		Easy to convert lists to strings and back
	# encode message as byte stream
	message = ("0" + str([dest_nid, message])).encode()

	# send message
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((HOST, PORT))
		sock.sendall(message)
		sock.close()

	except:
		print('error, message not sent')
		pass

# function: hello (alive)
def send_udp(dest_nid, message):

	# global variables
	global NID, hostname, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port
	global l1_NID, l2_NID, l3_NID, l4_NID

	if dest_nid == str(l1_NID):
		HOST = l1_hostname
		PORT = l1_udp_port

	elif dest_nid == str(l2_NID):
		HOST = l2_hostname
		PORT = l2_udp_port

	elif dest_nid == str(l3_NID):
		HOST = l3_hostname
		PORT = l3_udp_port

	elif dest_nid == str(l4_NID):
		HOST = l4_hostname
		PORT = l4_udp_port

	else:
		print('no address information for destination')

	# encode message as byte stream
	message = message.encode()

	try:
		# open socket and send to neighbor 4
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
		sock.sendto(message, (HOST, PORT))
	except:
		print('error, message not sent')
		pass

# function: start listener
def start_listener():

	# global variables
	global node, NID, hostname, udp_port, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_udp_port, l2_udp_port, l3_udp_port, l4_udp_port
	global l1_tcp_port, l2_tcp_port, l3_tcp_port, l4_tcp_port
	global l1_NID, l2_NID, l3_NID, l4_NID

	# check links for node attributes
	links = node.GetLinks()
	link1 = links[0]
	link2 = links[1]
	link3 = links[2]
	link4 = links[3]

	# set link attributes
	l1_NID = link1[0]
	l1_hostname = link1[1]
	l1_udp_port = link1[2]
	l1_tcp_port = l1_udp_port + 500

	l2_NID = link2[0]
	l2_hostname = link2[1]
	l2_udp_port = link2[2]
	l2_tcp_port = l2_udp_port + 500

	l3_NID = link3[0]
	l3_hostname = link3[1]
	l3_udp_port = link3[2]
	l3_tcp_port = l3_udp_port + 500

	l4_NID = link4[0]
	l4_hostname = link4[1]
	l4_udp_port = link4[2]
	l4_tcp_port = l4_udp_port + 500

	hostname = node.GetHostName()
	NID = node.GetNID()
	udp_port = node.GetPort()
	tcp_port = udp_port + 500

	# slight pause to let things catch up
	time.sleep(2)

	# start thread for listener
	t1 = threading.Thread(target=TCP_listener)
	t1.daemon=True
	t1.start()

	# start thread for listener
	t2 = threading.Thread(target=UDP_listener)
	t2.daemon=True
	t2.start()

# function: TCP listener
def TCP_listener():

	# global variables
	global hostname, tcp_port

	# set socket for listener
	server = socketserver.TCPServer((hostname, tcp_port), MyTCPHandler)
	server.serve_forever()

# function: receiver (listener)
def UDP_listener():

 	# global variables
	global hostname, udp_port

	# set socket for listener
	server = socketserver.UDPServer((hostname, udp_port), MyUDPHandler)
	server.serve_forever()

# print status
def PrintInfo():

	# global variables
	global node, NID, hostname, udp_port, tcp_port

	# output data
	os.system('clear')
	print("NID: " + str(NID))
	print("Link Table: " + str(node.Get_link_table()))

	print("Address Data: " + str(node.Get_address_data_table()))

	print("Links: ")
	for link in node.Get_Connections():
		print("	" + str(link))

	print("Routing Table: " + str(node.routing_table))
	print("Forwarding Table: " + str(node.forwarding_table))

	os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")

#NOTE My functions
def Update_Connections():

	# global variables
	global NID, hostname, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port
	global l1_NID, l2_NID, l3_NID, l4_NID

	ports = (l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port)
	connections = []

	for index, link in enumerate(node.GetLinks()):
		# send message
		HOST = link[1]
		PORT = ports[index]
		table_info = [NID, node.routing_table]
		message = ("1" + str(table_info)).encode()

		if link[0] != 0:
			try:
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.connect((HOST, PORT))
				sock.sendall(message)
				sock.close()
				connections.append(link[0])

				#if node is connected, cost is 1
				node.routing_table[link[0] - 1] = 1
				node.forwarding_table[link[0] - 1] = link[0]

			except:

				#if node is not connected, cost is infinity
				#dv has a max cost of 16
				node.routing_table[link[0] - 1] = 16
				pass

	return connections

def Update_Table(source_nid, table):
	# global variables
	global NID, hostname, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port
	global l1_NID, l2_NID, l3_NID, l4_NID

	#Used to compare new table to see if anything has changed
	#if something has changed other nodes need to be notified
	curr_table = node.routing_table.copy()

	#if recieving message, that node must be neighbor, therefore hop count is 1
	node.routing_table[source_nid - 1] = 1

	#if the distance to a node is shorter than currently in routing table, table is changed
	for index in range(0, len(table)):
		dist = node.routing_table[source_nid - 1] + table[index]
		if node.routing_table[index] > dist:
			print("Shorter route: " + str(dist))
			node.routing_table[index] = dist
			node.forwarding_table[index] = source_nid

	#Notify connected nodes of any changes in routing table
	if node.routing_table == curr_table:
		print("No Changes")
	else:
		print("Has Changed")
		node.Get_Connections()

	print("Routing Table: " + str(node.routing_table))
	print("Forwarding Table: " + str(node.forwarding_table))

# main function
def main(argv):

	# global variables
	global node

	# set initial value for loop
	run = 1

	# check for command line arguments
	if len(sys.argv) != 3:
		print("Usage: <program_file><nid><itc.txt>")
		exit(1)

	# initialize node object
	node = InitializeTopology(sys.argv[1], sys.argv[2])

	# start UDP listener
	start_listener()

	#Update_Connections()

	# loop
	while(run):

		#print menu options
		os.system('clear')
		print("Enter 'info' to check network information")
		print("Enter 'send_tcp' to message another node via TCP")
		print("Enter 'send_udp' to message another node via UDP")
		print("Enter 'quit' to end program")

		# set selection value from user
		selection = input("Enter Selection: ")

		# selection: status
		if selection == 'info':
			PrintInfo()

		# selection: send_tcp
		elif(selection == 'send_tcp'):
			os.system('clear')
			dest_nid = input("enter node to message: ")
			message = input("enter the message you want to send: ")
			send_tcp(dest_nid, message)
			os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")

		# selection: send_udp
		elif(selection == 'send_udp'):
			os.system('clear')
			dest_nid = input("enter node to message: ")
			message = input("enter the message you want to send: ")
			send_udp(dest_nid, message)
			os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")

		# selection: quit
		elif(selection == 'quit'):
			run = 0
			os.system('clear')

		elif(selection == 'connections'):
			os.system('clear')
			Update_Connections()
			os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")

		elif(selection == 'send_ad'):
			os.system('clear')
			Send_state_advertisement()
			os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")

		else:

			# default for bad input
			os.system('clear')
			time.sleep(.5)
			continue

# initiate program
if __name__ == "__main__":
	main(sys.argv)
