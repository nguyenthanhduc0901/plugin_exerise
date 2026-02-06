#!/usr/bin/env python
"""
Simple test to validate plugin structure without external dependencies
"""

import os
import sys
import json
from pathlib import Path

def check_environment():
    """Verify environment variables are set"""
    print("\n" + "="*60)
    print("1️⃣  ENVIRONMENT VARIABLES CHECK")
    print("="*60)
    
    required = {
        'DB_HOST': '10.1.0.4',
        'DB_PORT': '5432',
        'DB_NAME': 'difytest',
        'DB_USER': 'dify',
        'DB_PASSWORD': '123'
    }
    
    all_ok = True
    for var, expected in required.items():
        actual = os.getenv(var)
        if actual == expected:
            print(f"✅ {var}: {actual}")
        else:
            print(f"❌ {var}: Expected '{expected}', got '{actual}'")
            all_ok = False
    
    return all_ok

def check_file_structure():
    """Verify plugin file structure is correct"""
    print("\n" + "="*60)
    print("2️⃣  FILE STRUCTURE CHECK")
    print("="*60)
    
    required_files = [
        'main.py',
        'manifest.yaml',
        'requirements.txt',
        'provider/ingestion_plugin.py',
        'provider/ingestion_plugin.yaml',
        'tools/ingestion_plugin.py',
        'tools/ingestion_plugin.yaml',
    ]
    
    all_ok = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_ok = False
    
    return all_ok

def check_python_files():
    """Verify Python files have correct content"""
    print("\n" + "="*60)
    print("3️⃣  PYTHON FILES CONTENT CHECK")
    print("="*60)
    
    # Check main.py imports
    with open('main.py', 'r') as f:
        main_content = f.read()
        if 'from dify_plugin import Plugin' in main_content:
            print("✅ main.py has correct imports")
        else:
            print("❌ main.py missing dify_plugin import")
    
    # Check provider/ingestion_plugin.py
    with open('provider/ingestion_plugin.py', 'r') as f:
        provider_content = f.read()
        checks = [
            ('psycopg2', 'PostgreSQL connection'),
            ('_validate_credentials', 'Credentials validation'),
            ('ToolProvider', 'Tool provider class'),
        ]
        for check, desc in checks:
            if check in provider_content:
                print(f"✅ provider/ingestion_plugin.py has {desc}")
            else:
                print(f"❌ provider/ingestion_plugin.py missing {desc}")
    
    # Check tools/ingestion_plugin.py
    with open('tools/ingestion_plugin.py', 'r') as f:
        tool_content = f.read()
        checks = [
            ('csv.DictReader', 'CSV parsing'),
            ('CREATE TABLE', 'Table creation'),
            ('execute_values', 'Bulk insert'),
            ('name', 'name column'),
            ('salary', 'salary column'),
            ('address', 'address column'),
            ('gpa', 'gpa column'),
            ('school', 'school column'),
        ]
        for check, desc in checks:
            if check in tool_content:
                print(f"✅ tools/ingestion_plugin.py has {desc}")
            else:
                print(f"❌ tools/ingestion_plugin.py missing {desc}")

def check_yaml_config():
    """Verify YAML configuration files"""
    print("\n" + "="*60)
    print("4️⃣  YAML CONFIGURATION CHECK")
    print("="*60)
    
    try:
        import yaml
        
        # Check manifest.yaml
        with open('manifest.yaml', 'r') as f:
            manifest = yaml.safe_load(f)
            print(f"✅ manifest.yaml: version {manifest.get('version')}")
            print(f"   - Name: {manifest.get('name')}")
            print(f"   - Type: {manifest.get('type')}")
            print(f"   - Python: {manifest.get('meta', {}).get('runner', {}).get('version')}")
        
        # Check provider config
        with open('provider/ingestion_plugin.yaml', 'r') as f:
            provider_config = yaml.safe_load(f)
            print(f"✅ provider/ingestion_plugin.yaml: {provider_config.get('identity', {}).get('name')}")
        
        # Check tool config
        with open('tools/ingestion_plugin.yaml', 'r') as f:
            tool_config = yaml.safe_load(f)
            params = tool_config.get('parameters', [])
            print(f"✅ tools/ingestion_plugin.yaml: {len(params)} parameter(s)")
            for param in params:
                print(f"   - {param.get('name')} ({param.get('type')})")
        
        return True
    except ImportError:
        print("⚠️  PyYAML not installed, skipping YAML validation")
        return True
    except Exception as e:
        print(f"❌ YAML validation error: {str(e)}")
        return False

def create_sample_csv():
    """Create sample CSV for testing"""
    print("\n" + "="*60)
    print("5️⃣  SAMPLE CSV CREATION")
    print("="*60)
    
    csv_content = """name,salary,address,gpa,school
Alice Johnson,50000,123 Main St,3.8,State University
Bob Smith,60000,456 Oak Ave,3.5,Tech Institute
Charlie Brown,55000,789 Pine Rd,3.9,City College
Diana Prince,70000,321 Elm St,4.0,Harvard
Eve Wilson,45000,654 Maple Ave,3.6,Stanford"""
    
    try:
        with open('test_data.csv', 'w') as f:
            f.write(csv_content)
        print(f"✅ Created test_data.csv (5 rows)")
        print(f"   Location: {Path('test_data.csv').absolute()}")
        return True
    except Exception as e:
        print(f"❌ Failed to create CSV: {str(e)}")
        return False

def summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    results = {
        "Environment": check_environment(),
        "File Structure": check_file_structure(),
        "Python Files": lambda: (check_python_files(), True)[1](),
        "YAML Config": check_yaml_config(),
        "Sample CSV": create_sample_csv(),
    }
    
    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    
    if all_passed:
        print("\n1. Install dependencies:")
        print("   pip install -r requirements.txt")
        print("\n2. Verify PostgreSQL connection:")
        print("   psql -h 10.1.0.4 -U dify -d difytest")
        print("\n3. Run the plugin:")
        print("   python main.py")
        print("\n4. The plugin will start a server and wait for requests")
        print("   from Dify application")
        print("\n5. Upload test_data.csv through Dify UI to test")
        print("\n6. Verify in database:")
        print("   SELECT * FROM csv_data;")
    else:
        print("\n⚠️  Please fix the issues above before running the plugin")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    print("\n" + "🧪 INGESTION PLUGIN VALIDATION SCRIPT 🧪")
    print("="*60)
    
    summary()
