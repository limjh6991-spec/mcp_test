#!/usr/bin/env python3
"""
간단한 MCP 서버 테스트 스크립트
"""

import requests
import time
import sys

# 테스트할 서버 목록
servers = {
    "prompt_generator": "http://localhost:8000",
    "stable_diffusion": "http://localhost:8001", 
    "blender": "http://localhost:8002",
    "env_manager": "http://localhost:8003",
    "github": "http://localhost:8004"
}

def test_server_health(name, url):
    """Server health check"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] {name}: {data}")
            return True
        else:
            print(f"[FAIL] {name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[DOWN] {name}: Connection failed (server not running)")
        return False
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        return False

def test_prompt_generator():
    """Prompt generator functionality test"""
    try:
        data = {
            "goal": "cleaning robot",
            "style_guide": "modern",
            "complexity": "medium"
        }
        
        response = requests.post("http://localhost:8000/generate_3d_robot_prompt", json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Prompt generation test passed:")
            print(f"   Original: {result.get('prompt', 'N/A')}")
            print(f"   Enhanced: {result.get('enhanced_prompt', 'N/A')[:100]}...")
            return True
        else:
            print(f"[FAIL] Prompt generation failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Prompt generation error: {e}")
        return False

def main():
    print("=== MCP Server Integration Test ===\n")
    
    print("1. Server Health Check:")
    healthy_servers = 0
    for name, url in servers.items():
        if test_server_health(name, url):
            healthy_servers += 1
        time.sleep(0.5)
    
    print(f"\nRunning servers: {healthy_servers}/{len(servers)}")
    
    if healthy_servers == 0:
        print("\n[WARNING] No servers are running.")
        print("Please start servers first:")
        print("  .\\run_servers_fixed.ps1 -Action start")
        return
    
    print("\n2. Functionality Tests:")
    
    # Prompt generator test
    if "http://localhost:8000" in [url for url in servers.values()]:
        test_prompt_generator()
    
    print("\n=== Test Completed ===")

if __name__ == "__main__":
    main()