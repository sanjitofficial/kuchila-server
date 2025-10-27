# KUCHILA SERVER 🌍

A lightweight, Python-based local web server that intelligently detects whether a directory should be served as a static web app or a file manager.
Designed for developers who need quick local hosting or secure LAN sharing of files with thumbnail previews and bulk download support.

---
## Installation

#### Clone the repository
```sh
git clone https://github.com/<your-username>/kuchila-server.git
cd kuchila-server
```

#### Run the server
```sh
python kuchila_server.py
```

The script will:

- Automatically create and activate a virtual environment (if not present).

- Check for Flask and install it if missing.

- Launch the server automatically once setup is complete.

### Usage

When prompted, enter the full path to the directory you want to share or host.

#### The server will automatically:

- Detect if the folder is a web app (index.html present).
- → You’ll be asked whether to “Run Web App” or “View as Folder.”

Otherwise, it launches the File Manager mode.

### Access the URLs displayed in your terminal:
```sh
Local URL:    http://127.0.0.1:8000
Network URL:  http://<your-local-ip>:8000
```

Press CTRL + C anytime to stop the server.
---
### Requirements

- Python 3.8 or higher

- Internet connection (for first-time dependency setup)

All dependencies are automatically handled by the script.
---

### Example Use Cases

- Instantly host a front-end project with index.html

- Share local files securely over LAN

- Access and download multiple files remotely from another device

- Quick local preview server for testing static sites

###License

This project is open-source and available under the MIT License.
You’re free to modify, distribute, or integrate it into your own tools.
