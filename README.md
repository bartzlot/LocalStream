
# LocalStream Application

## Overview
LocalStream is a Python-based application designed for secure and efficient file transfer over a local network. It incorporates advanced encryption mechanisms for secure data transmission and supports robust session management to ensure reliable connections.

---

## **Usage**
This project provides a command-line interface (CLI) to manage both server and client-side file operations. The commands are handled via the `fire` library, which provides a simple and flexible way to interact with the application from the command line.

### Start the CLI:
```bash
   python localstream.py
```
The `CLI` class defines the command-line interface commands that can be executed by the user.

#### Server-Side Commands

1. **Add a Connection**
    - **Command**: `add_connection`
    - **Arguments**:
        - `port` (int) - The port number the server will listen to.
        - `max_connections` (int, optional, default: 1) - Maximum number of connections allowed.
    - **Example**:
      ```bash
      add_connection 8080 10
      ```
    - **Description**: Adds a new connection on the server to allow clients to connect.


2. **Add a Local Connection**
    - **Command**: `add_local_connection`
    - **Arguments**:
        - `host` (str) - The IP address of the host.
        - `port` (int) - The port number.
        - `max_connections` (int) - Maximum number of connections allowed.
    - **Example**:
      ```bash
      add_local_connection 192.168.1.1 8080 10
      ```
    - **Description**: Adds a local connection to the server with the provided host and port.


3. **Delete a Connection**
    - **Command**: `del_connection`
    - **Arguments**:
        - `port` (int) - The port number of the connection to delete.
    - **Example**:
      ```bash
      del_connection 8080
      ```
    - **Description**: Removes an existing connection from the server based on the provided port.


4. **Send a File**
    - **Command**: `send_file`
    - **Arguments**:
        - `port` (int) - The port of the connection.
        - `file_path` (str) - The path of the file to send.
        - `chunk_size` (int, optional, default: 1024) - Size of chunks for file transfer.
    - **Example**:
      ```bash
      send_file 8080 /path/to/file.txt 2048
      ```
    - **Description**: Sends a file to the connected client.


5. **List Possible Connections**
    - **Command**: `possible_connections`
    - **Arguments**: None
    - **Example**:
      ```bash
      possible_connections
      ```
    - **Description**: Lists all the available possible connections on the server.


6. **Get Server Status**
    - **Command**: `status`
    - **Arguments**: None
    - **Example**:
      ```bash
      status
      ```
    - **Description**: Displays the current status of the server, including active connections.

---

### Client-Side Commands

1. **Connect to Server**
    - **Command**: `connect`
    - **Arguments**:
        - `host` (str) - The IP address of the server.
        - `port` (int) - The port number of the server.
    - **Example**:
      ```bash
      connect 192.168.1.1 8080
      ```
    - **Description**: Connects the client to the server at the specified host and port.


2. **Receive a File**
    - **Command**: `receive_file`
    - **Arguments**:
        - `file_save_path` (str) - The path where the file will be saved on the client-side.
    - **Example**:
      ```bash
      receive_file /path/to/save/file.txt
      ```
    - **Description**: Receives a file from the server and saves it to the specified path.


3. **Exit CLI**
    - **Command**: `exit`
    - **Arguments**: None
    - **Example**:
      ```bash
      exit
      ```
    - **Description**: Exits the CLI application.

---


### Additional Notes:
- Ensure that both server and client devices are on the same network.
- All files transferred are encrypted for security.

---

## **Libraries**
### Language:
- **Python Version**: Python 3.8 or higher is required.

### Standard Libraries:
- `socket`: Facilitates communication over the network.
- `os`: Manages file and directory operations.
- `json`: Handles configuration and session data.
- `base64`: Used for encoding and decoding data.
- `uuid`: Generates unique identifiers for identifying devices and sessions.

## Third-Party Libraries

- **`cryptography`**: For encryption and key management.
- **`fire`**: For building the command-line interface (CLI).
- **`netifaces`**: For interacting with network interfaces and retrieving MAC/IP addresses.

 To install dependencies, run:
  ```bash
  pip install -r requirements.txt
  ```

---

## **Modules**
### **Connections**
#### **`client.py`**
Handles client-side network interactions. Main responsibilities include:
- Establishing a connection to the server.
- Sending files securely after encryption.
- Managing error handling during transmission.

#### **`server.py`**
Listens for client connections and processes incoming encrypted files. Features:
- Handles decryption and stores the received files.
- Verifies client credentials using session keys.

#### **`connection_management.py`**
Utility functions supporting connections:
- Socket setup and configuration.
- Error handling for failed connection attempts.

#### **`new_connection.py`**
Responsible for initializing and validating new client connections:
- Exchanges public keys for secure session setup.
- Ensures clients are authenticated before accepting files.

#### **`server_message_flags.json`**
A configuration file containing predefined flags for server responses, such as success, error, and status codes.

### **Files**
#### **`file_manager.py`**
Core module for file operations:
- Encrypts files on the client-side before transmission.
- Decrypts files on the server-side after receipt.
- Validates file integrity post-transfer.

#### **`error_handler.py`**
Custom error-handling utilities for:
- Logging connection or file transfer errors.
- Gracefully recovering from failures without terminating the application.

### **Session**
#### **`session_manager.py`**
Manages session-level operations:
- Stores session data (e.g., client MAC addresses and encryption keys) in JSON format.
- Ensures persistent logging of active sessions.
- Supports secure retrieval of session-related information.

---

## **Features**
1. **End-to-End Encryption**:
   - Files are encrypted using AES before transmission.
   - Public-key exchange using RSA ensures secure key sharing.

2. **Session Management**:
   - Tracks client sessions, ensuring secure, authenticated connections.

3. **Modular Architecture**:
   - Each component is self-contained, making the application scalable and easy to maintain.

4. **Cross-Platform Compatibility**:
   - Works on any system supporting Python 3.8+.

5. **Customizable**:
   - Easily adaptable to include additional encryption methods or file transfer protocols.

---

## License
LocalStream is licensed under the MIT License. See `LICENSE.md` for details.

---
