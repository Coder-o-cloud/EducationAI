import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure project root and src directory are on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Load .env safely
env_file = BASE_DIR / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip("'\" ")] = val.strip("'\" \r\n")

# Import Gemini agents
try:
    from generating_syllabus import generate_syllabus, build_fallback_syllabus
    from teaching_agent import teaching_agent
except Exception as e:
    print(f"Notice: Agent module loaded with warnings: {e}")
    generate_syllabus = None
    teaching_agent = None


app = FastAPI(
    title="EduGPT AI Instructor API",
    description="Multi-agent syllabus generation and interactive instructor API",
    version="1.1.0",
)

# Enable CORS for local web development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session tracking
current_session = {
    "topic": "",
    "syllabus": "",
    "syllabus_ready": False,
    "total_messages": 0,
    "demo_mode": False,
}


class SyllabusRequest(BaseModel):
    topic: str
    force_demo: Optional[bool] = False


class ChatRequest(BaseModel):
    message: str


class SettingsUpdateRequest(BaseModel):
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    demo_mode: Optional[bool] = False



def build_fallback_syllabus(topic: str) -> str:
    """Intelligent curriculum generator for offline/demo testing or key fallbacks."""
    return f"""# Comprehensive Syllabus: {topic}

> *Interactive Curriculum generated for **{topic}**. Switch to the Classroom tab to begin your step-by-step interactive lessons!*

---

### Module 1: Core Fundamentals & Architectural Foundations
- **Primary Objective:** Master the foundational principles, vocabulary, and conceptual building blocks of {topic}.
- **Key Concepts Covered:**
  - 1.1 Introduction, Domain Overview & Mental Models
  - 1.2 Syntax, Structural Mechanics & Core Tooling Setup
  - 1.3 Primitive Data Types, State Representation & Execution Flow
  - 1.4 Idiomatic Patterns, Clean Code & Modularity
- **Practical Checkpoint:** Construct an interactive, self-contained demonstration implementing core concepts.

---

### Module 2: Intermediate Deep Dive & Practical Implementations
- **Primary Objective:** Build resilience, handle complexity, and understand real-world application paradigms.
- **Key Concepts Covered:**
  - 2.1 Concurrency, Asynchronous Execution & Event-Driven Patterns
  - 2.2 Advanced Design Patterns, Abstractions & Composition
  - 2.3 Comprehensive Error Handling, Edge Cases & Diagnostics
  - 2.4 Ecosystem Tooling, Testing Suites & Performance Optimization
- **Practical Checkpoint:** Implement an end-to-end service with defensive error handling and unit test suites.

---

### Module 3: Advanced Architectures & Production Mastery
- **Primary Objective:** Transition from practitioner to system architect with scalability and security.
- **Key Concepts Covered:**
  - 3.1 Distributed Systems Integration, Microservices & High-Throughput Pipelines
  - 3.2 Security Hardening, Authentication & Operational Guardrails
  - 3.3 Profiling, Memory Optimization & Benchmarking Under Load
  - 3.4 CI/CD Deployment Strategies, Containerization & Production Observability
- **Final Capstone:** Deliver a production-grade, architecturally sound solution with documentation and automated benchmarks.

---

### Recommended Learning Path:
- Proceed module by module in the **Interactive Classroom**.
- Ask your instructor for code demonstrations, architectural diagrams, or quizzes at any time!
"""


