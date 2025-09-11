# Agentic TodoList

An AI-powered task management application that intelligently organizes and prioritizes your todos using advanced agentic workflows. Transform your productivity with smart task scheduling, automatic categorization, and intelligent reminders.

## Features

- 🤖 **AI-Powered Task Management** - Intelligent task categorization and prioritization
- 📅 **Smart Scheduling** - Automatic task scheduling based on deadlines and importance
- 🔄 **Agentic Workflows** - Self-organizing task systems that adapt to your work patterns
- 💬 **Natural Language Processing** - Add tasks using natural language descriptions
- 📊 **Analytics Dashboard** - Track productivity patterns and task completion rates
- 🔗 **Integration Ready** - Connect with your favorite productivity tools

## Tech Stack

### Backend
- **Python** - Core application logic
- **FastAPI** - RESTful API framework
- **UV** - Package management and dependency resolution

### Frontend
- **React** - User interface framework
- **TypeScript** - Type-safe development
- **Vite** - Fast build tooling
- **Tailwind CSS** - Utility-first styling

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Bun (recommended) or npm

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/fathurwithyou/agentic-todolist.git
   cd agentic-todolist
   ```

2. **Backend Setup**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your configuration
   uv sync
   uv run python main.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   cp .env.example .env
   # Edit .env with your configuration
   bun install
   bun dev
   ```

### Environment Variables

#### Backend ([backend/.env](backend/.env.example))
- `DATABASE_URL` - Database connection string
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `JWT_SECRET` - Secret key for authentication

#### Frontend ([frontend/.env](frontend/.env.example))
- `VITE_API_URL` - Backend API URL
- `VITE_APP_NAME` - Application name

## Usage

1. **Start the application**
   - Backend will run on `http://localhost:8000`
   - Frontend will run on `http://localhost:5173`

2. **Create your first task**
   - Use natural language: "Schedule meeting with team next Tuesday at 2 PM"
   - The AI will automatically categorize and set appropriate reminders

3. **Let the AI organize**
   - Tasks are automatically prioritized based on deadlines and importance
   - Smart scheduling suggestions help optimize your day

## Project Structure

```
agentic-todolist/
├── backend/                 # Python FastAPI backend
│   ├── app/                # Application modules
│   ├── data/               # Data storage
│   ├── main.py            # Application entry point
│   └── pyproject.toml     # Python dependencies
├── frontend/               # React frontend
│   ├── src/               # Source code
│   ├── components.json    # UI component configuration
│   └── package.json       # Node.js dependencies
└── scripts/               # Utility scripts
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation powered by FastAPI's automatic OpenAPI generation.

## Contributing

We welcome contributions! Please see our contributing guidelines below:

### Development Setup

1. **Fork the repository** and create a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Follow the coding standards**
   - Backend: Follow PEP 8 and use type hints
   - Frontend: Use TypeScript and follow the existing code style

3. **Submit a pull request**
   - Ensure all tests pass
   - Include a clear description of changes
   - Reference any related issues

### Code Style

- **Backend**: We use `black` for code formatting and `mypy` for type checking
- **Frontend**: We use Biome for linting and formatting (see [frontend/biome.jsonc](frontend/biome.jsonc))

### Reporting Issues

Please use the GitHub issue tracker to report bugs or request features. Include:
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Environment details (OS, Python/Node versions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
