import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useVoiceControl } from '../context/VoiceControlContext';
import {
    Container,
    TextField,
    Button,
    Typography,
    Box,
    Alert,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    FormControlLabel,
    Checkbox,
    FormLabel,
    FormGroup,
    Grid,
    Switch,
    Card,
    CardContent,
    CardHeader,
    Chip
} from '@mui/material';
import {
    Person,
    Mic,
    VolumeUp,
    Accessibility,
    Code,
    GitHub,
    Save,
    Help
} from '@mui/icons-material';

const ProfilePage = () => {
    const { user, updateProfile } = useAuth();
    const { speakFeedback } = useVoiceControl();
    
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        disability: '',
        canType: false,
        preferredInputMethod: '',
        typingSpeed: '',
        additionalNeeds: '',
        programmingExperience: '',
        preferredLanguages: [],
        assistiveTechnologies: {
            screenReader: false,
            voiceControl: false,
            switchControl: false,
            other: ''
        },
        voiceSettings: {
            enabled: true,
            speed: 1.0,
            pitch: 1.0,
            volume: 0.8,
            voice: 'default',
            language: 'en-US'
        },
        githubSettings: {
            username: '',
            token: '',
            defaultVisibility: 'public'
        },
        preferences: {
            theme: 'dark',
            fontSize: 'medium',
            autoSave: true,
            notifications: true
        }
    });
    
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [pendingChanges, setPendingChanges] = useState({});
    const [confirmationPending, setConfirmationPending] = useState(null);

    const programmingLanguages = [
        'JavaScript', 'Python', 'Java', 'C++', 'C#', 'React', 'Node.js', 
        'PHP', 'Ruby', 'Go', 'Rust', 'TypeScript', 'Swift', 'Kotlin'
    ];

    const mapBackendToFormData = (backendUser) => {
        return {
            name: backendUser.full_name || '',
            email: backendUser.email || '',
            disability: backendUser.disability || '',
            canType: backendUser.can_type || false,
            preferredInputMethod: backendUser.preferred_input_method || '',
            typingSpeed: backendUser.typing_speed || '',
            additionalNeeds: backendUser.additional_needs || '',
            programmingExperience: backendUser.programming_experience || '',
            preferredLanguages: backendUser.preferred_languages || [],
            assistiveTechnologies: {
                screenReader: backendUser.assistive_technologies?.screen_reader || false,
                voiceControl: backendUser.assistive_technologies?.voice_control || false,
                switchControl: backendUser.assistive_technologies?.switch_control || false,
                other: backendUser.assistive_technologies?.other || ''
            },
            voiceSettings: backendUser.voice_settings || {
                enabled: true,
                speed: 1.0,
                pitch: 1.0,
                volume: 0.8,
                voice: 'default',
                language: 'en-US'
            },
            githubSettings: {
                username: backendUser.github_username || '',
                token: '',
                defaultVisibility: 'public'
            },
            preferences: {
                theme: 'dark',
                fontSize: 'medium',
                autoSave: true,
                notifications: true
            }
        };
    };

    const handleFieldVoiceCommands = useCallback((action) => {
        // Voice commands for specific fields with confirmation
        if (action.startsWith('name is ') || action.startsWith('set name to ')) {
            const name = action.replace('name is ', '').replace('set name to ', '');
            setPendingChanges({ field: 'name', value: name, label: 'name' });
            setConfirmationPending({ field: 'name', value: name, label: 'name' });
            speakFeedback(`Do you want to change your name to ${name}? Say yes to confirm or no to cancel.`);
        } else if (action.startsWith('email is ') || action.startsWith('set email to ')) {
            const email = action.replace('email is ', '').replace('set email to ', '');
            setPendingChanges({ field: 'email', value: email, label: 'email' });
            setConfirmationPending({ field: 'email', value: email, label: 'email' });
            speakFeedback(`Do you want to change your email to ${email}? Say yes to confirm or no to cancel.`);
        } else if (action.startsWith('speed ') || action.startsWith('set speed to ')) {
            const speed = parseFloat(action.replace('speed ', '').replace('set speed to ', ''));
            if (!isNaN(speed) && speed >= 0.5 && speed <= 2.0) {
                setPendingChanges({ field: 'voiceSettings.speed', value: speed, label: 'voice speed' });
                setConfirmationPending({ field: 'voiceSettings.speed', value: speed, label: 'voice speed' });
                speakFeedback(`Do you want to change voice speed to ${speed}? Say yes to confirm or no to cancel.`);
            }
        } else if (action.startsWith('pitch ') || action.startsWith('set pitch to ')) {
            const pitch = parseFloat(action.replace('pitch ', '').replace('set pitch to ', ''));
            if (!isNaN(pitch) && pitch >= 0.5 && pitch <= 2.0) {
                setPendingChanges({ field: 'voiceSettings.pitch', value: pitch, label: 'voice pitch' });
                setConfirmationPending({ field: 'voiceSettings.pitch', value: pitch, label: 'voice pitch' });
                speakFeedback(`Do you want to change voice pitch to ${pitch}? Say yes to confirm or no to cancel.`);
            }
        } else if (action.startsWith('volume ') || action.startsWith('set volume to ')) {
            const volume = parseFloat(action.replace('volume ', '').replace('set volume to ', ''));
            if (!isNaN(volume) && volume >= 0.0 && volume <= 1.0) {
                setPendingChanges({ field: 'voiceSettings.volume', value: volume, label: 'volume' });
                setConfirmationPending({ field: 'voiceSettings.volume', value: volume, label: 'volume' });
                speakFeedback(`Do you want to change volume to ${volume}? Say yes to confirm or no to cancel.`);
            }
        } else if (action.includes('enable voice control')) {
            setPendingChanges({ field: 'voiceSettings.enabled', value: true, label: 'voice control' });
            setConfirmationPending({ field: 'voiceSettings.enabled', value: true, label: 'voice control' });
            speakFeedback('Do you want to enable voice control? Say yes to confirm or no to cancel.');
        } else if (action.includes('disable voice control')) {
            setPendingChanges({ field: 'voiceSettings.enabled', value: false, label: 'voice control' });
            setConfirmationPending({ field: 'voiceSettings.enabled', value: false, label: 'voice control' });
            speakFeedback('Do you want to disable voice control? Say yes to confirm or no to cancel.');
        } else if (action.startsWith('github username ') || action.startsWith('set github username to ')) {
            const username = action.replace('github username ', '').replace('set github username to ', '');
            setPendingChanges({ field: 'githubSettings.username', value: username, label: 'GitHub username' });
            setConfirmationPending({ field: 'githubSettings.username', value: username, label: 'GitHub username' });
            speakFeedback(`Do you want to set GitHub username to ${username}? Say yes to confirm or no to cancel.`);
        } else if (action.includes('beginner') || action.includes('intermediate') || action.includes('advanced') || action.includes('expert')) {
            let experience = 'beginner';
            if (action.includes('intermediate')) experience = 'intermediate';
            else if (action.includes('advanced')) experience = 'advanced';
            else if (action.includes('expert')) experience = 'expert';
            setPendingChanges({ field: 'programmingExperience', value: experience, label: 'programming experience' });
            setConfirmationPending({ field: 'programmingExperience', value: experience, label: 'programming experience' });
            speakFeedback(`Do you want to set programming experience to ${experience}? Say yes to confirm or no to cancel.`);
        } else if (action.includes('yes') && confirmationPending) {
            applyPendingChange();
        } else if (action.includes('no') && confirmationPending) {
            cancelPendingChange();
        }
    }, [speakFeedback, confirmationPending]);

    const applyPendingChange = useCallback(() => {
        if (!confirmationPending) return;
        
        const { field, value, label } = confirmationPending;
        
        if (field.includes('.')) {
            const [section, subfield] = field.split('.');
            setFormData(prev => ({
                ...prev,
                [section]: { ...prev[section], [subfield]: value }
            }));
        } else {
            setFormData(prev => ({ ...prev, [field]: value }));
        }
        
        speakFeedback(`${label} has been changed. Say "save changes" to save your profile.`);
        setConfirmationPending(null);
        setPendingChanges({});
    }, [confirmationPending, speakFeedback]);

    const cancelPendingChange = useCallback(() => {
        if (!confirmationPending) return;
        speakFeedback(`Change to ${confirmationPending.label} cancelled.`);
        setConfirmationPending(null);
        setPendingChanges({});
    }, [confirmationPending, speakFeedback]);

    const handleSave = useCallback(async () => {
        try {
            const backendFormData = mapFormDataToBackend(formData);
            await updateProfile(user.id, backendFormData);
            setSuccess('Profile updated successfully!');
            setError('');
            speakFeedback('Profile saved successfully');
        } catch (err) {
            console.error('Profile update error:', err);
            setError('Failed to update profile');
            speakFeedback('Failed to save profile. Please try again.');
        }
    }, [formData, user?.id, updateProfile, speakFeedback]);

    const showHelp = useCallback(() => {
        const helpText = `Profile page voice commands:
        Say "Name is [your name]" to change your name
        Say "Email is [email]" to change your email
        Say "Speed [number from 0.5 to 2]" to adjust voice speed
        Say "Pitch [number from 0.5 to 2]" to adjust voice pitch
        Say "Volume [number from 0 to 1]" to adjust volume
        Say "Enable voice control" or "Disable voice control"
        Say "GitHub username [username]" to set GitHub username
        Say "Beginner", "Intermediate", "Advanced", or "Expert" for experience level
        Say "Yes" to confirm changes or "No" to cancel
        Say "Save changes" to save your profile
        Say "Scroll down", "Scroll up", "Scroll left", or "Scroll right" to navigate
        Say "Help" for this message`;
        speakFeedback(helpText);
    }, [speakFeedback]);

    useEffect(() => {
        speakFeedback('Profile page loaded. You can change any setting by voice. For example, say "Speed 1.5" or "Name is John". Say "Help" for all commands.');
        
        if (user) {
            const mappedUserData = mapBackendToFormData(user);
            setFormData(prevData => ({
                ...prevData,
                ...mappedUserData
            }));
        }

        // Listen for voice page actions
        const handleVoiceAction = (event) => {
            const detail = event.detail;
            const action = typeof detail === 'string' ? detail : detail?.action;
            if (!action) return;

            switch (action) {
                case 'save':
                case 'save changes':
                case 'save profile':
                    handleSave();
                    break;
                case 'test voice':
                case 'test settings':
                    testVoiceSettings();
                    break;
                case 'voice settings':
                case 'configure voice':
                    speakFeedback('Voice settings section. Say "Speed [number]", "Pitch [number]", or "Volume [number]" to adjust.');
                    break;
                case 'github settings':
                case 'setup github':
                    speakFeedback('GitHub settings. Say "GitHub username [name]" to set your username.');
                    break;
                case 'help':
                    showHelp();
                    break;
                default:
                    // Handle field-specific voice commands
                    handleFieldVoiceCommands(action);
                    break;
            }
        };

        window.addEventListener('voicePageAction', handleVoiceAction);
        return () => window.removeEventListener('voicePageAction', handleVoiceAction);
    }, [user, handleFieldVoiceCommands, handleSave, showHelp, speakFeedback]);

    const handleInputChange = (field, value) => {
        // When changed via UI, also prompt for confirmation
        setPendingChanges({ field, value, label: field });
        setConfirmationPending({ field, value, label: field });
        speakFeedback(`Do you want to change ${field}? Say yes to confirm or no to cancel.`);
    };

    const handleNestedInputChange = (section, field, value) => {
        // When changed via UI, also prompt for confirmation
        const fullField = `${section}.${field}`;
        setPendingChanges({ field: fullField, value, label: field });
        setConfirmationPending({ field: fullField, value, label: field });
        speakFeedback(`Do you want to change ${field}? Say yes to confirm or no to cancel.`);
    };

    const handleLanguageToggle = (language) => {
        const isAdding = !formData.preferredLanguages.includes(language);
        setPendingChanges({ 
            field: 'preferredLanguages', 
            value: isAdding 
                ? [...formData.preferredLanguages, language]
                : formData.preferredLanguages.filter(lang => lang !== language),
            label: `${language} ${isAdding ? 'to' : 'from'} preferred languages`
        });
        setConfirmationPending({ 
            field: 'preferredLanguages', 
            value: isAdding 
                ? [...formData.preferredLanguages, language]
                : formData.preferredLanguages.filter(lang => lang !== language),
            label: `${language} ${isAdding ? 'to' : 'from'} preferred languages`
        });
        speakFeedback(`Do you want to ${isAdding ? 'add' : 'remove'} ${language} ${isAdding ? 'to' : 'from'} preferred languages? Say yes to confirm or no to cancel.`);
    };

    const mapFormDataToBackend = (formData) => {
        return {
            full_name: formData.name,
            disability: formData.disability,
            can_type: formData.canType,
            preferred_input_method: formData.preferredInputMethod,
            typing_speed: formData.typingSpeed,
            additional_needs: formData.additionalNeeds,
            programming_experience: formData.programmingExperience,
            preferred_languages: formData.preferredLanguages,
            github_username: formData.githubSettings?.username,
            assistive_technologies: {
                screen_reader: formData.assistiveTechnologies?.screenReader || false,
                voice_control: formData.assistiveTechnologies?.voiceControl || false,
                switch_control: formData.assistiveTechnologies?.switchControl || false,
                other: formData.assistiveTechnologies?.other || ''
            }
        };
    };

    const testVoiceSettings = () => {
        const testMessage = "This is how your voice settings sound.";
        speakFeedback(testMessage);
    };

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Person color="primary" />
                Profile Settings
            </Typography>
            
            <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
                🎤 Voice Commands: "Name is [name]", "Speed 1.5", "Volume 0.8", "Save changes", "Yes/No" to confirm
            </Typography>

            {confirmationPending && (
                <Alert severity="info" sx={{ mb: 2 }}>
                    <Typography>
                        Pending change: {confirmationPending.label}
                    </Typography>
                    <Typography variant="body2">
                        Say "Yes" to confirm or "No" to cancel
                    </Typography>
                </Alert>
            )}

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
                {/* Personal Information */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                        <CardHeader 
                            title="Personal Information"
                            avatar={<Person />}
                        />
                        <CardContent>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                <TextField
                                    fullWidth
                                    label="Full Name"
                                    value={formData.name}
                                    onChange={(e) => handleInputChange('name', e.target.value)}
                                />
                                <TextField
                                    fullWidth
                                    label="Email"
                                    value={formData.email}
                                    onChange={(e) => handleInputChange('email', e.target.value)}
                                    type="email"
                                />
                                <FormControl fullWidth>
                                    <InputLabel>Programming Experience</InputLabel>
                                    <Select
                                        value={formData.programmingExperience}
                                        onChange={(e) => handleInputChange('programmingExperience', e.target.value)}
                                    >
                                        <MenuItem value="beginner">Beginner (0-1 years)</MenuItem>
                                        <MenuItem value="intermediate">Intermediate (2-5 years)</MenuItem>
                                        <MenuItem value="advanced">Advanced (5+ years)</MenuItem>
                                        <MenuItem value="expert">Expert (10+ years)</MenuItem>
                                    </Select>
                                </FormControl>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Voice Settings */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                        <CardHeader title="Voice Control Settings" avatar={<Mic />} />
                        <CardContent>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={formData.voiceSettings.enabled}
                                            onChange={(e) => handleNestedInputChange('voiceSettings', 'enabled', e.target.checked)}
                                        />
                                    }
                                    label="Enable Voice Control"
                                />
                                
                                <Typography gutterBottom>Voice Speed: {formData.voiceSettings.speed}</Typography>
                                <input
                                    type="range"
                                    min="0.5"
                                    max="2.0"
                                    step="0.1"
                                    value={formData.voiceSettings.speed}
                                    onChange={(e) => handleNestedInputChange('voiceSettings', 'speed', parseFloat(e.target.value))}
                                    style={{ width: '100%' }}
                                />
                                
                                <Typography gutterBottom>Voice Pitch: {formData.voiceSettings.pitch}</Typography>
                                <input
                                    type="range"
                                    min="0.5"
                                    max="2.0"
                                    step="0.1"
                                    value={formData.voiceSettings.pitch}
                                    onChange={(e) => handleNestedInputChange('voiceSettings', 'pitch', parseFloat(e.target.value))}
                                    style={{ width: '100%' }}
                                />
                                
                                <Typography gutterBottom>Volume: {formData.voiceSettings.volume}</Typography>
                                <input
                                    type="range"
                                    min="0.0"
                                    max="1.0"
                                    step="0.1"
                                    value={formData.voiceSettings.volume}
                                    onChange={(e) => handleNestedInputChange('voiceSettings', 'volume', parseFloat(e.target.value))}
                                    style={{ width: '100%' }}
                                />

                                <Button
                                    variant="outlined"
                                    startIcon={<VolumeUp />}
                                    onClick={testVoiceSettings}
                                    size="small"
                                >
                                    Test Voice
                                </Button>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* GitHub Integration */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                        <CardHeader title="GitHub Integration" avatar={<GitHub />} />
                        <CardContent>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                <TextField
                                    fullWidth
                                    label="GitHub Username"
                                    value={formData.githubSettings.username}
                                    onChange={(e) => handleNestedInputChange('githubSettings', 'username', e.target.value)}
                                />
                                <TextField
                                    fullWidth
                                    label="GitHub Personal Access Token"
                                    type="password"
                                    value={formData.githubSettings.token}
                                    onChange={(e) => handleNestedInputChange('githubSettings', 'token', e.target.value)}
                                    placeholder="ghp_..."
                                />
                                <FormControl fullWidth>
                                    <InputLabel>Default Repository Visibility</InputLabel>
                                    <Select
                                        value={formData.githubSettings.defaultVisibility}
                                        onChange={(e) => handleNestedInputChange('githubSettings', 'defaultVisibility', e.target.value)}
                                    >
                                        <MenuItem value="public">Public</MenuItem>
                                        <MenuItem value="private">Private</MenuItem>
                                    </Select>
                                </FormControl>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Accessibility Settings */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                        <CardHeader title="Accessibility Settings" avatar={<Accessibility />} />
                        <CardContent>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                <TextField
                                    fullWidth
                                    label="Disability (Optional)"
                                    value={formData.disability}
                                    onChange={(e) => handleInputChange('disability', e.target.value)}
                                    placeholder="e.g., Visual impairment, Motor disability"
                                />
                                
                                <FormControlLabel
                                    control={
                                        <Checkbox
                                            checked={formData.canType}
                                            onChange={(e) => handleInputChange('canType', e.target.checked)}
                                        />
                                    }
                                    label="Can type on keyboard"
                                />

                                <FormControl>
                                    <FormLabel>Assistive Technologies</FormLabel>
                                    <FormGroup>
                                        <FormControlLabel
                                            control={
                                                <Checkbox
                                                    checked={formData.assistiveTechnologies.screenReader}
                                                    onChange={(e) => handleNestedInputChange('assistiveTechnologies', 'screenReader', e.target.checked)}
                                                />
                                            }
                                            label="Screen Reader"
                                        />
                                        <FormControlLabel
                                            control={
                                                <Checkbox
                                                    checked={formData.assistiveTechnologies.voiceControl}
                                                    onChange={(e) => handleNestedInputChange('assistiveTechnologies', 'voiceControl', e.target.checked)}
                                                />
                                            }
                                            label="Voice Control"
                                        />
                                        <FormControlLabel
                                            control={
                                                <Checkbox
                                                    checked={formData.assistiveTechnologies.switchControl}
                                                    onChange={(e) => handleNestedInputChange('assistiveTechnologies', 'switchControl', e.target.checked)}
                                                />
                                            }
                                            label="Switch Control"
                                        />
                                    </FormGroup>
                                </FormControl>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Programming Preferences */}
                <Grid size={{ xs: 12 }}>
                    <Card>
                        <CardHeader title="Programming Preferences" avatar={<Code />} />
                        <CardContent>
                            <Typography variant="subtitle2" gutterBottom>
                                Preferred Programming Languages:
                            </Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                                {programmingLanguages.map((lang) => (
                                    <Chip
                                        key={lang}
                                        label={lang}
                                        onClick={() => handleLanguageToggle(lang)}
                                        color={formData.preferredLanguages.includes(lang) ? 'primary' : 'default'}
                                        variant={formData.preferredLanguages.includes(lang) ? 'filled' : 'outlined'}
                                    />
                                ))}
                            </Box>

                            <TextField
                                fullWidth
                                multiline
                                rows={3}
                                label="Additional Needs/Preferences"
                                value={formData.additionalNeeds}
                                onChange={(e) => handleInputChange('additionalNeeds', e.target.value)}
                                placeholder="Describe any specific needs or preferences for coding assistance..."
                            />
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2, mt: 3, justifyContent: 'center' }}>
                <Button
                    variant="contained"
                    startIcon={<Save />}
                    onClick={handleSave}
                    size="large"
                >
                    Save Changes
                </Button>
                
                <Button
                    variant="outlined"
                    startIcon={<Help />}
                    onClick={showHelp}
                    size="large"
                >
                    Voice Help
                </Button>
            </Box>

            {/* Voice Commands Reference */}
            <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>Voice Commands Reference:</Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label="🎤 Name is [your name]" variant="outlined" />
                    <Chip label="🎤 Email is [your email]" variant="outlined" />
                    <Chip label="🎤 Speed [0.5-2.0]" variant="outlined" />
                    <Chip label="🎤 Pitch [0.5-2.0]" variant="outlined" />
                    <Chip label="🎤 Volume [0.0-1.0]" variant="outlined" />
                    <Chip label="🎤 Enable/Disable voice control" variant="outlined" />
                    <Chip label="🎤 GitHub username [name]" variant="outlined" />
                    <Chip label="🎤 Beginner/Intermediate/Advanced/Expert" variant="outlined" />
                    <Chip label="🎤 Yes/No (to confirm changes)" variant="outlined" />
                    <Chip label="🎤 Save changes" variant="outlined" />
                    <Chip label="🎤 Scroll up/down/left/right" variant="outlined" />
                </Box>
            </Box>
        </Container>
    );
};

export default ProfilePage;