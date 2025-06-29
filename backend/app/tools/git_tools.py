"""Enhanced Git and GitHub integration tools for publishing Kanban board to GitHub Pages."""

from langchain.tools import BaseTool
from typing import Dict, Any, List
import logging
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

from app.models.database import Task, TeamMember, KanbanChange
from app.core.config import settings

logger = logging.getLogger(__name__)

class GitTools:
    """Collection of Git and GitHub tools for publishing Kanban board to GitHub Pages."""
    
    def __init__(self):
        self.repo_path = None
        self.temp_dir = None
    
    async def initialize(self):
        """Initialize Git tools."""
        logger.info("Git tools initialized")
    
    def _setup_temp_repo(self) -> str:
        """Setup temporary repository for GitHub operations."""
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="kanban_publish_")
            self.repo_path = os.path.join(self.temp_dir, "kanban-board")
            
            # Clone or initialize repository
            if settings.github_repo:
                # Clone existing repository
                clone_url = f"https://{settings.github_token}@github.com/{settings.github_repo}.git"
                result = subprocess.run([
                    "git", "clone", clone_url, self.repo_path
                ], capture_output=True, text=True, cwd=self.temp_dir)
                
                if result.returncode != 0:
                    logger.warning(f"Failed to clone repository: {result.stderr}")
                    # Initialize new repository
                    os.makedirs(self.repo_path, exist_ok=True)
                    subprocess.run(["git", "init"], cwd=self.repo_path, check=True)
            else:
                # Initialize new repository
                os.makedirs(self.repo_path, exist_ok=True)
                subprocess.run(["git", "init"], cwd=self.repo_path, check=True)
            
            # Configure git user
            subprocess.run([
                "git", "config", "user.name", "Assistant Manager"
            ], cwd=self.repo_path, check=True)
            subprocess.run([
                "git", "config", "user.email", "assistant@manager.local"
            ], cwd=self.repo_path, check=True)
            
            return self.repo_path
            
        except Exception as e:
            logger.error(f"Error setting up temporary repository: {e}")
            raise
    
    def _cleanup_temp_repo(self):
        """Cleanup temporary repository."""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
                self.repo_path = None
        except Exception as e:
            logger.error(f"Error cleaning up temporary repository: {e}")
    
    def _generate_kanban_html(self, board_data: Dict[str, Any]) -> str:
        """Generate beautiful HTML for the Kanban board."""
        
        # Get current timestamp
        last_updated = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        # Calculate statistics
        total_tasks = sum(len(column.get('tasks', [])) for column in board_data.get('columns', []))
        completed_tasks = len([
            task for column in board_data.get('columns', []) 
            if column.get('id') == 'done'
            for task in column.get('tasks', [])
        ])
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Team Kanban Board - Project Status</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    colors: {{
                        primary: {{
                            50: '#fef7f0',
                            100: '#fdeee0',
                            200: '#fad9c1',
                            300: '#f6be97',
                            400: '#f19a6b',
                            500: '#ed7c4a',
                            600: '#e85d2f',
                            700: '#c44a25',
                            800: '#9c3d23',
                            900: '#7e3420',
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        .task-card {{ transition: all 0.2s ease; }}
        .task-card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
        .priority-dot {{ width: 8px; height: 8px; border-radius: 50%; }}
        .priority-urgent {{ background-color: #ef4444; }}
        .priority-high {{ background-color: #ed7c4a; }}
        .priority-medium {{ background-color: #eab308; }}
        .priority-low {{ background-color: #6b7280; }}
        .fade-in {{ animation: fadeIn 0.5s ease-in; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-6 py-6">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">Team Kanban Board</h1>
                    <p class="text-gray-600 mt-1">Project status and task tracking</p>
                </div>
                <div class="text-right">
                    <div class="flex items-center space-x-6">
                        <div class="text-center">
                            <div class="text-2xl font-bold text-primary-600">{total_tasks}</div>
                            <div class="text-sm text-gray-500">Total Tasks</div>
                        </div>
                        <div class="text-center">
                            <div class="text-2xl font-bold text-green-600">{completed_tasks}</div>
                            <div class="text-sm text-gray-500">Completed</div>
                        </div>
                        <div class="text-center">
                            <div class="text-2xl font-bold text-blue-600">{total_tasks - completed_tasks}</div>
                            <div class="text-sm text-gray-500">In Progress</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-6 py-8">
        <!-- Last Updated -->
        <div class="mb-8 text-center">
            <p class="text-gray-500">Last updated: {last_updated}</p>
        </div>

        <!-- Kanban Board -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
"""
        
        # Generate columns
        column_styles = {
            'todo': {'bg': 'bg-gray-50', 'border': 'border-gray-200', 'header': 'text-gray-700', 'icon': '📋'},
            'in_progress': {'bg': 'bg-blue-50', 'border': 'border-blue-200', 'header': 'text-blue-700', 'icon': '🔄'},
            'review': {'bg': 'bg-yellow-50', 'border': 'border-yellow-200', 'header': 'text-yellow-700', 'icon': '👀'},
            'done': {'bg': 'bg-green-50', 'border': 'border-green-200', 'header': 'text-green-700', 'icon': '✅'},
            'blocked': {'bg': 'bg-red-50', 'border': 'border-red-200', 'header': 'text-red-700', 'icon': '🚫'},
        }
        
        for column in board_data.get('columns', []):
            column_id = column.get('id', '')
            column_title = column.get('title', '')
            tasks = column.get('tasks', [])
            style = column_styles.get(column_id, column_styles['todo'])
            
            html_content += f"""
            <!-- {column_title} Column -->
            <div class="fade-in">
                <div class="{style['bg']} {style['border']} border rounded-xl p-4 h-full">
                    <!-- Column Header -->
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center space-x-2">
                            <span class="text-xl">{style['icon']}</span>
                            <h3 class="font-semibold {style['header']}">{column_title}</h3>
                        </div>
                        <span class="bg-white px-2 py-1 rounded-md text-sm font-medium text-gray-600 border">
                            {len(tasks)}
                        </span>
                    </div>
                    
                    <!-- Tasks -->
                    <div class="space-y-3">
"""
            
            # Generate tasks for this column
            for task in tasks:
                assignee_name = task.get('assignee', {}).get('name', 'Unassigned')
                assignee_initials = ''.join([name[0] for name in assignee_name.split()[:2]]).upper()
                priority = task.get('priority', 'medium')
                due_date = task.get('due_date')
                tags = task.get('tags', [])
                
                # Format due date
                due_date_str = ""
                if due_date:
                    try:
                        due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        due_date_str = due_date_obj.strftime("%b %d")
                        
                        # Check if overdue
                        if due_date_obj < datetime.now() and column_id != 'done':
                            due_date_str = f'<span class="text-red-600 font-medium">⚠️ {due_date_str}</span>'
                        else:
                            due_date_str = f'<span class="text-gray-500">{due_date_str}</span>'
                    except:
                        due_date_str = '<span class="text-gray-500">Invalid date</span>'
                
                # Generate tags HTML
                tags_html = ""
                if tags:
                    tags_html = '<div class="flex flex-wrap gap-1 mt-2">'
                    for tag in tags[:3]:  # Show max 3 tags
                        tags_html += f'<span class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">{tag}</span>'
                    if len(tags) > 3:
                        tags_html += f'<span class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">+{len(tags) - 3}</span>'
                    tags_html += '</div>'
                
                html_content += f"""
                        <div class="task-card bg-white rounded-lg border border-gray-200 p-3 shadow-sm">
                            <!-- Task Header -->
                            <div class="flex items-start justify-between mb-2">
                                <h4 class="font-medium text-gray-900 text-sm leading-tight pr-2">
                                    {task.get('title', 'Untitled Task')}
                                </h4>
                                <div class="priority-dot priority-{priority}"></div>
                            </div>
                            
                            <!-- Task Description -->
                            {f'<p class="text-xs text-gray-600 mb-3 leading-relaxed">{task.get("description", "")[:100]}{"..." if len(task.get("description", "")) > 100 else ""}</p>' if task.get('description') else ''}
                            
                            <!-- Task Footer -->
                            <div class="flex items-center justify-between">
                                <!-- Assignee -->
                                <div class="flex items-center space-x-2">
                                    <div class="w-6 h-6 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center">
                                        <span class="text-white text-xs font-medium">{assignee_initials}</span>
                                    </div>
                                    <span class="text-xs text-gray-600 font-medium">{assignee_name.split()[0] if assignee_name != 'Unassigned' else 'Unassigned'}</span>
                                </div>
                                
                                <!-- Due Date -->
                                {f'<div class="text-xs">{due_date_str}</div>' if due_date_str else ''}
                            </div>
                            
                            <!-- Tags -->
                            {tags_html}
                        </div>
"""
            
            html_content += """
                    </div>
                </div>
            </div>
"""
        
        # Close main content and add footer
        html_content += f"""
        </div>
        
        <!-- Statistics Section -->
        <div class="mt-12 bg-white rounded-xl border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Project Statistics</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center p-4 bg-gray-50 rounded-lg">
                    <div class="text-2xl font-bold text-gray-900">{total_tasks}</div>
                    <div class="text-sm text-gray-500">Total Tasks</div>
                </div>
                <div class="text-center p-4 bg-green-50 rounded-lg">
                    <div class="text-2xl font-bold text-green-600">{completed_tasks}</div>
                    <div class="text-sm text-gray-500">Completed</div>
                </div>
                <div class="text-center p-4 bg-blue-50 rounded-lg">
                    <div class="text-2xl font-bold text-blue-600">{total_tasks - completed_tasks}</div>
                    <div class="text-sm text-gray-500">Active</div>
                </div>
                <div class="text-center p-4 bg-primary-50 rounded-lg">
                    <div class="text-2xl font-bold text-primary-600">{round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)}%</div>
                    <div class="text-sm text-gray-500">Progress</div>
                </div>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-12">
        <div class="max-w-7xl mx-auto px-6 py-6">
            <div class="text-center text-gray-500">
                <p>Generated by Assistant Manager • Last updated: {last_updated}</p>
                <p class="text-xs mt-1">Automated team workflow management system</p>
            </div>
        </div>
    </footer>

    <script>
        // Add fade-in animation to elements
        document.addEventListener('DOMContentLoaded', function() {{
            const elements = document.querySelectorAll('.fade-in');
            elements.forEach((el, index) => {{
                setTimeout(() => {{
                    el.style.opacity = '1';
                    el.style.transform = 'translateY(0)';
                }}, index * 100);
            }});
        }});
        
        // Auto-refresh every 5 minutes
        setTimeout(() => {{
            window.location.reload();
        }}, 300000);
    </script>
</body>
</html>"""
        
        return html_content
    
    @property
    def publish_kanban_to_github(self):
        """Tool for publishing Kanban board to GitHub Pages."""
        
        class PublishKanbanTool(BaseTool):
            name = "publish_kanban_to_github"
            description = "Publish the current Kanban board to GitHub Pages as a beautiful HTML website"
            
            def __init__(self, git_tools):
                super().__init__()
                self.git_tools = git_tools
            
            def _run(self) -> str:
                try:
                    # Get current board data
                    board_data = self._get_board_data()
                    
                    # Setup temporary repository
                    repo_path = self.git_tools._setup_temp_repo()
                    
                    # Generate HTML content
                    html_content = self.git_tools._generate_kanban_html(board_data)
                    
                    # Write HTML file
                    index_path = os.path.join(repo_path, "index.html")
                    with open(index_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    # Create README
                    readme_content = f"""# Team Kanban Board

This is an automatically generated Kanban board showing the current status of team tasks and projects.

## Statistics
- Total Tasks: {sum(len(column.get('tasks', [])) for column in board_data.get('columns', []))}
- Completed: {len([task for column in board_data.get('columns', []) if column.get('id') == 'done' for task in column.get('tasks', [])])}
- Last Updated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

## View Board
Visit the live board at: https://{settings.github_repo.split('/')[0]}.github.io/{settings.github_repo.split('/')[1]}/

---
*Generated by Assistant Manager - Automated Team Workflow System*
"""
                    
                    readme_path = os.path.join(repo_path, "README.md")
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                    
                    # Git operations
                    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
                    
                    # Check if there are changes to commit
                    result = subprocess.run([
                        "git", "diff", "--cached", "--quiet"
                    ], cwd=repo_path, capture_output=True)
                    
                    if result.returncode != 0:  # There are changes
                        # Commit changes
                        commit_message = f"Update Kanban board - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        subprocess.run([
                            "git", "commit", "-m", commit_message
                        ], cwd=repo_path, check=True)
                        
                        # Push to GitHub
                        if settings.github_repo and settings.github_token:
                            # Set up remote if it doesn't exist
                            remote_url = f"https://{settings.github_token}@github.com/{settings.github_repo}.git"
                            
                            # Check if remote exists
                            result = subprocess.run([
                                "git", "remote", "get-url", "origin"
                            ], cwd=repo_path, capture_output=True, text=True)
                            
                            if result.returncode != 0:
                                # Add remote
                                subprocess.run([
                                    "git", "remote", "add", "origin", remote_url
                                ], cwd=repo_path, check=True)
                            
                            # Push to main branch
                            subprocess.run([
                                "git", "push", "-u", "origin", "main"
                            ], cwd=repo_path, check=True)
                            
                            # Create/update gh-pages branch
                            subprocess.run([
                                "git", "checkout", "-B", "gh-pages"
                            ], cwd=repo_path, check=True)
                            
                            subprocess.run([
                                "git", "push", "-f", "origin", "gh-pages"
                            ], cwd=repo_path, check=True)
                            
                            github_pages_url = f"https://{settings.github_repo.split('/')[0]}.github.io/{settings.github_repo.split('/')[1]}/"
                            
                            result_message = f"Successfully published Kanban board to GitHub Pages!\n\nView your board at: {github_pages_url}\n\nThe board includes:\n- Beautiful responsive design\n- Real-time task status\n- Team member assignments\n- Priority indicators\n- Due date tracking\n- Project statistics"
                        else:
                            result_message = "Kanban board HTML generated successfully, but GitHub repository not configured for publishing."
                    else:
                        result_message = "No changes detected in Kanban board. GitHub Pages is already up to date."
                    
                    # Cleanup
                    self.git_tools._cleanup_temp_repo()
                    
                    logger.info("Kanban board published to GitHub Pages successfully")
                    return result_message
                    
                except Exception as e:
                    # Cleanup on error
                    self.git_tools._cleanup_temp_repo()
                    error_msg = f"Error publishing Kanban board to GitHub Pages: {str(e)}"
                    logger.error(error_msg)
                    return error_msg
            
            def _get_board_data(self) -> Dict[str, Any]:
                """Get current board data from database."""
                try:
                    # Get all tasks with their assignees
                    tasks = list(Task.select().join(TeamMember))
                    
                    # Group tasks by status
                    columns = {
                        "todo": {"id": "todo", "title": "To Do", "tasks": []},
                        "in_progress": {"id": "in_progress", "title": "In Progress", "tasks": []},
                        "review": {"id": "review", "title": "Review", "tasks": []},
                        "done": {"id": "done", "title": "Done", "tasks": []},
                        "blocked": {"id": "blocked", "title": "Blocked", "tasks": []},
                    }
                    
                    for task in tasks:
                        task_data = {
                            "id": task.id,
                            "title": task.title,
                            "description": task.description,
                            "status": task.status,
                            "due_date": task.due_date.isoformat() if task.due_date else None,
                            "priority": task.priority,
                            "tags": task.tags_list,
                            "assignee": {
                                "id": task.assignee.id,
                                "name": task.assignee.name,
                                "email": task.assignee.email,
                                "role": task.assignee.role,
                            }
                        }
                        
                        if task.status in columns:
                            columns[task.status]["tasks"].append(task_data)
                    
                    # Sort tasks by order within each column
                    for column in columns.values():
                        column["tasks"].sort(key=lambda x: x.get("order", 0))
                    
                    return {
                        "columns": list(columns.values()),
                        "last_updated": datetime.now().isoformat()
                    }
                    
                except Exception as e:
                    logger.error(f"Error getting board data: {e}")
                    return {"columns": [], "last_updated": datetime.now().isoformat()}
            
            async def _arun(self) -> str:
                return self._run()
        
        return PublishKanbanTool(self)
    
    @property
    def get_github_status(self):
        """Tool for checking GitHub repository status."""
        
        class GetGitHubStatusTool(BaseTool):
            name = "get_github_status"
            description = "Check the status of GitHub repository and Pages deployment"
            
            def _run(self) -> str:
                try:
                    if not settings.github_repo:
                        return "GitHub repository not configured. Please set GITHUB_REPO in settings."
                    
                    if not settings.github_token:
                        return "GitHub token not configured. Please set GITHUB_TOKEN in settings."
                    
                    github_pages_url = f"https://{settings.github_repo.split('/')[0]}.github.io/{settings.github_repo.split('/')[1]}/"
                    repo_url = f"https://github.com/{settings.github_repo}"
                    
                    return f"""GitHub Integration Status:
✅ Repository: {settings.github_repo}
✅ Token: Configured
🌐 GitHub Pages URL: {github_pages_url}
📁 Repository URL: {repo_url}

Status: Ready for publishing"""
                    
                except Exception as e:
                    return f"Error checking GitHub status: {str(e)}"
            
            async def _arun(self) -> str:
                return self._run()
        
        return GetGitHubStatusTool()