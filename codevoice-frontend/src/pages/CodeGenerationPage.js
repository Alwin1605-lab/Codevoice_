import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Box, Paper, Typography, Button, Select, MenuItem, FormControl, InputLabel, TextField, CircularProgress, Chip
} from '@mui/material';
import { Code, Mic, PlayArrow, Save, ContentCopy, Clear as ClearIcon, Speed, BugReport, MenuBook, TrendingUp, ErrorOutline } from '@mui/icons-material';
import { Editor } from '@monaco-editor/react';
import apiService from '../services/apiService';
import { useVoiceControl } from '../context/VoiceControlContext';
import TRANSCRIPTION_LANGUAGES from '../constants/transcriptionLanguages';

const CodeGenerationPage = () => {
  const navigate = useNavigate();
  const { speakFeedback } = useVoiceControl();
  const [transcript, setTranscript] = useState('');
  const [manualPrompt, setManualPrompt] = useState('');
  const [generatedCode, setGeneratedCode] = useState('');
  const [compileOutput, setCompileOutput] = useState('');
  const [userInput, setUserInput] = useState('');
  const [micLoading, setMicLoading] = useState(false);
  const [generateLoading, setGenerateLoading] = useState(false);
  const [compileLoading, setCompileLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [language, setLanguage] = useState('python');
  const [languages, setLanguages] = useState(['python','javascript','java','cpp','c']);
  const [modelPreset, setModelPreset] = useState('balanced');
  const [usedModel, setUsedModel] = useState(null);
  const [transcriptionLanguage, setTranscriptionLanguage] = useState('en');
  const [nativeTranscript, setNativeTranscript] = useState('');

  // refs removed to avoid unused var warnings
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    speakFeedback('Code Generation page loaded. You can say "generate code", "compile", "optimize", "debug", "save", or "copy".');
    // Load available languages from backend (Judge0 info) with graceful fallback
    (async () => {
      try {
        const info = await apiService.getAvailableLanguages();
        let langs = [];
        if (Array.isArray(info)) {
          langs = info;
        } else if (info && Array.isArray(info.supported_languages)) {
          langs = info.supported_languages;
        } else if (info && info.languages && Array.isArray(info.languages)) {
          langs = info.languages;
        }
        // Normalize common ids
        langs = langs.map(l => (typeof l === 'string' ? l.toLowerCase() : (l.id || l.name || '').toLowerCase())).filter(Boolean);
        // Ensure a useful default set if empty
        if (!langs.length) langs = ['python','javascript','typescript','java','cpp','c','go','rust','php','ruby'];
        setLanguages(Array.from(new Set(langs)));
      } catch (e) {
        setLanguages(['python','javascript','typescript','java','cpp','c','go','rust','php','ruby']);
      }
    })();
    
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
        case 'generate':
        case 'generate code':
          run(handleGenerateCode);
          break;
        case 'compile':
        case 'run':
          run(handleCompile);
          break;
        case 'optimize':
        case 'optimize code':
          run(handleOptimizeCode);
          break;
        case 'debug':
        case 'debug code':
          run(handleDebugCode);
          break;
        case 'explain':
        case 'explain code':
          run(handleExplainCode);
          break;
        case 'improve':
        case 'improve code':
          run(handleImproveCode);
          break;
        case 'analyze error':
          run(handleAnalyzeError);
          break;
        case 'save':
          run(handleSaveFile);
          break;
        case 'copy':
          run(handleCopyCode);
          break;
        case 'clear':
          run(clearAll);
          break;
        case 'start recording':
          run(startRecording);
          break;
        case 'stop recording':
          run(stopRecording);
          break;
        case 'help':
          showHelp();
          handled = true;
          detail.suppressAutoFeedback = true;
          break;
        default:
          const voiceMap = [
            ['c plus plus','cpp'],
            ['c++','cpp'],
            ['typescript','typescript'],
            ['python','python'],
            ['javascript','javascript'],
            ['java','java'],
            ['go','go'],
            ['golang','go'],
            ['rust','rust'],
            ['php','php'],
            ['ruby','ruby'],
            ['c sharp','csharp'],
            ['c#','csharp'],
            ['c','c']
          ];
          for (const [key, val] of voiceMap) {
            if (action.includes(key) && languages.includes(val)) {
              setLanguage(val);
              handled = true;
              detail.feedback = `Language set to ${val.toUpperCase()}`;
              break;
            }
          }
          break;
      }

      if (handled) {
        detail.handled = true;
      }
    };

    window.addEventListener('voicePageAction', handleVoiceAction);
    return () => window.removeEventListener('voicePageAction', handleVoiceAction);
  }, []);

  const speak = (text) => {
    speakFeedback(text);
  };

  const showHelp = () => {
    const helpText = `Code Generation voice commands:
    Say "Generate code" to generate code from your prompt
    Say "Compile" or "Run" to compile and run the code with AI
    Say "Optimize" to optimize your code with AI
    Say "Debug" to analyze your code for bugs
    Say "Explain" to get detailed code explanation
    Say "Improve" to get improvement suggestions
    Say "Analyze error" to analyze compilation errors
    Say "Save" to save the generated code
    Say "Copy" to copy code to clipboard
    Say "Clear" to clear all content
    Say "Python", "JavaScript", "Java", "C++", or "C" to switch languages`;
    speak(helpText);
  };

  const clearAll = () => {
    setTranscript('');
    setManualPrompt('');
    setGeneratedCode('');
    setCompileOutput('');
    setUserInput('');
    speak('All content cleared');
  };

  const handleCopyCode = () => {
    if (generatedCode) {
      navigator.clipboard.writeText(generatedCode);
      speak('Code copied to clipboard');
    } else {
      speak('No code to copy');
    }
  };

  const startRecording = async () => {
    if (recording) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await handleTranscribe(audioBlob);
      };

      mediaRecorder.start();
      setRecording(true);
      speak('Recording started');
    } catch (err) {
      setTranscript('Microphone access denied or not available');
    }
  };

  const stopRecording = () => {
    if (recording && mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const handleTranscribe = async (audioBlob) => {
    setMicLoading(true);
    try {
      const res = await apiService.transcribeAudio(audioBlob, transcriptionLanguage);
      const englishText = (res && (res.transcript || res.translation || res.translated_text)) || '';
      const nativeText = (res && (res.transcript_native || res.native_transcript)) || englishText;

      if (englishText) {
        setTranscript((prev) => (prev ? `${prev} ${englishText}`.trim() : englishText));
        setNativeTranscript((prev) => (prev ? `${prev}\n${nativeText}`.trim() : nativeText));
        speak(`Transcription added in ${transcriptionLanguage === 'en' ? 'English' : 'native language with English translation.'}`);
      } else if (res && res.error) {
        setTranscript('❌ ' + res.error);
        speak('Error transcribing audio.');
      } else {
        setTranscript('❌ No transcript received.');
        speak('No transcript received.');
      }
    } catch (err) {
      console.error(err);
      setTranscript('❌ Error transcribing audio.');
      speak('Error transcribing audio.');
    }
    setMicLoading(false);
  };

  const handleGenerateCode = async () => {
    const promptToSend = transcript.trim() || manualPrompt.trim();
    if (!promptToSend) {
      speak('Please provide a prompt first');
      return;
    }
    setGenerateLoading(true);
    speak('Generating code...');
    try {
      // Map preset to an optional model hint for backend
      let preferredModel = null;
      if (modelPreset === 'fast') preferredModel = 'llama-3.1-8b-instant';
      if (modelPreset === 'accurate') preferredModel = 'llama-3.3-70b-versatile';

      const res = await apiService.generateCode(promptToSend, language, preferredModel);
      setGeneratedCode(res.code || '// No code generated');
      if (res.model) setUsedModel(res.model);
      speak('Code generated successfully.');
    } catch (err) {
      console.error(err);
      setGeneratedCode('// Error generating code');
      speak('Error generating code.');
    }
    setGenerateLoading(false);
  };

  const handleCompile = async () => {
    if (!generatedCode) {
      speak('No code to compile');
      return;
    }
    setCompileLoading(true);
    speak('Compiling with AI intelligence...');
    try {
      // Use Codex AI for intelligent compilation
      const res = await apiService.compileWithCodex(generatedCode, language, 'compile_and_run', userInput);
      
      let output = '';
      if (res.success) {
        output = `✅ Compilation Successful!\n\n`;
        
        if (res.execution_result && res.execution_result.stdout) {
          output += `📤 Output:\n${res.execution_result.stdout}\n\n`;
        }
        
        if (res.execution_result && res.execution_result.stderr) {
          output += `⚠️ Warnings/Errors:\n${res.execution_result.stderr}\n\n`;
        }
        
        if (res.ai_explanation) {
          output += `🤖 AI Analysis:\n${res.ai_explanation}\n\n`;
        }
        
        if (res.optimization_suggestions && res.optimization_suggestions.length > 0) {
          output += `💡 Optimization Suggestions:\n${res.optimization_suggestions.join('\n')}\n\n`;
        }
        
        speak('Code compiled successfully with AI analysis');
      } else {
        // Auto fallback to basic compile when Codex fails (quota, etc.)
        speak('AI compilation failed, falling back to basic compiler...');
        const basic = await apiService.compileCode(generatedCode, language, userInput);
        const basicOut = basic.stdout || basic.stderr || basic.compile_output || '';
        output = `🔧 Basic Compilation Result (fallback):\n${basicOut}`;
      }
      
      setCompileOutput(output);
    } catch (err) {
      console.error(err);
      // Fallback to basic compilation
      try {
        speak('AI compilation failed, using basic compiler...');
        const res = await apiService.compileCode(generatedCode, language, userInput);
        const output = res.stdout || res.stderr || res.compile_output || '// No output received';
        setCompileOutput(`🔧 Basic Compilation Result:\n${output}`);
        speak('Basic compilation completed.');
      } catch (fallbackErr) {
        console.error(fallbackErr);
        setCompileOutput('// Error: Both AI and basic compilation failed');
        speak('Error: All compilation methods failed.');
      }
    }
    setCompileLoading(false);
  };

  // New AI-powered code optimization function
  const handleOptimizeCode = async () => {
    if (!generatedCode) {
      speak('No code to optimize');
      return;
    }
    setGenerateLoading(true);
    speak('Optimizing code with AI...');
    try {
      const res = await apiService.optimizeCodeWithCodex(generatedCode, language, ['performance', 'readability']);
      
      if (res.success && res.optimized_code) {
        setGeneratedCode(res.optimized_code);
        
        let feedback = 'Code optimized successfully.';
        if (res.improvements_made && res.improvements_made.length > 0) {
          feedback += ` Improvements: ${res.improvements_made.join(', ')}`;
        }
        speak(feedback);
        
        // Show optimization details in output
        let output = `🚀 Code Optimization Results:\n\n`;
        output += `✨ Improvements Made:\n${res.improvements_made.join('\n')}\n\n`;
        if (res.performance_impact) {
          output += `📊 Performance Impact: ${res.performance_impact}\n\n`;
        }
        if (res.explanation) {
          output += `🤖 AI Explanation:\n${res.explanation}`;
        }
        setCompileOutput(output);
      } else {
        speak('No optimizations found or optimization failed');
        setCompileOutput('🔍 No optimizations found for this code.');
      }
    } catch (err) {
      console.error(err);
      speak('Error optimizing code');
      setCompileOutput('❌ Error during code optimization');
    }
    setGenerateLoading(false);
  };

  // New AI-powered code debugging function
  const handleDebugCode = async () => {
    if (!generatedCode) {
      speak('No code to debug');
      return;
    }
    setGenerateLoading(true);
    speak('Analyzing code for bugs with AI...');
    try {
      const res = await apiService.debugCodeWithCodex(generatedCode, language);
      
      if (res.success) {
        let output = `🐛 AI Code Analysis Results:\n\n`;
        
        if (res.issues_found && res.issues_found.length > 0) {
          output += `⚠️ Issues Found:\n${res.issues_found.map(issue => `• ${issue}`).join('\n')}\n\n`;
        } else {
          output += `✅ No major issues found!\n\n`;
        }
        
        if (res.suggestions && res.suggestions.length > 0) {
          output += `💡 Suggestions:\n${res.suggestions.map(suggestion => `• ${suggestion}`).join('\n')}\n\n`;
        }
        
        if (res.fixed_code && res.fixed_code !== generatedCode) {
          output += `🔧 AI has suggestions for fixes. Would you like to apply them?\n\n`;
          output += `Fixed Code Preview:\n${res.fixed_code.substring(0, 200)}...`;
        }
        
        if (res.explanation) {
          output += `\n\n🤖 Detailed Analysis:\n${res.explanation}`;
        }
        
        setCompileOutput(output);
        speak('Code analysis completed. Check the output for details.');
      } else {
        speak('Debug analysis failed');
        setCompileOutput('❌ Error during code analysis');
      }
    } catch (err) {
      console.error(err);
      speak('Error analyzing code');
      setCompileOutput('❌ Error during code debugging');
    }
    setGenerateLoading(false);
  };

  // New Groq AI-powered code explanation function
  const handleExplainCode = () => {
    if (!generatedCode) {
      speak('No code to explain');
      return;
    }
    // Route to Learning Mode with prefilled code and desired action
    navigate('/learning-mode', { state: { code: generatedCode, action: 'explain' } });
    speak('Opening Learning Mode for explanation');
  };

  // New Groq AI-powered code improvement function
  const handleImproveCode = () => {
    if (!generatedCode) {
      speak('No code to improve');
      return;
    }
    navigate('/learning-mode', { state: { code: generatedCode, action: 'improve' } });
    speak('Opening Learning Mode for improvement suggestions');
  };

  // New Groq AI-powered error analysis function
  const handleAnalyzeError = async () => {
    if (!compileOutput || !compileOutput.includes('Error')) {
      speak('No compilation errors to analyze. Try compiling your code first.');
      return;
    }
    setGenerateLoading(true);
    speak('Analyzing compilation errors with AI...');
    try {
      // Extract error message from compile output
      const errorMessage = compileOutput.split('Error:')[1]?.trim() || 'Unknown error';
      
      const res = await apiService.analyzeErrorWithGroq(generatedCode, language, errorMessage, 'intermediate', true);
      
      if (res.success) {
        let output = `🔍 AI Error Analysis:\n\n`;
        
        output += `❌ Original Error: ${errorMessage}\n\n`;
        
        if (res.error_explanation) {
          output += `🤖 Error Explanation:\n${res.error_explanation}\n\n`;
        }
        
        if (res.possible_causes && res.possible_causes.length > 0) {
          output += `🔎 Possible Causes:\n${res.possible_causes.map(cause => `• ${cause}`).join('\n')}\n\n`;
        }
        
        if (res.fix_suggestions && res.fix_suggestions.length > 0) {
          output += `🔧 Fix Suggestions:\n${res.fix_suggestions.map(fix => `• ${fix}`).join('\n')}\n\n`;
        }
        
        if (res.fixed_code && res.fixed_code !== generatedCode) {
          output += `✅ Suggested Fixed Code:\n\`\`\`${language}\n${res.fixed_code}\n\`\`\`\n\n`;
          output += `💭 Note: Review and apply the suggested fixes to your code.`;
        }
        
        if (res.prevention_tips && res.prevention_tips.length > 0) {
          output += `\n\n🛡️ Prevention Tips:\n${res.prevention_tips.map(tip => `• ${tip}`).join('\n')}`;
        }
        
        setCompileOutput(output);
        speak('Error analysis completed. Check the detailed fix suggestions in the output.');
      } else {
        speak('Error analysis failed');
        setCompileOutput('❌ Error during error analysis');
      }
    } catch (err) {
      console.error(err);
      speak('Error analyzing compilation errors');
      setCompileOutput('❌ Error during error analysis');
    }
    setGenerateLoading(false);
  };

  const handleSaveFile = () => {
    if (!generatedCode) {
      speak('No code to save');
      return;
    }
    
    const blob = new Blob([generatedCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `code.${getFileExtension(language)}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    speak('Code saved to file');
  };

  const getFileExtension = (lang) => {
    const extensions = {
      'python': 'py',
      'javascript': 'js',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c'
    };
    return extensions[lang] || 'txt';
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Header */}
        <Paper elevation={3} sx={{ p: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
          <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Code /> AI-Powered Code Generation
          </Typography>
          <Typography variant="body1">
            Generate, compile, optimize, and debug code using voice commands or text input with AI intelligence
          </Typography>
        </Paper>

        {/* Voice Commands Guide */}
        <Paper elevation={2} sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.06)' }}>
          <Typography variant="h6" sx={{ mb: 1, color: 'rgba(255,255,255,0.85)' }}>Voice Commands:</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {['Generate code','Compile','Optimize','Debug','Explain','Improve','Analyze error','Save','Copy','Help'].map((t, i) => (
              <Chip key={i} label={`🎤 ${t}`} variant="outlined" sx={{
                color: 'rgba(255,255,255,0.9)',
                borderColor: 'rgba(255,255,255,0.3)',
                bgcolor: 'rgba(255,255,255,0.04)'
              }} />
            ))}
          </Box>
        </Paper>

        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          {/* Input Section */}
          <Box sx={{ flex: 1, minWidth: '300px' }}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>Input & Configuration</Typography>
              
              {/* Language Selection */}
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Programming Language</InputLabel>
                <Select value={language} onChange={(e) => setLanguage(e.target.value)}>
                  {languages.map((lang) => (
                    <MenuItem key={lang} value={lang}>{lang.toUpperCase()}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Model Preset Selection */}
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Model Preset</InputLabel>
                <Select value={modelPreset} onChange={(e) => setModelPreset(e.target.value)}>
                  <MenuItem value="fast">Fast (small, cheaper)</MenuItem>
                  <MenuItem value="balanced">Balanced</MenuItem>
                  <MenuItem value="accurate">Accurate (larger model)</MenuItem>
                </Select>
              </FormControl>

              {/* Voice Input */}
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 1, flexWrap: 'wrap' }}>
                  <Typography variant="subtitle1">Voice Input:</Typography>
                  <FormControl size="small" sx={{ minWidth: 180 }}>
                    <InputLabel>Speech Language</InputLabel>
                    <Select
                      value={transcriptionLanguage}
                      label="Speech Language"
                      onChange={(e) => {
                        setTranscriptionLanguage(e.target.value);
                        setNativeTranscript('');
                      }}
                    >
                      {TRANSCRIPTION_LANGUAGES.map((lang) => (
                        <MenuItem key={lang.code} value={lang.code}>{lang.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Box>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  value={transcript}
                  onChange={(e) => setTranscript(e.target.value)}
                  placeholder="English (translated) transcript for AI prompt"
                  variant="outlined"
                />
                {transcriptionLanguage !== 'en' && (
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    value={nativeTranscript}
                    onChange={(e) => setNativeTranscript(e.target.value)}
                    placeholder="Original transcript in your language"
                    variant="outlined"
                    sx={{ mt: 2 }}
                  />
                )}
                <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                  <Button
                    variant={recording ? "contained" : "outlined"}
                    color={recording ? "error" : "primary"}
                    startIcon={recording ? <CircularProgress size={20} /> : <Mic />}
                    onClick={recording ? stopRecording : startRecording}
                    disabled={micLoading}
                  >
                    {recording ? 'Stop Recording' : 'Start Recording'}
                  </Button>
                </Box>
              </Box>

              {/* Manual Prompt */}
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" sx={{ mb: 1 }}>Manual Prompt:</Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  value={manualPrompt}
                  onChange={(e) => setManualPrompt(e.target.value)}
                  placeholder="Type your code generation prompt here..."
                  variant="outlined"
                />
              </Box>

              {/* User Input for Code Execution */}
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" sx={{ mb: 1 }}>Input for Code Execution:</Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  placeholder="Enter input data for your code (if needed)..."
                  variant="outlined"
                />
              </Box>

              {/* Action Buttons */}
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Button
                  variant="contained"
                  startIcon={generateLoading ? <CircularProgress size={20} /> : <Code />}
                  onClick={handleGenerateCode}
                  disabled={generateLoading}
                >
                  Generate Code
                </Button>
                <Button
                  variant="contained"
                  color="success"
                  startIcon={compileLoading ? <CircularProgress size={20} /> : <PlayArrow />}
                  onClick={handleCompile}
                  disabled={compileLoading}
                >
                  AI Compile & Run
                </Button>
                <Button
                  variant="contained"
                  color="warning"
                  startIcon={generateLoading ? <CircularProgress size={20} /> : <Speed />}
                  onClick={handleOptimizeCode}
                  disabled={generateLoading}
                >
                  Optimize
                </Button>
                <Button
                  variant="contained"
                  color="error"
                  startIcon={generateLoading ? <CircularProgress size={20} /> : <BugReport />}
                  onClick={handleDebugCode}
                  disabled={generateLoading}
                >
                  Debug
                </Button>
                <Button
                  variant="contained"
                  color="info"
                  startIcon={generateLoading ? <CircularProgress size={20} /> : <MenuBook />}
                  onClick={handleExplainCode}
                  disabled={generateLoading}
                >
                  Explain
                </Button>
                <Button
                  variant="contained"
                  color="secondary"
                  startIcon={generateLoading ? <CircularProgress size={20} /> : <TrendingUp />}
                  onClick={handleImproveCode}
                  disabled={generateLoading}
                >
                  Improve
                </Button>
                <Button
                  variant="contained"
                  sx={{ bgcolor: '#ff6b35', '&:hover': { bgcolor: '#e55a2e' } }}
                  startIcon={generateLoading ? <CircularProgress size={20} /> : <ErrorOutline />}
                  onClick={handleAnalyzeError}
                  disabled={generateLoading}
                >
                  Analyze Error
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Save />}
                  onClick={handleSaveFile}
                >
                  Save
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<ContentCopy />}
                  onClick={handleCopyCode}
                >
                  Copy
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<ClearIcon />}
                  onClick={clearAll}
                >
                  Clear
                </Button>
              </Box>
            </Paper>
          </Box>

          {/* Code Editor */}
          <Box sx={{ flex: 1, minWidth: '400px' }}>
            <Paper elevation={2} sx={{ p: 3, height: 'fit-content' }}>
              <Typography variant="h6" sx={{ mb: 2 }}>Generated Code</Typography>
              {usedModel && (
                <Typography variant="caption" sx={{ mb: 1, display: 'block' }}>Generated with model: {usedModel}</Typography>
              )}
              <Box sx={{ border: '1px solid #ddd', borderRadius: 1, overflow: 'hidden' }}>
                <Editor
                  height="400px"
                  language={language === 'cpp' ? 'cpp' : language}
                  value={generatedCode || '// Generated code will appear here...'}
                  onChange={(value) => setGeneratedCode(value || '')}
                  theme="vs-dark"
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: 'on',
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                  }}
                />
              </Box>
            </Paper>
          </Box>
        </Box>

        {/* Output Section */}
        {compileOutput && (
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>AI Analysis & Output</Typography>
            <Box sx={{ 
              bgcolor: 'rgba(0,0,0,0.6)', 
              color: 'rgba(255,255,255,0.9)',
              p: 2, 
              borderRadius: 1, 
              fontFamily: 'monospace', 
              whiteSpace: 'pre-wrap',
              maxHeight: '300px',
              overflow: 'auto',
              border: '1px solid rgba(255,255,255,0.12)'
            }}>
              {compileOutput}
            </Box>
          </Paper>
        )}


      </Box>
    </Container>
  );
};

export default CodeGenerationPage;