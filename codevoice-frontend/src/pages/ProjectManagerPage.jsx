import React, { useState, useEffect, useCallback } from 'react';
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
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel,
  InputAdornment
} from '@mui/material';
import { 
  AutoAwesome, 
  GitHub, 
  Download, 
  Code, 
  Rocket, 
  ExpandMore,
  Help
} from '@mui/icons-material';
import { useVoiceControl } from '../context/VoiceControlContext';
import apiService from '../services/apiService';
import config from '../config/api';
import { userService } from '../services/userService';
import MicControl from '../components/MicControl';

const ProjectManagerPage = () => {
  const { speakFeedback } = useVoiceControl();
  
  // AI Project Generation State
  const [projectDescription, setProjectDescription] = useState('');
  const [projectName, setProjectName] = useState('');
  // Must match backend enum values in gemini_project_generator.ProjectType
  // e.g., web_app, mobile_app, desktop_app, api_server, microservice, library, machine_learning, data_analysis, game_dev
  const [projectType, setProjectType] = useState('web_app');
  const [framework, setFramework] = useState('react');
  const [features, setFeatures] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedCode, setGeneratedCode] = useState(null);
  const [generationProgress, setGenerationProgress] = useState(0);
  
  // GitHub Integration State
  const [githubToken, setGithubToken] = useState('');
  const [githubUsername, setGithubUsername] = useState('');
  const [repositoryName, setRepositoryName] = useState('');
  const [isPublicRepo, setIsPublicRepo] = useState(false);
  const [pushToGithub, setPushToGithub] = useState(false);
  const [requireGithubInfo, setRequireGithubInfo] = useState(false);
  
  // UI State
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [showGithubSettings, setShowGithubSettings] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  const handleDescriptionSpeech = useCallback((spokenText = '') => {
    if (!spokenText.trim()) return;
    setProjectDescription(prev => {
      if (!prev) return spokenText.trim();
      const separator = prev.endsWith(' ') ? '' : ' ';
      return `${prev}${separator}${spokenText}`.replace(/\s+/g, ' ').trim();
    });
  }, []);

  const handleNameSpeech = useCallback((spokenText = '') => {
    if (!spokenText.trim()) return;
    setProjectName(spokenText.trim());
  }, []);

  // Available features for selection
  const availableFeatures = [
    'authentication', 'database', 'api', 'responsive-design', 
    'dark-mode', 'notifications', 'real-time-chat', 'file-upload',
    'payment-integration', 'analytics', 'admin-panel', 'mobile-responsive'
  ];

  useEffect(() => {
    // Load current user
    const user = userService.getCurrentUser();
    setCurrentUser(user);
    
    speakFeedback('AI Project Generator loaded. Describe your project idea or say "generate project" to start.');
    loadGithubSettings();
    fetchProjects();
    
    // Listen for voice page actions
    const handleVoiceAction = (event) => {
      const detail = event.detail || {};
      const rawAction = typeof detail.action === 'string' ? detail.action : '';
      const action = rawAction.toLowerCase();
      let handled = false;
      let feedback = '';

      switch (action) {
        case 'generate':
        case 'generate project':
        case 'create project':
          setOpenDialog(true);
          handled = true;
          feedback = 'Opening AI project generator dialog.';
          break;
        case 'github settings':
        case 'setup github':
          setShowGithubSettings(true);
          handled = true;
          feedback = 'Opening GitHub integration settings.';
          break;
        case 'help':
          showHelp();
          handled = true;
          detail.suppressAutoFeedback = true;
          break;
        case 'list projects':
          fetchProjects();
          handled = true;
          feedback = 'Refreshing your project list.';
          break;
        default:
          if (rawAction.length > 10) {
            setProjectDescription(rawAction);
            handled = true;
            feedback = 'Project description captured. Click generate to create your project.';
          }
      }

      if (handled) {
        detail.handled = true;
        if (feedback) detail.feedback = feedback;
      }
    };

    window.addEventListener('voicePageAction', handleVoiceAction);
    return () => window.removeEventListener('voicePageAction', handleVoiceAction);
  }, []);

  const loadGithubSettings = () => {
    const savedToken = localStorage.getItem('githubToken');
    const savedUsername = localStorage.getItem('githubUsername');
    if (savedToken) setGithubToken(savedToken);
    if (savedUsername) setGithubUsername(savedUsername);
  };

  const saveGithubSettings = () => {
    localStorage.setItem('githubToken', githubToken);
    localStorage.setItem('githubUsername', githubUsername);
    setShowGithubSettings(false);
    speakFeedback('GitHub settings saved successfully');
  };

  const fetchProjects = async () => {
    try {
      // Use new database API
      const data = await apiService.listProjectsDB();
      setProjects(data.projects || []);
    } catch (err) {
      console.error('Failed to fetch projects:', err);
      // Fallback to old API if new one fails
      try {
        const data = await apiService.getProjects(currentUser?.id || '');
        setProjects((data && (data.projects || data.data || [])));
      } catch (fallbackErr) {
        console.error('Fallback also failed:', fallbackErr);
      }
    }
  };

  const generateProject = async () => {
    if (!projectDescription.trim() || !projectName.trim()) {
      setError('Please enter project name and description');
      speakFeedback('Please enter project name and description');
      return;
    }

    if (!currentUser || !currentUser.id) {
      setError('Please log in to create projects');
      speakFeedback('Please log in to create projects');
      return;
    }

    setIsGenerating(true);
    setGenerationProgress(0);
    let progressInterval;
    try {
      // Progress tracking
      progressInterval = setInterval(() => {
        setGenerationProgress(prev => {
          if (prev >= 80) {
            if (progressInterval) clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 800);

      speakFeedback('Generating your project with AI intelligence...');
      
      // Build request payload to match backend ProjectGenerationRequest
      const geminiRequest = {
        project_name: projectName,
        description: projectDescription,
        project_type: projectType, // must be one of backend enums (e.g., 'web_app', 'api_server')
        framework: framework,      // must be one of backend enums (e.g., 'react', 'fastapi')
        features: features,
        technologies: [],
        include_tests: false,
        include_docker: false,
        include_ci_cd: false,
        database_type: null,
        authentication: features.includes('authentication'),
        api_documentation: true,
        // Use valid complexity enums: basic | intermediate | advanced | enterprise
        complexity: features.length > 6 ? 'advanced' : (features.length > 2 ? 'intermediate' : 'basic')
      };

      // Use Gemini AI for intelligent project generation (async path)
      setGenerationProgress(20);
      // Preflight health check
      try {
        const health = await apiService.getGeminiHealth();
        if (!health || health.status !== 'healthy') {
          throw new Error('Gemini not configured');
        }
      } catch (e) {
        speakFeedback('Gemini API is not configured. Falling back to basic project creation.');
        throw new Error('Gemini not available');
      }
      speakFeedback('Using Gemini AI to understand your requirements...');

      // Enqueue async generation so we can stream progress via websocket
      const enqueueResp = await apiService.generateGeminiProjectAsync(geminiRequest);

      if (!enqueueResp || !enqueueResp.task_id) {
        // Fallback to synchronous generation if async enqueue not available
        speakFeedback('Async generation not available; attempting synchronous generation');
        const geminiResponse = await apiService.generateGeminiProject(geminiRequest);

        setGenerationProgress(50);
        speakFeedback('Generating project structure and files...');

        if (geminiResponse && geminiResponse.success) {
          setGenerationProgress(70);
          const generated = geminiResponse.project || {};

        // Create the actual project in the database (store structure as part of metadata)
        const dbProjectData = {
          name: projectName,
          description: projectDescription,
          project_type: projectType,
          framework: framework,
          features: features,
          ai_generated: true,
          user_id: currentUser.id,
          gemini_metadata: generated, // preserve entire generation payload
          project_structure: generated.project_structure || {},
          recommended_dependencies: generated.recommended_dependencies || {},
          environment_variables: generated.environment_variables || {},
          scripts: generated.scripts || {},
          setup_instructions: generated.setup_instructions || []
        };

        const data = await apiService.createProjectDB(dbProjectData);
        
  if (progressInterval) clearInterval(progressInterval);
        setGenerationProgress(100);
        
        if (data && data.success) {
          setGeneratedCode({
            project: data.project,
            structure: generated.project_structure || {},
            dependencies: (generated.recommended_dependencies && (generated.recommended_dependencies.production || [])) || [],
            setup_instructions: generated.setup_instructions || [],
            notes: generated.architecture_notes || ''
          });
          setSuccess(`AI-powered project "${projectName}" created successfully!`);
          speakFeedback(`AI project ${projectName} created successfully with ${features.length} features and intelligent code generation`);
          
          // If user wants to push to GitHub, ensure credentials exist and prompt for repo name
          if (pushToGithub) {
            if (!githubUsername || !githubToken) {
              setRequireGithubInfo(true);
              setShowGithubSettings(true);
              speakFeedback('Please provide your GitHub username and token to create a repository.');
            } else {
              try {
                const repo = await apiService.createGithubRepo({
                  repo_name: (repositoryName || projectName).replace(/\s+/g, '-').toLowerCase(),
                  description: projectDescription,
                  private: !isPublicRepo
                });
                if (repo?.success) {
                  setSuccess('GitHub repository created successfully');
                }
              } catch (e) {
                console.error('GitHub repo creation failed', e);
              }
            }
          }

          // Reset form
          setProjectDescription('');
          setProjectName('');
          setFeatures([]);
          setOpenDialog(false);
          fetchProjects();
        } else {
          throw new Error(data.message || 'Failed to create project');
        }
        }
      } else {
        // We received a task id — subscribe to progress via WebSocket
        const taskId = enqueueResp.task_id;
        const wsProtocol = config.API_URL.startsWith('https') ? 'wss' : 'ws';
        const wsHost = config.API_URL.replace(/^https?:/, '');
        const wsUrl = `${wsProtocol}:${wsHost}/api/project-generation/ws/tasks/${taskId}`;

        speakFeedback('Project generation started. Streaming progress now.');

        await new Promise((resolve, reject) => {
          try {
            const ws = new WebSocket(wsUrl);
            ws.onmessage = async (evt) => {
              try {
                const msg = JSON.parse(evt.data);
                // Update progress by status
                if (msg.status === 'queued') setGenerationProgress(25);
                else if (msg.status === 'running' || msg.status === 'in_progress') setGenerationProgress(55);
                else if (msg.status === 'completed') setGenerationProgress(95);

                if (msg.status === 'completed') {
                  // If result contains project payload, save to DB
                  const generated = msg.result && msg.result.response ? msg.result.response : null;
                  // Try to create project record if we have structured project
                  if (generated && generated.project) {
                    const dbProjectData = {
                      name: projectName,
                      description: projectDescription,
                      project_type: projectType,
                      framework: framework,
                      features: features,
                      ai_generated: true,
                      user_id: currentUser.id,
                      gemini_metadata: generated,
                      project_structure: generated.project_structure || {},
                      recommended_dependencies: generated.recommended_dependencies || {},
                      environment_variables: generated.environment_variables || {},
                      scripts: generated.scripts || {},
                      setup_instructions: generated.setup_instructions || []
                    };
                    try {
                      const data = await apiService.createProjectDB(dbProjectData);
                      if (data && data.success) {
                        setGeneratedCode({ project: data.project, structure: generated.project_structure || {} });
                        setSuccess(`AI-powered project "${projectName}" created successfully!`);
                        speakFeedback(`AI project ${projectName} created successfully`);
                        fetchProjects();
                      }
                    } catch (e) {
                      console.error('Failed to save project after generation', e);
                    }
                  }

                  ws.close();
                  resolve();
                }
              } catch (err) {
                console.error('WS message handling error', err);
              }
            };
            ws.onerror = (err) => {
              console.error('WebSocket error', err);
            };
            ws.onclose = () => resolve();
          } catch (err) {
            reject(err);
          }
        });
      }
    } catch (err) {
      if (progressInterval) clearInterval(progressInterval);
      setError(`Failed to create AI project: ${err.message}`);
      speakFeedback('Failed to create AI project. Please check your description and try again.');
      
      // Fallback to basic project creation if AI fails
      try {
        speakFeedback('Falling back to basic project creation...');
        const basicProjectData = {
          name: projectName,
          description: projectDescription,
          framework: framework,
          features: features,
          is_public: false,
          user_id: currentUser.id,
          ai_generated: false
        };
        
        const data = await apiService.createProjectDB(basicProjectData);
        
        if (data && data.success) {
          setSuccess(`Basic project "${projectName}" created successfully!`);
          speakFeedback(`Basic project ${projectName} created as fallback`);
          setProjectDescription('');
          setProjectName('');
          setFeatures([]);
          setOpenDialog(false);
          fetchProjects();
        }
      } catch (fallbackErr) {
        console.error('Both AI and fallback creation failed:', fallbackErr);
      }
    } finally {
      setIsGenerating(false);
      setGenerationProgress(0);
    }
  };

  const handleFeatureToggle = (feature) => {
    setFeatures(prev => {
      const newFeatures = prev.includes(feature) 
        ? prev.filter(f => f !== feature)
        : [...prev, feature];
      
      speakFeedback(`${prev.includes(feature) ? 'Removed' : 'Added'} ${feature} feature`);
      return newFeatures;
    });
  };

  const downloadProject = async (projectName) => {
    try {
      const response = await fetch(`http://localhost:8000/projects/projects/${projectName}/download/`, {
        headers: {
          'X-User-Id': currentUser.id
        }
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${projectName}.zip`;
        a.click();
        speakFeedback(`Project ${projectName} downloaded`);
      } else {
        speakFeedback('Download failed: ' + response.statusText);
      }
    } catch (err) {
      console.error('Download failed:', err);
      speakFeedback('Download failed');
    }
  };

  const showHelp = () => {
    const helpText = `AI Project Generator voice commands:
    Say "Generate project" to create a new AI-powered project
    Say "GitHub settings" to configure GitHub integration
    Describe your project idea naturally, like "Create a blog website with user authentication"
    Say "Add authentication" or similar to add features`;
    speakFeedback(helpText);
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <AutoAwesome color="primary" />
        AI Project Generator
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
        🎤 Voice Commands: "Generate project", "GitHub settings", or describe your project idea naturally
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

      {/* Main Generation Card */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Rocket />
          Describe Your Project Idea
        </Typography>
        
        <Box sx={{ position: 'relative', mb: 2 }}>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={projectDescription}
            onChange={(e) => setProjectDescription(e.target.value)}
            placeholder="Describe your project idea in natural language... e.g., 'Create a social media app with real-time chat, user profiles, and photo sharing'"
            sx={{ pr: 6 }}
          />
          <Box sx={{ position: 'absolute', right: 8, bottom: 8 }}>
            <MicControl
              onTranscript={handleDescriptionSpeech}
              tooltip="Speak project description"
            />
          </Box>
        </Box>

        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid size={{ xs: 12, md: 6 }}>
            <TextField
              fullWidth
              label="Project Name"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="my-awesome-project"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <MicControl
                      onTranscript={handleNameSpeech}
                      tooltip="Speak project name"
                    />
                  </InputAdornment>
                )
              }}
            />
          </Grid>
          <Grid size={{ xs: 12, md: 3 }}>
            <FormControl fullWidth>
              <InputLabel>Project Type</InputLabel>
              <Select value={projectType} onChange={(e) => setProjectType(e.target.value)}>
                {/* Values must match backend enums */}
                <MenuItem value="web_app">Web App</MenuItem>
                <MenuItem value="api_server">API Server</MenuItem>
                <MenuItem value="mobile_app">Mobile App</MenuItem>
                <MenuItem value="desktop_app">Desktop App</MenuItem>
                <MenuItem value="microservice">Microservice</MenuItem>
                <MenuItem value="library">Library</MenuItem>
                <MenuItem value="data_analysis">Data Analysis</MenuItem>
                <MenuItem value="machine_learning">Machine Learning</MenuItem>
                <MenuItem value="game_dev">Game Dev</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 3 }}>
            <FormControl fullWidth>
              <InputLabel>Framework</InputLabel>
              <Select value={framework} onChange={(e) => setFramework(e.target.value)}>
                {/* Frontend */}
                <MenuItem value="react">React</MenuItem>
                <MenuItem value="nextjs">Next.js</MenuItem>
                <MenuItem value="vue">Vue.js</MenuItem>
                <MenuItem value="angular">Angular</MenuItem>
                <MenuItem value="svelte">Svelte</MenuItem>
                {/* Backend */}
                <MenuItem value="fastapi">FastAPI</MenuItem>
                <MenuItem value="flask">Flask</MenuItem>
                <MenuItem value="django">Django</MenuItem>
                <MenuItem value="express">Express</MenuItem>
                <MenuItem value="spring_boot">Spring Boot</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Features Selection */}
        <Typography variant="subtitle1" gutterBottom>
          Select Features (click or use voice):
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
          {availableFeatures.map((feature) => (
            <Chip
              key={feature}
              label={feature}
              onClick={() => handleFeatureToggle(feature)}
              color={features.includes(feature) ? 'primary' : 'default'}
              variant={features.includes(feature) ? 'filled' : 'outlined'}
            />
          ))}
        </Box>

        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<AutoAwesome />}
            onClick={() => setOpenDialog(true)}
            disabled={!projectDescription.trim() || !projectName.trim()}
          >
            Generate Project
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<GitHub />}
            onClick={() => setShowGithubSettings(true)}
          >
            GitHub Settings
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<Help />}
            onClick={showHelp}
          >
            Voice Help
          </Button>
        </Box>
      </Paper>

      {/* GitHub Integration Settings */}
      <Accordion expanded={showGithubSettings} onChange={() => setShowGithubSettings(!showGithubSettings)}>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6">
            <GitHub sx={{ mr: 1, verticalAlign: 'middle' }} />
            GitHub Integration
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="GitHub Username"
                value={githubUsername}
                onChange={(e) => setGithubUsername(e.target.value)}
                placeholder="your-username"
                required={requireGithubInfo}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                type="password"
                label="GitHub Personal Access Token"
                value={githubToken}
                onChange={(e) => setGithubToken(e.target.value)}
                placeholder="ghp_..."
                required={requireGithubInfo}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Repository Name"
                value={repositoryName}
                onChange={(e) => setRepositoryName(e.target.value)}
                placeholder={projectName || 'my-repo'}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={pushToGithub}
                    onChange={(e) => setPushToGithub(e.target.checked)}
                  />
                }
                label="Automatically push generated projects to GitHub"
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <Button variant="contained" onClick={saveGithubSettings}>
                Save GitHub Settings
              </Button>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Project Generation Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <AutoAwesome sx={{ mr: 1, verticalAlign: 'middle' }} />
          Generate AI Project
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            Project: <strong>{projectName}</strong>
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {projectDescription}
          </Typography>
          
          {features.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2">Features:</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                {features.map(feature => (
                  <Chip key={feature} label={feature} size="small" />
                ))}
              </Box>
            </Box>
          )}

          {isGenerating && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="body2" gutterBottom>
                Generating your project... {generationProgress}%
              </Typography>
              <LinearProgress variant="determinate" value={generationProgress} />
            </Box>
          )}

          {pushToGithub && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="subtitle2">
                <GitHub sx={{ mr: 1, verticalAlign: 'middle' }} />
                Will be pushed to GitHub
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Repository: {githubUsername}/{repositoryName || projectName}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={generateProject}
            disabled={isGenerating}
            startIcon={<AutoAwesome />}
          >
            {isGenerating ? 'Generating...' : 'Generate Project'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Generated Projects List */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Your Generated Projects ({projects.length})
        </Typography>
        
        {projects.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No projects generated yet. Create your first AI-powered project above!
          </Typography>
        ) : (
          <Grid container spacing={2}>
            {projects.map((project, index) => (
              <Grid size={{ xs: 12, md: 6, lg: 4 }} key={index}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {project.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {project.description || 'No description available'}
                    </Typography>
                    <Chip 
                      label={project.framework || 'Unknown'} 
                      size="small" 
                      sx={{ mb: 2 }}
                    />
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        size="small"
                        startIcon={<Download />}
                        onClick={() => downloadProject(project.name)}
                      >
                        Download
                      </Button>
                      <Button
                        size="small"
                        startIcon={<Code />}
                        onClick={() => window.open(project.githubUrl, '_blank')}
                        disabled={!project.githubUrl}
                      >
                        GitHub
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>

      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 3 }}>
        <Chip label="🎤 Generate project" variant="outlined" />
        <Chip label="🎤 Add authentication" variant="outlined" />
        <Chip label="🎤 GitHub settings" variant="outlined" />
        <Chip label="🎤 Help" variant="outlined" />
      </Box>
    </Box>
  );
};

export default ProjectManagerPage;