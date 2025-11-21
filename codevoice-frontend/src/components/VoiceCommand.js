// src/components/VoiceCommand.js
const VoiceCommand = async (command) => {
  if (command.includes("generate")) {
    const response = await fetch("/api/generate-code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: "generate" }), // dummy prompt
    });
    const data = await response.json();
    console.log("⚙️ Code generated:", data.code);
    return { transcript: "generate" };
  }

  if (command.includes("compile")) {
    const response = await fetch("/api/compile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: "compile" }),
    });
    const data = await response.json();
    console.log("🔧 Compiled Output:", data.output);
    return {};
  }

  if (command.includes("save")) {
    // Could trigger a download or backend call
    console.log("💾 Saving code...");
    return {};
  }

  if (command.includes("start recording")) {
    console.log("🎙️ Awaiting prompt for generation...");
    return { transcript: "" }; // Reset for MicInput
  }

  return {};
};

export default VoiceCommand;
