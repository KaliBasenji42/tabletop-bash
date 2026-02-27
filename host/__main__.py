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
  format='%(asctime)s | %(filename)s:%(lineno)s | %(levelname)s: %(message)s',
  filename='app.log'
)
logging.debug('New Run')

### Variables ###

# Files

configPath = 'config.json' # Path to config file
itemsPath = 'items.json' # Path to item definition file

# Server Config

host = '127.0.0.1' # Host IP
port = 65432 # Host Port

enableWhitelist = False # Wether to use whitelist or blacklist
whitelist = [] # Whitelist
blacklist = [] # Blacklist
managers = [] # Whitelist of managers

# Server

clients = [] # Array of client connections
clientsLock = threading.RLock() # Thread lock for clients 
# Lock ensures threads play nice with global value

serverQueue = queue.Queue() # Queue to process all client messages

usernames = {} # Dictionary of usernames

# Control

run = threading.Event() # Thread event, wether to run Main Loop
run.set()

# Data

chatLog = [] # Array of tuples of strings (user, message, type), containing the chat log
chatLength = 20 # Max chat log length

tableState = [] # 3D Array of objects on the table

items = {} # Dictionary of default items
defaultRender = {} # Dictionary of default rendering

### Functions ###

# Basic

def strToPosInt(string): # Converts string to positive integer, returns 0 if no number, ignores non-numeric characters
  
  numStr = ''
  
  for i in range(len(string)):
    if string[i].isnumeric(): numStr = numStr + string[i]
  
  if len(numStr) == 0: return 0
  
  else: return int(numStr)
  

def hasNumerics(string): # Returns wether a string has numeric characters
  
  for char in string:
    if char.isnumeric(): return True
  
  return False
  

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
  
  # Logging
  
  logging.debug('Whitelist Enabled: ' + str(enableWhitelist))
  logging.debug('Whitelist: ' + str(whitelist))
  logging.debug('Blacklist: ' + str(blacklist))
  logging.debug('Managers: ' + str(managers))
  

def readItems(): # Read item file
  
  # Variables
  
  global items
  global defaultRender
  
  # Read Files
  
  with open(itemsPath, 'r') as file: data = json.loads(file.read())
  
  # Set variables
  
  for itemKey in data['items']: # Each item
    
    item = data['items'][itemKey] # Get item
    
    # Default Render
    
    if 'char' in item and 'color' in item: # If it has a default char and color
    
      defaultRender[itemKey] = { # Set default render value
        'char': item['char'],
        'color': item['color']
      }
      
    
    # Items
    
    stacks = False # Wether the item can stack
    flips = False # Wether the item can flip
    roll = [] # Items the item can randomly transform to
    
    if 'stacks' in item: # If it has 'stacks'...
      stacks = item['stacks'] # ..set
    
    if 'flip' in item: # If it has 'flip'...
      flips = True # ..true
    
    if 'roll' in item: # If it has 'roll'...
      roll = item['roll'] # ..set
    
    items[itemKey] = { # Add item
      'stacks': stacks,
      'flips': flips,
      'roll': roll
    }
    
  
  for itemKey in data['render']: # Each render item
    
    item = data['render'][itemKey] # Get item
    
    # Default Render
    
    if item['char'] and item['color']: # If it has a default char and color
    
      defaultRender[itemKey] = { # Set default render value
        'char': item['char'],
        'color': item['color']
      }
      
    
  # Logging
  
  #logging.debug('Items: ' + str(items))
  #logging.debug('Default Render: ' + str(defaultRender))
  

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
    
    for client in clients.copy(): # For each client (copy to avoid disconnect error)
      
      try:
        
        client[0].sendall((message + '\n').encode()) # Send
        
        logging.info('Broadcast: ' + message) # Logging
        
      except Exception as e:
        
        logging.exception('Failed to send message to ' + str(client)) # Logging
        
      
    
  

