# 🎓 Lecture Synthesizer — Web Frontend

This project converts **handwritten or printed lecture notes** into spoken audio lectures using an AI-powered pipeline:

- **OCR**: CRAFT + TrOCR (extracts text from images or PDFs)  
- **LLM**: Ollama (llama3:8b) to generate a natural lecture script  
- **TTS**: ElevenLabs to produce high-quality narration audio  

The tool runs as a **simple web application** so you can upload notes and directly download the generated audio from your browser.

⚠️ **Access Requirement:**  
You must be connected to the **MWN network (eduVPN)** to SSH into the server.  
Use the provided credentials to log in.

---

## 🚀 Running the Frontend on the Server

⚠️ **Important:** You must use **two separate SSH sessions (two terminals)**:  
one for running **Ollama** and one for running the **Flask web frontend**.

### 1. Start Ollama (first SSH session)
```bash
ssh abderrahmen@10.152.225.210
# Enter the password (shared privately)
cd ~/lecture-synthesizer
ollama serve
```
Leave this running.

### 2. Start the Web Frontend (second SSH session)
```bash
ssh abderrahmen@10.152.225.210
# Enter the password (shared privately)
cd ~/lecture-synthesizer
source .venv_frontend/bin/activate
python webapp/app.py
```

By default, the frontend will run on port **5000**.  

### 3. Open in your local browser
```
http://10.152.225.210:5000
```

---

## 🌐 Using the App

1. Upload a **PDF (1 page)** or an **image** of your lecture notes.  
2. Wait while the pipeline processes it step by step:  
   - OCR → LLM → TTS  
3. Once finished:  
   - ✅ Listen to the audio in the browser  
   - 💾 Download the MP3 file  

---

## 📂 Output Files (saved on the server)

- **Audio files:** `Final_Output/`  
- **Generated lecture transcripts:** `step_outputs/llm_outputs/`  

