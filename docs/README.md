# Assistant Manager - Team Workflow Automation

A comprehensive desktop application that automates team management workflows using local LLMs, email automation, and intelligent task tracking.

## 🎯 Overview

Assistant Manager is a local-first team workflow automation system that:

- **Automates email communication** with team members for status updates
- **Manages Kanban boards** with drag-and-drop task management
- **Uses local LLMs** (via Ollama) for intelligent email parsing and responses
- **Publishes to GitHub Pages** for transparent project tracking
- **Operates entirely locally** with no cloud dependencies (except GitHub publishing)

## 🏗️ Architecture

### Frontend (React + TypeScript)
- **React 18** with TypeScript for type safety
- **Tailwind CSS** for modern, responsive design
- **@dnd-kit** for drag-and-drop kanban functionality
- **Axios** for API communication
- **WebSocket** integration for real-time updates

### Backend (Python + FastAPI)
- **FastAPI** for high-performance API endpoints
- **LangGraph** for agentic workflow orchestration
- **Ollama** integration for local LLM processing
- **SQLite** with Peewee ORM for local data storage
- **pywin32** for Outlook email automation

### Key Components
- **Assistant Agent**: LangGraph-based workflow orchestration
- **Email Tools**: Outlook COM automation for email management
- **Kanban Tools**: Task management and board synchronization
- **Git Tools**: GitHub Pages publishing automation
- **LLM Service**: Local Ollama integration with error handling

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** and npm
- **Python 3.9+** and pip
- **Ollama** installed and running locally
- **Microsoft Outlook** (for email automation)
- **Git** (for GitHub publishing)

### Installation

1. **Clone and setup:**
```bash
git clone <repository-url>
cd assistant-manager
npm run setup  # Installs both frontend and backend dependencies
```

2. **Configure Ollama:**
```bash
# Install and start Ollama
ollama pull llama3.2  # or your preferred model
ollama serve
```

3. **Configure environment:**
```bash
# Backend configuration
cd backend
cp .env.example .env
# Edit .env with your settings (GitHub token, etc.)
```

4. **Initialize database:**
```bash
cd backend
python -c "from app.models.database import initialize_database; import asyncio; asyncio.run(initialize_database())"
```

5. **Start the application:**
```bash
# Terminal 1: Backend
npm run backend:dev

# Terminal 2: Frontend
npm run dev
```

The application will be available at `http://localhost:5173`

## 📖 User Guide

### Initial Setup

1. **Team Configuration**
   - Navigate to "Team Members" tab
   - Search and add team members from Outlook contacts
   - Configure roles and active status

2. **Email Templates**
   - Go to "Email Center" → "Templates"
   - Customize default templates or create new ones
   - Use variables like `{{name}}`, `{{date}}` for personalization

3. **GitHub Integration**
   - Configure GitHub repository in settings
   - Add GitHub token for publishing permissions
   - Test publishing with "Sync to GitHub" button

### Daily Workflow

1. **Send Update Requests**
   - Use "Email Center" → "Send Update Requests"
   - Choose template and send to active team members
   - Monitor responses in "Email Threads"

2. **Manage Kanban Board**
   - Drag and drop tasks between columns
   - Create, edit, and delete tasks
   - Approve pending changes before publishing

3. **Query the Agent**
   - Use "Query Agent" for status reports
   - Ask questions like "What's the team status?" or "Show overdue tasks"
   - Get intelligent summaries and insights

4. **Publish Updates**
   - Review and approve kanban changes
   - Click "Sync to GitHub" to publish board
   - Share GitHub Pages URL with stakeholders

### Email Automation

The system automatically:
- Sends weekly update requests (configurable schedule)
- Parses email responses using local LLM
- Extracts task information and updates kanban board
- Sends follow-up reminders for overdue items
- Tracks response rates and communication metrics

## 🔧 Configuration

### Environment Variables

```bash
# Application
APP_NAME=Assistant Manager
DEBUG=false

# Database
DATABASE_URL=sqlite:///assistant_manager.db

# LLM Configuration
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=llama3.2

# Email Configuration
OUTLOOK_ENABLED=true
EMAIL_CHECK_INTERVAL=300

# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=your_username/your_repo
GITHUB_PAGES_BRANCH=gh-pages

# Scheduling
UPDATE_FREQUENCY=weekly
REMINDER_DAYS=2
MAX_FOLLOW_UPS=3
```

### Email Templates

Templates support variable substitution:

