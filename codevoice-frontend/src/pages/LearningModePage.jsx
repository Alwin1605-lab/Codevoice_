import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Button,
  Card,
  CardContent,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Chip,
  IconButton
} from '@mui/material';
import { School, Psychology, BugReport, Lightbulb, Mic, FileUpload, ContentPaste } from '@mui/icons-material';
import { useVoiceControl } from '../context/VoiceControlContext';
import apiService from '../services/apiService';

const LearningModePage = () => {
  const location = useLocation();
  const { speakFeedback, executePageAction } = useVoiceControl();
  const [codeToExplain, setCodeToExplain] = useState('');
  const [explanation, setExplanation] = useState('');
  const [difficulty, setDifficulty] = useState('beginner');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [recording, setRecording] = useState(false);
  const [micLoading, setMicLoading] = useState(false);
  const mediaRecorderRef = React.useRef(null);
  const audioChunksRef = React.useRef([]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    speakFeedback('Learning Mode page loaded. You can say "explain code", "analyze error", or ask for help.');
    
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
        case 'explain':
        case 'explain code':
          run(explainCode);
          break;
        case 'analyze':
        case 'analyze error':
          run(analyzeError);
          break;
        case 'clear':
          run(clearContent);
          break;
        case 'improve':
        case 'improve code':
          run(improveCode);
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

  // Prefill code and optionally trigger action if navigated from Code Generation
  useEffect(() => {
    const state = location.state || {};
    if (state.code) {
      setCodeToExplain(state.code);
      if (state.action === 'explain') {
        // Defer to allow state to set
        setTimeout(() => explainCode(), 100);
      } else if (state.action === 'improve') {
        setTimeout(() => improveCode(), 100);
      }
    }
    // Clear one-time state to avoid retrigger on back/forward
    // history.state is not directly mutable here; rely on one-shot timing
  }, [location.state]);

  const explainCode = async () => {
    if (!codeToExplain.trim()) {
      setError('Please enter some code to explain');
      speakFeedback('Please enter some code to explain');
      return;
    }

    setLoading(true);
    try {
      // Use Groq analysis API for richer explanations
  const data = await apiService.explainCodeWithGroq(codeToExplain, 'python', difficulty, 'overview', []);
      setExplanation(data.explanation || data.ai_explanation || 'No explanation generated');
      setSuccess('Code explained successfully!');
      speakFeedback('Code explanation generated. Check the explanation section.');
    } catch (err) {
      setError('Failed to explain code');
      speakFeedback('Failed to explain code. Please try again.');
    }
    setLoading(false);
  };

  const analyzeError = async () => {
    if (!codeToExplain.trim()) {
      setError('Please enter code with an error to analyze');
      speakFeedback('Please enter code with an error to analyze');
      return;
    }

    setLoading(true);
    try {
      const data = await apiService.analyzeErrorWithGroq(codeToExplain, 'python', 'General error analysis', difficulty, true);
      setExplanation(data.error_explanation || data.analysis || data.explanation || 'No analysis generated');
      setSuccess('Error analysis completed!');
      speakFeedback('Error analysis completed. Check the analysis section.');
    } catch (err) {
      setError('Failed to analyze error');
      speakFeedback('Failed to analyze error. Please try again.');
    }
    setLoading(false);
  };

  const improveCode = async () => {
    if (!codeToExplain.trim()) {
      setError('Please enter some code to improve');
      speakFeedback('Please enter some code to improve');
      return;
    }
    setLoading(true);
    try {
      const data = await apiService.suggestImprovementsWithGroq(codeToExplain, 'python', difficulty);
      const list = [];
      if (Array.isArray(data.suggestions)) list.push(...data.suggestions.map(s => `• ${s}`));
      if (Array.isArray(data.best_practices)) list.push(...data.best_practices.map(s => `• ${s}`));
      if (Array.isArray(data.potential_issues)) list.push(...data.potential_issues.map(s => `• ${s}`));
      const improved = data.improved_code ? `\n\nSuggested Improved Code:\n${data.improved_code}` : '';
      setExplanation(list.length ? `AI Improvement Suggestions:\n${list.join('\n')}${improved}` : 'No improvements suggested.');
      setSuccess('Improvement suggestions generated!');
      speakFeedback('Improvement suggestions ready.');
    } catch (err) {
      setError('Failed to suggest improvements');
      speakFeedback('Failed to suggest improvements.');
    }
    setLoading(false);
  };

  const clearContent = () => {
    setCodeToExplain('');
    setExplanation('');
    setError('');
    setSuccess('');
    speakFeedback('Content cleared');
  };

  const showHelp = () => {
    const helpText = `Learning Mode voice commands:
    Say "Explain code" to get code explanations
    Say "Analyze error" to analyze code errors
    Say "Clear" to clear all content
    Say "Beginner mode", "Intermediate mode", or "Advanced mode" to change difficulty`;
    speakFeedback(helpText);
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <School color="primary" />
        Learning Mode
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
        🎤 Voice Commands: "Explain code", "Analyze error", "Clear", "Help"
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

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          <Psychology sx={{ mr: 1, verticalAlign: 'middle' }} />
          Code Analysis & Learning
        </Typography>

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Difficulty Level</InputLabel>
          <Select
            value={difficulty}
            onChange={(e) => {
              setDifficulty(e.target.value);
              speakFeedback(`Switched to ${e.target.value} level`);
            }}
          >
            <MenuItem value="beginner">Beginner</MenuItem>
            <MenuItem value="intermediate">Intermediate</MenuItem>
            <MenuItem value="advanced">Advanced</MenuItem>
          </Select>
        </FormControl>

        <TextField
          fullWidth
          multiline
          rows={10}
          label="Enter your code here"
          value={codeToExplain}
          onChange={(e) => setCodeToExplain(e.target.value)}
          sx={{ mb: 2 }}
          placeholder="// Paste your code here for explanation or error analysis"
        />

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Button
            variant="contained"
            onClick={explainCode}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={16} /> : <Lightbulb />}
          >
            Explain Code
          </Button>
          <Button
            variant="outlined"
            onClick={analyzeError}
            disabled={loading}
            startIcon={<BugReport />}
          >
            Analyze Error
          </Button>
          <Button
            variant="outlined"
            onClick={improveCode}
            disabled={loading}
          >
            Improve
          </Button>
          <Button
            variant="text"
            onClick={clearContent}
          >
            Clear
          </Button>
          <Button
            variant="text"
            onClick={showHelp}
          >
            Voice Help
          </Button>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 2 }}>
          <IconButton title="Record/Transcribe" onClick={async () => {
            try {
              if (recording) {
                if (mediaRecorderRef.current) mediaRecorderRef.current.stop();
                setRecording(false);
                return;
              }
              setMicLoading(true);
              const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
              const mediaRecorder = new MediaRecorder(stream);
              mediaRecorderRef.current = mediaRecorder;
              audioChunksRef.current = [];
              mediaRecorder.ondataavailable = (e) => { if (e.data && e.data.size > 0) audioChunksRef.current.push(e.data); };
              mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                try {
                  const res = await apiService.transcribeAudio(audioBlob);
                  if (res && res.transcript) {
                    setCodeToExplain(prev => prev ? prev + '\n' + res.transcript : res.transcript);
                    speakFeedback('Transcription added');
                  } else {
                    setError('No transcript received');
                  }
                } catch (err) {
                  console.error('Transcription failed', err);
                  setError('Transcription failed');
                } finally { setMicLoading(false); setRecording(false); }
              };
              mediaRecorder.start();
              setRecording(true);
            } catch (err) {
              console.error('Mic start failed', err);
              setError('Microphone not available');
              setMicLoading(false);
            }
          }}>
            <Mic color={recording ? 'error' : 'inherit'} />
          </IconButton>

          <input
            accept="audio/*"
            id="learning-upload-audio"
            type="file"
            style={{ display: 'none' }}
            onChange={async (e) => {
              const file = e.target.files && e.target.files[0];
              if (!file) return;
              setMicLoading(true);
              try {
                const res = await apiService.transcribeAudio(file);
                if (res && res.transcript) setCodeToExplain(prev => prev ? prev + '\n' + res.transcript : res.transcript);
              } catch (err) { setError('Transcription failed'); }
              setMicLoading(false);
              e.target.value = null;
            }}
          />
          <label htmlFor="learning-upload-audio">
            <IconButton component="span"><FileUpload /></IconButton>
          </label>

          <IconButton title="Paste from clipboard" onClick={async () => {
            try { const txt = await navigator.clipboard.readText(); if (txt) setCodeToExplain(prev => prev ? prev + '\n' + txt : txt); else setError('Clipboard empty'); }
            catch (err) { setError('Failed to read clipboard'); }
          }}>
            <ContentPaste />
          </IconButton>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip label="🎤 Explain code" variant="outlined" />
          <Chip label="🎤 Analyze error" variant="outlined" />
          <Chip label="🎤 Improve" variant="outlined" />
          <Chip label="🎤 Clear" variant="outlined" />
          <Chip label="🎤 Beginner mode" variant="outlined" />
        </Box>
      </Paper>

      {explanation && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Analysis Result:
          </Typography>
          <Box 
            sx={{ 
              whiteSpace: 'pre-wrap', 
              backgroundColor: 'grey.100', 
              color: '#000000',
              p: 2, 
              borderRadius: 1,
              maxHeight: '400px',
              overflow: 'auto'
            }}
          >
            {explanation}
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default LearningModePage;