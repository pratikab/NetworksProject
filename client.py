import sys
import socket
import select
import os.path

def chat_client():
    if(len(sys.argv) < 3) :
        print 'Usage : python2 client.py hostname port'
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print 'Unable to connect'
        sys.exit()
     
    var = raw_input("Enter 'Username:Password' - ")
    auth = str(var);
    user = auth.split(":")[0]
    s.send(var);
    buff = []
    buff = s.recv(4096);
    print buff
    if buff == 'Authenticated':
        print 'You can start sending messages now'
        fname = 'DATA/'+user+'.txt'
        if os.path.isfile(fname) :
	        with open(fname,"r+") as f:
	            data = f.read()
	            if data != '':
	                print data
	            f.write('')
	            f.truncate(0)
    else:
    	s.close()
    	return 
    while 1 :
        socket_list = [sys.stdin, s]
        ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])
        for sock in ready_to_read:             
            if sock == s:
                buff = []
                buff = s.recv(4096);
                if buff == "Logout":
                	s.close()
                	return
                print buff;

            else :
                msg = sys.stdin.readline()
                s.send(msg)

if __name__ == "__main__":
    sys.exit(chat_client())