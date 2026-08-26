#!/usr/bin/env python3
"""
AGENT MULTI-LAUNCHER
Functions: FunPay, OSINT (4 mirrors), Telegram Tools, VPN Parser
"""

import os
import sys
import subprocess
from pathlib import Path
import platform
import requests
import importlib

REPO_URL = "https://github.com/beanonim/my-opensource.git"
REPO_DIR = "my-opensource"

FUNPAY_PATH = os.path.join(REPO_DIR, "FunPayCortex-main", "cortex.py")
OSINT_MIRRORS = {
    "1": os.path.join(REPO_DIR, "hate", "main.py"),
    "2": os.path.join(REPO_DIR, "lightwave", "main.py"),
    "3": os.path.join(REPO_DIR, "nihilist", "main.py"),
    "4": os.path.join(REPO_DIR, "versus", "main.py"),
}
TELEGRAM_SCRIPTS = {
    "funstat": os.path.join(REPO_DIR, "funstatfarm.py"),
    "gift": os.path.join(REPO_DIR, "giftsend.py"),
    "manager": os.path.join(REPO_DIR, "manager.py"),
}
VPN_REPOS = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS_mobile.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-checked.txt",
    "https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/githubmirror/6.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/Splitted-By-Protocol/vless.txt",
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/filtered/subs/vless.txt",
]

ALL_REQUIREMENTS = [
    "pyrogram", "telethon", "aiohttp", "requests",
    "colorama", "rich", "cryptography", "pysocks",
    "python-dotenv", "sqlalchemy", "beautifulsoup4",
    "lxml", "selenium", "fake-useragent", "pyyaml"
]

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
    print(" [4] 🌐 AGENT VPN Parser")
    print(" [0] ❌ Exit AGENT")
    print("=" * 60)

def install_all_modules():
    print("\n[AGENT] Installing all required modules...")
    for module in ALL_REQUIREMENTS:
        try:
            importlib.import_module(module)
            print(f"[AGENT] ✅ {module} already installed")
        except ImportError:
            print(f"[AGENT] 📦 Installing {module}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                print(f"[AGENT] ✅ {module} installed")
            except:
                print(f"[AGENT] ❌ Failed to install {module}")
    
    print("\n[AGENT] All modules installed!")

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
    if os.path.exists(os.path.join(REPO_DIR, "FunPayCortex-main")):
        req_file = os.path.join(REPO_DIR, "FunPayCortex-main", "requirements.txt")
        install_requirements_file(req_file)
        run_script(FUNPAY_PATH)
    else:
        print("[AGENT] FunPayCortex-main not found in repository!")

def run_osint_mirror():
    print("\n[AGENT] OSINT Suite - Select Mirror:")
    for key, path in OSINT_MIRRORS.items():
        status = "✅" if os.path.exists(path) else "❌"
        mirror_name = os.path.basename(os.path.dirname(path))
        print(f" [{key}] {status} AGENT {mirror_name}")
    
    choice = input("\n[AGENT] Select mirror (1-4): ").strip()
    if choice in OSINT_MIRRORS:
        script_path = OSINT_MIRRORS[choice]
        mirror_dir = os.path.dirname(script_path)
        req_file = os.path.join(mirror_dir, "requirements.txt")
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

def run_vpn_parser():
    print("\n[AGENT] VPN Config Parser")
    print(f"[AGENT] Found {len(VPN_REPOS)} sources")
    
    output_dir = os.path.join(REPO_DIR, "vpn_configs")
    os.makedirs(output_dir, exist_ok=True)
    
    for i, url in enumerate(VPN_REPOS, 1):
        print(f"[AGENT] [{i}/{len(VPN_REPOS)}] Downloading: {url.split('/')[-1]}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                filename = os.path.join(output_dir, f"config_{i}.txt")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  [AGENT] Saved: {filename}")
            else:
                print(f"  [AGENT] Status: {response.status_code}")
        except Exception as e:
            print(f"  [AGENT] Error: {e}")
    
    print(f"\n[AGENT] VPN configs saved to: {output_dir}")

def main():
    if not os.path.exists(REPO_DIR):
        print("[AGENT] First run detected. Setting up...")
        install_all_modules()
        clone_or_update_repo()
    
    while True:
        print_banner()
        choice = input("[AGENT] Select function (0-4): ").strip()
        
        if choice == "1":
            run_funpay()
        elif choice == "2":
            run_osint_mirror()
        elif choice == "3":
            run_telegram_tools()
        elif choice == "4":
            run_vpn_parser()
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