```
Subject: Weekly Update - {{date}}

Hi {{name}},

Please provide your weekly update on:
1. Current tasks and progress
2. Any blockers or challenges
3. Priorities for next week

Thanks!
```

Available variables:
- `{{name}}` - Team member name
- `{{email}}` - Team member email
- `{{date}}` - Current date
- `{{role}}` - Team member role
- `{{task_name}}` - Specific task name
- `{{due_date}}` - Task due date
- `{{priority}}` - Task priority

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest                    # Run all tests
python -m pytest --cov=app         # With coverage
python -m pytest -v tests/test_models.py  # Specific test file
```

### Frontend Tests
```bash
npm test                    # Run all tests
npm run test:watch         # Watch mode
npm run test:coverage      # With coverage
```

### Test Structure
- **Unit Tests**: Individual components and functions
- **Integration Tests**: API endpoints and workflows
- **Component Tests**: React component behavior
- **Hook Tests**: Custom React hooks

## 📊 Monitoring & Analytics

### Dashboard Metrics
- **Task Completion**: Track completed vs. active tasks
- **Response Rates**: Monitor team communication effectiveness
- **Email Statistics**: Sent, received, and pending emails
- **Agent Activity**: Automated actions and workflow status

### Health Checks
- **Agent Status**: Monitor LLM and workflow health
- **Database**: Connection and performance metrics
- **Email Integration**: Outlook connectivity status
- **GitHub Sync**: Publishing status and errors

## 🔒 Security & Privacy

### Local-First Design
- All sensitive data stored locally in SQLite
- LLM processing entirely on local machine
- No cloud dependencies except GitHub publishing
- Email content never leaves local environment

### Data Protection
- Encrypted database storage for sensitive information
- Secure IPC channels between frontend and backend
- Audit logging for all automated actions
- Configurable data retention policies

## 🛠️ Development

### Project Structure
```
assistant-manager/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── agents/         # LangGraph agent implementations
│   │   ├── api/            # FastAPI route handlers
│   │   ├── models/         # Database models and schemas
│   │   ├── services/       # Core services (LLM, email, etc.)
│   │   ├── tools/          # Agent tools (email, kanban, git)
│   │   └── core/           # Configuration and utilities
│   └── tests/              # Backend test suite
├── src/                    # React frontend
│   ├── components/         # React components
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API and WebSocket services
│   ├── types/              # TypeScript type definitions
│   └── __tests__/          # Frontend test suite
└── docs/                   # Documentation
```

### Adding New Features

1. **Backend API Endpoint**
   - Add route in `backend/app/api/`
   - Define Pydantic schemas in `models/schemas.py`
   - Add database models if needed
   - Write tests in `backend/tests/`

2. **Frontend Component**
   - Create component in `src/components/`
   - Add TypeScript types in `src/types/`
   - Implement API integration in `src/services/`
   - Write component tests in `src/__tests__/`

3. **Agent Tool**
   - Implement tool in `backend/app/tools/`
   - Register in `AssistantAgent` class
   - Add error handling and logging
   - Write unit tests

### Code Quality

```bash
# Backend
cd backend
black .                     # Format code
isort .                     # Sort imports
flake8 .                    # Lint code

# Frontend
npm run lint                # ESLint
npm run build               # Type checking
```

## 🚨 Troubleshooting

### Common Issues

**Ollama Connection Failed**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve
```

**Outlook Integration Issues**
- Ensure Outlook is installed and configured
- Check Windows security settings for COM access
- Verify email account is properly set up

**GitHub Publishing Fails**
- Verify GitHub token has repository permissions
- Check repository exists and is accessible
- Ensure GitHub Pages is enabled for the repository

**Database Errors**
```bash
# Reset database
cd backend
rm assistant_manager.db
python -c "from app.models.database import initialize_database; import asyncio; asyncio.run(initialize_database())"
```

### Logs and Debugging

- **Backend logs**: `backend/logs/assistant_manager.log`
- **Frontend console**: Browser developer tools
- **Agent activity**: Dashboard → Agent Status
- **Database queries**: Enable DEBUG mode in `.env`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Guidelines
- Follow existing code style and patterns
- Write comprehensive tests
- Update documentation for new features
- Use TypeScript for type safety
- Follow security best practices

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain/LangGraph** for agent orchestration framework
- **Ollama** for local LLM integration
- **FastAPI** for high-performance backend
- **React** and **Tailwind CSS** for modern frontend
- **@dnd-kit** for drag-and-drop functionality