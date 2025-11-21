import React, { useMemo } from 'react';
import { IconButton, Tooltip } from '@mui/material';
import { Mic, MicOff } from '@mui/icons-material';
import useSpeechInput from '../hooks/useSpeechInput';

const MicControl = ({
  onTranscript,
  tooltip = 'Speak to fill this field',
  lang = 'en-US',
  continuous = false,
  disabled = false,
}) => {
  const speechOptions = useMemo(() => ({
    onResult: onTranscript,
    lang,
    continuous,
  }), [onTranscript, lang, continuous]);

  const {
    isSupported,
    isListening,
    error,
    startListening,
    stopListening,
  } = useSpeechInput(speechOptions);

  const handleToggle = () => {
    if (!isSupported || disabled) return;
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const resolvedTooltip = !isSupported
    ? 'Speech recognition not supported in this browser'
    : error === 'not-allowed'
      ? 'Microphone permission denied'
      : isListening
        ? 'Stop listening'
        : tooltip;

  return (
    <Tooltip title={resolvedTooltip}>
      <span>
        <IconButton
          onClick={handleToggle}
          color={isListening ? 'error' : 'primary'}
          disabled={!isSupported || disabled}
          size="small"
        >
          {isListening ? <MicOff fontSize="small" /> : <Mic fontSize="small" />}
        </IconButton>
      </span>
    </Tooltip>
  );
};

export default MicControl;
