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
def encrypt_intvalue (cipherkey, data):
	return None


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary strings coded in base64
def decrypt_intvalue (cipherkey, data):
	return None


# verify if response from server is valid or is an error message and act accordingly
def validate_response (client_sock, response):
	return None


# process QUIT operation
def quit_action (client_sock, attempts):
	return None


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


#
# Suporte da execução do cliente
#
def run_client (client_sock, client_id):
	print('STARTING CONNECTION...')
	print(sendrecv_dict(client_sock, { 'op': 'QUIT' }))
	print(sendrecv_dict(client_sock, { 'op': 'START', 'client_id': client_id}))
	print(sendrecv_dict(client_sock, { 'op': 'NUMBER', 'number': 1 }))
	print(sendrecv_dict(client_sock, { 'op': 'NUMBER', 'number': 2 }))
	print(sendrecv_dict(client_sock, { 'op': 'NUMBER', 'number': 3 }))
	print(sendrecv_dict(client_sock, { 'op': 'STOP' }))
	
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
		print('[ERROR:1] Wrong number of Arguments for Client Connection')
		exit(1)

	# Verify format for port (Positive Integer)
	if not argv[2].isdigit():
		print('[ERROR:2] Invalid value for port: \'', argv[2], '\'')
		exit(1)
	# Verify format for hostname (IPv4 Format) 
	try:
		if argc == 4:
			socket.inet_aton(argv[3])
	except socket.error:
		print('[ERROR:] Invalid value for hostname: \'', argv[3], '\'')
		exit(1)

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
	client_sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	client_sock.connect ((hostname, port))

	# Run client
	run_client (client_sock, client_id)

	# End connection
	client_sock.close ()
	exit (0)

if __name__ == "__main__":
    main()
