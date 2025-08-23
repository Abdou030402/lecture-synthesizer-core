import os
import argparse
import sys
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

DEFAULT_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

def synthesize_audio(text: str, voice_id: str, output_path: str, model_id: str = "eleven_multilingual_v2") -> None:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY environment variable is not set.")

    client = ElevenLabs(api_key=api_key)
    
    try:
        audio_stream = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format="mp3_44100_128",
        )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                if chunk:
                    f.write(chunk)
        print(f"✅ Audio saved as {output_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to synthesize audio with ElevenLabs: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ElevenLabs TTS audio generation.")
    parser.add_argument('--text', required=True, help="The text to convert to speech.")
    parser.add_argument('--output', required=True, help="The full path to the output .mp3 file.")
    parser.add_argument('--voice_id', default=DEFAULT_VOICE_ID, help="The ElevenLabs voice ID to use.")
    args = parser.parse_args()

    try:
        synthesize_audio(
            text=args.text,
            voice_id=args.voice_id,
            output_path=args.output
        )
    except (ValueError, RuntimeError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
