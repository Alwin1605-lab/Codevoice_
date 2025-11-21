import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Card,
  CardContent,
  TextField,
  Alert,
  List,
  ListItem,
  ListItemText,
  Chip,
  Grid,
  Avatar,
  Badge,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Autocomplete,
  IconButton,
  Tooltip,
  InputAdornment
} from '@mui/material';
import { 
  Groups, 
  VideoCall, 
  PersonAdd, 
  Share, 
  Chat, 
  Send as SendIcon,
  Notifications,
  Close
} from '@mui/icons-material';
import { useVoiceControl } from '../context/VoiceControlContext';
import apiService from '../services/apiService';
import { showCollaborationInvite } from '../components/NotificationBar';
import MicControl from '../components/MicControl';

const CollaborationPage = () => {
  const { speakFeedback } = useVoiceControl();
  const [sessionId, setSessionId] = useState('');
  const [participants, setParticipants] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeSessions, setActiveSessions] = useState([]);
  
  // Invite functionality
  const [inviteDialog, setInviteDialog] = useState(false);
  const [availableUsers, setAvailableUsers] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [inviteMessage, setInviteMessage] = useState('');
  const [currentProject, setCurrentProject] = useState('My Project');

  const handleSessionIdSpeech = useCallback((spokenText = '') => {
    const sanitized = spokenText.replace(/\s+/g, '').trim();
    if (!sanitized) return;
    setSessionId(sanitized);
  }, []);

  const handleInviteMessageSpeech = useCallback((spokenText = '') => {
    if (!spokenText.trim()) return;
    setInviteMessage(prev => {
      if (!prev) return spokenText.trim();
      const separator = prev.endsWith(' ') ? '' : ' ';
      return `${prev}${separator}${spokenText}`.replace(/\s+/g, ' ').trim();
    });
  }, []);

  useEffect(() => {
    speakFeedback('Collaboration page loaded. You can say "create session", "invite users", or "join session".');
    fetchActiveSessions();
    fetchAvailableUsers();
    
    // Listen for voice page actions
    const handleVoiceAction = (event) => {
      const detail = event.detail || {};
      const rawAction = typeof detail.action === 'string' ? detail.action : '';
      const action = rawAction.toLowerCase();
      let handled = false;
      const run = (fn) => {
        fn();
        handled = true;
        detail.suppressAutoFeedback = true;
      };

      switch (action) {
        case 'create':
        case 'create session':
          run(createSession);
          break;
        case 'join':
        case 'join session':
          run(joinSession);
          break;
        case 'invite':
        case 'invite users':
        case 'send invite':
          setInviteDialog(true);
          handled = true;
          detail.feedback = 'Invite dialog opened. Select collaborators to invite.';
          break;
        case 'leave':
        case 'leave session':
          run(leaveSession);
          break;
        case 'share':
        case 'share code':
          run(shareCode);
          break;
        case 'help':
          showHelp();
          handled = true;
          detail.suppressAutoFeedback = true;
          break;
        default:
          break;
      }

      if (handled) {
        detail.handled = true;
      }
    };

    window.addEventListener('voicePageAction', handleVoiceAction);
    return () => window.removeEventListener('voicePageAction', handleVoiceAction);
  }, []);

  const fetchActiveSessions = async () => {
    try {
      const data = await apiService.getActiveSessions();
      setActiveSessions(data.sessions || []);
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
    }
  };

  const createSession = async () => {
    setLoading(true);
    try {
      console.log('Creating collaboration session...');
      const data = await apiService.createCollaborationSession('Voice Coding Session', 'Real-time collaboration session');
      console.log('Session created:', data);
      setSessionId(data.session.id);
      setSuccess(`Session created: ${data.session.id}`);
      speakFeedback(`Session created with ID ${data.session.id}. Share this ID with collaborators.`);
      fetchActiveSessions();
    } catch (err) {
      console.error('Create session error:', err);
      console.error('Error response:', err.response?.data);
      setError('Failed to create session');
      speakFeedback('Failed to create session. Please try again.');
    }
    setLoading(false);
  };

  const joinSession = async () => {
    if (!sessionId.trim()) {
      setError('Please enter a session ID');
      speakFeedback('Please enter a session ID first');
      return;
    }
    
    setLoading(true);
    try {
      const data = await apiService.joinCollaborationSession(sessionId, 'User');
      
      if (data) {
        setIsConnected(true);
        setSuccess('Joined session successfully!');
        speakFeedback(`Successfully joined session ${sessionId}. You can now collaborate in real-time.`);
        // Here you would establish WebSocket connection
        connectWebSocket(sessionId);
      }
    } catch (err) {
      setError('Failed to join session');
      speakFeedback('Failed to join session. Please check the session ID.');
    }
    setLoading(false);
  };

  const leaveSession = () => {
    setIsConnected(false);
    setSessionId('');
    setParticipants([]);
    setSuccess('Left session');
    speakFeedback('Left collaboration session');
  };

  const shareCode = () => {
    if (!isConnected) {
      setError('Please join a session first');
      speakFeedback('Please join a session first before sharing code');
      return;
    }
    
    // Implement code sharing logic
    speakFeedback('Code shared with all participants');
  };

  const connectWebSocket = (sessionId) => {
    // WebSocket connection would be implemented here
    // For demonstration, we'll simulate participants
    setParticipants([
      { name: 'User', status: 'active', id: '1' },
      { name: 'Collaborator 1', status: 'active', id: '2' }
    ]);
  };

  const fetchAvailableUsers = async () => {
    try {
      // Simulate available users - in real app, this would fetch from API
      setAvailableUsers([
        { id: '1', name: 'Alice Johnson', email: 'alice@example.com', avatar: '', online: true },
        { id: '2', name: 'Bob Smith', email: 'bob@example.com', avatar: '', online: true },
        { id: '3', name: 'Carol Davis', email: 'carol@example.com', avatar: '', online: false },
        { id: '4', name: 'David Wilson', email: 'david@example.com', avatar: '', online: true },
      ]);
    } catch (err) {
      console.error('Failed to fetch users:', err);
    }
  };

  const sendInvites = async () => {
    if (selectedUsers.length === 0) {
      setError('Please select at least one user to invite');
      speakFeedback('Please select users to invite');
      return;
    }

    setLoading(true);
    try {
      // Send invites to selected users
      for (const user of selectedUsers) {
        // Simulate sending invite - trigger notification for demo
        setTimeout(() => {
          showCollaborationInvite({
            invite_id: `invite_${Date.now()}`,
            project_id: '123',
            project_name: currentProject,
            from_user: 'Current User', // In real app, get from auth context
            from_user_avatar: '',
            to_user: user.name,
            message: inviteMessage || `Join me on ${currentProject}`
          });
        }, 1000 * selectedUsers.indexOf(user)); // Stagger notifications
      }

      setSuccess(`Sent ${selectedUsers.length} collaboration invite(s)`);
      speakFeedback(`Sent invites to ${selectedUsers.length} users`);
      
      // Reset form
      setSelectedUsers([]);
      setInviteMessage('');
      setInviteDialog(false);
    } catch (err) {
      setError('Failed to send invites');
      speakFeedback('Failed to send invites. Please try again.');
    }
    setLoading(false);
  };

  const showHelp = () => {
    const helpText = `Collaboration voice commands:
    Say "Create session" to start a new collaboration session
    Say "Invite users" to send collaboration invites
    Say "Join session" to join an existing session
    Say "Leave session" to exit current session
    Say "Share code" to share your code with participants`;
    speakFeedback(helpText);
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Groups color="primary" />
        Real-Time Collaboration
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
        🎤 Voice Commands: "Create session", "Join session", "Leave session", "Share code"
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
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <VideoCall sx={{ mr: 1, verticalAlign: 'middle' }} />
              Session Management
            </Typography>

            <TextField
              fullWidth
              label="Session ID"
              value={sessionId}
              onChange={(e) => setSessionId(e.target.value)}
              sx={{ mb: 2 }}
              placeholder="Enter session ID to join or leave empty to create new"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <MicControl
                      onTranscript={handleSessionIdSpeech}
                      tooltip="Speak session ID"
                    />
                  </InputAdornment>
                )
              }}
            />

            <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                onClick={createSession}
                disabled={loading}
                startIcon={<PersonAdd />}
              >
                Create Session
              </Button>
              <Button
                variant="outlined"
                onClick={joinSession}
                disabled={!sessionId || loading}
                startIcon={<Groups />}
              >
                Join Session
              </Button>
              <Button
                variant="outlined"
                onClick={() => setInviteDialog(true)}
                startIcon={<SendIcon />}
                color="secondary"
              >
                Invite Users
              </Button>
              {isConnected && (
                <Button
                  variant="text"
                  onClick={leaveSession}
                  color="error"
                >
                  Leave Session
                </Button>
              )}
            </Box>

            {isConnected && (
              <Alert severity="success" sx={{ mb: 2 }}>
                <strong>Connected to session: {sessionId}</strong>
                <br />
                Real-time collaboration is active
              </Alert>
            )}

            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip label="🎤 Create session" variant="outlined" />
              <Chip label="🎤 Join session" variant="outlined" />
              <Chip label="🎤 Share code" variant="outlined" />
            </Box>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <Chat sx={{ mr: 1, verticalAlign: 'middle' }} />
              Participants ({participants.length})
            </Typography>

            {participants.length > 0 ? (
              <List>
                {participants.map((participant) => (
                  <ListItem key={participant.id}>
                    <Badge
                      color={participant.status === 'active' ? 'success' : 'default'}
                      variant="dot"
                      sx={{ mr: 2 }}
                    >
                      <Avatar sx={{ width: 32, height: 32 }}>
                        {participant.name[0]}
                      </Avatar>
                    </Badge>
                    <ListItemText 
                      primary={participant.name}
                      secondary={participant.status}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No participants yet. Create or join a session to start collaborating.
              </Typography>
            )}

            {isConnected && (
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="outlined"
                  onClick={shareCode}
                  startIcon={<Share />}
                  fullWidth
                >
                  Share Current Code
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid size={{ xs: 12 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Active Sessions
            </Typography>
            
            {activeSessions.length > 0 ? (
              <Grid container spacing={2}>
                {activeSessions.map((session) => (
                  <Grid size={{ xs: 12, sm: 6, md: 4 }} key={session.id}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6">{session.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          ID: {session.id}
                        </Typography>
                        <Typography variant="body2">
                          Participants: {session.participant_count}
                        </Typography>
                        <Button
                          size="small"
                          onClick={() => {
                            setSessionId(session.id);
                            speakFeedback(`Session ID ${session.id} entered`);
                          }}
                          sx={{ mt: 1 }}
                        >
                          Use This ID
                        </Button>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No active sessions found.
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Invite Users Dialog */}
      <Dialog open={inviteDialog} onClose={() => setInviteDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SendIcon color="primary" />
            Invite Users to Collaborate
            <IconButton 
              onClick={() => setInviteDialog(false)}
              sx={{ ml: 'auto' }}
            >
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Select users who are currently online in the app to invite them to collaborate on "{currentProject}"
          </Typography>

          <Autocomplete
            multiple
            options={availableUsers}
            getOptionLabel={(option) => `${option.name} (${option.email})`}
            value={selectedUsers}
            onChange={(event, newValue) => {
              setSelectedUsers(newValue);
              if (newValue.length > 0) {
                speakFeedback(`Selected ${newValue.length} users`);
              }
            }}
            renderOption={(props, option) => (
              <Box component="li" {...props}>
                <Badge
                  color={option.online ? 'success' : 'default'}
                  variant="dot"
                  sx={{ mr: 2 }}
                >
                  <Avatar sx={{ width: 32, height: 32 }}>
                    {option.name.charAt(0)}
                  </Avatar>
                </Badge>
                <Box>
                  <Typography variant="body2">{option.name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {option.email} • {option.online ? 'Online' : 'Offline'}
                  </Typography>
                </Box>
              </Box>
            )}
            renderTags={(tagValue, getTagProps) =>
              tagValue.map((option, index) => (
                <Chip
                  key={option.id}
                  label={option.name}
                  avatar={<Avatar>{option.name.charAt(0)}</Avatar>}
                  {...getTagProps({ index })}
                />
              ))
            }
            renderInput={(params) => (
              <TextField
                {...params}
                label="Select Users to Invite"
                placeholder="Choose collaborators..."
                sx={{ mb: 2 }}
              />
            )}
          />

          <Box sx={{ position: 'relative', mb: 2 }}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Invitation Message (Optional)"
              value={inviteMessage}
              onChange={(e) => setInviteMessage(e.target.value)}
              placeholder="Add a personal message to your invitation..."
              sx={{ pr: 6 }}
            />
            <Box sx={{ position: 'absolute', right: 8, bottom: 8 }}>
              <MicControl
                onTranscript={handleInviteMessageSpeech}
                tooltip="Speak invite message"
              />
            </Box>
          </Box>

          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip label="🎤 Say names to select users" variant="outlined" size="small" />
            <Chip label="🎤 Send invite" variant="outlined" size="small" />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInviteDialog(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={sendInvites}
            disabled={loading || selectedUsers.length === 0}
            startIcon={<SendIcon />}
          >
            Send Invites ({selectedUsers.length})
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CollaborationPage;
