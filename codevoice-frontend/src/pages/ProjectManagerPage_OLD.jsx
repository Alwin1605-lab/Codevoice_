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
  FormControlLabel,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  AutoAwesome, 
  GitHub, 
  Download, 
  Code, 
  Rocket, 
  PlayArrow,
  ExpandMore,
  Settings,
  Mic,
  Help,
  CloudUpload,
  Share
} from '@mui/icons-material';
import { useVoiceControl } from '../context/VoiceControlContext';
import apiService from '../services/apiService';

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

  // Available features for selection
  const availableFeatures = [
    'authentication', 'database', 'api', 'responsive-design', 
    'dark-mode', 'notifications', 'real-time-chat', 'file-upload',
    'payment-integration', 'analytics', 'admin-panel', 'mobile-responsive'
  ];

  useEffect(() => {
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
          speakFeedback('New project dialog opened');
          break;
        case 'list':
        case 'list projects':
          fetchProjects();
          speakFeedback(`You have ${projects.length} projects`);
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
  }, [projects.length]);

  const fetchProjects = async () => {
    try {
      const data = await apiService.listProjects();
      setProjects(data.projects || []);
    } catch (err) {
      console.error('Failed to fetch projects:', err);
    }
  };

  const fetchTemplates = async () => {
    try {
      const data = await apiService.getProjectTemplates();
      setTemplates(data.templates || []);
    } catch (err) {
      console.error('Failed to fetch templates:', err);
    }
  };

  const createProject = async () => {
    if (!projectName.trim() || !selectedTemplate) {
      setError('Please enter project name and select a template');
      speakFeedback('Please enter project name and select a template');
      return;
    }

    setLoading(true);
    try {
      const data = await apiService.createProject(projectName, selectedTemplate);
      
      if (data) {
        setSuccess(`Project ${projectName} created successfully!`);
        speakFeedback(`Project ${projectName} created successfully using ${selectedTemplate} template`);
        setProjectName('');
        setSelectedTemplate('');
        setOpenDialog(false);
        fetchProjects();
      }
    } catch (err) {
      setError('Failed to create project');
      speakFeedback('Failed to create project. Please try again.');
    }
    setLoading(false);
  };

  const downloadProject = async (projectName) => {
    try {
      // Note: This would need a corresponding API method in apiService
      // For now, using direct fetch as download endpoints may need special handling
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
    const helpText = `Project Manager voice commands:
    Say "New project" or "Create project" to create a new project
    Say "List projects" to refresh the project list
    Say "React project", "Django project", "Node project", or "Python project" to select templates`;
    speakFeedback(helpText);
  };

  // Voice commands for template selection
  useEffect(() => {
    const handleVoiceTemplateSelection = (event) => {
      const { action } = event.detail;
      const templateMap = {
        'react project': 'react_app',
        'react app': 'react_app',
        'django project': 'django_app',
        'django app': 'django_app',
        'node project': 'node_api',
        'node app': 'node_api',
        'python project': 'python_cli',
        'python app': 'python_cli'
      };
      
      if (templateMap[action]) {
        setSelectedTemplate(templateMap[action]);
        speakFeedback(`Selected ${action} template`);
      }
    };

    window.addEventListener('voicePageAction', handleVoiceTemplateSelection);
    return () => window.removeEventListener('voicePageAction', handleVoiceTemplateSelection);
  }, []);

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Folder color="primary" />
        Project Manager
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
        🎤 Voice Commands: "New project", "Create project", "React project", "Django project"
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
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Your Projects ({projects.length})
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setOpenDialog(true)}
          >
            New Project
          </Button>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 3 }}>
          <Chip label="🎤 New project" variant="outlined" />
          <Chip label="🎤 React project" variant="outlined" />
          <Chip label="🎤 Django project" variant="outlined" />
          <Chip label="🎤 Node project" variant="outlined" />
          <Chip label="🎤 Python project" variant="outlined" />
        </Box>

        {projects.length > 0 ? (
          <Grid container spacing={2}>
            {projects.map((project) => (
              <Grid item xs={12} sm={6} md={4} key={project.name}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <Code sx={{ mr: 1, verticalAlign: 'middle' }} />
                      {project.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {project.files} files
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Path: {project.path}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                      <Button 
                        size="small"
                        onClick={() => {
                          speakFeedback(`Opening project ${project.name}`);
                          // Implement project opening logic
                        }}
                      >
                        Open
                      </Button>
                      <Button 
                        size="small"
                        startIcon={<Download />}
                        onClick={() => downloadProject(project.name)}
                      >
                        Download
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Typography variant="body1" color="text.secondary">
            No projects yet. Create your first project using the "New Project" button or say "New project".
          </Typography>
        )}
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Available Templates
        </Typography>
        <Grid container spacing={2}>
          {templates.map((template) => (
            <Grid item xs={12} sm={6} md={3} key={template.id}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  border: selectedTemplate === template.id ? 2 : 1,
                  borderColor: selectedTemplate === template.id ? 'primary.main' : 'divider'
                }}
                onClick={() => {
                  setSelectedTemplate(template.id);
                  speakFeedback(`Selected ${template.name} template`);
                }}
              >
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <Build sx={{ mr: 1, verticalAlign: 'middle' }} />
                    {template.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {template.files_count} files included
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Create Project Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Project</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Project Name"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            sx={{ mb: 2, mt: 1 }}
            placeholder="Enter project name"
          />

          <FormControl fullWidth>
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
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button 
            onClick={createProject} 
            variant="contained"
            disabled={!projectName || !selectedTemplate || loading}
          >
            Create Project
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProjectManagerPage;