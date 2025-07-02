import subprocess
import json
import tools
import os
import requests
from colorama import Fore, Style, init
init(autoreset=True)

# Config
OLLAMA_MODEL = "phi3"
SYSTEM_PROMPT_PATH = "prompts/system_prompt.txt"

# Load system prompt
with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:

    system_prompt = f.read()

# Conversation history
messages = [{"role": "system", "content": system_prompt}]

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

def print_separator():
    print(f"\n{Fore.BLUE}{'-' * 60}\n")

def main():
    print("🤖 NetRakshak: BARC's Own Network Troubleshooting Assistant")
    print("-----------------------------------------------------------\n")
    print("Type your problem below (or type 'exit' to quit):")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting NetRakshak. Stay connected!")
            break

        messages.append({"role": "user", "content": user_input})
        
        # Step-by-step loop — one assistant reply per user response
        while True:
            assistant_reply = call_phi3(messages)
            print("\n[NetRakshak]:\n")
            print(assistant_reply)
            print_separator()

            tool_instruction = process_response(assistant_reply)

            messages.append({"role": "assistant", "content": assistant_reply})

            if tool_instruction:
                tool_output = run_tool(tool_instruction["tool"], tool_instruction["parameters"])
                messages.append({
                    "role": "user", 
                    "content": f"[Tool Output]\n{tool_output}"
                })
            else:
                break  # If no tool or follow-up, stop here and ask user for next input

if __name__ == "__main__":
    main()
