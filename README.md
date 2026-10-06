<style>
  img {max-height: 32rem;}
  body {background-color: rgb(32, 32, 32); color: rgb(240, 240, 240);}
  pre {white-space: pre; overflow-x: scroll; line-height: 1.2em;}
</style>

# General

This is Python project that emulates tabletop games with bash rendering.  
It uses Curses for terminal rendering and Socket (TCP) for networking.  

Binary files are packaged for Linux systems after 2014 and using an x86_64 architecture. Although one can always run the python script itself (`__main__.py`) rather than the binary (`__main__`). Python version 3.12.11 and newer should work.  

Since this software uses Curses, it will problem not work on Window devices. Although I am sure there are forks of Curses that work on Windows. Feel free to edit the code, thats what the GPL v2 License is for :3 (I don't use Windows and don't plan to make it compatible myself).  

> **IMPORTANT:**  
> Do not share your IP address with people you do not trust.  
> And forwarding your IP outside of a local network is risky.    
> This (currently) uses very simple network architecture, and may not be the most secure.  
> This software comes with **no warranty**.  

Note that GitHub breaks CSS, so colors may not be shown.  

## Table of Contents

- [Getting Started](#getting-started)  
- [Client UI](#client-ui)
- [File Structure](#file-structure)
- [Data Files](#data-files)
- [Server](#server)
- [Error Messages](#error-messages)

# Getting Started

## Host

1. On the host device move to `./host/`
2. Configure your device IP and Port in `config.json`
    - Ensure your clients can access this IP and Port, you may need to disable your firewall on the given port.
    - If your clients are outside your local network, you may need to forward your port (DO AT YOUR OWN RISK!) (Tunneling may be more secure, do your own networking). 
3. Configure anything else you want (whitelist, blacklist, PIN)
4. Run `__main__`
5. Press [ctrl + c] to quit
6. Run `manager` (in a new terminal window/device) to connect as Manager client
    - See [Network](#network) for more details
    - Send "quit" as manager to exit

## Client

1. Move to `./client/`
2. Run `__main__`
3. Input the host IP and Port
4. Input the correct PIN. If none was set for the server, then just press enter (empty string)
5. Input your username
    - This can by **any** string (including someone else's), you can press 'u' to change it at any point in the game
6. Press 'q' then 'e' or '1' to quit

# Client UI

Help Text:  
<pre>
wasd: Move/Navigate
[shift] (capitals): Move 5X faster (for table)
e: Select
x: Cancel
q: Main Menu/Quit
h: Help
t: Chat (enter nothing to cancel)
b: Buzzer
u: Change username
p: paint

Press "x" to exit
</pre>

# File Structure

<pre>
.
├── client <i>- Folder for client program</i>
│   ├── app.log <i>- Log file</i>
│   ├── config.json <i>- Config file</i>
│   ├── __main__.py <i>- Main program source script</i>
│   ├── __main__ <i>- Main program binary*</i>
│   └── rendering <i>- Folder for custom rendering data</i>
│       ├── high-contrast.json <i>- High contrast colors</i>
│       └── non-special.json <i>- For terminals that can't render special characters</i>
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

\* Binary files are packaged using manylinux2014_x86_64 (`quay.io/pypa/manylinux2014_x86_64` docker image), with Python 3.12.11.  
\*\* File that defines the table items.  

# Data Files

## Host

### Configs

Config file `config.json` in host folder.  

```JSON
{
  
  "IP and Port": "comment", // In file comments (JSONs don't allow comments)
  "IP": "127.0.0.1", // Host IP
  "port": 65432, // Host Port
  
  "Enable Whitelist (not Blacklist)": "comment",
  "enableWhitelist": false, // Wether to use whitelist or blacklist
  
  "Whitelist, list IPs": "comment",
  "whitelist": [ // List of IPs to whitelist
    "127.0.0.1" // Wildcards ("*") are allowed
  ],
  
  "Blacklist, list IPs": "comment",
  "blacklist": [ // List of IPs to blacklist
    
  ],
  
  "Allowed managers (whitelist), list IPs": "comment",
  "managers": [ // List of IPs to whitelist for managers
    "127.0.0.1"
  ],
  
  "Enable PIN verification": "comment",
  "enablePin": false, // Wether to prompt server for PIN (default is '')
  
  "Wether the contents of disconnected inventories return to Toy Box (discarded otherwise)": "comment",
  "returnDisconnected": true, // Default is to add to Toy Box
  
  "Toy Box contents, -1 is infinite": "comment",
  "toyBox": { // Each item's amount in Toy Box
    "aceSpade": -1, // Default is each from item default json set to infinite
    ...
  },
  
  "Logging level for python's logging module (0-50)": "comment",
  "loggingLevel": 30 // Takes effect after config is read (default is WARNING)
  
}
```

### Items

`items.json` file for defining item behavior and default rendering.  

```JSON
{
  "items": { // Each item by item ID
    "aceSpade": { // Item
      "char": "🂡", // Character for (default) rendering
      "color": 16, // Default rendering color
      "stacks": true, // Wether it stacks (into a deck)
      "flip": "flippedCard" // What the flipped variant references
    },
    
    "dice1": { // Another item
      "char": "⚀",
      "color": 16,
      "stacks": false,
      "roll": ["dice1", "dice2", "dice3", "dice4", "dice5", "dice6"] // When rolled, which item(s) does it randomly change to
    },
    
    ...
  },
  
  "render": { // IDs only for rendering
    
    "flippedCard": { // ID
      "char": "🂠", // Default rendering character
      "color": 16 // Default rendering color
    }
    
    ...
  }
}
```

## Client

### Config

Config file `config.json` in client folder.  

```JSON
{
  
  "Frames per second cap": "comment",
  "fps": 20,
  
  "List of file paths for Custom Rendering": "comment",
  "customRendering": [
    // List of file paths
    // Relative to `__main__.py` (Remember to add `rendering/`)
    // Processes in order listed, last file is dominant
  ],
  
  "Wether to enable character whitelist": "comment",
  "enableCharWhitelist": false,
  
  "Whitelist (string) of allowed characters to render": "comment",
  "charWhitelist": "abcdefghijclmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890-=!@#$%^&*()_+,./<>?;':\"[]\\{}|`~",
  // By Default: All text characters on my keyboard
  
  "Base case character for character whitelist": "comment",
  "baseChar": "?", // Character that replaces characters not in whitelist
  
  "Wether to sort inventory, otherwise will be in the order added": "comment",
  "enableSort": false,
  
  "Order to sort inventory by, unspecified will sort alphabetically at end": "comment",
  "sortOrder": [
    "aceSpade", // Default is copied from the order in the item default json
    ...
  ],
  
  "Logging level for python's logging module (0-50)": "comment",
  "loggingLevel": 30 // Takes effect after config is read (default is WARNING)
  
}
```

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

### Custom Renderings' Look

> Note: GitHub breaks CSS, so colors will not show up if you are viewing through GitHub.  

**Default:**  

Cards:  

<span style="color: rgb(240,240,240)">🂡🂢🂣🂤🂥🂦🂧🂨🂩🂪🂫🂬🂭🂮</span>  
<span style="color: rgb(255,0,0)"    >🂱🂲🂳🂴🂵🂶🂷🂸🂹🂺🂻🂼🂽🂾</span>  
<span style="color: rgb(255,0,0)"    >🃁🃂🃃🃄🃅🃆🃇🃈🃉🃊🃋🃌🃍🃎</span>  
<span style="color: rgb(240,240,240)">🃑🃒🃓🃔🃕🃖🃗🃘🃙🃚🃛🃜🃝🃞</span>  
<span style="color: rgb(240,240,240)">🃟</span>
<span style="color: rgb(255,0,0)"    >🃟</span>
<span style="color: rgb(240,240,240)">🂠</span>  

Chess:  

<span style="color: rgb(240,240,240)">♚♛♜♝♞♟</span>  
<span style="color: rgb(240,240,240)">♔♕♖♗♘♙</span>  

Checkers:  

<span style="color: rgb(240,240,240)">⛂⛃</span>  
<span style="color: rgb(240,240,240)">⛀⛁</span>  

Dice:  

<span style="color: rgb(240,240,240)">⚀⚁⚂⚃⚄⚅</span>  

Stones:  

<span style="color: rgb(128,128,128)">●</span>
<span style="color: rgb(240,0,0)    ">●</span>
<span style="color: rgb(0,240,0)    ">●</span>
<span style="color: rgb(240,240,0)  ">●</span>
<span style="color: rgb(0,0,240)    ">●</span>
<span style="color: rgb(240,0,240)  ">●</span>
<span style="color: rgb(0,240,240)  ">●</span>
<span style="color: rgb(240,240,240)">●</span>  

**`high-contrast.json`:**  

Cards:  

<span style="color: rgb(240,240,240)">🂡🂢🂣🂤🂥🂦🂧🂨🂩🂪🂫🂬🂭🂮</span>  
<span style="color: rgb(255,0,0)"    >🂱🂲🂳🂴🂵🂶🂷🂸🂹🂺🂻🂼🂽🂾</span>  
<span style="color: rgb(0,0,255)"    >🃁🃂🃃🃄🃅🃆🃇🃈🃉🃊🃋🃌🃍🃎</span>  
<span style="color: rgb(0,255,0)"    >🃑🃒🃓🃔🃕🃖🃗🃘🃙🃚🃛🃜🃝🃞</span>  
<span style="color: rgb(240,240,240)">🃟</span>
<span style="color: rgb(255,0,0)"    >🃟</span>
<span style="color: rgb(240,240,240)">🂠</span>  

Chess:  

<span style="color: rgb(240,240,240)">♚♛♜♝♞♟</span>  
<span style="color: rgb(0,240,240)"  >♔♕♖♗♘♙</span>  

Checkers:  

<span style="color: rgb(240,240,240)">⛂⛃</span>  
<span style="color: rgb(0,240,240)"  >⛀⛁</span>  

Dice:  

<span style="color: rgb(240,0,240)">⚀⚁⚂⚃⚄⚅</span>  

Stones:  

<span style="color: rgb(128,128,128)">●</span>
<span style="color: rgb(240,0,0)    ">●</span>
<span style="color: rgb(0,240,0)    ">●</span>
<span style="color: rgb(240,240,0)  ">●</span>
<span style="color: rgb(0,0,240)    ">●</span>
<span style="color: rgb(240,0,240)  ">●</span>
<span style="color: rgb(0,240,240)  ">●</span>
<span style="color: rgb(240,240,240)">●</span>  

**`non-special.json`:**  

Cards:  

<span style="color: rgb(240,240,240)">A234567890JCQK</span>  
<span style="color: rgb(255,0,0)"    >A234567890JCQK</span>  
<span style="color: rgb(0,0,255)"    >A234567890JCQK</span>  
<span style="color: rgb(0,255,0)"    >A234567890JCQK</span>  
<span style="color: rgb(240,240,240)">\*</span>
<span style="color: rgb(255,0,0)"    >\*</span>
<span style="color: rgb(240,240,240)">#</span>  

Chess:  

<span style="color: rgb(240,240,0)">KQRBNP</span>  
<span style="color: rgb(0,240,240)">KQRBNP</span>  

> "N" for kNight  

Checkers:  

<span style="color: rgb(240,240,0)">dD</span>  
<span style="color: rgb(0,240,240)">dD</span>  

> "d"/"D" for daughter  

Dice:  

<span style="color: rgb(240,0,240)">123456</span>  

Stones:  

<span style="color: rgb(128,128,128)">@</span>
<span style="color: rgb(240,0,0)    ">@</span>
<span style="color: rgb(0,240,0)    ">@</span>
<span style="color: rgb(240,240,0)  ">@</span>
<span style="color: rgb(0,0,240)    ">@</span>
<span style="color: rgb(240,0,240)  ">@</span>
<span style="color: rgb(0,240,240)  ">@</span>
<span style="color: rgb(240,240,240)">@</span>  

# Server

The following describes how the receptive programs' server behaves when receiving the respective strings.   

## Host

**"disconnect":**  

Signifies that a client is disconnected.  

Sends the following in chat:  
&#91;*UN*&#93;: Left

> Sent internally  

**"join:*UN*":**  

Signifies that a client has joined.  
Updates `username` dictionary with the client's address as *UN*.  

Sends the following in chat:  
&#91;*UN*&#93;: Joined  

**"un:*UN*":**  

Signifies that a client has changed their username.  
Updates `username` dictionary with the client's address as *UN*.  

Sends the following in chat:  
&#91;*UN*&#93;: Changed UN

**"msg:*message*":**  

Signifies that a client has sent a chat message.  

Sends the following in chat:  
&#91;*UN*&#93;:<br>> *message*  

**"buzz:*message*":**  

Signifies that a client has pressed their buzzer.  

Sends the following in chat:  
&#91;*UN*&#93;: *message*  

Note: The message is normally sent in format "\*Buzzer\* at *time*"  
*time* being the client's time of day in format "*minutes*:*seconds*.*microsecond*"  

**"kill":**  

Kill signal, shutdown server.  

> Used by Manager  

**"kick:*addr*":**  

Disconnect connection with the matching *addr*.  

*addr* is in form 0.0.0.0:0000 (ensure port is specified).  

> Used by Manager  

**"color:*color*,*y*,*x*":**  

Sets color of table at location. Splits string into *color*, *y*, and *x*, then converts to integers. *color* is based on [Color Key](#color-key). If *y* or *x* is out of range, message is silently ignored.  

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

# Error Messages

> Note: GitHub breaks CSS, so colors will not show up if you are viewing through GitHub.  

**Message:**  

<span style="color: rgb(240, 240, 240); background-color: rgb(240, 0, 0);">File Read Error</span>  
*Error*  

**Description:**  

The program was unable to read a file storing required data for startup. Usually a config file. Most likely caused by a file named incorrectly. The *error* is printed.  

## Client

**Message:**  

<span style="color: rgb(240, 240, 240); background-color: rgb(240, 0, 0);">Connection Error</span>  
*Error*  

**Description:**  

The program was unable to connect to the server. Most likely caused by an incorrect address. Ensure the correct address is configured in the server config (use `ip addr` or similar to check local/home network address), and that the address the client inputs matches this. The *error* is printed.  

**Message:**  

<span style="color: rgb(240, 240, 240); background-color: rgb(240, 0, 0);">Fatal Error</span>  
*Error*  

**Description:**  

An unresolvable error in the main loop occurred. Probably a programming error (please report, if so). The *error* is printed.  

**Message:**  

<span style="color: rgb(240, 240, 240); background-color: rgb(240, 0, 0);">Disconnected From Server</span>  

**Description:**  

Client is no longer able to connect to server. Most likely caused by a kick or server shutdown.  

**Message:**  

<span style="color: rgb(0, 0, 0); background-color: rgb(240, 240, 0);">PIN Failed</span>  

**Description:**  

Hashed PINs did not match. Incorrect PIN was likely inputted (note that servers with PIN disabled use a blank PIN, so one should only press enter).  

**Message:**  

<span style="color: rgb(240, 0, 0); background-color: rgb(0, 0, 0);">Rendering Error</span>  

**Description:**  

An unresolvable error in the main rendering function occurred. Probably a programming error (please report, if so). Exit by pressing 'q' then 'e' or '1' (or [ctrl + c]).  

## Server

**Message:**  

<span style="color: rgb(240, 240, 240); background-color: rgb(240, 0, 0);">Socket Bind Error</span>  
*Error*

**Description:**  

The server is unable to use the configured address. Likely due to the configured port currently being in use, or your system thinking it is currently in use. Try again in a few moments, or configure a different port. The *error* is printed.  

**Message:**  

<span style="color: rgb(0, 0, 0); background-color: rgb(240, 240, 0);">Server Queue Error</span>  
*Error*  

**Description:**  

The server was unable to process a message (messages are stored in a queue, hence the name). Most likely a message formatted incorrectly, or a programming error being handled non-fatally. The *error* is printed.  
