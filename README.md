# Codevoice_

A Voice Controlled IDE for people with Motor disabilities.

## Overview

Codevoice_ is an innovative Integrated Development Environment (IDE) designed specifically for individuals with motor disabilities. It leverages advanced AI technologies and voice recognition to enable hands-free coding, project management, and software development. The platform combines speech-to-text transcription, AI-powered code generation, and voice command processing to create an accessible coding experience.

## Features

### Core Functionality
- **Voice-Controlled Code Editing**: Control your IDE entirely through voice commands
- **AI-Powered Code Generation**: Generate code snippets and entire projects using Groq and Google Gemini AI
- **Real-time Speech Recognition**: Advanced transcription using Whisper models
- **Multi-language Support**: Support for English, Spanish, French, and German voice commands
- **Text-to-Speech Narration**: Audio feedback and code narration capabilities

### Advanced Features
- **Learning Mode**: AI-powered code explanations with beginner, intermediate, and advanced levels
- **Error Analysis**: Intelligent error diagnosis and solution suggestions
- **Collaboration Tools**: Real-time collaborative coding sessions
- **Project Management**: Complete project lifecycle management through voice
- **Voice Commands API**: Extensible voice command system for custom integrations
- **Remote Code Execution**: Execute code remotely using Judge0 API
- **GitHub Integration**: Direct repository management and file operations

### Supported Technologies
- **Backend**: Python FastAPI with MongoDB database
- **Frontend**: React with Material-UI and Monaco Editor
- **AI Providers**: Groq, Google Gemini, OpenAI
- **Speech Processing**: Faster-Whisper, WebRTC VAD
- **Authentication**: JWT-based user authentication

## Architecture

### Backend (codevoice-backend/)
- **FastAPI Framework**: High-performance async web framework
- **MongoDB**: NoSQL database for user data and projects
- **AI Integration**: Multiple AI providers for code generation and analysis
- **WebSocket Support**: Real-time communication for collaborative features
- **Modular Design**: Separate routers for different functionalities

### Frontend (codevoice-frontend/)
- **React**: Modern JavaScript framework
- **Material-UI**: Dark theme with purple aesthetic
- **Monaco Editor**: Professional code editing experience
- **React Speech Recognition**: Voice input handling
- **Responsive Design**: Accessible interface design

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB
- Git

### Backend Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Alwin1605-lab/Codevoice_.git
   cd Codevoice_/codevoice-backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (see ENVIRONMENT_SETUP.md)
   ```

4. **Start MongoDB** and run the backend:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd ../codevoice-frontend
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

## Usage

### Getting Started
1. Open the application in your browser
2. Register or login to your account
3. Grant microphone permissions for voice input
4. Start coding with voice commands!

### Voice Commands Examples
- "Create new file"
- "Generate function to calculate fibonacci"
- "Compile and run code"
- "Explain this code"
- "Save project"

### Multi-language Commands
- English: "compile code"
- Spanish: "compilar código"
- French: "compiler code"
- German: "code kompilieren"

## API Documentation

### Main Endpoints
- `POST /generate-code/` - AI code generation
- `POST /transcribe/` - Speech to text
- `POST /compile/` - Code compilation
- `POST /voice-commands/` - Voice command processing
- `POST /learning/explain-code/` - Code explanation
- `POST /multilang/transcribe-multilang/` - Multi-language transcription

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/profile` - Get user profile

## Configuration

### Environment Variables
```env
GROQ_API_KEY=your-groq-api-key
GEMINI_API_KEY=your-gemini-api-key
GIT_TOKEN=your-github-token
MONGODB_URL=mongodb://localhost:27017/codevoice
SECRET_KEY=your-secret-key
```

See `ENVIRONMENT_SETUP.md` for detailed setup instructions.

## Testing

### Backend Tests
```bash
cd codevoice-backend
pytest
```

### Frontend Tests
```bash
cd codevoice-frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Project Structure

```
Codevoice_/
├── codevoice-backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── ai_code_generator.py    # AI code generation logic
│   ├── voice_commands.py       # Voice command processing
│   ├── transcription.py        # Speech recognition
│   ├── database.py             # MongoDB connection
│   ├── models/                 # Data models
│   ├── services/               # Business logic services
│   └── tests/                  # Unit and integration tests
├── codevoice-frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React application
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Application pages
│   │   ├── context/           # React context providers
│   │   └── services/          # API service functions
│   ├── public/                # Static assets
│   └── package.json           # Node dependencies
├── voice_diagnostic.html      # Voice testing utilities
├── voice_test.html           # Voice functionality tests
└── voice_troubleshooting.js  # Voice troubleshooting tools
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with ❤️ for accessibility in software development
- Powered by cutting-edge AI technologies
- Special thanks to the open-source community

## Support

For support, please open an issue on GitHub or contact the maintainers.

---

*Empowering developers with disabilities through voice-controlled innovation*
