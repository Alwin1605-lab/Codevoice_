import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    AppBar,
    Toolbar,
    Typography,
    Button,
    Box,
    IconButton,
    Menu,
    MenuItem,
    Container,
    Chip,
    Avatar,
    Tooltip
} from '@mui/material';
import {
    AccountCircle,
    Code,
    RecordVoiceOver,
    School,
    Groups,
    Folder,
    Mic,
    Build,
    Logout,
    Person,
    Home
} from '@mui/icons-material';

const Navigation = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [anchorEl, setAnchorEl] = useState(null);

    const handleMenu = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleLogout = () => {
        logout();
        handleClose();
        navigate('/login');
    };

    const handleProfile = () => {
        handleClose();
        navigate('/profile');
    };

    const isActive = (path) => location.pathname === path;

    const navItems = [
        { path: '/code-generation', label: 'Code Gen', icon: <Code fontSize="small" /> },
        { path: '/code-transcription', label: 'Transcribe', icon: <RecordVoiceOver fontSize="small" /> },
        { path: '/code-crafting', label: 'Craft', icon: <Build fontSize="small" /> },
        { path: '/learning-mode', label: 'Learn', icon: <School fontSize="small" /> },
        { path: '/collaboration', label: 'Collab', icon: <Groups fontSize="small" /> },
        { path: '/project-manager', label: 'Projects', icon: <Folder fontSize="small" /> },
        { path: '/voice-commands', label: 'Voice', icon: <Mic fontSize="small" /> },
        { path: '/friends', label: 'Friends', icon: <Groups fontSize="small" /> },
    ];

    return (
        <AppBar 
            position="sticky" 
            elevation={3}
            sx={{ 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                boxShadow: '0 4px 20px rgba(102, 126, 234, 0.3)'
            }}
        >
            <Container maxWidth="xl">
                <Toolbar disableGutters sx={{ minHeight: '70px' }}>
                    {/* Logo */}
                    <Button
                        component={Link}
                        to="/"
                        startIcon={<Home />}
                        sx={{
                            mr: 4,
                            color: 'white',
                            fontWeight: 800,
                            fontSize: '1.2rem',
                            textTransform: 'none',
                            letterSpacing: '0.5px',
                            background: 'rgba(255, 255, 255, 0.1)',
                            borderRadius: '12px',
                            px: 2,
                            py: 1,
                            backdropFilter: 'blur(10px)',
                            '&:hover': {
                                background: 'rgba(255, 255, 255, 0.2)',
                                transform: 'translateY(-2px)',
                            },
                            transition: 'all 0.3s ease'
                        }}
                    >
                        🎤 Voice IDE
                    </Button>
                    
                    {user ? (
                        <>
                            {/* Navigation Items */}
                            <Box sx={{ flexGrow: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                {navItems.map((item) => (
                                    <Tooltip key={item.path} title={item.label} arrow>
                                        <Button
                                            component={Link}
                                            to={item.path}
                                            size="small"
                                            startIcon={item.icon}
                                            sx={{
                                                color: 'white',
                                                px: 1.5,
                                                py: 0.75,
                                                minWidth: 'auto',
                                                textTransform: 'none',
                                                fontSize: '0.875rem',
                                                fontWeight: isActive(item.path) ? 600 : 400,
                                                background: isActive(item.path) 
                                                    ? 'rgba(255, 255, 255, 0.2)' 
                                                    : 'transparent',
                                                borderRadius: '8px',
                                                transition: 'all 0.2s ease',
                                                '&:hover': {
                                                    background: 'rgba(255, 255, 255, 0.15)',
                                                    transform: 'translateY(-2px)',
                                                },
                                            }}
                                        >
                                            {item.label}
                                        </Button>
                                    </Tooltip>
                                ))}
                            </Box>

                            {/* User Menu */}
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 2 }}>
                                <Chip
                                    label={user.name || user.email}
                                    size="small"
                                    sx={{
                                        background: 'rgba(255, 255, 255, 0.2)',
                                        color: 'white',
                                        fontWeight: 500,
                                        display: { xs: 'none', md: 'flex' }
                                    }}
                                />
                                <Tooltip title="Account">
                                    <IconButton
                                        onClick={handleMenu}
                                        sx={{
                                            background: 'rgba(255, 255, 255, 0.15)',
                                            backdropFilter: 'blur(10px)',
                                            '&:hover': {
                                                background: 'rgba(255, 255, 255, 0.25)',
                                                transform: 'scale(1.05)',
                                            },
                                            transition: 'all 0.2s ease'
                                        }}
                                    >
                                        <Avatar
                                            sx={{
                                                width: 32,
                                                height: 32,
                                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                                color: 'white',
                                                fontSize: '1rem',
                                                fontWeight: 700,
                                                border: '2px solid white'
                                            }}
                                        >
                                            {(user.name || user.email)[0].toUpperCase()}
                                        </Avatar>
                                    </IconButton>
                                </Tooltip>
                                <Menu
                                    anchorEl={anchorEl}
                                    open={Boolean(anchorEl)}
                                    onClose={handleClose}
                                    PaperProps={{
                                        sx: {
                                            mt: 1.5,
                                            minWidth: 200,
                                            borderRadius: 2,
                                            boxShadow: '0 8px 24px rgba(0,0,0,0.12)'
                                        }
                                    }}
                                >
                                    <MenuItem onClick={handleProfile} sx={{ gap: 1.5, py: 1.5 }}>
                                        <Person fontSize="small" />
                                        Profile
                                    </MenuItem>
                                    <MenuItem onClick={handleLogout} sx={{ gap: 1.5, py: 1.5, color: 'error.main' }}>
                                        <Logout fontSize="small" />
                                        Logout
                                    </MenuItem>
                                </Menu>
                            </Box>
                        </>
                    ) : (
                        <Box sx={{ ml: 'auto', display: 'flex', gap: 1 }}>
                            <Button 
                                component={Link} 
                                to="/login"
                                variant="outlined"
                                sx={{
                                    color: 'white',
                                    borderColor: 'rgba(255, 255, 255, 0.5)',
                                    borderRadius: '8px',
                                    px: 3,
                                    '&:hover': {
                                        borderColor: 'white',
                                        background: 'rgba(255, 255, 255, 0.1)',
                                        transform: 'translateY(-2px)',
                                    },
                                    transition: 'all 0.2s ease'
                                }}
                            >
                                Login
                            </Button>
                            <Button 
                                component={Link} 
                                to="/register"
                                variant="contained"
                                sx={{
                                    bgcolor: 'white',
                                    color: '#764ba2',
                                    fontWeight: 700,
                                    borderRadius: '8px',
                                    px: 3,
                                    boxShadow: '0 4px 14px rgba(255, 255, 255, 0.3)',
                                    '&:hover': {
                                        bgcolor: 'rgba(255, 255, 255, 0.95)',
                                        transform: 'translateY(-2px)',
                                        boxShadow: '0 6px 20px rgba(255, 255, 255, 0.4)',
                                    },
                                    transition: 'all 0.2s ease'
                                }}
                            >
                                Register
                            </Button>
                        </Box>
                    )}
                </Toolbar>
            </Container>
        </AppBar>
    );
};

export default Navigation;