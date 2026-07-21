# PRIORITY 4 - TECHNICAL SPECIFICATIONS & ARCHITECTURE

**Created:** January 27, 2026  
**Type:** Architectural Design Document  

---

## 📐 CURRENT ARCHITECTURE ANALYSIS

### System Diagram (Current State - PRIORITY 1-3)

```
┌─────────────────────────────────────────────────────────┐
│                   CRM Downloader v3.0                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  CLI Interface                                          │
│  ├─ downloader.py (main entry)                         │
│  └─ menu.py (interactive menu)                         │
│                                                         │
│  Core Services                                          │
│  ├─ DownloadStats (metrics)                            │
│  ├─ ConfigManager (load_config)                        │
│  ├─ FileFiltering (should_download_file)              │
│  ├─ NotificationSystem (notify_completion)             │
│  └─ DownloadLogic (download_single_file)              │
│                                                         │
│  Utilities                                              │
│  ├─ MD5 Detection                                       │
│  ├─ History Management (JSON)                          │
│  ├─ Disk Space Checking                                │
│  └─ File Organization                                  │
│                                                         │
│  Storage                                                │
│  ├─ config.json                                        │
│  ├─ download_history.json                              │
│  └─ logs/downloader_*.log                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Current Data Flow

```
┌─────────────┐
│  User Input │ (CLI/Menu)
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Argument Parsing    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Load Config + Initialize Logger │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Check Disk Space                │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Process URL (get links)         │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ ThreadPool: Download Single File            │
│ ├─ Check Filters                            │
│ ├─ Download with progress bar               │
│ ├─ Calculate MD5                            │
│ └─ Save History + Stats                     │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Display Statistics + Notify     │
└─────────────────────────────────┘
```

---

## 🏗️ PROPOSED PRIORITY 4 ARCHITECTURE

### Layered Architecture Model

```
┌──────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                          │
├──────────────────────────────────────────────────────────────┤
│  CLI             Menu          Web UI (Flask)  API (FastAPI) │
│  ├─ argparse     ├─ Tables     ├─ Dashboard   ├─ REST        │
│  ├─ Progress     ├─ Dialogs    ├─ History     ├─ Swagger     │
│  └─ Logging      └─ Options    └─ Config      └─ Auth        │
└──────────────────────────────────────────────────────────────┘
                             ▲
                             │
┌──────────────────────────────────────────────────────────────┐
│                   SERVICE LAYER (CORE)                       │
├──────────────────────────────────────────────────────────────┤
│  DownloadService (REFACTORED)                                │
│  ├─ process_url(url) → Result                                │
│  ├─ get_history(filter) → List[Download]                     │
│  ├─ get_stats() → Statistics                                 │
│  └─ validate_config() → bool                                 │
│                                                              │
│  ScheduleService (Phase 1)                                   │
│  ├─ create_schedule(trigger, url)                            │
│  ├─ execute_schedule(id)                                     │
│  └─ list_schedules()                                         │
│                                                              │
│  CloudService (Phase 4)                                      │
│  ├─ upload_to_provider(file, provider)                       │
│  ├─ sync_with_cloud()                                        │
│  └─ resolve_conflicts()                                      │
│                                                              │
│  ProcessingService (Phase 5)                                 │
│  ├─ process_file(file, plugins)                              │
│  ├─ extract_metadata(file)                                   │
│  └─ organize_by_metadata()                                   │
└──────────────────────────────────────────────────────────────┘
                             ▲
                             │
┌──────────────────────────────────────────────────────────────┐
│                  DOMAIN LAYER (ENTITIES)                     │
├──────────────────────────────────────────────────────────────┤
│  Download (data class)          │  Schedule (data class)     │
│  ├─ url: str                    │  ├─ id: str                │
│  ├─ filename: str               │  ├─ trigger: str           │
│  ├─ size: int                   │  ├─ url: str               │
│  ├─ status: DownloadStatus      │  ├─ next_run: datetime     │
│  ├─ md5: str                    │  └─ enabled: bool          │
│  ├─ created_at: datetime        │                            │
│  └─ updated_at: datetime        │  CloudCredential (encrypted)│
│                                 │  ├─ provider: str          │
│  Statistics (data class)        │  ├─ credentials: dict      │
│  ├─ total_bytes: int            │  └─ expires_at: datetime   │
│  ├─ duration: float             │                            │
│  ├─ speed_mbps: float           │  ProcessingJob (queued)    │
│  └─ success_rate: float         │  ├─ input_file: Path      │
│                                 │  ├─ processor: str        │
│                                 │  ├─ output_file: Path     │
│                                 │  └─ status: JobStatus     │
└──────────────────────────────────────────────────────────────┘
                             ▲
                             │
┌──────────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                         │
├──────────────────────────────────────────────────────────────┤
│  Data Access (Repository Pattern)                            │
│  ├─ JSONRepository (current)    │  ├─ CloudProviderFactory  │
│  ├─ SQLRepository (Phase 5)      │  └─ CredentialVault       │
│  └─ HistoryRepository           │                            │
│                                 │  File System Access       │
│  Config Management              │  ├─ FileSystemDriver      │
│  ├─ ConfigLoader                │  ├─ PathResolver          │
│  ├─ CryptoManager (Phase 1)      │  └─ FileOrganizer        │
│  └─ ConfigValidator             │                            │
│                                 │  Logging & Observability  │
│  Network / External Services    │  ├─ StructuredLogger      │
│  ├─ HTTPClient (requests)        │  ├─ MetricsCollector     │
│  ├─ CloudProvider (abstract)     │  └─ HealthCheckEndpoint  │
│  ├─ WebhookSender               │                            │
│  └─ NotificationDispatcher      │  Queue & Scheduling      │
│                                 │  ├─ APScheduler Backend   │
│                                 │  ├─ ProcessingQueue      │
│                                 │  └─ BackgroundWorker     │
└──────────────────────────────────────────────────────────────┘
                             ▲
                             │
┌──────────────────────────────────────────────────────────────┐
│              EXTERNAL SERVICES & STORAGE                     │
├──────────────────────────────────────────────────────────────┤
│  Cloud Providers        │  Message Services  │  Data Storage │
│  ├─ Google Drive        │  ├─ Discord        │  ├─ SQLite    │
│  ├─ OneDrive            │  ├─ Slack          │  ├─ PostgreSQL│
│  ├─ S3/AWS              │  ├─ Telegram       │  └─ File System
│  └─ SharePoint          │  └─ Email (future) │                │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 REFACTORED DATA FLOW (WITH PHASES)

```
PHASE 1: Foundation (Encryption, Scheduler, Webhooks)
─────────────────────────────────────────────────────

User Input (Menu/CLI)
  │
  ├─→ [Schedule Creation] (NEW)
  │   └─→ ScheduleService.create_schedule()
  │       └─→ APScheduler registers trigger
  │
  └─→ [Immediate Download]
      │
      └─→ CryptoManager.load_config() (ENHANCED)
          └─→ Decrypt sensitive fields
              │
              ├─→ DownloadService.process_url()
              │   │
              │   ├─→ Check filters
              │   ├─→ Download files
              │   └─→ Update history
              │
              └─→ NotificationDispatcher.notify()
                  ├─→ play_sound()
                  ├─→ send_toast()
                  └─→ WebhookNotifier.send() (NEW)
                      ├─→ Discord
                      ├─→ Slack
                      └─→ Telegram


PHASE 2: APIs & Interfaces
───────────────────────────

User
  │
  ├─→ CLI/Menu (existing)
  │   └─→ Direct DownloadService calls
  │
  ├─→ Web Browser (NEW - Flask)
  │   │
  │   └─→ HTTP Request
  │       └─→ Flask Router
  │           └─→ REST API Client
  │
  └─→ External System (NEW - FastAPI)
      │
      └─→ HTTP REST Request
          └─→ FastAPI Route
              └─→ DownloadService
                  └─→ Return JSON


PHASE 3: Reliability & Performance
───────────────────────────────────

DownloadService.download_single_file()
  │
  ├─→ ResumeManager.check_can_resume() (NEW)
  │   └─→ If partial file exists and supports Range
  │       └─→ Add Range header to request
  │
  ├─→ HTTP Request (with resume offset)
  │   │
  │   └─→ Download with caching (NEW)
  │       └─→ Check ETag
  │       └─→ Use cached version if match
  │
  ├─→ Cache/Bandwidth Optimization (NEW)
  │   └─→ Apply throttling
  │   └─→ Compress if possible
  │
  └─→ MetricsCollector.emit_metrics() (NEW)
      └─→ Record to Prometheus-compatible endpoint


PHASE 4: Cloud Integration
──────────────────────────

DownloadService.process_url()
  │
  └─→ On completion:
      │
      ├─→ CloudProvider.upload() (NEW)
      │   │
      │   ├─→ GoogleDriveProvider (NEW)
      │   │   └─→ OAuth2 flow
      │   │   └─→ Upload to Drive
      │   │
      │   ├─→ OneDriveProvider (NEW)
      │   │   └─→ Azure AD auth
      │   │   └─→ Upload to OneDrive
      │   │
      │   └─→ S3Provider (NEW)
      │       └─→ AWS credentials
      │       └─→ Upload to S3
      │
      └─→ SyncService.sync() (NEW)
          └─→ Resolve conflicts
          └─→ Update metadata


PHASE 5: Advanced Processing & Scalability
───────────────────────────────────────────

DownloadService.process_url()
  │
  ├─→ [Database Persistence] (NEW)
  │   └─→ SQLRepository.save_download()
  │       └─→ Update PostgreSQL/SQLite
  │
  ├─→ [Post-Download Processing] (NEW)
  │   │
  │   └─→ ProcessingService.process_file()
  │       │
  │       ├─→ ImageProcessor (NEW)
  │       │   ├─→ Convert format
  │       │   └─→ Extract EXIF
  │       │
  │       ├─→ ArchiveProcessor (NEW)
  │       │   └─→ Extract & organize
  │       │
  │       └─→ MetadataExtractor (NEW)
  │           └─→ Extract metadata
  │           └─→ Organize by date/type
  │
  └─→ [Network Resilience] (NEW)
      └─→ NetworkManager.check_connectivity()
          ├─→ Auto-failover on loss
          └─→ Queue for retry
```

