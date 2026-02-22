# Tabletop Bash - Client
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
import datetime
import random
import socket
import threading
import queue
import json
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
chatLog = [] # 2D array of strings, containing the chat log
# Note: Sent as json string

# Control

spf = 1/20 # Second per Frames
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
      
      chatLog = json.loads(message[5:]) # Load json
      
  

# output

def renderTable(): # Takes tableState and redraws tableGrid for rendering
  
  pass
  

def render(stdscr): # Render screen
  
  stdscr.clear() # Clear
  
  # Backgrounds
  
  for window in windows:
    window.renderBackground(stdscr)
  
  # Chat
  
  global chatLog
  
  chatArr = [] # Array for chat rendering
  
  prevLog = ['','',''] # Previous log
  
  for log in chatLog: # Each log
    
    if log[2] == 'conn' or log[2] == 'buzz': # Type is connection or buzzer
      chatArr.append(log) # Append normally
    
    elif log[2] == 'msg': # Type is message
      
      if prevLog[2] != 'msg' or prevLog[0] != log[0]: # Only add header if:
        # Previous was not a message, or different sender/UN
        chatArr.append([log[0], '', 'msgHead']) # Message/UN header
      
      chatArr.append(['', log[1], 'msgCont']) # Message content
      
    
    prevLog = log # Set previous log
    
  
  while len(chatArr) > chatWindow.height - 3: # While too long
    chatArr.pop(0) # Remove oldest
  
  for i in range(len(chatArr)): # Each line
    
    # Username
    
    UN = chatArr[i][0][:chatWindow.width - 12] # Username
    lenUN = len(UN) # Username length
    
    # Render UN?
    
    if chatArr[i][2] == 'msgCont': # Type is message content (no UN)
      
      stdscr.addstr( # '>'
        chatWindow.y + i + 1, chatWindow.x + 1,
        '>', curses.color_pair(15) # Cyan
      )
      
      stdscr.addstr( # Content
        chatWindow.y + i + 1, chatWindow.x + 3,
        chatArr[i][1]
      )
      
    
    else: # Not message content (render UN)
      
      stdscr.addstr(chatWindow.y + i + 1, chatWindow.x + 1, '[') # UN '['
      stdscr.addstr( # UN
        chatWindow.y + i + 1, chatWindow.x + 2, 
        UN, curses.color_pair(11) # Green
      )
      stdscr.addstr(chatWindow.y + i + 1, chatWindow.x + lenUN + 2, ']:') # UN ']'
      
    
    # Message content that is not a message
    
    if chatArr[i][2] == 'conn': # Type is connection
      
      if chatArr[i][1] == 'Joined': # Join message
        
        stdscr.addstr(
          chatWindow.y + i + 1, chatWindow.x + lenUN + 5,
          chatArr[i][1], curses.color_pair(13) # Blue
        )
        
      
      elif chatArr[i][1] == 'Left': # Left message
        
        stdscr.addstr(
          chatWindow.y + i + 1, chatWindow.x + lenUN + 5,
          chatArr[i][1], curses.color_pair(12) # Yellow
        )
        
      
      elif chatArr[i][1] == 'Changed UN': # Changed username
        
        stdscr.addstr(
          chatWindow.y + i + 1, chatWindow.x + lenUN + 5,
          chatArr[i][1], curses.color_pair(14) # Magenta
        )
        
      
    
    elif chatArr[i][2] == 'buzz': # Type is buzzer
      
      stdscr.addstr(
        chatWindow.y + i + 1, chatWindow.x + lenUN + 5,
        '*Buzzer* at ' + chatArr[i][1], curses.color_pair(10) # Red
      )
      
    
  # Context
  
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
  
  for i in range(16): # Color
    stdscr.addstr(i, 0, str(i+1), curses.color_pair(i+1))
  
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
      stdscr.addstr(self.y + rowNum, self.x, row, curses.color_pair(9)) # Add string
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
  
  def __init__(self, host, port, clientName):
    
    # Variables
    
    self.run = True # Loop control
    self.disconnect = False # Wether its connected
    
    self.name = clientName # Player name
    
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
    
  

### Threads ###

#inputThread = threading.Thread(target=inputThreadFunc)
#inputThread.start()

