from declicker import DeClicker
from noise_gate import NoiseGate


def process_audio(input_file, output_file):
    # Apply DeClicker
    declicker = DeClicker(input_file)
    declicker.remove_clicks()
    declicker.save("temp.wav")

    # Apply Noise Gate
    noise_gate = NoiseGate("temp.wav")
    noise_gate.apply_gate()
    noise_gate.save(output_file)


if __name__ == "__main__":
    process_audio("input.wav", "output.wav")
