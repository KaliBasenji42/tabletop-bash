# General

This is Python project that emulates tabletop games with bash rendering.  
It uses Curses for terminal rendering and Socket (TCP) for networking.  

> **IMPORTANT:**  
> Do not share your IP address with people you do not trust.  
> This (currently) uses very simple network architecture, and may not be the must secure, this software is for entertainment purposes.  

## Table of Contents

- [Getting Started](#getting-started)  
- [Client UI](#client-ui)
- [File Structure](#file-structure)
- [Data Files](#data-files)
- [Network](#network)

# Getting Started

## Host

1. On the host device move to `./host/`
2. Configure your device IP and Port in `config.json`
    - Ensure your clients can access this IP and Port, you may need to disable your firewall on the given port.
    - If your clients are outside your local network, you may need to forward your port (DO AT YOUR OWN RISK!) (Tunneling may be more secure, do your own networking). 
3. Run `__main__` (type `./__main__` in terminal)
4. Press \[ctrl + c\] to quit
5. Run `manager` (in a new terminal window/device) to send manage the server
    - See [Network](#network) for more details
6. Enter "quit" to quit

## Client

1. Move to `./client/`
2. Run `__main__` (type `./__main__` in terminal)
3. Input the host IP and Port
4. Input your username
    - This can by **any** string (including someone else's), you can press 'u' to change it at any point in the game
5. Press 'q' then 'e' or '1' to quit

# Client UI

Help Text:  
<pre style="white-space: pre; overflow-x: scroll;">
wasd: Move/Navigate
e: Select
x: Cancel
q: Main Menu/Quit
h: Help
t: Chat (enter nothing to cancel)
b: Buzzer
u: Change username

Press "x" to exit
</pre>

# File Structure

<pre style="white-space: pre; overflow-x: scroll;">
.
├── client <i>- Folder for client program</i>
│   ├── app.log <i>- Log file</i>
│   ├── config.json <i>- Config file</i>
│   ├── __main__.py <i>- Main program source script</i>
│   └── __main__ <i>- Main program binary*</i>
├── host <i>- Folder for host server program</i>
│   ├── app.log <i>- Log file</i>
│   ├── config.json <i>- Config file</i>
│   ├── items.json <i>- Item definition file**</i>
│   ├── __main__.py <i>- Main program source script</i>
│   ├── __main__ <i>- Main program binary*</i>
│   ├── manager.py <i>- Manager program source script</i>
│   └── manager <i>- Manager program binary*</i>
├── LICENSE.md <i>- GPL v2 License</i>
└── README.md <i>- This file</i>
</pre>

\* Binary files are packaged using manylinux2014_x86_64 (CentOS), with Python 3.12 Pyinstaller.  
\*\* File that defines the table items.  

# Data Files

## Configs

Config files `config.json` in their respective folders.  

### Host

```JSON
{
  "IP and Port": "comment", // In file comments (JSONs don't allow comments)
  "IP": "127.0.0.1", // Host IP
  "port": 65432, // Host Port
  
  "Enable Whitelist (not Blacklist)": "comment",
  "enableWhitelist": false, // Wether to use whitelist or blacklist
  
  "Whitelist, list IPs": "comment",
  "whitelist": [ // List of IPs to whitelist
    "127.0.0.1"
  ],
  
  "Black;ist, list IPs": "comment",
  "blacklist": [ // List of IPs to blacklist
    
  ],
  
  "Allowed managers (whitelist), list IPs": "comment",
  "managers": [ // List of IPs to whitelist for managers
    "127.0.0.1"
  ]
}
```

### Client

<span id="color-key"></span>

**Color Key:**  

| Int | Color          |
| --- | -------------- |
| 1   | Black          |
| 2   | Red            |
| 3   | Green          |
| 4   | Yellow         |
| 5   | Blue           |
| 6   | Magenta        |
| 7   | Cyan           |
| 8   | White          |
| 9   | Bright Black   |
| 10  | Bright Red     |
| 11  | Bright Green   |
| 12  | Bright Yellow  |
| 13  | Bright Blue    |
| 14  | Bright Magenta |
| 15  | Bright Cyan    |
| 16  | Bright White   |

# Network

## Host

The following describes how the host server behaves when receiving the respective strings.   

**"disconnect":**  

Signifies that a client is disconnected.  

Sends the following in chat:  
\[*UN*\]: Left

> Sent internally  

**"join:*UN*":**  

Signifies that a client has joined.  
Updates `username` dictionary with the client's address as *UN*.  

Sends the following in chat:  
\[*UN*\]: Joined  

**"un:*UN*":**  

Signifies that a client has changed their username.  
Updates `username` dictionary with the client's address as *UN*.  

Sends the following in chat:  
\[*UN*\]: Changed UN

**"msg:*message*":**  

Signifies that a client has sent a chat message.  

Sends the following in chat:  
\[*UN*\]:<br>> *message*  

**"buzz:*message*":**  

Signifies that a client has pressed their buzzer.  

Sends the following in chat:  
\[*UN*\]: *message*  

Note: The message is normally sent in format "\*Buzzer\* at *time*"  
*time* being the client's time of day in format "*minutes*:*seconds*.*microsecond*"  

**"kill":**  

Kill signal, shutdown server.  

> Used by Manager  

**"kick:*addr*":**  

Disconnect connection with the matching *addr*.  

*addr* is in form 0.0.0.0:0000 (ensure port is specified).  

> Used by Manager  

## Client

**"chat:*data*":**  

Updated chat log, sets `chatLog` to *data*.  
*data* is stringified JSON data in form:  
```JSON
[
  [
    "username", // Username of the sender/subject client
    "message", // Message content
    "type", // Type of message (EX: "msg" or "buzz")
  ],
  ...
]
```
> The chat log sent is at most 20 in length.  

**"defaultRender:*data*":**  

Sets `defaultRender` to *data*.  
*data* is stringified JSON data in form:  
```JSON
{
  "itemName": { // Item name/ID
    "char": "🂡", // Character printed for item
    "color": 16 // Color the character is printed in*
  },
  ...
}
```

*[Color Key](#color-key)  

Host server sends this to each client as they join.  