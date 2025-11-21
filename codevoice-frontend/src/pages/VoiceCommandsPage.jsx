import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid
} from '@mui/material';
import { 
  Mic, 
  MicOff, 
  VolumeUp, 
  ExpandMore,
  PlayArrow,
  Stop,
  Save,
  Build,
  NavigateNext
} from '@mui/icons-material';
import { useVoiceControl } from '../context/VoiceControlContext';
import apiService from '../services/apiService';

const VoiceCommandsPage = () => {
  const { 
    isListening, 
    isEnabled, 
    setIsEnabled, 
    lastCommand, 
    voiceStatus, 
    startListening, 
    stopListening,
    speakFeedback 
  } = useVoiceControl();
  
  const [commands, setCommands] = useState({});
  const [commandStatus, setCommandStatus] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    speakFeedback('Voice Commands page loaded. Voice control is active for all navigation and actions.');
    fetchCommands();
    fetchCommandStatus();
    
    // Listen for voice page actions
    const handleVoiceAction = (event) => {
      const { action } = event.detail;
      switch (action) {
        case 'toggle':
        case 'toggle listening':
          toggleListening();
          break;
        case 'enable':
        case 'enable voice':
          enableVoice();
          break;
        case 'disable':
        case 'disable voice':
          disableVoice();
          break;
        case 'test':
        case 'test voice':
          testVoice();
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

  const fetchCommands = async () => {
    try {
      const data = await apiService.getAvailableCommands();
      setCommands(data.categories || {});
    } catch (err) {
      console.error('Failed to fetch commands:', err);
    }
  };

  const fetchCommandStatus = async () => {
    try {
      const data = await apiService.getVoiceCommandStatus();
      setCommandStatus(data || {});
    } catch (err) {
      console.error('Failed to fetch command status:', err);
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const enableVoice = () => {
    setIsEnabled(true);
    speakFeedback('Voice control enabled');
  };

  const disableVoice = () => {
    setIsEnabled(false);
    speakFeedback('Voice control disabled');
  };

  const testVoice = () => {
    speakFeedback('Voice test successful. All systems are working correctly.');
    setSuccess('Voice test completed successfully!');
  };

  const executeQuickCommand = async (action) => {
    try {
      const result = await apiService.executeQuickVoiceCommand(action);
      if (result.success || result) {
        setSuccess(`Executed: ${action}`);
        speakFeedback(`${action} command executed`);
      }
    } catch (err) {
      setError(`Failed to execute: ${action}`);
      speakFeedback(`Failed to execute ${action}`);
    }
  };

  const showHelp = () => {
    const helpText = `Voice Commands page help:
    This page shows all available voice commands
    Say any navigation command like "Code Generation", "Learning Mode"
    Say action commands like "Save", "Compile", "Run", "Clear"
    Say "Toggle listening" to start or stop voice recognition
    All commands work from any page in the application`;
    speakFeedback(helpText);
  };

  // Global navigation commands that work from anywhere
  const globalNavigationCommands = [
    'Home', 'Code Generation', 'Code Transcription', 'Learning Mode', 
    'Collaboration', 'Projects', 'Voice Commands', 'Profile'
  ];

  const globalActionCommands = [
    'Save', 'Compile', 'Run', 'Clear', 'Copy', 'Paste', 'Undo', 'Redo', 'Help'
  ];

  const authCommands = [
    'Login', 'Sign Up', 'Logout', 'Focus Username', 'Focus Password'
  ];

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Mic color="primary" />
        Voice Commands Control Center
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
        🎤 Voice Commands: "Toggle listening", "Enable voice", "Test voice", "Help"
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Voice Control Status */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Voice Control Status
            </Typography>

            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={isEnabled}
                    onChange={(e) => setIsEnabled(e.target.checked)}
                    color="primary"
                  />
                }
                label="Voice Control Enabled"
              />
              <Chip 
                label={isListening ? 'Listening' : 'Not Listening'}
                color={isListening ? 'success' : 'default'}
                icon={isListening ? <Mic /> : <MicOff />}
                sx={{ ml: 2 }}
              />
            </Box>

            <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
              <Button
                variant={isListening ? "outlined" : "contained"}
                onClick={toggleListening}
                startIcon={isListening ? <Stop /> : <PlayArrow />}
                disabled={!isEnabled}
              >
                {isListening ? 'Stop Listening' : 'Start Listening'}
              </Button>
              <Button
                variant="outlined"
                onClick={testVoice}
                startIcon={<VolumeUp />}
              >
                Test Voice
              </Button>
            </Box>

            {lastCommand && (
              <Alert severity="info" sx={{ mb: 2 }}>
                Last Command: "{lastCommand}"
              </Alert>
            )}

            <Typography variant="body2" color="text.secondary">
              Voice Status: {voiceStatus}
              <br />
              Commands Available: {commandStatus.total_commands || 0}
            </Typography>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Voice Actions
            </Typography>
            
            <Typography variant="body2" sx={{ mb: 2 }}>
              Try these commands by saying them:
            </Typography>

            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
              {['save', 'compile', 'run', 'clear', 'help'].map((cmd) => (
                <Button
                  key={cmd}
                  variant="outlined"
                  size="small"
                  onClick={() => executeQuickCommand(cmd)}
                  startIcon={cmd === 'save' ? <Save /> : cmd === 'compile' ? <Build /> : undefined}
                >
                  {cmd}
                </Button>
              ))}
            </Box>

            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip label="🎤 Save" variant="outlined" />
              <Chip label="🎤 Compile" variant="outlined" />
              <Chip label="🎤 Run" variant="outlined" />
              <Chip label="🎤 Clear" variant="outlined" />
              <Chip label="🎤 Help" variant="outlined" />
            </Box>
          </Paper>
        </Grid>

        {/* Global Navigation Commands */}
        <Grid size={{ xs: 12 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Global Voice Navigation
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              These commands work from any page to navigate the application:
            </Typography>
            
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, md: 4 }}>
                <Typography variant="subtitle2" gutterBottom>Page Navigation:</Typography>
                <List dense>
                  {globalNavigationCommands.map((cmd) => (
                    <ListItem key={cmd}>
                      <ListItemIcon>
                        <NavigateNext fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={`"${cmd}"`} />
                    </ListItem>
                  ))}
                </List>
              </Grid>
              
              <Grid size={{ xs: 12, md: 4 }}>
                <Typography variant="subtitle2" gutterBottom>Actions:</Typography>
                <List dense>
                  {globalActionCommands.map((cmd) => (
                    <ListItem key={cmd}>
                      <ListItemIcon>
                        <PlayArrow fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={`"${cmd}"`} />
                    </ListItem>
                  ))}
                </List>
              </Grid>
              
              <Grid size={{ xs: 12, md: 4 }}>
                <Typography variant="subtitle2" gutterBottom>Authentication:</Typography>
                <List dense>
                  {authCommands.map((cmd) => (
                    <ListItem key={cmd}>
                      <ListItemIcon>
                        <VolumeUp fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={`"${cmd}"`} />
                    </ListItem>
                  ))}
                </List>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Available Commands by Category */}
        <Grid size={{ xs: 12 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              All Available Commands
            </Typography>
            {Object.entries(commands).map(([category, cmdList]) => (
              <Accordion key={category}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="subtitle1">
                    {category} ({Array.isArray(cmdList) ? cmdList.length : 0} commands)
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {Array.isArray(cmdList) && cmdList.map((cmd) => (
                      <Chip 
                        key={cmd} 
                        label={`"${cmd}"`} 
                        size="small" 
                        variant="outlined"
                        onClick={() => speakFeedback(`Command: ${cmd}`)}
                      />
                    ))}
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default VoiceCommandsPage;
