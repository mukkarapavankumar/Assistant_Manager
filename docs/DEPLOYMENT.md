# Deployment Guide - Assistant Manager

This guide covers deploying Assistant Manager for production use, including packaging, distribution, and maintenance.

## 🎯 Deployment Overview

Assistant Manager is designed as a **local-first desktop application** with the following deployment characteristics:

- **Desktop Application**: Packaged as a native Windows executable
- **Local Database**: SQLite database stored locally
- **Local LLM**: Ollama running on the same machine
- **Email Integration**: Direct Outlook COM integration
- **GitHub Publishing**: Optional cloud integration for board publishing

## 📦 Production Build

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.9+** and pip
- **Ollama** installed and configured
- **Microsoft Outlook** installed and configured
- **Git** for version control

### Build Process

1. **Prepare Environment**
```bash
# Clone repository
git clone <repository-url>
cd assistant-manager

# Install dependencies
npm run setup
```

2. **Configure Production Settings**
```bash
# Backend configuration
cd backend
cp .env.example .env.production

# Edit production settings
nano .env.production
```

**Production Environment Variables:**
```bash
# Application
APP_NAME=Assistant Manager
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///data/assistant_manager.db

# LLM Configuration
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=llama3.2

# Email Configuration
OUTLOOK_ENABLED=true
EMAIL_CHECK_INTERVAL=300

# GitHub Configuration (optional)
GITHUB_TOKEN=your_production_token
GITHUB_REPO=your_org/team-kanban

# Security
SECRET_KEY=your_secure_production_key
```

3. **Build Frontend**
```bash
npm run build
```

4. **Package Backend**
```bash
cd backend
pip install pyinstaller
pyinstaller --onefile --add-data "app;app" --hidden-import=app.main app/main.py
```

## 🖥️ Desktop Application Packaging

### Using Electron (Recommended)

1. **Install Electron Builder**
```bash
npm install --save-dev electron electron-builder
```

