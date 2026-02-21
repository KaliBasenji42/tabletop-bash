# Tabletop Bash
# Copyright (C) 2026 KaliBasenji42

# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; version 2 of the License.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# License: ./LICENSE.md
# GPL v2: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
# KaliBasenji42's Github: https://github.com/KaliBasenji42

### Imports ###

import curses
import os
import time
import random
import socket
import threading
import queue
import selectors
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

clientName = '' # Player name

message = '' # Chat message to send
chatLog = [] # Array of strings, containing the chat log
# Note: Sent as string, split on '\n' at receive

# Control

spf = 1/30 # Second per Frames
tick = 0 # Time ticker
run = True # Run Main Loop
frameTime = time.time() # Time frame started for spf

selected = (0, 0) # Selected cell

termSize = (0, 0) # Terminal dimensions (Lines/Height, Columns/Width)
screenWidth = 0 # Screen width, defined after window objects
screenHeight = 0 # Screen height

termTooSmall = True # Wether the terminal is too small

# Game

tableGrid = [] # Array of strings representing the look of the table
tableState = [] # Array of objects on the table (sent from server, updated in thread)

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

def readFiles():
  
  pass
  

# Network

def processMessage(message): # Processes network messages and updates game state
  
  # Chat
  
  global chatLog
  
  if len(message) >= 5:
    if message[:5] == 'chat:': # If chat
      
      chatLog = message[5:].split('\\;') # Array of each row
      
      while len(chatLog) > chatWindow.height - 3: # While too long
        chatLog.pop(0) # Remove oldest
      
      logging.debug('Chat Log:\n' + str(chatLog)) # Logging
      
  

# output

def renderTable(): # Takes tableState and redraws tableGrid for rendering
  
  pass
  

def render(stdscr): # Render screen
  
  stdscr.clear() # Clear
  
  # Backgrounds
  
  for window in windows:
    window.renderBackground(stdscr)
  
  # Chat log
  
  global chatLog
  
  for i in range(len(chatLog)):
    
    stdscr.addstr(chatWindow.y + i + 1, chatWindow.x + 1, chatLog[i])
    
  
  stdscr.addstr( # Cursor
    chatWindow.y + chatWindow.height - 2,
    chatWindow.x + 1,
    '> '
  )
  
  # Debug
  
  heightStr = ( # String for logging height
    'Height: ' + str(screenHeight) +
    ' of ' + str(termSize[0])
  )
  
  widthStr = ( # String for logging width
    'Width: ' + str(screenWidth) +
    ' of ' + str(termSize[1])
  )
  
  tickStr = ( # String for logging tick
    'Tick: ' + str(tick)
  )
  
  stdscr.addstr(contextWindow.y + 1, contextWindow.x + 1, widthStr) # Out width
  stdscr.addstr(contextWindow.y + 2, contextWindow.x + 1, heightStr) # Out height
  stdscr.addstr(contextWindow.y + 3, contextWindow.x + 1, tickStr) # Out tick
  
  stdscr.refresh() # Refresh
  

### Classes ###

# Graphics

class window:
  
  def __init__(self, x, y, width, height, title):
    
    # Variables
    
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.title = title
    
  
  def generateBackground(self): # Generate background array, set to self
    
    background = [] # Background array (each line)
    row = '' # Temp row string
    
    row = '╭' + self.title # Title
    
    for i in range(self.width - len(self.title) - 2): # Top border
      row = row + '─'
    
    row = row + '╮' # End top border
    
    background.append(row) # Add row
    row = ''
    
    for i in range(self.height - 2): # Each empty row
      
      row = row + '│' # Left border
      
      for j in range(self.width - 2): # Each empty column
        row = row + ' '
      
      row = row + '│' # Right border
      
      background.append(row) # Add row
      row = ''
      
    
    row = row + '╰' # Start bottom border
    
    for i in range(self.width - 2): # Bottom border
      row = row + '─'
    
    row = row + '╯' # End bottom border
    
    background.append(row) # Add row
    row = ''
    
    self.background = background # Set to self
    
    #logging.debug(self.title + 'Background:\n' + str(background)) # Logging
    
  
  def renderBackground(self, stdscr):
    
    rowNum = 0 # Row iterator
    
    for row in self.background: # For each row
      stdscr.addstr(self.y + rowNum, self.x, row, curses.color_pair(1)) # Add string
      rowNum += 1 # Iterate
    
  

