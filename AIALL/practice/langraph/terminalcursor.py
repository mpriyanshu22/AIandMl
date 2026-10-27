import os
import subprocess
from typing import Annotated, Sequence
from dotenv import load_dotenv
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Load .env file (GEMINI_API_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST)
load_dotenv()

# Initialize Langfuse
langfuse = Langfuse()
print("Langfuse Authenticated:", langfuse.auth_check())

# The callback that automatically logs LangGraph steps to Langfuse
langfuse_handler = CallbackHandler()

@tool
def read_file(filepath: str) -> str:
    """Read the content of a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

@tool
def write_file(filepath: str, content: str) -> str:
    """Create or overwrite a file with new content."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {e}"

@tool
def list_directory(path: str = ".") -> str:
    """List all files and folders in a directory path."""
    try:
        items = os.listdir(path)
        return "\n".join(items) if items else "Directory is empty."
    except Exception as e:
        return f"Error listing directory: {e}"

@tool
def run_command(command: str) -> str:
    """Execute a shell/terminal command and return its output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=45)
        output = result.stdout.strip()
        errors = result.stderr.strip()
        if errors:
            return f"STDOUT:\n{output}\nSTDERR:\n{errors}"
        return output or "Command ran successfully with no output."
    except Exception as e:
        return f"Command execution failed: {e}"

# Bundle all tools in a list
tools = [read_file, write_file, list_directory, run_command]

# Bind tools to Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.0
).bind_tools(tools)

# Define the State: 'add_messages' appends new messages rather than overwriting old ones
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Worker 1: The AI Brain
def agent_node(state: AgentState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Decision function: Where do we go next?
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    # If the LLM wants to run a tool, go to 'tools', otherwise stop at END
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# Build the Graph
builder = StateGraph(AgentState)

# Add Nodes
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))

# Set entry point
builder.set_entry_point("agent")

# Add edges (paths)
builder.add_conditional_edges(
    "agent", 
    should_continue, 
    {"tools": "tools", END: END}
)
# After running a tool, send the output back to the agent to interpret the result
builder.add_edge("tools", "agent")

# Compile into a runnable application
app = builder.compile()

SYSTEM_PROMPT = (
    "You are MiniCursor, an autonomous coding assistant inside a terminal. "
    "You can inspect files, write code, run commands, and debug errors. "
    "Always check your work and explain what you did briefly."
)

def run_minicursor():
    print("=" * 50)
    print("🚀 MiniCursor Active! (Type 'exit' to quit)")
    print("=" * 50)

    history = [SystemMessage(content=SYSTEM_PROMPT)]

    while True:
        try:
            user_input = input("\n[MiniCursor] > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                langfuse.flush()
                print("Session saved. Exiting.")
                break

            history.append(HumanMessage(content=user_input))

            # Run the LangGraph agent and trace with Langfuse
            result = app.invoke(
                {"messages": history},
                config={"callbacks": [langfuse_handler]}
            )

            # Update conversation history with all intermediate node outputs
            history = result["messages"]
            
            # Print the final output from the assistant
            print(f"\n{history[-1].content}")

            # Send traces to Langfuse dashboard in real time
            langfuse.flush()

        except KeyboardInterrupt:
            langfuse.flush()
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[Error]: {e}")

if __name__ == "__main__":
    run_minicursor()