#!/usr/bin/env python3
"""
Update .env file with localhost connection for Railway tunnel
"""

import os
import sys
from pathlib import Path

def update_env_file(port=5432):
    """Update .env file with localhost connection string."""
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("❌ .env file not found!")
        sys.exit(1)
    
    # Read current .env
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Find and update DATABASE_URL
    updated = False
    new_lines = []
    
    for line in lines:
        if line.startswith('DATABASE_URL='):
            # Extract password from current URL or use default
            current_url = line.split('=', 1)[1].strip()
            if 'postgres:' in current_url:
                # Extract password
                try:
                    parts = current_url.split('@')
                    if len(parts) > 1:
                        user_pass = parts[0].split('://')[1]
                        password = user_pass.split(':')[1]
                    else:
                        password = 'jLDqXkXJFTMtapRTPynxdKWEZEkDSsJG'
                except:
                    password = 'jLDqXkXJFTMtapRTPynxdKWEZEkDSsJG'
            else:
                password = 'jLDqXkXJFTMtapRTPynxdKWEZEkDSsJG'
            
            # Create new connection string
            new_url = f"postgresql+psycopg://postgres:{password}@localhost:{port}/railway"
            new_lines.append(f"DATABASE_URL={new_url}\n")
            updated = True
            print(f"✅ Updated DATABASE_URL to use localhost:{port}")
        else:
            new_lines.append(line)
    
    if not updated:
        # Add DATABASE_URL if it doesn't exist
        new_lines.append(f"\nDATABASE_URL=postgresql+psycopg://postgres:jLDqXkXJFTMtapRTPynxdKWEZEkDSsJG@localhost:{port}/railway\n")
        print(f"✅ Added DATABASE_URL with localhost:{port}")
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"\n✅ .env file updated!")
    print(f"   Connection: localhost:{port}")
    print(f"\n⚠️  Make sure Railway tunnel is running!")
    print(f"   Run: railway connect postgres")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5432
    update_env_file(port)

