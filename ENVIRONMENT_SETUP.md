# Environment Setup Guide

## 🔐 Security Notice
**NEVER commit your `.env` file to Git!** It contains sensitive API keys and secrets.

## 📋 Required API Keys

To run this project, you'll need to obtain the following API keys:

### 1. GROQ API Key
- **Purpose**: Language model access for transcription and code generation
- **Get it from**: [https://console.groq.com/keys](https://console.groq.com/keys)
- **Free tier**: Available
- **Variables**: `GROQ_API_KEY`, `GROQ_COMPILER_API_KEY`

### 2. Google Gemini API Key
- **Purpose**: AI code generation and project structure creation
- **Get it from**: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- **Free tier**: Available with limits
- **Variable**: `GEMINI_API_KEY`

### 3. GitHub Personal Access Token
- **Purpose**: Repository creation and file management
- **Get it from**: [https://github.com/settings/tokens](https://github.com/settings/tokens)
- **Required scopes**: `repo`, `user`
- **Variable**: `GIT_TOKEN`

## 🛠️ Setup Instructions

1. **Copy the environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** and replace the placeholder values:
   ```env
   GROQ_API_KEY=your-actual-groq-api-key
   GEMINI_API_KEY=your-actual-gemini-api-key
   GIT_TOKEN=your-actual-github-token
   ```

3. **Generate a secure secret key** for production:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. **Install MongoDB** (if running locally):
   ```bash
   # Windows (using Chocolatey)
   choco install mongodb
   
   # Or download from: https://www.mongodb.com/try/download/community
   ```

## 🔒 Security Best Practices

- ✅ `.env` is in `.gitignore` - your secrets are safe
- ✅ Use `.env.example` as a template for team members
- ✅ Rotate API keys regularly
- ✅ Use different keys for development and production
- ✅ Never share API keys in chat, email, or documentation

## 🚀 Deployment Notes

For production deployment:
- Use environment variables or secure secret management
- Don't use the `.env` file in production
- Use services like:
  - **Heroku**: Config Vars
  - **Vercel**: Environment Variables
  - **AWS**: Systems Manager Parameter Store
  - **Azure**: Key Vault
  - **Railway**: Environment Variables

## ❗ Troubleshooting

If you get API key errors:
1. Check that your `.env` file exists and has the correct values
2. Restart your development server after adding new environment variables
3. Verify API keys are valid by testing them in the respective dashboards
4. Check for trailing spaces or quotes in your `.env` file

## 📞 Support

If you need help obtaining API keys:
- GROQ: [Documentation](https://console.groq.com/docs)
- Gemini: [Getting Started](https://ai.google.dev/tutorials/setup)
- GitHub: [Token Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)