def build_fallback_instructor_reply(message: str, topic: str) -> str:
    """Intelligent simulated instructor reply for interactive demo learning."""
    msg_lower = message.lower()
    t = topic or "your selected topic"

    if "quiz" in msg_lower or "test" in msg_lower:
        return f"""### Practice Quiz for {t}:

Here are three quick diagnostic questions to test your current understanding:

1. **Question 1:** What is the primary conceptual trade-off when implementing the core architecture of {t}?
2. **Question 2:** In a high-concurrency or production scenario, what is the most common failure mode or bottleneck in {t}, and how do you mitigate it?
3. **Question 3:** How does {t} compare with alternative paradigms in modern software engineering?

*Take a moment to answer any or all of these, and I will evaluate your responses with detailed feedback!*"""

    elif "module 1" in msg_lower or "start" in msg_lower or "begin" in msg_lower:
        return f"""### Welcome to Module 1: Core Fundamentals of {t}!

Let's establish a strong foundation. 

#### 1. The Core Philosophy
When working with **{t}**, our primary goal is to understand how data and logic flow through the system:
- **Foundational Abstraction:** Everything begins with clean mental models and predictable state transitions.
- **Best Practice:** Always write self-documenting, modular components before attempting complex optimizations.

#### 2. Hands-on Conceptual Exercise:
Think of {t} as a pipeline: inputs are validated, transformed according to business rules, and dispatched to their target state.

Would you like me to walk through a concrete **code example**, or would you like to explore the theoretical mechanics first?"""

    elif "example" in msg_lower or "code" in msg_lower:
        class_name = t.replace(' ', '').replace('&', '') + "Controller"
        code_block = f"""# Idiomatic implementation pattern for {t}
class {class_name}:
    def __init__(self, name: str, debug: bool = True):
        self.name = name
        self.debug = debug
        self._state = "INITIALIZED"

    def execute_pipeline(self, payload: dict) -> dict:
        \"\"\"Process workload with defensive validation.\"\"\"
        if not payload:
            raise ValueError("Payload cannot be empty")
            
        print(f"[{{self.name}}] Processing step for: {{list(payload.keys())}}")
        self._state = "COMPLETED"
        return {{"status": "success", "processed_payload": payload}}

# Execution
controller = {class_name}("EduDemoEngine")
result = controller.execute_pipeline({{"topic": "{t}", "level": "advanced"}})
print(result)"""

        return f"""### Practical Implementation Example for {t}

Here is an idiomatic demonstration showcasing core conventions:

```python
{code_block}
```

Notice the defensive check and clean state tracking. Would you like to build on this structure?"""


    elif "summar" in msg_lower:
        return f"""### Key Takeaways for {t}:

1. **Hierarchy of Concepts:** Master fundamental mechanics first before scaling up.
2. **Defensive Design:** Always validate contracts, sanitize inputs, and plan for edge-case errors.
3. **Continuous Practice:** Active questioning and checkpoint project builds are the fastest way to achieve fluency.

What would you like to explore next in our syllabus?"""

    else:
        return f"""### Instructor Response ({t}):

Regarding: *"{message}"*

In the context of **{t}**, this is an important area to consider. 

- **Core Insight:** It directly connects back to our architectural syllabus roadmap. Understanding how this fits into the broader ecosystem helps prevent fragile implementations down the road.
- **Next Step:** We can either break this concept down into simpler building blocks, or look at how industry leaders handle this at scale.

Which direction would best assist your learning right now?"""



@app.get("/api/status")
def get_status():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    model_name = os.environ.get("MODEL_NAME", "gemini-3.8-flash")

    masked_key = ""
    if api_key:
        masked_key = (
            api_key[:6] + "..." + api_key[-4:]
            if len(api_key) > 10
            else "configured"
        )

    return {
        "status": "online",
        "provider": "google-gemini",
        "model_name": model_name,
        "api_key_configured": bool(api_key and not api_key.startswith("your_")),
        "api_key_masked": masked_key,
        "demo_mode": current_session["demo_mode"],
        "active_topic": current_session["topic"],
        "syllabus_ready": current_session["syllabus_ready"],
        "total_messages": current_session["total_messages"],
    }


