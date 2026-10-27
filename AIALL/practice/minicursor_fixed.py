import os
import json
import shutil
import subprocess
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Initialize the official Gemini Client
# Make sure GEMINI_API_KEY is set in your .env file
client = genai.Client()

# ----------------------------------------------------------------------
# 1. DEFINE CORE SYSTEM TOOLS
# ----------------------------------------------------------------------

def execute_command(command: str) -> str:
    """
    Executes a terminal or PowerShell command safely on the host system 
    and returns the standard output or error.
    """
    print(f"💻 [Tool Executing]: {command}")
    command = command.strip()
    try:
        powershell_path = shutil.which("powershell")
        if powershell_path:
            exec_args = [powershell_path, "-Command", command]
        else:
            exec_args = command
            
        use_shell = False if powershell_path else True
        
        result = subprocess.run(
            exec_args, 
            shell=use_shell, 
            capture_output=True, 
            text=True,
            timeout=30 # Prevent hanging commands
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            return output if output else "Success: Command executed with no visual output."
        else:
            error_msg = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
            return f"Command Failed! Error: {error_msg}"
            
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Exception occurred while running command: {str(e)}"


def write_file(filepath: str, content: str) -> str:
    """
    Creates or overwrites a file at the specified filepath with the given content string.
    """
    print(f"📝 [Tool Writing File]: {filepath}")
    try:
        # Create directory structure if it doesn't exist
        dirname = os.path.dirname(filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Success: File successfully written at '{filepath}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"


def read_file(filepath: str) -> str:
    """
    Reads and returns the contents of a file at the specified filepath.
    """
    print(f"📖 [Tool Reading File]: {filepath}")
    try:
        if not os.path.exists(filepath):
            return f"Error: File '{filepath}' does not exist."
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Map string names to actual function objects for local execution mapping
tools_map = {
    "execute_command": execute_command,
    "write_file": write_file,
    "read_file": read_file
}

# ----------------------------------------------------------------------
# 2. AGENT CONFIGURATION & ORCHESTRATION
# ----------------------------------------------------------------------

SYSTEM_INSTRUCTION = """
You are Mini-Cursor, an advanced autonomous software engineering agent. 
You have direct access to the user's local filesystem and terminal.

Your workflow:
1. When a user asks you to create, modify, inspect, or run code, select the appropriate tool.
2. If a task requires multiple steps (e.g., write a script, then test it by running it), execute the tools sequentially.
3. Always explain your intent briefly to the user before running a tool.
4. If an execution fails, inspect the error output and correct your steps.
"""

def run_minicursor():
    # Pass the actual function definitions into the config tools array
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.2,
        tools=[execute_command, write_file, read_file]
    )
    
    # Using gemini-3.1-flash-lite as it is highly performant with function calling
    chat = client.chats.create(model="gemini-3.1-flash-lite", config=config)
    
    print("🚀 Mini-Cursor Online. What are we building today?")
    print("-" * 50)
    
    while True:
        try:
            user_query = input("\n👤 You: ")
            if user_query.strip().lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
                
            if not user_query.strip():
                continue
                
            # Send initial message to the agent
            response = chat.send_message(user_query)
            
            # The execution loop: loop as long as the model wants to call functions
            while response.function_calls:
                for function_call in response.function_calls:
                    name = function_call.name
                    args = function_call.args
                    call_id = function_call.id # Crucial tracking mechanism for the chat API
                    
                    if name in tools_map:
                        # Convert Gemini Args map to a native Python dictionary
                        tool_args = dict(args)
                        # Execute the local function
                        tool_result = tools_map[name](**tool_args)
                        
                        # Provide the tool output back to the Gemini Chat session
                        response = chat.send_message(
                            types.Part.from_function_response(
                                name=name,
                                response={"result": tool_result},
                                id=call_id
                            )
                        )
                    else:
                        print(f"❌ Model requested unknown tool: {name}")
                        break
            
            # Print final synthesized textual response from the agent
            if response.text:
                print(f"\n🤖 Mini-Cursor: {response.text}")
                
        except KeyboardInterrupt:
            print("\nExiting Mini-Cursor session.")
            break
        except Exception as e:
            print(f"\n💥 An error occurred in the agent loop: {e}")

if __name__ == "__main__":
    run_minicursor()