---

## 🔑 KEY DESIGN PATTERNS

### 1. Repository Pattern (Data Access)

**Current (PRIORITY 1-3):**
```python
# Data scattered across files
history = json.load(open('download_history.json'))
history[task_name].append(file_info)
json.dump(history, f)
```

**Proposed (PRIORITY 4):**
```python
class Repository(ABC):
    @abstractmethod
    def save_download(self, record: Download) -> bool: ...
    @abstractmethod
    def get_downloads(self, filters: Dict) -> List[Download]: ...

class JSONRepository(Repository):
    def save_download(self, record: Download) -> bool:
        history = self._load()
        history[record.task_name].append(record.to_dict())
        self._save(history)
        return True

class SQLRepository(Repository):
    def save_download(self, record: Download) -> bool:
        session.add(DownloadModel(**record.to_dict()))
        session.commit()
        return True

# Usage (abstracted, works with both)
repository: Repository = get_repository_for_backend()
repository.save_download(my_download)
```

**Benefits:**
- Can switch JSON ↔ Database without changing business logic
- Testable with mock repository
- Extensible for new backends

---

### 2. Cloud Provider Pattern (Strategy Pattern)

**Current:** No cloud support

**Proposed:**
```python
class CloudProvider(ABC):
    """Strategy interface for cloud storage."""
    
    @abstractmethod
    async def upload(self, local_path: Path, remote_path: str) -> bool: ...
    
    @abstractmethod
    async def download(self, remote_path: str, local_path: Path) -> bool: ...
    
    @abstractmethod
    async def sync(self, local_dir: Path, remote_dir: str) -> SyncResult: ...

class GoogleDriveProvider(CloudProvider):
    def __init__(self, credentials_path: str):
        self.service = build('drive', 'v3', credentials=...)
    
    async def upload(self, local_path: Path, remote_path: str) -> bool:
        file_metadata = {'name': remote_path}
        media = MediaFileUpload(local_path)
        file = self.service.files().create(body=file_metadata, media_body=media).execute()
        return file is not None

class OneDriveProvider(CloudProvider):
    def __init__(self, token: str):
        self.client = GraphClient(token)
    
    async def upload(self, local_path: Path, remote_path: str) -> bool:
        # Azure AD implementation
        ...

class S3Provider(CloudProvider):
    def __init__(self, aws_access_key: str, aws_secret_key: str, bucket: str):
        self.s3 = boto3.client('s3', aws_access_key_id=..., aws_secret_access_key=...)
    
    async def upload(self, local_path: Path, remote_path: str) -> bool:
        self.s3.upload_file(str(local_path), self.bucket, remote_path)
        return True

# Usage
provider = GoogleDriveProvider(credentials)
await provider.upload(Path("downloads/file.pdf"), "backups/file.pdf")
```

**Benefits:**
- Easy to add new cloud providers
- Runtime provider selection
- Same interface for all clouds
- Testable with mock provider

---

### 3. Notification Strategy Pattern

**Current:**
```python
def notify_completion(...):
    if CONFIG.get('notification_sound'): play_sound()
    if CONFIG.get('notification_toast'): send_toast()
```

