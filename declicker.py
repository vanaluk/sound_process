from audio_processor import AudioProcessor
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt


class DeClicker(AudioProcessor):
    def __init__(self, input_file):
        super().__init__(input_file)

    def _split_into_bands(self, data, n_bands=12, freq_low=150, freq_high=9600):
        """Split audio into frequency bands using bandpass filters"""
        bands = []
        # Calculate frequency ranges for each band (logarithmic spacing)
        frequencies = np.logspace(np.log10(freq_low), np.log10(freq_high), n_bands + 1)

        for i in range(n_bands):
            low = frequencies[i]
            high = frequencies[i + 1]

            # Create bandpass filter
            nyquist = self.sample_rate / 2
            b, a = butter(4, [low / nyquist, high / nyquist], btype="band")

            # Apply filter to get this frequency band
            filtered = filtfilt(b, a, data)
            bands.append(filtered)

        return bands

    def _merge_bands(self, bands):
        """Merge frequency bands back together"""
        return np.sum(bands, axis=0)

    def remove_clicks(
        self,
        threshold=0.5,
        max_steps=2,
        separation=3,
        crackle_threshold=-45,
        crossfade_ms=5,
        n_bands=12,
        passes=2,
        freq_low=150,
        freq_high=9600,
    ):
        """Remove clicks from audio using multi-band processing.

        Args:
            threshold (float): Sensitivity threshold (default: 0.5)
            max_steps (int): Maximum click length in steps (default: 2)
            separation (int): Minimum samples between clicks (default: 3)
            crackle_threshold (float): Dense click threshold in dB (default: -45)
            crossfade_ms (float): Crossfade duration in ms (default: 5)
            n_bands (int): Number of frequency bands (default: 12)
            passes (int): Number of processing passes (default: 2)
            freq_low (float): Lower frequency bound in Hz (default: 150)
            freq_high (float): Upper frequency bound in Hz (default: 9600)
        """
        # Convert parameters
        crossfade_samples = int(self.sample_rate * crossfade_ms / 1000)

        # Process multiple passes
        for pass_num in range(passes):
            # Split into frequency bands
            bands = self._split_into_bands(
                self.audio_data, n_bands, freq_low, freq_high
            )
            processed_bands = []

            # Process each band separately
            for band in bands:
                # Find peaks in this frequency band
                peaks, _ = find_peaks(
                    np.abs(band), height=threshold, distance=separation
                )

                # Process clicks in this band
                for peak in peaks:
                    start = max(0, peak - max_steps)
                    end = min(len(band), peak + max_steps)

                    # Create smooth transition
                    left = band[start:peak]
                    right = band[peak:end]

                    # Interpolate values
                    interpolated = np.linspace(left[0], right[-1], end - start)

                    # Apply crossfade
                    if len(left) > 0 and len(right) > 0:
                        fade_in = np.linspace(
                            0, 1, min(len(interpolated), crossfade_samples)
                        )
                        fade_out = np.linspace(
                            1, 0, min(len(interpolated), crossfade_samples)
                        )

                        # Apply crossfade at the edges of the interpolated section
                        if len(interpolated) > crossfade_samples:
                            interpolated[:crossfade_samples] *= fade_in
                            interpolated[-crossfade_samples:] *= fade_out

                    # Replace click
                    band[start:end] = interpolated

                processed_bands.append(band)

            # Merge bands back together
            self.audio_data = self._merge_bands(processed_bands)
