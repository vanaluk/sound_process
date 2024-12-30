from main import process_audio
import os


def process_directory(input_dir, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Process all wav files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".wav"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"processed_{filename}")

            print(f"Processing {filename}...")
            process_audio(input_path, output_path)
            print(f"Saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    input_directory = "audio/input"
    output_directory = "audio/output"

    process_directory(input_directory, output_directory)
