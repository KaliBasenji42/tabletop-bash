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

message = '' # Chat message to send

# Control

spf = 1/30 # Second per Frames
tick = 0 # Time ticker
run = True # Run Main Loop

selected = (0, 0) # Selected cell

termSize = (0, 0) # Terminal dimensions

screenWidth = 0 # Screen width, defined after window objects
screenHeight = 0 # Screen height

termTooSmall = True # Wether the terminal is too small

# Game

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
  

# output

def render(stdscr): # Render screen
  
  stdscr.clear() # Clear
  
  # Backgrounds
  
  for window in windows:
    window.renderBackground(stdscr)
  
  # Debug
  
  widthStr = ( # String for logging width
    'Width: ' + str(screenWidth) +
    ' of ' + str(termSize[0])
  )
  
  heightStr = ( # String for logging height
    'Height: ' + str(screenHeight) +
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

class window:
  
  def __init__(self, x, y, width, height, title):
    
    # Variables
    
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.title = title
    
  
  def generateBackground(self): # Generate background away, set to self
    
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
    
  

# Define Windows

tableWindow = window(0, 0, 64, 32, '┐Table┌')
chatWindow = window(64, 0, 64, 16, '┐Chat┌')
contextWindow = window(64, 16, 64, 16, '┐Context/Inventory┌')

windows = [tableWindow, chatWindow, contextWindow] # List to iterate

for window in windows: # Each window
  
  window.generateBackground() # Generate backgrounds
  
  screenWidth = max(screenWidth, window.x + window.width) # Screen width
  screenHeight = max(screenHeight, window.y + window.height) # Screen height
  

### Threads ###

#inputThread = threading.Thread(target=inputThreadFunc)
#inputThread.start()

### Pre-Loop ###

try:
  
  readFiles() # Try reading files
  
except Exception as e:
  
  logging.exception(e) # Log
  
  # Error message
  print('\033[97;41mCould Not Read File\033[0m')
  
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
  
  # Global Variables
  
  global run
  global tick
  global spf
  global selected
  global message
  global termSize
  
  # Main Loop
  
  while run:
    
    ### Clock ###
    
    tick += 1 # Iterate time ticker
    
    time.sleep(spf)
    
    ### Rendering ###
    
    # Terminal width
    
    termSize = ( # Terminal size
      os.get_terminal_size().columns,
      os.get_terminal_size().lines
    )
    
    termTooSmall = False # Too small base case
    
    if termSize[0] < screenWidth : # Width too small
      
      termTooSmall = True # Set too small
      
      stdscr.clear() # Clear
      
      text = ( # Output text
        'Terminal width too small!\n' +
        str(termSize[0]) + ' of ' +
        str(screenWidth) + ' columns'
      )
      
      stdscr.addstr(0, 0, text, curses.color_pair(2)) # Out
      
      stdscr.refresh() # Refresh
      
    elif termSize[1] < screenHeight + 2: # Height too small
      
      termTooSmall = True # Set too small
      
      stdscr.clear() # Clear
      
      text = ( # Output text
        'Terminal height too small!\n' +
        str(termSize[1]) + ' of ' +
        str(screenHeight + 2) + ' lines'
      )
      
      stdscr.addstr(0, 0, text, curses.color_pair(2)) # Out
      
      stdscr.refresh() # Refresh
    
    else: # Everything is fine
      
      render(stdscr)
      
    
    ### Key Input ###
    
    try: key = chr(stdscr.getch())
    except: key = ''
    
    # Escape
    
    if key.lower() == 'q':
      
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
    
    elif key.lower() == 'd': selected = (selected[0] + 1, selected[1])
    elif key.lower() == 'a': selected = (selected[0] - 1, selected[1])
    elif key.lower() == 's': selected = (selected[0], selected[1] + 1)
    elif key.lower() == 'w': selected = (selected[0], selected[1] - 1)
    
    # Other keys
    
    elif key.lower() == 'h' and not termTooSmall: # Help
      
      stdscr.nodelay(False) # Block until input
      
      text = [ # Help text array
        'wasd: Move selected',
        'q/Q: Quit',
        'h/H: Help',
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
      
    
    elif key.lower() == 't' and not termTooSmall: # Chat
      
      curses.echo() # Allow echo
      stdscr.nodelay(False) # Block until input
      
      message = stdscr.getstr(0, 0, 16) # Get message
      
      curses.noecho() # Reset to no echo
      stdscr.nodelay(True) # Reset to non-blocking
      
    
    # Clamp Movements
    
    if key != '':
      
      selected = (
        max(min(selected[0], tableWindow.width), 0),
        max(min(selected[1], tableWindow.height), 0)
      )
      
      logging.debug('Key: ' + key) # Logging
      logging.debug('Selected: ' + str(selected))
      
    
  

# Try: Wrapper

try:
  curses.wrapper(main)
except Exception as e:
  
  logging.exception("Fatal Error") # Log
  
  # Error message
  print('\033[97;41mFatal Error\033[0m')
  

### Post-Loop ###

print('Bye 👋')

#inputThread.join()