### Pre-Loop ###

# Title

title = """
▄▄▄▄  ▄▄▄▄  ▄▄▄▄  ▖     ▄▄▄▄  ═⍐═  ╔⍐╗  ╔═╗    ┌─╮  ╭─╮  ╭─╴  ╷ ╷
 ▐▌   ▙▄▄▟  ▙▄▄▟  ▌     ▙▄▄▄   ║   ⍐ ⍐  ⍐═╝    ├─┤  ├─┤  ╰─╮  ├─┤
 ▟▙   ▌  ▐  ▙▄▄▟  ▙▄▄▄  ▙▄▄▄   ║   ╚⍐╝  ║      └─╯  ╵ ╵  ╶─╯  ╵ ╵

<===### Client ###===>

Copyright (C) 2026 KaliBasenji42
Tabletop Bash comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain conditions.

License: ./LICENSE.md
GPL v2: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
KaliBasenji42's Github: https://github.com/KaliBasenji42

NOTE: Press 'h' for help menu once connected
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
  
  for i in range(16): # Base 4-bit colors (on black)
    curses.init_pair(i+1, i, -1)
  
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
      
      stdscr.addstr(0, 0, text, curses.color_pair(12)) # Out
      
      stdscr.refresh() # Refresh
      
    elif termSize[1] < screenWidth : # Width too small
      
      termTooSmall = True # Set too small
      
      stdscr.clear() # Clear
      
      text = ( # Output text
        'Terminal width too small!\n' +
        str(termSize[1]) + ' of ' +
        str(screenWidth) + ' columns'
      )
      
      stdscr.addstr(0, 0, text, curses.color_pair(12)) # Out
      
      stdscr.refresh() # Refresh
      
    else: # Everything is fine
      
      try: # Try because resizing terminal acts funny
        
        render(stdscr)
        
      except Exception as e:
        
        # Screen
        stdscr.clear()
        stdscr.addstr(0, 0, 'Rendering Error', curses.color_pair(10))
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
        'e: Select',
        'q: Quit',
        'h: Help',
        't: Chat (enter nothing to cancel)',
        'b: Buzzer',
        'u: Change username',
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
      
      stdscr.addstr( # Cursor
        chatWindow.y + chatWindow.height - 2,
        chatWindow.x + 1,
        '> '
      )
      
      message = stdscr.getstr( # Get message
        chatWindow.y + chatWindow.height - 2,
        chatWindow.x + 3,
        chatWindow.width - 4
      ).decode()
      
      if message != '': clientServer.send('msg:' + message) # Send
      
      curses.noecho() # Reset to no echo
      stdscr.nodelay(True) # Reset to non-blocking
      
    
    elif key == ord('b') and not termTooSmall: # Buzzer
      
      curses.beep() # Beep
      
      timeNow = datetime.datetime.now() # Current time down to ms
      
      msStr = str(timeNow.microsecond) # Micro second string
      while len(msStr) < 6: # While too short
        msStr = '0' + msStr # Add '0'
      
      timeStr = ( # String to send
        str(timeNow.minute) + ':' +
        str(timeNow.second) + '.' +
        msStr
      )
      
      clientServer.send('buzz:' + timeStr) # Send
      
      logging.debug('Buzzer at ' + str(timeNow)) # Logging
      
    
    elif key == ord('u') and not termTooSmall: # Username
      
      curses.echo() # Allow echo
      stdscr.nodelay(False) # Block until input
      
      contextWindow.renderBackground(stdscr) # Clear context
      
      stdscr.addstr( # Header
        contextWindow.y + 1,
        contextWindow.x + 1,
        'Change Username'
      )
      
      stdscr.addstr( # Original UN
        contextWindow.y + 2,
        contextWindow.x + 1,
        ('Originally: "' + clientServer.name + '"')[:contextWindow.width - 2]
      )
      
      stdscr.addstr( # Cursor
        contextWindow.y + 3,
        contextWindow.x + 1,
        '> '
      )
      
      clientServer.name = stdscr.getstr( # Get message
        contextWindow.y + 3,
        contextWindow.x + 3
      ).decode()
      
      clientServer.send('un:' + clientServer.name) # Send
      
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
