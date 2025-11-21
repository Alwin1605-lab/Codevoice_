import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { AuthProvider, useAuth } from './context/AuthContext';
import { VoiceControlProvider } from './context/VoiceControlContext';
import CodeGenerationPage from './pages/CodeGenerationPage';
import Navigation from './components/Navigation.js';
import NotificationBar from './components/NotificationBar';
import LearningModePage from './pages/LearningModePage';
import CollaborationPage from './pages/CollaborationPage';
import ProjectManagerPage from './pages/ProjectManagerPage';
import VoiceCommandsPage from './pages/VoiceCommandsPage';
import FriendsPage from './pages/FriendsPage.jsx';
import CodeCraftingPage from './pages/CodeCraftingPage.jsx';
import ProjectDebugPage from './pages/ProjectDebugPage.jsx';

// Import pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import CodeTranscriptionPage from './pages/CodeTranscriptionPage';

// Protected Route component
const ProtectedRoute = ({ children }) => {
    const { user } = useAuth();
    if (!user) {
        return <Navigate to="/login" />;
    }
    return children;
};

// Create theme with dark purple aesthetic
const theme = createTheme({
    palette: {
        mode: 'dark',
        primary: {
            main: '#9c27b0', // Deep purple
            light: '#ba68c8',
            dark: '#7b1fa2',
        },
        secondary: {
            main: '#ce93d8', // Light purple
            light: '#f3e5f5',
            dark: '#ab47bc',
        },
        background: {
            default: '#0a0a0a', // Almost black
            paper: '#1a1a1a', // Dark gray
        },
        text: {
            primary: '#ffffff',
            secondary: '#b0b0b0',
        },
    },
    components: {
        MuiAppBar: {
            styleOverrides: {
                root: {
                    backgroundImage: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                },
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    backgroundImage: 'none',
                },
            },
        },
        MuiButton: {
            styleOverrides: {
                contained: {
                    background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                    boxShadow: '0 3px 5px 2px rgba(102, 126, 234, .3)',
                    '&:hover': {
                        background: 'linear-gradient(45deg, #764ba2 30%, #667eea 90%)',
                    },
                },
            },
        },
    },
    typography: {
        fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    },
});

function App() {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <AuthProvider>
                <Router>
                    <VoiceControlProvider>
                        <Navigation />
                        <NotificationBar />
                        <Routes>
                            <Route path="/" element={<HomePage />} />
                            <Route path="/login" element={<LoginPage />} />
                            <Route path="/register" element={<RegisterPage />} />
                            <Route 
                                path="/profile" 
                                element={
                                    <ProtectedRoute>
                                        <ProfilePage />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/code-generation" 
                                element={
                                    <ProtectedRoute>
                                        <CodeGenerationPage />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/code-transcription" 
                                element={
                                    <ProtectedRoute>
                                        <CodeTranscriptionPage />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/code-crafting" 
                                element={
                                    <ProtectedRoute>
                                        <CodeCraftingPage />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/learning-mode" 
                                element={
                                    <ProtectedRoute>
                                        <LearningModePage />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/collaboration" 
                                element={
                                    <ProtectedRoute>
                                        <CollaborationPage />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/project-manager" 
                                element={
                                    <ProtectedRoute>
                                        <ProjectManagerPage />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/voice-commands" 
                                element={
                                    <ProtectedRoute>
                                        <VoiceCommandsPage />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/friends" 
                                element={
                                    <ProtectedRoute>
                                        <FriendsPage />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/debug-projects" 
                                element={
                                    <ProtectedRoute>
                                        <ProjectDebugPage />
                                    </ProtectedRoute>
                                } 
                            />
                        </Routes>
                    </VoiceControlProvider>
                </Router>
            </AuthProvider>
        </ThemeProvider>
    );
}

export default App;