# PRIORITY 4 - QUICK REFERENCE GUIDE

**Created:** January 27, 2026  
**For:** CRM Downloader v4.0+ Development  

---

## 🎯 THE 15 FEATURES AT A GLANCE

| # | Feature | Category | Complexity | Hours | Value | Phase |
|---|---------|----------|-----------|-------|-------|-------|
| 1 | Google Drive Sync | Cloud | HARD | 30 | HIGH | 4 |
| 2 | OneDrive/SharePoint | Cloud | HARD | 28 | HIGH | 4 |
| 3 | S3/AWS Backup | Cloud | MEDIUM | 15 | MEDIUM | 4 |
| 4 | Web UI Dashboard | API/Web | HARD | 35 | HIGH | 2 |
| 5 | REST API Server | API/Web | HARD | 32 | HIGH | 2 |
| 6 | Task Scheduler | Automation | MEDIUM | 14 | HIGH | 1 |
| 7 | Webhook Notifications | Automation | MEDIUM | 12 | MEDIUM | 1 |
| 8 | Config Encryption | Security | MEDIUM | 10 | HIGH | 1 |
| 9 | Download Resumption | Reliability | MEDIUM | 14 | HIGH | 3 |
| 10 | Performance Optimization | Performance | MEDIUM | 16 | MEDIUM | 3 |
| 11 | File Processing Pipeline | Advanced | HARD | 24 | MEDIUM | 5 |
| 12 | Metadata Extraction | Advanced | MEDIUM | 14 | MEDIUM | 5 |
| 13 | Advanced Logging | Monitoring | MEDIUM | 16 | MEDIUM | 3 |
| 14 | Database Persistence | Scalability | HARD | 25 | MEDIUM | 5 |
| 15 | Network Intelligence | Resilience | HARD | 20 | MEDIUM | 5 |

---

## ⚡ IMPLEMENTATION BY PHASE

### Phase 1: Foundation & Security (36 hours) - Weeks 1-2

**Feature #8: Config Encryption** (10 hours)
```
Prerequisites: cryptography library
Changes: load_config(), config security
Risk: LOW
Tests needed: Encryption/decryption roundtrip
```

**Feature #6: Task Scheduler** (14 hours)
```
Prerequisites: apscheduler
Changes: New ScheduleManager class, background worker
Risk: MEDIUM (background process)
Tests needed: Schedule creation, execution, persistence
```

**Feature #7: Webhook Notifications** (12 hours)
```
Prerequisites: None (uses requests)
Changes: Extend notify_completion()
Risk: LOW
Tests needed: Discord, Slack, Telegram integration
```

---

### Phase 2: API & Web Interface (67 hours) - Weeks 3-4

**Feature #5: REST API (FastAPI)** (32 hours)
```
Prerequisites: fastapi, uvicorn
Key endpoints:
  - POST /api/download
  - GET /api/history
  - GET /api/stats
  - PUT /api/config
  - POST /api/schedule
  - POST /api/webhooks
Changes: Service layer refactor, dependency injection
Risk: HIGH (architectural change)
Tests needed: All endpoints, auth, rate limiting
```

**Feature #4: Web Dashboard (Flask)** (35 hours)
```
Prerequisites: flask, flask-cors, Bootstrap 5
Pages:
  - Dashboard (realtime stats)
  - History (searchable table)
  - Upload (single + batch)
  - Config (editor)
  - Logs (viewer)
Changes: Serve static files, API calls
Risk: MEDIUM (frontend complexity)
Tests needed: UI responsiveness, API integration
```

---

### Phase 3: Reliability & Performance (46 hours) - Weeks 5-6

**Feature #9: Download Resumption** (14 hours)
```
Prerequisites: None (native in requests)
Key changes:
  - HTTP Range header support
  - Resume state tracking
  - Partial file verification
Risk: MEDIUM (state management)
Tests needed: Interrupt/resume scenarios
```

**Feature #10: Performance Optimization** (16 hours)
```
Prerequisites: requests-cache (or custom)
Optimizations:
  - ETag-based caching
  - Bandwidth throttling
  - Compression support
Risk: LOW
Tests needed: Speed benchmarks
```

