import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import * as apiService from '../services/apiService';
import CodeCraftingPage from '../pages/CodeCraftingPage';

beforeAll(() => {
  // Mock MediaRecorder and getUserMedia similar to Recorder test
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
  global.navigator.mediaDevices = { getUserMedia: jest.fn().mockResolvedValue({ getTracks: () => [] }) };
  global.MediaRecorder = MockMediaRecorder;
});

import Recorder from '../components/Recorder';

jest.mock('../services/apiService', () => ({
  transcribeAudio: jest.fn(),
  generateCode: jest.fn(),
}));

test('Record -> transcribe -> generate sequence using Recorder component', async () => {
  apiService.transcribeAudio.mockResolvedValue({ transcript: 'print(\"hi\")' });
  apiService.generateCode.mockResolvedValue({ code: 'print("hi")' });

  const onRecorded = jest.fn(async (blob) => {
    const t = await apiService.transcribeAudio(blob);
    const g = await apiService.generateCode(t.transcript, 'python');
    return g.code;
  });

  const { getByRole } = render(<Recorder onRecorded={onRecorded} renderButton={({ isRecording, start, stop }) => (
    <button onClick={() => (isRecording ? stop() : start())} aria-label="rec-run">{isRecording ? 'Stop' : 'Start'}</button>
  )} />);

  const btn = getByRole('button', { name: /Start/i });
  fireEvent.click(btn);
  fireEvent.click(btn);

  await waitFor(() => expect(onRecorded).toHaveBeenCalled());
  await waitFor(() => expect(apiService.transcribeAudio).toHaveBeenCalled());
  await waitFor(() => expect(apiService.generateCode).toHaveBeenCalled());
});
