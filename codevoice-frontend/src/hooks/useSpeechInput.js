import { useCallback, useEffect, useRef, useState } from 'react';

const getSpeechRecognition = () => {
  if (typeof window === 'undefined') return null;
  return window.SpeechRecognition || window.webkitSpeechRecognition || null;
};

const useSpeechInput = ({
  onResult,
  lang = 'en-US',
  continuous = false,
  interimResults = false,
} = {}) => {
  const recognitionRef = useRef(null);
  const onResultRef = useRef(onResult);
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    onResultRef.current = onResult;
  }, [onResult]);

  useEffect(() => {
    const SpeechRecognition = getSpeechRecognition();
    setIsSupported(Boolean(SpeechRecognition));

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const startListening = useCallback(() => {
    const SpeechRecognition = getSpeechRecognition();
    if (!SpeechRecognition) {
      setError('not-supported');
      return;
    }
    if (isListening) return;

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    recognition.lang = lang;
    recognition.continuous = continuous;
    recognition.interimResults = interimResults;

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0]?.transcript || '')
        .join(' ')
        .trim();

      if (transcript && onResultRef.current) {
        onResultRef.current(transcript, event);
      }
    };

    recognition.onerror = (event) => {
      setError(event.error || 'unknown');
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      recognitionRef.current = null;
    };

    recognition.start();
    setError(null);
    setIsListening(true);
  }, [isListening, lang, continuous, interimResults]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
  }, []);

  return {
    isSupported,
    isListening,
    error,
    startListening,
    stopListening,
  };
};

export default useSpeechInput;
