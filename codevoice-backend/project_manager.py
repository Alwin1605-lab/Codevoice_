import os
import json
from typing import Dict, List
from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
import zipfile
import tempfile
import shutil
from models.project_models import Project
from models.user_models import User
from auth_dependencies import get_current_user

router = APIRouter()

PROJECT_TEMPLATES = {
    "react_app": {
        "name": "React Application",
        "structure": {
            "package.json": '''{
  "name": "voice-controlled-react-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}''',
            "public/index.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Voice Controlled React App</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>''',
            "src/index.js": '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);''',
            "src/App.js": '''import React, { useState } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('Hello from Voice Controlled IDE!');
  
  return (
    <div className="App">
      <header className="App-header">
        <h1>{message}</h1>
        <button onClick={() => setMessage('Updated via voice!')}>
          Update Message
        </button>
      </header>
    </div>
  );
}

export default App;''',
            "src/App.css": '''.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}'''
        }
    },
    "django_app": {
        "name": "Django Application",
        "structure": {
            "requirements.txt": '''Django>=4.2.0
djangorestframework>=3.14.0''',
            "manage.py": '''#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voice_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)''',
            "voice_project/__init__.py": "",
            "voice_project/settings.py": '''import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key-here'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'voice_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'voice_project.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
''',
            "voice_project/urls.py": '''from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('voice_app.urls')),
]''',
            "voice_app/__init__.py": "",
            "voice_app/models.py": '''from django.db import models

class VoiceCommand(models.Model):
    command = models.CharField(max_length=200)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.command''',
            "voice_app/views.py": '''from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import VoiceCommand

@api_view(['GET', 'POST'])
def voice_commands(request):
    if request.method == 'GET':
        commands = VoiceCommand.objects.all()
        return Response([{'command': c.command, 'response': c.response} for c in commands])
    elif request.method == 'POST':
        command = VoiceCommand.objects.create(
            command=request.data.get('command'),
            response=request.data.get('response')
        )
        return Response({'id': command.id, 'command': command.command})''',
            "voice_app/urls.py": '''from django.urls import path
from . import views

urlpatterns = [
    path('commands/', views.voice_commands, name='voice_commands'),
]'''
        }
    },
    "node_api": {
        "name": "Node.js API",
        "structure": {
            "package.json": '''{
  "name": "voice-controlled-api",
  "version": "1.0.0",
  "description": "Voice controlled Node.js API",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.0",
    "cors": "^2.8.5",
    "dotenv": "^16.0.0",
    "body-parser": "^1.20.0"
  },
  "devDependencies": {
    "nodemon": "^2.0.20"
  }
}''',
            "server.js": '''const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Voice Controlled API is running!' });
});

app.get('/api/status', (req, res) => {
  res.json({ 
    status: 'active',
    timestamp: new Date().toISOString(),
    voice_enabled: true
  });
});

app.post('/api/voice-command', (req, res) => {
  const { command, parameters } = req.body;
  
  // Process voice command here
  res.json({
    received_command: command,
    parameters: parameters,
    processed_at: new Date().toISOString(),
    response: `Processed command: ${command}`
  });
});

app.listen(PORT, () => {
  console.log(`Voice API server running on port ${PORT}`);
});''',
            ".env": '''PORT=3000
NODE_ENV=development''',
            "README.md": '''# Voice Controlled Node.js API

## Installation
```bash
npm install
```

## Usage
```bash
npm start
# or for development
npm run dev
```

## API Endpoints
- GET / - Health check
- GET /api/status - API status
- POST /api/voice-command - Process voice commands
'''
        }
    },
    "python_cli": {
        "name": "Python CLI Tool",
        "structure": {
            "requirements.txt": '''click>=8.0.0
colorama>=0.4.4
pyyaml>=6.0''',
            "main.py": '''#!/usr/bin/env python3
import click
import os
from voice_cli.commands import process_voice_command

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Voice Controlled CLI Tool"""
    pass

@cli.command()
@click.argument('command')
@click.option('--voice', '-v', is_flag=True, help='Enable voice input')
def execute(command, voice):
    """Execute a voice command"""
    if voice:
        click.echo("🎤 Voice mode enabled")
    
    result = process_voice_command(command)
    click.echo(f"✅ Executed: {command}")
    click.echo(f"📋 Result: {result}")

@cli.command()
def status():
    """Show CLI status"""
    click.echo("🔊 Voice CLI is active")
    click.echo(f"📁 Working directory: {os.getcwd()}")

if __name__ == '__main__':
    cli()''',
            "voice_cli/__init__.py": "",
            "voice_cli/commands.py": '''def process_voice_command(command: str) -> str:
    """Process voice commands and return results"""
    
    commands = {
        "hello": "Hello! Voice CLI is working.",
        "status": "System is operational",
        "list": "Listing available commands...",
        "help": "Available commands: hello, status, list, help"
    }
    
    return commands.get(command.lower(), f"Unknown command: {command}")

def execute_file_operation(operation: str, filename: str) -> str:
    """Execute file operations via voice"""
    
    if operation == "create":
        try:
            with open(filename, 'w') as f:
                f.write("# Created via voice command\\n")
            return f"✅ Created file: {filename}"
        except Exception as e:
            return f"❌ Error creating file: {e}"
    
    elif operation == "read":
        try:
            with open(filename, 'r') as f:
                content = f.read()
            return f"📖 Content of {filename}:\\n{content}"
        except Exception as e:
            return f"❌ Error reading file: {e}"
    
    return f"❌ Unknown operation: {operation}"''',
            "setup.py": '''from setuptools import setup, find_packages

setup(
    name="voice-cli",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "colorama>=0.4.4",
        "pyyaml>=6.0"
    ],
    entry_points={
        'console_scripts': [
            'voice-cli=main:cli',
        ],
    },
    author="Voice Controlled IDE",
    description="A voice-controlled command line interface",
)'''
        }
    }
}

