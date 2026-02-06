# 🧪 INGESTION PLUGIN - COMPLETE TESTING & EXECUTION GUIDE

## 📌 Plugin Overview (Tóm tắt)

**Tên Plugin:** `ingestion_plugin`  
**Chức năng:** Import CSV data vào PostgreSQL database  
**Yêu cầu:** Python 3.12, PostgreSQL, dify_plugin SDK

---

## 🔍 LOGIC & ARCHITECTURE (Chi tiết)

### **Luồng xử lý:**

```
┌─────────────────────────────────────────────────────────┐
│ User uploads CSV file through Dify                      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ main.py - Plugin Entry Point                            │
│ - Khởi tạo Plugin instance                             │
│ - Timeout: 120 giây                                    │
│ - Chạy server chờ request                              │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ provider/ingestion_plugin.py - Validate Credentials     │
│ - Kiểm tra: DB_HOST, DB_PORT, DB_NAME, DB_USER, PASS  │
│ - Test kết nối PostgreSQL                             │
│ - Raise exception nếu credential sai                  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ tools/ingestion_plugin.py - Main CSV Processing        │
│                                                         │
│ Step 1: Extract CSV File                              │
│   - Get from tool_parameters['csv_file']              │
│   - Convert bytes to string                           │
│                                                         │
│ Step 2: Parse & Validate CSV                          │
│   - Dùng csv.DictReader                              │
│   - Check required columns:                           │
│     * name (string)                                   │
│     * salary (decimal)                                │
│     * address (text)                                  │
│     * gpa (decimal)                                   │
│     * school (string)                                 │
│   - Return error nếu columns sai                     │
│                                                         │
│ Step 3: Connect to PostgreSQL                         │
│   - Use credentials from .env:                        │
│     * DB_HOST=10.1.0.4                               │
│     * DB_PORT=5432                                   │
│     * DB_NAME=difytest                               │
│     * DB_USER=dify                                   │
│     * DB_PASSWORD=123                                │
│                                                         │
│ Step 4: Create Table (if not exists)                 │
│   - Table: csv_data                                  │
│   - Columns:                                          │
│     id (SERIAL PRIMARY KEY)                          │
│     name VARCHAR(255)                                │
│     salary DECIMAL(15,2)                             │
│     address TEXT                                     │
│     gpa DECIMAL(3,2)                                 │
│     school VARCHAR(255)                              │
│     created_at TIMESTAMP (DEFAULT: now)              │
│                                                         │
│ Step 5: Bulk Insert Data                             │
│   - Convert CSV values to proper types               │
│   - Use execute_values() cho batch insert            │
│   - INSERT INTO csv_data VALUES (...)                │
│                                                         │
│ Step 6: Commit & Clean up                            │
│   - conn.commit() lưu changes                        │
│   - Close cursor & connection                        │
│   - Return success message + row count               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ JSON Response                                           │
│ {                                                       │
│   "status": "success" | "error",                       │
│   "message": "description",                            │
│   "rows_inserted": 5  // nếu success                   │
│ }                                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 File Structure Chi Tiết

### **main.py** (Entry point - 6 dòng)
```python
from dify_plugin import Plugin, DifyPluginEnv

plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=120))

if __name__ == '__main__':
    plugin.run()  # Khởi chạy plugin server
```

### **manifest.yaml** (Plugin metadata)
```yaml
version: 0.0.1
type: plugin                    # Kiểu: plugin
name: ingestion_plugin
author: ducthanhn
description: "Ingestion csv data to database"
meta:
  runner:
    language: python
    version: "3.12"             # Requires Python 3.12
  minimum_dify_version: null
```

### **provider/ingestion_plugin.py** (Credential validation)
```python
class IngestionPluginProvider(ToolProvider):
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # Kiểm tra các field bắt buộc
        required_fields = ['db_host', 'db_port', 'db_name', 'db_user', 'db_password']
        
        # Test kết nối PostgreSQL
        conn = psycopg2.connect(
            host=credentials.get('db_host'),
            port=int(credentials.get('db_port')),
            database=credentials.get('db_name'),
            user=credentials.get('db_user'),
            password=credentials.get('db_password')
        )
        conn.close()  # Nếu success, close; nếu fail, raise exception
