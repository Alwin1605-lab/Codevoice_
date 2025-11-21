import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import apiService from '../services/apiService';
import { userService } from '../services/userService';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

const VoiceControlContext = createContext();

export const useVoiceControl = () => {
    const context = useContext(VoiceControlContext);
    if (!context) {
        throw new Error('useVoiceControl must be used within a VoiceControlProvider');
    }
    return context;
};

const API_BASE = 'http://localhost:8000';

export const VoiceControlProvider = ({ children }) => {
    const navigate = useNavigate();
    const { user, login, logout } = useAuth();
    const [isListening, setIsListening] = useState(false);
    const [isEnabled, setIsEnabled] = useState(true);
    const [currentPage, setCurrentPage] = useState('home');
    const [lastCommand, setLastCommand] = useState('');
    const [voiceStatus, setVoiceStatus] = useState('ready');
    
    const recognitionRef = useRef(null);
    const silenceTimeoutRef = useRef(null);
    const startInProgressRef = useRef(false);
    const watchdogIntervalRef = useRef(null);

    // Voice command mappings
    const globalCommands = {
        // Navigation commands
        'home': () => navigate('/'),
        'go home': () => navigate('/'),
        'code generation': () => navigate('/code-generation'),
        'code transcription': () => navigate('/code-transcription'),
        'learning mode': () => navigate('/learning-mode'),
        'collaboration': () => navigate('/collaboration'),
        'projects': () => navigate('/project-manager'),
        'project manager': () => navigate('/project-manager'),
        'voice commands': () => navigate('/voice-commands'),
        'profile': () => navigate('/profile'),
        'friends': () => navigate('/friends'),
        'debug projects': () => navigate('/debug-projects'),
        
        // Authentication commands
        'sign up': () => navigate('/register'),
        'register': () => navigate('/register'),
        'login': () => navigate('/login'),
        'log in': () => navigate('/login'),
        'logout': () => handleLogout(),
        'log out': () => handleLogout(),
        
        // Global actions
        'help': () => showHelp(),
        'what can i say': () => showHelp(),
        'voice help': () => showHelp(),
        'stop listening': () => stopListening(),
        'start listening': () => startListening(),
        'enable voice': () => setIsEnabled(true),
        'disable voice': () => setIsEnabled(false),

    // Scrolling
    'scroll down': () => window.scrollBy({ top: 400, behavior: 'smooth' }),
    'scroll up': () => window.scrollBy({ top: -400, behavior: 'smooth' }),
    'scroll left': () => window.scrollBy({ left: -400, behavior: 'smooth' }),
    'scroll right': () => window.scrollBy({ left: 400, behavior: 'smooth' }),
    'scroll top': () => window.scrollTo({ top: 0, behavior: 'smooth' }),
    'scroll bottom': () => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }),
        
        // Common actions
        'save': () => executePageAction('save'),
        'compile': () => executePageAction('compile'),
        'run': () => executePageAction('run'),
        'clear': () => executePageAction('clear'),
        'copy': () => executePageAction('copy'),
        'paste': () => executePageAction('paste'),
        'undo': () => executePageAction('undo'),
        'redo': () => executePageAction('redo'),
        
        // Form actions
        'submit': () => executePageAction('submit'),
        'cancel': () => executePageAction('cancel'),
        'reset': () => executePageAction('reset'),
        'focus username': () => focusField('username'),
        'focus password': () => focusField('password'),
        'focus email': () => focusField('email'),
        'focus name': () => focusField('name'),
    };

    // Initialize speech recognition
    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            
            const recognition = recognitionRef.current;
            recognition.continuous = true;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onstart = () => {
                setVoiceStatus('listening');
            };
            
            recognition.onresult = (event) => {
                const last = event.results.length - 1;
                const command = event.results[last][0].transcript.toLowerCase().trim();
                setLastCommand(command);
                processVoiceCommand(command);
            };
            
            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error || event);
                // Some browsers emit 'aborted' or non-standard error names; treat 'aborted' as a graceful stop
                if (event.error === 'aborted' || event.type === 'abort') {
                    // Do not mark as error; onend will handle restart logic
                    return;
                }
                setVoiceStatus('error');
                if (event.error === 'not-allowed') {
                    speakFeedback('Microphone access denied. Please allow microphone access and try again.');
                }
            };
            
            recognition.onend = () => {
                setVoiceStatus('ready');
                setIsListening(false);

                // Only restart if explicitly listening and enabled. Some implementations set event.type to 'abort'
                if (isListening && isEnabled) {
                    setTimeout(() => {
                        try {
                            if (recognitionRef.current && isEnabled) {
                                recognitionRef.current.start();
                                setIsListening(true);
                            }
                        } catch (e) {
                            console.log('Recognition restart failed:', e);
                            setVoiceStatus('error');
                        }
                    }, 500); // Increased delay to prevent conflicts
                }
            };
        }
        
        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.abort();
                recognitionRef.current = null;
            }
        };
    }, []);

    // Auto-start voice control after permissions are granted, to support hands-free usage
    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => {
        let mounted = true;
        (async () => {
            if (!mounted) return;
            if (isEnabled) {
                try {
                    await navigator.mediaDevices.getUserMedia({ audio: true });
                    startListening();
                    // Check backend and DB status and announce once
                    try {
                        const res = await fetch(`${API_BASE}/health`);
                        const json = await res.json();
                        if (json && json.status === 'healthy') {
                            speakFeedback('Backend and database are connected. Voice control is active.');
                        }
                    } catch {}
                } catch (e) {
                    // Permission denied; we still keep voice active once user grants it
                    console.warn('Microphone permission not granted yet.');
                }
            }
        })();
        return () => { mounted = false; };
    }, [isEnabled]);

    // Watchdog to prevent long-term stall: if listening state hasn't changed in a while, restart
    useEffect(() => {
        if (watchdogIntervalRef.current) {
            clearInterval(watchdogIntervalRef.current);
            watchdogIntervalRef.current = null;
        }
        let lastStatus = voiceStatus;
        let unchangedCount = 0;
        watchdogIntervalRef.current = setInterval(() => {
            if (voiceStatus === lastStatus) {
                unchangedCount += 1;
            } else {
                unchangedCount = 0;
                lastStatus = voiceStatus;
            }
            // If stuck in 'ready' or 'listening' for too long without results, try a soft restart
            if (unchangedCount >= 60) { // ~60 * 2s = 2 minutes
                try {
                    if (recognitionRef.current) {
                        recognitionRef.current.abort();
                        setTimeout(() => {
                            try {
                                if (isEnabled) {
                                    recognitionRef.current.start();
                                    setIsListening(true);
                                }
                            } catch {}
                        }, 500);
                    }
                } catch {}
                unchangedCount = 0;
            }
        }, 2000);
        return () => {
            if (watchdogIntervalRef.current) {
                clearInterval(watchdogIntervalRef.current);
                watchdogIntervalRef.current = null;
            }
        };
    }, [voiceStatus, isEnabled]);

    const startListening = async () => {
        if (!recognitionRef.current || !isEnabled) {
            console.warn('Speech recognition not available or disabled');
            return;
        }

        // Check for microphone permission first
        try {
            await navigator.mediaDevices.getUserMedia({ audio: true });
        } catch (error) {
            console.error('Microphone permission denied:', error);
            setVoiceStatus('error');
            speakFeedback('Microphone access denied. Please grant permission and try again.');
            return;
        }

        try {
            if (startInProgressRef.current) {
                return;
            }
            startInProgressRef.current = true;
            if (isListening) {
                console.log('Already listening, stopping first...');
                recognitionRef.current.stop();
                await new Promise(resolve => setTimeout(resolve, 600));
            }
            // Double-check not already started before calling start
            setTimeout(() => {
                try {
                    if (!isListening && recognitionRef.current) {
                        recognitionRef.current.start();
                        setIsListening(true);
                    }
                } catch (e) {
                    console.warn('Recognition start error:', e);
                } finally {
                    startInProgressRef.current = false;
                }
            }, 50);
        } catch (error) {
            console.error('Failed to start recognition:', error);
            setVoiceStatus('error');
            speakFeedback('Failed to start voice control');
            startInProgressRef.current = false;
        }
    };

    const stopListening = () => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
            setIsListening(false);
            speakFeedback('Voice control stopped');
        }
    };

    const dispatchVoiceAction = (action, payload = {}) => {
        if (typeof window === 'undefined') {
            return { action, handled: false, feedback: '', suppressAutoFeedback: false, ...payload };
        }
        const detail = {
            action,
            handled: false,
            feedback: '',
            suppressAutoFeedback: false,
            ...payload
        };
        try {
            window.dispatchEvent(new CustomEvent('voicePageAction', { detail }));
        } catch (error) {
            console.error('Voice action dispatch failed:', error);
        }
        return detail;
    };

    const processVoiceCommand = async (command) => {
        console.log('Processing voice command:', command);
        // Log command to MongoDB if user is known
        try {
            const currentUser = userService.getCurrentUser();
            if (currentUser && currentUser.id) {
                await apiService.saveVoiceCommandDB({
                    user_id: currentUser.id,
                    command_text: command,
                    command_type: 'global_command',
                    language: 'en',
                    confidence_score: 0.9,
                    execution_successful: true,
                    response_text: null,
                    execution_time_ms: 0
                });
            }
        } catch (e) {
            console.warn('Voice command logging failed', e);
        }
        
        // Check for direct command matches
        if (globalCommands[command]) {
            try {
                await globalCommands[command]();
                speakFeedback(`Executed: ${command}`);
                
                // Send to backend for logging
                await fetch(`${API_BASE}/commands/execute-voice-command/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ command, source: 'global' })
                });
            } catch (error) {
                console.error('Command execution error:', error);
                speakFeedback('Command failed to execute');
            }
            return;
        }

        // Check for partial matches
        const partialMatch = Object.keys(globalCommands).find(cmd => 
            command.includes(cmd) || cmd.includes(command)
        );
        
        if (partialMatch) {
            try {
                await globalCommands[partialMatch]();
                speakFeedback(`Executed: ${partialMatch}`);
            } catch (error) {
                console.error('Partial command execution error:', error);
                speakFeedback('Command failed to execute');
            }
            return;
        }

        const pageDetail = dispatchVoiceAction(command, { source: 'speech' });
        if (pageDetail.handled) {
            if (!pageDetail.suppressAutoFeedback) {
                speakFeedback(pageDetail.feedback || `Executed: ${command}`);
            }
            return;
        }

        // Send unknown commands to backend for processing
        try {
            const response = await fetch(`${API_BASE}/commands/execute-voice-command/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ command })
            });
            
            const result = await response.json();
            if (result.success) {
                speakFeedback(result.result || 'Command executed');
            } else {
                speakFeedback(`Unknown command: ${command}. Say "help" for available commands.`);
            }
        } catch (error) {
            console.error('Backend command processing error:', error);
            speakFeedback('Command not recognized');
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/');
        speakFeedback('Logged out successfully');
    };

    const executePageAction = (action, payload = {}) => {
        const detail = dispatchVoiceAction(action, { source: 'global', ...payload });
        if (detail.handled) {
            if (!detail.suppressAutoFeedback && detail.feedback) {
                speakFeedback(detail.feedback);
            }
        } else if (!detail.suppressAutoFeedback) {
            speakFeedback(`${action} action triggered`);
        }
    };

    const focusField = (fieldName) => {
        // Focus specific form fields
        const selectors = {
            username: 'input[name="username"], input[type="text"]',
            password: 'input[name="password"], input[type="password"]',
            email: 'input[name="email"], input[type="email"]',
            name: 'input[name="name"], input[placeholder*="name"]'
        };
        
        const selector = selectors[fieldName];
        if (selector) {
            const field = document.querySelector(selector);
            if (field) {
                field.focus();
                speakFeedback(`Focused ${fieldName} field`);
            } else {
                speakFeedback(`${fieldName} field not found`);
            }
        }
    };

    const speakFeedback = async (text) => {
        try {
            await fetch(`${API_BASE}/narration/speak/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ text, immediate: 'true' })
            });
        } catch (error) {
            console.error('Speech feedback error:', error);
        }
    };

    const showHelp = () => {
        const helpText = `Voice commands available:
        Navigation: Say "Code Generation", "Learning Mode", "Collaboration", "Projects", "Voice Commands", or "Home"
        Authentication: Say "Login", "Sign Up", or "Logout"
        Actions: Say "Save", "Compile", "Run", "Clear", "Help"
        Form controls: Say "Focus Username", "Focus Password", "Submit"
        Voice control: Say "Stop Listening" or "Start Listening"`;
        
        speakFeedback(helpText);
    };

    const value = {
        isListening,
        isEnabled,
        setIsEnabled,
        currentPage,
        setCurrentPage,
        lastCommand,
        voiceStatus,
        startListening,
        stopListening,
        processVoiceCommand,
        speakFeedback,
        executePageAction,
        focusField
    };

    return (
        <VoiceControlContext.Provider value={value}>
            {children}
        </VoiceControlContext.Provider>
    );
};