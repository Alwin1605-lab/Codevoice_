import os
import json
import subprocess
from typing import Dict, List, Optional
from fastapi import APIRouter, Form, HTTPException
from pathlib import Path
import asyncio

router = APIRouter()

class VoiceCommandProcessor:
    def __init__(self):
        self.command_mappings = {
            # File operations
            "create file": self._create_file,
            "new file": self._create_file,
            "save file": self._save_file,
            "save": self._save_file,
            "open file": self._open_file,
            "load file": self._open_file,
            "delete file": self._delete_file,
            "rename file": self._rename_file,
            
            # Code operations
            "compile": self._compile_code,
            "compile code": self._compile_code,
            "run": self._run_code,
            "run code": self._run_code,
            "run program": self._run_code,
            "execute": self._run_code,
            "stop execution": self._stop_execution,
            "stop": self._stop_execution,
            
            # Editor operations
            "clear editor": self._clear_editor,
            "clear": self._clear_editor,
            "undo": self._undo,
            "redo": self._redo,
            "copy": self._copy,
            "paste": self._paste,
            "cut": self._cut,
            "select all": self._select_all,
            
            # Project operations
            "new project": self._new_project,
            "open project": self._open_project,
            "save project": self._save_project,
            "build project": self._build_project,
            
            # Language switching
            "switch to python": self._switch_language,
            "switch to javascript": self._switch_language,
            "switch to java": self._switch_language,
            "switch to cpp": self._switch_language,
            "switch to c": self._switch_language,
            
            # Navigation
            "go to line": self._go_to_line,
            "find": self._find_text,
            "replace": self._replace_text,
            "next": self._find_next,
            "previous": self._find_previous,
            
            # IDE controls
            "toggle terminal": self._toggle_terminal,
            "toggle sidebar": self._toggle_sidebar,
            "zoom in": self._zoom_in,
            "zoom out": self._zoom_out,
            "reset zoom": self._reset_zoom,
            
            # Voice controls
            "start listening": self._start_listening,
            "stop listening": self._stop_listening,
            "mute": self._mute_voice,
            "unmute": self._unmute_voice,
            
            # Help and information
            "help": self._show_help,
            "show commands": self._show_commands,
            "status": self._show_status,
            "version": self._show_version
        }
        
        self.current_execution = None
        self.listening_active = True
        self.voice_muted = False
    
    async def process_command(self, command: str, parameters: Dict = None) -> Dict:
        """Process a voice command and return result"""
        command = command.lower().strip()
        parameters = parameters or {}
        
        # Check if voice is muted
        if self.voice_muted and command not in ["unmute", "help"]:
            return {
                "success": False,
                "message": "Voice commands are muted. Say 'unmute' to activate.",
                "command": command
            }
        
        # Find matching command
        handler = None
        for cmd_pattern, cmd_handler in self.command_mappings.items():
            if cmd_pattern in command or command.startswith(cmd_pattern):
                handler = cmd_handler
                break
        
        if not handler:
            return {
                "success": False,
                "message": f"Unknown command: '{command}'. Say 'help' for available commands.",
                "command": command,
                "suggestions": self._get_command_suggestions(command)
            }
        
        try:
            result = await handler(command, parameters)
            return {
                "success": True,
                "command": command,
                "result": result,
                "parameters": parameters
            }
        except Exception as e:
            return {
                "success": False,
                "command": command,
                "error": str(e),
                "parameters": parameters
            }
    
    def _get_command_suggestions(self, command: str) -> List[str]:
        """Get command suggestions based on similarity"""
        suggestions = []
        command_words = command.split()
        
        for cmd in self.command_mappings.keys():
            cmd_words = cmd.split()
            common_words = set(command_words) & set(cmd_words)
            if common_words:
                suggestions.append(cmd)
        
        return suggestions[:3]  # Return top 3 suggestions
    
    # File Operations
    async def _create_file(self, command: str, params: Dict) -> str:
        filename = params.get('filename', 'untitled.py')
        content = params.get('content', '# New file created via voice command\n')
        
        try:
            with open(filename, 'w') as f:
                f.write(content)
            return f"Created file: {filename}"
        except Exception as e:
            raise Exception(f"Failed to create file: {e}")
    
    async def _save_file(self, command: str, params: Dict) -> str:
        filename = params.get('filename')
        content = params.get('content', '')
        
        if not filename:
            return "Please specify a filename to save"
        
        try:
            with open(filename, 'w') as f:
                f.write(content)
            return f"Saved file: {filename}"
        except Exception as e:
            raise Exception(f"Failed to save file: {e}")
    
    async def _open_file(self, command: str, params: Dict) -> str:
        filename = params.get('filename')
        
        if not filename:
            return "Please specify a filename to open"
        
        if not os.path.exists(filename):
            return f"File not found: {filename}"
        
        try:
            with open(filename, 'r') as f:
                content = f.read()
            return f"Opened file: {filename} ({len(content)} characters)"
        except Exception as e:
            raise Exception(f"Failed to open file: {e}")
    
    async def _delete_file(self, command: str, params: Dict) -> str:
        filename = params.get('filename')
        
        if not filename:
            return "Please specify a filename to delete"
        
        if not os.path.exists(filename):
            return f"File not found: {filename}"
        
        try:
            os.remove(filename)
            return f"Deleted file: {filename}"
        except Exception as e:
            raise Exception(f"Failed to delete file: {e}")
    
    async def _rename_file(self, command: str, params: Dict) -> str:
        old_name = params.get('old_name')
        new_name = params.get('new_name')
        
        if not old_name or not new_name:
            return "Please specify both old and new filenames"
        
        try:
            os.rename(old_name, new_name)
            return f"Renamed {old_name} to {new_name}"
        except Exception as e:
            raise Exception(f"Failed to rename file: {e}")
    
    # Code Operations
    async def _compile_code(self, command: str, params: Dict) -> str:
        # This would integrate with the existing compile_api.py
        language = params.get('language', 'python')
        code = params.get('code', '')
        
        if not code:
            return "No code provided for compilation"
        
        # Here you would call the existing compilation system
        return f"Compiling {language} code... (integration with compile_api.py needed)"
    
    async def _run_code(self, command: str, params: Dict) -> str:
        code = params.get('code', '')
        language = params.get('language', 'python')
        
        if not code:
            return "No code provided for execution"
        
        # This would integrate with the existing run_code_utils.py
        return f"Running {language} code... (integration with run_code_utils.py needed)"
    
    async def _stop_execution(self, command: str, params: Dict) -> str:
        if self.current_execution:
            try:
                self.current_execution.terminate()
                self.current_execution = None
                return "Execution stopped"
            except:
                return "Failed to stop execution"
        else:
            return "No active execution to stop"
    
    # Editor Operations
    async def _clear_editor(self, command: str, params: Dict) -> str:
        return "Editor cleared"
    
    async def _undo(self, command: str, params: Dict) -> str:
        return "Undo performed"
    
    async def _redo(self, command: str, params: Dict) -> str:
        return "Redo performed"
    
    async def _copy(self, command: str, params: Dict) -> str:
        return "Text copied to clipboard"
    
    async def _paste(self, command: str, params: Dict) -> str:
        return "Text pasted from clipboard"
    
    async def _cut(self, command: str, params: Dict) -> str:
        return "Text cut to clipboard"
    
    async def _select_all(self, command: str, params: Dict) -> str:
        return "All text selected"
    
    # Project Operations
    async def _new_project(self, command: str, params: Dict) -> str:
        project_name = params.get('name', 'new_project')
        template = params.get('template', 'python_cli')
        return f"Creating new project: {project_name} with template: {template}"
    
    async def _open_project(self, command: str, params: Dict) -> str:
        project_name = params.get('name')
        if not project_name:
            return "Please specify project name to open"
        return f"Opening project: {project_name}"
    
    async def _save_project(self, command: str, params: Dict) -> str:
        return "Project saved successfully"
    
    async def _build_project(self, command: str, params: Dict) -> str:
        return "Building project..."
    
    # Language Operations
    async def _switch_language(self, command: str, params: Dict) -> str:
        if "python" in command:
            language = "python"
        elif "javascript" in command:
            language = "javascript"
        elif "java" in command:
            language = "java"
        elif "cpp" in command:
            language = "cpp"
        elif "c" in command:
            language = "c"
        else:
            language = params.get('language', 'python')
        
        return f"Switched to {language} mode"
    
    # Navigation Operations
    async def _go_to_line(self, command: str, params: Dict) -> str:
        line_number = params.get('line', 1)
        return f"Moved to line {line_number}"
    
    async def _find_text(self, command: str, params: Dict) -> str:
        search_text = params.get('text', '')
        if not search_text:
            return "Please specify text to find"
        return f"Searching for: {search_text}"
    
    async def _replace_text(self, command: str, params: Dict) -> str:
        find_text = params.get('find', '')
        replace_text = params.get('replace', '')
        return f"Replacing '{find_text}' with '{replace_text}'"
    
    async def _find_next(self, command: str, params: Dict) -> str:
        return "Moving to next match"
    
    async def _find_previous(self, command: str, params: Dict) -> str:
        return "Moving to previous match"
    
    # IDE Controls
    async def _toggle_terminal(self, command: str, params: Dict) -> str:
        return "Terminal toggled"
    
    async def _toggle_sidebar(self, command: str, params: Dict) -> str:
        return "Sidebar toggled"
    
    async def _zoom_in(self, command: str, params: Dict) -> str:
        return "Zoomed in"
    
    async def _zoom_out(self, command: str, params: Dict) -> str:
        return "Zoomed out"
    
    async def _reset_zoom(self, command: str, params: Dict) -> str:
        return "Zoom reset to default"
    
    # Voice Controls
    async def _start_listening(self, command: str, params: Dict) -> str:
        self.listening_active = True
        return "Voice listening activated"
    
    async def _stop_listening(self, command: str, params: Dict) -> str:
        self.listening_active = False
        return "Voice listening deactivated"
    
    async def _mute_voice(self, command: str, params: Dict) -> str:
        self.voice_muted = True
        return "Voice commands muted"
    
    async def _unmute_voice(self, command: str, params: Dict) -> str:
        self.voice_muted = False
        return "Voice commands unmuted"
    
    # Information Commands
    async def _show_help(self, command: str, params: Dict) -> str:
        return """
Voice Controlled IDE Commands:

File Operations:
- "create file" - Create a new file
- "save file" - Save current file
- "open file" - Open an existing file
- "delete file" - Delete a file

Code Operations:
- "compile" / "compile code" - Compile the current code
- "run" / "run code" - Execute the current code
- "stop execution" - Stop running code

Editor Operations:
- "clear editor" - Clear the editor content
- "undo" / "redo" - Undo/redo actions
- "copy" / "paste" / "cut" - Clipboard operations

Project Operations:
- "new project" - Create a new project
- "save project" - Save the current project

Language Switching:
- "switch to python/javascript/java/cpp/c"

Voice Controls:
- "mute" / "unmute" - Mute/unmute voice commands
- "help" - Show this help message

For more detailed commands, visit the voice guide.
        """
    
    async def _show_commands(self, command: str, params: Dict) -> str:
        commands = list(self.command_mappings.keys())
        return f"Available commands: {', '.join(commands[:10])}... (total: {len(commands)})"
    
    async def _show_status(self, command: str, params: Dict) -> str:
        return f"""
IDE Status:
- Voice listening: {'Active' if self.listening_active else 'Inactive'}
- Voice commands: {'Muted' if self.voice_muted else 'Enabled'}
- Active execution: {'Yes' if self.current_execution else 'No'}
- Available commands: {len(self.command_mappings)}
        """
    
    async def _show_version(self, command: str, params: Dict) -> str:
        return "Voice Controlled IDE v2.0 - Advanced Features Edition"

