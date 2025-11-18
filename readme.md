# Express Management System

This is a desktop application for managing express packages, built with Python and Tkinter.

## What the project does

This project is a comprehensive Express Management System designed to streamline the process of package handling. It provides a graphical user interface for users to manage express package information. Key features include adding new packages, updating existing package statuses, viewing package details, and deleting packages. The system supports role-based access control, with distinct functionalities for administrators and regular users. A standout feature is the integration of QR code generation for each package, allowing for easy tracking and identification. The system also incorporates TOTP two-factor authentication to ensure secure access, particularly for administrative functions.

## Why the project is useful

This system offers a practical solution for small-scale logistics or internal package management within an organization. It replaces manual, paper-based tracking with an efficient, digitized workflow. The use of QR codes simplifies package identification and reduces human error. By providing different user roles, it ensures that sensitive operations are restricted to authorized personnel. The inclusion of data visualization helps in analyzing package flow and identifying trends. Overall, it enhances efficiency, improves accuracy, and increases the security of the package management process.

## How to use the project

1. Clone the repository:

```powershell
git clone <repository-url>
cd <repository-folder>
```

2. Install dependencies (PowerShell):

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Required libraries (examples; see `requirements.txt` for exact versions): `pandas`, `qrcode`, `opencv-python`, `pyzbar`, `Pillow`, `matplotlib`, `pyotp`, `ttkthemes`.

3. Run the application:

```powershell
python main.py
```

4. Login: The application will present a login screen. You can log in as an administrator or a regular user.

5. Functionality:
	- Admin: Can view all packages, add new packages, edit package information, delete packages, and manage user-related settings.
	- User: Can view packages associated with them and check their status.
	- QR Codes: When a package is added or viewed, a QR code is generated. This can be saved or scanned directly from the screen.

## Where to get help

If you encounter any issues or have questions about the project, please open an issue on the project's GitHub repository. Provide a detailed description of the problem, including steps to reproduce it, and any relevant error messages.

## Who maintains and contributes to the project

This project is maintained by the initial developers. We welcome contributions from the community. If you would like to contribute, please fork the repository, create a new branch for your feature or bug fix, and submit a pull request. Please make sure to follow the existing code style and add relevant documentation for your changes.

## Optional: Running and debugging tips

- If you see GUI errors on startup, run `python main.py` from a terminal to view traceback messages.
- For development, consider creating a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## License

This project does not include a license file by default. Add a `LICENSE` if you want to specify reuse terms (for example, MIT License).

---

If you want, I can also add a short `CONTRIBUTING.md`, include example screenshots, or extract a minimal `requirements.txt` with pinned versions. Tell me which you'd prefer next.