class ProjectManager:
    def __init__(self, base_path: str = "projects"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def create_project(self, project_name: str, template_name: str) -> str:
        """Create a new project from template"""
        if template_name not in PROJECT_TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = PROJECT_TEMPLATES[template_name]
        project_path = os.path.join(self.base_path, project_name)
        
        if os.path.exists(project_path):
            raise ValueError(f"Project {project_name} already exists")
        
        os.makedirs(project_path)
        
        # Create all files from template
        for file_path, content in template["structure"].items():
            full_path = os.path.join(project_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return project_path
    
    def list_projects(self) -> List[Dict]:
        """List all projects"""
        projects = []
        for item in os.listdir(self.base_path):
            item_path = os.path.join(self.base_path, item)
            if os.path.isdir(item_path):
                projects.append({
                    "name": item,
                    "path": item_path,
                    "files": self._count_files(item_path)
                })
        return projects
    
    def get_project_structure(self, project_name: str) -> Dict:
        """Get project file structure"""
        project_path = os.path.join(self.base_path, project_name)
        if not os.path.exists(project_path):
            raise ValueError(f"Project {project_name} not found")
        
        return self._get_directory_structure(project_path)
    
    def _count_files(self, path: str) -> int:
        count = 0
        for root, dirs, files in os.walk(path):
            count += len(files)
        return count
    
    def _get_directory_structure(self, path: str) -> Dict:
        """Recursively get directory structure"""
        structure = {"type": "directory", "children": {}}
        
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    structure["children"][item] = self._get_directory_structure(item_path)
                else:
                    structure["children"][item] = {
                        "type": "file",
                        "size": os.path.getsize(item_path)
                    }
        except PermissionError:
            structure["error"] = "Permission denied"
        
        return structure

project_manager = ProjectManager()

@router.get("/templates/")
async def list_project_templates():
    """List available project templates"""
    templates = []
    for key, template in PROJECT_TEMPLATES.items():
        templates.append({
            "id": key,
            "name": template["name"],
            "files_count": len(template["structure"])
        })
    return {"templates": templates}

@router.post("/create-project/")
async def create_project(
    project_name: str = Form(...),
    template_name: str = Form(...)
):
    """Create a new project from template"""
    try:
        project_path = project_manager.create_project(project_name, template_name)
        return {
            "success": True,
            "project_name": project_name,
            "project_path": project_path,
            "template_used": template_name
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects/")
async def list_projects():
    """List all projects"""
    projects = project_manager.list_projects()
    return {"projects": projects}

@router.get("/projects/{project_name}/structure/")
async def get_project_structure(project_name: str):
    """Get project file structure"""
    try:
        structure = project_manager.get_project_structure(project_name)
        return {"project_name": project_name, "structure": structure}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/projects/{project_name}/files/{file_path:path}")
async def get_project_file(project_name: str, file_path: str):
    """Get content of a specific file"""
    try:
        full_path = os.path.join(project_manager.base_path, project_name, file_path)
        
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "project_name": project_name,
            "file_path": file_path,
            "content": content,
            "size": os.path.getsize(full_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_name}/files/{file_path:path}")
async def update_project_file(
    project_name: str,
    file_path: str,
    content: str = Form(...)
):
    """Update content of a specific file"""
    try:
        full_path = os.path.join(project_manager.base_path, project_name, file_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "project_name": project_name,
            "file_path": file_path,
            "message": "File updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_name}/download/")
async def download_project(project_name: str, current_user: User = Depends(get_current_user)):
    """Download project as ZIP file from MongoDB"""
    try:
        # Find the project in MongoDB by name and user
        project = await Project.find_one(
            Project.name == project_name,
            Project.user_id == str(current_user.id)
        )
        
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        # Create temporary directory for project files
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = os.path.join(temp_dir, project_name)
            os.makedirs(project_path, exist_ok=True)
            
            # Generate files from project structure
            if project.project_structure and 'files' in project.project_structure:
                files_data = project.project_structure['files']
                for file_path, file_info in files_data.items():
                    full_path = os.path.join(project_path, file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    content = file_info.get('content', '') if isinstance(file_info, dict) else file_info
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
            
            # Create folders from project structure
            if project.project_structure and 'folders' in project.project_structure:
                for folder in project.project_structure['folders']:
                    folder_path = os.path.join(project_path, folder)
                    os.makedirs(folder_path, exist_ok=True)
            
            # Add README with setup instructions
            if project.setup_instructions:
                readme_path = os.path.join(project_path, 'README.md')
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {project.name}\n\n")
                    f.write(f"{project.description}\n\n")
                    f.write("## Setup Instructions\n\n")
                    for i, instruction in enumerate(project.setup_instructions, 1):
                        f.write(f"{i}. {instruction}\n")
                    
                    if project.environment_variables:
                        f.write("\n## Environment Variables\n\n")
                        for var, desc in project.environment_variables.items():
                            f.write(f"- `{var}`: {desc}\n")
            
            # Create ZIP file
            zip_path = tempfile.mktemp(suffix='.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_path)
                        zipf.write(file_path, arcname)
            
            return FileResponse(
                path=zip_path,
                media_type='application/zip',
                filename=f"{project_name}.zip",
                headers={"Content-Disposition": f"attachment; filename={project_name}.zip"}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Download error: Failed to download project '{project_name}': {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to download project: {str(e)}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied accessing project '{project_name}'")
    except Exception as e:
        import traceback
        error_msg = f"Failed to download project '{project_name}': {str(e)}"
        print(f"Download error: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)