def sendAddr(message, addr): # Send message to specific address
  
  with clientsLock:
    
    for client in clients.copy(): # For each client (copy to avoid disconnect error)
      
      try:
        
        if client[1] == addr: # If address matches
          
          client[0].sendall((message + '\n').encode()) # Send
          
          logging.info('Send Addr to: ' + addr + ': ' + message) # Logging
          
        
      except Exception as e:
        
        logging.exception('Failed to send message to ' + str(client)) # Logging
        
      
    
  

def kickAddr(addr): # Disconnect specific address
  
  with clientsLock:
    
    for client in clients.copy(): # For each client (copy to avoid disconnect error)
      
      try:
        
        if client[1] == addr: # If address matches
          
          try: client[0].shutdown(socket.SHUT_RDWR) # Shutdown
          except: pass
          
          removeClient(client) # Remove
          
          client[0].close() # Close
          
          logging.info('Kicked: ' + addr) # Logging
          
        
      except Exception as e:
        
        logging.exception('Failed to kick ' + str(client)) # Logging
        
      
    
  

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
      
      # Manager
      
      if addr.split(':')[0] in managers: # If sent from manager
        
        if message == 'kill': # Kill
          
          run.clear() # Kill
          
          print('Kill signal from manager ' + addr) # Print
          
          logging.info('Kill signal from manager ' + addr) # Logging
          
        
        elif message.startswith('kick:'): # Kick
          
          logging.debug('Kicking: ' + message[5:]) # Logging
          
          kickAddr(message[5:]) # Kick
          
        
      
      # Disconnect
      
      if message == 'disconnect':
        
        chatLog.append((addr, 'Left', 'conn')) # Chat log
        while len(chatLog) > chatLength: # While too long
          chatLog.pop(0) # Remove oldest
        
        broadcast('chat:' + generateChatLog(chatLog))
        
      
      # Join
      
      elif message.startswith('join:'): # If join
        
        usernames[addr] = message[5:] # Add username
        
        print(addr + ' is "' + message[5:] + '"') # Print
        
        logging.info(addr + ' is "' + message[5:] + '"') # Logging
        logging.debug('Usernames:\n' + str(usernames))
        
        chatLog.append((addr, 'Joined', 'conn')) # Chat log
        while len(chatLog) > chatLength: # While too long
          chatLog.pop(0) # Remove oldest
        
        
        broadcast('chat:' + generateChatLog(chatLog))
        
      
      # Change Username
      
      elif message.startswith('un:'): # If UN change
        
        usernames[addr] = message[3:] # Set username
        
        print(addr + ' is "' + message[3:] + '"') # Print
        
        logging.info(addr + ' is "' + message[3:] + '"') # Logging
        logging.debug('Usernames:\n' + str(usernames))
        
        chatLog.append((addr, 'Changed UN', 'conn')) # Chat log
        while len(chatLog) > chatLength: # While too long
          chatLog.pop(0) # Remove oldest
        
        
        broadcast('chat:' + generateChatLog(chatLog))
        
      
      # Chat Message
      
      elif message.startswith('msg:'): # If chat message
        
        chatLog.append((addr, message[4:], 'msg')) # Chat log
        while len(chatLog) > chatLength: # While too long
          chatLog.pop(0) # Remove oldest
        
        broadcast('chat:' + generateChatLog(chatLog))
        
      
      # Buzzer
      
      elif message.startswith('buzz:'): # If buzzer
        
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
  readItems()
  
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
  
  # White/Black list
  
  if(enableWhitelist): # Do whitelist
    
    if(not addr[0] in whitelist): # Not in whitelist
      logging.info('"' + addr[0] + '" blocked (whitelist)') # Logging
      conn.close() # Close
      return # Exit
    
  
  else: # Do blacklist
    
    if(addr[0] in blacklist): # In blacklist
      logging.info('"' + addr[0] + '" blocked (blacklist)') # Logging
      conn.close() # Close
      return # Exit
    
  
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
