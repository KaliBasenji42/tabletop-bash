# Tabletop Bash - Host
# Copyright (C) 2026 KaliBasenji42

# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; version 2 of the License.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# License: ./LICENSE.md
# GPL v2: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
# KaliBasenji42's Github: https://github.com/KaliBasenji42

### Imports ###

import random
import socket
import threading
import queue
import json
import logging

logging.basicConfig(
  level=logging.DEBUG,
  format='%(asctime)s | %(levelname)s: %(message)s',
  filename='host.log'
)
logging.debug('New Run: ')

### Variables ###

# Files

configPath = 'config.json' # Path to config file

# Server Config

host = '127.0.0.1' # Host IP
port = 65432 # Host Port

enableWhitelist = False # Wether to use whitelist or blacklist
whitelist = [] # Whitelist
blacklist = [] # Blacklist
managers = [] # Whitelist of managers

# Server

clients = [] # Array of client connections
clientsLock = threading.Lock() # Thread lock for clients 
# Lock ensures threads play nice with global value

serverQueue = queue.Queue() # Queue to process all client messages

usernames = {} # Dictionary of usernames

# Control

run = threading.Event() # Thread event, wether to run Main Loop
run.set()

# Data (sent stuff)

chatLog = [] # Array of tuples of strings (user, message, type), containing the chat log
# Note: Sent as string, split on '\\;' at receive
tableState = [] # Array of objects on the table (sent from server, updated in thread)

chatLength = 20 # Max chat log length

### Functions ###

# Basic

def strToPosInt(string): # Converts string to positive integer, returns 0 if no number, ignores non-numeric characters
  
  numStr = ''
  
  for i in range(len(string)):
    if string[i].isnumeric(): numStr = numStr + string[i]
  
  if len(numStr) == 0: return 0
  
  else: return int(numStr)
  

def strToFloat(string): # Converts string to float, returns 0 if no number, ignores non-numeric characters
  
  numStr = ''
  
  for i in range(len(string)):
    
    if string[i].isnumeric(): numStr = numStr + string[i]
    if string[i] == '.': numStr = numStr + string[i]
    
  
  if len(numStr) == 0: return 0
  
  if string[0] == '-': return -1 * float(numStr)
  else: return float(numStr)
  

def hasNumerics(string): # Returns wether a string has numeric characters
  
  for char in string:
    if char.isnumeric(): return True
  
  return False
  

def roll(arr, new): # Have an array roll in a new value, removing the first
  
  out = arr
  
  out.append(new) # Add new
  out.pop(0) # Remove first
  
  return out
  

# File

def readConfig(): # Read config file
  
  # Variables
  
  global host
  global port
  
  global enableWhitelist
  global whitelist
  global blacklist
  global managers
  
  # Read Files
  
  with open(configPath, 'r') as file: data = json.loads(file.read())
  
  # Set variables
  
  host = data['IP']
  port = data['port']
  
  enableWhitelist = data['enableWhitelist']
  whitelist = data['whitelist']
  blacklist = data['blacklist']
  managers = data['managers']
  

# Network

def addClient(client): # Add client to clients array
  # Client is form (conn, addr)
  
  with clientsLock:
    
    clients.append(client) # Add
    
  

def removeClient(client): # Remove client from clients array
  # Client is form (conn, addr)
  
  with clientsLock:
    
    if client in clients: # If it exists
      
      clients.remove(client) # Remove
      
    
  

def broadcast(message): # Send message to all connections
  
  with clientsLock:
    
    for conn in clients.copy(): # For each client (copy to avoid disconnect error)
      
      try:
        
        conn[0].sendall((message + '\n').encode()) # Send
        
        logging.info('Broadcast: ' + message) # Logging
        
      except Exception as e:
        
        logging.exception('Failed to send message to ' + str(conn)) # Logging
        
      
    
  

