#!/usr/bin/env python3
"""Verify that all routes are properly registered"""
import sys
sys.path.insert(0, '/root/sharedata3/ai-sns-el')

from api_server_modular import app

print("=" * 60)
print("Registered Routes:")
print("=" * 60)

tools_routes = []
for route in app.routes:
    if hasattr(route, 'path') and '/api/tools' in route.path:
        tools_routes.append(f"{', '.join(route.methods)} {route.path}")

if tools_routes:
    print("\n✓ Found Tools Module Routes:")
    for route in sorted(tools_routes):
        print(f"  {route}")
    print(f"\nTotal: {len(tools_routes)} routes")
else:
    print("\n✗ No tools routes found!")
    
print("=" * 60)
