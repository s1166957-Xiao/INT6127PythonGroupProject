# INT6127PythonGroupProject
# Express Management System
Topic: Intelligent Management System for Campus Express Stations Based on Python (GUI)

### Members: 

Xiao Boersheng 11669576

Li Yueming 11654923

Zhao Zihan 11669318

Zhen Tianying 11654478

Zhang Fangzhe 11654894 @metr0man


### Background:

With the rapid development of the e-commerce industry, the national express delivery business volume exceeded 120 billion pieces in 2024, and the "last mile" delivery has become a key link in the logistics chain. As a mainstream way to solve the "last mile" problem, campus express delivery stations handle an average of 300-800 pieces per day, and even exceed 1,000 pieces during peak seasons. Traditional management methods mostly rely on manual registration and paper or Excel ledgers, leading to problems such as low efficiency, chaotic data, and poor user experience. 
In addition, the security and traceability of express delivery data have also attracted increasing attention. Traditional databases are prone to tampering or loss, making it difficult to meet the needs of supervision and users for data authenticity. To this end, the project introduces blockchain technology to put express delivery data on the chain, realizing the immutability of information and full-process traceability, and further improving management transparency and data security.

### Solution and Approach

This system targets the high-frequency business scenarios of campus courier stations, proposing an integrated solution of "Intelligent Courier Management + Data On-Chain + Security Authentication":

1. **Efficient Courier Management**: A graphical interface developed with Python enables digital management of the entire process, including courier storage, classification, pickup, query, and statistics, greatly improving operational efficiency.
2. **Data Security and Traceability**: Core courier data (such as storage, pickup, user information, operation logs, etc.) is synchronized and uploaded to the blockchain, ensuring data immutability and verifiability to meet regulatory and user requirements for data security.
3. **Security Authentication Mechanism**: The system integrates TOTP (Time-based One-Time Password) dynamic code authentication for station staff identity verification. In addition to mainstream authenticators (such as mobile apps), we have independently developed a Micropython-based TOTP hardware key, achieving physical-level security authentication. Only administrators who pass TOTP authentication can perform sensitive operations (such as resetting keys, managing users), effectively preventing unauthorized actions and ensuring system security.
4. **User Experience Optimization**: Integrated QR code generation and recognition support scan-to-pickup and quick information entry, reducing manual operation time and improving user satisfaction.
5. **Scalability and Maintainability**: Modular design supports functional expansion and third-party system integration, facilitating future upgrades and maintenance.

## Project Introduction

This project is an intelligent courier management system for campus courier stations, developed in Python and combined with blockchain technology to achieve secure storage and full-process traceability of courier data. The system features a user-friendly graphical interface, supporting core functions such as courier storage, pickup, query, user management, and data statistics, and integrates QR code technology to enhance operational efficiency. All key business data can be automatically synchronized to the blockchain, ensuring data security and transparency. Administrator authentication uses TOTP dynamic codes and supports Micropython hardware keys for enhanced system security.

## Core Features

- **Courier Storage Management**: Automatically generates tracking numbers and pickup codes, supports courier information entry and classification, and uploads storage data to the blockchain in real time.
- **QR Code Integration**: Supports generation and recognition of courier information QR codes, enabling scan-to-pickup and quick information entry.
- **Courier Pickup Management**: Supports pickup code verification and status updates, with pickup operations automatically recorded and synchronized to the blockchain.
- **User Management**: Maintains sender and recipient information, supports batch import and editing, with user data securely stored and uploaded to the blockchain.
- **Data Statistics and Visualization**: Real-time statistics of stored courier quantities and area distribution, supports chart display, and statistical results can be stored on-chain.
- **Real-time Search and Retrieval**: Supports multi-condition courier information query to improve search efficiency.
- **Blockchain Data Synchronization**: All core business data (storage, pickup, user, statistics, etc.) is automatically uploaded to the blockchain, ensuring data immutability and traceability.
- **Security Authentication and Permission Management**: Integrates TOTP dynamic codes and supports Micropython hardware keys to ensure administrator operation security.
- **Lightweight Deployment and Easy Maintenance**: Supports standalone deployment without complex server environments, with robust data persistence and backup mechanisms for daily operation and maintenance.

