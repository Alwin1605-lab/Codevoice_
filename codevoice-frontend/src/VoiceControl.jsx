// eslint-disable-next-line no-unused-vars
import React, { useEffect, useRef, useState, useCallback } from "react";
import apiService from './services/apiService';
import { userService } from './services/userService';

const VoiceControl = ({
  isRecording,
  onTranscriptChange,
  onStartRecording,
  onStopRecording,
  onGenerateCode,
  onCompileCode,
  onSaveCode,
  onCopyCode,
}) => {
  const recognitionRef = useRef(null);
  const listeningRef = useRef(false);
  const [currentUser, setCurrentUser] = useState(null);

  // Load current user on component mount
  useEffect(() => {
    const user = userService.getCurrentUser();
    setCurrentUser(user);
  }, []);

  // Function to save voice command to database
  const saveVoiceCommand = async (commandText, commandType, executionSuccessful = true, responseText = null) => {
    try {
      // Only save if user is logged in
      if (!currentUser || !currentUser.id) {
        console.log('User not logged in, skipping voice command save');
        return;
      }

      await apiService.saveVoiceCommandDB({
        user_id: currentUser.id,
        command_text: commandText,
        command_type: commandType,
        language: "en",
        confidence_score: 0.95, // We don't have actual confidence from webkitSpeechRecognition
        execution_successful: executionSuccessful,
        response_text: responseText,
        execution_time_ms: Date.now() % 1000 // Simple execution time approximation
      });
    } catch (error) {
      console.warn('Failed to save voice command:', error);
    }
  };

  useEffect(() => {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Speech Recognition not supported");
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let transcriptText = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        transcriptText += event.results[i][0].transcript.trim() + " ";
      }

      transcriptText = transcriptText.toLowerCase().trim();
      console.log("Heard:", transcriptText);

      // Commands detection with database saving
      if (transcriptText.includes("start recording")) {
        console.log("Command: Start Recording");
        onStartRecording();
        listeningRef.current = true;
        saveVoiceCommand(transcriptText, "start_recording", true, "Recording started");
      }

      if (transcriptText.includes("stop recording")) {
        console.log("Command: Stop Recording");
        listeningRef.current = false;
        onStopRecording();
        saveVoiceCommand(transcriptText, "stop_recording", true, "Recording stopped");
        // Do not return here; allow transcript to be appended if isRecording is true
      }

      if (transcriptText.includes("generate code")) {
        console.log("Command: Generate Code");
        onGenerateCode();
        saveVoiceCommand(transcriptText, "generate_code", true, "Code generation initiated");
      }

      if (transcriptText.includes("compile")) {
        console.log("Command: Compile Code");
        onCompileCode();
        saveVoiceCommand(transcriptText, "compile_code", true, "Code compilation initiated");
      }

      if (transcriptText.includes("save")) {
        console.log("Command: Save Code");
        onSaveCode();
        saveVoiceCommand(transcriptText, "save_code", true, "Code saved");
      }

      if (transcriptText.includes("copy")) {
        console.log("Command: Copy Code");
        if (onCopyCode) onCopyCode();
        saveVoiceCommand(transcriptText, "copy_code", true, "Code copied to clipboard");
      }

      // Append transcript only if recording is active
      if (isRecording && listeningRef.current) {
        onTranscriptChange((prev) => (prev ? prev + " " + transcriptText : transcriptText));
      }
    };

    recognition.onerror = (e) => {
      console.error("Speech recognition error", e);
    };

    recognition.onend = () => {
      console.log("Speech recognition ended, restarting...");
      if (listeningRef.current) {
        recognition.start();
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
    listeningRef.current = isRecording;

    return () => {
      listeningRef.current = false;
      recognition.stop();
    };
  }, [isRecording]);

  return null; // UI is handled in App.jsx
};

export default VoiceControl;
