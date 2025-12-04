#!/usr/bin/env python3
"""
Railway Database Connection Diagnostic Tool
Tests connection to Railway PostgreSQL database with various configurations.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

def parse_db_url(url):
    """Parse database URL and return components."""
    parsed = urlparse(url.replace('postgresql+psycopg://', 'postgresql://'))
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/'),
        'user': parsed.username,
        'password': parsed.password,
        'query': parse_qs(parsed.query)
    }

def test_connection(host, port, database, user, password, sslmode='require', timeout=10):
    """Test database connection with specific parameters."""
    try:
        conn_string = f"host={host} port={port} dbname={database} user={user} password={password} sslmode={sslmode} connect_timeout={timeout}"
        conn = psycopg.connect(conn_string)
        version = conn.execute("SELECT version()").fetchone()[0]
        conn.close()
        return True, version.split(',')[0]
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("Railway Database Connection Diagnostic")
    print("=" * 70)
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment")
        print("\nPlease set it in backend/.env file")
        sys.exit(1)
    
    # Parse URL
    db_info = parse_db_url(database_url)
    
    print(f"\n📊 Connection Details:")
    print(f"   Host: {db_info['host']}")
    print(f"   Port: {db_info['port']}")
    print(f"   Database: {db_info['database']}")
    print(f"   User: {db_info['user']}")
    print(f"   Password: {'*' * len(db_info['password']) if db_info['password'] else 'Not set'}")
    
    # Test network connectivity
    print(f"\n🌐 Testing Network Connectivity...")
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((db_info['host'], db_info['port']))
        sock.close()
        if result == 0:
            print(f"   ✅ Port {db_info['port']} is reachable")
        else:
            print(f"   ❌ Port {db_info['port']} is NOT reachable (connection refused)")
    except socket.timeout:
        print(f"   ❌ Connection timeout - port {db_info['port']} may be blocked")
    except Exception as e:
        print(f"   ⚠️  Network test failed: {e}")
    
    # Test different SSL modes
    print(f"\n🔐 Testing SSL Modes...")
    ssl_modes = ['require', 'prefer', 'allow', 'disable']
    success = False
    
    for sslmode in ssl_modes:
        print(f"\n   Trying sslmode={sslmode}...", end=' ')
        success_flag, result = test_connection(
            db_info['host'],
            db_info['port'],
            db_info['database'],
            db_info['user'],
            db_info['password'],
            sslmode=sslmode,
            timeout=10
        )
        
        if success_flag:
            print(f"✅ SUCCESS!")
            print(f"   {result}")
            success = True
            break
        else:
            error_msg = result[:60] if len(result) > 60 else result
            print(f"❌ Failed: {error_msg}")
    
    print("\n" + "=" * 70)
    if success:
        print("✅ Database connection is working!")
        print("\nNext steps:")
        print("1. Run: python migrate_database.py")
        print("2. Verify tables are created")
    else:
        print("❌ Could not connect to database")
        print("\nPossible issues:")
        print("1. 🔥 Firewall blocking port 20563")
        print("2. 🌐 Network restrictions (VPN, corporate network)")
        print("3. 🔒 Railway IP whitelisting enabled")
        print("4. ⏸️  Database service not running on Railway")
        print("\nSolutions:")
        print("• Check Railway dashboard → Database → Settings → Network")
        print("• Ensure 'Public Networking' is enabled")
        print("• Check if IP whitelisting is blocking your IP")
        print("• Try from a different network/VPN")
        print("• If deploying on Railway, use internal URL: postgres.railway.internal")
    print("=" * 70)

if __name__ == "__main__":
    main()

