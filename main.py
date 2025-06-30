import subprocess
import json
import tools
import os
import requests

# Config
OLLAMA_MODEL = "phi3"
SYSTEM_PROMPT_PATH = "prompts/system_prompt.txt"

# Load system prompt
with open(SYSTEM_PROMPT_PATH, "r") as f:
    system_prompt = f.read()

# Conversation history (system + chat)
messages = [
    {"role": "system", "content": system_prompt}
]

def call_phi3(messages):
    response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 2048,
            "repeat_penalty": 1.1
        }
    }
)
    response.raise_for_status()
    return response.json()["message"]["content"]

def process_response(response):
    try:
        parsed = json.loads(response)
        if "tool" in parsed and "parameters" in parsed:
            return parsed
        else:
            return None
    except json.JSONDecodeError:
        return None

def run_tool(tool_name, parameters):
    try:
        if tool_name == "run_ping":
            return tools.run_ping(parameters["host"])
        elif tool_name == "run_traceroute":
            return tools.run_traceroute(parameters["host"])
        elif tool_name == "run_nslookup":
            return tools.run_nslookup(parameters["domain"])
        elif tool_name == "get_ip_config":
            return tools.get_ip_config()
        elif tool_name == "ask_user":
            return tools.ask_user(parameters["question"])
        else:
            return "Unknown tool."
    except Exception as e:
        return f"Error running tool: {str(e)}"
from colorama import Fore, Style, init
init(autoreset=True)

def print_separator():
    print(f"\n{Fore.BLUE}{'-' * 60}\n")


def main():
    print("🤖 Network Troubleshooting Bot (powered by phi3)\n")
    print("Type your problem below (or type 'exit' to quit):")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        messages.append({"role": "user", "content": user_input})
        
        while True:
            response = call_phi3(messages)
            print("\n[phi3]:", response)

            tool_instruction = process_response(response)

            if tool_instruction:
                tool_output = run_tool(tool_instruction["tool"], tool_instruction["parameters"])
                messages.append({
                    "role": "assistant", 
                    "content": response
                })
                messages.append({
                    "role": "user", 
                    "content": f"I ran the tool and got this result:\n{tool_output}"
                })
            else:
                messages.append({"role": "assistant", "content": response})
                break

if __name__ == "__main__":
    main()
