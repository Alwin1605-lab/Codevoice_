/**
 * Voice Control Troubleshooting Guide
 * 
 * Common issues and their solutions for voice commands not working
 */

// Issue 1: Microphone Permission
// Solution: Grant microphone access in browser settings
// - Chrome: chrome://settings/content/microphone
// - Firefox: about:preferences#privacy
// - Edge: edge://settings/content/microphone

// Issue 2: HTTPS Requirement (some browsers)
// Solution: Use localhost or enable HTTPS
const isSecureContext = window.isSecureContext;
console.log('Secure context:', isSecureContext);

// Issue 3: Browser Compatibility
// Solution: Use Chrome or Edge
const speechRecognitionSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
console.log('Speech recognition supported:', speechRecognitionSupported);

// Issue 4: Autoplay Policy
// Solution: User interaction required before starting
let userInteracted = false;
document.addEventListener('click', () => {
    userInteracted = true;
    console.log('User interaction detected');
});

// Issue 5: Multiple instances
// Solution: Stop existing recognition before starting new
let globalRecognition = null;

function startVoiceRecognition() {
    if (globalRecognition) {
        globalRecognition.stop();
    }
    
    if (!userInteracted) {
        console.warn('User interaction required before starting voice recognition');
        return;
    }
    
    const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
    globalRecognition = new SpeechRecognition();
    
    globalRecognition.continuous = true;
    globalRecognition.interimResults = false;
    globalRecognition.lang = 'en-US';
    
    globalRecognition.start();
}

// Issue 6: Network connectivity
// Solution: Ensure backend is running
async function checkBackend() {
    try {
        const response = await fetch('http://localhost:8000/health');
        console.log('Backend status:', response.status);
        return response.ok;
    } catch (error) {
        console.error('Backend not accessible:', error);
        return false;
    }
}

// Export for debugging
window.voiceDebug = {
    isSecureContext,
    speechRecognitionSupported,
    userInteracted,
    checkBackend,
    startVoiceRecognition
};