import os
from typing import List

from langchain_openai import ChatOpenAI
try:
    from langchain_core.prompts.chat import (
        HumanMessagePromptTemplate,
        SystemMessagePromptTemplate,
    )
except ImportError:
    from langchain.prompts.chat import (
        HumanMessagePromptTemplate,
        SystemMessagePromptTemplate,
    )

try:
    from langchain_core.messages import (
        AIMessage,
        BaseMessage,
        HumanMessage,
        SystemMessage,
    )
except ImportError:
    from langchain.schema import (
        AIMessage,
        BaseMessage,
        HumanMessage,
        SystemMessage,
    )


# Define a Discuss agent class
class DiscussAgent:
    def __init__(
        self,
        system_message: SystemMessage,
        model: ChatOpenAI,
    ) -> None:
        self.system_message = system_message
        self.model = model
        self.init_messages()

    def reset(self) -> None:
        self.init_messages()
        return self.stored_messages

    def init_messages(self) -> None:
        self.stored_messages = [self.system_message]

    def update_messages(self, message: BaseMessage) -> List[BaseMessage]:
        self.stored_messages.append(message)
        return self.stored_messages

    def step(
        self,
        input_message: HumanMessage,
    ) -> AIMessage:
        messages = self.update_messages(input_message)

        if hasattr(self.model, "invoke"):
            output_message = self.model.invoke(messages)
        else:
            output_message = self.model(messages)
        self.update_messages(output_message)

        return output_message


# import your OpenAI key (put in your .env file)
from pathlib import Path as _Path

_env_path = _Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    with open(_env_path, "r", encoding="utf-8") as f:
        for _line in f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ[_k.strip()] = _v.strip()

# Support Modal Proxy Token ID and Secret if present
if "MODAL_PROXY_TOKEN_ID" in os.environ and "MODAL_PROXY_TOKEN_SECRET" in os.environ:
    os.environ["OPENAI_API_KEY"] = f"{os.environ['MODAL_PROXY_TOKEN_ID']}.{os.environ['MODAL_PROXY_TOKEN_SECRET']}"

# Model configuration from .env (defaults to gpt-3.5-turbo for vanilla OpenAI)
_model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")

def _create_chat_model(temperature: float = 0.7) -> ChatOpenAI:
    kwargs = {"model_name": _model_name, "temperature": temperature}
    session_id = os.environ.get("MODAL_SESSION_ID")
    if session_id:
        kwargs["default_headers"] = {"Modal-Session-ID": session_id}
    if "deepseek" in _model_name.lower():
        kwargs["extra_body"] = {"reasoning_effort": "high"}
    return ChatOpenAI(**kwargs)

# Set up roles
assistant_role_name = "Instructor"
user_role_name = "Teaching Assistant"

word_limit = 50  # word limit for task brainstorming

# Create inception prompts for AI assistant and AI user for role-playing
assistant_inception_prompt = """Never forget you are a {assistant_role_name} and I am a {user_role_name}. Never flip roles! Never instruct me!
We share a common interest in collaborating to successfully complete a task.
You must help me to complete the task.
Here is the task: {task}. Never forget our task!
I must instruct you based on your expertise and my needs to complete the task.

I must give you one instruction at a time.
You must write a specific solution that appropriately completes the requested instruction.
You must decline my instruction honestly if you cannot perform the instruction due to physical, moral, legal reasons or your capability and explain the reasons.
Do not add anything else other than your solution to my instruction.
You are never supposed to ask me any questions you only answer questions.
You are never supposed to reply with a flake solution. Explain your solutions.
Your solution must be declarative sentences and simple present tense.
Unless I say the task is completed, you should always start with:

Solution: <YOUR_SOLUTION>

<YOUR_SOLUTION> should be specific and provide preferable implementations and examples for task-solving.
Always end <YOUR_SOLUTION> with: Next request."""

user_inception_prompt = """Never forget you are a {user_role_name} and I am a {assistant_role_name}. Never flip roles! You will always instruct me.
We share a common interest in collaborating to successfully complete a task.
I must help you to complete the task.
Here is the task: {task}. Never forget our task!
You must instruct me based on my expertise and your needs to complete the task ONLY in the following two ways:

1. Instruct with a necessary input:
Instruction: <YOUR_INSTRUCTION>
Input: <YOUR_INPUT>

2. Instruct without any input:
Instruction: <YOUR_INSTRUCTION>
Input: None

The "Instruction" describes a task or question. The paired "Input" provides further context or information for the requested "Instruction".

You must give me one instruction at a time.
I must write a response that appropriately completes the requested instruction.
I must decline your instruction honestly if I cannot perform the instruction due to physical, moral, legal reasons or my capability and explain the reasons.
You should instruct me not ask me questions.
Now you must start to instruct me using the two ways described above.
Do not add anything else other than your instruction and the optional corresponding input!
Keep giving me instructions and necessary inputs until you think the task is completed.
When the task is completed, you must only reply with a single word <TASK_DONE>.
Never say <TASK_DONE> unless my responses have solved your task."""


