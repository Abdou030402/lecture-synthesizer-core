import torchaudio
from chatterbox.tts import ChatterboxTTS
import os
import argparse
import sys

chatterbox_model = None
try:
    chatterbox_model = ChatterboxTTS.from_pretrained(device="cuda")
except Exception as e:
    print(f"[ERROR] Chatterbox model could not be loaded: {e}", file=sys.stderr)

def synthesize_chatterbox_audio(text: str, output_filepath: str) -> str:
    if chatterbox_model is None:
        return "[ERROR] Chatterbox model not loaded. Cannot synthesize audio."

    try:
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        audio = chatterbox_model.generate(text)
        torchaudio.save(output_filepath, audio, chatterbox_model.sr)
        return output_filepath
    except Exception as e:
        return f"[ERROR] Failed to synthesize audio with Chatterbox: {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chatterbox TTS audio generation.")
    parser.add_argument('--text', required=True, help="The text to convert to speech.")
    parser.add_argument('--output', required=True, help="The full path to the output .wav file.")
    args = parser.parse_args()

    saved_path = synthesize_chatterbox_audio(
        text=args.text,
        output_filepath=args.output
    )

    if "[ERROR]" in saved_path:
        print(saved_path, file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Audio saved to: {saved_path}")