**Proposed (Extensible):**
```python
class Notifier(ABC):
    @abstractmethod
    def send(self, title: str, message: str) -> bool: ...

class SoundNotifier(Notifier):
    def send(self, title: str, message: str) -> bool:
        play_notification_sound()
        return True

class ToastNotifier(Notifier):
    def send(self, title: str, message: str) -> bool:
        send_toast_notification(title, message)
        return True

class DiscordNotifier(Notifier):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send(self, title: str, message: str) -> bool:
        requests.post(self.webhook_url, json={
            'content': f"**{title}**: {message}"
        })
        return True

class SlackNotifier(Notifier):
    # Implementation

class TelegramNotifier(Notifier):
    # Implementation

class NotificationDispatcher:
    def __init__(self):
        self.notifiers: List[Notifier] = []
    
    def add_notifier(self, notifier: Notifier):
        self.notifiers.append(notifier)
    
    def notify_all(self, title: str, message: str):
        for notifier in self.notifiers:
            try:
                notifier.send(title, message)
            except Exception as e:
                logger.error(f"Notifier error: {e}")

# Usage
dispatcher = NotificationDispatcher()
dispatcher.add_notifier(SoundNotifier())
dispatcher.add_notifier(ToastNotifier())
dispatcher.add_notifier(DiscordNotifier("https://discord.com/..."))
dispatcher.notify_all("Download Complete", "10 files downloaded")
```

**Benefits:**
- Easy to add new notification channels
- Decoupled from download logic
- Can notify multiple channels simultaneously
- Graceful error handling

---

### 4. Plugin System (Processing Pipeline)

**Proposed for Phase 5:**
```python
class FileProcessor(ABC):
    """Plugin interface for file processing."""
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]: ...
    
    @abstractmethod
    def process(self, input_path: Path, output_path: Path) -> bool: ...
    
    @abstractmethod
    def get_metadata(self, file_path: Path) -> Dict: ...

class ImageProcessor(FileProcessor):
    @property
    def supported_extensions(self):
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    def process(self, input_path: Path, output_path: Path) -> bool:
        img = Image.open(input_path)
        # Convert, resize, watermark, etc.
        img.save(output_path)
        return True
    
    def get_metadata(self, file_path: Path) -> Dict:
        img = Image.open(file_path)
        exif = img._getexif() if hasattr(img, '_getexif') else {}
        return {'created': exif.get(36867), 'size': img.size}

class ArchiveProcessor(FileProcessor):
    @property
    def supported_extensions(self):
        return ['.zip', '.rar', '.7z']
    
    def process(self, input_path: Path, output_path: Path) -> bool:
        with ZipFile(input_path, 'r') as archive:
            archive.extractall(output_path)
        return True

class ProcessorRegistry:
    def __init__(self):
        self.processors: Dict[str, FileProcessor] = {}
    
    def register(self, ext: str, processor: FileProcessor):
        self.processors[ext.lower()] = processor
    
    def process(self, file_path: Path) -> ProcessResult:
        ext = file_path.suffix.lower()
        if ext not in self.processors:
            return ProcessResult(success=False, reason="No processor for extension")
        
        processor = self.processors[ext]
        try:
            metadata = processor.get_metadata(file_path)
            output_path = file_path.parent / f"{file_path.stem}_processed{file_path.suffix}"
            success = processor.process(file_path, output_path)
            return ProcessResult(success=success, output=output_path, metadata=metadata)
        except Exception as e:
            return ProcessResult(success=False, reason=str(e))

# Usage
registry = ProcessorRegistry()
registry.register('.jpg', ImageProcessor())
registry.register('.png', ImageProcessor())
registry.register('.zip', ArchiveProcessor())

result = registry.process(Path('downloads/image.jpg'))
if result.success:
    print(f"Processed to: {result.output}")
```

**Benefits:**
- Extensible without modifying core
- Third-party plugins can be added
- Metadata extraction built-in
- Error handling per processor

---

### 5. Dependency Injection Pattern

**Current (Tightly Coupled):**
```python
def process_url(url):
    config = load_config()  # Global config
    logger.info(...)  # Global logger
    history = load_download_history(BASE_DIR)  # Global BASE_DIR
    # ... hard to test, can't mock dependencies
```

