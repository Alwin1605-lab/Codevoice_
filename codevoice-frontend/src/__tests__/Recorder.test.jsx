import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import Recorder from '../components/Recorder';

// Mock MediaRecorder and navigator.mediaDevices
class MockMediaRecorder {
  constructor(stream) {
    this.stream = stream;
    this.state = 'inactive';
    this.ondataavailable = null;
    this.onstop = null;
  }
  start() { this.state = 'recording'; }
  stop() { this.state = 'inactive'; if (this.ondataavailable) this.ondataavailable({ data: new Blob(['hello']) }); if (this.onstop) this.onstop(); }
}

beforeAll(() => {
  global.navigator.mediaDevices = {
    getUserMedia: jest.fn().mockResolvedValue({ getTracks: () => [] })
  };
  global.MediaRecorder = MockMediaRecorder;
});

test('Recorder calls onRecorded with a blob when stopped', async () => {
  const onRecorded = jest.fn();
  const { getByLabelText } = render(<Recorder onRecorded={onRecorded} renderButton={({ isRecording, start, stop }) => (
    <button onClick={() => (isRecording ? stop() : start())} aria-label="rec-btn">{isRecording ? 'Stop' : 'Start'}</button>
  )} />);

  const btn = getByLabelText('rec-btn');
  fireEvent.click(btn);
  // Now it should be recording; click again to stop
  fireEvent.click(btn);

  await waitFor(() => expect(onRecorded).toHaveBeenCalled());
});
