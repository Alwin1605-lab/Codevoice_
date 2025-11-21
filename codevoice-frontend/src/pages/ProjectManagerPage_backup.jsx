import React, { useState, useEffect } from 'react';
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
  FormControlLabel
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
import { userService } from '../services/userService';

const ProjectManagerPage = () => {
  const { speakFeedback } = useVoiceControl();
  
  // AI Project Generation State
  const [projectDescription, setProjectDescription] = useState('');
  const [projectName, setProjectName] = useState('');
  const [projectType, setProjectType] = useState('web-app');
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
  
  // UI State
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [showGithubSettings, setShowGithubSettings] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

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
      const { action } = event.detail;
      switch (action) {
        case 'generate':
        case 'generate project':
        case 'create project':
          setOpenDialog(true);
          break;
        case 'github settings':
        case 'setup github':
          setShowGithubSettings(true);
          break;
        case 'help':
          showHelp();
          break;
        case 'list projects':
          fetchProjects();
          break;
        default:
          // Check if it's a project description
          if (action.length > 10) {
            setProjectDescription(action);
            speakFeedback('Project description captured. Click generate to create your project.');
          }
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
        const data = await apiService.listProjects();
        setProjects(data.projects || []);
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
    
    try {
      // Progress tracking
      const progressInterval = setInterval(() => {
        setGenerationProgress(prev => {
          if (prev >= 80) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 800);

      speakFeedback('Generating your project with AI intelligence...');
      
      const projectData = {
        name: projectName,
        description: projectDescription,
        natural_language_prompt: projectDescription,
        project_type: projectType,
        framework: framework,
        features: features,
        is_public: false,
        user_id: currentUser.id,
        use_ai_generation: true,
        complexity: features.length > 5 ? 'advanced' : 'standard'
      };

      // Use Gemini AI for intelligent project generation
      setGenerationProgress(20);
      speakFeedback('Using Gemini AI to understand your requirements...');
      
      const geminiResponse = await apiService.generateGeminiProject(projectData);
      
      setGenerationProgress(50);
      speakFeedback('Generating project structure and files...');
      
      if (geminiResponse && geminiResponse.success) {
        setGenerationProgress(70);
        
        // Create the actual project in the database
        const dbProjectData = {
          ...projectData,
          ai_generated: true,
          project_structure: geminiResponse.project_structure,
          generated_files: geminiResponse.files,
          technical_details: geminiResponse.technical_details,
          dependencies: geminiResponse.dependencies
        };

        const data = await apiService.createProjectDB(dbProjectData);
        
        clearInterval(progressInterval);
        setGenerationProgress(100);
        
        if (data && data.success) {
          setGeneratedCode({
            project: data.project,
            files: geminiResponse.files || [],
            structure: geminiResponse.project_structure || {},
            dependencies: geminiResponse.dependencies || [],
            technical_details: geminiResponse.technical_details || ''
          });
          setSuccess(`AI-powered project "${projectName}" created successfully!`);
          speakFeedback(`AI project ${projectName} created successfully with ${features.length} features and intelligent code generation`);
          
          // Reset form
          setProjectDescription('');
          setProjectName('');
          setFeatures([]);
          setOpenDialog(false);
          fetchProjects();
        } else {
          throw new Error(data.message || 'Failed to create project');
        }
      } else {
        throw new Error(geminiResponse.message || 'Failed to generate project with AI');
      }
    } catch (err) {
      clearInterval(progressInterval);
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
        
        // Save usage analytics
        try {
          await apiService.saveUsageAnalyticsDB({
            user_id: currentUser.id,
            feature_used: "project_creation",
            session_duration_seconds: Math.floor((Date.now() - Date.now()) / 1000),
            actions_performed: 1,
            errors_encountered: 0,
            success_rate: 100.0,
            additional_data: {
              project_name: projectName,
              framework: framework,
              features_count: features.length
            }
          });
        } catch (analyticsErr) {
          console.warn('Failed to save analytics:', analyticsErr);
        }
        
        // Reset form
        setProjectDescription('');
        setProjectName('');
        setFeatures([]);
        setOpenDialog(false);
        fetchProjects();
      }
    } catch (err) {
      clearInterval(progressInterval);
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
      const response = await fetch(`http://localhost:8000/projects/projects/${projectName}/download/`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${projectName}.zip`;
        a.click();
        speakFeedback(`Project ${projectName} downloaded`);
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
        
        <TextField
          fullWidth
          multiline
          rows={4}
          value={projectDescription}
          onChange={(e) => setProjectDescription(e.target.value)}
          placeholder="Describe your project idea in natural language... e.g., 'Create a social media app with real-time chat, user profiles, and photo sharing'"
          sx={{ mb: 2 }}
        />

        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid size={{ xs: 12, md: 6 }}>
            <TextField
              fullWidth
              label="Project Name"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="my-awesome-project"
            />
          </Grid>
          <Grid size={{ xs: 12, md: 3 }}>
            <FormControl fullWidth>
              <InputLabel>Project Type</InputLabel>
              <Select value={projectType} onChange={(e) => setProjectType(e.target.value)}>
                <MenuItem value="web-app">Web Application</MenuItem>
                <MenuItem value="mobile-app">Mobile App</MenuItem>
                <MenuItem value="api">REST API</MenuItem>
                <MenuItem value="desktop-app">Desktop App</MenuItem>
                <MenuItem value="chrome-extension">Chrome Extension</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 3 }}>
            <FormControl fullWidth>
              <InputLabel>Framework</InputLabel>
              <Select value={framework} onChange={(e) => setFramework(e.target.value)}>
                <MenuItem value="react">React</MenuItem>
                <MenuItem value="nextjs">Next.js</MenuItem>
                <MenuItem value="vue">Vue.js</MenuItem>
                <MenuItem value="angular">Angular</MenuItem>
                <MenuItem value="svelte">Svelte</MenuItem>
                <MenuItem value="vanilla">Vanilla JS</MenuItem>
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