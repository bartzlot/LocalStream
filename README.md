
# LocalStream Application

## Overview
LocalStream is a Python-based application designed for secure and efficient file transfer over a local network. It incorporates advanced encryption mechanisms for secure data transmission and supports robust session management to ensure reliable connections.

---

## **Usage**
### Main Commands
#### **Server (`main.py`)**:
Launches the server-side application to listen for incoming connections and receive encrypted files. This is typically run on the machine designated to collect files from clients.
```bash
python main.py
```

#### **Client (`test.py`)**:
Initiates a connection to the server and securely sends files. This is used by the client-side user to transmit files over the network.
```bash
python test.py <server_ip> <file_path>
```

#### Arguments:
- `<server_ip>`: The IP address of the server machine to which the file will be sent. This must match the IP where the server is running.
- `<file_path>`: The full path to the file on the local system that you want to transmit.

### Example Workflow:
1. Start the server:
   ```bash
   python main.py
   ```
   The server will display its IP address, ready to accept connections.
   
2. On the client-side, send a file:
   ```bash
   python test.py 192.168.1.10 /path/to/file.txt
   ```

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

### Third-party Libraries:
- **`cryptography`**: Core library used for encryption and decryption.
  - **AES (Advanced Encryption Standard)**: Ensures secure file content transmission.
  - **RSA (Rivest-Shamir-Adleman)**: Used for public-key exchange.
- To install dependencies, run:
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

## **Future Enhancements**
1. Add support for file compression during transmission.
2. Integrate a GUI for better user experience.
3. Implement a notification system for transfer completion.

---

## **Contributing**
We welcome contributions to improve LocalStream. Please fork the repository, create a feature branch, and submit a pull request.

### **Development Guidelines**:
1. Ensure the code is PEP 8 compliant.
2. Write unit tests for new features.
3. Document new modules and functions clearly.

---

## License
LocalStream is licensed under the MIT License. See `LICENSE.md` for details.

---