**Proposed (Loosely Coupled):**
```python
class DownloadService:
    def __init__(self,
                 config: ConfigProvider,
                 repository: Repository,
                 logger: Logger,
                 notifier: NotificationDispatcher):
        self.config = config
        self.repository = repository
        self.logger = logger
        self.notifier = notifier
    
    def process_url(self, url: str) -> Result:
        self.logger.info(f"Processing {url}")
        # Uses injected dependencies, not globals
        config = self.config.get_config()
        self.repository.save_download(...)
        self.notifier.notify_all(...)

# Dependency Container
class Container:
    @singleton
    def config_provider(self) -> ConfigProvider:
        return JsonConfigProvider('config.json')
    
    @singleton
    def repository(self) -> Repository:
        if self.config_provider.use_database:
            return SQLRepository()
        return JSONRepository()
    
    @singleton
    def logger(self) -> Logger:
        return setup_logging()
    
    @singleton
    def download_service(self) -> DownloadService:
        return DownloadService(
            config=self.config_provider(),
            repository=self.repository(),
            logger=self.logger(),
            notifier=self.notification_dispatcher()
        )

# Usage
container = Container()
service = container.download_service()
service.process_url("https://example.com")

# Testing
@pytest.fixture
def mock_repository():
    return MockRepository()

def test_process_url(mock_repository):
    service = DownloadService(
        config=MockConfig(),
        repository=mock_repository,  # Injected mock
        logger=MockLogger(),
        notifier=MockNotifier()
    )
    # Test with mocks, no external dependencies
```

**Benefits:**
- Testable (easy to inject mocks)
- Loose coupling
- Configurable at runtime
- Explicit dependencies

---

## 📋 DATA MODELS

### Current Download History Format (JSON)

```json
{
  "task_name": {
    "url": "https://example.com/task/123",
    "downloaded_at": "2026-01-27T15:30:00",
    "total_files": 5,
    "files": [
      {
        "filename": "image_001.jpg",
        "size_bytes": 2048576,
        "md5": "abc123def456",
        "downloaded_at": "2026-01-27T15:30:15",
        "status": "success"
      }
    ]
  }
}
```

### Proposed Database Schema (SQLite/PostgreSQL)

```sql
-- Downloads table
CREATE TABLE downloads (
    id INTEGER PRIMARY KEY,
    task_name VARCHAR(255),
    url VARCHAR(1000),
    filename VARCHAR(500),
    filesize INTEGER,
    md5_hash VARCHAR(32),
    status ENUM('success', 'failed', 'skipped'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schedules table
CREATE TABLE schedules (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    trigger_cron VARCHAR(100),
    url VARCHAR(1000),
    enabled BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Cloud credentials (encrypted)
CREATE TABLE cloud_credentials (
    id INTEGER PRIMARY KEY,
    provider VARCHAR(50),  -- 'google_drive', 'onedrive', 's3'
    credentials_encrypted TEXT,
    encryption_key_id VARCHAR(100),
    expires_at TIMESTAMP,
    created_at TIMESTAMP
);

-- Processing jobs
CREATE TABLE processing_jobs (
    id INTEGER PRIMARY KEY,
    input_file_path VARCHAR(1000),
    processor_type VARCHAR(100),
    output_file_path VARCHAR(1000),
    status ENUM('queued', 'processing', 'complete', 'failed'),
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Logs (for advanced logging)
CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    level VARCHAR(20),  -- 'DEBUG', 'INFO', 'WARNING', 'ERROR'
    message TEXT,
    context JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Proposed ORM Models (SQLAlchemy)

```python
from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Download(Base):
    __tablename__ = "downloads"
    
    id: int = Column(Integer, primary_key=True)
    task_name: str = Column(String(255), index=True)
    url: str = Column(String(1000))
    filename: str = Column(String(500))
    filesize: int = Column(Integer)
    md5_hash: str = Column(String(32), index=True)
    status: str = Column(Enum('success', 'failed', 'skipped'), default='success')
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'task_name': self.task_name,
            'url': self.url,
            'filename': self.filename,
            'filesize': self.filesize,
            'md5': self.md5_hash,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }

class Schedule(Base):
    __tablename__ = "schedules"
    
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(255), unique=True)
    trigger_cron: str = Column(String(100))
    url: str = Column(String(1000))
    enabled: bool = Column(Boolean, default=True)
    last_run: Optional[datetime] = Column(DateTime)
    next_run: Optional[datetime] = Column(DateTime)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
