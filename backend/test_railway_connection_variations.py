#!/usr/bin/env python3
"""
Test Railway connection with various parameter combinations
"""

import psycopg
import time

# Connection parameters
host = 'turntable.proxy.rlwy.net'
port = 20563
database = 'railway'
user = 'postgres'
password = 'jLDqXkXJFTMtapRTPynxdKWEZEkDSsJG'

print("=" * 70)
print("Testing Railway Database Connection - Multiple Variations")
print("=" * 70)
print(f"\nHost: {host}")
print(f"Port: {port}")
print(f"Database: {database}")
print(f"User: {user}\n")

# Test variations
variations = [
    ("sslmode=require", "SSL Required"),
    ("sslmode=prefer", "SSL Preferred"),
    ("sslmode=allow", "SSL Allowed"),
    ("sslmode=disable", "SSL Disabled"),
    ("sslmode=require connect_timeout=30", "SSL Required + 30s timeout"),
    ("sslmode=require connect_timeout=30 keepalives=1 keepalives_idle=30", "SSL + Keepalives"),
]

success = False

for params, description in variations:
    print(f"\n🔍 Testing: {description}")
    print(f"   Parameters: {params}")
    
    try:
        start = time.time()
        conn_string = f"host={host} port={port} dbname={database} user={user} password={password} {params}"
        conn = psycopg.connect(conn_string)
        elapsed = time.time() - start
        
        print(f"   ✅ SUCCESS! Connected in {elapsed:.2f} seconds")
        
        # Test query
        cur = conn.cursor()
        cur.execute("SELECT version(), current_database(), current_user")
        result = cur.fetchone()
        
        print(f"   📋 PostgreSQL: {result[0].split(',')[0]}")
        print(f"   📊 Database: {result[1]}")
        print(f"   👤 User: {result[2]}")
        
        # Check tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        if tables:
            print(f"   📋 Tables: {len(tables)} found")
            for table in tables[:5]:  # Show first 5
                print(f"      - {table}")
            if len(tables) > 5:
                print(f"      ... and {len(tables) - 5} more")
        else:
            print("   📋 Database is empty (ready for migration)")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ CONNECTION SUCCESSFUL!")
        print("=" * 70)
        print(f"\nWorking connection string:")
        print(f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}?{params.replace(' ', '&')}")
        
        success = True
        break
        
    except psycopg.OperationalError as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            print(f"   ❌ Connection timeout")
        elif "refused" in error_msg.lower():
            print(f"   ❌ Connection refused")
        else:
            print(f"   ❌ Failed: {error_msg[:60]}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:60]}")

if not success:
    print("\n" + "=" * 70)
    print("❌ All connection attempts failed")
    print("=" * 70)
    print("\nSince your Railway dashboard shows the database is ACTIVE,")
    print("but we can't connect, please:")
    print("\n1. Click the 'Database' tab in Railway dashboard")
    print("2. Copy the connection string shown there")
    print("3. Check if there's a 'Connect' button with connection details")
    print("4. Verify the port number matches (should be 20563)")
    print("\nThe connection string format should be:")
    print("postgresql://postgres:PASSWORD@turntable.proxy.rlwy.net:PORT/railway")

