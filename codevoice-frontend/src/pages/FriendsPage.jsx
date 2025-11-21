import React, { useEffect, useState, useCallback } from 'react';
import { 
  Box, Typography, Paper, List, ListItem, ListItemText, 
  Chip, Button, Tabs, Tab, Avatar, TextField, InputAdornment,
  Alert, CircularProgress
} from '@mui/material';
import { PersonAdd, Search, People, PersonAddAlt } from '@mui/icons-material';
import { useVoiceControl } from '../context/VoiceControlContext';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/apiService';
import MicControl from '../components/MicControl';

const FriendsPage = () => {
  const { speakFeedback } = useVoiceControl();
  const { user: currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [friends, setFriends] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleSearchSpeech = useCallback((spokenText = '') => {
    if (!spokenText.trim()) return;
    setSearchTerm(spokenText.trim());
  }, []);

  useEffect(() => {
    speakFeedback('Friends page loaded. Browse users, send friend requests, and manage your friends.');
    fetchAllUsers();
    fetchFriends();
    
    // Voice commands handler
    const handleVoiceAction = (event) => {
      const detail = event.detail || {};
      const rawAction = typeof detail.action === 'string' ? detail.action : (typeof event.detail === 'string' ? event.detail : '');
      const action = rawAction.toLowerCase();
      let handled = false;
      let feedback = '';

      if (action === 'my friends' || action === 'show friends') {
        setActiveTab(0);
        handled = true;
        feedback = 'Showing your friends list.';
      } else if (action === 'find users' || action === 'discover users') {
        setActiveTab(1);
        handled = true;
        feedback = 'Showing discover users tab.';
      }

      if (handled) {
        detail.handled = true;
        detail.feedback = feedback;
      }
    };

    window.addEventListener('voicePageAction', handleVoiceAction);
    return () => window.removeEventListener('voicePageAction', handleVoiceAction);
  }, []);

  const fetchAllUsers = async () => {
    try {
      const data = await apiService.getAllUsers();
      // Filter out current user
      const filtered = (data.users || []).filter(u => u.id !== currentUser.id);
      setAllUsers(filtered);
    } catch (err) {
      console.error('Failed to fetch users:', err);
      setAllUsers([]);
    }
  };

  const fetchFriends = async () => {
    try {
      const data = await apiService.getFriends();
      setFriends(data.friends || []);
    } catch (err) {
      console.error('Failed to fetch friends:', err);
      setFriends([]);
    }
  };

  const sendFriendRequest = async (userId, userName) => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      await apiService.sendFriendRequest(userId);
      setSuccess(`Friend request sent to ${userName}`);
      speakFeedback(`Friend request sent to ${userName}`);
    } catch (err) {
      setError('Failed to send friend request');
      speakFeedback('Failed to send friend request');
    }
    
    setLoading(false);
  };

  const filteredUsers = allUsers.filter(user => 
    user.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box sx={{ 
      minHeight: 'calc(100vh - 70px)',
      background: 'radial-gradient(ellipse at top, #1a1a2e 0%, #0a0a0a 100%)',
      py: 4
    }}>
      <Box sx={{ maxWidth: 1000, mx: 'auto', px: 3 }}>
        <Typography 
          variant="h3" 
          gutterBottom
          sx={{
            fontWeight: 800,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1
          }}
        >
          <People sx={{ fontSize: 40, mr: 2, verticalAlign: 'middle' }} />
          Friends & Community
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph>
          Connect with other developers, collaborate on projects, and build your coding network
        </Typography>

        {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}
        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

        <Paper elevation={8} sx={{ 
          background: 'rgba(26, 26, 26, 0.8)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(118, 75, 162, 0.2)',
          borderRadius: 3,
          overflow: 'hidden'
        }}>
          <Tabs 
            value={activeTab} 
            onChange={(e, newValue) => setActiveTab(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
          >
            <Tab label={`My Friends (${friends.length})`} icon={<People />} iconPosition="start" />
            <Tab label="Discover Users" icon={<PersonAddAlt />} iconPosition="start" />
          </Tabs>

          {/* My Friends Tab */}
          {activeTab === 0 && (
            <Box sx={{ p: 3 }}>
              {friends.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <People sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No friends yet
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Go to "Discover Users" to find and add friends
                  </Typography>
                  <Button 
                    variant="contained" 
                    onClick={() => setActiveTab(1)}
                    startIcon={<PersonAddAlt />}
                  >
                    Find Users
                  </Button>
                </Box>
              ) : (
                <List>
                  {friends.map((friend) => (
                    <ListItem 
                      key={friend.id}
                      sx={{
                        mb: 1,
                        borderRadius: 2,
                        '&:hover': { bgcolor: 'rgba(118, 75, 162, 0.1)' }
                      }}
                    >
                      <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                        {friend.name?.[0]?.toUpperCase() || 'U'}
                      </Avatar>
                      <ListItemText 
                        primary={friend.name || 'User'}
                        secondary={friend.email}
                      />
                      <Chip label="Friend" color="success" size="small" />
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
          )}

          {/* Discover Users Tab */}
          {activeTab === 1 && (
            <Box sx={{ p: 3 }}>
              <TextField
                fullWidth
                placeholder="Search users by name or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                sx={{ mb: 3 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <MicControl
                        onTranscript={handleSearchSpeech}
                        tooltip="Speak search query"
                      />
                    </InputAdornment>
                  )
                }}
              />

              {loading && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <CircularProgress />
                </Box>
              )}

              {!loading && filteredUsers.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <Search sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary">
                    No users found
                  </Typography>
                </Box>
              )}

              {!loading && filteredUsers.length > 0 && (
                <List>
                  {filteredUsers.map((user) => (
                    <ListItem 
                      key={user.id}
                      sx={{
                        mb: 1,
                        borderRadius: 2,
                        border: '1px solid rgba(118, 75, 162, 0.2)',
                        '&:hover': { 
                          bgcolor: 'rgba(118, 75, 162, 0.1)',
                          borderColor: 'rgba(118, 75, 162, 0.5)'
                        }
                      }}
                    >
                      <Avatar sx={{ mr: 2, bgcolor: 'secondary.main' }}>
                        {user.name?.[0]?.toUpperCase() || 'U'}
                      </Avatar>
                      <ListItemText 
                        primary={user.name || 'User'}
                        secondary={
                          <>
                            {user.email}
                            {user.programming_experience && (
                              <Chip 
                                label={user.programming_experience} 
                                size="small" 
                                sx={{ ml: 1 }}
                              />
                            )}
                          </>
                        }
                      />
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<PersonAdd />}
                        onClick={() => sendFriendRequest(user.id, user.name)}
                        disabled={loading}
                      >
                        Add Friend
                      </Button>
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
          )}
        </Paper>

        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
            💡 Voice Commands: "My friends", "Find users", "Scroll up", "Scroll down"
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default FriendsPage;
