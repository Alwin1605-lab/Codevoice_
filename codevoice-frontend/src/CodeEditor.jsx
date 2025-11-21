import React from "react";
import axios from "axios";

function CodeEditor({
  transcript,
  manualPrompt,
  generatedCode,
  setGeneratedCode,
  handleCompile,
  handleSaveFile,
  compileOutput,
}) {
  // Generate code inside the editor
  const handleGenerateCode = async () => {
    const text = transcript || manualPrompt;
    if (!text.trim()) return;

    try {
      const res = await axios.post("http://localhost:5000/api/generate-code", {
        prompt: text, // ✅ fixed key
      });
      setGeneratedCode(res.data.code || "No code generated.");
    } catch (err) {
      console.error("Code generation failed:", err);
      setGeneratedCode("❌ Error generating code.");
    }
  };

  // Compile code inside the editor
  const handleCompileCode = async () => {
    try {
      const res = await axios.post("http://localhost:5000/api/compile", {
        code: generatedCode,
        inputs: [],
      });
      alert(res.data.stdout || res.data.stderr || "⚠️ No output received.");
    } catch (err) {
      console.error("Compilation error:", err);
      alert("❌ Error compiling code.");
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-4 flex flex-col">
      <h2 className="text-xl font-semibold mb-2">📝 Code Editor</h2>

      <textarea
        className="flex-1 w-full p-3 rounded-lg border focus:ring-2 focus:ring-purple-500 resize-none"
        rows="12"
        value={generatedCode}
        onChange={(e) => setGeneratedCode(e.target.value)}
      />

      <div className="mt-4 flex flex-wrap gap-2">
        <button
          onClick={handleGenerateCode}
          className="bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-lg shadow"
        >
          Generate
        </button>
        <button
          onClick={handleCompileCode}
          className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg shadow"
        >
          Compile
        </button>
        <button
          onClick={handleSaveFile}
          className="bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg shadow"
        >
          Save
        </button>
      </div>

      {compileOutput && (
        <div className="mt-4 p-3 bg-gray-100 rounded-lg border text-sm whitespace-pre-wrap">
          {compileOutput}
        </div>
      )}
    </div>
  );
}

export default CodeEditor;
