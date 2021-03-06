#!/usr/bin/python3

import sys
import socket
import select
import json
import base64
import csv
import random
from common_comm import send_dict, recv_dict, sendrecv_dict

from Crypto.Cipher import AES

# Dicionário com a informação relativa aos clientes
users = {}

# return the client_id of a socket or None
def find_client_id(client_sock):
	for user_id in users:
		user = users[user_id]
		if user['socket'] == client_sock:
			return user_id
	return None


# Função para encriptar valores a enviar em formato json com codificação base64
# return int data encrypted in a 16 bytes binary string and coded base64
def encrypt_intvalue (client_id, data):
	return None


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary string and coded base64
def decrypt_intvalue (client_id, data):
	return None


# Incomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP" }
#
# Outcomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, min, max }


#
# Suporte de descodificação da operação pretendida pelo cliente
#
def new_msg (client_sock):
	# Get request from client
	req = recv_dict(client_sock)

	# Get operation from request
	op = req['op']

	if op == 'START':
		return new_client(client_sock, req)
	if op == 'QUIT':
		return quit_client(client_sock, req)
	if op == 'NUMBER':
		return number_client(client_sock, req)
	if op == 'STOP':
		return stop_client(client_sock, req)

#
# Suporte da criação de um novo jogador - operação START
#
def new_client (client_sock, request):
	# Validate if client_id field is included in request
	if 'client_id' not in request:
		return send_dict(client_sock, { 'op': 'START', 'status': False, 'error': 'No \'client_id\' field in START request'})
	
	client_id = request['client_id']

	# Verify that client_id is not in use
	if client_id in users.keys():
		errorMsg = '[ERROR] Client with client_id \'' + str(client_id) + '\' already connected'
		return send_dict(client_sock, { 'op': 'START', 'status': False, 'error':  errorMsg})
	
	# Add user register to users dictionary
	users[client_id] = { 'socket': client_sock, 'numbers': [] }

	# Return successful message to client
	return send_dict(client_sock, { 'op': 'START', 'status': True })

#
# Suporte da eliminação de um cliente
#
def clean_client (client_sock):
	# Find client id
	client_id = find_client_id(client_sock)
	# If client exists, remove from users dictionary
	if client_id is not None:
		del users[client_id]

#
# Suporte do pedido de desistência de um cliente - operação QUIT
#
def quit_client (client_sock, request):
	# Get client_id from client_sock
	client_id = find_client_id(client_sock)

	# Verify that client_id is active
	# If not, send response with error message
	if client_id is None:
		errorMsg = '[ERROR] Client not active'
		return send_dict(client_sock, { 'op': 'QUIT', 'status': False, 'error':  errorMsg})
	
	# Clean client data
	clean_client(client_sock)

	# Return success message to client
	return send_dict(client_sock, { 'op': 'QUIT', 'status': True })

#
# Suporte da criação de um ficheiro csv com o respectivo cabeçalho
#
def create_file ():
	# Header list for the report.csv
	header = ['CLIENT_ID', '#VALUES', 'MIN', 'MAX']

	# Open file and write header
	file = open('./report.csv', 'w')
	writer = csv.writer(file)
	writer.writerow(header)

#
# Suporte da actualização de um ficheiro csv com a informação do cliente e resultado
#
def update_file (client_id, result):
	file = open('./report.csv', 'a')
	writer = csv.writer(file)
	writer.writerow(result)

#
# Suporte do processamento do número de um cliente - operação NUMBER
#
def number_client (client_sock, request):
	client_id = find_client_id(client_sock)

	# Check if client is active
	# If not, send response with error message
	if client_id is None:
		errorMsg = '[ERROR] Client with client_id \'' + str(client_id) + '\' not active'
		return send_dict(client_sock, { 'op': 'NUMBER', 'status': False, 'error':  errorMsg})

	# Get number from request
	number = request['number']

	# Check if number only contain digits (Therefore int type)
	if not number.isdigit():
		errorMsg = '[ERROR] Wrong format for \'value\' argument in \'NUMBER value\' command'
		return send_dict(client_sock, { 'op': 'NUMBER', 'status': False, 'error':  errorMsg})

	# String to int
	number = int(number)
	# Add number to client list
	users[client_id]['numbers'].append(number)

	# Return success message to client
	return send_dict(client_sock, { 'op': 'NUMBER', 'status': True})

#
# Suporte do pedido de terminação de um cliente - operação STOP
#
def stop_client (client_sock, request):
	client_id = find_client_id(client_sock)

	# Check if client is active
	# If not, send response with error message
	if client_id is None:
		errorMsg = '[ERROR] Client not active'
		return send_dict(client_sock, { 'op': 'STOP', 'status': False, 'error':  errorMsg })

	# Process client's number list
	numbers = users[client_id]['numbers']

	if len(numbers) > 0:
		# Get max and min from list
		maxNum = max(numbers)
		minNum = min(numbers)
		# Write data in report
		row = [client_id, len(numbers), minNum, maxNum]
		update_file(client_id, row)
		# Build response message
		res = send_dict(client_sock, { 'op': 'STOP', 'status': True, 'min': minNum, 'max': maxNum})
	else:
		# Build response message
		errorMsg = '[ERROR] Not enough data to process request from client \'' + str(client_id) + '\''
		res = send_dict(client_sock, { 'op': 'STOP', 'status': False, 'error':  errorMsg})

	# Clean client data
	clean_client(client_sock)

	# Return status message for operation to client
	return res


def main():
	# Get number of arguments and values
	argc = len(sys.argv)
	argv = sys.argv

	# Validate the number of arguments and eventually print error message and exit with error
	if argc != 2:
		print('[ERROR] Wrong number of Arguments for Client Connection')
		exit(1)

	# Verify format for port (Positive Integer)
	if not argv[1].isdigit():
		print('[ERROR] Wrong format for port \'', argv[1], '\'')
		exit(1)

	# Get server connection details from arguments
	port = int(argv[1])	
	
	server_socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind (("127.0.0.1", port))
	server_socket.listen (10)

	print('Server connected at PORT', port)

	clients = []
	create_file ()

	while True:
		try:
			available = select.select ([server_socket] + clients, [], [])[0]
		except ValueError:
			# Sockets may have been closed, check for that
			for client_sock in clients:
				if client_sock.fileno () == -1: client_sock.remove (client) # closed
			continue # Reiterate select

		for client_sock in available:
			# New client?
			if client_sock is server_socket:
				newclient, addr = server_socket.accept ()
				clients.append (newclient)
			# Or an existing client
			else:
				# See if client sent a message
				if len (client_sock.recv (1, socket.MSG_PEEK)) != 0:
					# client socket has a message
					##print ("server" + str (client_sock))
					new_msg (client_sock)
				else: # Or just disconnected
					clients.remove (client_sock)
					clean_client (client_sock)
					client_sock.close ()
					break # Reiterate select

if __name__ == "__main__":
	main()
