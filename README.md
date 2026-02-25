# General

This is Python project that emulates tabletop games with bash rendering.  
It uses Curses for terminal rendering and Socket (TCP) for networking.  

> **IMPORTANT:**  
> Do not share your IP address with people you do not trust.  

# Getting Started

## Host

1. On the host device move to `./host/`
2. Configure your device IP and Port in `config.json`
    - Ensure your clients can access this IP and Port, you may need to disable your firewall on the given port.
3. Run `__main__` (type `./__main__` in terminal)
4. Run `manager` (in a new terminal window/device) to send manage the server
    - See [Network](#network) for more details
5. Press \[ctrl + c\] to quit

## Client

1. Move to `./client/`
2. Run `__main__` (type `./__main__` in terminal)
3. Input the host IP and Port
4. Input your username
    - This can by **any** string (including someone else's), you can press 'u' to change it at any point in the game
5. Press 'q' then 'y' to quit

# Client UI

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
*data* is JSON data in form:  
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