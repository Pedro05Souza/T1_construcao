#!/usr/bin/env python3
"""
Script para aguardar o banco de dados estar pronto antes de executar migrações.
"""
import sys
import time
import os
import asyncio
from urllib.parse import urlparse

try:
    import asyncpg
except ImportError:
    print("⚠️  asyncpg not available, using simple TCP check")
    import socket
    asyncpg = None

async def check_postgres_async(database_url: str, max_retries: int = 30, delay: int = 2) -> bool:
    """Verifica se o PostgreSQL está pronto usando asyncpg."""
    parsed = urlparse(database_url)
    
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    user = parsed.username or "postgres"
    password = parsed.password or "postgres"
    database = parsed.path.lstrip("/") or "postgres"
    
    for attempt in range(1, max_retries + 1):
        try:
            conn = await asyncpg.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                timeout=5
            )
            await conn.execute("SELECT 1")
            await conn.close()
            print(f"✓ Database is ready! (attempt {attempt})")
            return True
        except Exception as e:
            if attempt < max_retries:
                print(f"⏳ Waiting for database... (attempt {attempt}/{max_retries})")
                await asyncio.sleep(delay)
            else:
                print(f"✗ Failed to connect to database after {max_retries} attempts")
                print(f"Error: {e}")
                return False
    
    return False

def check_postgres_tcp(host: str, port: int, max_retries: int = 30, delay: int = 2) -> bool:
    """Verifica se a porta do PostgreSQL está aberta (fallback simples)."""
    for attempt in range(1, max_retries + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✓ Database port is open! (attempt {attempt})")
                return True
        except Exception as e:
            pass
        
        if attempt < max_retries:
            print(f"⏳ Waiting for database port... (attempt {attempt}/{max_retries})")
            time.sleep(delay)
    
    print(f"✗ Failed to connect to database port after {max_retries} attempts")
    return False

if __name__ == "__main__":
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("✗ DATABASE_URL environment variable is not set")
        sys.exit(1)
    
    parsed = urlparse(database_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    
    print(f"🔍 Checking database connection...")
    print(f"   Host: {host}, Port: {port}")
    
    if asyncpg:
        # Usar asyncpg para verificação completa
        result = asyncio.run(check_postgres_async(database_url))
    else:
        # Fallback: apenas verificar se a porta está aberta
        result = check_postgres_tcp(host, port)
    
    if result:
        print("✅ Database is ready!")
        sys.exit(0)
    else:
        print("❌ Database connection failed")
        sys.exit(1)

