# 🧪 INGESTION PLUGIN - COMPLETE ANALYSIS & TESTING GUIDE

## 📌 Quick Summary

This plugin ingests CSV data into PostgreSQL. It validates CSV format, creates a table if needed, and inserts all rows.

---

## 🔍 PLUGIN STRUCTURE & LOGIC

### **Project Layout**
```
ingestion_plugin/
├── main.py                          # Entry point - initializes plugin
├── manifest.yaml                    # Plugin metadata & configuration
├── requirements.txt                 # Python dependencies
├── provider/
│   ├── ingestion_plugin.py         # Credential validation provider
│   └── ingestion_plugin.yaml       # Provider configuration
├── tools/
│   ├── ingestion_plugin.py         # CSV ingestion tool logic
│   └── ingestion_plugin.yaml       # Tool input/output configuration
└── .env                            # Environment variables for DB connection
```

---

## 🚀 COMPONENT BREAKDOWN

### **1. main.py - Entry Point**
```python
from dify_plugin import Plugin, DifyPluginEnv

plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=120))

if __name__ == '__main__':
    plugin.run()
```

**What it does:**
- Creates a Plugin instance with 120-second timeout
- `plugin.run()` starts the plugin server
- Handles communication between Dify and the plugin

---

### **2. manifest.yaml - Plugin Metadata**
- **Name:** ingestion_plugin
- **Version:** 0.0.1
- **Type:** plugin
- **Author:** ducthanhn
- **Runtime:** Python 3.12
- **Memory:** 256MB
- **Description:** "Ingestion csv data to database"
- **Main Entry:** main.py

---

### **3. provider/ingestion_plugin.py - Credential Validation**

**Purpose:** Validates PostgreSQL credentials before the tool runs

**Function: `_validate_credentials()`**
```
Input: Dictionary with keys:
  - db_host      (required)
  - db_port      (required)
  - db_name      (required)
  - db_user      (required)
  - db_password  (required)

Logic:
  1. Check all required fields exist and are non-empty
  2. Try to connect to PostgreSQL
  3. Close connection
  4. Raise ToolProviderCredentialValidationError if fails

Output: Raises exception on error, succeeds silently if valid
```

---

### **4. tools/ingestion_plugin.py - CSV Ingestion Logic**

**Purpose:** Ingests CSV file into PostgreSQL database

**Function: `_invoke()` - Main Tool Logic**

```
INPUT:
  tool_parameters: {
    'csv_file': <File object or bytes>,
    'file': <Alternative file parameter>
  }

PROCESS FLOW:
  1. Get CSV file from parameters
  2. Convert bytes to string if needed
  3. Parse CSV using DictReader
  
  4. VALIDATION:
     ✓ Check CSV has required columns:
       - name, salary, address, gpa, school
     ✓ Return error if columns missing
  
  5. DATABASE CONNECTION:
     ✓ Get credentials from tool_runtime_data
     ✓ Connect to PostgreSQL
     ✓ Create cursor
  
  6. TABLE CREATION:
     ✓ Execute CREATE TABLE IF NOT EXISTS csv_data
     ✓ Columns:
       - id (SERIAL PRIMARY KEY)
       - name (VARCHAR 255)
       - salary (DECIMAL 15,2)
       - address (TEXT)
       - gpa (DECIMAL 3,2)
       - school (VARCHAR 255)
       - created_at (TIMESTAMP with default CURRENT_TIMESTAMP)
  
  7. DATA INSERTION:
     ✓ Loop through CSV rows
     ✓ Convert data types (salary & gpa to float)
     ✓ Use execute_values() for bulk insert
     ✓ INSERT INTO csv_data (name, salary, address, gpa, school) VALUES
  
  8. COMMIT & CLEANUP:
     ✓ Commit transaction
     ✓ Close cursor and connection
     ✓ Return success message with row count

OUTPUT:
  JSON Response:
  {
    'status': 'success' | 'error',
    'message': <description>,
    'rows_inserted': <count> (if success)
  }

ERROR HANDLING:
  - Returns JSON error message with exception details
  - Catches: missing file, invalid columns, DB errors, data type errors
```

---

### **5. tools/ingestion_plugin.yaml - Tool Definition**

**Parameter Definition:**
```yaml
Name: csv_file
Type: file
Required: true
Label: CSV File
Description: "CSV file with columns: name, salary, address, gpa, school"
```

**Required CSV Columns:**
- `name` - Student/person name
- `salary` - Numeric salary value
- `address` - Text address
- `gpa` - Grade point average (decimal)
- `school` - School name

---

## 🔗 DATABASE CONNECTION (from .env)

Your current environment variables:
```env
DB_HOST=10.1.0.4          # PostgreSQL server IP
DB_PORT=5432              # PostgreSQL port
DB_NAME=difytest          # Database name to use
DB_USER=dify              # Database user
DB_PASSWORD=123           # Database password
```

**Connection String (conceptually):**
```
postgresql://dify:123@10.1.0.4:5432/difytest
```

---

## 📊 WORKFLOW DIAGRAM

```
User uploads CSV file
         ↓
[main.py] - Receives request
         ↓
[Credential Provider] - Validates DB credentials
         ↓
[Tool - _invoke()] - Main logic
         ├─→ Extract CSV file from parameters
         ├─→ Parse CSV with DictReader
         ├─→ Validate required columns exist
         ├─→ Connect to PostgreSQL
         ├─→ CREATE TABLE IF NOT EXISTS csv_data
         ├─→ Convert row data types (str → float)
         ├─→ Bulk INSERT rows using execute_values()
         ├─→ COMMIT transaction
         └─→ Return JSON response
         ↓
JSON Response returned to Dify
```

---

## 🧪 TESTING GUIDE

### **Step 1: Verify Environment**
```bash
# Check if DB is accessible
$env:DB_HOST = "10.1.0.4"
$env:DB_PORT = "5432"
$env:DB_NAME = "difytest"
$env:DB_USER = "dify"
$env:DB_PASSWORD = "123"

# Try connecting via psql
psql -h 10.1.0.4 -p 5432 -U dify -d difytest
```

### **Step 2: Install Dependencies**
```bash
cd C:\Users\dthanhnguyen\Project\plugin\ingestion_plugin
pip install -r requirements.txt
```

Required packages:
- `dify_plugin>=0.4.0,<0.7.0` - Dify plugin SDK
- `psycopg2-binary==2.9.9` - PostgreSQL adapter

### **Step 3: Prepare Test CSV**
Create `test_data.csv`:
```csv
name,salary,address,gpa,school
Alice Johnson,50000,123 Main St,3.8,State University
Bob Smith,60000,456 Oak Ave,3.5,Tech Institute
Charlie Brown,55000,789 Pine Rd,3.9,City College
Diana Prince,70000,321 Elm St,4.0,Harvard
Eve Wilson,45000,654 Maple Ave,3.6,Stanford
```

### **Step 4: Run Plugin**
```bash
python main.py
```

This will:
- Start a local server (typically on localhost:5001 or similar port)
- Wait for requests from Dify
- Be ready to receive CSV files for ingestion

### **Step 5: Test via Dify UI**
1. Open Dify application
2. Create a workflow/agent that uses the ingestion_plugin
3. Upload test_data.csv through the UI
4. Check PostgreSQL database:
```sql
-- Check if table exists
\dt csv_data

-- View inserted data
SELECT * FROM csv_data;

-- Count rows
SELECT COUNT(*) FROM csv_data;
```

### **Step 6: Verify Data in Database**
```sql
-- Login to database
psql -h 10.1.0.4 -p 5432 -U dify -d difytest

-- List tables
\dt

-- Check csv_data table structure
\d csv_data

-- View sample data
SELECT * FROM csv_data LIMIT 5;

-- Check total rows
SELECT COUNT(*) as total_rows FROM csv_data;
```

---

## ⚠️ COMMON ISSUES & TROUBLESHOOTING

### **Issue 1: "Database connection failed"**
```
Symptoms: ❌ Database connection refused
Solution:
  1. Check if PostgreSQL is running on 10.1.0.4:5432
  2. Verify firewall allows connection
  3. Confirm credentials in .env are correct
  4. Test with psql: psql -h 10.1.0.4 -U dify -d difytest
```

### **Issue 2: "CSV must contain: {required_columns}"**
```
Symptoms: ❌ Error about missing columns
Solution:
  1. Verify CSV has exactly these columns:
     - name, salary, address, gpa, school
  2. Check column names are EXACTLY as specified (case-sensitive)
  3. Ensure NO extra/missing columns
  4. Use the test_data.csv provided above
```

### **Issue 3: "psycopg2-binary" installation fails**
```
Symptoms: ModuleNotFoundError: No module named 'psycopg2'
Solution:
  1. Install build tools if on Windows
  2. Try: pip install --upgrade setuptools wheel
  3. Then: pip install psycopg2-binary==2.9.9
  4. If still fails, use Docker PostgreSQL adapter
```

### **Issue 4: "dify_plugin" not found**
```
Symptoms: ModuleNotFoundError: No module named 'dify_plugin'
Solution:
  1. Verify pip install completed: pip list | grep dify_plugin
  2. Ensure Python version is 3.12 or compatible
  3. Reinstall: pip install dify_plugin==0.6.2
```

### **Issue 5: Request timeout (>120 seconds)**
```
Symptoms: ⏱️ Operation takes too long
Solution:
  1. Modify MAX_REQUEST_TIMEOUT in main.py
  2. Change to: MAX_REQUEST_TIMEOUT=300  (5 minutes)
  3. Reduce CSV file size if too large
```

---

## 📈 DATA TYPES & CONVERSION

The plugin converts CSV string data to PostgreSQL types:

| CSV Field  | CSV Type | PostgreSQL Type | Conversion |
|-----------|----------|-----------------|-----------|
| name      | string   | VARCHAR(255)    | .strip() or NULL |
| salary    | string   | DECIMAL(15,2)   | float() |
| address   | string   | TEXT            | .strip() or NULL |
| gpa       | string   | DECIMAL(3,2)    | float() |
| school    | string   | VARCHAR(255)    | .strip() or NULL |

**Null handling:**
- Empty string → NULL (for name, address, school)
- Missing salary/gpa → NULL

---

## 🔐 Security Notes

⚠️ **Current Setup:**
- DB credentials stored in .env file (plain text)
- Password is "123" (very weak)
- Consider for production:
  1. Use strong passwords
  2. Use environment variables or secrets vault
  3. Implement OAuth if available
  4. Use SSL/TLS for DB connection

---

## 🎯 NEXT STEPS

1. **Verify PostgreSQL is accessible** at 10.1.0.4:5432
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Create test CSV** with the sample data provided
4. **Run**: `python main.py`
5. **Test via Dify UI** by uploading CSV file
6. **Query PostgreSQL** to verify data was inserted

---

## 📝 Summary

Your plugin is a **CSV → PostgreSQL ingestion tool** that:
✅ Validates CSV format (requires 5 specific columns)
✅ Connects to PostgreSQL database
✅ Creates `csv_data` table automatically
✅ Bulk inserts CSV rows with proper type conversion
✅ Returns success/error status

The plugin is well-structured and ready for testing!
