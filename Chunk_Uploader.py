import os
import sys
import json
import math
import socket
from datetime import datetime

#Color
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

# Define Constant Variables
SERVER_PORT = 5000
BUFFER_SIZE = 4096

def sliceFile(content_name:str) -> None:
    # Create the directory for sliced_files
    if not os.path.exists('sliced_files'):
        os.makedirs('sliced_files')

    # Function to slice the file into chunks
    fileURL = 'shared_files/' + content_name
    c = os.path.getsize(fileURL)
    CHUNK_SIZE = math.ceil(math.ceil(c) / 5)
    
    index = 1
    with open(fileURL, 'rb') as infile:
        chunk = infile.read(int(CHUNK_SIZE))
        while chunk:
            chunkname = content_name + '_' + str(index) + '_' + 'temp'
            chunk_addr = 'sliced_files/' + chunkname
            with open(chunk_addr, 'wb+') as chunk_file:
                chunk_file.write(chunk)
            index += 1
            chunk = infile.read(int(CHUNK_SIZE))
    chunk_file.close()

# Get the server IP address
temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
temp_sock.connect(('8.8.8.8', 80))
SERVER_IP = temp_sock.getsockname()[0]
temp_sock.close()

# Create and configure the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((SERVER_IP, SERVER_PORT))
sock.listen(9)
print('Server is listening on' + Fore.GREEN + f' {SERVER_IP}:{SERVER_PORT}!')

# Get the list of shared files
shared_files = os.listdir('shared_files')

# Modify the file names in the list
for i in range(len(shared_files)):
    print(Fore.YELLOW + str(i) + ': ' + Fore.RESET + shared_files[i])

# Select a file to host
selection = input('Select a file number to host: ')
selectedFileName = shared_files[int(selection)]
print('Selected ' + Fore.BLUE + selectedFileName)

# Delete existing files under 'sliced_files' folder
folder_name = 'sliced_files'


def delete_files_in_folder(folder_path:str) -> None:
    file_count = 0  # Counter for deleted files

    for root, directories, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            os.remove(file_path)
            file_count += 1
    print('Total files deleted: ' + Fore.RED + str(file_count))
        
delete_files_in_folder(folder_path=folder_name)

# Slice the selected file into chunks
sliceFile(selectedFileName)

print(Fore.GREEN + '<SERVER>: TCP Server Started')

while True:
    try:
        # Accept incoming connections
        conn, addr = sock.accept()
        print(Fore.GREEN + 'Connected to client with address: ' + Fore.RESET + str(addr))

        # Receive the requested chunk name
        reqJSON = conn.recv(BUFFER_SIZE)
        print(Fore.YELLOW + str(reqJSON) + ' was requested')
        reqJSON = json.loads(reqJSON)
        requestedChunkName = reqJSON['filename']

        # Read and send the requested chunk to the client
        with open('sliced_files/' + requestedChunkName, 'rb') as outFile:
            totalsent = 0
            msg = outFile.read()
            # print(len(msg))

            while totalsent < len(msg):
                sent = conn.send(msg[totalsent:])
                totalsent += sent
                print(Fore.CYAN + 'Sent ' + str(sent))
                # print(Back.CYAN + '=' * 70)

            # Log the successful upload

            # Create the directory for logs
            if not os.path.exists('logs'):
                os.makedirs('logs')

            with open('logs/upload_log.txt', 'a+') as up_log:
                now = datetime.now()
                dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
                up_log.write(dt_string + ' ' + requestedChunkName + ' to ' + str(addr[0]) + '\n')

        conn.close()

    except KeyboardInterrupt:
        print(Fore.RED + '<SERVER>: TCP Server Closed')
        conn.close()
        sock.close()
        sys.exit()

    except Exception as e:
        print(e.args)
        print(Fore.RED + '<SERVER>: TCP Server Closed')
        sock.close()
        sys.exit()