```

---

## 🔐 Security Considerations

### Credential Storage (Phase 1)

**Never:**
```python
❌ CONFIG['my_cookie'] = "secret_value"  # Plaintext in config
❌ print(credentials)  # Logs credentials
❌ Store tokens in memory indefinitely
```

**Always:**
```python
✅ Use encryption at rest (AES-256)
✅ Use environment variables for runtime secrets
✅ Rotate credentials periodically
✅ Use secure credential vaults (AWS Secrets Manager, Azure KeyVault)
✅ Hash passwords, never store plaintext
✅ Use HTTPS for external API calls
✅ Implement token refresh mechanisms
```

### Implementation

```python
class CredentialVault:
    def __init__(self, master_password: str):
        self.cipher = Cipher(
            algorithms.AES(self._derive_key(master_password)),
            modes.CBC(os.urandom(16))
        )
    
    def store(self, key: str, value: str) -> bool:
        encrypted = self.cipher.encryptor().update(value.encode())
        # Store encrypted in config
        return True
    
    def retrieve(self, key: str) -> str:
        # Get encrypted from config
        decrypted = self.cipher.decryptor().update(encrypted)
        return decrypted.decode()
    
    def _derive_key(self, password: str) -> bytes:
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)

# Usage
vault = CredentialVault(master_password="user_password")
vault.store('google_drive_token', oauth_token)
token = vault.retrieve('google_drive_token')
```

---

## 🧪 Testing Strategy

### Unit Tests (Per Feature)

```python
# Phase 1: Encryption
def test_crypto_encrypt_decrypt_roundtrip():
    vault = CredentialVault("password123")
    original = "secret_token_12345"
    encrypted = vault.encrypt(original)
    decrypted = vault.decrypt(encrypted)
    assert decrypted == original

# Phase 1: Scheduler
def test_schedule_creation():
    scheduler = ScheduleManager()
    schedule = scheduler.create_schedule(
        trigger="cron(0 8 * * ?)",  # 8 AM daily
        url="https://example.com/task"
    )
    assert schedule.id is not None
    assert schedule.enabled is True

# Phase 2: API
def test_api_download_endpoint():
    client = TestClient(app)
    response = client.post("/api/download", json={"url": "https://example.com"})
    assert response.status_code == 202  # Accepted
    assert "job_id" in response.json()

# Phase 4: Cloud
@pytest.mark.asyncio
async def test_google_drive_upload():
    provider = GoogleDriveProvider(mock_credentials)
    result = await provider.upload(
        Path("test.pdf"),
        "backups/test.pdf"
    )
    assert result is True
```

### Integration Tests

```python
def test_full_download_and_notify_workflow():
    # Setup
    service = DownloadService(
        config=MockConfig(),
        repository=JSONRepository(),
        notifier=TestNotificationDispatcher()
    )
    
    # Execute
    result = service.process_url("https://example.com/task")
    
    # Verify
    assert result.success is True
    assert TestNotificationDispatcher.last_notification is not None
    assert "Download Complete" in TestNotificationDispatcher.last_notification
```

### E2E Tests

```python
def test_scheduled_download_execution():
    # Create schedule
    scheduler = ScheduleManager()
    schedule = scheduler.create_schedule(
        trigger="cron(* * * * *)",  # Every minute
        url="https://example.com/task"
    )
    
    # Wait for execution
    time.sleep(65)
    
    # Verify it executed
    history = scheduler.get_execution_history(schedule.id)
    assert len(history) > 0
    assert history[0].status == "success"
```

---

## 📊 Performance Targets

### Phase 1-2
- API response time: < 200ms (90th percentile)
- Schedule execution: < 5s from trigger
- Web dashboard load: < 1s

### Phase 3
- Resume download: < 100ms overhead (check + seek)
- ETag cache hit rate: > 30%
- Bandwidth throttling: ±5% of configured limit

### Phase 4
- Cloud upload: < 10s (for 100MB file on 10Mbps connection)
- Sync conflict resolution: < 500ms

### Phase 5
- File processing: < 2s per 100MB (for image conversion)
- Database query: < 100ms (with proper indexes)
- Metadata extraction: < 500ms per file

---

## 🚀 Deployment Considerations

### Single Machine Deployment
- SQLite for database (embedded)
- APScheduler as in-process scheduler
- Flask/FastAPI on port 8000
- Runs as background service (Windows Service or systemd)

### Distributed Deployment
- PostgreSQL for shared database
- Redis for queue (optional, for webhook processing)
- Multiple instances of API (load-balanced)
- Separate scheduler service (one instance)
- Separate file processing worker (multiple instances)

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "downloader.api"]
```

---

**Document Version:** 1.0  
**Last Updated:** January 27, 2026  
**Status:** Ready for Architecture Review
