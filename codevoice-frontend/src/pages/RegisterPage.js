import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useVoiceControl } from '../context/VoiceControlContext';
import {
    Container,
    Paper,
    Button,
    Typography,
    Box,
    Alert,
    TextField
} from '@mui/material';
import HelpIcon from '@mui/icons-material/Help';
import ClearIcon from '@mui/icons-material/Clear';
import { VoiceInput } from '../components/VoiceInput';

const RegisterPage = () => {
    const navigate = useNavigate();
    const { register } = useAuth();
    const { speakFeedback } = useVoiceControl();
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    
    const nameRef = useRef(null);
    const emailRef = useRef(null);
    const passwordRef = useRef(null);
    const confirmPasswordRef = useRef(null);

    const speak = speakFeedback;

    // Voice page actions
    const voicePageActions = {
        'focus name': () => {
            nameRef.current?.focus();
            speak('Name field focused');
        },
        'focus full name': () => voicePageActions['focus name'](),
        'focus email': () => {
            emailRef.current?.focus();
            speak('Email field focused');
        },
        'focus password': () => {
            passwordRef.current?.focus();
            speak('Password field focused');
        },
        'focus confirm password': () => {
            confirmPasswordRef.current?.focus();
            speak('Confirm password field focused');
        },
        'submit': () => {
            handleSubmit();
            speak('Submitting registration form');
        },
        'sign up': () => voicePageActions['submit'](),
        'register': () => voicePageActions['submit'](),
        'clear': () => clearForm(),
        'clear all': () => clearForm(),
        'clear form': () => clearForm(),
        'help': () => showHelp(),
        'voice help': () => showHelp()
    };

    // Helper functions
    const clearForm = () => {
        setFormData({
            name: '',
            email: '',
            password: '',
            confirmPassword: ''
        });
        setError('');
        speak('Form cleared');
    };

    const showHelp = () => {
        const commands = [
            'Voice commands available:',
            'Focus Name - Focus the name field',
            'Focus Email - Focus the email field', 
            'Focus Password - Focus the password field',
            'Focus Confirm Password - Focus the confirm password field',
            'Submit - Submit the registration form',
            'Clear - Clear all form fields',
            'Help - Show this help'
        ];
        speak(commands.join('. '));
    };

    useEffect(() => {
        // Voice action event listener
        const handleVoiceAction = (event) => {
            const action = voicePageActions[event.detail];
            if (action) {
                action();
            }
        };

        window.addEventListener('voicePageAction', handleVoiceAction);
        return () => window.removeEventListener('voicePageAction', handleVoiceAction);
    }, []);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        if (e) e.preventDefault();
        
        if (!formData.name.trim()) {
            setError('Name is required');
            speak('Name is required');
            return;
        }
        
        if (!formData.email.trim()) {
            setError('Email is required');
            speak('Email is required');
            return;
        }
        
        if (!formData.password.trim()) {
            setError('Password is required');
            speak('Password is required');
            return;
        }
        
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            speak('Passwords do not match');
            return;
        }

        try {
            await register({
                name: formData.name,
                email: formData.email,
                password: formData.password
            });
            speak('Registration successful. Redirecting to login page.');
            navigate('/login');
        } catch (err) {
            setError(err.message);
            speak('Registration failed. ' + err.message);
        }
    };

    return (
        <Container maxWidth="sm">
            <Box sx={{ mt: 8 }}>
                <Paper elevation={3} sx={{ p: 4 }}>
                    <Typography variant="h4" component="h1" gutterBottom align="center">
                        Register
                    </Typography>
                    
                    {error && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {error}
                        </Alert>
                    )}

                    <form onSubmit={handleSubmit}>
                        <TextField
                            inputRef={nameRef}
                            label="Full Name"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            fullWidth
                            margin="normal"
                            required
                        />
                        <TextField
                            inputRef={emailRef}
                            label="Email"
                            name="email"
                            type="email"
                            value={formData.email}
                            onChange={handleChange}
                            fullWidth
                            margin="normal"
                            required
                        />
                        <TextField
                            inputRef={passwordRef}
                            label="Password"
                            name="password"
                            type="password"
                            value={formData.password}
                            onChange={handleChange}
                            fullWidth
                            margin="normal"
                            required
                        />
                        <TextField
                            inputRef={confirmPasswordRef}
                            label="Confirm Password"
                            name="confirmPassword"
                            type="password"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            fullWidth
                            margin="normal"
                            required
                        />
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            color="primary"
                            sx={{ mt: 3, mb: 2 }}
                        >
                            Register
                        </Button>
                        
                        <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                            <Button
                                onClick={clearForm}
                                variant="outlined"
                                startIcon={<ClearIcon />}
                                sx={{ flex: 1 }}
                            >
                                Clear Form
                            </Button>
                            <Button
                                onClick={showHelp}
                                variant="outlined"
                                startIcon={<HelpIcon />}
                                sx={{ flex: 1 }}
                            >
                                Voice Help
                            </Button>
                        </Box>
                    </form>
                    
                    <Box sx={{ textAlign: 'center', mt: 2 }}>
                        <Typography variant="body2">
                            Already have an account?{' '}
                            <Link to="/login">Login here</Link>
                        </Typography>
                    </Box>
                </Paper>
            </Box>
        </Container>
    );
};

export default RegisterPage;