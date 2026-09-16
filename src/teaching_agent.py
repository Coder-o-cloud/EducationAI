import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    """Return an initialized Google GenAI client."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=key)


class TeachingGPT:
    """Controller model for the interactive AI Teaching Agent powered by Gemini."""

    def __init__(
        self,
        syllabus: str = "",
        conversation_topic: str = "",
        conversation_history: Optional[List[str]] = None,
        model_name: Optional[str] = None,
    ):
        self.syllabus = syllabus
        self.conversation_topic = conversation_topic
        self.conversation_history: List[str] = conversation_history or []
        self.model_name = model_name or os.environ.get("MODEL_NAME", _DEFAULT_MODEL)
        self.last_interaction_id: Optional[str] = None
        self.pending_human_input: Optional[str] = None

    def seed_agent(self, syllabus: str, task: str):
        """Seed or re-initialize the conversation with a new syllabus and topic."""
        self.syllabus = syllabus
        self.conversation_topic = task
        self.conversation_history = []
        self.last_interaction_id = None
        self.pending_human_input = None
        print(f"[*] Teaching agent seeded with syllabus for: {task}")

    def human_step(self, human_input: str):
        """Process and record student's input message."""
        cleaned_input = human_input.replace("<END_OF_TURN>", "").strip()
        self.pending_human_input = cleaned_input
        self.conversation_history.append(f"Student: {cleaned_input}")

    def instructor_step(self) -> str:
        """Generate the next instructor reply using Gemini."""
        return self._call_instructor()

    def _build_system_instruction(self) -> str:
        return f"""You are an elite, encouraging, and deeply knowledgeable AI Instructor.
Your goal is to teach the student step-by-step strictly according to the syllabus provided below.

=== COURSE SYLLABUS ===
{self.syllabus}
=== END OF SYLLABUS ===

Topic / Goal: {self.conversation_topic}

Instruction Guidelines:
1. Follow the syllabus step-by-step. Do not jump ahead unless requested by the student.
2. Teach one concept or section at a time. Provide crystal-clear explanations, intuition, code snippets or mathematical formulations when appropriate.
3. Keep your tone supportive, academic, and engaging.
4. Always conclude each explanation with a thought-provoking check question, mini exercise, or asking if the student understands before moving forward.
5. If the student asks for a quiz or code review, provide immediate, constructive feedback.
6. End each response with '<END_OF_TURN>' to signal the student's turn.
"""

    def _get_candidate_models(self) -> list:
        configured = os.environ.get("MODEL_NAME", self.model_name)
        candidates = [configured, "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
        seen = set()
        res = []
        for m in candidates:
            if m and m not in seen:
                seen.add(m)
                res.append(m)
        return res

    def _call_instructor(self) -> str:
        """Call Gemini to get the instructor's response with multi-model fallback."""
        client = get_genai_client()
        candidate_models = self._get_candidate_models()

        student_msg = self.pending_human_input or "Hello! I am ready to start learning based on the syllabus. Please begin Module 1."
        system_instruction = self._build_system_instruction()

        last_error = None

        for model in candidate_models:
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    # If we have an ongoing interaction chain on this model, continue it
                    if self.last_interaction_id:
                        print(f"[*] Continuing interaction chain with {model}: {self.last_interaction_id}")
                        try:
                            interaction = client.interactions.create(
                                model=model,
                                previous_interaction_id=self.last_interaction_id,
                                input=student_msg,
                            )
                        except Exception as chain_err:
                            print(f"[!] Chain continuation failed on {model} ({chain_err}). Starting fresh with history context...")
                            recent_history = "\n".join(self.conversation_history[-6:])
                            augmented_input = f"Conversation context so far:\n{recent_history}\n\nStudent says: {student_msg}"
                            interaction = client.interactions.create(
                                model=model,
                                system_instruction=system_instruction,
                                input=augmented_input,
                            )
                    else:
                        print(f"[*] Starting new teaching interaction with model: {model}")
                        interaction = client.interactions.create(
                            model=model,
                            system_instruction=system_instruction,
                            input=student_msg,
                        )

                    self.last_interaction_id = interaction.id
                    raw_reply = getattr(interaction, "output_text", None) or getattr(interaction, "text", str(interaction))
                    
                    # Clean up formatting
                    reply = raw_reply.strip()
                    if not reply.endswith("<END_OF_TURN>"):
                        reply += " <END_OF_TURN>"

                    self.conversation_history.append(f"Instructor: {reply}")
                    self.pending_human_input = None
                    print(f"[*] Instructor ({model}): {reply[:100]}...")
                    return reply

                except Exception as e:
                    last_error = e
                    err_str = str(e).lower()
                    print(f"[!] Model {model} attempt {attempt + 1} failed: {e}")
                    if "429" in err_str or "rate limit" in err_str or "quota" in err_str:
                        import re
                        match = re.search(r"retry in (\d+(\.\d+)?)s", str(e), re.IGNORECASE)
                        if match:
                            wait_sec = float(match.group(1))
                            if wait_sec <= 5 and attempt < max_retries - 1:
                                print(f"[*] Waiting {wait_sec:.1f}s as suggested by Gemini API...")
                                time.sleep(wait_sec + 0.5)
                                continue
                        print(f"[*] Model {model} quota hit. Cascading to next candidate model...")
                        break
                    else:
                        self.last_interaction_id = None
                        break

        # If all candidate models failed, raise so server.py can provide fallback
        raise last_error


    @classmethod
    def from_llm(cls, *args, **kwargs) -> "TeachingGPT":
        """Compatibility constructor for legacy callers."""
        return cls()


# Global default instance
teaching_agent = TeachingGPT()