def sendAddr(message, addr): # Send message to specific address
  
  with clientsLock:
    
    for conn in clients.copy(): # For each client (copy to avoid disconnect error)
      
      try:
        
        if conn[1] == addr: # If address matches
          
          conn[0].sendall((message + '\n').encode()) # Send
          
          logging.info('Send Addr to: ' + addr + ': ' + message) # Logging
          
        
      except Exception as e:
        
        logging.exception('Failed to send message to ' + str(conn)) # Logging
        
      
    
  

def generateChatLog(chatLog): # Generate string to send for chat log
  
  global usernames
  
  out = [] # Output array
  
  for log in chatLog: # Each log
    
    outLog = ( # Output log
      usernames.get(log[0], log[0]), # Get username
      log[1], # Message
      log[2], # Type
    )
    
    out.append(outLog) # Add
    
  
  outStr = json.dumps(out) # Output string
  
  return outStr # Return
  

### (Other) Threads ###

# Server Queue Function

def serverQueueThreadFunction(): # Processes server queue messages
  
  # Pre-Loop
  
  global managers
  
  global run
  global chatLog
  
  # Main Loop
  
  while run.is_set():
    
    try:
      
      # Get message
      
      addr, message = serverQueue.get(timeout = 1)
      
      # Disconnect
      
      if message == 'disconnect':
        
        chatLog.append((addr, 'Left', 'conn')) # Chat log
        while len(chatLog) > chatLength: # While too long
          chatLog.pop(0) # Remove oldest
        
        broadcast('chat:' + generateChatLog(chatLog))
        
      
      # Manager
      
      if message == 'kill': # Kill
        
        if addr.split(':')[0] in managers: # If sent from manager
          
          run.clear() # Kill
          
          print('Kill signal from manager ' + addr) # Print
          
          logging.info('Kill signal from manager ' + addr) # Logging
          
        
      
      # Join
      
      if len(message) >= 5:
        if message[:5] == 'join:': # If join
          
          usernames[addr] = message[5:] # Add username
          
          print(addr + ' is "' + message[5:] + '"') # Print
          
          logging.info(addr + ' is "' + message[5:] + '"') # Logging
          logging.debug('Usernames:\n' + str(usernames))
          
          chatLog.append((addr, 'Joined', 'conn')) # Chat log
          while len(chatLog) > chatLength: # While too long
            chatLog.pop(0) # Remove oldest
          
          
          broadcast('chat:' + generateChatLog(chatLog))
          
      
      # Change Username
      
      if len(message) >= 3:
        if message[:3] == 'un:': # If UN change
          
          usernames[addr] = message[3:] # Set username
          
          print(addr + ' is "' + message[3:] + '"') # Print
          
          logging.info(addr + ' is "' + message[3:] + '"') # Logging
          logging.debug('Usernames:\n' + str(usernames))
          
          chatLog.append((addr, 'Changed UN', 'conn')) # Chat log
          while len(chatLog) > chatLength: # While too long
            chatLog.pop(0) # Remove oldest
          
          
          broadcast('chat:' + generateChatLog(chatLog))
          
      
      # Chat Message
      
      if len(message) >= 4:
        if message[:4] == 'msg:': # If chat message
          
          chatLog.append((addr, message[4:], 'msg')) # Chat log
          while len(chatLog) > chatLength: # While too long
            chatLog.pop(0) # Remove oldest
          
          broadcast('chat:' + generateChatLog(chatLog))
          
        
      
      # Buzzer
      
      if len(message) >= 5:
        if message[:5] == 'buzz:': # If buzzer
          
          chatLog.append((addr, message[5:], 'buzz')) # Chat log
          while len(chatLog) > chatLength: # While too long
            chatLog.pop(0) # Remove oldest
          
          broadcast('chat:' + generateChatLog(chatLog))
          
      
    except queue.Empty:
      continue # Continue if empty
    
  

# Server Queue Thread

serverQueueThread = threading.Thread(target = serverQueueThreadFunction, daemon = True) # Declare
serverQueueThread.start() # Start

