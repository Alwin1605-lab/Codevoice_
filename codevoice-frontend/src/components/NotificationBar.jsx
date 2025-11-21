import React, { useState, useEffect } from 'react';
import {
  Snackbar,
  Alert,
  Box,
  Typography,
  Button,
  Avatar,
  IconButton,
  Chip,
  Slide,
  Paper
} from '@mui/material';
import { 
  Close, 
  Person, 
  Check, 
  Clear, 
  Notifications,
  GroupAdd 
} from '@mui/icons-material';

const NotificationBar = () => {
  const [notifications, setNotifications] = useState([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    // Listen for new notifications
    const handleNewNotification = (event) => {
      const notification = event.detail;
      setNotifications(prev => [...prev, { ...notification, id: Date.now() }]);
      setOpen(true);
    };

    // Listen for collaboration invites
    const handleCollaborationInvite = (event) => {
      const invite = event.detail;
      const notification = {
        id: Date.now(),
        type: 'collaboration_invite',
        title: 'Collaboration Invite',
        message: `${invite.from_user} invited you to collaborate on "${invite.project_name}"`,
        avatar: invite.from_user_avatar,
        data: invite,
        timestamp: new Date().toISOString()
      };
      setNotifications(prev => [...prev, notification]);
      setOpen(true);

      // Voice feedback
      if (window.speakFeedback) {
        window.speakFeedback(`New collaboration invite from ${invite.from_user}`);
      }
    };

    window.addEventListener('newNotification', handleNewNotification);
    window.addEventListener('collaborationInvite', handleCollaborationInvite);
    
    return () => {
      window.removeEventListener('newNotification', handleNewNotification);
      window.removeEventListener('collaborationInvite', handleCollaborationInvite);
    };
  }, []);

  const handleAcceptInvite = async (notification) => {
    try {
      // Call API to accept collaboration invite
      const response = await fetch('/api/collaboration/accept-invite/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          invite_id: notification.data.invite_id,
          project_id: notification.data.project_id
        })
      });

      if (response.ok) {
        // Remove notification
        setNotifications(prev => prev.filter(n => n.id !== notification.id));
        
        // Show success message
        const successNotification = {
          id: Date.now(),
          type: 'success',
          title: 'Collaboration Accepted',
          message: `You joined "${notification.data.project_name}" collaboration`,
          timestamp: new Date().toISOString()
        };
        setNotifications(prev => [...prev, successNotification]);

        if (window.speakFeedback) {
          window.speakFeedback('Collaboration invite accepted');
        }
      }
    } catch (error) {
      console.error('Failed to accept invite:', error);
    }
  };

  const handleDeclineInvite = (notification) => {
    setNotifications(prev => prev.filter(n => n.id !== notification.id));
    if (window.speakFeedback) {
      window.speakFeedback('Collaboration invite declined');
    }
  };

  const handleDismiss = (notificationId) => {
    setNotifications(prev => prev.filter(n => n.id !== notificationId));
  };

  const renderNotificationContent = (notification) => {
    switch (notification.type) {
      case 'collaboration_invite':
        return (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2 }}>
            <Avatar src={notification.avatar}>
              <Person />
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle2" fontWeight="bold">
                {notification.title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {notification.message}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <Button
                  size="small"
                  variant="contained"
                  color="primary"
                  startIcon={<Check />}
                  onClick={() => handleAcceptInvite(notification)}
                >
                  Accept
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  color="secondary"
                  startIcon={<Clear />}
                  onClick={() => handleDeclineInvite(notification)}
                >
                  Decline
                </Button>
              </Box>
            </Box>
            <IconButton 
              size="small" 
              onClick={() => handleDismiss(notification.id)}
            >
              <Close />
            </IconButton>
          </Box>
        );

      case 'success':
      case 'info':
      case 'warning':
      case 'error':
        return (
          <Alert 
            severity={notification.type}
            onClose={() => handleDismiss(notification.id)}
            sx={{ mb: 1 }}
          >
            <Typography variant="subtitle2">{notification.title}</Typography>
            <Typography variant="body2">{notification.message}</Typography>
          </Alert>
        );

      default:
        return (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2 }}>
            <Notifications color="primary" />
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle2">{notification.title}</Typography>
              <Typography variant="body2" color="text.secondary">
                {notification.message}
              </Typography>
            </Box>
            <IconButton 
              size="small" 
              onClick={() => handleDismiss(notification.id)}
            >
              <Close />
            </IconButton>
          </Box>
        );
    }
  };

  // Show multiple notifications stacked
  return (
    <Box sx={{ position: 'fixed', top: 80, right: 20, zIndex: 9999, maxWidth: 400 }}>
      {notifications.map((notification, index) => (
        <Slide 
          key={notification.id} 
          direction="left" 
          in={true}
          style={{ transformOrigin: 'right top' }}
        >
          <Paper 
            elevation={6} 
            sx={{ 
              mb: 1, 
              borderRadius: 2,
              overflow: 'hidden',
              border: notification.type === 'collaboration_invite' ? '2px solid' : 'none',
              borderColor: notification.type === 'collaboration_invite' ? 'primary.main' : 'transparent'
            }}
          >
            {renderNotificationContent(notification)}
          </Paper>
        </Slide>
      ))}
    </Box>
  );
};

// Helper function to trigger notifications from anywhere in the app
export const showNotification = (notification) => {
  window.dispatchEvent(new CustomEvent('newNotification', { detail: notification }));
};

// Helper function to trigger collaboration invites
export const showCollaborationInvite = (invite) => {
  window.dispatchEvent(new CustomEvent('collaborationInvite', { detail: invite }));
};

export default NotificationBar;