**Feature #13: Advanced Logging** (16 hours)
```
Prerequisites: python-json-logger
Changes:
  - Structured logging (JSON)
  - Metrics collection (Prometheus)
  - Log rotation
Risk: LOW
Tests needed: Log format, metrics collection
```

---

### Phase 4: Cloud & Enterprise (73 hours) - Weeks 7-8

**Feature #3: S3/AWS Integration** (15 hours)
```
Prerequisites: boto3
Features:
  - S3 bucket upload
  - Lifecycle policies
  - Cost tracking
Risk: MEDIUM (AWS API)
Tests needed: S3 operations, error handling
```

**Feature #1: Google Drive Sync** (30 hours)
```
Prerequisites: google-auth-oauthlib, google-api-python-client
Key requirement: CloudProvider abstraction
Features:
  - OAuth 2.0
  - Two-way sync
  - Conflict resolution
Risk: HIGH (OAuth, state sync)
Tests needed: Auth flow, sync logic, conflict resolution
```

**Feature #2: OneDrive/SharePoint** (28 hours)
```
Prerequisites: msal, msgraph-core
Uses: CloudProvider abstraction from Feature #1
Risk: HIGH
Tests needed: Azure AD auth, sync operations
```

---

### Phase 5: Advanced Features (83 hours) - Weeks 9-10+

**Feature #14: Database Persistence** (25 hours)
```
Prerequisites: sqlalchemy, alembic
Schema: Downloads, Schedules, Webhooks, Logs
Risk: HIGH (major refactor)
Strategy: Support both JSON and DB in parallel
```

**Feature #11: File Processing Pipeline** (24 hours)
```
Prerequisites: pillow, optional: pymupdf, pytesseract
Pattern: Plugin system with processors
Processors: Image, Archive, PDF, Video
Risk: MEDIUM
```

**Feature #12: Metadata Extraction** (14 hours)
```
Prerequisites: piexif, pymupdf, python-magic
Features:
  - EXIF extraction
  - PDF metadata
  - Auto-organization
Risk: LOW
```

**Feature #15: Network Intelligence** (20 hours)
```
Prerequisites: icmplib, optional: pysocks
Features:
  - Availability detection
  - Failover handling
  - Queue management
Risk: MEDIUM
```

---

## 🛠️ DEPENDENCIES BY CATEGORY

### Python Packages to Add

**Phase 1:**
```
cryptography>=40.0
apscheduler>=3.10
```

**Phase 2:**
```
fastapi>=0.100
uvicorn>=0.20
flask>=2.3
flask-cors>=4.0
```

**Phase 3:**
```
requests-cache>=1.1
prometheus-client>=0.17
```

**Phase 4:**
```
google-auth-oauthlib>=1.0
google-api-python-client>=2.90
msal>=1.24
msgraph-core>=0.2
boto3>=1.28
```

**Phase 5:**
```
sqlalchemy>=2.0
alembic>=1.12
pillow>=10.0
pymupdf>=1.23
piexif>=1.1
python-magic>=0.4
icmplib>=3.0
```

---

## 🏗️ REQUIRED REFACTORING

### Current Structure
```
downloader.py
  ├─ load_config()
  ├─ process_url()
  └─ download_single_file()

menu.py
  └─ MenuManager
```

### Proposed Structure (After Refactoring)

```
downloader/
  ├─ core/
  │  ├─ __init__.py
  │  ├─ service.py          (DownloadService - extracts logic)
  │  ├─ stats.py            (DownloadStats - existing)
  │  └─ config.py           (ConfigManager - new)
  │
  ├─ features/
  │  ├─ scheduler.py        (Phase 1)
  │  ├─ notifications.py    (Phase 1)
  │  ├─ cloud/
  │  │  ├─ providers.py     (Phase 4)
  │  │  └─ sync.py          (Phase 4)
  │  ├─ processing/         (Phase 5)
  │  └─ database/           (Phase 5)
  │
  ├─ interfaces/
  │  ├─ cli.py             (existing downloader.py)
  │  ├─ web.py             (Phase 2 - Flask)
  │  ├─ api.py             (Phase 2 - FastAPI)
  │  └─ menu.py            (existing menu.py)
  │
  └─ tests/
     ├─ test_core.py
     ├─ test_features.py
     ├─ test_interfaces.py
     └─ test_integration.py
```

