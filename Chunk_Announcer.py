# Import Libraries
import os
import json
import time
from socket import *
from sys import platform
import sys
from datetime import datetime

#Color
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

# Define Constant Variables
IP = '192.168.1.165'  # provide your own local address here! (you can use ifconfig command in your terminal)
PORT = 5000

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
    IP = '127.0.0.1'  # fallback to loopback address if the platform is unknown'''
print('IP:',IP)

# Get the username from the user
username = input('Please enter a username: ')
username = Fore.RED + f'{username}' + Fore.RESET + Fore.YELLOW + Fore.RESET
# Get the list of sliced files
sliced_files = os.listdir('sliced_files')

# Create a dictionary containing the username and files
user_dictionary = {
    'username': username,
    'files': sliced_files}

# Convert the dictionary to JSON
user_json = json.dumps(user_dictionary)

# Create the directory for json_files
if not os.path.exists('json_files'):
    os.makedirs('json_files')

# Write the JSON to the announceFile
with open('json_files/announceFile.json', 'w') as announceFile:
    announceFile.write(user_json)

print('announce file created' + Fore.GREEN + ' successfully.')

# Create and configure the socket
socket = socket(AF_INET, SOCK_DGRAM)
socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

lastSentTime = 0
announcePeriod = 5

# Clear the console before starting
os.system('cls' if os.name == 'nt' else 'clear')

while True:
    # Check if it's time to send an announcement
    if (time.time() - lastSentTime) > announcePeriod:
        # Send the JSON data as bytes over the socket
        socket.sendto(bytes(user_json.encode('utf-8')), (IP, PORT))

        lastSentTime = time.time()
        now = datetime.now()
        dt_string = now.strftime('%H:%M:%S')
        dt_string = Fore.RED + f'{dt_string}' + Fore.RESET

        # Clear the console before printing the new announcement
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f'\nAnnouncement sent by {username} at {dt_string}: ')
        print(Fore.YELLOW + f'Files announced - {sliced_files}\n')
        # print(Back.CYAN + '=' * 70)

        # Flush the output to ensure immediate display
        sys.stdout.flush()

    # Sleep for 1 second before checking for changes
    time.sleep(1)