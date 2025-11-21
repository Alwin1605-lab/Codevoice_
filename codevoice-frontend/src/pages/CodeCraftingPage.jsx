import React, { useState, useEffect } from 'react';
import {
    Container,
    Box,
    Typography,
    TextField,
    Button,
    MenuItem,
    Paper,
    CircularProgress,
    Alert,
    IconButton,
    Input
} from '@mui/material';
import { Build, ContentCopy, FileUpload, ContentPaste } from '@mui/icons-material';
import Recorder from '../components/Recorder';
import { useVoiceControl } from '../context/VoiceControlContext';
import apiService from '../services/apiService';
import TRANSCRIPTION_LANGUAGES from '../constants/transcriptionLanguages';

const CodeCraftingPage = () => {
    const { speakFeedback } = useVoiceControl();
    const [description, setDescription] = useState('');
    const [language, setLanguage] = useState('python');
    const [generatedCode, setGeneratedCode] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [recording, setRecording] = useState(false);
    const [micLoading, setMicLoading] = useState(false);
    const [transcriptionLanguage, setTranscriptionLanguage] = useState('en');
    const [nativeDescription, setNativeDescription] = useState('');
    const mediaRecorderRef = React.useRef(null);
    const audioChunksRef = React.useRef([]);

    const languages = [
        { value: 'python', label: 'Python' },
        { value: 'javascript', label: 'JavaScript' },
        { value: 'typescript', label: 'TypeScript' },
        { value: 'java', label: 'Java' },
        { value: 'cpp', label: 'C++' },
        { value: 'go', label: 'Go' },
        { value: 'rust', label: 'Rust' },
        { value: 'csharp', label: 'C#' },
        { value: 'php', label: 'PHP' },
        { value: 'ruby', label: 'Ruby' }
    ];

    useEffect(() => {
        const handleVoiceAction = (event) => {
            const detail = event.detail || {};
            const rawAction = typeof detail.action === 'string' ? detail.action : (typeof event.detail === 'string' ? event.detail : '');
            const action = rawAction.toLowerCase();
            let handled = false;
            const run = (fn) => {
                fn();
                handled = true;
                detail.suppressAutoFeedback = true;
            };

            if (action === 'craft' || action === 'generate') {
                run(handleCraft);
            } else if (action === 'copy') {
                run(handleCopy);
            } else if (action === 'clear') {
                run(handleClear);
            }

            if (handled) {
                detail.handled = true;
            }
        };

        window.addEventListener('voicePageAction', handleVoiceAction);
        return () => window.removeEventListener('voicePageAction', handleVoiceAction);
    }, [description, language, generatedCode]);

    const startRecording = async () => {
        try {
            setMicLoading(true);
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data && e.data.size > 0) audioChunksRef.current.push(e.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                try {
                    const res = await apiService.transcribeAudio(audioBlob, transcriptionLanguage);
                    if (res && res.transcript) {
                        const englishTranscript = res.transcript || '';
                        const nativeTranscript = res.transcript_native || englishTranscript;
                        setDescription(prev => prev ? `${prev}\n${englishTranscript}` : englishTranscript);
                        setNativeDescription(prev => prev ? `${prev}\n${nativeTranscript}` : nativeTranscript);
                        speakFeedback('Transcription added');
                    } else if (res && res.error) {
                        setError(res.error);
                        speakFeedback('Transcription failed');
                    } else {
                        setError('No transcript received');
                        speakFeedback('No transcription received');
                    }
                } catch (err) {
                    console.error('Transcription error', err);
                    setError('Transcription failed');
                    speakFeedback('Transcription failed');
                } finally {
                    setMicLoading(false);
                    setRecording(false);
                }
            };

            mediaRecorder.start();
            setRecording(true);
        } catch (err) {
            console.error('Failed to start recording', err);
            setError('Microphone not available or permission denied');
            setMicLoading(false);
            setRecording(false);
        }
    };

    const stopRecording = () => {
        try {
            if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
                mediaRecorderRef.current.stop();
            }
        } catch (e) {
            console.warn('Stop recording failed', e);
            setRecording(false);
            setMicLoading(false);
        }
    };

    const handlePasteFromClipboard = async () => {
        try {
            const text = await navigator.clipboard.readText();
            if (text) {
                setDescription(prev => prev ? prev + '\n' + text : text);
                speakFeedback('Pasted from clipboard');
            } else {
                setError('Clipboard is empty');
            }
        } catch (err) {
            console.error('Paste failed', err);
            setError('Failed to read clipboard');
        }
    };

    const handleUploadAudio = async (e) => {
        const file = e.target.files && e.target.files[0];
        if (!file) return;
        setMicLoading(true);
        try {
            const res = await apiService.transcribeAudio(file, transcriptionLanguage);
            if (res && res.transcript) {
                const englishTranscript = res.transcript || '';
                const nativeTranscript = res.transcript_native || englishTranscript;
                setDescription(prev => prev ? `${prev}\n${englishTranscript}` : englishTranscript);
                setNativeDescription(prev => prev ? `${prev}\n${nativeTranscript}` : nativeTranscript);
                speakFeedback('Transcription added');
            } else {
                setError(res.error || 'No transcript received');
            }
        } catch (err) {
            console.error('Audio upload/transcribe failed', err);
            setError('Transcription failed');
        } finally {
            setMicLoading(false);
            e.target.value = null;
        }
    };

    const handleCraft = async () => {
        if (!description.trim()) {
            setError('Please describe what code you want to generate');
            speakFeedback('Please describe what code you want to generate');
            return;
        }

        setLoading(true);
        setError('');
        speakFeedback('Crafting your code');

        try {
            // apiService.generateCode expects (prompt, type) and returns response object or data
            const result = await apiService.generateCode(description, language);

            // apiService returns the parsed data (see apiService.js: generateCode returns response.data)
            // Accept several possible shapes for backward compatibility
            const data = result || {};
            const code = data.code || data.generated_code || data.result || data.output;

            if (code && typeof code === 'string' && code.trim().length > 0) {
                setGeneratedCode(code);
                speakFeedback('Code crafted successfully');
            } else {
                // Provide richer debug info in console and surface a friendly error
                console.warn('Code generation returned empty payload', data);
                throw new Error('No code returned from API');
            }
        } catch (err) {
            console.error('Code crafting error:', err);
            const errorMsg = err.response?.data?.detail || 'Failed to craft code';
            setError(errorMsg);
            speakFeedback('Failed to craft code. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleCopy = () => {
        if (generatedCode) {
            navigator.clipboard.writeText(generatedCode);
            speakFeedback('Code copied to clipboard');
        }
    };

    const handleClear = () => {
        setDescription('');
        setNativeDescription('');
        setGeneratedCode('');
        setError('');
        speakFeedback('Cleared');
    };

    return (
        <Container maxWidth="xl" sx={{ py: 4 }}>
            <Box sx={{ mb: 4 }}>
                <Typography variant="h3" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Build fontSize="large" />
                    Code Crafting
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    Describe the code and the logic, and we'll generate it using Groq AI
                </Typography>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
                    {error}
                </Alert>
            )}

            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
                <TextField
                    fullWidth
                    multiline
                    rows={6}
                    label="Code Description (English)"
                    placeholder="Provide the English summary that will be sent to the AI"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    sx={{ mb: 3 }}
                />

                <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Native Transcript"
                    placeholder="Optional transcript in your spoken language"
                    value={nativeDescription}
                    onChange={(e) => setNativeDescription(e.target.value)}
                    sx={{ mb: 3 }}
                />

                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                    <TextField
                        select
                        label="Language"
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        sx={{ minWidth: 200 }}
                    >
                        {languages.map((lang) => (
                            <MenuItem key={lang.value} value={lang.value}>
                                {lang.label}
                            </MenuItem>
                        ))}
                    </TextField>

                    <TextField
                        select
                        label="Speech Language"
                        value={transcriptionLanguage}
                        onChange={(e) => setTranscriptionLanguage(e.target.value)}
                        sx={{ minWidth: 200 }}
                    >
                        {TRANSCRIPTION_LANGUAGES.map((lang) => (
                            <MenuItem key={lang.value} value={lang.value}>
                                {lang.label}
                            </MenuItem>
                        ))}
                    </TextField>

                    <Button
                        variant="contained"
                        size="large"
                        startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Build />}
                        onClick={handleCraft}
                        disabled={loading || !description.trim()}
                    >
                        {loading ? 'Crafting...' : 'Craft Code'}
                    </Button>

                    {/* Combined Record -> Transcribe (previous behavior) */}
                    <Recorder
                        tooltip="Record → Transcribe → Generate"
                        onRecorded={async (blob) => {
                            // Combined flow: transcribe then generate
                            try {
                                setLoading(true);
                                setError('');
                                speakFeedback('Processing audio and generating code');
                                // Transcribe
                                const tRes = await apiService.transcribeAudio(blob, transcriptionLanguage);
                                const transcript = tRes?.transcript || tRes?.text || '';
                                const nativeTranscript = tRes?.transcript_native || transcript;
                                const combinedDescription = description ? `${description}\n${transcript}` : transcript;
                                const combinedNative = nativeDescription ? `${nativeDescription}\n${nativeTranscript}` : nativeTranscript;
                                if (!combinedDescription.trim()) {
                                    setError('No transcription produced from audio');
                                    return;
                                }
                                setDescription(combinedDescription);
                                setNativeDescription(combinedNative);
                                // Generate
                                const gen = await apiService.generateCode(combinedDescription, language);
                                const data = gen || {};
                                const code = data.code || data.generated_code || data.result || data.output;
                                if (!code) {
                                    console.warn('Generator returned empty payload', gen);
                                    setError('No code returned from generator');
                                    return;
                                }
                                setGeneratedCode(code);
                                speakFeedback('Code crafted successfully from audio');
                            } catch (err) {
                                console.error('Record->Generate failed', err);
                                setError('Failed to generate from audio');
                            } finally {
                                setLoading(false);
                            }
                        }}
                        renderButton={({ isRecording, start, stop }) => (
                            <IconButton
                                title={isRecording ? 'Stop and generate' : 'Record and generate'}
                                onClick={() => (isRecording ? stop() : start())}
                                color={isRecording ? 'error' : 'default'}
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 14 0h-2zM11 19a1 1 0 0 0 2 0v-1h-2v1z"/></svg>
                            </IconButton>
                        )}
                    />

                    <input
                        accept="audio/*"
                        id="upload-audio"
                        type="file"
                        style={{ display: 'none' }}
                        onChange={handleUploadAudio}
                    />
                    <label htmlFor="upload-audio">
                        <IconButton component="span" title="Upload audio file">
                            <FileUpload />
                        </IconButton>
                    </label>

                    <IconButton title="Paste from clipboard" onClick={handlePasteFromClipboard}>
                        <ContentPaste />
                    </IconButton>

                    {generatedCode && (
                        <>
                            <Button
                                variant="outlined"
                                startIcon={<ContentCopy />}
                                onClick={handleCopy}
                            >
                                Copy
                            </Button>
                            <Button
                                variant="outlined"
                                onClick={handleClear}
                            >
                                Clear
                            </Button>
                        </>
                    )}
                </Box>
            </Paper>

            {generatedCode && (
                <Paper elevation={3} sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        Generated Code:
                    </Typography>
                    <Box
                        component="pre"
                        sx={{
                            backgroundColor: '#1e1e1e',
                            color: '#d4d4d4',
                            padding: 2,
                            borderRadius: 1,
                            overflow: 'auto',
                            maxHeight: '500px',
                            fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                            fontSize: '14px',
                            lineHeight: 1.5
                        }}
                    >
                        <code>{generatedCode}</code>
                    </Box>
                </Paper>
            )}

            <Box sx={{ mt: 3 }}>
                <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                    💡 Voice Commands: "craft" or "generate" to create code, "copy" to copy to clipboard, "clear" to reset
                </Typography>
            </Box>
        </Container>
    );
};

export default CodeCraftingPage;
