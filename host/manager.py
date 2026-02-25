# Tabletop Bash - Host Manager
# Copyright (C) 2026 KaliBasenji42

# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; version 2 of the License.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# License: ./LICENSE.md
# GPL v2: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
# KaliBasenji42's Github: https://github.com/KaliBasenji42

### Imports ###

import time
import socket
import threading
import queue
import logging

logging.basicConfig(
  level=logging.DEBUG,
  format='%(asctime)s | %(levelname)s: %(message)s',
  filename='manager.log'
)
logging.debug('New Run: ')

### Variables ###

# Server

host = '127.0.0.1' # Host IP
port = 65432 # Host Port

clientName = '' # Manager name

# Control

run = True # Run Main Loop

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
  

### Classes ###

# Network

class server:
  
  def __init__(self, host, port, clientName):
    
    # Variables
    
    self.run = True # Loop control
    self.disconnect = False # Wether its connected
    
    self.name = 'MANAGER ' + clientName # Manager name
    
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket client
    self.host = host # Host IP
    self.port = port # Port
    self.addr = (self.host, self.port) # Full address
    
    # Connect
    
    self.sock.connect(self.addr)
    self.sock.settimeout(1) # Block for 1 second
    
    # Initial Message
    
    self.send(('join:' + self.name))
    
    # Thread
    
    self.queue = queue.Queue() # Queue to ensure all messages received
    self.buffer = '' # Buffer to ensure message whole-ness
    
    self.thread = threading.Thread(target = self.recv, daemon = True)
    self.thread.start()
    
  
  def send(self, message): # Send to server
    
    logging.info('Sending: ' + message) # Logging
    
    try:
      
      self.sock.sendall((message + '\n').encode())
      
    except Exception:
      
      self.disconnect = True # Disconnect
      self.run = False
      
      logging.exception("Send Error")
      
    
  
  def recv(self): # Receive from server
    
    while self.run:
      
      try:
        
        # Get data
        
        data = self.sock.recv(2048)
        
        # Disconnect
        
        if not data:
          
          self.disconnect = True
          
          logging.info('Disconnected from server: No data/clean') # Logging
          
          break # Break
          
        
        # Set Queue
        
        self.buffer += data.decode()
        
        while "\n" in self.buffer: # While data not a complete message
          
          message, self.buffer = self.buffer.split('\n', 1) # Split on message end
          
          self.queue.put(message) # Push to queue
          
          logging.debug('Message from server: ' + message) # Logging
          logging.debug('Queue Size: ' + str(self.queue.qsize())) # Logging
          
        
      except socket.timeout:
        
        pass # Ignore if timed out
        
      except Exception as e:
        
        self.disconnect = True
        
        logging.info('Disconnected from server\n' + str(e)) # Logging
        
        break # Break if shutdown
        
      
    
  
  def close(self): # Close connection
    
    self.run = False # Stop recv loop
    
    self.sock.close() # Close
    
    if self.thread.is_alive(): # If alive
      self.thread.join() # End thread
    
    logging.debug('Closed server') # Logging
    
  

### Pre-Loop ###

# Title

title = """
███▀███▀███▀▛▀▀▀███ ═⍐═ ╔⍐╗ ╔═╗   ┬─╮ ╭─╮ ╭─╴ ╷ ╷
 █  ▙▄▟ ▙▄▟ ▌   ▙▄▄  ║  ⍐ ⍐ ⍐═╝   ├─┤ ├─┤ ╰─╮ ├─┤
 █  ▌ ▐ ▙▄▟ ▙▄▄ ▙▄▄  ║  ╚⍐╝ ║     ┴─╯ ╵ ╵ ╶─╯ ╵ ╵

<===### Host Manager ###===>

Copyright (C) 2026 KaliBasenji42
Tabletop Bash comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain conditions.

License: ./LICENSE.md
GPL v2: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
KaliBasenji42's Github: https://github.com/KaliBasenji42

Note: This only sends messages to the host to change its behavior (ignores responses)

Refer to README.md's Network section for details
"""

print(title)

# Server

host = input('Connect to Host:\n\nHost IP: ') # Inputs
port = strToPosInt(input('Port: '))
clientName = input('Username: ')
print()

try:
  
  clientServer = server(host, port, clientName) # Try making server
  
except Exception as e:
  
  logging.exception('Connection Error') # Logging
  
  print('\033[97;41mConnection Error\033[0m\n' + str(e)) # Error message
  
  quit() # Quit
  

### Main Loop ###

def main(): 
  
  global run
  
  # Main Loop
  
  while run:
    
    # Server disconnect
    
    if clientServer.disconnect:
      
      run = False # Stop running
      
      logging.debug('Server Disconnected') # Logging
      
      break # Stop loop
      
    
    ### Input ###
    
    inp = input('Input: ')
    
    # Quit
    
    if inp.lower() == 'quit': run = False
    
    # Send
    
    else: clientServer.send(inp)  
    
  

# Try

try:
  main()
except Exception as e:
  
  logging.exception('Fatal Error') # Log
  
  # Error message
  print('\033[97;41mFatal Error\033[0m')
  

### Post-Loop ###

if clientServer.disconnect: # Killed due to disconnect?
  print('\033[97;41mDisconnected From Server\033[0m') # Print

clientServer.close() # Close server

print('Good Bye!')