### Technology Stack
- Core Language: Python 3.x
- GUI Framework: Tkinter
- Data Storage: SQLite
- Dependent Libraries: pandas, qrcode, opencv-python, pyzbar, Pillow, matplotlib

### Project Highlights
- Lightweight Design: Standalone deployment without complex server environment
- Reliable Data: Uses SQLite database with data persistence support
- User-friendly Interface: Intuitive graphical interface for easy operation
- Extensibility: Modular design facilitating functional expansion

---

## Deployment Guide

### Prerequisites
- none
#### System Requirements
- Windows 7/10/11 or Linux
- Python 3.x (3.7+ recommended)
- Minimum 2GB available memory
- 500MB available disk space

#### Required Software
- Python 3.x
- pip (Python Package Manager)
- Git (optional, for source code acquisition)

### Deployment Steps

1. **Obtain Source Code**
   ```bash
   git clone <Your Project Repository URL>  # Or download directly
   cd python-express
   ```

2. **Create and Activate Virtual Environment (Recommended)**
   - On Windows:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - On Linux/macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

   - Exit:
     ```bash
     deactivate
     ```
   

3. **Install Dependent Packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database and Directories**
   - The SQLite database will be automatically created when the system runs for the first time.
   - Ensure the project directory has write permissions.
   - If importing data from Excel, make sure `user.xlsx` and `express.xlsx` exist and are formatted correctly.

5. **Launch the Application**
   ```bash
   python main.py
   ```
## Module Function Introduction

- **main.py**  
  The main entry point of the project, responsible for the main interface and core logic of the system.

- **area_dialog.py**  
  Handles area management related interfaces and logic.

- **dialogs.py**  
  Contains common dialog and popup components.

- **database.py**  
  Database operation module, encapsulating all data read and write operations.

- **qrcode_create.py**  
  Functions related to generating courier QR codes.

- **qrcode_load.py**  
  Functions for recognizing and parsing courier QR codes.

- **style_manager.py**  
  Manages interface styles and themes.

- **totp_manager.py**  
  Handles TOTP security authentication features.

- **requirements.txt**  
  Project dependency list.

- **README.md**  
  Project documentation.


### Deployment Verification

#### Function Verification
- Check if the main interface displays correctly after startup
- Try adding a new user
- Attempt to enter a new courier and generate a QR code
- Test courier query and pickup functions

#### Data Verification
- Verify if the `express.db` file is created correctly
- Confirm data is saved properly
- Ensure QR code images can be generated and scanned normally

### Common Issues

#### Dependency Installation Failures
- Solution: Try updating pip before reinstalling dependencies
- For Windows systems, some packages may require Visual C++ Build Tools

#### QR Code Scanning Abnormalities
- Confirm `opencv-python` and `pyzbar` are correctly installed
- Windows systems may require additional installation of zbar shared libraries

#### Database Access Errors
- Check file system permissions
- Ensure the SQLite database file is not occupied by other programs

#### GUI Display Issues
- Verify Python version compatibility
- Confirm Tkinter is properly installed

#### Chart Display Problems
- Update matplotlib to the latest version
- Check that all necessary graphics library dependencies are installed

### Supplementary Notes

#### Data Backup Recommendations
- Regularly back up the `express.db` database file
- Optionally export data to Excel format for archiving

#### Security Recommendations
- Regularly update Python and dependent library versions
- Protect database file access permissions
- Use in a trusted network environment

#### Performance Optimization
- Periodically clean up historical data
- Timely clear QR code image cache
- Adjust automatic refresh interval based on usage conditions

