# 🚀 PLUGIN CHẠY NGAY LẬP TỨC

## Tóm tắt Plugin

**Tên:** `ingestion_plugin`  
**Chức năng:** Import CSV → PostgreSQL  
**Ngôn ngữ:** Python 3.12  
**Dependencies:** dify_plugin, psycopg2-binary  

---

## 📋 Plugin Logic (Quá trình xử lý)

```
CSV File → [Parse] → [Validate] → [Connect DB] → [Create Table] → [Insert] → Response
   ↓
- Extract csv_file parameter
- Parse CSV with DictReader
- Check required columns: name, salary, address, gpa, school
- Connect to 10.1.0.4:5432 with user "dify"
- CREATE TABLE IF NOT EXISTS csv_data (...)
- INSERT rows using execute_values() for bulk insert
- Return: {"status": "success", "message": "Ingested X rows", "rows_inserted": X}
```

---

## ⚡ Quick Start (3 bước)

### **Bước 1: Cài Dependencies**
```bash
cd c:\Users\dthanhnguyen\Project\plugin\ingestion_plugin
pip install -r requirements.txt
```

### **Bước 2: Chạy Plugin**
```bash
python main.py
```
→ Server khởi động, chờ request từ Dify

### **Bước 3: Test**
- Mở Dify UI
- Upload `test_data.csv` 
- Xem database: `SELECT * FROM csv_data;`

---

## 📂 File Structure

```
ingestion_plugin/
├── main.py                     ← Entry point (khởi chạy plugin)
├── manifest.yaml               ← Plugin metadata
├── requirements.txt            ← Dependencies (dify_plugin, psycopg2)
├── .env                        ← DB credentials (10.1.0.4:5432)
├── provider/
│   ├── ingestion_plugin.py    ← Validate credentials
│   └── ingestion_plugin.yaml  ← Provider config
├── tools/
│   ├── ingestion_plugin.py    ← CSV processing logic (main logic!)
│   └── ingestion_plugin.yaml  ← Tool definition
├── test_data.csv              ← Sample CSV for testing (5 rows)
├── PLUGIN_ANALYSIS.md          ← Detailed analysis
└── TESTING_GUIDE_VI.md         ← Vietnamese testing guide
```

---

## 🔍 Core Logic (tools/ingestion_plugin.py)

```python
def _invoke(self, tool_parameters):
    # 1. Get CSV
    csv_file = tool_parameters.get('csv_file')
    
    # 2. Parse & Validate
    csv_reader = csv.DictReader(...)
    required_columns = {'name', 'salary', 'address', 'gpa', 'school'}
    if columns not match:
        return error
    
    # 3. Connect to DB (from .env)
    conn = psycopg2.connect(
        host='10.1.0.4',
        port=5432,
        database='difytest',
        user='dify',
        password='123'
    )
    
    # 4. Create table
    CREATE TABLE IF NOT EXISTS csv_data (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        salary DECIMAL(15,2),
        address TEXT,
        gpa DECIMAL(3,2),
        school VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW()
    )
    
    # 5. Insert rows
    execute_values(cur, 'INSERT INTO csv_data VALUES %s', rows)
    conn.commit()
    
    # 6. Return response
    return {"status": "success", "rows_inserted": 5}
```

---

## 📊 Database Connection

```
From: .env file
Host:     10.1.0.4
Port:     5432
Database: difytest
User:     dify
Password: 123
```

**Test connection:**
```bash
psql -h 10.1.0.4 -p 5432 -U dify -d difytest
```

---

## 📝 CSV Format Required

```csv
name,salary,address,gpa,school
Alice Johnson,50000,123 Main St,3.8,State University
Bob Smith,60000,456 Oak Ave,3.5,Tech Institute
Charlie Brown,55000,789 Pine Rd,3.9,City College
Diana Prince,70000,321 Elm St,4.0,Harvard
Eve Wilson,45000,654 Maple Ave,3.6,Stanford
```

**⚠️ MUST HAVE:**
- Exactly 5 columns: `name`, `salary`, `address`, `gpa`, `school`
- `salary` and `gpa` must be numeric
- Column names must match exactly (case-sensitive)

---

## 🔧 Running Plugin

```bash
# Install dependencies (if not done)
pip install -r requirements.txt

# Run plugin server
python main.py

# Expected output:
# [INFO] Starting ingestion_plugin...
# [INFO] Server listening on 0.0.0.0:port
# [INFO] Ready to accept requests
# Waiting for requests...
```

Then:
1. Open Dify application
2. Create workflow using ingestion_plugin
3. Upload CSV file
4. Click run/execute
5. Check database

---

## ✅ Verify Results

```bash
# Connect to database
psql -h 10.1.0.4 -p 5432 -U dify -d difytest

# Check data
difytest=> SELECT COUNT(*) FROM csv_data;

# View all rows
difytest=> SELECT * FROM csv_data;

# Expected: 5 rows inserted from test_data.csv
```

---

## 🚨 Common Errors

| Error | Solution |
|-------|----------|
| `No module named 'dify_plugin'` | `pip install dify_plugin` |
| `No module named 'psycopg2'` | `pip install psycopg2-binary` |
| `could not translate host name "10.1.0.4"` | Check if PostgreSQL running at that IP |
| `password authentication failed` | Check DB_PASSWORD in .env is "123" |
| `database "difytest" does not exist` | Create database: `CREATE DATABASE difytest;` |
| `CSV must contain: {'name'...}` | Check CSV has exact 5 columns with right names |

---

## 📚 Files Created for You

1. **PLUGIN_ANALYSIS.md** - Detailed component breakdown
2. **TESTING_GUIDE_VI.md** - Full Vietnamese testing guide  
3. **test_data.csv** - Sample CSV for testing (5 rows)
4. **test_plugin.py** - Full test suite
5. **validate_plugin.py** - Quick validation script
6. **QUICKSTART.md** - This file

---

## 🎯 Next Actions

1. ✅ **Understand** - Read PLUGIN_ANALYSIS.md for detailed logic
2. ✅ **Setup** - Install dependencies: `pip install -r requirements.txt`
3. ✅ **Run** - Start plugin: `python main.py`
4. ✅ **Test** - Upload test_data.csv via Dify UI
5. ✅ **Verify** - Query database to confirm data inserted

---

## 🔐 Security Note

⚠️ Current setup uses weak credentials for testing. For production:
- Change password from "123" to strong password
- Use environment variables or secrets manager
- Enable SSL/TLS for DB connection
- Don't commit .env to git

---

**Ready to test!** Run `python main.py` now! 🚀
