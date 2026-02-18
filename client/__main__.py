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

tableSize = (24, 24) # Table dimensions

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
  

### Classes ###

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
  
  # Global Variables
  
  global run
  global tick
  global spf
  global selected
  global message
  
  while run:
    
    ### Clock ###
    
    tick += 1 # Iterate time ticker
    
    time.sleep(spf)
    
    ### Rendering ###
    
    termSize = ( # Terminal size
      os.get_terminal_size().columns,
      os.get_terminal_size().lines
    )
    
    stdscr.clear() # Clear
    
    stdscr.addstr(0, 0, 'Width: ' + str(termSize[0]))
    stdscr.addstr(1, 0, 'Height: ' + str(termSize[1]))
    stdscr.addstr(2, 0, 'Ticks: ' + str(tick))
    stdscr.addstr(3, 0, 'Message: ' + str(message))
    stdscr.addstr(4, 0, 'H for Help')
    
    stdscr.refresh() # Refresh
    
    ### Key Input ###
    
    try: key = chr(stdscr.getch())
    except: key = ''
    
    # Escape
    
    if key.lower() == 'q':
      
      stdscr.nodelay(False) # Block until input
      
      stdscr.clear() # Clear
      
      screen = ('Quit? (y)') # Message
      
      stdscr.addstr(0, 0, screen) # Output
      stdscr.refresh()
      
      if stdscr.getch() == ord('y'): # Confirm
        run = False
      
      stdscr.nodelay(True) # Reset to non-blocking
      
    
    # Movements
    
    elif key.lower() == 'd': selected = (selected[0] + 1, selected[1])
    elif key.lower() == 'a': selected = (selected[0] - 1, selected[1])
    elif key.lower() == 's': selected = (selected[0], selected[1] + 1)
    elif key.lower() == 'w': selected = (selected[0], selected[1] - 1)
    
    # Other keys
    
    elif key.lower() == 'h': # Help
      
      stdscr.nodelay(False) # Block until input
      
      stdscr.clear() # Clear
      
      screen = ('wasd: Move selected\n' +
                'q/Q: Quit\n' +
                'h/H: Help\n' +
                '\nPress any key to exit\n') # Help screen
      
      stdscr.addstr(0, 0, screen) # Output
      stdscr.refresh()
      
      stdscr.getch() # Pause
      
      stdscr.nodelay(True) # Reset to non-blocking
      
    
    elif key.lower() == 't': # Chat
      
      curses.echo() # Allow echo
      stdscr.nodelay(False) # Block until input
      
      message = stdscr.getstr(0, 0, 16) # Get message
      
      curses.noecho() # Reset to no echo
      stdscr.nodelay(True) # Reset to non-blocking
      
    
    # Clamp Movements
    
    if key != '':
      
      selected = (
        max(min(selected[0], tableSize[0] - 1), 0),
        max(min(selected[1], tableSize[1] - 1), 0)
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

print('Exited')

#inputThread.join()
