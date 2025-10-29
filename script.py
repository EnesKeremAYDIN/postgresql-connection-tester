#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import time
import socket
from urllib.parse import urlparse, parse_qs
import psycopg2
from psycopg2 import sql
from datetime import datetime


def parse_postgres_url(url):
    try:
        parsed = urlparse(url)
        
        host = parsed.hostname
        port = parsed.port or 5432
        database = parsed.path.lstrip('/') if parsed.path else None
        username = parsed.username
        password = parsed.password
        
        query_params = parse_qs(parsed.query)
        ssl_mode = query_params.get('sslmode', ['prefer'])[0]
        
        connection_info = {
            'host': host,
            'port': port,
            'database': database,
            'username': username,
            'password': password,
            'ssl_mode': ssl_mode,
            'original_url': url,
            'query_params': query_params,
            'parsed_at': datetime.now().isoformat()
        }
        
        return connection_info
        
    except Exception as e:
        raise ValueError(f"URL parsing error: {str(e)}")


def test_host_connectivity(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def get_detailed_database_info(cursor):
    info = {}
    
    try:
        cursor.execute("SELECT version();")
        info['version'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT current_database(), current_user, current_schema();")
        db_info = cursor.fetchone()
        info['database'] = db_info[0]
        info['user'] = db_info[1]
        info['schema'] = db_info[2]
        
        cursor.execute("SELECT inet_server_addr(), inet_server_port();")
        server_info = cursor.fetchone()
        info['server_ip'] = server_info[0]
        info['server_port'] = server_info[1]
        
        cursor.execute("SELECT pg_database_size(current_database());")
        info['database_size'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM pg_stat_activity;")
        info['active_connections'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT setting FROM pg_settings WHERE name = 'max_connections';")
        info['max_connections'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT setting FROM pg_settings WHERE name = 'shared_buffers';")
        info['shared_buffers'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT setting FROM pg_settings WHERE name = 'effective_cache_size';")
        info['effective_cache_size'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT setting FROM pg_settings WHERE name = 'work_mem';")
        info['work_mem'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT setting FROM pg_settings WHERE name = 'maintenance_work_mem';")
        info['maintenance_work_mem'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT setting FROM pg_settings WHERE name = 'checkpoint_completion_target';")
        info['checkpoint_completion_target'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT setting FROM pg_settings WHERE name = 'wal_buffers';")
        info['wal_buffers'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT setting FROM pg_settings WHERE name = 'default_statistics_target';")
        info['default_statistics_target'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
        info['public_tables_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM information_schema.tables;")
        info['total_tables_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM information_schema.schemata;")
        info['schemas_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM pg_user;")
        info['users_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM pg_database;")
        info['databases_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT pg_postmaster_start_time();")
        info['server_start_time'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT now();")
        info['current_time'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
        info['database_size_pretty'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT pg_size_pretty(pg_total_relation_size('pg_class'));")
        info['system_catalog_size'] = cursor.fetchone()[0]
        
    except Exception as e:
        info['error'] = str(e)
    
    return info


def test_connection(connection_info):
    test_results = {
        'connection_successful': False,
        'error_message': None,
        'detailed_info': None,
        'connection_time': None,
        'host_reachable': False,
        'performance_metrics': {}
    }
    
    try:
        start_time = time.time()
        
        host_reachable = test_host_connectivity(connection_info['host'], connection_info['port'])
        test_results['host_reachable'] = host_reachable
        
        if not host_reachable:
            test_results['error_message'] = f"Host {connection_info['host']}:{connection_info['port']} is not reachable"
            return test_results
        
        conn_params = {
            'host': connection_info['host'],
            'port': connection_info['port'],
            'database': connection_info['database'],
            'user': connection_info['username'],
            'password': connection_info['password'],
            'sslmode': connection_info['ssl_mode'],
            'connect_timeout': 10
        }
        
        conn_start = time.time()
        conn = psycopg2.connect(**conn_params)
        conn_time = time.time() - conn_start
        
        cursor = conn.cursor()
        
        query_start = time.time()
        detailed_info = get_detailed_database_info(cursor)
        query_time = time.time() - query_start
        
        connection_time = time.time() - start_time
        
        test_results['connection_successful'] = True
        test_results['detailed_info'] = detailed_info
        test_results['connection_time'] = round(connection_time, 3)
        test_results['performance_metrics'] = {
            'connection_time': round(conn_time, 3),
            'query_time': round(query_time, 3),
            'total_time': round(connection_time, 3)
        }
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        test_results['error_message'] = f"PostgreSQL error: {str(e)}"
    except Exception as e:
        test_results['error_message'] = f"General error: {str(e)}"
    
    return test_results


def print_connection_info(connection_info):
    print("\n" + "="*80)
    print("🔍 POSTGRESQL CONNECTION INFORMATION")
    print("="*80)
    
    print(f"📍 Host: {connection_info['host']}")
    print(f"🔌 Port: {connection_info['port']}")
    print(f"🗄️  Database: {connection_info['database']}")
    print(f"👤 Username: {connection_info['username']}")
    print(f"🔒 Password: {'*' * len(connection_info['password']) if connection_info['password'] else 'None'}")
    print(f"🔐 SSL Mode: {connection_info['ssl_mode']}")
    print(f"⏰ Parse Time: {connection_info['parsed_at']}")
    
    if connection_info['query_params']:
        print(f"⚙️  Query Parameters:")
        for key, values in connection_info['query_params'].items():
            print(f"    {key}: {', '.join(values)}")
    
    print(f"🔗 Original URL: {connection_info['original_url']}")


def print_test_results(test_results):
    print("\n" + "="*80)
    print("🧪 CONNECTION TEST RESULTS")
    print("="*80)
    
    if test_results['connection_successful']:
        print("✅ Connection successful!")
        
        metrics = test_results['performance_metrics']
        print(f"⏱️  Performance Metrics:")
        print(f"    Connection Time: {metrics['connection_time']} seconds")
        print(f"    Query Time: {metrics['query_time']} seconds")
        print(f"    Total Time: {metrics['total_time']} seconds")
        
        if test_results['detailed_info']:
            info = test_results['detailed_info']
            
            print(f"\n🖥️  Server Information:")
            print(f"    Version: {info.get('version', 'N/A')}")
            print(f"    Server IP: {info.get('server_ip', 'N/A')}")
            print(f"    Server Port: {info.get('server_port', 'N/A')}")
            print(f"    Start Time: {info.get('server_start_time', 'N/A')}")
            print(f"    Current Time: {info.get('current_time', 'N/A')}")
            
            print(f"\n📊 Database Information:")
            print(f"    Database: {info.get('database', 'N/A')}")
            print(f"    Active User: {info.get('user', 'N/A')}")
            print(f"    Schema: {info.get('schema', 'N/A')}")
            print(f"    Size: {info.get('database_size_pretty', 'N/A')}")
            print(f"    System Catalog Size: {info.get('system_catalog_size', 'N/A')}")
            
            print(f"\n🔗 Connection Information:")
            print(f"    Active Connections: {info.get('active_connections', 'N/A')}")
            print(f"    Max Connections: {info.get('max_connections', 'N/A')}")
            print(f"    Connection Usage: %{(info.get('active_connections', 0) / int(info.get('max_connections', 1)) * 100):.1f}")
            
            print(f"\n⚙️  Performance Settings:")
            print(f"    Shared Buffers: {info.get('shared_buffers', 'N/A')}")
            print(f"    Effective Cache Size: {info.get('effective_cache_size', 'N/A')}")
            print(f"    Work Memory: {info.get('work_mem', 'N/A')}")
            print(f"    Maintenance Work Memory: {info.get('maintenance_work_mem', 'N/A')}")
            print(f"    WAL Buffers: {info.get('wal_buffers', 'N/A')}")
            print(f"    Checkpoint Completion Target: {info.get('checkpoint_completion_target', 'N/A')}")
            print(f"    Default Statistics Target: {info.get('default_statistics_target', 'N/A')}")
            
            print(f"\n📈 Database Statistics:")
            print(f"    Public Tables: {info.get('public_tables_count', 'N/A')}")
            print(f"    Total Tables: {info.get('total_tables_count', 'N/A')}")
            print(f"    Schema Count: {info.get('schemas_count', 'N/A')}")
            print(f"    User Count: {info.get('users_count', 'N/A')}")
            print(f"    Database Count: {info.get('databases_count', 'N/A')}")
            
    else:
        print("❌ Connection failed!")
        print(f"🌐 Host Reachability: {'✅ Yes' if test_results['host_reachable'] else '❌ No'}")
        print(f"🚨 Error message: {test_results['error_message']}")


def main():
    print("🐘 PostgreSQL URL Parser and Detailed Test Script")
    print("="*60)
    
    while True:
        url = input("\n📝 Enter PostgreSQL URL (e.g., postgresql://user:pass@host:port/db): ").strip()
        
        if not url:
            print("❌ URL cannot be empty!")
            continue
            
        if not url.startswith(('postgresql://', 'postgres://')):
            print("❌ Please enter a valid PostgreSQL URL!")
            continue
            
        break
    
    try:
        print("\n🔄 Parsing URL...")
        connection_info = parse_postgres_url(url)
        
        print_connection_info(connection_info)
        
        print("\n🔄 Testing connection...")
        test_results = test_connection(connection_info)
        
        print_test_results(test_results)
        
        print("\n🎉 Test completed!")
        
    except ValueError as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Program terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
