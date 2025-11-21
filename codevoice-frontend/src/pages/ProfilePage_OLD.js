import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    Container,
    Paper,
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
    Radio,
    RadioGroup,
    FormLabel,
    FormGroup
} from '@mui/material';

const ProfilePage = () => {
    const navigate = useNavigate();
    const { user, updateProfile } = useAuth();
    const [formData, setFormData] = useState({
        name: '',
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
        }
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        if (user) {
            setFormData(prevData => ({
                ...prevData,
                ...user
            }));
        }
    }, [user]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevData => ({
            ...prevData,
            [name]: value
        }));
    };

    const handleCheckboxChange = (e) => {
        const { name, checked } = e.target;
        if (name.startsWith('assistiveTechnologies.')) {
            const tech = name.split('.')[1];
            setFormData(prevData => ({
                ...prevData,
                assistiveTechnologies: {
                    ...prevData.assistiveTechnologies,
                    [tech]: checked
                }
            }));
        } else {
            setFormData(prevData => ({
                ...prevData,
                [name]: checked
            }));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await updateProfile(user.id, formData);
            setSuccess('Profile updated successfully');
            setError('');
        } catch (err) {
            setError(err.message);
            setSuccess('');
        }
    };

    if (!user) {
        navigate('/login');
        return null;
    }

    return (
        <Container maxWidth="md">
            <Box sx={{ mt: 8, mb: 4 }}>
                <Paper elevation={3} sx={{ p: 4 }}>
                    <Typography variant="h4" component="h1" gutterBottom align="center">
                        Profile Settings
                    </Typography>
                    
                    {error && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {error}
                        </Alert>
                    )}
                    
                    {success && (
                        <Alert severity="success" sx={{ mb: 2 }}>
                            {success}
                        </Alert>
                    )}

                    <form onSubmit={handleSubmit}>
                        <TextField
                            fullWidth
                            label="Full Name"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            margin="normal"
                            required
                        />

                        <FormControl fullWidth margin="normal">
                            <InputLabel>Type of Motor Disability</InputLabel>
                            <Select
                                name="disability"
                                value={formData.disability}
                                onChange={handleChange}
                                required
                            >
                                <MenuItem value="hand-mobility">Limited Hand Mobility</MenuItem>
                                <MenuItem value="upper-limb">Upper Limb Disability</MenuItem>
                                <MenuItem value="fine-motor">Fine Motor Control Issues</MenuItem>
                                <MenuItem value="other">Other</MenuItem>
                            </Select>
                        </FormControl>

                        <FormControlLabel
                            control={
                                <Checkbox
                                    checked={formData.canType}
                                    onChange={handleCheckboxChange}
                                    name="canType"
                                />
                            }
                            label="Can you type on a keyboard?"
                            sx={{ mt: 2 }}
                        />

                        <FormControl component="fieldset" sx={{ mt: 2 }}>
                            <FormLabel component="legend">Preferred Input Method</FormLabel>
                            <RadioGroup
                                name="preferredInputMethod"
                                value={formData.preferredInputMethod}
                                onChange={handleChange}
                            >
                                <FormControlLabel value="voice" control={<Radio />} label="Voice Commands" />
                                <FormControlLabel value="keyboard" control={<Radio />} label="Keyboard" />
                                <FormControlLabel value="switch" control={<Radio />} label="Switch Device" />
                                <FormControlLabel value="other" control={<Radio />} label="Other" />
                            </RadioGroup>
                        </FormControl>

                        {formData.canType && (
                            <FormControl fullWidth margin="normal">
                                <InputLabel>Typing Speed</InputLabel>
                                <Select
                                    name="typingSpeed"
                                    value={formData.typingSpeed}
                                    onChange={handleChange}
                                >
                                    <MenuItem value="very-slow">Very Slow</MenuItem>
                                    <MenuItem value="slow">Slow</MenuItem>
                                    <MenuItem value="moderate">Moderate</MenuItem>
                                    <MenuItem value="normal">Normal</MenuItem>
                                </Select>
                            </FormControl>
                        )}

                        <FormControl fullWidth component="fieldset" sx={{ mt: 2 }}>
                            <FormLabel component="legend">Assistive Technologies Used</FormLabel>
                            <FormGroup>
                                <FormControlLabel
                                    control={
                                        <Checkbox
                                            checked={formData.assistiveTechnologies.screenReader}
                                            onChange={handleCheckboxChange}
                                            name="assistiveTechnologies.screenReader"
                                        />
                                    }
                                    label="Screen Reader"
                                />
                                <FormControlLabel
                                    control={
                                        <Checkbox
                                            checked={formData.assistiveTechnologies.voiceControl}
                                            onChange={handleCheckboxChange}
                                            name="assistiveTechnologies.voiceControl"
                                        />
                                    }
                                    label="Voice Control"
                                />
                                <FormControlLabel
                                    control={
                                        <Checkbox
                                            checked={formData.assistiveTechnologies.switchControl}
                                            onChange={handleCheckboxChange}
                                            name="assistiveTechnologies.switchControl"
                                        />
                                    }
                                    label="Switch Control"
                                />
                            </FormGroup>
                        </FormControl>

                        <TextField
                            fullWidth
                            label="Additional Needs or Preferences"
                            name="additionalNeeds"
                            value={formData.additionalNeeds}
                            onChange={handleChange}
                            margin="normal"
                            multiline
                            rows={4}
                        />

                        <FormControl fullWidth margin="normal">
                            <InputLabel>Programming Experience</InputLabel>
                            <Select
                                name="programmingExperience"
                                value={formData.programmingExperience}
                                onChange={handleChange}
                            >
                                <MenuItem value="beginner">Beginner</MenuItem>
                                <MenuItem value="intermediate">Intermediate</MenuItem>
                                <MenuItem value="advanced">Advanced</MenuItem>
                                <MenuItem value="professional">Professional</MenuItem>
                            </Select>
                        </FormControl>

                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            color="primary"
                            sx={{ mt: 3 }}
                        >
                            Save Profile
                        </Button>
                    </form>
                </Paper>
            </Box>
        </Container>
    );
};

export default ProfilePage;