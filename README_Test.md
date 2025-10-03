# Lecture Synthesizer — Server Usage Guide

# Use this Readme to test with the console each TTS model seperately

This tool turns handwritten or printed notes into spoken lectures using:
1. **OCR** (CRAFT + TrOCR)  
2. **LLM** (Ollama `llama3:8b`)  
3. **TTS** (`chatterbox`, `elevenlabs_v2`, `dia`)

Everything is pre-configured on the server:  
`abderrahmen@10.152.225.210`

---

## ⚠️ Authentication

- Each time you use `ssh` or `scp`, the **server password** will be requested.  
- The password is shared privately.

---

## 🔄 Workflow Overview

1. Upload your input document (PDF or image) to the server  
2. Run `main.py` to generate lecture text + audio  
3. Copy back only your results  

---

## 📤 Step 1. Upload a Document

**Supported formats:**  
`.pdf, .png, .jpg, .jpeg, .bmp, .gif, .tiff, .webp`

From your laptop:

scp /path/to/lecture_notes.png abderrahmen@10.152.225.210:~/lecture-synthesizer/OCR_test_documents/

You now pass this path as input: --input OCR_test_documents/lecture_notes.png

## 🖥️ Step 2. Generate the Lecture
SSH into the server:
ssh abderrahmen@10.152.225.210
cd ~/lecture-synthesizer
source .venv_main/bin/activate

Run with your file (choose a TTS engine):
python main.py --input OCR_test_documents/lecture_notes.png --tts chatterbox
python main.py --input OCR_test_documents/lecture_notes.png --tts elevenlabs_v2
python main.py --input OCR_test_documents/lecture_notes.png --tts dia

## 📥 Step 3. Copy Back Your Output
Output names are based on your input filename (BASE = filename without extension).

Audio files:
Final_Output/{BASE}_chatterbox.wav
Final_Output/{BASE}_elevenlabs_v2.mp3
Final_Output/{BASE}_dia.wav
(only elevenlabs output is .mp3)

Lecture text:
step_outputs/llm_outputs/{BASE}_llama3-8b_{TTS}.txt

From your laptop:
mkdir -p ~/Lecture_outputs
BASE=lecture_notes

# Example: chatterbox
scp abderrahmen@10.152.225.210:~/lecture-synthesizer/Final_Output/${BASE}_chatterbox.wav ~/Lecture_outputs/
scp abderrahmen@10.152.225.210:~/lecture-synthesizer/step_outputs/llm_outputs/${BASE}_llama3-8b_chatterbox.txt ~/Lecture_outputs/
Only files matching your input are copied.

📝 Example Workflow
# Upload input (from local WSL/laptop)
scp ~/Desktop/lecture_notes.png abderrahmen@10.152.225.210:~/lecture-synthesizer/OCR_test_documents/

# Run on server (on remote SSH server)
ssh abderrahmen@10.152.225.210
cd ~/lecture-synthesizer
source .venv_main/bin/activate
python main.py --input OCR_test_documents/lecture_notes.png --tts chatterbox

# Copy back results (from local WSL/laptop)
scp abderrahmen@10.152.225.210:~/lecture-synthesizer/Final_Output/lecture_notes_chatterbox.wav ~/Lecture_outputs/
scp abderrahmen@10.152.225.210:~/lecture-synthesizer/step_outputs/llm_outputs/lecture_notes_llama3-8b_chatterbox.txt ~/Lecture_outputs/