### Pre-Loop ###

# Title

title = """
███▀███▀███▀▛▀▀▀███ ═⍐═ ╔⍐╗ ╔═╗   ┬─╮ ╭─╮ ╭─╴ ╷ ╷
 █  ▙▄▟ ▙▄▟ ▌   ▙▄▄  ║  ⍐ ⍐ ⍐═╝   ├─┤ ├─┤ ╰─╮ ├─┤
 █  ▌ ▐ ▙▄▟ ▙▄▄ ▙▄▄  ║  ╚⍐╝ ║     ┴─╯ ╵ ╵ ╶─╯ ╵ ╵

<===### Host ###===>

Copyright (C) 2026 KaliBasenji42
Tabletop Bash comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain conditions.

License: ./LICENSE.md
GPL v2: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
KaliBasenji42's Github: https://github.com/KaliBasenji42
"""

print(title)

# Read Files

try:
  
  readConfig()
  
except Exception as e:
  
  logging.exception('File Read Error') # Logging
  print('\033[97;41mFile Read Error\033[0m\n' + str(e))
  
  quit() # Exit
  

# Socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Declare socket

try:
  
  sock.bind((host, port)) # Try bond
  sock.listen(5) # Listen for incoming connections
  sock.settimeout(1) # Timeout
  
  logging.info('Server Started') # Logging
  print('Server Started!\n')
  
except Exception as e:
  
  logging.exception('Socket Bind Error') # Logging
  print('\033[97;41mSocket Bind Error\033[0m\n' + str(e))
  
  quit() # Exit
  

### Main Loop ###

# Thread Function

def clientThreadFunction(conn, addr):
  
  # Pre-Loop
  
  addrStr = addr[0] + ':' + str(addr[1]) # Address as string
  
  addClient((conn, addrStr)) # Add to clients array
  
  logging.info('Connected to: ' + addrStr) # Logging
  print('Connected to: ' + addrStr)
  
  conn.sendall('Welcome!\n'.encode()) # Test welcome message
  
  clientBuffer = '' # Buffer to ensure message whole-ness
  
  # Main Loop
  
  while run.is_set():
    
    try:
      
      # Get data
      
      data = conn.recv(2048)
      
      # Disconnect
      
      if not data:
        
        logging.info('Disconnected from: ' + addrStr + ' No data/clean') # Logging
        print('Disconnected from: ' + addrStr + ' No data/clean')
        
        break # Break
        
      
      # Set Queue
      
      clientBuffer += data.decode()
      
      while "\n" in clientBuffer: # While data not a complete message
        
        message, clientBuffer = clientBuffer.split('\n', 1) # Split on message end
        
        serverQueue.put((addrStr, message)) # Push to queue
        
        logging.debug('Message from ' + addrStr + ': ' + message) # Logging
        
      
      # Process
      
      
    except Exception as e:
      
      logging.info('Disconnected from: ' + addrStr + '\n' + str(e)) # Logging
      print('Disconnected from: ' + addrStr + '\n' + str(e))
      
      break # Exit loop
      
    
  
  removeClient((conn, addrStr)) # Remove from clients array
  
  serverQueue.put((addrStr, 'disconnect')) # Tell server queue
  
  conn.close() # Close
  

# Try

try:
  
  while run.is_set():
    
    try: # Try
      
      conn, addr = sock.accept() # Accept incoming
      
      thread = threading.Thread(target = clientThreadFunction, args = (conn, addr), daemon = True)
      thread.start() # Thread per client
      
    except socket.timeout: pass # Ignore if timeout
    
  
except KeyboardInterrupt: # Shutdown
  
  logging.info('Keyboard Interrupt') # Logging
  print('\033[92m\nShutting Down - Keyboard Interrupt\033[0m')
  
  run.clear() # Stop threads
  

### Post-Loop ###

serverQueueThread.join(10) # Join

sock.close() # Close socket

logging.info('Server Shutdown') # Logging
print('Good Bye!')
