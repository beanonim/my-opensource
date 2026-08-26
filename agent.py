#!/usr/bin/env python3
"""
AGENT MULTI-LAUNCHER
"""

import os
import sys
import subprocess
import platform
import requests
import importlib

REPO_URL = "https://github.com/beanonim/my-opensource.git"
REPO_DIR = "my-opensource"
MAIN_DIR = os.path.join(REPO_DIR, "my-opensource-main")

FUNPAY_PATH = os.path.join(MAIN_DIR, "agent funpay", "cortex.py")
AGENT_PATHS = {
    "1": os.path.join(MAIN_DIR, "agent 1", "main.py"),
    "2": os.path.join(MAIN_DIR, "agent 2", "main.py"),
    "3": os.path.join(MAIN_DIR, "agent 3", "main.py"),
    "4": os.path.join(MAIN_DIR, "agent 4", "main.py"),
}
TELEGRAM_SCRIPTS = {
    "funstat": os.path.join(MAIN_DIR, "agent startfarm.py"),
    "gift": os.path.join(MAIN_DIR, "giftsend.py"),
    "manager": os.path.join(MAIN_DIR, "manager.py"),
}

AGENT_BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   █████╗  ██████╗ ███████╗███╗   ██╗████████╗                   ║
║  ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝                   ║
║  ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║                      ║
║  ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║                      ║
║  ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║                      ║
║  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝                      ║
║                                                                  ║
║              AGENT MULTI-LAUNCHER v1.0                           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_banner():
    clear_screen()
    print(AGENT_BANNER)
    print(" [1] 🔥 AGENT FunPay Cortex")
    print(" [2] 🕵️ AGENT OSINT Suite (4 Mirrors)")
    print(" [3] 📱 AGENT Telegram Tools")
    print(" [0] ❌ Exit AGENT")
    print("=" * 60)

def install_requirements_file(req_file):
    if os.path.exists(req_file):
        print(f"[AGENT] Installing requirements from {req_file}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
            print(f"[AGENT] ✅ Requirements installed!")
        except:
            print(f"[AGENT] ❌ Failed to install requirements")

def clone_or_update_repo():
    if not os.path.exists(REPO_DIR):
        print("[AGENT] Cloning repository...")
        subprocess.check_call(["git", "clone", REPO_URL])
    else:
        print("[AGENT] Updating repository...")
        os.chdir(REPO_DIR)
        subprocess.check_call(["git", "pull"])
        os.chdir("..")
    print("[AGENT] Repository ready!")

def run_script(script_path, args=None):
    if not os.path.exists(script_path):
        print(f"[AGENT] Script not found: {script_path}")
        return
    
    print(f"[AGENT] Running: {os.path.basename(script_path)}")
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n[AGENT] Interrupted by user")
    except Exception as e:
        print(f"[AGENT] Error: {e}")

def run_funpay():
    print("\n[AGENT] Starting FunPay Cortex...")
    funpay_dir = os.path.join(MAIN_DIR, "agent funpay")
    if os.path.exists(funpay_dir):
        req_file = os.path.join(funpay_dir, "requirements.txt")
        install_requirements_file(req_file)
        run_script(FUNPAY_PATH)
    else:
        print("[AGENT] agent funpay not found!")

def run_osint_mirror():
    print("\n[AGENT] OSINT Suite - Select Agent:")
    for key, path in AGENT_PATHS.items():
        status = "✅" if os.path.exists(path) else "❌"
        agent_name = os.path.basename(os.path.dirname(path))
        print(f" [{key}] {status} AGENT {agent_name}")
    
    choice = input("\n[AGENT] Select agent (1-4): ").strip()
    if choice in AGENT_PATHS:
        script_path = AGENT_PATHS[choice]
        agent_dir = os.path.dirname(script_path)
        req_file = os.path.join(agent_dir, "requirements.txt")
        install_requirements_file(req_file)
        run_script(script_path)
    else:
        print("[AGENT] Invalid choice!")

def run_telegram_tools():
    print("\n[AGENT] Telegram Tools:")
    print(" [1] AGENT FunStat Farm")
    print(" [2] AGENT Send Gifts")
    print(" [3] AGENT Full Manager")
    choice = input("\n[AGENT] Select tool (1-3): ").strip()
    
    tools = {
        "1": TELEGRAM_SCRIPTS["funstat"],
        "2": TELEGRAM_SCRIPTS["gift"],
        "3": TELEGRAM_SCRIPTS["manager"],
    }
    if choice in tools:
        script_path = tools[choice]
        script_dir = os.path.dirname(script_path)
        req_file = os.path.join(script_dir, "requirements.txt")
        install_requirements_file(req_file)
        run_script(script_path)
    else:
        print("[AGENT] Invalid choice!")

def main():
    if not os.path.exists(REPO_DIR):
        print("[AGENT] First run detected. Setting up...")
        clone_or_update_repo()
    
    while True:
        print_banner()
        choice = input("[AGENT] Select function (0-3): ").strip()
        
        if choice == "1":
            run_funpay()
        elif choice == "2":
            run_osint_mirror()
        elif choice == "3":
            run_telegram_tools()
        elif choice == "0":
            print("[AGENT] Goodbye!")
            break
        else:
            print("[AGENT] Invalid choice!")
        
        if choice != "0":
            input("\n[AGENT] Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[AGENT] Exiting...")
    except Exception as e:
        print(f"[AGENT] Fatal error: {e}")
