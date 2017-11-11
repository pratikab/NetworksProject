import sys
import socket
import select
import time
HOST = '' 
SOCKET_LIST = []
RECV_BUFFER = 4096 
PORT = 9010
def chat_server():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((HOST, PORT))
	server_socket.listen(10)
	SOCKET_LIST.append(server_socket)
	with open('DATA/auth.txt') as f:
		auth = f.readlines()
	auth = [x.strip() for x in auth]
	users_avail = []
	blocked_list = {}
	for a in auth:
		us = a.split(":")[0]
		blocked_list[us] = []
		users_avail.append(us)
	connection_info = {}
	online_user = {}
	online_sock = {}
	block_ip = {}
	logged_out = {}
	while 1:
		ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
		for sock in ready_to_read:
			if sock == server_socket: 
				sockfd, addr = server_socket.accept()
				if addr[0] in block_ip:
					if time.time()-block_ip[addr[0]] < 60:
						sockfd.send("IP has been blocked");
						continue
				buff = []
				buff = sockfd.recv(4096)
				username = buff.split(":")[0]
				if username in online_user:
					sockfd.send("User already logged in")
					continue
				flag = 0;
				for j in auth:
					if j == buff:
						flag = 1;
						break;
				if flag:
					SOCKET_LIST.append(sockfd)
					online_user[username] = sockfd
					online_sock[sockfd] = username
					print "Client %s connected" % username
					sockfd.send("Authenticated");
				else:
					if addr[0] in connection_info:
						connection_info[addr[0]] += 1
						if connection_info[addr[0]] >=3:
							print "blocked %s" %addr[0]
							block_ip[addr[0]] = time.time()
					else:
						connection_info[addr[0]] = 1
					if connection_info[addr[0]] > 0:
						sockfd.send("Please check username and password, You have "+str(3 - connection_info[addr[0]])  +" attempts left");
					else:
						sockfd.send("Your IP has been blocked for 60 seconds")
			else:
				try:
					data = sock.recv(RECV_BUFFER)
					senduser = online_sock[sock]
					if data:
						data = data.split("\n")[0]
						parse = data.split(" ")
						command1 = parse[0];
						if command1 == 'broadcast':
							message = senduser + ':' + ' '.join(parse[1:])
							for s in SOCKET_LIST:
								if s != server_socket and s != sock:
									recvuser = online_sock[s]
									if senduser in blocked_list[recvuser]:
										continue
									s.send(message)
						elif command1 == 'message' and parse[1] is not None :
							recvuser = parse[1]
							if senduser in blocked_list[recvuser]:
								continue
							if recvuser in users_avail:
								message = senduser + ':' + ' '.join(parse[2:])
								if online_user.has_key(recvuser):
									usersock = online_user[recvuser]
									usersock.send(message)
								else :
									with open('DATA/'+recvuser+'.txt', "a") as myfile:
										myfile.write(message)
						elif command1 == 'whoelse':
							users = []
							for key, value in online_user.items():
								if key != senduser:
									users.append(key)
							message = 'Server:'+','.join(users)
							sock.send(message)
						elif command1 == 'wholasthr':
							users = []
							for us, value in online_user.items():
								if us != senduser:
									users.append(us)
							for us in logged_out:
								if us != senduser:
									if time.time()-logged_out[us] <= 3600 and us not in users :
											users.append(us)
									else:
										logged_out.pop(us,None)
							message = 'Server:'+','.join(users)
							sock.send(message)
						elif command1 == 'block' and parse[1] is not None:
							usr = parse[1]
							if usr in users_avail:
								blocked_list[senduser].append(usr);
								sock.send("Server : Blocked "+usr)
							else:
								sock.send("Server: No such user")
						elif command1 == 'unblock'and parse[1] is not None:
							usr = parse[1]
							if usr in users_avail:
								blocked_list[senduser].remove(usr);
								sock.send("Server : Unblocked "+usr)
							else:
								sock.send("Server: No such user")
						elif command1 == 'logout':
							if sock in SOCKET_LIST:
								SOCKET_LIST.remove(sock)
								temp_user = online_sock[sock]
								online_sock.pop(sock)
								online_user.pop(temp_user)
								logged_out[temp_user] = time.time()
								print "Client %s disconnected" % temp_user
								sock.send("Logout");
								sock.close()
						else:
							message = 'Server: Please Enter Valid Command'
							sock.send(message)
					else:
						if sock in SOCKET_LIST:
							SOCKET_LIST.remove(sock)
							temp_user = online_sock[sock]
							online_sock.pop(sock)
							online_user.pop(temp_user)
							logged_out[temp_user] = time.time()
							print "Client %s disconnected" % temp_user
							sock.close()
				except:
					continue
if __name__ == "__main__":
	sys.exit(chat_server())         