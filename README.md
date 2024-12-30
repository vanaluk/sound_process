# Audio Processing Tool - Usage Guide

## Project Files Overview
- audio_processor.py - Base class for audio processing
- declicker.py - Click removal implementation
- noise_gate.py - Noise gate implementation
- main.py - Main processing script
- example_usage.py - Examples of different usage scenarios



## Setup



1. Install dependencies:

pip install numpy scipy


2. Create directory structure:

your_project/
├── audio/
│   ├── input/
│   └── output/
└── scripts/
    ├── audio_processor.py
    ├── declicker.py
    ├── noise_gate.py
    ├── main.py
    └── example_usage.py


## Usage Methods



### 1. Quick Processing
For basic processing with default settings:

from main import process_audio

# Process single file
process_audio("audio/input/file.wav", "audio/output/processed.wav")


### 2. DeClicker Only
To remove clicks and pops:

from declicker import DeClicker

declicker = DeClicker("input.wav")
declicker.remove_clicks(
    threshold=0.4,      # Click detection sensitivity
    max_steps=3,        # Click length
    separation=4,       # Space between clicks
    crossfade_ms=6      # Smooth transition
)
declicker.save("declicked.wav")


### 3. Noise Gate Only
To reduce background noise:

from noise_gate import NoiseGate

gate = NoiseGate("input.wav")
gate.apply_gate(
    threshold_db=-30,   # Noise threshold
    reduction_db=-20,   # Reduction amount
    attack_ms=15,       # Attack time
    decay_ms=150,       # Decay time
    hold_ms=60         # Hold time
)
gate.save("noise_reduced.wav")


### 4. Combined Processing
To apply both effects with custom settings:

def process_custom(input_file, output_file):
    # First remove clicks
    declicker = DeClicker(input_file)
    declicker.remove_clicks(threshold=0.3)
    declicker.save("temp.wav")
    
    # Then reduce noise
    gate = NoiseGate("temp.wav")
    gate.apply_gate(threshold_db=-25)
    gate.save(output_file)


## Parameter Settings



### DeClicker Parameters

{
    "threshold": 0.5,     # Default: 0.5 (0.1-1.0)
    "max_steps": 2,       # Default: 2 (1-10)
    "separation": 3,      # Default: 3 (1-10)
    "crossfade_ms": 5     # Default: 5 (1-20)
}


### Noise Gate Parameters

{
    "threshold_db": -27.8,  # Default: -27.8 (-60-0)
    "reduction_db": -24,    # Default: -24 (-60-0)
    "attack_ms": 10,        # Default: 10 (1-100)
    "decay_ms": 100,        # Default: 100 (1-1000)
    "hold_ms": 50          # Default: 50 (1-500)
}


## Common Use Cases



### Light Processing

# For slightly noisy audio
declicker.remove_clicks(threshold=0.6)
gate.apply_gate(threshold_db=-35, reduction_db=-15)


### Heavy Processing

# For very noisy audio
declicker.remove_clicks(threshold=0.3, max_steps=4)
gate.apply_gate(threshold_db=-25, reduction_db=-30)


## Important Notes
- Input files must be WAV format
- Processes mono audio (first channel if stereo)
- Temporary files are automatically cleaned up
- Process creates backup files by default
- Test with small audio segments first



## Troubleshooting

- If too many clicks detected: increase threshold

- If clicks remain: decrease threshold

- If audio sounds muffled: increase threshold_db

- If noise remains: decrease threshold_db

- For smoother transitions: increase attack_ms/decay_ms