tableWindow = window(0, 0, 64, 32, '┐Table┌')
chatWindow = window(64, 0, 64, 16, '┐Chat┌')
contextWindow = window(64, 16, 64, 16, '┐Context/Inventory┌')

windows = [tableWindow, chatWindow, contextWindow] # List to iterate

for window in windows: # Each window
  
  window.generateBackground() # Generate backgrounds
  
  screenWidth = max(screenWidth, window.x + window.width) # Screen width
  screenHeight = max(screenHeight, window.y + window.height) # Screen height
  

# Network

class server:
  
  def __init__(self, host, port, clientName, clientColor):
    
    # Variables
    
    self.run = True # Loop control
    self.disconnect = False # Wether its connected
    
    self.name = clientName # Player name
    self.color = clientColor # Display color
    
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket client
    self.host = host # Host IP
    self.port = port # Port
    self.addr = (self.host, self.port) # Full address
    
    # Connect
    
    self.sock.connect(self.addr)
    self.sock.setblocking(True) # Blocking
    
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
          
        
      except OSError as e:
        
        self.disconnect = True
        
        logging.info('Disconnected from server\n' + str(e)) # Logging
        
        break # Break if shutdown
        
      
    
  
  def close(self): # Close connection
    
    self.run = False # Stop recv loop
    
    try:
      self.sock.shutdown(socket.SHUT_RDWR) # Force stop recv loop
    except:
      pass
    
    self.sock.close() # Close
    
    if self.thread.is_alive(): # If alive
      self.thread.join() # End thread
    
    logging.debug('Closed server') # Logging
    
  

### Threads ###

#inputThread = threading.Thread(target=inputThreadFunc)
#inputThread.start()

### Pre-Loop ###

# Server

host = input('Host IP: ') # Inputs
port = strToPosInt(input('Port: '))
clientName = input('Username: ')

try:
  
  clientServer = server(host, port, clientName, '') # Try making server
  
except Exception as e:
  
  logging.exception('Connection Error') # Logging
  
  print('\033[97;41mConnection Error\033[0m\n' + str(e)) # Error message
  
  quit() # Quit
  

# Config

try:
  
  readFiles() # Try reading files
  
except Exception as e:
  
  logging.exception('File Read Error') # Logging
  
  print('\033[97;41mCould Not Read File\033[0m') # Error message
  
  quit() # Quit
  

### Main Loop ###

