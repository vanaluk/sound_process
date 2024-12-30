import numpy as np
from scipy.io import wavfile
# from scipy.signal import butter, filtfilt, convolve


class AudioProcessor:
    def __init__(self, input_file):
        self.sample_rate, self.audio_data = wavfile.read(input_file)
        # Convert to float32 for processing
        self.audio_data = self.audio_data.astype(np.float32)
        if len(self.audio_data.shape) > 1:
            self.audio_data = self.audio_data[:, 0]  # Take first channel if stereo
        # Normalize data
        self.audio_data = self.audio_data / np.max(np.abs(self.audio_data))

    def save(self, output_file):
        # Denormalize and convert back to int16
        audio_out = np.int16(self.audio_data * 32767)
        wavfile.write(output_file, self.sample_rate, audio_out)