@app.post("/api/settings")
def update_settings(payload: SettingsUpdateRequest):
    env_updates = {}
    if payload.api_key is not None:
        os.environ["GEMINI_API_KEY"] = payload.api_key
        env_updates["GEMINI_API_KEY"] = payload.api_key

    if payload.model_name is not None:
        os.environ["MODEL_NAME"] = payload.model_name
        env_updates["MODEL_NAME"] = payload.model_name

    if payload.demo_mode is not None:
        current_session["demo_mode"] = payload.demo_mode

    # Update .env file
    if env_updates:
        try:
            env_file = BASE_DIR / ".env"
            lines = []
            if env_file.exists():
                with open(env_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            
            existing_keys = set()
            new_lines = []
            for line in lines:
                matched = False
                for k, v in env_updates.items():
                    if line.startswith(f"{k}="):
                        new_lines.append(f"{k}={v}\n")
                        existing_keys.add(k)
                        matched = True
                        break
                if not matched:
                    new_lines.append(line)
            
            for k, v in env_updates.items():
                if k not in existing_keys:
                    new_lines.append(f"{k}={v}\n")
                    
            with open(env_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        except Exception as e:
            print(f"Failed to update .env: {e}")

    return {"status": "success", "message": "Settings updated successfully"}


@app.post("/api/generate-syllabus")
async def api_generate_syllabus(payload: SyllabusRequest):
    topic = payload.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    api_key = os.environ.get("GEMINI_API_KEY", "")

    # If demo mode is forced:
    if payload.force_demo or current_session["demo_mode"]:
        syllabus = build_fallback_syllabus(topic)
        current_session["topic"] = topic
        current_session["syllabus"] = syllabus
        current_session["syllabus_ready"] = True
        current_session["total_messages"] = 0
        current_session["demo_mode"] = True

        return {
            "status": "success",
            "topic": topic,
            "syllabus": syllabus,
            "demo_mode": True,
            "notice": "Demo Mode active. Generated curriculum using EduGPT Intelligent Engine.",
        }

    if not api_key or api_key.startswith("your_"):
        raise HTTPException(
            status_code=400,
            detail="Gemini API key is missing. Please provide a valid key in Settings or enable Demo Mode.",
        )

    task = f"Generate a comprehensive course syllabus to teach the topic: {topic}"

    def run_sync_generation():
        if generate_syllabus is None:
            raise RuntimeError("Gemini syllabus generator could not be loaded.")
        return generate_syllabus(topic, task)

    try:
        # Run blocking Gemini call in background thread
        syllabus = await asyncio.to_thread(run_sync_generation)

        # Seed the teaching agent
        if teaching_agent is not None:
            teaching_agent.seed_agent(syllabus, task)

        current_session["topic"] = topic
        current_session["syllabus"] = syllabus
        current_session["syllabus_ready"] = True
        current_session["total_messages"] = 0
        current_session["demo_mode"] = False

        return {
            "status": "success",
            "topic": topic,
            "syllabus": syllabus,
            "demo_mode": False,
        }
    except Exception as e:
        error_msg = str(e)
        error_lower = error_msg.lower()
        print(f"Error generating syllabus with Gemini: {error_msg}")
        
        auth_and_quota_keywords = [
            "429", "quota", "rate limit", "ratelimit", "too_many_requests",
            "api_key_invalid", "invalid_argument", "401", "unauthorized",
            "resource_exhausted", "not_found",
        ]
        is_recoverable = any(kw in error_lower for kw in auth_and_quota_keywords)

        if is_recoverable:
            print("Gemini quota or rate limit issue. Falling back to EduGPT curriculum engine...")
            syllabus = build_fallback_syllabus(topic)
            if teaching_agent is not None:
                teaching_agent.seed_agent(syllabus, task)
            current_session["topic"] = topic
            current_session["syllabus"] = syllabus
            current_session["syllabus_ready"] = True
            current_session["total_messages"] = 0
            current_session["demo_mode"] = False

            reason = "Free tier quota limit (429)" if ("429" in error_lower or "quota" in error_lower) else "Gemini notice"
            return {
                "status": "success",
                "topic": topic,
                "syllabus": syllabus,
                "demo_mode": False,
                "notice": f"{reason}. Generated curriculum via EduGPT Curriculum Engine. You can proceed to the Classroom tab for live lessons!",
            }

        raise HTTPException(
            status_code=500,
            detail=f"Syllabus generation failed: {error_msg}",
        )


@app.post("/api/chat")
async def api_chat(payload: ChatRequest):
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if not current_session["syllabus_ready"]:
        raise HTTPException(
            status_code=400,
            detail="No active syllabus found. Please design a syllabus in Course Studio first.",
        )

    # Only force simulated reply if demo_mode was explicitly requested in settings
    if current_session.get("force_demo", False):
        await asyncio.sleep(0.6)  # Natural conversational pacing
        reply = build_fallback_instructor_reply(message, current_session["topic"])
        current_session["total_messages"] += 2
        return {"status": "success", "reply": reply}

    def run_sync_step():
        if teaching_agent is None:
            raise RuntimeError("Teaching agent is not initialized.")
        teaching_agent.human_step(message)
        reply = teaching_agent.instructor_step()
        cleaned = reply.replace("<END_OF_TURN>", "").strip()
        return cleaned

    try:
        reply = await asyncio.to_thread(run_sync_step)
        current_session["total_messages"] += 2
        return {"status": "success", "reply": reply}
    except Exception as e:
        error_msg = str(e)
        error_lower = error_msg.lower()
        print(f"Error during Gemini instructor chat: {error_msg}")

        auth_and_quota_keywords = [
            "429", "quota", "rate limit", "ratelimit", "too_many_requests",
            "api_key_invalid", "401", "unauthorized", "resource_exhausted",
        ]
        is_recoverable = any(kw in error_lower for kw in auth_and_quota_keywords)

        if is_recoverable:
            # Fallback for this single turn only without locking future chat turns
            reply = build_fallback_instructor_reply(message, current_session["topic"])
            current_session["total_messages"] += 2
            return {"status": "success", "reply": reply}

        raise HTTPException(
            status_code=500,
            detail=f"Instructor response failed: {error_msg}",
        )



@app.post("/api/reset")
def api_reset():
    if teaching_agent is not None:
        teaching_agent.conversation_history = []
        teaching_agent.last_interaction_id = None
        teaching_agent.pending_human_input = None
    current_session["total_messages"] = 0
    return {"status": "success", "message": "Chat conversation reset"}



# Serve static web assets
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "message": "EduGPT Backend is running. Frontend index.html not yet found."
    }


if __name__ == "__main__":
    import uvicorn

    print("[*] Starting EduGPT Web Application on http://127.0.0.1:8000 ...")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True, app_dir=str(SRC_DIR))