```

### **tools/ingestion_plugin.py** (Main logic - ~80 dòng)
```python
class IngestionPluginTool(Tool):
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        
        # 1. Extract CSV
        csv_file = tool_parameters.get('csv_file')
        content = csv_file.read() if hasattr(csv_file, 'read') else csv_file
        
        # 2. Parse CSV
        csv_reader = csv.DictReader(io.StringIO(content))
        
        # 3. Validate columns: {name, salary, address, gpa, school}
        required_columns = {'name', 'salary', 'address', 'gpa', 'school'}
        if not required_columns.issubset(set(csv_reader.fieldnames)):
            yield error response
        
        # 4. Connect to PostgreSQL (from .env)
        conn = psycopg2.connect(...)
        cur = conn.cursor()
        
        # 5. Create table
        cur.execute("""CREATE TABLE IF NOT EXISTS csv_data (...)""")
        
        # 6. Insert rows
        rows = []
        for row in csv_reader:
            rows.append((
                row.get('name').strip() or None,
                float(row['salary']) if row.get('salary') else None,
                row.get('address').strip() or None,
                float(row['gpa']) if row.get('gpa') else None,
                row.get('school').strip() or None
            ))
        
        execute_values(cur, 'INSERT INTO csv_data (...) VALUES %s', rows)
        conn.commit()
        cur.close()
        conn.close()
        
        yield success response with row count
```

---

## 🔐 Environment Variables (.env)

```env
DB_HOST=10.1.0.4               # PostgreSQL server
DB_PORT=5432                   # PostgreSQL port
DB_NAME=difytest               # Database name
DB_USER=dify                   # Database user
DB_PASSWORD=123                # Database password (WEAK - change in production!)

INSTALL_METHOD=remote          # Installation method
REMOTE_INSTALL_URL=http://localhost:5003  # Remote installation URL
REMOTE_INSTALL_KEY=6aca79c0-eb7e-494c-8c28-cbbdfa0b23fd  # Installation key
```

---

## 🚀 CÁCH CHẠY & TEST PLUGIN

### **Bước 1: Cài đặt Dependencies**

```bash
cd c:\Users\dthanhnguyen\Project\plugin\ingestion_plugin

# Cài tất cả packages từ requirements.txt
pip install -r requirements.txt

# Hoặc cài từng cái:
pip install "dify_plugin>=0.4.0,<0.7.0"
pip install "psycopg2-binary==2.9.9"
```

**Packages cần cài:**
- `dify_plugin>=0.4.0,<0.7.0` - SDK của Dify
- `psycopg2-binary==2.9.9` - Driver PostgreSQL

### **Bước 2: Kiểm tra kết nối Database**

```bash
# Kiểm tra PostgreSQL có chạy không
# Command dưới đây sẽ kết nối tới DB
psql -h 10.1.0.4 -p 5432 -U dify -d difytest

# Nếu connect được, output:
# Password for user dify: 
# psql (version)
# Type "help" for help.
# difytest=>

# Kiểm tra bảng csv_data có tồn tại không
# difytest=> \dt csv_data

# List tất cả tables
# difytest=> \dt

# Thoát
# difytest=> \q
```

### **Bước 3: Tạo Sample CSV cho test**

File `test_data.csv` đã được tạo sẵn với nội dung:

```csv
name,salary,address,gpa,school
Alice Johnson,50000,123 Main St,3.8,State University
Bob Smith,60000,456 Oak Ave,3.5,Tech Institute
Charlie Brown,55000,789 Pine Rd,3.9,City College
Diana Prince,70000,321 Elm St,4.0,Harvard
Eve Wilson,45000,654 Maple Ave,3.6,Stanford
```

**⚠️ QUAN TRỌNG:** CSV phải có đúng 5 columns: `name`, `salary`, `address`, `gpa`, `school`

### **Bước 4: Chạy Plugin**

```bash
cd c:\Users\dthanhnguyen\Project\plugin\ingestion_plugin

