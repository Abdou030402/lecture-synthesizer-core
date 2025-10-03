import os
import sys
import uuid
import subprocess
import re
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
FINAL_OUTPUT_DIR = BASE_DIR / "Final_Output"
MAIN_SCRIPT = BASE_DIR / "main.py"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("LECTURE_SYNTH_SECRET", "change-me")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB upload limit

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "bmp", "gif", "tiff", "webp"}


def detect_ollama_port():
    """Auto-detect Ollama port and set OLLAMA_HOST env var"""
    try:
        result = subprocess.check_output("ss -ltnp | grep ollama", shell=True, text=True)
        match = re.search(r":(\d+)\s", result)
        if match:
            port = match.group(1)
            os.environ["OLLAMA_HOST"] = f"http://127.0.0.1:{port}"
            print(f"[INFO] OLLAMA_HOST set to {os.environ['OLLAMA_HOST']}")
        else:
            raise ValueError("No port found")
    except Exception:
        os.environ["OLLAMA_HOST"] = "http://127.0.0.1:11434"
        print(f"[WARN] Falling back to default OLLAMA_HOST={os.environ['OLLAMA_HOST']}")

# Call this once at startup
detect_ollama_port()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("document")
        if file is None or file.filename == "":
            flash("Please choose a file before submitting.", "error")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Unsupported file type. Please upload a PDF or image.", "error")
            return redirect(request.url)

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        original_filename = secure_filename(file.filename)
        file_extension = Path(original_filename).suffix
        unique_id = uuid.uuid4().hex
        saved_filename = f"{unique_id}{file_extension}"
        saved_path = UPLOAD_DIR / saved_filename
        file.save(saved_path)

        try:
            audio_filename = run_pipeline(saved_path, unique_id)
        except RuntimeError as exc:  # pragma: no cover - defensive logging path
            flash(str(exc), "error")
            return redirect(request.url)

        return redirect(url_for("result", job_id=unique_id, audio_filename=audio_filename))

    return render_template("index.html")


def run_pipeline(input_path: Path, unique_id: str) -> str:
    if not MAIN_SCRIPT.exists():
        raise RuntimeError("main.py not found. Please ensure you are running the app from the project root.")

    command = [
        sys.executable,
        str(MAIN_SCRIPT),
        "--input",
        str(input_path),
        "--tts",
        "elevenlabs_v2",
    ]

    try:
        completed_process = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        error_message = exc.stderr.strip() or "An unknown error occurred while generating the lecture audio."
        raise RuntimeError(error_message)

    audio_filename = f"{unique_id}_elevenlabs_v2.mp3"
    audio_path = FINAL_OUTPUT_DIR / audio_filename

    if not audio_path.exists():
        stdout_preview = (completed_process.stdout or "").strip().splitlines()[-5:]
        raise RuntimeError(
            "The lecture audio could not be located after processing.\n"
            + "\n".join(stdout_preview)
        )

    return audio_filename


@app.route("/result")
def result():
    job_id = request.args.get("job_id")
    audio_filename = request.args.get("audio_filename")
    if not job_id or not audio_filename:
        flash("Missing job information. Please start over.", "error")
        return redirect(url_for("index"))

    audio_path = FINAL_OUTPUT_DIR / audio_filename
    if not audio_path.exists():
        flash("The generated audio file is no longer available. Please run the conversion again.", "error")
        return redirect(url_for("index"))

    return render_template(
        "result.html",
        audio_filename=audio_filename,
        job_id=job_id,
    )


@app.route("/download/<path:filename>")
def download(filename: str):
    audio_path = FINAL_OUTPUT_DIR / Path(filename).name
    if not audio_path.exists():
        flash("Requested audio file was not found.", "error")
        return redirect(url_for("index"))

    return send_file(audio_path, as_attachment=True)


@app.route("/listen/<path:filename>")
def listen(filename: str):
    audio_path = FINAL_OUTPUT_DIR / Path(filename).name
    if not audio_path.exists():
        flash("Requested audio file was not found.", "error")
        return redirect(url_for("index"))

    return send_file(audio_path, mimetype="audio/mpeg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
