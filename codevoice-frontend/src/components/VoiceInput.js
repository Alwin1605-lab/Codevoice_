import React, { useState, useCallback, useEffect } from 'react';
import {
    FormControl,
    InputLabel,
    OutlinedInput,
    InputAdornment,
    IconButton
} from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';

export const useVoiceInput = () => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [recognition, setRecognition] = useState(null);
    
    const startListening = useCallback(() => {
        if ('webkitSpeechRecognition' in window) {
            const newRecognition = new window.webkitSpeechRecognition();
            newRecognition.continuous = false;
            newRecognition.interimResults = true;

            newRecognition.onstart = () => {
                setIsListening(true);
            };

            newRecognition.onresult = (event) => {
                const transcript = Array.from(event.results)
                    .map(result => result[0])
                    .map(result => result.transcript)
                    .join('');
                setTranscript(transcript);
            };

            newRecognition.onerror = (event) => {
                console.error('Speech recognition error', event.error);
                setIsListening(false);
                setRecognition(null);
            };

            newRecognition.onend = () => {
                setIsListening(false);
                setRecognition(null);
            };

            setRecognition(newRecognition);
            newRecognition.start();
        } else {
            alert('Speech recognition is not supported in this browser. Please use Chrome.');
        }
    }, []);

    const stopListening = useCallback(() => {
        setIsListening(false);
        if (recognition && typeof recognition.stop === 'function') {
            recognition.stop();
        }
        setRecognition(null);
    }, [recognition]);

    const resetTranscript = useCallback(() => {
        setTranscript('');
    }, []);

    return {
        isListening,
        transcript,
        startListening,
        stopListening,
        resetTranscript
    };
};

// Create a voice-enabled text input component
export const VoiceInput = ({ label, value, onChange, multiline = false, rows = 1 }) => {
    const { isListening, transcript, startListening, stopListening, resetTranscript } = useVoiceInput();
    const [internalValue, setInternalValue] = useState(value || '');

    const handleVoiceInput = useCallback(() => {
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    }, [isListening, startListening, stopListening]);

    useEffect(() => {
        if (transcript) {
            const newValue = internalValue + ' ' + transcript;
            setInternalValue(newValue);
            onChange(newValue);
            resetTranscript();
        }
    }, [transcript, onChange, resetTranscript]); // Removed internalValue from dependencies

    const handleTextInput = (e) => {
        setInternalValue(e.target.value);
        onChange(e.target.value);
    };

    return (
        <FormControl fullWidth variant="outlined" margin="normal">
            <InputLabel>{label}</InputLabel>
            <OutlinedInput
                value={internalValue}
                onChange={handleTextInput}
                multiline={multiline}
                rows={rows}
                endAdornment={
                    <InputAdornment position="end">
                        <IconButton
                            onClick={handleVoiceInput}
                            edge="end"
                        >
                            {isListening ? <MicOffIcon color="error" /> : <MicIcon />}
                        </IconButton>
                    </InputAdornment>
                }
                label={label}
            />
        </FormControl>
    );
};