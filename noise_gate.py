from audio_processor import AudioProcessor
import numpy as np
from scipy.signal import butter, filtfilt
from scipy.io import wavfile


class NoiseGate(AudioProcessor):
    def __init__(self, input_file):
        super().__init__(input_file)
        self.is_stereo = len(self.audio_data.shape) > 1
        if self.is_stereo:
            self.audio_data_right = self.audio_data[:, 1]
            self.audio_data = self.audio_data[:, 0]  # Left channel

    def _apply_frequency_gate(self, data, gate_freq):
        """Apply gate to specific frequency band"""
        if gate_freq > 0:
            nyquist = self.sample_rate / 2
            b, a = butter(4, gate_freq / nyquist, btype="lowpass")
            return filtfilt(b, a, data)
        return data

    def apply_gate(
        self,
        threshold_db=-27.8,
        reduction_db=-24,
        attack_ms=10,
        decay_ms=100,
        hold_ms=50,
        gate_freq=0,
        mode="Gate",
        stereo_link="LinkStereo",
    ):
        """Apply noise gate effect to audio.

        Args:
            threshold_db (float): Threshold level in dB (default: -27.8)
            reduction_db (float): Amount of reduction in dB (default: -24)
            attack_ms (int): Attack time in ms (default: 10)
            decay_ms (int): Decay time in ms (default: 100)
            hold_ms (int): Hold time in ms (default: 50)
            gate_freq (float): Frequency-specific gate in Hz (default: 0)
            mode (str): Gate mode - "Gate" or "Duck" (default: "Gate")
            stereo_link (str): Stereo linking mode (default: "LinkStereo")
        """
        # Convert from dB
        threshold = 10 ** (threshold_db / 20)
        reduction = 10 ** (reduction_db / 20)

        # Convert times to samples
        attack_samples = int(self.sample_rate * attack_ms / 1000)
        decay_samples = int(self.sample_rate * decay_ms / 1000)
        hold_samples = int(self.sample_rate * hold_ms / 1000)

        def process_channel(data):
            # Apply frequency-specific gate if needed
            data = self._apply_frequency_gate(data, gate_freq)

            # Create envelope
            envelope = np.abs(data)

            # Apply gate
            gate_mask = np.zeros_like(data)

            # Gate state
            is_open = False
            hold_counter = 0

            for i in range(len(data)):
                if envelope[i] > threshold:
                    is_open = True
                    hold_counter = hold_samples
                    gate_mask[i] = 1
                elif hold_counter > 0:
                    hold_counter -= 1
                    gate_mask[i] = 1
                else:
                    is_open = False
                    if mode == "Gate":
                        gate_mask[i] = reduction
                    else:  # Duck mode
                        gate_mask[i] = 1 - reduction

            # Apply attack and decay
            smoothed_mask = np.zeros_like(gate_mask)
            for i in range(len(gate_mask)):
                if gate_mask[i] > smoothed_mask[i - 1]:
                    # Attack
                    smoothed_mask[i] = min(1, smoothed_mask[i - 1] + 1 / attack_samples)
                else:
                    # Decay
                    smoothed_mask[i] = max(
                        reduction, smoothed_mask[i - 1] - 1 / decay_samples
                    )

            return data * smoothed_mask

        # Process left channel
        self.audio_data = process_channel(self.audio_data)

        # Process right channel if stereo
        if self.is_stereo:
            if stereo_link == "LinkStereo":
                # Use same envelope for both channels
                self.audio_data_right = self.audio_data_right * (
                    self.audio_data / self.audio_data_right
                )
            else:
                self.audio_data_right = process_channel(self.audio_data_right)

    def save(self, output_file):
        if self.is_stereo:
            # Combine channels
            stereo_data = np.vstack((self.audio_data, self.audio_data_right)).T
            audio_out = np.int16(stereo_data * 32767)
        else:
            audio_out = np.int16(self.audio_data * 32767)
        wavfile.write(output_file, self.sample_rate, audio_out)
