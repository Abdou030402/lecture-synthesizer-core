import argparse
import logging
import os
import sys
import subprocess
from ocr.pdf_parser import analyze_and_save

def main():
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Lecture Synthesizer: Convert document to lecture audio.")
    parser.add_argument('--input', '-i', required=True, help="Path to the input file (PDF or image)")
    parser.add_argument('--tts', '-t', required=True, choices=['chatterbox', 'elevenlabs_v2', 'dia'],
                        help="TTS engine to use: 'chatterbox', 'elevenlabs_v2', or 'dia'")
    args = parser.parse_args()

    input_path = args.input
    tts_engine = args.tts

    if not os.path.isfile(input_path):
        logging.error(f"Input file not found: {input_path}")
        sys.exit(1)

    ext = os.path.splitext(input_path)[1].lower()
    is_pdf = ext == '.pdf'
    is_image = ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp']
    if not is_pdf and not is_image:
        logging.error("Unsupported file type. Please provide a PDF or image file as input.")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = script_dir

    if sys.platform == "win32":
        ocr_env_python = os.path.join(project_root, '.venv_ocr_craft', 'Scripts', 'python.exe')
        ollama_env_python = os.path.join(project_root, '.venv_ollama', 'Scripts', 'python.exe')
        chatter_env_python = os.path.join(project_root, '.venv_chatter', 'Scripts', 'python.exe')
        elevenlabs_env_python = os.path.join(project_root, '.venv_elevenlabs', 'Scripts', 'python.exe')
        dia_env_python = os.path.join(project_root, '.venv_dia', 'Scripts', 'python.exe')
    else:
        ocr_env_python = os.path.join(project_root, '.venv_ocr_craft', 'bin', 'python')
        ollama_env_python = os.path.join(project_root, '.venv_ollama', 'bin', 'python')
        chatter_env_python = os.path.join(project_root, '.venv_chatter', 'bin', 'python')
        elevenlabs_env_python = os.path.join(project_root, '.venv_elevenlabs', 'bin', 'python')
        dia_env_python = os.path.join(project_root, '.venv_dia', 'bin', 'python')

    trocr_script = os.path.join(project_root, 'ocr', 'trocr_craft.py')
    generate_lecture_script = os.path.join(project_root, 'nlp', 'nlp_model.py')
    chatterbox_script = os.path.join(project_root, 'TTS', 'chatterbox_audio.py')
    elevenlabs_script = os.path.join(project_root, 'TTS', 'elevenlabs_audio.py')
    dia_script = os.path.join(project_root, 'TTS', 'Dia_audio.py')

    nlp_output_dir = os.path.join(project_root, 'step_outputs', 'llm_outputs')
    final_output_dir = os.path.join(project_root, 'Final_Output')
    os.makedirs(nlp_output_dir, exist_ok=True)
    os.makedirs(final_output_dir, exist_ok=True)

    logging.info(f"Processing input file: {input_path}")
    text_content = ""

    if is_pdf:
        logging.info("Input is a PDF. Extracting text using PDF parser...")
        try:
            text_content = analyze_and_save(input_path)
        except Exception as e:
            logging.error(f"Failed to extract text from PDF: {e}")
            sys.exit(1)
    elif is_image:
        logging.info("Input is an image. Extracting text using OCR (TrOCR + CRAFT)...")
        if not os.path.exists(ocr_env_python):
            logging.error(f"OCR Python executable not found at '{ocr_env_python}'. Please ensure .venv_trocr is set up.")
            sys.exit(1)
        if not os.path.exists(trocr_script):
            logging.error(f"OCR script not found at '{trocr_script}'. Please ensure trocr_craft.py exists.")
            sys.exit(1)
        try:
            result = subprocess.run(
                [ocr_env_python, trocr_script, input_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            text_content = result.stdout.strip()
            if result.stderr:
                logging.info(f"OCR Subprocess Stderr: {result.stderr.strip()}")
        except FileNotFoundError as e:
            logging.error(f"OCR execution failed: {e}. Ensure OCR virtual environment and script exist.")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            logging.error(f"OCR script returned error code {e.returncode}. Stderr: {e.stderr.strip()}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"An unexpected error occurred during OCR subprocess execution: {e}")
            sys.exit(1)
    else:
        logging.error("Unknown input file type.")
        sys.exit(1)

    if not text_content:
        logging.error("No text was extracted from the input file. Exiting.")
        sys.exit(1)

    logging.info(f"Extracted text length: {len(text_content)} characters.")

    logging.info("Generating lecture script using NLP model (Ollama llama3:8b)...")
    ollama_model_name = "llama3:8b"
    system_prompt_type = tts_engine
    
    if not os.path.exists(ollama_env_python):
        logging.error(f"Ollama client Python executable not found at '{ollama_env_python}'. Please ensure .venv_ollama is set up.")
        sys.exit(1)
    if not os.path.exists(generate_lecture_script):
        logging.error(f"Lecture generation script not found at '{generate_lecture_script}'. Please ensure generate_lecture.py exists.")
        sys.exit(1)

    try:
        result = subprocess.run(
            [ollama_env_python, generate_lecture_script, text_content, ollama_model_name, system_prompt_type],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        lecture_script = result.stdout.strip()
        if result.stderr:
            logging.info(f"NLP Subprocess Stderr: {result.stderr.strip()}")

        if "[ERROR]" in lecture_script:
            logging.error(f"Lecture generation failed: {lecture_script}")
            sys.exit(1)
            
    except FileNotFoundError as e:
        logging.error(f"NLP model generation failed: {e}. Ensure Ollama client virtual environment and script exist.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logging.error(f"Ollama script returned error code {e.returncode}. Stderr: {e.stderr.strip()}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred during NLP model generation: {e}")
        sys.exit(1)
    
    logging.info("Lecture script generation completed.")

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    lecture_text_filename = f"{base_name}_{ollama_model_name.replace(':', '-')}_{tts_engine}.txt"
    lecture_text_path = os.path.join(nlp_output_dir, lecture_text_filename)
    try:
        with open(lecture_text_path, 'w', encoding='utf-8') as f:
            f.write(lecture_script)
    except Exception as e:
        logging.error(f"Failed to save lecture script to file: {e}")
    else:
        logging.info(f"Lecture script saved to {lecture_text_path}")

    final_ext = 'mp3' if tts_engine == 'elevenlabs_v2' else 'wav'
    final_audio_filename = f"{base_name}_{tts_engine}.{final_ext}"
    final_audio_path = os.path.join(final_output_dir, final_audio_filename)
    logging.info(f"Converting lecture script to speech using TTS engine: {tts_engine}")

    try:
        if tts_engine == 'chatterbox':
            if not os.path.exists(chatter_env_python):
                logging.error(f"Chatterbox Python executable not found at '{chatter_env_python}'. Please ensure .venv_chatter is set up.")
                sys.exit(1)
            if not os.path.exists(chatterbox_script):
                logging.error(f"Chatterbox script not found at '{chatterbox_script}'. Please ensure chatterbox_audio.py exists.")
                sys.exit(1)
            cmd = [chatter_env_python, chatterbox_script, "--text", lecture_script, "--output", final_audio_path]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            if result.stderr:
                logging.info(f"Chatterbox TTS Subprocess Stderr: {result.stderr.strip()}")
        elif tts_engine == 'elevenlabs_v2':
            if not os.path.exists(elevenlabs_env_python):
                logging.error(f"ElevenLabs Python executable not found at '{elevenlabs_env_python}'. Please ensure .venv_elevenlabs is set up.")
                sys.exit(1)
            if not os.path.exists(elevenlabs_script):
                logging.error(f"ElevenLabs script not found at '{elevenlabs_script}'. Please ensure elevenlabs_audio.py exists.")
                sys.exit(1)
            cmd = [elevenlabs_env_python, elevenlabs_script, "--text", lecture_script, "--output", final_audio_path]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            if result.stderr:
                logging.info(f"ElevenLabs TTS Subprocess Stderr: {result.stderr.strip()}")
        elif tts_engine == 'dia':
            if not os.path.exists(dia_env_python):
                logging.error(f"DIA Python executable not found at '{dia_env_python}'. Please ensure .venv_dia is set up.")
                sys.exit(1)
            if not os.path.exists(dia_script):
                logging.error(f"DIA script not found at '{dia_script}'. Please ensure dia_audio.py exists.")
                sys.exit(1)
            cmd = [dia_env_python, dia_script, "--text", lecture_script, "--output", final_audio_path]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            if result.stderr:
                logging.info(f"DIA TTS Subprocess Stderr: {result.stderr.strip()}")
        else:
            logging.error(f"Unknown TTS engine: {tts_engine}")
            sys.exit(1)
    except FileNotFoundError as e:
        logging.error(f"TTS execution failed: {e}. Ensure the correct virtual environment and TTS script exist.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logging.error(f"TTS script returned error code {e.returncode}. Stderr: {e.stderr.strip()}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred during TTS conversion: {e}")
        sys.exit(1)

    if os.path.isfile(final_audio_path):
        logging.info(f"Audio output saved to {final_audio_path}")
    else:
        logging.error("TTS process completed, but no audio file was found.")
        sys.exit(1)

    logging.info("Processing complete. Lecture audio is ready.")

if __name__ == "__main__":
    main()
