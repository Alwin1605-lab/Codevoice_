import axios from 'axios';
import config from '../config/api';
import { userService } from './userService';

// Attach X-User-Id header to all requests if available
axios.interceptors.request.use((configReq) => {
  try {
    const user = userService.getCurrentUser();
    if (user?.id) {
      configReq.headers = configReq.headers || {};
      configReq.headers['X-User-Id'] = user.id;
    }
  } catch {}
  return configReq;
});

const apiService = {
    // Authentication APIs
    
    register: async (name, email, password) => {
        const formData = new FormData();
        formData.append("name", name);
        formData.append("email", email);
        formData.append("password", password);
        const response = await axios.post(
            `${config.API_URL}${config.ENDPOINTS.REGISTER}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    login: async (email, password) => {
        const formData = new FormData();
        formData.append("email", email);
        formData.append("password", password);
        const response = await axios.post(
            `${config.API_URL}${config.ENDPOINTS.LOGIN}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    getUser: async (userId) => {
        const response = await axios.get(`${config.API_URL}${config.ENDPOINTS.GET_USER}${userId}`);
        return response.data;
    },

    // Transcription service
    transcribeAudio: async (audioBlob, language = 'en') => {
        const formData = new FormData();
        formData.append("file", audioBlob, "audio.wav");
        if (language) formData.append("language", language);
        const response = await axios.post(
            `${config.API_URL}${config.ENDPOINTS.TRANSCRIBE}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    // Code Generation APIs
    
    generateCode: async (prompt, type = "python", model = null, voice_feedback = false) => {
        const formData = new FormData();
        formData.append("prompt", prompt);
        formData.append("type", type);
        if (model) formData.append("model", model);
        formData.append("voice_feedback", voice_feedback.toString());
        const response = await axios.post(
            `${config.API_URL}${config.ENDPOINTS.GENERATE_CODE}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    explainCode: async (code, voice_feedback = false) => {
        const formData = new FormData();
        formData.append("code", code);
        formData.append("voice_feedback", voice_feedback.toString());
        const response = await axios.post(
            `${config.API_URL}${config.ENDPOINTS.EXPLAIN_CODE}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    improveCode: async (code, voice_feedback = false) => {
        const formData = new FormData();
        formData.append("code", code);
        formData.append("voice_feedback", voice_feedback.toString());
        const response = await axios.post(
            `${config.API_URL}${config.ENDPOINTS.IMPROVE_CODE}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    debugCode: async (code, voice_feedback = false) => {
        const formData = new FormData();
        formData.append("code", code);
        formData.append("voice_feedback", voice_feedback.toString());
        const response = await axios.post(
            `${config.API_URL}${config.ENDPOINTS.DEBUG_CODE}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    // Tests API removed per requirements

    // Compilation APIs
    
    compileCode: async (code, language, input_data = "") => {
        const formData = new FormData();
        formData.append("code", code);
        formData.append("language", language);
        // Backend expects 'inputs' field (newline separated) for /compile/
        formData.append("inputs", input_data);
        const response = await axios.post(
            `${config.API_URL}${(config.ENDPOINTS.COMPILE_CODE || config.ENDPOINTS.COMPILE || '/compile/')}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    getAvailableLanguages: async () => {
        const response = await axios.get(`${config.API_URL}${config.ENDPOINTS.GET_LANGUAGES}`);
        return response.data;
    },

    // Project Management APIs
    
    // New Database-backed project APIs
    createProjectDB: async (projectData) => {
        // Backend expects JSON for /api/projects/create
        const response = await axios.post(
            `${config.API_URL}/api/projects/create`,
            projectData,
            {
                headers: { "Content-Type": "application/json" }
            }
        );
        return response.data;
    },

    listProjectsDB: async (userId = null) => {
        const url = userId
            ? `${config.API_URL}/api/projects/list?user_id=${encodeURIComponent(userId)}`
            : `${config.API_URL}/api/projects/list`;
        const response = await axios.get(url);
        return response.data;
    },

    createProject: async (projectData) => {
        const formData = new FormData();
        formData.append("name", projectData.name);
        formData.append("description", projectData.description || "");
        formData.append("project_type", projectData.projectType || "general");
        formData.append("framework", projectData.framework || "");
        
        if (projectData.files) {
            formData.append("files", JSON.stringify(projectData.files));
        }
        
        const response = await axios.post(
            `${config.API_URL}${config.ENDPOINTS.CREATE_PROJECT}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    getProjects: async (userId) => {
        const response = await axios.get(`${config.API_URL}${config.ENDPOINTS.GET_PROJECTS}?user_id=${userId}`);
        return response.data;
    },

    getProject: async (projectId) => {
        const response = await axios.get(`${config.API_URL}${config.ENDPOINTS.GET_PROJECT}${projectId}`);
        return response.data;
    },

    updateProject: async (projectId, projectData) => {
        const formData = new FormData();
        Object.keys(projectData).forEach(key => {
            if (typeof projectData[key] === 'object') {
                formData.append(key, JSON.stringify(projectData[key]));
            } else {
                formData.append(key, projectData[key]);
            }
        });
        
        const response = await axios.put(
            `${config.API_URL}${config.ENDPOINTS.UPDATE_PROJECT}${projectId}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    deleteProject: async (projectId) => {
        const response = await axios.delete(`${config.API_URL}${config.ENDPOINTS.DELETE_PROJECT}${projectId}`);
        return response.data;
    },

    downloadProject: async (projectId) => {
        const response = await axios.get(
            `${config.API_URL}${config.ENDPOINTS.DOWNLOAD_PROJECT}${projectId}`,
            {
                responseType: 'blob'
            }
        );
        return response;
    },

    // File Management APIs
    
    uploadFile: async (projectId, file, filePath = "") => {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("file_path", filePath);
        
        const response = await axios.post(
            `${config.API_URL}${config.ENDPOINTS.UPLOAD_FILE}${projectId}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    getFile: async (projectId, filePath) => {
        const response = await axios.get(
            `${config.API_URL}${config.ENDPOINTS.GET_FILE}${projectId}`,
            {
                params: { file_path: filePath }
            }
        );
        return response.data;
    },

    updateFile: async (projectId, filePath, content) => {
        const formData = new FormData();
        formData.append("file_path", filePath);
        formData.append("content", content);
        
        const response = await axios.put(
            `${config.API_URL}${config.ENDPOINTS.UPDATE_FILE}${projectId}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    deleteFile: async (projectId, filePath) => {
        const response = await axios.delete(
            `${config.API_URL}${config.ENDPOINTS.DELETE_FILE}${projectId}`,
            {
                params: { file_path: filePath }
            }
        );
        return response.data;
    },

    // Template APIs
    
    getTemplates: async () => {
        const response = await axios.get(`${config.API_URL}${config.ENDPOINTS.GET_TEMPLATES}`);
        return response.data;
    },

    createFromTemplate: async (templateId, projectData) => {
        const formData = new FormData();
        formData.append("template_id", templateId);
        formData.append("name", projectData.name);
        formData.append("description", projectData.description || "");
        
        const response = await axios.post(
            `${config.API_URL}${config.ENDPOINTS.CREATE_FROM_TEMPLATE}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    // Voice Narration APIs
    
    speakText: async (text, voice_config = {}) => {
        const formData = new FormData();
        formData.append("text", text);
        formData.append("voice_config", JSON.stringify(voice_config));
        const response = await axios.post(
            `${config.API_URL}${config.ENDPOINTS.SPEAK_TEXT}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    stopSpeech: async () => {
        const response = await axios.post(`${config.API_URL}${config.ENDPOINTS.STOP_SPEECH}`);
        return response.data;
    },

    // Voice Commands APIs
    
    processVoiceCommand: async (command, context = {}) => {
        const formData = new FormData();
        formData.append("command", command);
        // Backend expects optional 'parameters' JSON string
        formData.append("parameters", JSON.stringify(context));
        const response = await axios.post(
            `${config.API_URL}${config.ENDPOINTS.PROCESS_COMMAND}`,
            formData,
            {
                headers: { "Content-Type": "multipart/form-data" }
            }
        );
        return response.data;
    },

    getAvailableCommands: async () => {
        const response = await axios.get(`${config.API_URL}${config.ENDPOINTS.GET_AVAILABLE_COMMANDS}`);
        return response.data;
    },

    // Voice Commands status and quick actions
    getVoiceCommandStatus: async () => {
        const response = await axios.get(`${config.API_URL}/commands/command-status/`);
        return response.data;
    },

    executeQuickVoiceCommand: async (action, target = null) => {
        const formData = new FormData();
        formData.append('action', action);
        if (target) formData.append('target', target);
        const response = await axios.post(`${config.API_URL}/commands/quick-command/`, formData, {
            headers: { "Content-Type": "multipart/form-data" }
        });
        return response.data;
    },

    // GEMINI PROJECT GENERATION APIs
    
    generateGeminiProject: async (projectData) => {
        const response = await axios.post(
            `${config.API_URL}/api/project-generation/generate`,
            projectData,
            {
                headers: { "Content-Type": "application/json" }
            }
        );
        return response.data;
    },

    generateGeminiProjectAsync: async (projectData) => {
        const response = await axios.post(
            `${config.API_URL}/api/project-generation/generate/async`,
            projectData,
            {
                headers: { "Content-Type": "application/json" }
            }
        );
        return response.data;
    },

    generateGeminiProjectFiles: async (projectData) => {
        const response = await axios.post(
            `${config.API_URL}/api/project-generation/generate-files`,
            projectData,
            {
                headers: { "Content-Type": "application/json" },
                responseType: 'blob'
            }
        );
        return response;
    },

    getGeminiTemplates: async () => {
        const response = await axios.get(`${config.API_URL}/api/project-generation/templates`);
        return response.data;
    },

    customizeGeminiTemplate: async (projectType, framework, features) => {
        const response = await axios.post(
            `${config.API_URL}/api/project-generation/customize-template`,
            {
                project_type: projectType,
                framework: framework,
                features: features
            },
            {
                headers: { "Content-Type": "application/json" }
            }
        );
        return response.data;
    },
    
    getGeminiHealth: async () => {
        const response = await axios.get(`${config.API_URL}/api/project-generation/health`);
        return response.data;
    },

    // CODEX COMPILER APIs
    
    compileWithCodex: async (code, language, mode = 'compile_and_run', inputData = null) => {
        const response = await axios.post(
            `${config.API_URL}/api/codex-compiler/compile`,
            {
                code: code,
                language: language,
                mode: mode,
                input_data: inputData,
                explain_output: true
            },
            {
                headers: { "Content-Type": "application/json" }
            }
        );
        return response.data;
    },

    optimizeCodeWithCodex: async (code, language, optimizationGoals = ['performance', 'readability']) => {
        const response = await axios.post(
            `${config.API_URL}/api/codex-compiler/optimize`,
            {
                code: code,
                language: language,
                optimization_goals: optimizationGoals,
                target_platform: 'general',
                maintain_functionality: true
            },
            {
                headers: { "Content-Type": "application/json" }
            }
        );
        return response.data;
    },

    debugCodeWithCodex: async (code, language, errorDescription = null, debugContext = null) => {
        const response = await axios.post(
            `${config.API_URL}/api/codex-compiler/debug`,
            {
                code: code,
                language: language,
                error_description: errorDescription,
                debug_context: debugContext
            },
            {
                headers: { "Content-Type": "application/json" }
            }
        );
        return response.data;
    },

    getCodexLanguages: async () => {
        const response = await axios.get(`${config.API_URL}/api/codex-compiler/languages`);
        return response.data;
    },

    // GROQ CODE ANALYSIS APIs
    
    explainCodeWithGroq: async (code, language, userLevel = 'intermediate', explanationType = 'overview', focusAreas = []) => {
        const response = await axios.post(
            `${config.API_URL}/api/code-analysis/explain`,
            {
                code: code,
                language: language,
                user_level: userLevel,
                explanation_type: explanationType,
                focus_areas: focusAreas
            },
            {
                headers: { "Content-Type": "application/json" }
            }
        );
        return response.data;
    },

    analyzeErrorWithGroq: async (code, language, errorMessage, userLevel = 'intermediate', includeFix = true) => {
        const response = await axios.post(
            `${config.API_URL}/api/code-analysis/analyze-error`,
            {
                code: code,
                language: language,
                error_message: errorMessage,
                user_level: userLevel,
                include_fix: includeFix
            },
            {
                headers: { "Content-Type": "application/json" }
            }
        );
        return response.data;
    },

    suggestImprovementsWithGroq: async (code, language, userLevel = 'intermediate') => {
        const response = await axios.post(
            `${config.API_URL}/api/code-analysis/suggest-improvements`,
            {
                code: code,
                language: language,
                user_level: userLevel,
                explanation_type: 'best_practices'
            },
            {
                headers: { "Content-Type": "application/json" }
            }
        );
        return response.data;
    },

    getGroqSkillLevels: async () => {
        const response = await axios.get(`${config.API_URL}/api/code-analysis/skill-levels`);
        return response.data;
    },

    // GitHub APIs
    createGithubRepo: async ({ repo_name, description = '', private: isPrivate = false }) => {
        const response = await axios.post(`${config.API_URL}/github/create-repo/`, {
            repo_name,
            description,
            private: isPrivate
        });
        return response.data;
    },

    // Collaboration DB API
    createCollaborationSession: async (name, description = '') => {
        // Get user ID from currentUser object in localStorage
        const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        const userId = currentUser.id;
        
        console.log('createCollaborationSession called with:', { name, description, userId, currentUser });
        
        if (!userId) {
            throw new Error('User not logged in - user ID not found');
        }
        
        const payload = {
            name,
            description,
            creator_id: userId,
            max_participants: 10,
            is_public: false
        };
        console.log('Sending payload:', payload);
        
        const response = await axios.post(`${config.API_URL}/api/collaboration/sessions`, payload, {
            headers: {
                'X-User-Id': userId
            }
        });
        console.log('Response:', response.data);
        return response.data;
    },

    joinCollaborationSession: async (sessionId, username) => {
        const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        const userId = currentUser.id;
        
        const response = await axios.post(`${config.API_URL}/api/collaboration/sessions/${sessionId}/join`, {
            user_id: userId,
            username: username || currentUser.name || 'User'
        }, {
            headers: {
                'X-User-Id': userId
            }
        });
        return response.data;
    },

    leaveCollaborationSession: async (sessionId) => {
        const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        const userId = currentUser.id;
        
        const response = await axios.post(`${config.API_URL}/api/collaboration/sessions/${sessionId}/leave`, {
            user_id: userId
        }, {
            headers: {
                'X-User-Id': userId
            }
        });
        return response.data;
    },

    getActiveSessions: async () => {
        const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        const userId = currentUser.id;
        
        const response = await axios.get(`${config.API_URL}/api/collaboration/sessions`, {
            headers: {
                'X-User-Id': userId
            }
        });
        return response.data;
    },

    getMyCollaborationInvites: async () => {
        const response = await axios.get(`${config.API_URL}${config.ENDPOINTS.GET_INVITES_DB}`);
        return response.data;
    },

    // Friends API
    getAllUsers: async () => {
        const response = await axios.get(`${config.API_URL}/api/users/list`);
        return response.data;
    },

    sendFriendRequest: async (friendId) => {
        const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        const userId = currentUser.id;
        
        const response = await axios.post(`${config.API_URL}/api/users/${userId}/friends/request`, {
            friend_id: friendId
        }, {
            headers: {
                'X-User-Id': userId
            }
        });
        return response.data;
    },

    acceptFriendRequest: async (friendId) => {
        const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        const userId = currentUser.id;
        
        const response = await axios.post(`${config.API_URL}/api/users/${userId}/friends/accept`, {
            friend_id: friendId
        }, {
            headers: {
                'X-User-Id': userId
            }
        });
        return response.data;
    },

    getFriends: async () => {
        const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        const userId = currentUser.id;
        
        const response = await axios.get(`${config.API_URL}/api/users/${userId}/friends`, {
            headers: {
                'X-User-Id': userId
            }
        });
        return response.data;
    }
};

// Database-backed Voice Commands & Analytics APIs
apiService.saveVoiceCommandDB = async (payload) => {
    const response = await axios.post(
        `${config.API_URL}/api/voice-commands/commands`,
        payload,
        { headers: { 'Content-Type': 'application/json' } }
    );
    return response.data;
};

apiService.saveUsageAnalyticsDB = async (payload) => {
    const response = await axios.post(
        `${config.API_URL}/api/voice-commands/usage-analytics`,
        payload,
        { headers: { 'Content-Type': 'application/json' } }
    );
    return response.data;
};

apiService.saveTranscriptionAnalyticsDB = async (payload) => {
    const response = await axios.post(
        `${config.API_URL}/api/voice-commands/transcription-analytics`,
        payload,
        { headers: { 'Content-Type': 'application/json' } }
    );
    return response.data;
};

apiService.getUserStatsDB = async (userId) => {
    const response = await axios.get(`${config.API_URL}/api/voice-commands/stats/${encodeURIComponent(userId)}`);
    return response.data;
};

apiService.getUserCommandsDB = async (userId, limit = 50) => {
    const response = await axios.get(`${config.API_URL}/api/voice-commands/commands/${encodeURIComponent(userId)}?limit=${limit}`);
    return response.data;
};

export default apiService;