# Get message from system
def get_sys_msgs(assistant_role_name: str, user_role_name: str, task: str):
    assistant_sys_template = SystemMessagePromptTemplate.from_template(
        template=assistant_inception_prompt
    )
    assistant_sys_msg = assistant_sys_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
    )[0]

    user_sys_template = SystemMessagePromptTemplate.from_template(
        template=user_inception_prompt
    )
    user_sys_msg = user_sys_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
    )[0]

    return assistant_sys_msg, user_sys_msg


# Create a task specify agent for brainstorming and get the specified task
task_specifier_sys_msg = SystemMessage(
    content="You can make a task more specific."
)
task_specifier_prompt = """Here is a task that {assistant_role_name} will help {user_role_name} to complete: {task}.
Please make it more specific. Be creative and imaginative.
Please reply with the specified task in {word_limit} words or less. Do not add anything else."""
task_specifier_template = HumanMessagePromptTemplate.from_template(
    template=task_specifier_prompt
)


# Function to generating the syllabus
def generate_syllabus(topic, task):
    # Create task specify agent lazily (avoids calling OpenAI at import time)
    task_specify_agent = DiscussAgent(
        task_specifier_sys_msg, _create_chat_model(temperature=1.0)
    )

    # Get the specified task
    task_specifier_msg = task_specifier_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
        word_limit=word_limit,
    )[0]
    specified_task_msg = task_specify_agent.step(task_specifier_msg)
    specified_task = specified_task_msg.content
    assistant_sys_msg, user_sys_msg = get_sys_msgs(
        assistant_role_name, user_role_name, specified_task
    )

    assistant_agent = DiscussAgent(
        assistant_sys_msg, _create_chat_model(temperature=0.2)
    )
    user_agent = DiscussAgent(user_sys_msg, _create_chat_model(temperature=0.2))

    # Reset agents
    assistant_agent.reset()
    user_agent.reset()

    # Initialize chats
    assistant_msg = HumanMessage(
        content=(
            f"{user_sys_msg.content}. "
            "Now start to give me introductions one by one. "
            "Only reply with Instruction and Input."
        )
    )

    user_msg = HumanMessage(content=f"{assistant_sys_msg.content}")
    user_msg = assistant_agent.step(user_msg)

    # print(f"Original task prompt:\n{task}\n")
    print(f"Specified task prompt:\n{specified_task}\n")
    conversation_history = []

    # Start role-playing session to solve the task!
    chat_turn_limit, n = 5, 0
    while n < chat_turn_limit:
        n += 1
        user_ai_msg = user_agent.step(assistant_msg)
        user_msg = HumanMessage(content=user_ai_msg.content)

        print(f"AI User ({user_role_name}):\n\n{user_msg.content}\n\n")
        conversation_history.append("AI User:" + user_msg.content)
        assistant_ai_msg = assistant_agent.step(user_msg)
        assistant_msg = HumanMessage(content=assistant_ai_msg.content)
        conversation_history.append("AI Assistant:" + assistant_msg.content)
        print(
            f"AI Assistant ({assistant_role_name}):\n\n{assistant_msg.content}\n\n"
        )
        if "<TASK_DONE>" in user_msg.content:
            break

    # Summarize the conversation to get the syllabus
    summarizer_sys_msg = SystemMessage(
        content="Summarize this converasion into a {topic} course syllabus form"
    )
    summarizer_prompt = """Here is a comversation history that {assistant_role_name} have disccuss with {user_role_name}: {conversation_history}.
    Please summarize this converasion into a course syllabus form with the topic from user input."""
    summarizer_template = HumanMessagePromptTemplate.from_template(
        template=summarizer_prompt
    )
    summarizer_agent = DiscussAgent(
        summarizer_sys_msg, _create_chat_model(temperature=1.0)
    )
    summarizer_msg = summarizer_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        conversation_history=conversation_history,
    )[0]
    summarizered_msg = summarizer_agent.step(summarizer_msg)
    # print(f"summarizered syllabus: {summarizered_msg.content}")
    return summarizered_msg.content