# Global command processor instance
command_processor = VoiceCommandProcessor()

@router.post("/execute-voice-command/")
async def execute_voice_command(
    command: str = Form(...),
    filename: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    parameters: Optional[str] = Form(None)  # JSON string of additional parameters
):
    """Execute a voice command"""
    try:
        # Parse additional parameters
        params = {}
        if parameters:
            params = json.loads(parameters)
        
        # Add form parameters to params
        if filename:
            params['filename'] = filename
        if content:
            params['content'] = content
        if language:
            params['language'] = language
        
        result = await command_processor.process_command(command, params)
        return result
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in parameters")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Command execution error: {str(e)}")

@router.get("/available-commands/")
async def get_available_commands():
    """Get list of all available voice commands"""
    commands = list(command_processor.command_mappings.keys())
    
    # Categorize commands
    categories = {
        "File Operations": [cmd for cmd in commands if any(word in cmd for word in ['file', 'save', 'open', 'delete', 'rename'])],
        "Code Operations": [cmd for cmd in commands if any(word in cmd for word in ['compile', 'run', 'execute', 'stop'])],
        "Editor Operations": [cmd for cmd in commands if any(word in cmd for word in ['clear', 'undo', 'redo', 'copy', 'paste', 'cut', 'select'])],
        "Project Operations": [cmd for cmd in commands if 'project' in cmd],
        "Language Operations": [cmd for cmd in commands if 'switch' in cmd],
        "Navigation": [cmd for cmd in commands if any(word in cmd for word in ['go', 'find', 'replace', 'next', 'previous'])],
        "IDE Controls": [cmd for cmd in commands if any(word in cmd for word in ['toggle', 'zoom'])],
        "Voice Controls": [cmd for cmd in commands if any(word in cmd for word in ['listening', 'mute'])],
        "Information": [cmd for cmd in commands if any(word in cmd for word in ['help', 'status', 'version', 'commands'])]
    }
    
    return {
        "total_commands": len(commands),
        "categories": categories,
        "all_commands": commands
    }

