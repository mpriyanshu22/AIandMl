import json
import os
import requests
import subprocess
import shutil
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langsmith import wrappers
load_dotenv()

gemclient = genai.Client()
# Wrap the Gemini client to enable LangSmith tracing
client = wrappers.wrap_gemini(
        gemclient,
        tracing_extra={
            "tags": ["gemini", "python"],
            "metadata": {
                "integration": "google-genai",
            },
        },
)


def run_command(command: str) -> str:
    print(f"💻 [Executing System Tool]: Running command '{command}'...")
    command = command.strip()
    
    try:
        # 1. Check karein ki kya system par powershell available hai
        powershell_path = shutil.which("powershell")
        
        if powershell_path:
            # Agar Windows hai, toh powershell execution wrapper use karein
            # -Command se powershell Linux aliases (touch, ls, rm) ko natively handle kar lega
            exec_args = [powershell_path, "-Command", command]
        else:
            # Fallback for Linux/Mac/Git-Bash setups
            exec_args = command
            
        # 2. Execute with safety (shell=True only needed if fallback to string on standard cmd)
        use_shell = False if powershell_path else True
        
        result = subprocess.run(
            exec_args, 
            shell=use_shell, 
            capture_output=True, 
            text=True
        )
        
        # 3. Handle Outputs based on real system codes
        if result.returncode == 0:
            output = result.stdout.strip()
            return output if output else "Success: Command executed with no visual output."
        else:
            # Dono stdout aur stderr check karein kyunki kuch commands cross-output deti hain
            error_msg = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
            return f"Command Failed! Error from system: {error_msg}"
            
    except Exception as e:
        return f"Exception occurred while running command: {str(e)}"


# This remains your local python tool execution
def get_weather(city: str) -> str:
    print(f"🔌 [Executing Local Tool]: Querying weather database for '{city}'...")
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code ==200:
        return f"the weather in {city} is {response.text}."
    return "Something went wrong 31 deg default!"
# FIXED: We explicitly describe the available tools inside the prompt text
system_prompt = """
you are an ai agent who is specialised in resolving user query.
you work on start, plan, action, observe mode.
for the given user query and available tools, plan the step by step execution, based on the planning,
select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
wait for the observation and based on observation from the tool call resolve the user query.

AVAILABLE TOOLS:
- get_weather: Accepts a 'city' string parameter and returns the current temperature.
- run_command: Accepts command as input,then run commands on system and give result.

Rules:
1. Follow the strict JSON output as per Output schema.
2. Always perform one step at a time and wait for next input. Do not skip ahead.
3. Carefully analyse the user query.

Output Format (Strict JSON):
{ "step": "plan|action|output", "content": "explanation string", "function": "name_of_function_only_if_action", "input": "parameter_only_if_action" }

example:
user query: what is the weather of new york?
Output: {{"step":"plan","content":"The user is interested in weather data of new york"}}
Output:{{"step":"plan","content":"from the available tools i should call get_weather"}}
Output:{{"step":"action","function":"get_weather","input":"new york"}}
Output:{{"step":"observe", "output":"12 degree cel"}}
Output:{{"step":"output","content":"the weather in new york is 12 degree cel."}}
"""

# FIXED: Removed tools=[get_weather] to resolve the 400 error conflict
config = types.GenerateContentConfig(
    system_instruction=system_prompt,
    response_mime_type="application/json",
    temperature=0.0 
)

chat = client.chats.create(
    model="gemini-3.1-flash-lite",
    config=config
)

query = input("> ")
response = chat.send_message(query)

while True:
    try:
        parsed_response = json.loads(response.text)
    except json.JSONDecodeError:
        print(f"🤖 Failed to parse JSON configuration from model: {response.text}")
        break

    step = parsed_response.get("step")
    content = parsed_response.get("content")

    if step == "plan":
        print(f"🧠 [PLAN]: {content}")
        response = chat.send_message("Proceed to the next step based on your plan.")
        
    elif step == "action":
        func_name = parsed_response.get("function")
        func_input = parsed_response.get("input")
        print(f"🧠 [ACTION]: Requesting tool '{func_name}' with input '{func_input}'")
        
        if func_name == "get_weather":
            tool_output = get_weather(func_input)
        elif func_name == "run_command":
            tool_output = run_command(func_input)    
        else:
            tool_output = "Error: Tool not found"
            
        observation_payload = {
            "step": "observe",
            "output": tool_output
        }
        print(f"🧠 [OBSERVE]: {tool_output}")
        response = chat.send_message(json.dumps(observation_payload))
        
    elif step == "output":
        print(f"🤖 [OUTPUT]: {content}")
        break
    else:
        print(f"Unexpected Step Received: {parsed_response}")
        break