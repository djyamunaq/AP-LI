#!/usr/bin/python3
import re
import os
import sys
import socket
import json
import base64
from common_comm import send_dict, recv_dict, sendrecv_dict

from Crypto.Cipher import AES

# Função para encriptar valores a enviar em formato jsos com codificação base64
# return int data encrypted in a 16 bytes binary string coded in base64
def encrypt_intvalue(cipherkey, data):
	return None


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary strings coded in base64
def decrypt_intvalue(cipherkey, data):
	return None


# verify if response from server is valid or is an error message and act accordingly
def validate_response(client_sock, response):
	# If error in response -> print error, close socket and exit with error code 3
	if 'error' in response:
		print(response['error'])
		client_sock.close()
		exit(3)
	return True

# process QUIT operation
def quit_action(client_sock, attempts):
	res = sendrecv_dict(client_sock, { 'op': 'QUIT' })

	# Process response
	if 'error' in res:
		print(res['error'])
	else:
		print('Connection terminated successfully')

	# End connection and exit with error 4
	client_sock.close()
	exit(4)

# Outcomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP" }
#
# Incomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, min, max }

def print_help():
	print('<')
	print('COMMANDS')
	print('\tSTART CLIENT_ID\t\t:\tStart connection with server')
	print('\tNUMBER VALUE\t\t:\tSend number to server')
	print('\tSTOP\t\t\t:\tProcess result and end connection')
	print('\tQUIT\t\t\t:\tEnd connection without processing result')
	print('>')

# 
# Build request to send to server from high level command from user 
#
def command_to_request(command, client_id,  cipher):
	# Get number of arguments from command
	argc = len(command)

	# Get operation from command
	op = command[0]

	# Outcomming message structure:
	# { op = "START", client_id, [cipher] }
	# { op = "QUIT" }
	# { op = "NUMBER", number }
	# { op = "STOP" }
	if op == 'START':
		if argc != 1:
			print('[ERROR] Wrong number of Arguments for \'START\' request')
			exit(1)

		return { 'op': 'START', 'client_id': client_id, 'cipher': cipher }

	if op == 'NUMBER':
		if argc != 2:
			print('[ERROR] Wrong number of Arguments for \'NUMBER\' request')
			exit(1)

		number = command[1]

		return { 'op': 'NUMBER', 'number': number }

	if op == 'STOP':
		if argc != 1:
			print('[ERROR] Wrong number of Arguments for \'STOP\' request')
			exit(1)

		return { 'op': 'STOP' }

	if op == 'QUIT':
		if argc != 1:
			print('[ERROR] Wrong number of Arguments for \'QUIT\' request')
			exit(1)

		return { 'op': 'QUIT' }
	
	# If command does not exist, print error and end program with code 1
	print('[ERROR] Operation \'%s\' unknown' % (op))
	exit(1)

#
# Suporte da execução do cliente
#
def run_client(client_sock, client_id):
	print('- Commands in format \'OPERATION ARGS\'\n- Type h for help\n- Type q to quit\n- Press ENTER to confirm\'\n')

	while True:
		# Get command from user
		command = input()

		# Process help request
		if command == 'h':
			print_help()
			continue
		if command == 'q':
			break
		
		# Process other requests
		command = command.split(' ')

		# Get request from command format	
		request = command_to_request(command, client_id, None)
		# Send request to server and get response
		response = sendrecv_dict(client_sock, request)
		# print response
		print(response)

	return None
	
def print_connection_details(client_id, port, hostname):
	print('CLIENT_ID\t:\t', client_id)
	print('PORT\t\t:\t', port)
	print('HOSTNAME\t:\t', hostname)

def main():
	# Get number of arguments and values
	argc = len(sys.argv)
	argv = sys.argv

	# Validate the number of arguments and eventually print error message and exit with error
	if argc < 3 or argc > 4:
		print('[ERROR] Wrong number of Arguments for Client Connection')
		exit(1)

	# Verify format for port (Positive Integer)
	if not argv[2].isdigit():
		print('[ERROR] Invalid value for port: \'', argv[2], '\'')
		exit(2)
	# Verify format for hostname (IPv4 Format) 
	try:
		if argc == 4:
			socket.inet_aton(argv[3])
	except socket.error:
		print('[ERROR] Invalid value for hostname: \'', argv[3], '\'')
		exit(2)

	# Get client connection details from arguments
	client_id = argv[1]
	port = argv[2]
	hostname = 'localhost'
	if argc == 4:
		hostname = argv[3]
	
	port = int(port)
	
	# DEBUG-START
	print_connection_details(client_id, port, hostname)
	# DEBUG-END

	# Prepare and connect socket 
	client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_sock.connect((hostname, port))

	# Run client
	run_client(client_sock, client_id)

	# End connection
	client_sock.close()
	exit(0)

if __name__ == "__main__":
    main()
