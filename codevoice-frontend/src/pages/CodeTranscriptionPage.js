import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useVoiceControl } from '../context/VoiceControlContext';
import apiService from '../services/apiService';
import TRANSCRIPTION_LANGUAGES from '../constants/transcriptionLanguages';
import {
    Container,
    Paper,
    Typography,
    Box,
    Button,
    CircularProgress,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Chip,
    Grid,
    TextField
} from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import ClearIcon from '@mui/icons-material/Clear';
import SaveIcon from '@mui/icons-material/Save';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { Editor } from '@monaco-editor/react';

const CodeTranscriptionPage = () => {
    const { user } = useAuth();
    const { speakFeedback } = useVoiceControl();
    const [isRecording, setIsRecording] = useState(false);
    const [transcribedCode, setTranscribedCode] = useState('');
    const [loading, setLoading] = useState(false);
    const [language, setLanguage] = useState('python');
    const [languages, setLanguages] = useState(['python','javascript','java','cpp','c']);
    const [compileOutput, setCompileOutput] = useState('');
    const [compiling, setCompiling] = useState(false);
    const [transcriptionLanguage, setTranscriptionLanguage] = useState('en');
    const [nativeTranscript, setNativeTranscript] = useState('');
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const outputRef = useRef(null);

    const speak = speakFeedback;

    // Voice page actions
    const voicePageActions = {
        'start recording': () => {
            if (!isRecording) {
                startRecording();
                speak('Starting voice recording for code transcription.');
            } else {
                speak('Recording is already in progress.');
            }
        },
        'stop recording': () => {
            if (isRecording) {
                stopRecording();
                speak('Stopping recording and transcribing code.');
            } else {
                speak('No recording in progress.');
            }
        },
        'start transcription': () => voicePageActions['start recording'](),
        'stop transcription': () => voicePageActions['stop recording'](),
        'compile': () => handleCompile(),
        'run code': () => handleCompile(),
        'clear': () => clearAll(),
        'clear all': () => clearAll(),
        'save': () => handleSaveFile(),
        'save file': () => handleSaveFile(),
        'copy': () => handleCopyCode(),
        'copy code': () => handleCopyCode(),
        'english speech': () => { setTranscriptionLanguage('en'); speak('Speech language switched to English'); },
        'tamil speech': () => { setTranscriptionLanguage('ta'); speak('Speech language switched to Tamil'); },
        'hindi speech': () => { setTranscriptionLanguage('hi'); speak('Speech language switched to Hindi'); },
        // Extended language voice mappings
        'python': () => { setLanguage('python'); speak('Language switched to Python'); },
        'javascript': () => { setLanguage('javascript'); speak('Language switched to JavaScript'); },
        'typescript': () => { if (languages.includes('typescript')) { setLanguage('typescript'); speak('Language switched to TypeScript'); } },
        'java': () => { setLanguage('java'); speak('Language switched to Java'); },
        'c plus plus': () => { setLanguage('cpp'); speak('Language switched to C plus plus'); },
        'c++': () => { setLanguage('cpp'); speak('Language switched to C plus plus'); },
        'go': () => { if (languages.includes('go')) { setLanguage('go'); speak('Language switched to Go'); } },
        'golang': () => { if (languages.includes('go')) { setLanguage('go'); speak('Language switched to Go'); } },
        'rust': () => { if (languages.includes('rust')) { setLanguage('rust'); speak('Language switched to Rust'); } },
        'php': () => { if (languages.includes('php')) { setLanguage('php'); speak('Language switched to PHP'); } },
        'ruby': () => { if (languages.includes('ruby')) { setLanguage('ruby'); speak('Language switched to Ruby'); } },
        'c sharp': () => { if (languages.includes('csharp')) { setLanguage('csharp'); speak('Language switched to C sharp'); } },
        'c#': () => { if (languages.includes('csharp')) { setLanguage('csharp'); speak('Language switched to C sharp'); } },
        'c': () => { setLanguage('c'); speak('Language switched to C'); },
        'help': () => showHelp(),
        'voice help': () => showHelp()
    };

    // Helper functions
    const clearAll = () => {
        setTranscribedCode('');
        setCompileOutput('');
        setNativeTranscript('');
        speak('All content cleared.');
    };

    const showHelp = () => {
        const commands = [
            'Voice commands available:',
            'Start Recording - Begin voice to code transcription',
            'Stop Recording - End recording and transcribe',
            'Compile - Run the transcribed code',
            'Clear - Clear all content',
            'Save - Save transcribed code to file',
            'Copy - Copy code to clipboard',
            'Python, JavaScript, Java, C, C++ - Switch language',
            'Help - Show this help'
        ];
        speak(commands.join('. '));
    };

    const handleCopyCode = async () => {
        if (!transcribedCode) {
            speak('No code to copy');
            return;
        }
        try {
            await navigator.clipboard.writeText(transcribedCode);
            speak('Code copied to clipboard.');
        } catch (err) {
            speak('Failed to copy code.');
        }
    };

    const handleSaveFile = () => {
        if (!transcribedCode) {
            speak('No code to save');
            return;
        }
        const blob = new Blob([transcribedCode], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'transcribed_code.' + (language === 'python' ? 'py' : language === 'javascript' ? 'js' : language === 'java' ? 'java' : 'txt');
        a.click();
        window.URL.revokeObjectURL(url);
        speak('File saved successfully.');
    };

    useEffect(() => {
        // Initialize any necessary audio/transcription services here
        // Load available languages from backend (Judge0 info)
        (async () => {
            try {
                const info = await apiService.getAvailableLanguages();
                let langs = [];
                if (Array.isArray(info)) {
                    langs = info;
                } else if (info && Array.isArray(info.supported_languages)) {
                    langs = info.supported_languages;
                } else if (info && info.languages && Array.isArray(info.languages)) {
                    langs = info.languages;
                }
                langs = langs.map(l => (typeof l === 'string' ? l.toLowerCase() : (l.id || l.name || '').toLowerCase())).filter(Boolean);
                if (!langs.length) langs = ['python','javascript','typescript','java','cpp','c','go','rust','php','ruby'];
                setLanguages(Array.from(new Set(langs)));
            } catch (e) {
                setLanguages(['python','javascript','typescript','java','cpp','c','go','rust','php','ruby']);
            }
        })();

        // Voice action event listener
        const handleVoiceAction = (event) => {
            const detail = event.detail || {};
            const rawKey = typeof detail.action === 'string' ? detail.action : (typeof event.detail === 'string' ? event.detail : '');
            if (!rawKey) return;
            const key = rawKey.toLowerCase();
            const action = voicePageActions[key];
            if (action) {
                action();
                detail.handled = true;
                detail.suppressAutoFeedback = true;
            }
        };

        window.addEventListener('voicePageAction', handleVoiceAction);
        return () => window.removeEventListener('voicePageAction', handleVoiceAction);
    }, []);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    audioChunksRef.current.push(e.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                await handleTranscribe(audioBlob);
            };

            mediaRecorder.start();
            setIsRecording(true);
            speak('Recording started. Speak your code and I will transcribe it.');
        } catch (error) {
            console.error('Failed to start recording:', error);
            speak('Failed to access microphone. Please check permissions.');
        }
    };

    const stopRecording = async () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
            speak('Recording stopped. Transcribing your code now.');
        }
    };

    const handleTranscribe = async (audioBlob) => {
        setLoading(true);
        try {
            const result = await apiService.transcribeAudio(audioBlob, transcriptionLanguage);
            const transcript = result?.transcript || result?.text || '';
            const native = result?.transcript_native || transcript;
            if (transcript) {
                setTranscribedCode(prev => (prev ? prev + '\n' : '') + transcript);
                setNativeTranscript(prev => prev ? `${prev}\n${native}` : native);
                speak('Code transcribed successfully.');
            } else {
                speak('No code could be transcribed from the audio.');
            }
        } catch (e) {
            console.error('Transcription failed', e);
            speak('Transcription failed. Please try again.');
        }
        setLoading(false);
    };

    const addNewLine = () => {
        setTranscribedCode(prev => prev + '\n');
    };

    const clearCode = () => {
        setTranscribedCode('');
    };

    const handleCompile = async () => {
        if (!transcribedCode.trim()) {
            speak('Please add some code to compile');
            return;
        }

        setCompiling(true);
        setCompileOutput('');
        speak('Compiling and running code...');
        
        try {
            const result = await apiService.compileCode(transcribedCode, language, '');
            let output = '';
            
            if (result.compile_output) {
                output += `Compile Output:\n${result.compile_output}\n\n`;
            }
            
            if (result.stdout) {
                output += `Output:\n${result.stdout}\n`;
            }
            
            if (result.stderr) {
                output += `Errors:\n${result.stderr}\n`;
            }
            
            if (!output.trim()) {
                output = 'Code compiled and executed successfully with no output.';
            }
            
            setCompileOutput(output);
            speak('Compilation finished.');
        } catch (error) {
            console.error('Compile failed:', error);
            setCompileOutput(`Compilation failed: ${error.message || 'Unknown error'}`);
            speak('Compilation failed.');
        }
        
        setCompiling(false);
    };

    // Auto-scroll output when it changes
    useEffect(() => {
        if (outputRef.current) {
            outputRef.current.scrollTo({ top: outputRef.current.scrollHeight, behavior: 'smooth' });
        }
    }, [compileOutput]);

    const handleSave = () => {
        if (!transcribedCode.trim()) {
            alert('No code to save');
            return;
        }

        const filename = `transcribed_code.${language === 'cpp' ? 'cpp' : language === 'javascript' ? 'js' : language}`;
        const blob = new Blob([transcribedCode], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const handleCopy = async () => {
        if (!transcribedCode.trim()) {
            alert('No code to copy');
            return;
        }

        try {
            await navigator.clipboard.writeText(transcribedCode);
            alert('Code copied to clipboard!');
        } catch (error) {
            console.error('Failed to copy:', error);
            alert('Failed to copy code to clipboard');
        }
    };

    const scrollDelta = 300;
    const voiceKeywords = {
        "Brackets & Parentheses": [
            { say: "open parenthesis", gets: "(" },
            { say: "close parenthesis", gets: ")" },
            { say: "open bracket", gets: "[" },
            { say: "close bracket", gets: "]" },
            { say: "open brace", gets: "{" },
            { say: "close brace", gets: "}" },
            { say: "open angle bracket", gets: "<" },
            { say: "close angle bracket", gets: ">" }
        ],
        "Operators": [
            { say: "plus", gets: "+" },
            { say: "minus", gets: "-" },
            { say: "times", gets: "*" },
            { say: "divide", gets: "/" },
            { say: "modulo", gets: "%" },
            { say: "power", gets: "**" },
            { say: "floor divide", gets: "//" },
            { say: "equals", gets: "=" },
            { say: "plus equals", gets: "+=" },
            { say: "minus equals", gets: "-=" },
            { say: "times equals", gets: "*=" }
        ],
        "Comparisons": [
            { say: "double equals", gets: "==" },
            { say: "not equal", gets: "!=" },
            { say: "less than", gets: "<" },
            { say: "greater than", gets: ">" },
            { say: "less than or equal to", gets: "<=" },
            { say: "greater than or equal to", gets: ">=" },
            { say: "right arrow", gets: "->" }
        ],
        "Logical": [
            { say: "and", gets: " and " },
            { say: "or", gets: " or " },
            { say: "not", gets: " not " },
            { say: "logical and", gets: "&&" },
            { say: "logical or", gets: "||" }
        ],
        "Punctuation": [
            { say: "semicolon", gets: ";" },
            { say: "colon", gets: ":" },
            { say: "comma", gets: "," },
            { say: "period", gets: "." },
            { say: "exclamation mark", gets: "!" },
            { say: "question mark", gets: "?" },
            { say: "underscore", gets: "_" },
            { say: "hash", gets: "#" },
            { say: "at", gets: "@" }
        ],
        "Quotes & Strings": [
            { say: "double quote", gets: '"' },
            { say: "single quote", gets: "'" },
            { say: "backtick", gets: "`" }
        ],
        "Special Commands": [
            { say: "new line", gets: "\\n (line break)" },
            { say: "tab", gets: "\\t (tab)" },
            { say: "space", gets: " (space)" }
        ]
    };

    // Page-specific voice actions for output scrolling
    voicePageActions['scroll down'] = () => {
        if (outputRef.current) outputRef.current.scrollBy({ top: scrollDelta, behavior: 'smooth' });
    };
    voicePageActions['scroll up'] = () => {
        if (outputRef.current) outputRef.current.scrollBy({ top: -scrollDelta, behavior: 'smooth' });
    };

    return (
        <Container maxWidth="lg">
            <Box sx={{ mt: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Live Code Transcription{user?.name ? ` — Hello, ${user.name}` : ''}
                </Typography>
                <Typography color="textSecondary" paragraph>
                    Speak your code and watch it appear in real-time
                </Typography>

                <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
                    <FormControl sx={{ minWidth: 200 }}>
                        <InputLabel>Language</InputLabel>
                        <Select value={language} label="Language" onChange={(e) => {
                            setLanguage(e.target.value);
                            speak(`Language switched to ${e.target.value}`);
                        }}>
                            {languages.map((lang) => (
                                <MenuItem key={lang} value={lang}>{lang.toUpperCase()}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <FormControl sx={{ minWidth: 200 }}>
                        <InputLabel>Speech Language</InputLabel>
                        <Select
                            value={transcriptionLanguage}
                            label="Speech Language"
                            onChange={(e) => {
                                setTranscriptionLanguage(e.target.value);
                                const langLabel = TRANSCRIPTION_LANGUAGES.find(l => l.value === e.target.value)?.label || e.target.value;
                                speak(`Speech language switched to ${langLabel}`);
                            }}
                        >
                            {TRANSCRIPTION_LANGUAGES.map((lang) => (
                                <MenuItem key={lang.value} value={lang.value}>{lang.label}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <Button
                        variant="contained"
                        color={isRecording ? "secondary" : "primary"}
                        startIcon={isRecording ? <StopIcon /> : <MicIcon />}
                        onClick={isRecording ? stopRecording : startRecording}
                        disabled={loading}
                    >
                        {isRecording ? 'Stop Recording' : 'Start Recording'}
                    </Button>
                    <Button
                        variant="outlined"
                        onClick={addNewLine}
                        disabled={loading}
                    >
                        Add New Line
                    </Button>
                    <Button
                        variant="contained"
                        color="success"
                        onClick={handleCompile}
                        disabled={loading || compiling || !transcribedCode.trim()}
                    >
                        {compiling ? 'Compiling...' : 'Compile & Run'}
                    </Button>
                    <Button
                        variant="outlined"
                        onClick={handleSaveFile}
                        disabled={loading || !transcribedCode.trim()}
                        startIcon={<SaveIcon />}
                    >
                        Save
                    </Button>
                    <Button
                        variant="outlined"
                        onClick={handleCopyCode}
                        disabled={loading || !transcribedCode.trim()}
                    >
                        Copy
                    </Button>
                    <Button
                        variant="outlined"
                        color="error"
                        onClick={clearAll}
                        disabled={loading}
                        startIcon={<ClearIcon />}
                    >
                        Clear
                    </Button>
                    <Button
                        variant="outlined"
                        onClick={showHelp}
                        startIcon={<HelpOutlineIcon />}
                    >
                        Voice Help
                    </Button>
                </Box>

                <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
                    <Typography variant="subtitle1" gutterBottom>
                        Native Transcript
                    </Typography>
                    <TextField
                        fullWidth
                        multiline
                        minRows={3}
                        placeholder="Original-language transcription appears here"
                        value={nativeTranscript}
                        onChange={(e) => setNativeTranscript(e.target.value)}
                    />
                </Paper>

                {/* Voice Keywords Guide */}
                <Box sx={{ mb: 3 }}>
                    <Accordion>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <HelpOutlineIcon color="primary" />
                                <Typography variant="h6">Voice Keywords Guide</Typography>
                                <Typography variant="body2" color="textSecondary">
                                    - What to say for symbols and operators
                                </Typography>
                            </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                            <Grid container spacing={3}>
                                {Object.entries(voiceKeywords).map(([category, keywords]) => (
                                    <Grid size={{ xs: 12, md: 6, lg: 4 }} key={category}>
                                        <Paper sx={{ p: 2, height: '100%' }}>
                                            <Typography variant="subtitle1" gutterBottom color="primary" sx={{ fontWeight: 'bold' }}>
                                                {category}
                                            </Typography>
                                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                                {keywords.map((item, idx) => (
                                                    <Box key={idx} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                        <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                                                            "{item.say}"
                                                        </Typography>
                                                        <Chip 
                                                            label={item.gets} 
                                                            size="small" 
                                                            variant="outlined"
                                                            sx={{ fontFamily: 'monospace' }}
                                                        />
                                                    </Box>
                                                ))}
                                            </Box>
                                        </Paper>
                                    </Grid>
                                ))}
                            </Grid>
                            <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                                <Typography variant="body2" color="textSecondary">
                                    <strong>Tips:</strong>
                                    <br />• Speak clearly and pause briefly between symbols
                                    <br />• Say "new line" to go to the next line
                                    <br />• Use "space" for explicit spacing between words
                                    <br />• The system automatically handles common programming patterns
                                </Typography>
                            </Box>
                        </AccordionDetails>
                    </Accordion>
                </Box>

                {loading && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <CircularProgress size={20} />
                        <Typography>Transcribing...</Typography>
                    </Box>
                )}

                {compiling && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <CircularProgress size={20} />
                        <Typography>Compiling and running code...</Typography>
                    </Box>
                )}

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '70vh' }}>
                    {/* Code Editor */}
                    <Paper elevation={3} sx={{ flex: 1, minHeight: '40vh' }}>
                        <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Typography variant="subtitle2">Code Editor</Typography>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                                <Button size="small" onClick={() => voicePageActions['scroll up']?.()}>Scroll Up</Button>
                                <Button size="small" onClick={() => voicePageActions['scroll down']?.()}>Scroll Down</Button>
                            </Box>
                        </Box>
                        <Editor
                            height="calc(100% - 40px)"
                            defaultLanguage={language === 'cpp' ? 'cpp' : language}
                            value={transcribedCode}
                            options={{
                                readOnly: loading,
                                minimap: { enabled: false },
                                fontSize: 14
                            }}
                            onChange={(value) => setTranscribedCode(value || '')}
                        />
                    </Paper>

                    {/* Output Panel below editor */}
                    <Paper elevation={3} sx={{ flex: 1, minHeight: '25vh' }}>
                        <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Typography variant="subtitle2">Output</Typography>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                                <Button size="small" onClick={() => { if (outputRef.current) outputRef.current.scrollTo({ top: 0, behavior: 'smooth' }); }}>Top</Button>
                                <Button size="small" onClick={() => { if (outputRef.current) outputRef.current.scrollTo({ top: outputRef.current.scrollHeight, behavior: 'smooth' }); }}>Bottom</Button>
                            </Box>
                        </Box>
                        <Box ref={outputRef} sx={{ p: 2, height: 'calc(100% - 40px)', overflow: 'auto', bgcolor: 'background.default' }}>
                            {compileOutput ? (
                                <Typography
                                    component="pre"
                                    sx={{ 
                                        fontFamily: 'monospace', 
                                        fontSize: 12, 
                                        whiteSpace: 'pre-wrap',
                                        margin: 0
                                    }}
                                >
                                    {compileOutput}
                                </Typography>
                            ) : (
                                <Typography variant="body2" color="textSecondary">No output yet. Compile & Run to see results here.</Typography>
                            )}
                        </Box>
                    </Paper>
                </Box>
            </Box>
        </Container>
    );
};

export default CodeTranscriptionPage;
