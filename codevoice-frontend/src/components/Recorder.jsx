import React, { useState, useRef } from 'react';
import PropTypes from 'prop-types';
import { IconButton, Tooltip } from '@mui/material';
import { Mic } from '@mui/icons-material';

const Recorder = ({ onRecorded, renderButton, tooltip = 'Record' }) => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRef = useRef(null);
  const chunksRef = useRef([]);

  const start = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.warn('Media devices not supported');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRef.current = { recorder, stream };
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        onRecorded && onRecorded(blob);
        // stop tracks
        try {
          stream.getTracks().forEach((t) => t.stop());
        } catch (e) {}
      };

      recorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Failed to start recorder', err);
    }
  };

  const stop = () => {
    try {
      if (mediaRef.current && mediaRef.current.recorder && mediaRef.current.recorder.state !== 'inactive') {
        mediaRef.current.recorder.stop();
      }
    } catch (e) {
      console.warn('Stop failed', e);
    }
    setIsRecording(false);
  };

  if (renderButton) {
    return renderButton({ isRecording, start, stop });
  }

  return (
    <Tooltip title={tooltip}>
      <IconButton color={isRecording ? 'error' : 'default'} onClick={() => (isRecording ? stop() : start())}>
        <Mic />
      </IconButton>
    </Tooltip>
  );
};

Recorder.propTypes = {
  onRecorded: PropTypes.func,
  renderButton: PropTypes.func,
  tooltip: PropTypes.string
};

export default Recorder;
