# Tabletop Bash
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
import logging

logging.basicConfig(
  level=logging.DEBUG,
  format='%(asctime)s | %(levelname)s: %(message)s',
  filename='app.log'
)
logging.debug('New Run: ')

### Variables ###

# Server

host = '127.0.0.1' # Host IP
port = 65432 # Host Port

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
  

# Network

def addClient(conn): # Add client to clients array
  
  with clientsLock:
    
    clients.append(conn) # Add
    
  

def removeClient(conn): # Remove client from clients array
  
  with clientsLock:
    
    if conn in clients: # If it exists
      
      clients.remove(conn) # Remove
      
    
  

def broadcast(message): # Send message to all connections
  
  with clientsLock:
    
    for conn in clients.copy(): # For each client (copy to avoid disconnect error)
      
      try:
        
        conn.sendall((message + '\n').encode()) # Send
        
      except Exception as e:
        
        logging.exception('Failed to send message to ' + str(conn)) # Logging
        
      
    
  

def generateChatLog(chatLog): # Generate string to send for chat log
  
  global usernames
  
  out = '' # Output string
  
  while len(chatLog) > chatLength: # While too long
    chatLog.pop(0) # Remove oldest
  
  for log in chatLog: # Each log
    
    if log[2] == 'conn': # Type Connection
      out += usernames.get(log[0], log[0]) + ' ' # Add username
      out += log[1] + '\\;' # Add message
    
    elif log[2] == 'msg': # Type Message
      out += usernames.get(log[0], log[0]) + ':\\;> ' # Add username
      out += log[1] + '\\;' # Add message
    
  
  logging.debug('Chat log:\n' + str(chatLog))
  
  return out # Return
  

### (Other) Threads ###

# Server Queue Function

def serverQueueThreadFunction(): # Processes server queue messages
  
  # Pre-Loop
  
  global chatLog
  
  # Main Loop
  
  while run.is_set():
    
    try:
      
      # Get message
      
      addr, message = serverQueue.get(timeout = 1)
      
      # Disconnect
      
      if message == 'disconnect':
        
        chatLog.append((addr, 'Left', 'conn')) # Chat log
        broadcast('chat:' + generateChatLog(chatLog))
        
      
      # Join
      
      if len(message) >= 5:
        if message[:5] == 'join:': # If join
          
          usernames[addr] = message[5:] # Add username
          
          logging.debug('Usernames:\n' + str(usernames)) # Logging
          
          chatLog.append((addr, 'Joined', 'conn')) # Chat log
          broadcast('chat:' + generateChatLog(chatLog))
          
      
      # Chat Message
      
      if len(message) >= 4:
        if message[:4] == 'msg:': # If chat message
          
          chatLog.append((addr, message[4:], 'msg')) # Chat log
          broadcast('chat:' + generateChatLog(chatLog))
          
        
      
    except queue.Empty:
      continue # Continue if empty
    
  

# Server Queue Thread

serverQueueThread = threading.Thread(target = serverQueueThreadFunction, daemon = True) # Declare
serverQueueThread.start() # Start

### Pre-Loop ###

# Input

host = input('Host IP: ')
port = strToPosInt(input('Port: '))

# Socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Declare socket

try:
  
  sock.bind((host, port)) # Try bond
  sock.listen(5) # Listen for incoming connections
  
  logging.info('Server Started') # Logging
  print('Server Started!')
  
except Exception as e:
  
  logging.exception('Socket Bind Error') # Logging
  print('\033[97;41mSocket Bind Error\033[0m\n' + str(e))
  

### Main Loop ###

# Thread Function

def clientThreadFunction(conn, addr):
  
  # Pre-Loop
  
  addClient(conn) # Add to clients array
  
  print('Connected to: ' + str(addr)) # Logging
  logging.info('Connected to: ' + str(addr))
  
  conn.sendall('Welcome!\n'.encode()) # Test welcome message
  
  clientBuffer = '' # Buffer to ensure message whole-ness
  
  addrStr = addr[0] + ':' + str(addr[1]) # Address as string
  
  # Main Loop
  
  while run.is_set():
    
    try:
      
      # Get data
      
      data = conn.recv(2048)
      
      # Disconnect
      
      if not data:
        
        print('Disconnected from: ' + str(addr) + ' No data/clean') # Logging
        logging.info('Disconnected from: ' + str(addr) + ' No data/clean')
        
        break # Break
        
      
      # Set Queue
      
      clientBuffer += data.decode()
      
      while "\n" in clientBuffer: # While data not a complete message
        
        message, clientBuffer = clientBuffer.split('\n', 1) # Split on message end
        
        serverQueue.put((addrStr, message)) # Push to queue
        
        logging.debug('Message from ' + str(addr) + ': ' + message) # Logging
        
      
      # Process
      
      
    except Exception as e:
      
      print('Disconnected from: ' + str(addr) + '\n' + str(e)) # Logging
      logging.info('Disconnected from: ' + str(addr) + '\n' + str(e))
      
      break # Exit loop
      
    
  
  removeClient(conn) # Remove from clients array
  
  serverQueue.put((addrStr, 'disconnect')) # Tell server queue
  
  conn.close() # Close
  

# Try

try:
  
  while run.is_set():
    
    conn, addr = sock.accept() # Accept incoming
    
    thread = threading.Thread(target = clientThreadFunction, args = (conn, addr), daemon = True)
    thread.start() # Thread per client
    
  
except KeyboardInterrupt: # Shutdown
  
  logging.info('Keyboard Interrupt') # Logging
  print('\033[92mShutting Down\033[0m')
  
  run.clear() # Stop threads
  

### Post-Loop ###

sock.close() # Close socket

