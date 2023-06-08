# Import Libraries
import os
import json
import socket
from datetime import datetime

#Color
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

# Define Constant Variables
PORT = 5000
BUFFER_SIZE = 4096  # 4KB of data

def delete_files_with_suffix(directory:str, suffix:str) -> None:
    # Get the list of files in the directory
    files = os.listdir(directory)

    # Iterate through the files
    for file in files:
        if file.endswith(suffix):
            file_path = os.path.join(directory, file)
            os.remove(file_path)
            # print(f"Deleted file: {file}")

def combineSlices(content_name: str) -> None:
    # Combine downloaded chunks into a single file
    chunknames = [content_name+'_1_temp', content_name+'_2_temp', content_name+'_3_temp', content_name+'_4_temp', content_name+'_5_temp']

    with open('downloaded_files/' + content_name, 'wb') as outfile:
        for chunk in chunknames:
            with open('sliced_files/' + chunk, 'rb') as infile:
                outfile.write(infile.read())
                
    delete_files_with_suffix('downloaded_files','temp')
    

# Open and load the content dictionary file
contentFile = open('json_files/contentDictionary.json', 'rt')
contentFile_data = json.load(contentFile)

while True:
    availableFiles = []
    # Iterate through contentDictionary to get available file names
    for fileChunk in contentFile_data:
        fileName = str(fileChunk)[:len(fileChunk)-7]  # get rid of the number part (_i)
        if fileName not in availableFiles:
            availableFiles.append(fileName)

    print('Enter the index of the file you want to download.')
    # Display available file options
    for index in range(len(availableFiles)):
        print(Fore.YELLOW + str(index) + ': '+ Fore.RESET + availableFiles[index])

    selectedFileIndex = int(input('>'))

    allChunksDownloaded = True
    # Iterate through chunks to download them
    for i in range(1, 6):
        chunkToDownload = availableFiles[selectedFileIndex] + '_' + str(i) + '_' + 'temp'
        requestJSON = json.dumps({'filename': chunkToDownload}).encode('utf8')

        chunkIsDownloaded = False
        # Iterate through IPs associated with the chunk for downloading
        for ip in contentFile_data[chunkToDownload]:
            print(Fore.YELLOW + f'Requesting {ip} for {chunkToDownload}')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            try:
                s.connect((ip, PORT))
                s.send(requestJSON)
                print(Fore.YELLOW + requestJSON.decode('utf-8') + ' was requested.')
                downloadedChunk = s.recv(BUFFER_SIZE)

                # Receive remaining data
                while True:
                    msg = s.recv(BUFFER_SIZE)
                    if not msg:
                        break
                    downloadedChunk += bytes(msg)

                chunkIsDownloaded = True

            except Exception as e:
                s.close()
                print('Could not download ' + chunkToDownload + ' from ' + ip)
                print('Error: ', e)
                print(Back.CYAN + '=' * 70)
                continue

        if chunkIsDownloaded:
            # Log the downloaded chunk and save it to disk
            with open('logs/download_log.txt', 'a') as up_log:
                now = datetime.now()
                dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
                up_log.write(dt_string + ' ' + chunkToDownload + ' from ' + str(ip) + '\n')

            with open('downloaded_files/' + chunkToDownload, 'wb') as downloadedFile:
                downloadedFile.write(downloadedChunk)

            s.close()
            print(Fore.GREEN + 'Chunk downloaded successfully!')
            print(Back.CYAN + '=' * 70)


        else:
            allChunksDownloaded = False
            print(Fore.RED + 'Chunks could not be downloaded!')
            print(Back.CYAN + '=' * 70)
            break

    if allChunksDownloaded:
        # All chunks downloaded, combine them into a single file
        print(Fore.GREEN + 'Download finished successfully!')
        combineSlices(availableFiles[selectedFileIndex])
        print(Back.CYAN + '=' * 70)
        break

    else:
        print(Fore.RED + 'Download Failed!')
        print(Back.CYAN + '=' * 70)