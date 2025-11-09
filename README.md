# INT6127PythonGroupProject
# Express Management System
Topic: Intelligent Management System for Campus Express Stations Based on Python (GUI)

### Members: 

Xiao Boersheng 11669576

Li Yueming 11654923

Zhao Zihan 11669318

Zhen Tianying 11654478

Zhang Fangzhe 11654894 @metroman


### Background:

With the rapid development of the e-commerce industry, the national express delivery volume exceeded 120 billion pieces in 2024, making "last-mile delivery" a critical link in the logistics chain. Due to issues such as irregular delivery times and scattered addresses within campuses, campus delivery stations have become the mainstream solution to address the last-mile delivery challenge. According to the "2024 China Express Terminal Service Development Report", over 60% of packages are delivered through these stations, with an average daily processing volume of 300-800 pieces, and even exceeding 1,000 pieces during peak hours at campus stations.


### Plan / Solution：

In high-volume operational environments, express delivery stations increasingly require "efficient management tools" that address three core needs:

First, enabling staff to quickly complete parcel registration, inventory classification, and delivery verification; Second, providing users with clear pickup guidance; Third, efficiently integrating operational data (such as daily shipment volumes and statistics on delayed parcels). These requirements collectively form the practical application scenarios of the "Express Delivery Station Management System".

Most campus parcel stations still rely on manual registration and paper-based ledgers or "Excel spreadsheets" for management, creating operational pain points that severely impact efficiency and user experience.

Low efficiency: Manually entering parcel tracking numbers (13-18 digits) and recipient information takes an average of 30 seconds per parcel, often causing congestion during peak hours. Manual verification of names and phone numbers during pickup leads to user queues exceeding 5 minutes.

Inventory chaos: Packages are stacked by delivery time without proper categorization (e.g., "fresh produce", "bulk items", "delayed shipments"). This causes staff to spend time locating packages and increases the risk of misdelivery or loss (industry average loss rate is approximately 1.2%). Data is missing. Daily or weekly delivery volumes or delayed packages (i.e., packages that have not been picked up for more than 3 days) cannot be automatically calculated, making it difficult to optimize operational strategies (such as adjusting staffing during pickup peaks).

Poor user experience: Users cannot check the delivery status in real time and need to repeatedly consult the staff. If the information is wrong when picking up the package (such as entering the wrong phone number), disputes may occur.

The system will digitize the core processes of the station through Python programming, including "package registration, inventory management, pickup verification and data statistics", so as to directly solve the above efficiency and experience problems.



## Project Introduction
The Express Management System is a lightweight courier receiving and dispatching management application developed with Python. It is specifically designed for small courier service points, campus courier stations, and similar scenarios. The system adopts a graphical user interface (GUI) and supports core functions such as courier warehousing, pickup, and query. It also integrates QR code generation and scanning capabilities to achieve efficient management of courier information and convenient pickup services.

### Core Features
- Courier Warehousing Management: Automatically generates waybill numbers and pickup codes
- QR Code Integration: Supports generation and scanning of courier information QR codes
- Courier Pickup Management: Supports pickup code verification and status updates
- User Management: Manages sender and recipient information
- Data Statistics: Provides visual statistics on the number of in-stock couriers and location distribution
- Real-time Search: Supports multi-condition courier information query

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