2. **Create Electron Main Process**
```javascript
// electron/main.js
const { app, BrowserWindow, spawn } = require('electron');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;
let backendProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    icon: path.join(__dirname, 'assets/icon.png'),
    titleBarStyle: 'default',
    show: false,
  });

  // Start backend process
  if (!isDev) {
    const backendPath = path.join(process.resourcesPath, 'backend', 'main.exe');
    backendProcess = spawn(backendPath, [], {
      stdio: 'pipe',
      cwd: path.dirname(backendPath),
    });
  }

  // Load frontend
  const startUrl = isDev 
    ? 'http://localhost:5173' 
    : `file://${path.join(__dirname, '../dist/index.html')}`;
  
  mainWindow.loadURL(startUrl);
  
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
    if (backendProcess) {
      backendProcess.kill();
    }
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
```

3. **Configure Electron Builder**
```json
// package.json
{
  "main": "electron/main.js",
  "scripts": {
    "electron": "electron .",
    "electron:dev": "NODE_ENV=development electron .",
    "build:electron": "electron-builder",
    "dist": "npm run build && npm run build:electron"
  },
  "build": {
    "appId": "com.company.assistant-manager",
    "productName": "Assistant Manager",
    "directories": {
      "output": "dist-electron"
    },
    "files": [
      "dist/**/*",
      "electron/**/*",
      "node_modules/**/*"
    ],
    "extraResources": [
      {
        "from": "backend/dist/main.exe",
        "to": "backend/main.exe"
      }
    ],
    "win": {
      "target": "nsis",
      "icon": "electron/assets/icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
```

4. **Build Distribution**
```bash
npm run dist
```

### Alternative: Standalone Executable

For simpler deployment without Electron:

1. **Create Launcher Script**
```python
# launcher.py
import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def main():
    # Start backend
    backend_path = Path(__file__).parent / "backend" / "main.exe"
    backend_process = subprocess.Popen([str(backend_path)])
    
    # Wait for backend to start
    time.sleep(3)
    
    # Open browser
    webbrowser.open("http://localhost:8000")
    
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        backend_process.terminate()

if __name__ == "__main__":
    main()
```

2. **Package with PyInstaller**
```bash
pyinstaller --onefile --windowed launcher.py
```

## 🚀 Installation Package

### NSIS Installer (Windows)

1. **Install NSIS**
Download and install NSIS from https://nsis.sourceforge.io/

2. **Create Installer Script**
```nsis
; assistant-manager-installer.nsi
!define APP_NAME "Assistant Manager"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Your Company"
!define APP_URL "https://your-website.com"
!define APP_EXECUTABLE "AssistantManager.exe"

; Include Modern UI
!include "MUI2.nsh"

; General
Name "${APP_NAME}"
OutFile "AssistantManagerSetup.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer Sections
Section "Main Application" SecMain
  SetOutPath "$INSTDIR"
  
  ; Copy application files
  File /r "dist\*.*"
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXECUTABLE}"
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXECUTABLE}"
  
  ; Write registry keys
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

; Uninstaller Section
Section "Uninstall"
  ; Remove files
  RMDir /r "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd
```

3. **Build Installer**
```bash
makensis assistant-manager-installer.nsi
```

## 🔧 Configuration Management

### Application Configuration

1. **Configuration File Location**
```
Windows: %APPDATA%\AssistantManager\config.json
```

2. **Default Configuration**
```json
{
  "app": {
    "name": "Assistant Manager",
    "version": "1.0.0",
    "autoStart": false,
    "minimizeToTray": true
  },
  "database": {
    "path": "%APPDATA%\\AssistantManager\\data\\assistant_manager.db",
    "backupEnabled": true,
    "backupInterval": "daily"
  },
  "llm": {
    "host": "http://localhost:11434",
    "model": "llama3.2",
    "timeout": 30
  },
  "email": {
    "enabled": true,
    "checkInterval": 300,
    "maxFollowUps": 3
  },
  "github": {
    "enabled": false,
    "autoPublish": false
  },
  "ui": {
    "theme": "system",
    "language": "en",
    "notifications": true
  }
}
```

### Environment-Specific Configurations

1. **Development**
```json
{
  "debug": true,
  "logLevel": "DEBUG",
  "database": {
    "path": "./dev_assistant_manager.db"
  }
}
```

2. **Production**
```json
{
  "debug": false,
  "logLevel": "INFO",
  "database": {
    "path": "%APPDATA%\\AssistantManager\\data\\assistant_manager.db"
  }
}
```

## 📊 Monitoring and Logging

### Application Logging

1. **Log Configuration**
```python
# backend/app/core/logging.py
import logging
import logging.handlers
from pathlib import Path
import os

def setup_production_logging():
    # Create logs directory
    if os.name == 'nt':  # Windows
        log_dir = Path(os.environ['APPDATA']) / 'AssistantManager' / 'logs'
    else:
        log_dir = Path.home() / '.assistant-manager' / 'logs'
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                log_dir / 'assistant_manager.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
```

2. **Health Monitoring**
```python
# backend/app/services/health_monitor.py
import psutil
import asyncio
from datetime import datetime

class HealthMonitor:
    async def get_system_health(self):
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "process_count": len(psutil.pids())
        }
```

### Error Reporting

1. **Crash Reporting**
```python
# backend/app/core/error_handler.py
import traceback
import logging
from pathlib import Path

