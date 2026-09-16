import os
import time
from pathlib import Path
from typing import Optional

from google import genai

# Load environment variables safely
_BASE_DIR = Path(__file__).resolve().parent.parent
_env_path = _BASE_DIR / ".env"
if _env_path.exists():
    with open(_env_path, "r", encoding="utf-8") as f:
        for _line in f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ[_k.strip()] = _v.strip()

_DEFAULT_MODEL = "gemini-3.8-flash"


def get_genai_client(api_key: Optional[str] = None) -> genai.Client:
    """Instantiate and return the Google GenAI client."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY is not set. Please configure it in .env or Settings.")
    return genai.Client(api_key=key)


def build_fallback_syllabus(topic: str) -> str:
    """Rich structured fallback syllabus if network or rate limit is reached."""
    return f"""# Comprehensive Course Syllabus: {topic}

> *Curriculum generated for **{topic}**. Switch to the Classroom tab to begin your step-by-step interactive lessons!*

---

## Course Overview & Objectives
This intensive course is designed to guide you from foundational principles to production-grade mastery of **{topic}**. 
By the end of this curriculum, you will understand the theoretical architecture, practical implementation patterns, and industry best practices.

---

## Module 1: Core Fundamentals & Theoretical Foundations
- **Primary Objective:** Master the essential terminology, mental models, and foundational building blocks of {topic}.
- **Key Concepts Covered:**
  - 1.1 Introduction, Domain Overview & Mental Models
  - 1.2 Syntax, Structural Mechanics & Core Tooling Setup
  - 1.3 State Representation, Primitive Types & Execution Flow
  - 1.4 Idiomatic Patterns, Modularity & Clean Code
- **Practical Checkpoint:** Construct an interactive, self-contained demonstration implementing core concepts.

---

## Module 2: Intermediate Deep Dive & Practical Implementations
- **Primary Objective:** Build resilience, manage complexity, and implement real-world application paradigms.
- **Key Concepts Covered:**
  - 2.1 Concurrency, Asynchronous Execution & Event-Driven Patterns
  - 2.2 Advanced Design Patterns, Abstractions & Composition
  - 2.3 Comprehensive Defensive Error Handling & Diagnostics
  - 2.4 Ecosystem Tooling, Automated Testing Suites & Performance Optimization
- **Practical Checkpoint:** Implement an end-to-end service with robust error handling and test suites.

---

## Module 3: Advanced Architectures & Production Mastery
- **Primary Objective:** Transition from practitioner to system architect with scalability, efficiency, and security.
- **Key Concepts Covered:**
  - 3.1 Distributed Systems Integration, Microservices & High-Throughput Pipelines
  - 3.2 Security Hardening, Authentication & Operational Guardrails
  - 3.3 Profiling, Memory Optimization & Benchmarking Under Load
  - 3.4 CI/CD Deployment Strategies, Containerization & Production Observability
- **Final Capstone Project:** Deliver a production-grade, architecturally sound solution with documentation and automated benchmarks.

---

## Recommended Learning Path:
1. Review Module 1 in depth and experiment with code snippets.
2. Engage with your **Interactive AI Instructor** in the Classroom tab for line-by-line code walk-throughs.
3. Test your knowledge regularly with interactive quizzes!
"""


def get_candidate_models() -> list:
    """Return ordered list of Gemini models to attempt."""
    configured = os.environ.get("MODEL_NAME", "gemini-3.6-flash")
    candidates = [configured, "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
    seen = set()
    res = []
    for m in candidates:
        if m and m not in seen:
            seen.add(m)
            res.append(m)
    return res


def generate_syllabus(topic: str, task: Optional[str] = None, api_key: Optional[str] = None) -> str:
    """Generate a comprehensive course syllabus for a given topic using Google Gemini."""
    client = get_genai_client(api_key=api_key)
    candidate_models = get_candidate_models()

    prompt = f"""You are an elite academic curriculum designer and expert instructor.
Create a comprehensive, production-ready, beautifully structured course syllabus to teach the topic: {topic}.

Task context: {task or f"Generate a comprehensive course syllabus to teach: {topic}"}

Your syllabus MUST include the following sections formatted in clean, professional GitHub-flavored Markdown:
1. # Course Title: [Topic] (with a brief executive summary and target audience)
2. ## Prerequisites & Tooling Setup
3. ## Module 1: Foundational Principles & Architecture (detailed lessons, key concepts, formulas/theories if applicable, checkpoint exercise)
4. ## Module 2: Practical Implementation & Intermediate Deep Dive (hands-on patterns, defensive error handling, test strategies)
5. ## Module 3: Advanced Architectures, Scalability & Production Mastery (enterprise patterns, optimization, security)
6. ## Hands-on Milestone & Capstone Projects
7. ## Step-by-Step Learning Roadmap & Recommended Pace

Ensure the explanation is clear, encouraging, structured, and includes practical code examples or architectural diagrams where helpful. Do not output anything other than the markdown syllabus."""

    last_err = None

    for model_name in candidate_models:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                print(f"[*] Generating syllabus for '{topic}' with model '{model_name}' (attempt {attempt + 1}/{max_retries})...")
                interaction = client.interactions.create(
                    model=model_name,
                    input=prompt,
                )
                output = getattr(interaction, "output_text", None)
                if output and output.strip():
                    print(f"[*] Successfully generated syllabus with {model_name}!")
                    return output.strip()
                if hasattr(interaction, "text") and interaction.text:
                    return interaction.text.strip()
                return str(interaction).strip()
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                print(f"[!] Model {model_name} attempt {attempt + 1} failed: {e}")
                if "429" in err_str or "rate limit" in err_str or "quota" in err_str:
                    import re
                    match = re.search(r"retry in (\d+(\.\d+)?)s", str(e), re.IGNORECASE)
                    if match:
                        wait_sec = float(match.group(1))
                        if wait_sec <= 6 and attempt < max_retries - 1:
                            print(f"[*] Waiting {wait_sec:.1f}s as suggested by Gemini API...")
                            time.sleep(wait_sec + 0.5)
                            continue
                    # Otherwise immediately switch to next model in candidate_models!
                    print(f"[*] Model {model_name} quota hit. Cascading to next available model...")
                    break
                else:
                    break

    print(f"[!] All candidate models failed. Last error: {last_err}. Raising to caller.")
    raise last_err