def main(stdscr): 
  
  # Terminal Setup
  
  curses.curs_set(0) # Hide cursor
  stdscr.nodelay(True) # Non-blocking input
  stdscr.keypad(True) # Enable arrow keys
  curses.noecho() # Don't echo input
  curses.cbreak() # Auto enter input
  curses.start_color() # Allow colors
  curses.use_default_colors() 
  
  # Colors
  
  curses.init_pair(1, 8, -1) # Gray on black
  curses.init_pair(2, 1, -1) # Red on black
  curses.init_pair(3, 3, -1) # Yellow on black
  
  # Global Variables
  
  global run
  global tick
  global spf
  global frameTime
  global selected
  global message
  global termSize
  
  # Main Loop
  
  while run:
    
    # Server disconnect
    
    if clientServer.disconnect:
      
      run = False # Stop running
      
      logging.debug('Server Disconnected') # Logging
      
      break # Stop loop
      
    
    ### Clock ###
    
    tick += 1 # Iterate time ticker
    
    elapsed = time.time() - frameTime # Time since last frame
    time.sleep(max(0, spf - elapsed)) # Pause
    frameTime = time.time() # Update frame time
    
    ### Network ###
    
    while not clientServer.queue.empty(): # While there are messages
      
      message = clientServer.queue.get() # Get message from queue
      
      processMessage(message) # Process & update
      
    
    ### Rendering ###
    
    termSize = stdscr.getmaxyx() # Terminal size (Lines/Height, Columns/Width)
    
    termTooSmall = False # Too small base case
      
    if termSize[0] < screenHeight: # Height too small
      
      termTooSmall = True # Set too small
      
      stdscr.clear() # Clear
      
      text = ( # Output text
        'Terminal height too small!\n' +
        str(termSize[0]) + ' of ' +
        str(screenHeight) + ' lines'
      )
      
      stdscr.addstr(0, 0, text, curses.color_pair(3)) # Out
      
      stdscr.refresh() # Refresh
      
    elif termSize[1] < screenWidth : # Width too small
      
      termTooSmall = True # Set too small
      
      stdscr.clear() # Clear
      
      text = ( # Output text
        'Terminal width too small!\n' +
        str(termSize[1]) + ' of ' +
        str(screenWidth) + ' columns'
      )
      
      stdscr.addstr(0, 0, text, curses.color_pair(3)) # Out
      
      stdscr.refresh() # Refresh
      
    else: # Everything is fine
      
      try: # Try because resizing terminal acts funny
        
        render(stdscr)
        
      except Exception as e:
        
        # Screen
        stdscr.clear()
        stdscr.addstr(0, 0, 'Rendering Error', curses.color_pair(2))
        stdscr.refresh()
        
        logging.exception('Rendering Error') # Logging
        
      
    
    ### Key Input ###
    
    key = stdscr.getch()
    
    # Escape
    
    if key == ord('q'):
      
      if termTooSmall: # Minimal if too small
        run = False
        break
      
      stdscr.nodelay(False) # Block until input
      
      contextWindow.renderBackground(stdscr) # Clear context
      
      stdscr.addstr( # Output
        contextWindow.y + 1,
        contextWindow.x + 1,
        'Quit? (y)'
      )
      
      stdscr.refresh() # Refresh
      
      if stdscr.getch() == ord('y'): # Confirm
        run = False
      
      stdscr.nodelay(True) # Reset to non-blocking
      
    
    # Movements
    
    elif key == ord('d'): selected = (selected[0] + 1, selected[1])
    elif key == ord('a'): selected = (selected[0] - 1, selected[1])
    elif key == ord('s'): selected = (selected[0], selected[1] + 1)
    elif key == ord('w'): selected = (selected[0], selected[1] - 1)
    
    # Other keys
    
    elif key == ord('h') and not termTooSmall: # Help
      
      stdscr.nodelay(False) # Block until input
      
      text = [ # Help text array
        'wasd: Move selected',
        'q: Quit',
        'h: Help',
        '',
        'Press any key to exit'
      ]
      
      contextWindow.renderBackground(stdscr) # Clear context
      
      rowNum = 0 # Row iterator
      
      for row in text: # Each text row
        
        stdscr.addstr( # Output row
          contextWindow.y + 1 + rowNum,
          contextWindow.x + 1,
          row
        )
        
        rowNum += 1 # Iterate row
        
      
      stdscr.refresh() # Refresh
      
      stdscr.getch() # Pause
      
      stdscr.nodelay(True) # Reset to non-blocking
      
    
    elif key == ord('t') and not termTooSmall: # Chat
      
      curses.echo() # Allow echo
      stdscr.nodelay(False) # Block until input
      
      message = stdscr.getstr( # Get message
        chatWindow.y + chatWindow.height - 2,
        chatWindow.x + 3,
        chatWindow.width - 4
      ).decode()
      
      clientServer.send('msg:' + message) # Send
      
      curses.noecho() # Reset to no echo
      stdscr.nodelay(True) # Reset to non-blocking
      
    
    # Clamp Movements
    
    if key != -1: # If there was a keypress
      
      try: # Log key
        logging.debug('Key: ' + chr(key) + ' (' + str(key) + ')') # Normal
      except:
        logging.debug('Key: Error (' + str(key) + ')') # Error
      
      # Selected position
      
      selected = (
        max(min(selected[0], tableWindow.width), 0),
        max(min(selected[1], tableWindow.height), 0)
      )
      
      logging.debug('Selected: ' + str(selected))
      
    
  

# Try: Wrapper

try:
  curses.wrapper(main)
except Exception as e:
  
  logging.exception('Fatal Error') # Log
  
  # Error message
  print('\033[97;41mFatal Error\033[0m')
  

### Post-Loop ###

if clientServer.disconnect: # Killed due to disconnect?
  print('\033[97;41mDisconnected From Server\033[0m') # Print

clientServer.close() # Close server

print('Good Bye!')
