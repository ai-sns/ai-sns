#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Tools Module - Verify all functionality"""
import requests
import json

BASE_URL = "http://127.0.0.1:8788/api/tools"

print("=" * 60)
print("TOOLS MODULE API TESTS")
print("=" * 60)

# Test 1: GET Plugins
print("\n1. Testing GET /plugins")
try:
    r = requests.get(f"{BASE_URL}/plugins", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Found {len(data)} plugins")
        if data: print(f"  Example: {data[0].get('name', 'N/A')}")
    else:
        print(f"✗ Status {r.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: GET MCPs
print("\n2. Testing GET /mcp")
try:
    r = requests.get(f"{BASE_URL}/mcp", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Found {len(data)} MCPs")
    else:
        print(f"✗ Status {r.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: GET Functions
print("\n3. Testing GET /functions")
try:
    r = requests.get(f"{BASE_URL}/functions", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Found {len(data)} functions")
    else:
        print(f"✗ Status {r.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: GET Skills
print("\n4. Testing GET /skills")
try:
    r = requests.get(f"{BASE_URL}/skills", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Found {len(data)} skills")
    else:
        print(f"✗ Status {r.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("Tests completed! Check results above.")
print("=" * 60)
