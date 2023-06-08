# Import Libraries
import os
import json
import time
from socket import *
from datetime import datetime

#Color
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

# Define Constant Variables
IP = '192.168.1.165'  # provide your own local address here! (you can use ifconfig command in your terminal)
PORT = 5000

# Get the username from the user
username = input('Please enter a username: ')
username = Fore.RED + f'{username}' + Fore.RESET + Fore.YELLOW
# Get the list of sliced files
sliced_files = os.listdir('sliced_files')

# Create a dictionary containing the username and files
user_dictionary = {
    'username': username,
    'files': sliced_files}

# Convert the dictionary to JSON
user_json = json.dumps(user_dictionary)

# Write the JSON to the announceFile
with open('json_files/announceFile.json', 'w') as announceFile:
    announceFile.write(user_json)

print('announce file created' + Fore.GREEN + ' successfully.')

# Create and configure the socket
socket = socket(AF_INET, SOCK_DGRAM)
socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

lastSentTime = 0
announcePeriod = 5

while True:
    if (time.time() - lastSentTime) > announcePeriod:
        # Send the JSON data as bytes over the socket
        socket.sendto(bytes(user_json.encode('utf-8')), (IP, PORT))

        lastSentTime = time.time()
        now = datetime.now()
        dt_string = now.strftime('%H:%M:%S')
        dt_string = Fore.RED + f'{dt_string}' + Fore.RESET + Fore.YELLOW

        print(Fore.YELLOW + f'\nAnnouncement sent by {username} at {dt_string}: \nFiles announced - {sliced_files}\n')
        print(Back.CYAN + '=' * 70)

    # Sleep for 5 seconds before sending the next announcement
    time.sleep(5)