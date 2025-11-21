import React from 'react';
import { Link } from 'react-router-dom';
import { Button, Container, Typography, Box, Paper } from '@mui/material';
import CodeIcon from '@mui/icons-material/Code';
import RecordVoiceOverIcon from '@mui/icons-material/RecordVoiceOver';
import { Build } from '@mui/icons-material';

const HomePage = () => {
    return (
        <Box sx={{ 
            minHeight: 'calc(100vh - 70px)',
            background: 'radial-gradient(ellipse at top, #1a1a2e 0%, #0a0a0a 100%)',
            py: 8
        }}>
            <Container maxWidth="lg">
                <Box sx={{ textAlign: 'center', mb: 8 }}>
                    <Typography 
                        variant="h2" 
                        component="h1" 
                        gutterBottom
                        sx={{
                            fontWeight: 800,
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            mb: 2
                        }}
                    >
                        🎤 Voice Controlled IDE
                    </Typography>
                    <Typography 
                        variant="h5" 
                        sx={{ 
                            color: '#b0b0b0',
                            fontWeight: 300,
                            maxWidth: '800px',
                            mx: 'auto'
                        }}
                    >
                        An accessible development environment for programmers with motor disabilities
                    </Typography>
                </Box>
                
                <Box sx={{ 
                    display: 'grid', 
                    gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' },
                    gap: 4,
                    px: { xs: 2, md: 0 }
                }}>
                    <Paper 
                        elevation={8}
                        sx={{ 
                            p: 4, 
                            display: 'flex', 
                            flexDirection: 'column', 
                            alignItems: 'center',
                            background: 'rgba(26, 26, 26, 0.8)',
                            backdropFilter: 'blur(10px)',
                            border: '1px solid rgba(118, 75, 162, 0.2)',
                            borderRadius: 3,
                            transition: 'all 0.3s ease',
                            '&:hover': {
                                transform: 'translateY(-8px)',
                                boxShadow: '0 12px 40px rgba(102, 126, 234, 0.3)',
                                border: '1px solid rgba(118, 75, 162, 0.5)',
                            }
                        }}
                    >
                        <Box sx={{
                            p: 2,
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            mb: 3
                        }}>
                            <CodeIcon sx={{ fontSize: 48, color: 'white' }} />
                        </Box>
                        <Typography variant="h5" gutterBottom sx={{ fontWeight: 700 }}>
                            Code Generation
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph sx={{ textAlign: 'center', mb: 3 }}>
                            Generate code using voice commands and AI assistance
                        </Typography>
                        <Button 
                            component={Link}
                            to="/code-generation"
                            variant="contained"
                            fullWidth
                            sx={{ 
                                mt: 'auto',
                                py: 1.5,
                                borderRadius: 2,
                                fontWeight: 600,
                                textTransform: 'none',
                                fontSize: '1rem'
                            }}
                        >
                            Get Started
                        </Button>
                    </Paper>

                    <Paper 
                        elevation={8}
                        sx={{ 
                            p: 4, 
                            display: 'flex', 
                            flexDirection: 'column', 
                            alignItems: 'center',
                            background: 'rgba(26, 26, 26, 0.8)',
                            backdropFilter: 'blur(10px)',
                            border: '1px solid rgba(118, 75, 162, 0.2)',
                            borderRadius: 3,
                            transition: 'all 0.3s ease',
                            '&:hover': {
                                transform: 'translateY(-8px)',
                                boxShadow: '0 12px 40px rgba(102, 126, 234, 0.3)',
                                border: '1px solid rgba(118, 75, 162, 0.5)',
                            }
                        }}
                    >
                        <Box sx={{
                            p: 2,
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            mb: 3
                        }}>
                            <RecordVoiceOverIcon sx={{ fontSize: 48, color: 'white' }} />
                        </Box>
                        <Typography variant="h5" gutterBottom sx={{ fontWeight: 700 }}>
                            Code Transcription
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph sx={{ textAlign: 'center', mb: 3 }}>
                            Convert your voice directly into code in real-time
                        </Typography>
                        <Button 
                            component={Link}
                            to="/code-transcription"
                            variant="contained"
                            fullWidth
                            sx={{ 
                                mt: 'auto',
                                py: 1.5,
                                borderRadius: 2,
                                fontWeight: 600,
                                textTransform: 'none',
                                fontSize: '1rem'
                            }}
                        >
                            Start Transcribing
                        </Button>
                    </Paper>

                    <Paper 
                        elevation={8}
                        sx={{ 
                            p: 4, 
                            display: 'flex', 
                            flexDirection: 'column', 
                            alignItems: 'center',
                            background: 'rgba(26, 26, 26, 0.8)',
                            backdropFilter: 'blur(10px)',
                            border: '1px solid rgba(118, 75, 162, 0.2)',
                            borderRadius: 3,
                            transition: 'all 0.3s ease',
                            '&:hover': {
                                transform: 'translateY(-8px)',
                                boxShadow: '0 12px 40px rgba(102, 126, 234, 0.3)',
                                border: '1px solid rgba(118, 75, 162, 0.5)',
                            }
                        }}
                    >
                        <Box sx={{
                            p: 2,
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            mb: 3
                        }}>
                            <Build sx={{ fontSize: 48, color: 'white' }} />
                        </Box>
                        <Typography variant="h5" gutterBottom sx={{ fontWeight: 700 }}>
                            Code Crafting
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph sx={{ textAlign: 'center', mb: 3 }}>
                            Describe the code and logic, and we'll generate it using Groq AI
                        </Typography>
                        <Button 
                            component={Link}
                            to="/code-crafting"
                            variant="contained"
                            fullWidth
                            sx={{ 
                                mt: 'auto',
                                py: 1.5,
                                borderRadius: 2,
                                fontWeight: 600,
                                textTransform: 'none',
                                fontSize: '1rem'
                            }}
                        >
                            Craft Code
                        </Button>
                    </Paper>
                </Box>
            </Container>
        </Box>
    );
};

export default HomePage;