# Chạy plugin server
python main.py

# Output sẽ tương tự:
# [2026-02-06 10:30:45] Starting plugin server...
# [2026-02-06 10:30:46] Server running on 0.0.0.0:5001
# [2026-02-06 10:30:46] Ready to accept requests
# Waiting for requests...
```

Plugin sẽ:
- Khởi chạy một server (thường port 5001 hoặc random port)
- Chờ request từ Dify application
- Xử lý CSV files khi nhận được

### **Bước 5: Test via Dify Application**

1. **Mở Dify application**
2. **Tạo Workflow/Agent** sử dụng `ingestion_plugin`
3. **Upload CSV file** (test_data.csv)
4. **Click "Run"** hoặc trigger plugin
5. **Xem Response:**
   - Success: `{"status": "success", "message": "Ingested 5 rows", "rows_inserted": 5}`
   - Error: `{"status": "error", "message": "..."}`

### **Bước 6: Kiểm tra Data trong Database**

```bash
# Kết nối tới database
psql -h 10.1.0.4 -p 5432 -U dify -d difytest

# Kiểm tra bảng được tạo
difytest=> \dt csv_data

# Xem tất cả dữ liệu
difytest=> SELECT * FROM csv_data;

# Xem số dòng inserted
difytest=> SELECT COUNT(*) FROM csv_data;

# Xem chi tiết
difytest=> SELECT id, name, salary, school, created_at FROM csv_data;
```

**Output mong đợi:**
```
 id |     name      | salary |      address      | gpa |        school        |         created_at
----+---------------+--------+-------------------+-----+----------------------+-------------------------------
  1 | Alice Johnson |  50000 | 123 Main St       | 3.8 | State University     | 2026-02-06 10:35:20.123456
  2 | Bob Smith     |  60000 | 456 Oak Ave       | 3.5 | Tech Institute       | 2026-02-06 10:35:20.123456
  3 | Charlie Brown |  55000 | 789 Pine Rd       | 3.9 | City College         | 2026-02-06 10:35:20.123456
  4 | Diana Prince  |  70000 | 321 Elm St        | 4.0 | Harvard              | 2026-02-06 10:35:20.123456
  5 | Eve Wilson    |  45000 | 654 Maple Ave     | 3.6 | Stanford             | 2026-02-06 10:35:20.123456
```

---

## ⚠️ LỖI THƯỜNG GẶP & CÁCH FIX

### **Lỗi 1: "No module named 'dify_plugin'"**

```
ModuleNotFoundError: No module named 'dify_plugin'
```

**Nguyên nhân:** Package chưa cài đặt  
**Fix:**
```bash
pip install dify_plugin==0.6.2
pip list | findstr dify_plugin  # Check if installed
```

### **Lỗi 2: "No module named 'psycopg2'"**

```
ModuleNotFoundError: No module named 'psycopg2'
```

**Nguyên nhân:** PostgreSQL driver chưa cài  
**Fix:**
```bash
pip install psycopg2-binary==2.9.9
# Hoặc nếu bị lỗi build:
pip install --upgrade setuptools wheel
pip install psycopg2-binary==2.9.9
```

### **Lỗi 3: "could not translate host name"**

```
psycopg2.OperationalError: could not translate host name "10.1.0.4"
```

**Nguyên nhân:** Không kết nối được tới PostgreSQL server  
**Fix:**
1. Kiểm tra IP: `ping 10.1.0.4`
2. Kiểm tra PostgreSQL đang chạy: `netstat -an | findstr 5432`
3. Kiểm tra firewall có block không
4. Verify credentials trong .env

### **Lỗi 4: "authentication failed for user"**

```
psycopg2.OperationalError: FATAL: password authentication failed for user "dify"
```

**Nguyên nhân:** Password sai  
**Fix:**
1. Check .env: DB_PASSWORD=123
2. Reset password PostgreSQL:
   ```sql
   ALTER USER dify WITH PASSWORD '123';
   ```

### **Lỗi 5: "database 'difytest' does not exist"**

```
psycopg2.OperationalError: FATAL: database "difytest" does not exist
```

**Nguyên nhân:** Database chưa tạo  
**Fix:**
```bash
# Connect as admin
psql -h 10.1.0.4 -U postgres

