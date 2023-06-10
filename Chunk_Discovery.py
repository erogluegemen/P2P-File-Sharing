# Import Libraries
import os
import sys
import json
from socket import *
from sys import platform

#Color
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

# Define Constant Variables
IP = '10.0.31.255' # '192.168.2.255'  # provide your own local address here! (you can use ifconfig command in your terminal)
PORT = 5000
BUFFER_SIZE = 4096

'''# Retrieve the local IP address dynamically
if platform == "linux" or platform == "linux2":
    # Linux
    IP = gethostbyname_ex(gethostname())[2][0]
elif platform == "darwin":
    # macOS
    IP = gethostbyname_ex(gethostname())[2][0]
elif platform == "win32":
    # Windows
    IP = gethostbyname_ex(gethostname())[2][0]
else:
    IP = '127.0.0.1'  # fallback to loopback address if the platform is unknown
print('IP:',IP)'''

# Create and bind the socket
socket = socket(AF_INET, SOCK_DGRAM)
socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
socket.bind((IP, PORT))
print('Socket bound to port ' + Fore.GREEN + str(PORT))

# Initialize the content dictionary and online user list
contentDictionary = json.loads('{}')
onlineUsers = []

while True:
    try:
        # Receive incoming messages
        msg, addr = socket.recvfrom(BUFFER_SIZE)
        user_data_str = msg.decode('utf-8')
        user_data = json.loads(user_data_str)

        if user_data['username'] not in dict(onlineUsers):
            # Add the new user to the online user list
            onlineUsers.append((user_data['username'], addr[0]))

        isDictModified = False
    
        for file_chunk in user_data['files']:
            if file_chunk in contentDictionary:
                if addr[0] not in contentDictionary[file_chunk]:
                    # Add the user's address to the content dictionary for the file chunk
                    contentDictionary[file_chunk].append(addr[0])
                    print(Fore.YELLOW + '[Added] ' + str(addr[0]) + 'to ' + str(file_chunk))
                    isDictModified = True
            else:
                # Add the file chunk and user's address to the content dictionary
                contentDictionary[file_chunk] = [addr[0]]
                print(Fore.YELLOW + '[Added] ', file_chunk, 'to the dictionary.')
                # print(Back.CYAN + '=' * 70)
                isDictModified = True
        
		
        if isDictModified:
            # Create the directory for json_files
            if not os.path.exists('json_files'):
                os.makedirs('json_files')
            # Update the content dictionary in the JSON file
            with open('json_files/contentDictionary.json', 'w') as contentFile:
                json.dump(contentDictionary, contentFile)

    except KeyboardInterrupt:
        i = input('\n')
        if i == 'q':
            sys.exit()
            
        elif i == 'online_users':
            print(onlineUsers)