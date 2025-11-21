// API configuration
const config = {
    API_URL: 'http://localhost:8000',
    ENDPOINTS: {
        // Basic functionality
        TRANSCRIBE: '/transcribe/',
        GENERATE_CODE: '/generate-code/',
    COMPILE: '/compile/',
    // Some services use COMPILE_CODE key
    COMPILE_CODE: '/compile/',
    // Judge0 info endpoint used to list available languages
    GET_LANGUAGES: '/compile/judge0/info',
        
        // Authentication endpoints
        REGISTER: '/api/users/register',
        LOGIN: '/api/users/login',
        GET_USER: '/api/users/',
        UPDATE_PROFILE: '/api/users/',
        
        // Learning Mode endpoints
        EXPLAIN_CODE: '/learning/explain-code/',
        ANALYZE_ERROR: '/learning/analyze-error/',
        LEARNING_PROGRESS: '/learning/progress/',
        
        // Collaboration endpoints
        CREATE_SESSION: '/collaboration/create-session/',
        JOIN_SESSION: '/collaboration/join-session/',
        LEAVE_SESSION: '/collaboration/leave-session/',
        GET_SESSIONS: '/collaboration/sessions/',
        COLLABORATION_WS: '/collaboration/ws/',
        
        // Project Manager endpoints (NEW DATABASE VERSIONS)
        CREATE_PROJECT_DB: '/api/projects/create',
        LIST_PROJECTS_DB: '/api/projects/list',
        GET_PROJECT_DB: '/api/projects/',
        UPDATE_PROJECT_DB: '/api/projects/',
        DELETE_PROJECT_DB: '/api/projects/',
        ADD_FILE_TO_PROJECT_DB: '/api/projects/',
        CREATE_CODE_SESSION_DB: '/api/projects/code-session',
        
        // Collaboration endpoints (NEW DATABASE VERSIONS)
        CREATE_SESSION_DB: '/api/collaboration/sessions',
        LIST_SESSIONS_DB: '/api/collaboration/sessions',
        GET_SESSION_DB: '/api/collaboration/sessions/',
        JOIN_SESSION_DB: '/api/collaboration/sessions/',
        LEAVE_SESSION_DB: '/api/collaboration/sessions/',
        CREATE_INVITE_DB: '/api/collaboration/invites',
        GET_INVITES_DB: '/api/collaboration/invites/',
        ACCEPT_INVITE_DB: '/api/collaboration/invites/',
        CREATE_EVENT_DB: '/api/collaboration/events',
        
        // Voice Commands endpoints (NEW DATABASE VERSIONS)
        SAVE_VOICE_COMMAND_DB: '/api/voice-commands/commands',
        GET_USER_COMMANDS_DB: '/api/voice-commands/commands/',
        SAVE_USAGE_ANALYTICS_DB: '/api/voice-commands/usage-analytics',
        SAVE_TRANSCRIPTION_ANALYTICS_DB: '/api/voice-commands/transcription-analytics',
        GET_USER_STATS_DB: '/api/voice-commands/stats/',
        
    // Original Project Manager endpoints (FILE-BASED - DEPRECATED)
        CREATE_PROJECT: '/projects/create-project/',
    GET_TEMPLATES: '/projects/templates/',
    // Some pages call GET_PROJECTS constant
    GET_PROJECTS: '/projects/projects/',
    DOWNLOAD_PROJECT: '/projects/projects/', // id or name appended + '/download/' on callsite
    UPLOAD_FILE: '/projects/projects/', // + '{project_name}/files/{file_path}' (handled in service)
    GET_FILE: '/projects/projects/',
    UPDATE_FILE: '/projects/projects/',
    DELETE_FILE: '/projects/projects/',
    CREATE_FROM_TEMPLATE: '/projects/create-project/',
        SAVE_PROJECT: '/projects/save/',
        LOAD_PROJECT: '/projects/load/',
        DELETE_PROJECT: '/projects/delete/',
        LIST_PROJECTS: '/projects/projects/',
        
        // Voice Narration endpoints
        SPEAK_TEXT: '/narration/speak/',
        STOP_SPEECH: '/narration/stop/',
        SET_VOICE_CONFIG: '/narration/config/',
        
        // Voice Commands endpoints
    PROCESS_COMMAND: '/commands/execute-voice-command/',
    GET_AVAILABLE_COMMANDS: '/commands/available-commands/',
        SET_COMMAND_CONFIG: '/commands/config/',
        
        // Keep DB endpoints (defined above already) – no change
    }
};

export default config;