def handle_crash(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Log the crash
    logging.critical(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    # Save crash dump
    crash_dir = Path(os.environ['APPDATA']) / 'AssistantManager' / 'crashes'
    crash_dir.mkdir(parents=True, exist_ok=True)
    
    crash_file = crash_dir / f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(crash_file, 'w') as f:
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)

# Set as default exception handler
sys.excepthook = handle_crash
```

## 🔄 Updates and Maintenance

### Auto-Update System

1. **Update Checker**
```python
# backend/app/services/update_service.py
import requests
import json
from packaging import version

class UpdateService:
    def __init__(self, current_version: str):
        self.current_version = current_version
        self.update_url = "https://api.github.com/repos/your-org/assistant-manager/releases/latest"
    
    async def check_for_updates(self):
        try:
            response = requests.get(self.update_url)
            release_data = response.json()
            
            latest_version = release_data['tag_name'].lstrip('v')
            
            if version.parse(latest_version) > version.parse(self.current_version):
                return {
                    "update_available": True,
                    "latest_version": latest_version,
                    "download_url": release_data['assets'][0]['browser_download_url'],
                    "release_notes": release_data['body']
                }
            
            return {"update_available": False}
        
        except Exception as e:
            logging.error(f"Update check failed: {e}")
            return {"update_available": False, "error": str(e)}
```

2. **Update Installation**
```python
# backend/app/services/installer.py
import subprocess
import tempfile
import requests
from pathlib import Path

class UpdateInstaller:
    async def download_and_install(self, download_url: str):
        # Download update
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as temp_file:
            response = requests.get(download_url, stream=True)
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            
            installer_path = temp_file.name
        
        # Run installer
        subprocess.Popen([installer_path, '/S'], shell=True)
        
        # Exit current application
        sys.exit(0)
```

### Database Migrations

1. **Migration System**
```python
# backend/app/core/migrations.py
from peewee_migrate import Router
from app.models.database import db

class MigrationManager:
    def __init__(self):
        self.router = Router(db, migrate_dir='migrations')
    
    def run_migrations(self):
        self.router.run()
    
    def create_migration(self, name: str):
        self.router.create(name)
```

2. **Backup Before Migration**
```python
# backend/app/core/backup.py
import shutil
from pathlib import Path
from datetime import datetime

def backup_database():
    db_path = Path("assistant_manager.db")
    if db_path.exists():
        backup_name = f"assistant_manager_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = db_path.parent / "backups" / backup_name
        backup_path.parent.mkdir(exist_ok=True)
        shutil.copy2(db_path, backup_path)
        return backup_path
    return None
```

## 🔒 Security Considerations

### Application Security

1. **Code Signing** (Windows)
```bash
# Sign the executable
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com AssistantManager.exe
```

2. **Antivirus Whitelisting**
Create documentation for IT departments:

```markdown
# Antivirus Whitelist Instructions

Assistant Manager may be flagged by antivirus software due to:
- Email automation capabilities
- Local file system access
- Network communication

Recommended whitelist entries:
- Application: AssistantManager.exe
- Directory: %PROGRAMFILES%\Assistant Manager\
- Network: localhost:8000, localhost:11434
```

### Data Security

1. **Database Encryption**
```python
# backend/app/core/encryption.py
from cryptography.fernet import Fernet
import base64

class DatabaseEncryption:
    def __init__(self, key: bytes = None):
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

2. **Secure Configuration Storage**
```python
# backend/app/core/secure_config.py
import keyring
from cryptography.fernet import Fernet

class SecureConfig:
    def store_secret(self, key: str, value: str):
        keyring.set_password("AssistantManager", key, value)
    
    def get_secret(self, key: str) -> str:
        return keyring.get_password("AssistantManager", key)
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Code signed and verified
- [ ] Documentation updated
- [ ] Configuration validated
- [ ] Dependencies verified
- [ ] Security scan completed

### Deployment
- [ ] Build artifacts created
- [ ] Installer tested
- [ ] Installation guide updated
- [ ] Release notes prepared
- [ ] Distribution channels ready

### Post-Deployment
- [ ] Installation verified
- [ ] Basic functionality tested
- [ ] Monitoring configured
- [ ] Support documentation available
- [ ] Feedback collection setup

## 🆘 Troubleshooting

### Common Deployment Issues

1. **Ollama Not Found**
```
Error: Failed to connect to Ollama
Solution: Ensure Ollama is installed and running on localhost:11434
```

2. **Outlook Integration Failed**
```
Error: COM object creation failed
Solution: Ensure Outlook is installed and user has proper permissions
```

3. **Database Migration Failed**
```
Error: Migration failed
Solution: Restore from backup and retry with manual migration
```

4. **Port Already in Use**
```
Error: Port 8000 already in use
Solution: Configure alternative port in settings or stop conflicting service
```

### Support Resources

- **Installation Guide**: docs/INSTALLATION.md
- **User Manual**: docs/USER_GUIDE.md
- **API Documentation**: docs/API.md
- **Troubleshooting**: docs/TROUBLESHOOTING.md
- **Support Email**: support@your-company.com

## 📈 Performance Optimization

### Production Optimizations

1. **Database Optimization**
```sql
-- Create indexes for better performance
CREATE INDEX idx_tasks_status_assignee ON tasks(status, assignee_id);
CREATE INDEX idx_email_threads_member_status ON email_threads(team_member_id, status);
CREATE INDEX idx_agent_activities_timestamp ON agent_activities(created_at DESC);
```

2. **Memory Management**
```python
# backend/app/core/performance.py
import gc
import psutil

class PerformanceManager:
    def optimize_memory(self):
        # Force garbage collection
        gc.collect()
        
        # Monitor memory usage
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 80:
            logging.warning(f"High memory usage: {memory_percent}%")
```

3. **Caching Strategy**
```python
# backend/app/core/cache.py
from functools import lru_cache
import asyncio

class CacheManager:
    @lru_cache(maxsize=100)
    def get_team_member(self, member_id: int):
        return TeamMember.get_by_id(member_id)
    
    @lru_cache(maxsize=50)
    def get_email_template(self, template_id: int):
        return EmailTemplate.get_by_id(template_id)
```

This deployment guide provides comprehensive instructions for packaging, distributing, and maintaining Assistant Manager in production environments.