@router.get("/command-status/")
async def get_command_status():
    """Get current command processor status"""
    return {
        "listening_active": command_processor.listening_active,
        "voice_muted": command_processor.voice_muted,
        "has_active_execution": command_processor.current_execution is not None,
        "total_commands": len(command_processor.command_mappings)
    }

@router.post("/toggle-listening/")
async def toggle_voice_listening():
    """Toggle voice listening on/off"""
    command_processor.listening_active = not command_processor.listening_active
    return {
        "listening_active": command_processor.listening_active,
        "message": f"Voice listening {'activated' if command_processor.listening_active else 'deactivated'}"
    }

@router.post("/toggle-mute/")
async def toggle_voice_mute():
    """Toggle voice command mute on/off"""
    command_processor.voice_muted = not command_processor.voice_muted
    return {
        "voice_muted": command_processor.voice_muted,
        "message": f"Voice commands {'muted' if command_processor.voice_muted else 'unmuted'}"
    }

@router.post("/quick-command/")
async def execute_quick_command(
    action: str = Form(...),  # save, compile, run, clear, help
    target: Optional[str] = Form(None)
):
    """Execute common quick commands"""
    quick_commands = {
        "save": "save file",
        "compile": "compile code",
        "run": "run code", 
        "clear": "clear editor",
        "help": "help",
        "stop": "stop execution",
        "undo": "undo",
        "redo": "redo"
    }
    
    if action not in quick_commands:
        raise HTTPException(status_code=400, detail=f"Unknown quick command: {action}")
    
    command = quick_commands[action]
    params = {"target": target} if target else {}
    
    result = await command_processor.process_command(command, params)
    return result