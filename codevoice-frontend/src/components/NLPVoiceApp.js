import React, { useState, useRef } from "react";
import MicInput from "./MicInput";
import axios from "axios";
import Editor from "@monaco-editor/react";

const NLPVoiceApp = () => {
  const [inputText, setInputText] = useState("");
  const editorRef = useRef(null);

  const handleTranscript = async (spokenText) => {
    setInputText(spokenText);
    try {
      const response = await axios.post("http://localhost:5001/api/parse", {
        text: spokenText,
      });

      const code = response.data.spaCy || "// No code generated.";
      if (editorRef.current) {
        editorRef.current.setValue(code);
      }

    } catch (error) {
      console.error("Error calling Flask API:", error);
      if (editorRef.current) {
        editorRef.current.setValue("// Something went wrong.");
      }
    }
  };

  const handleEditorDidMount = (editor) => {
    editorRef.current = editor;
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">🎤 Voice to Code Generator</h1>

      <MicInput onTranscript={handleTranscript} />

      <div className="mt-4">
        <p className="text-gray-600">Recognized Text:</p>
        <div className="bg-gray-100 p-3 rounded">{inputText}</div>
      </div>

      <div className="mt-6">
        <p className="text-gray-600">Generated Code:</p>
        <div style={{ height: "400px", border: "1px solid #ccc" }}>
          <Editor
            height="100%"
            defaultLanguage="javascript"
            defaultValue="// Code will appear here"
            onMount={handleEditorDidMount}
          />
        </div>
      </div>
    </div>
  );
};

export default NLPVoiceApp;
