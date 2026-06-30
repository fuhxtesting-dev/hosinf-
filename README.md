# FX HOSTING - Ultimate VPS Management Panel v3.0.0

![FX HOSTING](https://img.shields.io/badge/FX-HOSTING-brightgreen)
![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-yellow)
![Flask](https://img.shields.io/badge/flask-3.0.0-red)

## Features

### Server Management
- Create, start, stop, restart, delete servers
- Clone existing servers
- Auto-restart with configurable intervals (30s to 24h)
- Server grouping and tagging
- Server notes and descriptions
- Environment variables support
- Real-time log monitoring
- Console input for running servers

### File Manager
- Upload and download files
- Create, edit, delete files and folders
- Rename files
- Extract ZIP and 7Z archives
- Syntax-highlighted file editor
- Breadcrumb navigation

### Terminal
- Full system terminal access
- Command history with arrow keys
- Real-time output
- Admin-only access control

### Process Monitor
- View all system processes
- CPU and RAM usage per process
- Kill processes (admin only)

### Package Manager
- Install/uninstall packages
- Support: PIP, NPM, APT, PKG, GEM
- Per-server package management

### Backup Manager
- Create backups of servers
- Restore from backups
- List all backups
- Delete old backups

### Telegram Bot Hosting
- Deploy Telegram bots automatically
- AIogram 3.x framework
- Built-in commands: /start, /help, /ping, /uptime, /status, /info

### Port Scanner
- View all open ports
- Process information per port
- Connection status tracking

### System Information
- Real-time CPU, RAM, Disk stats
- Network information
- System uptime
- Process count
- Load average

### Themes (20 Beautiful Themes)
1. Matrix Green
2. Night Blue
3. Ocean Blue
4. Sunset Orange
5. Blood Red
6. Neon Purple
7. Cyber Cyan
8. Vapor Pink
9. Royal Gold
10. Silver Grey
11. Midnight
12. Emerald
13. Ruby
14. Sapphire
15. Amber
16. Amethyst
17. Tokyo Night
18. Dracula
19. Monokai
20. Nord

### Security
- Dual password system (Admin/User)
- Password change functionality
- Activity logging
- Admin-only features (terminal, process kill)

## Installation

### For Termux
```bash
# Update packages
pkg update && pkg upgrade -y

# Install required packages
pkg install python git -y

# Clone or extract FX HOSTING
cd FX_HOSTING

# Install Python dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### For Linux VPS
```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip -y

# Navigate to FX HOSTING directory
cd FX_HOSTING

# Install requirements
pip3 install -r requirements.txt

# Run the application
python3 app.py
```

## Default Passwords

| Role | Password |
|------|----------|
| Admin (Secret) | `FXHOSTING2024` |
| User | `admin` |

## Access

After starting the application, open your browser and navigate to:
```
http://localhost:5000
```

On Android (Termux), you can also access via:
```
http://127.0.0.1:5000
```

## API Endpoints

### Server Management
- `POST /api/server/create` - Create new server
- `POST /api/server/upload` - Create server with file upload
- `POST /api/server/<id>/start` - Start server
- `POST /api/server/<id>/stop` - Stop server
- `POST /api/server/<id>/restart` - Restart server
- `POST /api/server/<id>/delete` - Delete server
- `POST /api/server/<id>/clone` - Clone server
- `GET /api/server/<id>/logs` - Get server logs
- `POST /api/server/<id>/input` - Send command to server
- `POST /api/server/<id>/clear_logs` - Clear server logs
- `GET/POST /api/server/<id>/config` - Get/Set server config

### File Management
- `GET /api/files/<server_id>` - List files
- `GET /api/files/<server_id>/content` - Get file content
- `POST /api/files/<server_id>/save` - Save file content
- `POST /api/files/<server_id>/create` - Create new file
- `POST /api/files/<server_id>/mkdir` - Create folder
- `POST /api/files/<server_id>/rename` - Rename file
- `POST /api/files/<server_id>/delete` - Delete file
- `POST /api/files/<server_id>/upload` - Upload file
- `GET /api/files/<server_id>/download` - Download file
- `POST /api/files/<server_id>/extract` - Extract archive

### Package Management
- `POST /api/packages/<server_id>/install` - Install package
- `POST /api/packages/<server_id>/uninstall` - Uninstall package
- `GET /api/packages/<server_id>/list` - List packages

### Backup Management
- `POST /api/backup/<server_id>/create` - Create backup
- `POST /api/backup/<server_id>/restore` - Restore backup
- `GET /api/backup/list` - List all backups
- `POST /api/backup/delete` - Delete backup

### System
- `GET /api/system/info` - System information
- `GET /api/system/stats` - System stats
- `GET /api/system/processes` - List processes
- `POST /api/system/kill_process` - Kill process
- `GET /api/system/ports` - List ports

### Terminal
- `POST /api/terminal/execute` - Execute command

### Telegram
- `POST /api/telegram/deploy` - Deploy Telegram bot

### Settings
- `GET/POST /api/settings` - Get/Update settings
- `POST /api/settings/password` - Change password

### Activity
- `GET /api/activity` - Get activity log

## File Structure
```
FX_HOSTING/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── config.json            # App configuration (auto-created)
├── servers_db.json        # Server database (auto-created)
├── activity_log.json      # Activity log (auto-created)
├── templates/
│   ├── index.html         # Main dashboard
│   └── login.html         # Login page
├── static/
│   ├── css/
│   ├── js/
│   └── img/
└── user_files/            # Server files (auto-created)
```

## Changelog

### v3.0.0 (2024)
- Complete UI redesign with 20 themes
- Server start date display
- Terminal emulator
- Process monitor
- Backup/Restore system
- Port scanner
- Telegram bot auto-deploy
- File editor with syntax highlighting
- Server cloning
- Activity logging
- Real-time stats updates
- Search and filter servers
- Server groups and tags
- Environment variables
- Quick actions dashboard

## Credits

**FX HOSTING** - Ultimate VPS Management Panel
- Optimized for Termux and Linux VPS
- Built with Flask & Tailwind CSS

## License

This project is for educational purposes.
