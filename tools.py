import subprocess
import platform

def run_ping(host):
    try:
        command = ["ping", "-n", "4", host] if platform.system() == "Windows" else ["ping", "-c", "4", host]
        return subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        return f"Error running ping: {e.output}"

def run_traceroute(host):
    try:
        command = ["tracert", host] if platform.system() == "Windows" else ["traceroute", host]
        return subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        return f"Error running traceroute: {e.output}"

def run_nslookup(domain):
    try:
        return subprocess.check_output(["nslookup", domain], stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        return f"Error running nslookup: {e.output}"

def get_ip_config():
    try:
        command = ["ipconfig"] if platform.system() == "Windows" else ["ifconfig"]
        return subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        return f"Error getting IP configuration: {e.output}"

def ask_user(question):
    return input(f"[Bot asks] {question}\n[You]: ")
