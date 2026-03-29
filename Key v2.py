#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Key Approval System - Leo Edition
Developer: Leo
Approved Key: Paing07709
"""

import os
import sys
import json
import time
import hashlib
import requests
import platform
import subprocess

# Colors
BRED = "\033[1;31m"
BGREEN = "\033[1;32m"
BCYAN = "\033[1;36m"
BYELLOW = "\033[1;33m"
BBLUE = "\033[1;34m"
RESET = "\033[0m"

# Configuration
SHEET_ID = "1TZQQDtenMG_X0iKpNqN_o86u4vFYZxg2V5WYVLQ2kYY"
KEY_FILE = os.path.expanduser("~/.leo_key_approved")

def get_device_id():
    """Generate unique device ID"""
    try:
        # Try to get Android serial number (for Termux/Android)
        if platform.system() == "Linux" and os.path.exists('/system/build.prop'):
            result = subprocess.run(['getprop', 'ro.serialno'], capture_output=True, text=True)
            if result.stdout.strip():
                return result.stdout.strip()
        
        # Try to get MAC address
        try:
            import uuid
            mac = uuid.getnode()
            if mac != 0:
                return hashlib.md5(str(mac).encode()).hexdigest()[:16]
        except:
            pass
        
        # Fallback: use hostname + home directory
        hostname = platform.node()
        home = os.path.expanduser('~')
        return hashlib.md5(f"{hostname}{home}".encode()).hexdigest()[:16]
        
    except:
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:16]

def save_approval():
    """Save approval status to file"""
    try:
        data = {
            'device_id': get_device_id(),
            'approved_at': time.time(),
            'approved_by': 'Leo',
            'version': '1.0'
        }
        with open(KEY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"{BRED}[!] Failed to save approval: {e}{RESET}")
        return False

def check_approval():
    """Check if device is already approved"""
    try:
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, 'r') as f:
                data = json.load(f)
                if data.get('device_id') == get_device_id():
                    return True
    except Exception as e:
        print(f"{BYELLOW}[!] Approval check failed: {e}{RESET}")
    return False

def clear_approval():
    """Clear saved approval (for testing)"""
    try:
        if os.path.exists(KEY_FILE):
            os.remove(KEY_FILE)
            print(f"{BGREEN}[✓] Approval cleared{RESET}")
            return True
    except:
        pass
    return False

def fetch_allowed_users():
    """Fetch allowed users from Google Sheets"""
    csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    
    try:
        print(f"{BCYAN}[*] Connecting to authorization server...{RESET}")
        response = requests.get(csv_url, timeout=8)
        
        if response.status_code == 200:
            content = response.text.strip()
            if content:
                lines = content.split('\n')
                if len(lines) >= 2:
                    allowed_users = []
                    for line in lines[1:]:
                        parts = line.split(',')
                        if parts and parts[0].strip():
                            allowed_users.append(parts[0].strip())
                    return allowed_users
    except requests.exceptions.Timeout:
        print(f"{BYELLOW}[!] Connection timeout{RESET}")
    except requests.exceptions.ConnectionError:
        print(f"{BYELLOW}[!] No internet connection{RESET}")
    except Exception as e:
        print(f"{BYELLOW}[!] Error: {e}{RESET}")
    
    return None

def verify_key(user_key):
    """
    Verify if a key is approved
    Returns: (approved, message)
    """
    # Hardcoded developer key
    if user_key == "Paing07709":
        return True, "Developer access granted"
    
    # Check online
    allowed_users = fetch_allowed_users()
    if allowed_users is not None:
        if user_key in allowed_users:
            return True, "Access granted"
        else:
            return False, f"Key '{user_key}' not approved"
    else:
        return False, "Internet required for first-time approval"

def login(show_banner=True):
    """
    Main login function
    Returns: True if approved, False if not
    """
    if show_banner:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{BCYAN}╔══════════════════════════════════════╗{RESET}")
        print(f"{BCYAN}║         LEO KEY APPROVAL SYSTEM      ║{RESET}")
        print(f"{BCYAN}╚══════════════════════════════════════╝{RESET}")
        print()
    
    # Check if already approved
    if check_approval():
        if show_banner:
            print(f"{BGREEN}[✓] Device already approved!{RESET}")
            print(f"{BGREEN}[*] Welcome back!{RESET}")
            print(f"{BGREEN}[*] Running in offline mode{RESET}")
            time.sleep(1)
        return True
    
    # Get user key
    user_key = get_device_id()
    
    if show_banner:
        print(f"{BCYAN}[*] Your device key: {BYELLOW}{user_key}{RESET}")
        print()
    
    # Verify key
    approved, message = verify_key(user_key)
    
    if approved:
        if show_banner:
            print(f"{BGREEN}[✓] {message}!{RESET}")
            print(f"{BGREEN}[*] Saving approval for offline use...{RESET}")
        save_approval()
        if show_banner:
            time.sleep(1.5)
        return True
    else:
        if show_banner:
            print(f"{BRED}[✗] {message}{RESET}")
            print()
            print(f"{BYELLOW}To request access, contact Developer Leo:{RESET}")
            print(f"  Your Key: {user_key}")
            print(f"  Developer Key: Paing07709")
            print(f"  Telegram: @LeoDev")
        return False

def get_approved_keys():
    """Get list of all approved keys (for admin use)"""
    # Hardcoded developer key
    keys = ["Paing07709"]
    
    # Add from Google Sheets if available
    allowed_users = fetch_allowed_users()
    if allowed_users:
        keys.extend(allowed_users)
    
    return list(set(keys))

def is_approved(user_key=None):
    """
    Quick check if a key is approved (no banner)
    Returns: True if approved
    """
    if user_key is None:
        user_key = get_device_id()
    
    # Check offline approval first
    if check_approval():
        return True
    
    # Check hardcoded
    if user_key == "Paing07709":
        return True
    
    # Check online
    allowed_users = fetch_allowed_users()
    if allowed_users is not None and user_key in allowed_users:
        return True
    
    return False

def get_status():
    """Get current approval status"""
    if check_approval():
        return {
            'approved': True,
            'offline': True,
            'device_id': get_device_id()
        }
    
    user_key = get_device_id()
    if user_key == "Paing07709":
        return {
            'approved': True,
            'offline': False,
            'device_id': user_key
        }
    
    allowed_users = fetch_allowed_users()
    if allowed_users is not None and user_key in allowed_users:
        return {
            'approved': True,
            'offline': False,
            'device_id': user_key
        }
    
    return {
        'approved': False,
        'offline': False,
        'device_id': user_key
    }

# ===============================
# SELF TEST (Run directly)
# ===============================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Leo Key Approval System')
    parser.add_argument('--check', action='store_true', help='Check approval status')
    parser.add_argument('--clear', action='store_true', help='Clear saved approval')
    parser.add_argument('--keys', action='store_true', help='Show approved keys')
    parser.add_argument('--device-id', action='store_true', help='Show device ID')
    
    args = parser.parse_args()
    
    if args.check:
        status = get_status()
        print(f"Device ID: {status['device_id']}")
        print(f"Approved: {status['approved']}")
        print(f"Offline Mode: {status['offline']}")
        
    elif args.clear:
        clear_approval()
        
    elif args.keys:
        keys = get_approved_keys()
        print("Approved Keys:")
        for k in keys:
            print(f"  - {k}")
            
    elif args.device_id:
        print(get_device_id())
        
    else:
        # Run login
        login()