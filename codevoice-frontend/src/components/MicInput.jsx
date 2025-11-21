import React, { useRef, useState } from "react";
import axios from "axios";

const MicInput = ({ transcript, setTranscript, manualPrompt, setManualPrompt }) => {
  const mediaRecorderRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);
  const audioChunks = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("file", audioBlob); // 'file' to match backend

        try {
          const response = await axios.post("http://localhost:5001/api/transcribe", formData);
          const text = response.data.transcript || "";
          setTranscript(text);
        } catch (error) {
          console.error("Transcription failed:", error);
          alert("Failed to transcribe audio.");
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Microphone access denied or not available:", error);
      alert("Microphone access denied or not available.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="w-full max-w-2xl bg-white p-4 rounded shadow mb-6">
      <div className="mb-4">
        {!isRecording ? (
          <button
            onClick={startRecording}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            🎤 Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="bg-red-600 text-white px-4 py-2 rounded"
          >
            ⏹️ Stop Recording
          </button>
        )}
      </div>

      <div className="mb-4">
        <label className="block font-medium mb-1">Transcript:</label>
        <textarea
          className="w-full p-2 border rounded"
          rows={3}
          value={transcript}
          readOnly
          placeholder="Transcript from mic will appear here..."
        />
      </div>

      <div>
        <label className="block font-medium mb-1">Or Enter Prompt Manually:</label>
        <textarea
          className="w-full p-2 border rounded"
          rows={3}
          value={manualPrompt}
          onChange={(e) => setManualPrompt(e.target.value)}
          placeholder="Type your prompt if mic does not work..."
        />
      </div>
    </div>
  );
};

export default MicInput;