# Create database
postgres=> CREATE DATABASE difytest;
postgres=> GRANT ALL PRIVILEGES ON DATABASE difytest TO dify;
postgres=> \q
```

### **Lỗi 6: "CSV must contain: {required_columns}"**

```
{"status": "error", "message": "CSV must contain: {'name', 'salary', 'address', 'gpa', 'school'}"}
```

**Nguyên nhân:** CSV thiếu columns hoặc tên sai  
**Fix:**
```csv
# Kiểm tra test_data.csv có đúng header:
name,salary,address,gpa,school
(tất cả 5 columns bắt buộc)
```

### **Lỗi 7: "Request timeout"**

```
Error: Request timeout (exceeded 120 seconds)
```

**Nguyên nhân:** CSV quá lớn hoặc database chậm  
**Fix:**
```python
# Trong main.py, tăng timeout:
plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=300))  # 5 minutes
```

### **Lỗi 8: "could not insert empty tuple"**

```
psycopg2.ProgrammingError: invalid literal for type integer
```

**Nguyên nhân:** CSV có data invalid (ví dụ: salary="abc")  
**Fix:**
```csv
# Kiểm tra CSV:
# - name: bất kỳ string
# - salary: phải là số (int/float)
# - address: bất kỳ string
# - gpa: phải là số 0-4
# - school: bất kỳ string
```

---

## 📊 Expected Database Schema

```sql
CREATE TABLE csv_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),           -- Student/person name
    salary DECIMAL(15,2),        -- Salary amount
    address TEXT,                -- Address
    gpa DECIMAL(3,2),           -- GPA 0.00 to 4.00
    school VARCHAR(255),        -- School name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Inserted datetime
);
```

**Data types:**
| Column | Type | Example |
|--------|------|---------|
| id | SERIAL | 1, 2, 3, ... |
| name | VARCHAR(255) | "Alice Johnson" |
| salary | DECIMAL(15,2) | 50000.00 |
| address | TEXT | "123 Main St" |
| gpa | DECIMAL(3,2) | 3.80 |
| school | VARCHAR(255) | "State University" |
| created_at | TIMESTAMP | 2026-02-06 10:35:20.123456 |

---

## ✅ CHECKLIST TRƯỚC KHI CHẠY

- [ ] PostgreSQL đang chạy tại 10.1.0.4:5432
- [ ] Database `difytest` tồn tại
- [ ] User `dify` có password `123`
- [ ] `pip install -r requirements.txt` hoàn tất
- [ ] File `test_data.csv` được tạo sẵn
- [ ] Python 3.12+ (hoặc compatible version)
- [ ] Dify application đã khởi chạy

---

## 🎯 QUICK START

```bash
# 1. Cài dependencies
pip install -r requirements.txt

# 2. Kiểm tra DB connection
psql -h 10.1.0.4 -U dify -d difytest

# 3. Chạy plugin
python main.py

# 4. Trong terminal khác, test (optional):
python test_plugin.py

# 5. Dùng Dify UI để upload test_data.csv

# 6. Kiểm tra result:
psql -h 10.1.0.4 -U dify -d difytest -c "SELECT COUNT(*) FROM csv_data;"
```

---

## 📝 SUMMARY

✅ **Plugin hoàn toàn sẵn sàng để test**

**Chức năng chính:**
- ✅ Đọc CSV file
- ✅ Validate required columns
- ✅ Kết nối PostgreSQL
- ✅ Tạo table tự động
- ✅ Insert data (bulk)
- ✅ Return JSON response

**Environment setup:**
- ✅ .env có tất cả credentials
- ✅ Database credentials đúng
- ✅ Sample CSV sẵn sàng

**Tiếp theo:**
1. Cài dependencies: `pip install -r requirements.txt`
2. Run: `python main.py`
3. Upload CSV via Dify UI
4. Verify in database

Happy testing! 🚀
