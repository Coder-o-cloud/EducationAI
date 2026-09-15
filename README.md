# 📖 EduGPT - Your AI Instructor

EduGPT is an intelligent, multi-agent AI Instructor built using Large Language Models (LLMs) and [LangChain](https://github.com/hwchase17/langchain), inspired by the [CAMEL](https://github.com/camel-ai/camel) (Communicative Agents for "Mind" Exploration) architecture.

Instead of generic single-prompt responses, EduGPT employs **role-playing AI agents** that collaboratively debate and design a customized, structured syllabus for any topic you want to learn, and then assigns a dedicated **Instructor Agent** to guide and teach you step-by-step in an interactive web classroom.

---

## ⚡ Quick Start (Run Instantly)

If this repository already has the `venv` folder set up, you can launch the web application in **one step**:

### On Windows:
```powershell
.\venv\Scripts\python.exe src/server.py
```

### On Linux / macOS:
```bash
./venv/bin/python src/server.py
```

Now open your web browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

*(Make sure your `.env` file contains your `OPENAI_API_KEY` before running)*

---

## 🏗️ Architecture

![Architecture Diagram](diagram.png)

The workflow consists of four core phases:
1. **Goal Specification**: The user enters a topic they want to master (e.g., *"Deep Reinforcement Learning"* or *"Microservices System Design"*).
2. **Collaborative Discussion (CAMEL Framework)**: Two role-playing AI agents (an Assistant agent and an Instructor/User role agent) engage in an iterative dialogue to brainstorm, structure, and refine concepts into a logical sequence.
3. **Syllabus Synthesis**: A Summarizer agent processes the dialogue history and produces an organized, coherent, step-by-step syllabus.
4. **Interactive Instruction**: The generated syllabus is loaded into a dedicated **Teaching Agent** that guides the student through each module via an interactive web interface.

---

## ✨ Key Features

- 🤖 **Multi-Agent Collaborative Design**: Two role-playing agents debate topic depth, prerequisites, and milestone sequencing.
- 🎨 **Product-Ready Web UI**: Built with pure **HTML5, Modern CSS3, and JavaScript (ES6+)** featuring a dark obsidian theme, glassmorphism, responsive design, and micro-animations.
- 💬 **Interactive Classroom**: Split-view arena with a live course checklist on the left and a real-time markdown chat with the AI Instructor on the right.
- ⚡ **FastAPI High-Performance Backend**: Non-blocking asynchronous Python backend directly interfacing with LangChain agents.
- ⌨️ **IME-Safe Chat**: Robust keyboard handling for international keyboard users and smooth Enter-to-send / Shift+Enter for newlines.
- 📋 **Export & Persistence**: One-click Markdown copy, `.md` file download, and browser `localStorage` persistence.
- 📓 **Jupyter Notebook Support**: Includes `src/EduGPT.ipynb` for step-by-step experimentation and agent inspection.

---

## 🔑 Environment Configuration (`.env`)

Before running, create a `.env` file in the **project root directory** (`EduGPT/`).

### Standard OpenAI API Key:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Modal / OpenAI-Compatible Bearer Token:
```env
OPENAI_API_KEY=wk-cinRWwgU4gH1fo2YbsVC9q.ws-DtsekCD5FAxHfvJ4eBJRXr
MODAL_TOKEN_ID=wk-cinRWwgU4gH1fo2YbsVC9q
MODAL_TOKEN_SECRET=ws-DtsekCD5FAxHfvJ4eBJRXr
```

> ⚠️ **Important `.env` Rules:**
> - Every line must strictly follow `KEY=VALUE`.
> - Do **not** leave blank lines or comments without an `=` sign at the end of the file.
> - The `.env` file is already listed in `.gitignore`, ensuring your keys are never committed to GitHub.

---

## 💻 How to Run the Application

### Option 1: Product-Ready Web App (Recommended)

This is the full-featured, modern interface built with HTML, CSS, JavaScript, and FastAPI.

```powershell
# Method A: Direct run via venv Python (Recommended - No activation needed)
.\venv\Scripts\python.exe src/server.py

# Method B: Activate venv first, then run
.\venv\Scripts\Activate.ps1
python src/server.py
```

Open your browser at: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

#### 🎮 Using the Web App:
1. **Course Studio View**:
   - Type any topic in the search box (or click quick chips like *Machine Learning*, *System Design*, *Fullstack Web*).
   - Click **Generate Syllabus**.
   - Watch the animated 3-stage agent debate visualizer.
   - Once generated, review the course plan, copy the Markdown, or export as `.md`.
2. **Interactive Classroom View**:
   - Click **Start Learning in Classroom**.
   - Your course modules will appear in the left sidebar with completion checkboxes and a progress bar.
   - Chat with your dedicated AI Instructor in the main arena. Click prompt chips (*"Start Module 1"*, *"Real-World Example"*, *"Quiz Me"*, *"Summarize"*) or ask any custom question!

---

### Option 2: Classic Gradio Prototype

If you want to run the original Gradio interface:

```powershell
.\venv\Scripts\python.exe src/run.py
```

- **Local URL**: `http://127.0.0.1:7860`
- **Public Shareable URL**: Temporary `https://....gradio.live` link.

---

### Option 3: Jupyter Notebook

If you prefer exploring the CAMEL agents and prompts interactively in Jupyter cells:

```powershell
.\venv\Scripts\pip.exe install notebook
.\venv\Scripts\python.exe -m notebook src/EduGPT.ipynb
```

---

## 🛠️ First-Time Setup (Only If Starting From Scratch on a New PC)

> [!NOTE]
> If a `venv` folder already exists in this directory, **do NOT re-create it**! Re-creating an active virtual environment causes a `Permission denied` error. Follow the [⚡ Quick Start](#-quick-start-run-instantly) section instead.

If you are setting up this repository on a fresh computer:

### 1. Clone the Repository
```bash
git clone https://github.com/hqanhh/EduGPT.git
cd EduGPT
```

### 2. Create Virtual Environment
- **Windows (PowerShell/CMD):**
  ```powershell
  python -m venv venv
  ```
- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  ```

### 3. Activate Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(If you get a script execution policy error, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` and retry)*
- **Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔌 REST API Endpoints

The FastAPI backend (`src/server.py`) exposes clean REST endpoints:

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/` | `GET` | Serves the HTML5/CSS3/JavaScript single-page application |
| `/api/status` | `GET` | Returns system health, API key configuration status, and active topic |
| `/api/generate-syllabus` | `POST` | Triggers multi-agent CAMEL debate to generate a syllabus for `{ "topic": "..." }` |
| `/api/chat` | `POST` | Interacts with the AI Teaching Agent for `{ "message": "..." }` |
| `/api/reset` | `POST` | Clears instructor conversation history and resets active session |
| `/api/settings` | `POST` | Updates and persists API key in `.env` |

---

## 📂 Project Structure

```text
EduGPT/
├── .env                       # Environment variables (API keys - gitignored)
├── .gitignore                 # Git ignore rules
├── LICENSE                    # MIT License
├── Makefile                   # Setup automation for Linux/macOS
├── README.md                  # Project documentation
├── diagram.png                # CAMEL architecture diagram
├── pyproject.toml             # Code formatting configuration
├── requirements.txt           # Python dependencies (pinned for compatibility)
├── setup.py                   # Package setup script
├── src/
│   ├── EduGPT.ipynb           # Interactive exploration notebook
│   ├── generating_syllabus.py # CAMEL multi-agent syllabus generation logic
│   ├── run.py                 # Legacy Gradio entrypoint
│   ├── server.py              # FastAPI server & REST API
│   └── teaching_agent.py      # LangChain teaching instructor agent
└── static/
    ├── app.js                 # Frontend JavaScript (state, chat, Markdown parser)
    ├── index.html             # Semantic HTML5 single-page application
    └── style.css              # Custom CSS (dark mode, glassmorphism, responsive)
```

---

## ❓ Frequently Asked Questions & Troubleshooting

#### 1. `Error: [Errno 13] Permission denied: '...venv\Scripts\python.exe'`
- **Reason:** A Python process is already using `python.exe`, or OneDrive is syncing files.
- **Solution:** You do not need to re-run `python -m venv venv` because `venv` is already created. Run the app directly with:
  ```powershell
  .\venv\Scripts\python.exe src/server.py
  ```

#### 2. `cannot be loaded because running scripts is disabled on this system`
- **Reason:** Windows PowerShell script execution policy restricts unapproved scripts.
- **Solution:** Run this command once in PowerShell:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
  .\venv\Scripts\Activate.ps1
  ```

#### 3. `ImportError: cannot import name 'ChatOpenAI' from 'langchain.chat_models'`
- **Reason:** Running outside of the virtual environment with an incompatible LangChain version installed globally.
- **Solution:** Always run using the `venv` Python:
  ```powershell
  .\venv\Scripts\python.exe src/server.py
  ```

#### 4. `ValueError: not enough values to unpack (expected 2, got 1)`
- **Reason:** Trailing empty lines in `.env`.
- **Solution:** Open `.env` and remove any empty lines. Every line must be `KEY=VALUE`.

#### 5. `ERROR: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)`
- **Reason:** Port 8000 is already in use by an existing server process.
- **Solution:** Stop the existing process, or kill all active Python instances in PowerShell:
  ```powershell
  Stop-Process -Name python -Force -ErrorAction SilentlyContinue
  .\venv\Scripts\python.exe src/server.py
  ```

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome! Feel free to open an issue or submit a pull request.

---

## 📬 Contact

For questions or inquiries:
- Author: **hqanhh**
- Email: [huynhquynhanh2003@gmail.com](mailto:huynhquynhanh2003@gmail.com)#   E d u c a t i o n A I  
 