---

## 🔑 KEY CLASSES TO IMPLEMENT

### Phase 1
```python
class CryptoManager:
    def encrypt(data: dict, password: str) -> str
    def decrypt(data: str, password: str) -> dict

class ScheduleManager:
    def add_schedule(trigger: str, url: str) -> Schedule
    def list_schedules() -> List[Schedule]
    def execute(schedule_id: str) -> Result

class WebhookNotifier:
    def send_discord(url: str, message: dict) -> bool
    def send_slack(webhook_url: str, message: dict) -> bool
    def send_telegram(token: str, chat_id: str, message: str) -> bool
```

### Phase 2
```python
class DownloadService:  # REFACTORED
    def process_url(url: str) -> Result
    def get_history() -> List[Download]
    def get_stats() -> Stats

class FastAPIServer(FastAPI):
    @post("/api/download")
    async def create_download(url: str): ...

class FlaskDashboard(Flask):
    @get("/")
    def dashboard(): ...
    
    @get("/api/stats")
    def get_stats(): ...
```

### Phase 3
```python
class ResumeManager:
    def can_resume(file_path: Path) -> bool
    def get_resume_offset(file_path: Path) -> int
    def save_resume_state(file_path: Path, offset: int)

class MetricsCollector:
    def emit_counter(name: str, value: int)
    def emit_gauge(name: str, value: float)
    def emit_histogram(name: str, value: float)
```

### Phase 4
```python
class CloudProvider:  # ABSTRACT
    async def upload(local_path: Path, remote_path: str) -> bool
    async def download(remote_path: str, local_path: Path) -> bool

class GoogleDriveProvider(CloudProvider):
    def __init__(self, credentials_path: str, token_path: str)
    # Implementation

class OneDriveProvider(CloudProvider):
    def __init__(self, client_id: str, client_secret: str, tenant_id: str)
    # Implementation
```

### Phase 5
```python
class FileProcessor:  # ABSTRACT
    def process(file_path: Path) -> ProcessResult

class ImageProcessor(FileProcessor): ...
class ArchiveProcessor(FileProcessor): ...
class PDFProcessor(FileProcessor): ...

class ProcessorRegistry:
    def register(extensions: List[str], processor: FileProcessor)
    def process(file_path: Path) -> ProcessResult

class MetadataExtractor:
    def extract_exif(image_path: Path) -> dict
    def extract_pdf_metadata(pdf_path: Path) -> dict
    def organize_by_metadata(file_path: Path) -> Path
```

---

## 📊 EFFORT & RISK MATRIX

```
EASY WINS (Low effort, High reward)
├─ #8 Config Encryption              10 hrs  🟢 LOW RISK
├─ #7 Webhooks                        12 hrs  🟢 LOW RISK
└─ #6 Task Scheduler                 14 hrs  🟡 MEDIUM RISK

MEDIUM EFFORT (Good value)
├─ #3 S3 Integration                 15 hrs  🟡 MEDIUM RISK
├─ #10 Performance Optimization      16 hrs  🟢 LOW RISK
├─ #13 Advanced Logging              16 hrs  🟢 LOW RISK
├─ #9 Download Resumption            14 hrs  🟡 MEDIUM RISK
└─ #12 Metadata Extraction           14 hrs  🟢 LOW RISK

MEDIUM-HIGH EFFORT
├─ #15 Network Intelligence          20 hrs  🟡 MEDIUM RISK
├─ #11 File Processing               24 hrs  🟡 MEDIUM RISK
├─ #14 Database Persistence          25 hrs  🟠 HIGH RISK
├─ #2 OneDrive Sync                  28 hrs  🔴 HIGH RISK
├─ #5 REST API                       32 hrs  🟡 MEDIUM RISK
└─ #1 Google Drive Sync              30 hrs  🔴 HIGH RISK

MAJOR EFFORT
└─ #4 Web Dashboard                  35 hrs  🟡 MEDIUM RISK
```

---

