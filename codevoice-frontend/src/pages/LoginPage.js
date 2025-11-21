import React, { useState, useEffect } from 'react';
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
    TextField,
    Chip
} from '@mui/material';
import { Login as LoginIcon, Mic } from '@mui/icons-material';

const LoginPage = () => {
    const navigate = useNavigate();
    const { login } = useAuth();
    const { speakFeedback } = useVoiceControl();
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [error, setError] = useState('');

    useEffect(() => {
        speakFeedback('Login page loaded. You can say "focus email", "focus password", or "submit" to login.');
        
        // Listen for voice page actions
        const handleVoiceAction = (event) => {
            const { action } = event.detail;
            switch (action) {
                case 'submit':
                case 'login':
                    handleSubmit(new Event('submit'));
                    break;
                case 'clear':
                    clearForm();
                    break;
                case 'help':
                    showHelp();
                    break;
                default:
                    break;
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
        e.preventDefault();
        try {
            speakFeedback('Logging in...');
            await login(formData.email, formData.password);
            speakFeedback('Login successful! Redirecting to home page.');
            navigate('/');
        } catch (err) {
            setError(err.message);
            speakFeedback('Login failed. Please check your credentials.');
        }
    };

    const clearForm = () => {
        setFormData({ email: '', password: '' });
        setError('');
        speakFeedback('Form cleared');
    };

    const showHelp = () => {
        const helpText = `Login page voice commands:
        Say "Focus email" to focus the email field
        Say "Focus password" to focus the password field
        Say "Submit" or "Login" to login
        Say "Clear" to clear the form
        Say "Sign up" to go to registration`;
        speakFeedback(helpText);
    };

    return (
        <Container maxWidth="sm">
            <Box sx={{ mt: 8 }}>
                <Paper elevation={3} sx={{ p: 4 }}>
                    <Typography variant="h4" component="h1" gutterBottom align="center">
                        <LoginIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Login
                    </Typography>
                    
                    <Typography variant="body2" sx={{ mb: 2, textAlign: 'center', color: 'text.secondary' }}>
                        🎤 Voice Commands: "Focus email", "Focus password", "Submit", "Clear"
                    </Typography>
                    
                    {error && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {error}
                        </Alert>
                    )}

                    <form onSubmit={handleSubmit}>
                        <TextField
                            fullWidth
                            label="Email"
                            name="email"
                            type="email"
                            value={formData.email}
                            onChange={handleChange}
                            sx={{ mb: 2 }}
                            required
                        />
                        <TextField
                            fullWidth
                            label="Password"
                            name="password"
                            type="password"
                            value={formData.password}
                            onChange={handleChange}
                            sx={{ mb: 2 }}
                            required
                        />
                        
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                            <Chip label="🎤 Focus email" variant="outlined" size="small" />
                            <Chip label="🎤 Focus password" variant="outlined" size="small" />
                            <Chip label="🎤 Submit" variant="outlined" size="small" />
                            <Chip label="🎤 Clear" variant="outlined" size="small" />
                        </Box>
                        
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            color="primary"
                            sx={{ mt: 2, mb: 2 }}
                            startIcon={<LoginIcon />}
                        >
                            Login
                        </Button>
                        
                        <Button
                            fullWidth
                            variant="outlined"
                            onClick={clearForm}
                            sx={{ mb: 2 }}
                        >
                            Clear Form
                        </Button>
                    </form>
                    
                    <Box sx={{ textAlign: 'center', mt: 2 }}>
                        <Typography variant="body2">
                            Don't have an account?{' '}
                            <Link to="/register">Register here</Link>
                        </Typography>
                    </Box>
                </Paper>
            </Box>
        </Container>
    );
};

export default LoginPage;