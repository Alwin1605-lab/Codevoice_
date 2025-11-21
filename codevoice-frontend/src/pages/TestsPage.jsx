import React, { useState } from 'react';
import { Box, Container, Paper, Typography, TextField, Button, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { useVoiceControl } from '../context/VoiceControlContext';
import apiService from '../services/apiService';

const sampleTests = {
  javascript: `// Add two numbers\nfunction add(a, b){ return a + b; }\nconsole.log(add(2, 3)); // 5`,
  python: `# Add two numbers\ndef add(a, b):\n    return a + b\n\nprint(add(2, 3))  # 5`,
};

const TestsPage = () => {
  const { speakFeedback } = useVoiceControl();
  const [language, setLanguage] = useState('javascript');
  const [code, setCode] = useState(sampleTests.javascript);
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [running, setRunning] = useState(false);

  const runTest = async () => {
    setRunning(true);
    setOutput('');
    speakFeedback('Running test');
    try {
      const result = await apiService.compileCode(code, language, input);
      let out = '';
      if (result.compile_output) out += `Compile Output:\n${result.compile_output}\n\n`;
      if (result.stdout) out += `Output:\n${result.stdout}\n`;
      if (result.stderr) out += `Errors:\n${result.stderr}\n`;
      if (!out.trim()) out = 'No output';
      setOutput(out);
    } catch (e) {
      setOutput(`Failed: ${e.message || 'Unknown error'}`);
    }
    setRunning(false);
  };

  const onLangChange = (val) => {
    setLanguage(val);
    setCode(sampleTests[val] || '');
    speakFeedback(`Language set to ${val}`);
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>Practice Tests</Typography>
        <Paper sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <FormControl size="small">
              <InputLabel>Language</InputLabel>
              <Select value={language} label="Language" onChange={(e) => onLangChange(e.target.value)}>
                <MenuItem value="javascript">JavaScript</MenuItem>
                <MenuItem value="python">Python</MenuItem>
                <MenuItem value="java">Java</MenuItem>
                <MenuItem value="cpp">C++</MenuItem>
              </Select>
            </FormControl>
            <Button variant="contained" onClick={runTest} disabled={running}>
              {running ? 'Running…' : 'Run'}
            </Button>
          </Box>

          <Typography variant="subtitle2">Code</Typography>
          <TextField multiline minRows={8} fullWidth value={code} onChange={(e) => setCode(e.target.value)} sx={{ mb: 2 }} />

          <Typography variant="subtitle2">Input (optional)</Typography>
          <TextField multiline minRows={3} fullWidth value={input} onChange={(e) => setInput(e.target.value)} sx={{ mb: 2 }} />

          <Typography variant="subtitle2">Output</Typography>
          <Paper variant="outlined" sx={{ p: 1, whiteSpace: 'pre-wrap', fontFamily: 'monospace', minHeight: 120 }}>
            {output || 'No output yet'}
          </Paper>
        </Paper>
      </Box>
    </Container>
  );
};

export default TestsPage;
