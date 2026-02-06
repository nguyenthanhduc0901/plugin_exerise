#!/usr/bin/env python
"""
Test script for ingestion_plugin
Tests CSV ingestion to PostgreSQL
"""

import os
import sys
import csv
import io
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_environment():
    """Check if environment variables are set"""
    print("=" * 60)
    print("1️⃣  TESTING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    env_status = {}
    
    for var in required_vars:
        value = os.getenv(var)
        status = "✅ SET" if value else "❌ MISSING"
        env_status[var] = status
        print(f"{var}: {status}")
        if value and var != 'DB_PASSWORD':
            print(f"   Value: {value}")
    
    print()
    return all("SET" in status for status in env_status.values())

def test_database_connection():
    """Test PostgreSQL connection"""
    print("=" * 60)
    print("2️⃣  TESTING DATABASE CONNECTION")
    print("=" * 60)
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✅ Connected to PostgreSQL")
        print(f"   Version: {version[0]}")
        
        cur.close()
        conn.close()
        print()
        return True
    
    except Exception as e:
        print(f"❌ Database connection failed:")
        print(f"   Error: {str(e)}")
        print()
        return False

def test_csv_parsing():
    """Test CSV parsing logic"""
    print("=" * 60)
    print("3️⃣  TESTING CSV PARSING")
    print("=" * 60)
    
    # Create test CSV
    test_csv = """name,salary,address,gpa,school
Alice,50000,123 Main St,3.8,State University
Bob,60000,456 Oak Ave,3.5,Tech Institute
Charlie,55000,789 Pine Rd,3.9,City College"""
    
    try:
        stream = io.StringIO(test_csv)
        csv_reader = csv.DictReader(stream)
        
        required_columns = {'name', 'salary', 'address', 'gpa', 'school'}
        if not csv_reader.fieldnames or not required_columns.issubset(set(csv_reader.fieldnames)):
            print(f"❌ CSV validation failed")
            print(f"   Required columns: {required_columns}")
            print(f"   Found columns: {set(csv_reader.fieldnames) if csv_reader.fieldnames else 'None'}")
            return False
        
        rows = list(csv_reader)
        print(f"✅ CSV parsing successful")
        print(f"   Rows parsed: {len(rows)}")
        for i, row in enumerate(rows, 1):
            print(f"   Row {i}: {row['name']} - {row['salary']} - {row['school']}")
        
        print()
        return True
    
    except Exception as e:
        print(f"❌ CSV parsing failed:")
        print(f"   Error: {str(e)}")
        print()
        return False

def test_plugin_import():
    """Test if plugin can be imported"""
    print("=" * 60)
    print("4️⃣  TESTING PLUGIN IMPORT")
    print("=" * 60)
    
    try:
        from dify_plugin import Plugin, DifyPluginEnv
        print(f"✅ dify_plugin imported successfully")
        
        # Try to import the tool
        from provider.ingestion_plugin import IngestionPluginProvider
        print(f"✅ IngestionPluginProvider imported successfully")
        
        from tools.ingestion_plugin import IngestionPluginTool
        print(f"✅ IngestionPluginTool imported successfully")
        
        print()
        return True
    
    except Exception as e:
        print(f"❌ Plugin import failed:")
        print(f"   Error: {str(e)}")
        print()
        return False

def create_sample_csv():
    """Create a sample CSV file for testing"""
    print("=" * 60)
    print("5️⃣  CREATING SAMPLE CSV FILE")
    print("=" * 60)
    
    csv_path = Path("test_data.csv")
    
    try:
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'salary', 'address', 'gpa', 'school'])
            writer.writeheader()
            writer.writerows([
                {'name': 'Alice Johnson', 'salary': '50000', 'address': '123 Main St', 'gpa': '3.8', 'school': 'State University'},
                {'name': 'Bob Smith', 'salary': '60000', 'address': '456 Oak Ave', 'gpa': '3.5', 'school': 'Tech Institute'},
                {'name': 'Charlie Brown', 'salary': '55000', 'address': '789 Pine Rd', 'gpa': '3.9', 'school': 'City College'},
                {'name': 'Diana Prince', 'salary': '70000', 'address': '321 Elm St', 'gpa': '4.0', 'school': 'Harvard'},
                {'name': 'Eve Wilson', 'salary': '45000', 'address': '654 Maple Ave', 'gpa': '3.6', 'school': 'Stanford'},
            ])
        
        print(f"✅ Sample CSV created: {csv_path}")
        print(f"   File path: {csv_path.absolute()}")
        print()
        return True
    
    except Exception as e:
        print(f"❌ Failed to create sample CSV:")
        print(f"   Error: {str(e)}")
        print()
        return False

def main():
    """Run all tests"""
    print("\n")
    print("🧪 INGESTION PLUGIN TEST SUITE")
    print("=" * 60)
    print()
    
    results = {
        "Environment": test_environment(),
        "Database Connection": test_database_connection(),
        "CSV Parsing": test_csv_parsing(),
        "Plugin Import": test_plugin_import(),
        "Sample CSV Creation": create_sample_csv(),
    }
    
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print()
    
    if all_passed:
        print("🎉 All tests passed! Plugin is ready to use.")
        print()
        print("Next steps:")
        print("1. Run: python main.py")
        print("2. Upload the test_data.csv file when prompted")
        print("3. Check your database for the csv_data table")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
    
    print()

if __name__ == '__main__':
    main()
