import os
import json
from typing import Dict, List, Any, Optional
import requests
from groq import Groq
import google.generativeai as genai
import logging
import re

logger = logging.getLogger(__name__)


class AICodeGenerator:
	def __init__(self):
		groq_key = os.getenv('GROQ_API_KEY')
		if groq_key:
			try:
				self.groq_client = Groq(api_key=groq_key)
			except Exception as e:
				logger.warning(f"Failed to initialize Groq client: {e}")
				self.groq_client = None
		else:
			logger.warning("GROQ_API_KEY not configured; Groq client disabled")
			self.groq_client = None

		# Configure Gemini (optional)
		gemini_key = os.getenv('GEMINI_API_KEY')
		if gemini_key and gemini_key != 'your-gemini-api-key-here':
			try:
				genai.configure(api_key=gemini_key)
				# Use a stable model identifier if available
				self.gemini_model = genai.GenerativeModel('models/gemini-2.0')
			except Exception as e:
				logger.warning(f"Failed to initialize Gemini client: {e}")
				self.gemini_model = None
		else:
			self.gemini_model = None
    
	def generate_project_structure(self, project_data: Dict) -> Dict:
		"""Generate complete project structure based on description"""
        
		prompt = self._build_project_prompt(project_data)
        
		try:
			project_files = None
			used_provider: Optional[str] = None

			# Try Gemini first if available
			if self.gemini_model:
				try:
					response = self.gemini_model.generate_content(prompt)
					text = getattr(response, 'text', None) or str(response)
					project_files = self._parse_ai_response(text)
					used_provider = 'gemini'
				except Exception as e:
					logger.warning(f"Gemini generation failed: {e}")
					project_files = None

			# Fallback to GROQ
			if project_files is None and self.groq_client:
				try:
					response = self.groq_client.chat.completions.create(
						messages=[
							{"role": "system", "content": "You are an expert full-stack developer who creates complete, working project structures."},
							{"role": "user", "content": prompt}
						],
						model=os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768'),
						temperature=0.7,
						max_tokens=8000
					)
					content = response.choices[0].message.content
					project_files = self._parse_ai_response(content)
					used_provider = 'groq'
				except Exception as e:
					logger.warning(f"Groq generation failed: {e}")
					project_files = None

			if not project_files:
				# Return fallback structure if both failed
				return {
					"success": False,
					"error": "AI generation failed for both providers",
					"fallback_files": self._get_fallback_structure(project_data)
				}

			return {
				"success": True,
				"project_name": project_data['name'],
				"description": project_data['description'],
				"framework": project_data['framework'],
				"features": project_data['features'],
				"files": project_files,
				"github_ready": True,
				"generated_by": used_provider
			}

		except Exception as e:
			logger.exception("Unexpected error in generate_project_structure")
			return {
				"success": False,
				"error": str(e),
				"fallback_files": self._get_fallback_structure(project_data)
			}
    
	def _build_project_prompt(self, project_data: Dict) -> str:
		"""Build detailed prompt for AI project generation"""
        
		prompt = f"""
Generate a complete, production-ready {project_data['framework']} project structure for:

PROJECT DETAILS:
- Name: {project_data['name']}
- Description: {project_data['description']}
- Type: {project_data['type']}
- Framework: {project_data['framework']}
- Features: {', '.join(project_data['features'])}

REQUIREMENTS:
1. Create a fully functional project with all necessary files
2. Include proper package.json/requirements.txt with all dependencies
3. Implement the requested features with working code
4. Add proper README.md with setup instructions
5. Include proper folder structure and configuration files
6. All code should be production-ready and follow best practices

FEATURES TO IMPLEMENT:
"""
        
		feature_descriptions = {
			'authentication': 'User login/register system with JWT tokens',
			'database': 'Database integration with models and schemas',
			'api': 'RESTful API endpoints with proper routing',
			'responsive-design': 'Mobile-responsive UI components',
			'dark-mode': 'Dark/light theme toggle functionality',
			'notifications': 'Real-time notification system',
			'real-time-chat': 'WebSocket-based chat functionality',
			'file-upload': 'File upload and storage system',
			'payment-integration': 'Payment processing integration',
			'analytics': 'User analytics and tracking',
			'admin-panel': 'Administrative dashboard',
			'mobile-responsive': 'Mobile-optimized responsive design'
		}
        
		for feature in project_data['features']:
			if feature in feature_descriptions:
				prompt += f"- {feature}: {feature_descriptions[feature]}\n"
        
		prompt += f"""

OUTPUT FORMAT:
Return a JSON object with this exact structure:
{{
	"files": [
		{{
			"path": "package.json",
			"content": "complete file content here"
		}},
		{{
			"path": "src/App.js",
			"content": "complete file content here"
		}}
		// ... all project files
	]
}}

Make sure ALL file contents are complete and functional. Include:
- package.json with ALL required dependencies
- Main application files
- Component files for each feature
- Configuration files (webpack, babel, etc.)
- README.md with setup instructions
- Environment configuration files
- Styling files (CSS/SCSS)

Ensure the project can be immediately run with npm install && npm start.
"""
		return prompt
    
	def _parse_ai_response(self, response_text: str) -> List[Dict]:
		"""Parse AI response and extract file structure.

		This tries multiple heuristics to locate JSON in noisy LLM output:
		- Extract largest JSON object/bracket block
		- Search for ```json blocks
		- Fallback to first JSON-like substring
		"""
		if not response_text:
			return self._create_basic_structure()

		# If it's already a dict/list string, try direct parse first
		try:
			parsed = json.loads(response_text)
			if isinstance(parsed, dict) and 'files' in parsed:
				return parsed.get('files', [])
			# If top-level is list of files
			if isinstance(parsed, list):
				return parsed
		except Exception:
			pass

		# Try to find fenced json blocks
		fenced = re.search(r"```json\s*([\s\S]*?)```", response_text, re.IGNORECASE)
		candidate = None
		if fenced:
			candidate = fenced.group(1).strip()

		# If not found, extract the largest {...} block
		if not candidate:
			braces = list(re.finditer(r"\{", response_text))
			if braces:
				# find last closing brace
				last_close = response_text.rfind('}')
				first_open = braces[0].start()
				candidate = response_text[first_open:last_close+1]

		# As a last effort, search for first JSON object
		if not candidate:
			m = re.search(r"(\{[\s\S]*\})", response_text)
			if m:
				candidate = m.group(1)

		if candidate:
			try:
				parsed = json.loads(candidate)
				if isinstance(parsed, dict) and 'files' in parsed:
					return parsed.get('files', [])
				if isinstance(parsed, list):
					return parsed
			except Exception as e:
				logger.warning(f"Failed to parse extracted JSON candidate: {e}")

		# Give up and return fallback minimal structure
		return self._create_basic_structure()
    
	def _create_basic_structure(self) -> List[Dict]:
		"""Create basic project structure as fallback"""
		return [
			{
				"path": "package.json",
				"content": json.dumps({
					"name": "ai-generated-project",
					"version": "1.0.0",
					"scripts": {
						"start": "react-scripts start",
						"build": "react-scripts build"
					},
					"dependencies": {
						"react": "^18.2.0",
						"react-dom": "^18.2.0",
						"react-scripts": "5.0.1"
					}
				}, indent=2)
			},
			{
				"path": "public/index.html",
				"content": """<!DOCTYPE html>
<html lang=\"en\">\n<head>\n    <meta charset=\"utf-8\" />\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n    <title>AI Generated Project</title>\n</head>\n<body>\n    <div id=\"root\"></div>\n</body>\n</html>"""
			},
			{
				"path": "src/index.js",
				"content": """import React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport App from './App';\n\nconst root = ReactDOM.createRoot(document.getElementById('root'));\nroot.render(<App />);"""
			},
			{
				"path": "src/App.js",
				"content": """import React from 'react';\nimport './App.css';\n\nfunction App() {\n  return (\n    <div className=\"App\">\n      <header className=\"App-header\">\n        <h1>AI Generated Project</h1>\n        <p>Your project has been successfully generated!</p>\n      </header>\n    </div>\n  );\n}\n\nexport default App;"""
			},
			{
				"path": "src/App.css",
				"content": ".App {\n  text-align: center;\n}\n\n.App-header {\n  background-color: #282c34;\n  padding: 20px;\n  color: white;\n  min-height: 100vh;\n  display: flex;\n  flex-direction: column;\n  align-items: center;\n  justify-content: center;\n}" 
			},
			{
				"path": "README.md",
				"content": """# AI Generated Project\n\nThis project was generated using AI-powered code generation.\n\n## Getting Started\n\n1. Install dependencies:\n```bash\nnpm install\n```\n\n2. Start the development server:\n```bash\nnpm start\n```\n\n3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.\n\n## Available Scripts\n\n- `npm start` - Runs the app in development mode\n- `npm run build` - Builds the app for production\n- `npm test` - Launches the test runner\n\n## Features\n\nThis project includes the following features:\n- Modern React setup\n- Responsive design\n- Development server\n- Production build process\n"""
			}
		]

	def _get_fallback_structure(self, project_data: Dict) -> List[Dict]:
		"""Get fallback project structure if AI generation fails"""
		return self._create_basic_structure()

# Global instance
ai_generator = AICodeGenerator()