## ✅ RECOMMENDED START ORDER (By Value/Effort Ratio)

### TIER 1: Do First (This Sprint)
1. **#8 Config Encryption** ⭐ (Security, quick)
2. **#6 Task Scheduler** ⭐ (High value, medium effort)
3. **#7 Webhooks** ⭐ (Team collaboration)

**Expected Result:** Core security + automation

### TIER 2: Do Next (Next Sprint)
4. **#5 REST API** ⭐ (Foundation for integrations)
5. **#4 Web Dashboard** ⭐ (Modern UX)

**Expected Result:** Browser interface, external integrations

### TIER 3: Do After (Following Sprint)
6. **#9 Download Resumption** (Reliability)
7. **#13 Advanced Logging** (Observability)
8. **#10 Performance Optimization** (Efficiency)

**Expected Result:** Robust, observable system

### TIER 4: Extended Roadmap
9. **#3 S3 Integration** (Cloud backup option)
10. **#1 Google Drive Sync** (Cloud sync - major feature)
11. **#2 OneDrive Sync** (Enterprise option)
12. **#12 Metadata Extraction** (Smart organization)
13. **#11 File Processing** (Content transformation)
14. **#14 Database** (Scalability)
15. **#15 Network Intelligence** (Network robustness)

---

## 🧪 TESTING STRATEGY

### Unit Tests (Per Feature)
```
- Encryption/decryption
- Schedule CRUD operations
- Webhook message formatting
- API endpoint contracts
- Resume logic
- Metadata extraction
```

### Integration Tests
```
- Scheduler executes downloads
- Notifications sent after completion
- API + Web Dashboard communication
- Cloud upload + sync
- File processing pipeline
```

### E2E Tests
```
- Complete download workflow
- Scheduled download execution
- Web UI workflow (login → download → view history)
- API workflow (create schedule → trigger → check status)
```

---

## 📝 DEPENDENCY GRAPH

```
#8 (Encryption) 
  ↓ (extends config loading)

#6 (Scheduler) → #7 (Webhooks)
  ↓
  ├─→ #5 (REST API) ← Core refactor
  │     ↓
  │     └─→ #4 (Web Dashboard)
  │           ├─→ #12 (Metadata)
  │           └─→ #11 (Processing)
  │
  └─→ #9 (Resumption)
        ↓
        └─→ #13 (Logging)
              ↓
              └─→ #10 (Optimization)

#3 (S3) ─────┐
             ├─→ #1 (Google Drive) ─┐
             │        ↓              │
             │    (CloudProvider)    │
             │        ↑              ├─→ #14 (Database)
             └────→ #2 (OneDrive) ──┘
                        ↓
                    #15 (Network)
```

---

## 🚀 QUICK START CHECKLIST FOR PHASE 1

- [ ] Create feature branches for each feature (#8, #6, #7)
- [ ] Add dependencies to requirements.txt
- [ ] Design CryptoManager API
- [ ] Design ScheduleManager API
- [ ] Design WebhookNotifier API
- [ ] Write unit tests first (TDD)
- [ ] Implement encryption layer
- [ ] Implement scheduler with background worker
- [ ] Integrate webhooks with notify_completion()
- [ ] Add configuration options to config.json
- [ ] Update README with new features
- [ ] Create example schedule file
- [ ] Create example webhook configurations
- [ ] Test end-to-end: Schedule → Execute → Notify
- [ ] Code review & merge to main

---

## 📞 SUPPORT RESOURCES

**For Cloud Integration:**
- Google Workspace API: https://developers.google.com/workspace/
- Microsoft Graph API: https://learn.microsoft.com/en-us/graph/
- AWS S3 Documentation: https://docs.aws.amazon.com/s3/

**For Web Development:**
- FastAPI: https://fastapi.tiangolo.com/
- Flask: https://flask.palletsprojects.com/
- Socket.IO: https://socket.io/

**For Scheduling:**
- APScheduler: https://apscheduler.readthedocs.io/

**For Security:**
- cryptography library: https://cryptography.io/

---

**Version:** 1.0  
**Last Updated:** January 27, 2026  
**Next Review:** After Phase 1 kickoff
