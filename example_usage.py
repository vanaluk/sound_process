from declicker import DeClicker
from noise_gate import NoiseGate
import os

# Using only DeClicker
declicker = DeClicker("audio/input.wav")
declicker.remove_clicks(
    threshold=0.4,  # Adjust sensitivity
    max_steps=3,  # Adjust click length
    separation=4,  # Minimum samples between clicks
    crackle_threshold=-40,  # Dense click threshold
    crossfade_ms=6,  # Crossfade duration
)
declicker.save("audio/declicked.wav")

# Using only NoiseGate
noise_gate = NoiseGate("audio/input.wav")
noise_gate.apply_gate(
    threshold_db=-30,  # Noise threshold
    reduction_db=-20,  # Amount of reduction
    attack_ms=15,  # Attack time
    decay_ms=150,  # Decay time
    hold_ms=60,  # Hold time
)
noise_gate.save("audio/gated.wav")


# Using both with custom parameters
def process_with_custom_params(input_file, output_file):
    # First apply declicker
    declicker = DeClicker(input_file)
    declicker.remove_clicks(threshold=0.3, max_steps=4)
    declicker.save("temp.wav")

    # Then apply noise gate
    noise_gate = NoiseGate("temp.wav")
    noise_gate.apply_gate(threshold_db=-25, reduction_db=-18)
    noise_gate.save(output_file)

    # Clean up temporary file
    os.remove("temp.wav")


# Process a file with custom parameters
process_with_custom_params("audio/input.wav", "audio/output.wav")
