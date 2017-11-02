import sys
import socket
import select

HOST = '' 
SOCKET_LIST = []
RECV_BUFFER = 4096 
PORT = 9009
def chat_server():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((HOST, PORT))
	server_socket.listen(10)
	SOCKET_LIST.append(server_socket)
	with open('DATA/auth.txt') as f:
		auth = f.readlines()
	auth = [x.strip() for x in auth]
	online_user = {}
	online_sock = {}
	while 1:
		ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
		for sock in ready_to_read:
			if sock == server_socket: 
				sockfd, addr = server_socket.accept()
				buff = []
				buff = sockfd.recv(4096)
				print buff
				username = buff.split(":")[0]
				flag = 0;
				for j in auth:
					if j == buff:
						flag = 1;
						break;
				if flag:
					SOCKET_LIST.append(sockfd)
					online_user[username] = sockfd
					online_sock[sockfd] = username
					print "Client (%s, %s) connected" % addr
					sockfd.send("Authenticated");
			else:
				# process data recieved from client, 
				try:
					# receiving data from the socket.
					data = sock.recv(RECV_BUFFER)
					senduser = online_sock[sock]
					if data:
						parse = data.split(" ")
						command1 = parse[0];
						command2 = data.split("\n")[0]
						if command1 == 'broadcast':
							message = senduser + ':' + ' '.join(parse[1:])
							for s in SOCKET_LIST:
								if s != server_socket and s != sock:
									s.send(message)
						elif command1 == 'message':
							recvuser = parse[1]
							message = senduser + ':' + ' '.join(parse[2:])
							if online_user.has_key(recvuser):
								usersock = online_user[recvuser]
								usersock.send(message)
							else :
								with open('DATA/'+recvuser+'.txt', "a") as myfile:
									myfile.write(message)
						elif command2 == 'whoelse':
							users = []
							for key, value in online_user.items():
								if key != senduser:
									users.append(key)
							message = 'Server:'+','.join(users)
							sock.send(message)
						# there is something in the socket
						# broadcast(server_socket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data)  
					else:
						# remove the socket that's broken    
						if sock in SOCKET_LIST:
							SOCKET_LIST.remove(sock)

						# at this stage, no data means probably the connection has been broken
						# broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr) 

				# exception 
				except:
					# broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
					continue
if __name__ == "__main__":
	sys.exit(chat_server())         