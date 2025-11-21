import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  Card,
  CardContent,
  CardActions,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tabs,
  Tab
} from '@mui/material';
import {
  ExpandMore,
  School,
  Language,
  Groups,
  VolumeUp,
  Folder,
  Mic,
  Settings,
  Help,
  PlayArrow,
  Stop,
  Save,
  Build
} from '@mui/icons-material';

const API_BASE = 'http://localhost:8000';

const AdvancedFeatures = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [features, setFeatures] = useState({
    learningMode: {
      enabled: false,
      difficulty: 'beginner',
      lastExplanation: null
    },
    multiLangSupport: {
      enabled: false,
      selectedLanguage: 'en',
      availableLanguages: ['en', 'es', 'fr', 'de']
    },
    realTimeCollab: {
      enabled: false,
      sessionId: null,
      participants: []
    },
    voiceNarration: {
      enabled: false,
      voice: null,
      rate: 180,
      volume: 0.8
    },
    projectManager: {
      enabled: false,
      currentProject: null,
      projects: []
    },
    voiceCommands: {
      enabled: true,
      listening: false,
      muted: false
    }
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dialogs, setDialogs] = useState({
    createProject: false,
    explainCode: false,
    voiceSettings: false,
    collaboration: false
  });

  // Learning Mode Component
  const LearningModePanel = () => {
    const [codeToExplain, setCodeToExplain] = useState('');
    const [explanation, setExplanation] = useState('');
    const [difficulty, setDifficulty] = useState('beginner');

    const explainCode = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE}/learning/explain-code/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            code: codeToExplain,
            difficulty_level: difficulty,
            language: 'python'
          })
        });
        const data = await response.json();
        setExplanation(data.explanation);
        setSuccess('Code explained successfully!');
      } catch (err) {
        setError('Failed to explain code');
      }
      setLoading(false);
    };

    const analyzeError = async (errorMessage) => {
      try {
        const response = await fetch(`${API_BASE}/learning/analyze-error/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            error_message: errorMessage,
            code: codeToExplain,
            language: 'python'
          })
        });
        const data = await response.json();
        setExplanation(data.analysis);
      } catch (err) {
        setError('Failed to analyze error');
      }
    };

    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          <School sx={{ mr: 1, verticalAlign: 'middle' }} />
          Learning Mode
        </Typography>
        
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Difficulty Level</InputLabel>
              <Select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
              >
                <MenuItem value="beginner">Beginner</MenuItem>
                <MenuItem value="intermediate">Intermediate</MenuItem>
                <MenuItem value="advanced">Advanced</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              multiline
              rows={6}
              label="Code to Explain"
              value={codeToExplain}
              onChange={(e) => setCodeToExplain(e.target.value)}
              sx={{ mb: 2 }}
            />

            <Button
              variant="contained"
              onClick={explainCode}
              disabled={!codeToExplain || loading}
              startIcon={loading ? <CircularProgress size={16} /> : <School />}
            >
              Explain Code
            </Button>
          </CardContent>
        </Card>

        {explanation && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Explanation:</Typography>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                {explanation}
              </Typography>
            </CardContent>
          </Card>
        )}
      </Box>
    );
  };

  // Multi-Language Support Component
  const MultiLanguagePanel = () => {
    const [selectedLang, setSelectedLang] = useState('en');
    const [transcriptionResult, setTranscriptionResult] = useState('');

    const testMultiLangTranscription = async () => {
      setLoading(true);
      try {
        // This would integrate with actual audio input
        const response = await fetch(`${API_BASE}/multilang/translate-commands/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            command: 'compilar código',
            source_language: 'es',
            target_language: 'en'
          })
        });
        const data = await response.json();
        setTranscriptionResult(`Translated: ${data.translated_command}`);
      } catch (err) {
        setError('Failed to test translation');
      }
      setLoading(false);
    };

    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          <Language sx={{ mr: 1, verticalAlign: 'middle' }} />
          Multi-Language Support
        </Typography>
        
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Voice Language</InputLabel>
              <Select
                value={selectedLang}
                onChange={(e) => setSelectedLang(e.target.value)}
              >
                <MenuItem value="en">English</MenuItem>
                <MenuItem value="es">Spanish</MenuItem>
                <MenuItem value="fr">French</MenuItem>
                <MenuItem value="de">German</MenuItem>
              </Select>
            </FormControl>

            <Typography variant="body2" sx={{ mb: 2 }}>
              Supported voice commands in {selectedLang}:
            </Typography>

            <Box sx={{ mb: 2 }}>
              {selectedLang === 'es' && (
                <div>
                  <Chip label="compilar código" sx={{ m: 0.5 }} />
                  <Chip label="ejecutar programa" sx={{ m: 0.5 }} />
                  <Chip label="guardar archivo" sx={{ m: 0.5 }} />
                </div>
              )}
              {selectedLang === 'fr' && (
                <div>
                  <Chip label="compiler code" sx={{ m: 0.5 }} />
                  <Chip label="exécuter programme" sx={{ m: 0.5 }} />
                  <Chip label="sauvegarder fichier" sx={{ m: 0.5 }} />
                </div>
              )}
              {selectedLang === 'de' && (
                <div>
                  <Chip label="code kompilieren" sx={{ m: 0.5 }} />
                  <Chip label="programm ausführen" sx={{ m: 0.5 }} />
                  <Chip label="datei speichern" sx={{ m: 0.5 }} />
                </div>
              )}
              {selectedLang === 'en' && (
                <div>
                  <Chip label="compile code" sx={{ m: 0.5 }} />
                  <Chip label="run program" sx={{ m: 0.5 }} />
                  <Chip label="save file" sx={{ m: 0.5 }} />
                </div>
              )}
            </Box>

            <Button
              variant="contained"
              onClick={testMultiLangTranscription}
              disabled={loading}
              startIcon={<Language />}
            >
              Test Translation
            </Button>

            {transcriptionResult && (
              <Alert severity="info" sx={{ mt: 2 }}>
                {transcriptionResult}
              </Alert>
            )}
          </CardContent>
        </Card>
      </Box>
    );
  };

  // Real-Time Collaboration Component
  const CollaborationPanel = () => {
    const [sessionId, setSessionId] = useState('');
    const [participants, setParticipants] = useState([]);
    const [isConnected, setIsConnected] = useState(false);

    const createSession = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE}/collaboration/create-session/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            session_name: 'Voice Coding Session',
            creator_name: 'User'
          })
        });
        const data = await response.json();
        setSessionId(data.session_id);
        setSuccess(`Session created: ${data.session_id}`);
      } catch (err) {
        setError('Failed to create session');
      }
      setLoading(false);
    };

    const joinSession = async () => {
      if (!sessionId) return;
      
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE}/collaboration/join-session/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            session_id: sessionId,
            participant_name: 'User'
          })
        });
        
        if (response.ok) {
          setIsConnected(true);
          setSuccess('Joined session successfully!');
          // Here you would establish WebSocket connection
        }
      } catch (err) {
        setError('Failed to join session');
      }
      setLoading(false);
    };

    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          <Groups sx={{ mr: 1, verticalAlign: 'middle' }} />
          Real-Time Collaboration
        </Typography>
        
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <TextField
              fullWidth
              label="Session ID"
              value={sessionId}
              onChange={(e) => setSessionId(e.target.value)}
              sx={{ mb: 2 }}
              placeholder="Enter session ID to join or create new"
            />

            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Button
                variant="contained"
                onClick={createSession}
                disabled={loading}
                startIcon={<Groups />}
              >
                Create Session
              </Button>
              <Button
                variant="outlined"
                onClick={joinSession}
                disabled={!sessionId || loading}
                startIcon={<PlayArrow />}
              >
                Join Session
              </Button>
            </Box>

            {isConnected && (
              <Alert severity="success">
                Connected to collaboration session: {sessionId}
              </Alert>
            )}

            <Typography variant="subtitle2" sx={{ mt: 2 }}>
              Participants:
            </Typography>
            <List dense>
              {participants.length > 0 ? (
                participants.map((participant, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={participant.name} />
                    <Chip 
                      label={participant.status} 
                      size="small" 
                      color={participant.status === 'active' ? 'success' : 'default'}
                    />
                  </ListItem>
                ))
              ) : (
                <ListItem>
                  <ListItemText primary="No participants yet" />
                </ListItem>
              )}
            </List>
          </CardContent>
        </Card>
      </Box>
    );
  };

  // Voice Narration Component
  const VoiceNarrationPanel = () => {
    const [voices, setVoices] = useState([]);
    const [selectedVoice, setSelectedVoice] = useState('');
    const [rate, setRate] = useState(180);
    const [volume, setVolume] = useState(0.8);
    const [testText, setTestText] = useState('Hello! This is a test of the voice narration system.');

    useEffect(() => {
      fetchVoices();
    }, []);

    const fetchVoices = async () => {
      try {
        const response = await fetch(`${API_BASE}/narration/available-voices/`);
        const data = await response.json();
        setVoices(data.voices || []);
      } catch (err) {
        console.error('Failed to fetch voices:', err);
      }
    };

    const testSpeech = async () => {
      try {
        await fetch(`${API_BASE}/narration/speak/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            text: testText,
            immediate: 'true'
          })
        });
        setSuccess('Speech test initiated');
      } catch (err) {
        setError('Failed to test speech');
      }
    };

    const configureVoice = async () => {
      try {
        await fetch(`${API_BASE}/narration/configure-voice/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            voice_id: selectedVoice,
            rate: rate.toString(),
            volume: volume.toString()
          })
        });
        setSuccess('Voice configured successfully');
      } catch (err) {
        setError('Failed to configure voice');
      }
    };

    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          <VolumeUp sx={{ mr: 1, verticalAlign: 'middle' }} />
          Voice Narration
        </Typography>
        
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Voice</InputLabel>
              <Select
                value={selectedVoice}
                onChange={(e) => setSelectedVoice(e.target.value)}
              >
                {voices.map((voice) => (
                  <MenuItem key={voice.id} value={voice.id}>
                    {voice.name} ({voice.gender})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Typography gutterBottom>Speech Rate: {rate} WPM</Typography>
            <input
              type="range"
              min="50"
              max="400"
              value={rate}
              onChange={(e) => setRate(parseInt(e.target.value))}
              style={{ width: '100%', marginBottom: '16px' }}
            />

            <Typography gutterBottom>Volume: {Math.round(volume * 100)}%</Typography>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={volume}
              onChange={(e) => setVolume(parseFloat(e.target.value))}
              style={{ width: '100%', marginBottom: '16px' }}
            />

            <TextField
              fullWidth
              multiline
              rows={2}
              label="Test Text"
              value={testText}
              onChange={(e) => setTestText(e.target.value)}
              sx={{ mb: 2 }}
            />

            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="contained"
                onClick={testSpeech}
                startIcon={<PlayArrow />}
              >
                Test Speech
              </Button>
              <Button
                variant="outlined"
                onClick={configureVoice}
                startIcon={<Settings />}
              >
                Apply Settings
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>
    );
  };

  // Project Manager Component
  const ProjectManagerPanel = () => {
    const [projects, setProjects] = useState([]);
    const [templates, setTemplates] = useState([]);
    const [selectedTemplate, setSelectedTemplate] = useState('');
    const [projectName, setProjectName] = useState('');

    useEffect(() => {
      fetchProjects();
      fetchTemplates();
    }, []);

    const fetchProjects = async () => {
      try {
        const response = await fetch(`${API_BASE}/projects/projects/`);
        const data = await response.json();
        setProjects(data.projects || []);
      } catch (err) {
        console.error('Failed to fetch projects:', err);
      }
    };

    const fetchTemplates = async () => {
      try {
        const response = await fetch(`${API_BASE}/projects/templates/`);
        const data = await response.json();
        setTemplates(data.templates || []);
      } catch (err) {
        console.error('Failed to fetch templates:', err);
      }
    };

    const createProject = async () => {
      if (!projectName || !selectedTemplate) return;

      setLoading(true);
      try {
        const formData = new FormData();
        formData.append('project_name', projectName);
        formData.append('template_name', selectedTemplate);

        const response = await fetch(`${API_BASE}/projects/create-project/`, {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          setSuccess(`Project ${projectName} created successfully!`);
          setProjectName('');
          fetchProjects();
        }
      } catch (err) {
        setError('Failed to create project');
      }
      setLoading(false);
    };

    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          <Folder sx={{ mr: 1, verticalAlign: 'middle' }} />
          Project Manager
        </Typography>
        
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <TextField
              fullWidth
              label="Project Name"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              sx={{ mb: 2 }}
            />

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Template</InputLabel>
              <Select
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
              >
                {templates.map((template) => (
                  <MenuItem key={template.id} value={template.id}>
                    {template.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Button
              variant="contained"
              onClick={createProject}
              disabled={!projectName || !selectedTemplate || loading}
              startIcon={<Folder />}
            >
              Create Project
            </Button>
          </CardContent>
        </Card>

        <Typography variant="subtitle1" gutterBottom>
          Existing Projects:
        </Typography>
        <Grid container spacing={2}>
          {projects.map((project) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={project.name}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{project.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {project.files} files
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small">Open</Button>
                  <Button size="small">Download</Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  };

  // Voice Commands Component
  const VoiceCommandsPanel = () => {
    const [commands, setCommands] = useState([]);
    const [commandStatus, setCommandStatus] = useState({});

    useEffect(() => {
      fetchCommands();
      fetchCommandStatus();
    }, []);

    const fetchCommands = async () => {
      try {
        const response = await fetch(`${API_BASE}/commands/available-commands/`);
        const data = await response.json();
        setCommands(data.categories || {});
      } catch (err) {
        console.error('Failed to fetch commands:', err);
      }
    };

    const fetchCommandStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/commands/command-status/`);
        const data = await response.json();
        setCommandStatus(data);
      } catch (err) {
        console.error('Failed to fetch command status:', err);
      }
    };

    const toggleListening = async () => {
      try {
        await fetch(`${API_BASE}/commands/toggle-listening/`, { method: 'POST' });
        fetchCommandStatus();
        setSuccess('Voice listening toggled');
      } catch (err) {
        setError('Failed to toggle listening');
      }
    };

    const executeQuickCommand = async (action) => {
      try {
        const formData = new FormData();
        formData.append('action', action);
        
        await fetch(`${API_BASE}/commands/quick-command/`, {
          method: 'POST',
          body: formData
        });
        setSuccess(`Executed: ${action}`);
      } catch (err) {
        setError(`Failed to execute: ${action}`);
      }
    };

    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          <Mic sx={{ mr: 1, verticalAlign: 'middle' }} />
          Voice Commands
        </Typography>
        
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={commandStatus.listening_active}
                    onChange={toggleListening}
                  />
                }
                label="Voice Listening"
              />
              <Chip 
                label={commandStatus.voice_muted ? 'Muted' : 'Active'}
                color={commandStatus.voice_muted ? 'error' : 'success'}
                sx={{ ml: 2 }}
              />
            </Box>

            <Typography variant="subtitle2" gutterBottom>
              Quick Commands:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
              {['save', 'compile', 'run', 'clear', 'help'].map((cmd) => (
                <Button
                  key={cmd}
                  variant="outlined"
                  size="small"
                  onClick={() => executeQuickCommand(cmd)}
                >
                  {cmd}
                </Button>
              ))}
            </Box>

            <Typography variant="subtitle2" gutterBottom>
              Available Command Categories:
            </Typography>
            {Object.entries(commands).map(([category, cmdList]) => (
              <Accordion key={category}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography>{category} ({cmdList.length})</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {cmdList.map((cmd) => (
                      <Chip key={cmd} label={cmd} size="small" variant="outlined" />
                    ))}
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))}
          </CardContent>
        </Card>
      </Box>
    );
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Advanced Voice IDE Features
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

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<School />} label="Learning Mode" />
          <Tab icon={<Language />} label="Multi-Language" />
          <Tab icon={<Groups />} label="Collaboration" />
          <Tab icon={<VolumeUp />} label="Voice Narration" />
          <Tab icon={<Folder />} label="Project Manager" />
          <Tab icon={<Mic />} label="Voice Commands" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {activeTab === 0 && <LearningModePanel />}
          {activeTab === 1 && <MultiLanguagePanel />}
          {activeTab === 2 && <CollaborationPanel />}
          {activeTab === 3 && <VoiceNarrationPanel />}
          {activeTab === 4 && <ProjectManagerPanel />}
          {activeTab === 5 && <VoiceCommandsPanel />}
        </Box>
      </Paper>
    </Box>
  );
};

export default AdvancedFeatures;
