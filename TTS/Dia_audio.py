import soundfile as sf
from dia.model import Dia
import os
import sys
import argparse

dia_model = None
try:
    dia_model = Dia.from_pretrained("nari-labs/Dia-1.6B-0626", compute_dtype="float16")
except Exception as e:
    print(f"[ERROR] Dia model could not be loaded: {e}", file=sys.stderr)

def synthesize_dia_audio(text: str, output_filepath: str) -> str:
    if dia_model is None:
        return "[ERROR] Dia model not loaded. Cannot synthesize audio."

    try:
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        audio = dia_model.generate(text)
        sf.write(output_filepath, audio, 44100)
        return output_filepath
    except Exception as e:
        return f"[ERROR] Failed to synthesize audio with Dia: {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dia TTS audio generation.")
    parser.add_argument('--text', required=True, help="The text to convert to speech.")
    parser.add_argument('--output', required=True, help="The full path to the output .wav file.")
    args = parser.parse_args()

    saved_path = synthesize_dia_audio(
        text=args.text,
        output_filepath=args.output
    )

    if "[ERROR]" in saved_path:
        print(saved_path, file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Audio saved to: {saved_path}")
