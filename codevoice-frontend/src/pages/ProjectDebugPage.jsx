import React, { useState } from 'react';
import { Box, Typography, Button, TextField, Paper, Alert } from '@mui/material';
import { BugReport } from '@mui/icons-material';
import apiService from '../services/apiService';

const ProjectDebugPage = () => {
  const [projectId, setProjectId] = useState('');
  const [debugInfo, setDebugInfo] = useState(null);
  const [error, setError] = useState('');

  const debugProject = async () => {
    if (!projectId) {
      setError('Please enter a project ID');
      return;
    }

    setError('');
    setDebugInfo(null);

    try {
      const userId = localStorage.getItem('user_id');
      const response = await fetch(`http://localhost:8000/api/projects-db/projects/${projectId}/debug`, {
        headers: {
          'X-User-Id': userId
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setDebugInfo(data);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        <BugReport sx={{ mr: 1, verticalAlign: 'middle' }} />
        Project Structure Debugger
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="body2" color="text.secondary" paragraph>
          Enter a project ID to inspect its structure and debug empty file issues.
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            fullWidth
            label="Project ID"
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            placeholder="Enter project ID from MongoDB"
          />
          <Button variant="contained" onClick={debugProject}>
            Debug
          </Button>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}
      </Paper>

      {debugInfo && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>Debug Information</Typography>
          
          <Box component="pre" sx={{ 
            bgcolor: '#0a0a0a', 
            p: 2, 
            borderRadius: 1, 
            overflow: 'auto',
            fontSize: '0.875rem'
          }}>
            {JSON.stringify(debugInfo, null, 2)}
          </Box>

          {debugInfo.sample_file && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>Analysis</Typography>
              <Alert severity={debugInfo.sample_file.has_content ? 'success' : 'warning'}>
                {debugInfo.sample_file.has_content
                  ? `✓ Files have content (${debugInfo.sample_file.content_length} chars in sample)`
                  : '⚠ Files appear to be empty or missing content property'}
              </Alert>
            </Box>
          )}
        </Paper>
      )}
    </Box>
  );
};

export default ProjectDebugPage;
