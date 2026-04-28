import os
import sys
import threading
import queue
import shutil
import platform
import time
import re
import json
import hashlib
import math
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from datetime import datetime
import psutil

# ============================================================================
# CONFIGURATION MANAGER
# ============================================================================
class ConfigManager:
    """Handles loading/saving user preferences."""
    CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".explorer_pro_config.json")
    DEFAULTS = {
        "theme": "dark",
        "scan_mode": "quick",
        "skip_system_dirs": False,
        "task_refresh_interval": 2,
        "recent_paths": [],
        "search_case_sensitive": False,
        "search_regex": False,
        "search_include_hidden": True,
        "tree_depth_limit": 5
    }

    def __init__(self):
        self.config = self.DEFAULTS.copy()
        self.load()

    def load(self):
        if os.path.exists(self.CONFIG_PATH):
            try:
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
            except Exception:
                pass

    def save(self):
        try:
            with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Config save error: {e}")

    def get(self, key, default=None):
        val = self.config.get(key)
        return val if val is not None else (default if default is not None else self.DEFAULTS.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save()

    def add_recent_path(self, path):
        if not path: return
        paths = self.get("recent_paths", [])
        if path in paths: paths.remove(path)
        paths.insert(0, path)
        self.config["recent_paths"] = paths[:10]
        self.save()

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================
FILE_TYPE_COLORS: Dict[str, str] = {
    '.pdf': '#1E90FF', '.docx': '#1E90FF', '.doc': '#1E90FF', '.txt': '#87CEEB',
    '.xlsx': '#1E90FF', '.xls': '#1E90FF', '.csv': '#1E90FF', '.odt': '#1E90FF',
    '.rtf': '#1E90FF', '.pptx': '#1E90FF', '.ppt': '#1E90FF',
    '.md': '#FFA500', '.markdown': '#FFA500',
    '.png': '#FF69B4', '.jpg': '#FF69B4', '.jpeg': '#FF69B4', '.webp': '#FF69B4',
    '.svg': '#FF69B4', '.bmp': '#FF69B4', '.ico': '#FF69B4', '.gif': '#FF69B4',
    '.tiff': '#FF69B4', '.tif': '#FF69B4', '.heic': '#FF69B4',
    '.psd': '#FF69B4', '.ai': '#FF69B4', '.eps': '#FF69B4',
    '.mp3': '#FF8C00', '.wav': '#FF8C00', '.flac': '#FF8C00', '.aac': '#FF8C00',
    '.ogg': '#FF8C00', '.wma': '#FF8C00', '.m4a': '#FF8C00',
    '.mp4': '#9370DB', '.mkv': '#9370DB', '.avi': '#9370DB', '.mov': '#9370DB',
    '.webm': '#9370DB', '.flv': '#9370DB', '.wmv': '#9370DB', '.m4v': '#9370DB',
    '.blend': '#9370DB', '.fbx': '#9370DB', '.obj': '#9370DB', '.mtl': '#9370DB',
    '.py': '#32CD32', '.js': '#32CD32', '.ts': '#32CD32', '.cpp': '#32CD32',
    '.h': '#32CD32', '.c': '#32CD32', '.java': '#32CD32', '.html': '#32CD32',
    '.css': '#32CD32', '.go': '#32CD32', '.rs': '#32CD32', '.rb': '#32CD32',
    '.lua': '#32CD32', '.dart': '#32CD32', '.kt': '#32CD32', '.swift': '#32CD32',
    '.php': '#32CD32', '.sh': '#32CD32', '.bat': '#32CD32', '.ps1': '#32CD32',
    '.gitignore': '#87CEEB', '.dockerignore': '#87CEEB',
    '.zip': '#FFD700', '.rar': '#FFD700', '.7z': '#FFD700', '.tar': '#FFD700',
    '.gz': '#FFD700', '.bz2': '#FFD700', '.xz': '#FFD700', '.iso': '#FFD700',
    '.dmg': '#FFD700', '.tgz': '#FFD700',
    '.exe': '#FF4500', '.msi': '#FF4500', '.com': '#FF4500', '.scr': '#FF4500',
    '.app': '#FF4500', '.apk': '#FF4500',
    '.sys': '#808080', '.dll': '#808080', '.so': '#808080', '.dylib': '#808080',
    '.pf': '#FF6B6B', '.pfx': '#FF6B6B', '.p12': '#FF6B6B',
    '.env': '#DDA0DD', '.config': '#DDA0DD', '.ini': '#DDA0DD', '.cfg': '#DDA0DD',
    '.toml': '#DDA0DD', '.yaml': '#DDA0DD', '.yml': '#DDA0DD', '.json': '#DDA0DD',
    '.pyc': '#D3D3D3', '.pyo': '#D3D3D3', '.pyd': '#D3D3D3',
    '.lock': '#A9A9A9', '.pid': '#A9A9A9',
    '.log': '#696969', '.out': '#696969', '.err': '#696969',
    '.bak': '#FFB6C1', '.backup': '#FFB6C1', '.old': '#FFB6C1', '.orig': '#FFB6C1',
    '.part': '#FF6347', '.crdownload': '#FF6347', '.tmp': '#FF6347', '.temp': '#FF6347',
    '.ttf': '#40E0D0', '.otf': '#40E0D0', '.woff': '#40E0D0', '.woff2': '#40E0D0', '.eot': '#40E0D0',
    '.db': '#DC143C', '.sqlite': '#DC143C', '.sqlite3': '#DC143C', '.sql': '#DC143C',
}
DEFAULT_COLOR = '#CCCCCC'
FOLDER_COLOR = '#4169E1'
SYSTEM_FOLDER_COLOR = '#696969'

SAFE_PATTERNS = {
    'extensions': {'.tmp', '.bak', '.temp', '.cache', '.crdownload', '.part', '.downloading', '.~tmp'},
    'directories': {'__pycache__', '.cache', '.pytest_cache', '.mypy_cache', 'node_modules', 'Cache', 'Cookies', 'History', 'SessionStorage', '.gradle', '.m2'},
    'path_segments': {'temp', 'tmp', 'cache', 'downloads', '$Recycle.Bin', '.cache'},
}
CRITICAL_PATTERNS = {
    'directories': {'Windows', 'System32', 'SysWOW64', 'Program Files', 'Program Files (x86)', 'ProgramData', 'Recovery', 'Boot', 'WinSxS', 'etc', 'bin', 'lib', 'sbin', 'var'},
    'path_prefixes': {'C:\\Windows', 'C:\\System32', 'C:\\Program Files', 'C:\\ProgramData', '/usr/bin', '/usr/lib', '/etc', '/System', '/Library', '/bin', '/sbin', '/var'},
}
SYSTEM_REMOVABLE_PATTERNS = {
    'directories': {'Windows.old', 'Prefetch', '$WINDOWS.~BT', 'installer', 'backup'},
    'path_segments': {'windows.old', 'prefetch', 'installer_cache', 'old_windows'},
}

DEFAULT_ROOT = str(Path.home()) if platform.system() != "Windows" else "C:\\"
MAX_TREE_DEPTH = 5
MAX_WORKERS = 6
BATCH_SIZE = 500
PAGINATION_LIMIT = 1000
LARGE_FILE_THRESHOLD = 100 * 1024 * 1024

class SafetyClassification(Enum):
    SAFE = "SAFE"
    CRITICAL = "CRITICAL"
    SYSTEM_REMOVABLE = "SYSTEM-REMOVABLE"
    UNKNOWN = "UNKNOWN"

@dataclass
class FileInfo:
    path: str
    filename: str
    extension: str
    is_dir: bool
    size: int
    safety_classification: SafetyClassification
    color: str
    modified_time: float = 0.0
    file_type_name: str = ""
    parent_path: str = ""
    
    def __lt__(self, other):
        if self.is_dir != other.is_dir:
            return self.is_dir
        return self.filename.lower() < other.filename.lower()

class LRU_Cache:
    def __init__(self, maxsize=5000):
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.lock = threading.Lock()

    def get(self, key, default=None):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            return default

    def set(self, key, value):
        with self.lock:
            self.cache[key] = value
            self.cache.move_to_end(key)
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)

class FileClassifier:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.is_windows = platform.system() == "Windows"
        self.running_process_paths = self._get_running_process_paths()
        self.cache = LRU_Cache(maxsize=5000)

    def _get_running_process_paths(self) -> Set[str]:
        locked_files = set()
        try:
            for proc in psutil.process_iter(['open_files']):
                try:
                    for file_info in proc.open_files():
                        locked_files.add(file_info.path.lower())
                except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                    pass
        except Exception: pass
        return locked_files

    def classify(self, path: str, use_cache: bool = True, scan_mode: str = "full") -> FileInfo:
        if use_cache:
            cached = self.cache.get(path)
            if cached: return cached

        try:
            stat_info = os.stat(path)
            is_dir = os.path.isdir(path)
            size = stat_info.st_size if not is_dir else 0
            mtime = stat_info.st_mtime
        except (OSError, PermissionError):
            fi = FileInfo(path, os.path.basename(path), '', False, 0, SafetyClassification.UNKNOWN, DEFAULT_COLOR, parent_path=os.path.dirname(path))
            self.cache.set(path, fi)
            return fi

        filename = os.path.basename(path)
        ext = os.path.splitext(filename)[1].lower()
        path_lower = path.lower()

        if is_dir:
            color = SYSTEM_FOLDER_COLOR if filename in CRITICAL_PATTERNS.get('directories', set()) else FOLDER_COLOR
            file_type_name = 'Folder'
        else:
            color = FILE_TYPE_COLORS.get(ext, DEFAULT_COLOR)
            file_type_name = self._get_file_type_name(ext)

        safety = SafetyClassification.UNKNOWN
        if scan_mode == "full" and size <= LARGE_FILE_THRESHOLD:
            safety = self._classify_safety(path, path_lower, filename, ext)

        fi = FileInfo(path=path, filename=filename, extension=ext, is_dir=is_dir, size=size,
                      safety_classification=safety, color=color, modified_time=mtime,
                      file_type_name=file_type_name, parent_path=os.path.dirname(path))
        self.cache.set(path, fi)
        return fi

    def _classify_safety(self, path: str, path_lower: str, filename: str, ext: str) -> SafetyClassification:
        if self._is_critical(path, path_lower, filename, ext): return SafetyClassification.CRITICAL
        if self._is_system_removable(path, path_lower, filename): return SafetyClassification.SYSTEM_REMOVABLE
        if self._is_safe(path, path_lower, filename, ext): return SafetyClassification.SAFE
        return SafetyClassification.UNKNOWN

    def _is_critical(self, path: str, path_lower: str, filename: str, ext: str) -> bool:
        if path_lower in self.running_process_paths: return True
        if filename in CRITICAL_PATTERNS.get('directories', set()): return True
        if ext.lower() in {'.dll', '.sys', '.exe'}: return True
        for prefix in CRITICAL_PATTERNS.get('path_prefixes', set()):
            if path_lower.startswith(prefix.lower()): return True
        return False

    def _is_system_removable(self, path: str, path_lower: str, filename: str) -> bool:
        if filename in SYSTEM_REMOVABLE_PATTERNS.get('directories', set()): return True
        path_parts = path_lower.split(os.sep)
        for segment in SYSTEM_REMOVABLE_PATTERNS.get('path_segments', set()):
            if segment in path_parts: return True
        return False

    def _is_safe(self, path: str, path_lower: str, filename: str, ext: str) -> bool:
        if ext.lower() in SAFE_PATTERNS.get('extensions', set()): return True
        if filename in SAFE_PATTERNS.get('directories', set()): return True
        path_parts = path_lower.split(os.sep)
        for segment in SAFE_PATTERNS.get('path_segments', set()):
            if segment in path_parts: return True
        return False

    @staticmethod
    def _get_file_type_name(ext: str) -> str:
        type_map = {
            '.pdf': 'PDF Document', '.docx': 'Word Document', '.xlsx': 'Excel Spreadsheet',
            '.py': 'Python Script', '.js': 'JavaScript', '.html': 'Web Page',
            '.jpg': 'JPEG Image', '.png': 'PNG Image', '.zip': 'ZIP Archive',
            '.exe': 'Application', '.mp4': 'MP4 Video', '.mp3': 'MP3 Audio',
        }
        return type_map.get(ext, f'{ext[1:].upper()} File' if ext else 'File')

class HighPerformanceScanner:
    def __init__(self, classifier: FileClassifier, result_queue: queue.Queue, config: ConfigManager):
        self.classifier = classifier
        self.result_queue = result_queue
        self.config = config
        self.stats = {'SAFE': 0, 'CRITICAL': 0, 'SYSTEM_REMOVABLE': 0, 'UNKNOWN': 0}
        self._stop_event = threading.Event()
        self._batch_buffer: List[FileInfo] = []
        self._total_scanned = 0

    def scan_root(self, root_path: str, max_depth: int = None):
        root_path = os.path.abspath(root_path)
        if not os.path.exists(root_path):
            self.result_queue.put(('error', f"Path does not exist: {root_path}"))
            return
        self.stats = {'SAFE': 0, 'CRITICAL': 0, 'SYSTEM_REMOVABLE': 0, 'UNKNOWN': 0}
        self._total_scanned = 0
        self._stop_event.clear()
        scan_mode = self.config.get("scan_mode", "quick")
        skip_sys = self.config.get("skip_system_dirs", False)
        depth = max_depth or self.config.get("tree_depth_limit", MAX_TREE_DEPTH)
        self.result_queue.put(('started', {'path': root_path}))
        self._scan_recursive(root_path, 0, depth, scan_mode, skip_sys)
        self._flush_batch()
        self.result_queue.put(('completed', {'total': self._total_scanned, 'stats': self.stats.copy()}))

    def scan_folder_expansion(self, folder_path: str, parent_item_id: str, depth: int):
        try:
            self.result_queue.put(('expand_started', {'folder': folder_path, 'parent': parent_item_id}))
            entries = sorted(os.scandir(folder_path), key=lambda e: (not e.is_dir(), e.name.lower()))
            scan_mode = self.config.get("scan_mode", "quick")
            for entry in entries:
                if entry.is_symlink(): continue
                fi = self.classifier.classify(entry.path, scan_mode=scan_mode)
                fi.parent_path = folder_path
                self._batch_buffer.append(fi)
                self.stats[fi.safety_classification.value] += 1
                self._total_scanned += 1
                if len(self._batch_buffer) >= BATCH_SIZE: self._flush_batch()
            self._flush_batch()
            self.result_queue.put(('expand_completed', {'folder': folder_path}))
        except Exception as e:
            self.result_queue.put(('expand_error', str(e)))

    def _scan_recursive(self, path: str, depth: int, max_depth: int, scan_mode: str, skip_sys: bool):
        if self._stop_event.is_set() or depth >= max_depth: return
        try:
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
        except (PermissionError, OSError): return

        for entry in entries:
            if self._stop_event.is_set(): return
            if entry.is_symlink(): continue
            path_lower = entry.path.lower()
            if skip_sys and any(path_lower.startswith(p.lower()) for p in CRITICAL_PATTERNS.get('path_prefixes', set())):
                continue

            self._total_scanned += 1
            try:
                fi = self.classifier.classify(entry.path, scan_mode=scan_mode)
                fi.parent_path = path
                self._batch_buffer.append(fi)
                self.stats[fi.safety_classification.value] += 1
                if len(self._batch_buffer) >= BATCH_SIZE: self._flush_batch()
                if entry.is_dir() and depth < max_depth - 1:
                    self._scan_recursive(entry.path, depth + 1, max_depth, scan_mode, skip_sys)
            except (PermissionError, OSError): pass

    def _flush_batch(self):
        if self._batch_buffer:
            self.result_queue.put(('batch', self._batch_buffer.copy()))
            self._batch_buffer.clear()

    def stop(self): self._stop_event.set()

class TaskMonitor(threading.Thread):
    def __init__(self, result_queue: queue.Queue, config: ConfigManager):
        super().__init__(daemon=True)
        self.result_queue = result_queue
        self.config = config
        self._stop_event = threading.Event()
        self._paused_by_interaction = False

    def set_paused(self, paused): self._paused_by_interaction = paused
    def stop(self): self._stop_event.set()

    def run(self):
        self.result_queue.put(('task_started', None))
        while not self._stop_event.is_set():
            if self._paused_by_interaction:
                self._stop_event.wait(0.5)
                continue
            try:
                processes = self._get_processes()
                self.result_queue.put(('processes', processes))
            except Exception as e:
                self.result_queue.put(('task_error', str(e)))
            self._stop_event.wait(self.config.get("task_refresh_interval", 2))

    @staticmethod
    def _get_processes() -> List[Dict]:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'status', 'username', 'cpu_percent', 'memory_info']):
            try:
                with proc.oneshot():
                    processes.append({
                        'pid': proc.pid, 'name': proc.name(), 'cpu_percent': proc.cpu_percent(interval=0),
                        'memory_mb': proc.memory_info().rss / (1024 * 1024), 'status': proc.status(),
                        'username': proc.username() if hasattr(proc, 'username') else 'System'
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess): pass
        processes.sort(key=lambda x: x['memory_mb'], reverse=True)
        return processes

class DuplicateDetector:
    def __init__(self, file_list: List[FileInfo], queue_obj: queue.Queue):
        self.files = file_list
        self.queue_obj = queue_obj

    def run(self):
        self.queue_obj.put(('dup_started', {'total': len(self.files)}))
        size_groups = {}
        for f in self.files:
            if f.is_dir: continue
            size_groups.setdefault(f.size, []).append(f)

        candidates = [g for g in size_groups.values() if len(g) > 1]
        hash_groups = {}
        for group in candidates:
            for f in group:
                try:
                    h = self._hash_file(f.path)
                    hash_groups.setdefault(h, []).append(f)
                except Exception: pass

        duplicates = [g for g in hash_groups.values() if len(g) > 1]
        self.queue_obj.put(('dup_completed', {'groups': duplicates}))

    @staticmethod
    def _hash_file(filepath: str, chunk_size: int = 65536) -> str:
        md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                md5.update(chunk)
        return md5.hexdigest()

class SearchEngine:
    def __init__(self, files: List[FileInfo], config: ConfigManager):
        self.files = files
        self.config = config

    def search(self, query: str) -> List[FileInfo]:
        if not query: return []
        results = []
        case_sensitive = self.config.get("search_case_sensitive", False)
        use_regex = self.config.get("search_regex", False)
        include_hidden = self.config.get("search_include_hidden", True)

        pattern = query if use_regex else re.escape(query)
        flags = 0 if case_sensitive else re.IGNORECASE
        try: compiled = re.compile(pattern, flags)
        except re.error: return []

        for f in self.files:
            if not include_hidden and f.filename.startswith('.'): continue
            if compiled.search(f.filename): results.append(f)
        return results

class ProjectExplorerPro:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("📂 PROJECT EXPLORER PRO - v3.0")
        self.root.geometry("1450x850")
        self.root.minsize(1100, 650)

        self.config = ConfigManager()
        self.classifier = FileClassifier(self.config)
        
        self.scanner_queue = queue.Queue()
        self.task_queue = queue.Queue()
        self.dup_queue = queue.Queue()
        self.scanner_thread: Optional[threading.Thread] = None
        self.task_monitor_thread: Optional[TaskMonitor] = None
        
        self.all_files: List[FileInfo] = []
        self.stats = {'SAFE': 0, 'CRITICAL': 0, 'SYSTEM_REMOVABLE': 0, 'UNKNOWN': 0}
        
        # FIXED: Robust handling of recent_paths
        recent_paths = self.config.get("recent_paths", [])
        self.current_path = recent_paths[0] if recent_paths else DEFAULT_ROOT
        
        self.tree_depth = 0
        self.scan_mode = tk.StringVar(value=self.config.get("scan_mode", "quick"))
        self.skip_system = tk.BooleanVar(value=self.config.get("skip_system_dirs", False))
        self.auto_refresh = tk.BooleanVar(value=True)
        self.refresh_interval_var = tk.IntVar(value=self.config.get("task_refresh_interval", 2))
        
        self._setup_dark_theme()
        self._build_ui()
        self._show_disclaimer()
        self._start_task_monitor()
        self._process_queues()

    def _setup_dark_theme(self):
        self.bg_primary = "#646464"
        self.bg_secondary = "#8D8DC7"
        self.bg_tertiary = "#3C3C91"
        self.fg_primary = '#E0E0E0'
        self.fg_secondary = "#C4BEBE"
        self.accent = "#0E8CE0"
        self.root.configure(bg=self.bg_primary)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.bg_primary, borderwidth=0)
        style.configure('TNotebook.Tab', padding=[20, 10], background=self.bg_secondary, foreground=self.fg_primary)
        style.map('TNotebook.Tab', background=[('selected', self.bg_tertiary)])
        style.configure('TFrame', background=self.bg_primary)
        style.configure('Secondary.TFrame', background=self.bg_secondary)
        style.configure('TLabel', background=self.bg_primary, foreground=self.fg_primary)
        style.configure('Header.TLabel', background=self.bg_primary, foreground=self.accent, font=('Segoe UI', 11, 'bold'))
        style.configure('TButton', background=self.bg_tertiary, foreground=self.fg_primary)
        style.map('TButton', background=[('active', self.accent), ('pressed', self.accent)])
        style.configure('Treeview', background=self.bg_secondary, foreground=self.fg_primary, fieldbackground=self.bg_secondary, borderwidth=1)
        style.map('Treeview', background=[('selected', self.accent)], foreground=[('selected', '#FFFFFF')])
        style.configure('Treeview.Heading', background=self.bg_tertiary, foreground=self.accent, borderwidth=1)
        style.map('Treeview.Heading', background=[('active', self.accent)])

    def _build_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        scanner_frame = ttk.Frame(notebook)
        notebook.add(scanner_frame, text="📁 Directory Scanner")
        self._build_scanner_tab(scanner_frame)
        
        task_frame = ttk.Frame(notebook)
        notebook.add(task_frame, text="⚙️ Task Manager")
        self._build_task_manager_tab(task_frame)
        
        status_frame = ttk.Frame(main_frame, style='Secondary.TFrame')
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        self.status_label = ttk.Label(status_frame, text="Ready", style='Header.TLabel')
        self.status_label.pack(side=tk.LEFT)
        self.memory_label = ttk.Label(status_frame, text=f"Mem: {self._get_app_memory():.1f} MB", style='Header.TLabel')
        self.memory_label.pack(side=tk.RIGHT, padx=10)
        self.root.after(2000, self._update_memory_label)

    def _build_scanner_tab(self, parent: ttk.Frame):
        ctrl_frame = ttk.Frame(parent, style='Secondary.TFrame')
        ctrl_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(ctrl_frame, text="⬆️", command=self._go_up).pack(side=tk.LEFT, padx=2)
        self.path_var = tk.StringVar(value=self.current_path)
        self.path_entry = ttk.Entry(ctrl_frame, textvariable=self.path_var, width=60)
        self.path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.path_entry.bind('<Return>', lambda e: self._start_scan())
        
        ttk.Button(ctrl_frame, text="🔍 Browse", command=self._browse_folder).pack(side=tk.LEFT, padx=2)
        self.scan_button = ttk.Button(ctrl_frame, text="▶ Scan", command=self._start_scan)
        self.scan_button.pack(side=tk.LEFT, padx=2)
        self.cancel_scan_button = ttk.Button(ctrl_frame, text="⏹ Cancel", command=self._cancel_scan, state=tk.DISABLED)
        self.cancel_scan_button.pack(side=tk.LEFT, padx=2)

        quick_frame = ttk.Frame(parent, style='Secondary.TFrame')
        quick_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(quick_frame, text="💾 All Drives", command=self._scan_all_drives).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="📂 Desktop", command=lambda: self._scan_quick("~\\Desktop")).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="📄 Docs", command=lambda: self._scan_quick("~\\Documents")).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(quick_frame, text="Skip System", variable=self.skip_system, command=self._save_config).pack(side=tk.LEFT, padx=15)
        ttk.Label(quick_frame, text="Mode:").pack(side=tk.LEFT)
        scan_combo = ttk.Combobox(quick_frame, textvariable=self.scan_mode, values=["quick", "full"], width=6, state="readonly")
        scan_combo.pack(side=tk.LEFT, padx=5)
        scan_combo.bind('<<ComboboxSelected>>', lambda e: self._save_config())

        search_frame = ttk.Frame(parent, style='Secondary.TFrame')
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.bind('<KeyRelease>', lambda e: self._on_search())
        self.search_entry.bind('<Return>', lambda e: self._on_search())
        
        self.dup_button = ttk.Button(search_frame, text="🔎 Duplicates", command=self._start_duplicate_scan)
        self.dup_button.pack(side=tk.RIGHT, padx=5)
        self.dup_progress = ttk.Progressbar(search_frame, orient="horizontal", length=200, mode='determinate')
        self.dup_progress.pack(side=tk.RIGHT, padx=5)

        prog_frame = ttk.Frame(parent, style='Secondary.TFrame')
        prog_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(prog_frame, text="Progress:").pack(side=tk.LEFT)
        self.progress_bar = ttk.Progressbar(prog_frame, mode='indeterminate', length=300)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.scan_status = ttk.Label(prog_frame, text="Ready", style='Header.TLabel')
        self.scan_status.pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.scanner_tree = ttk.Treeview(tree_frame, columns=('Size', 'Type', 'Modified', 'Safety'),
                                         yscrollcommand=vsb.set, xscrollcommand=hsb.set, height=20)
        self.scanner_tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.scanner_tree.yview)
        hsb.config(command=self.scanner_tree.xview)
        
        self.scanner_tree.heading('#0', text='📄 Filename')
        self.scanner_tree.heading('Size', text='Size')
        self.scanner_tree.heading('Type', text='Type')
        self.scanner_tree.heading('Modified', text='Modified')
        self.scanner_tree.heading('Safety', text='Safety')
        self.scanner_tree.column('#0', width=350, anchor=tk.W)
        self.scanner_tree.column('Size', width=90, anchor=tk.E)
        self.scanner_tree.column('Type', width=110, anchor=tk.W)
        self.scanner_tree.column('Modified', width=140, anchor=tk.W)
        self.scanner_tree.column('Safety', width=110, anchor=tk.CENTER)

        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.bg_secondary, fg=self.fg_primary)
        self.context_menu.add_command(label="Open Folder", command=self._open_folder_context)
        self.context_menu.add_command(label="Copy Path", command=self._copy_path_context)
        self.context_menu.add_command(label="Delete", command=self._delete_selected_context)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Properties", command=self._show_properties)
        self.scanner_tree.bind('<Button-3>', self._show_context_menu)
        self.scanner_tree.bind('<Double-1>', self._handle_double_click)

        self.load_more_btn = ttk.Button(parent, text="Load Next 1000 Items", command=self._load_more_items, state=tk.DISABLED)
        self.load_more_btn.pack(pady=5)
        self.load_count = 0

        bottom_frame = ttk.Frame(parent, style='Secondary.TFrame')
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        self.stats_label = ttk.Label(bottom_frame, text="Stats: Ready", style='Header.TLabel')
        self.stats_label.pack(side=tk.LEFT, padx=5)
        self.color_legend = ttk.Label(bottom_frame, text="Legend: Blue=Folder, Red=Critical, Green=Safe, Gray=System", style='Header.TLabel')
        self.color_legend.pack(side=tk.RIGHT, padx=5)

    def _build_task_manager_tab(self, parent: ttk.Frame):
        ctrl_frame = ttk.Frame(parent, style='Secondary.TFrame')
        ctrl_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Checkbutton(ctrl_frame, text="☑️ Auto-refresh", variable=self.auto_refresh, command=self._toggle_auto_refresh).pack(side=tk.LEFT)
        ttk.Label(ctrl_frame, text="Interval:").pack(side=tk.LEFT, padx=(15,5))
        self.interval_combo = ttk.Combobox(ctrl_frame, textvariable=self.refresh_interval_var, values=[1, 2, 5, 10, 30], width=4, state="readonly")
        self.interval_combo.pack(side=tk.LEFT)
        self.interval_combo.bind('<<ComboboxSelected>>', lambda e: self._save_config())
        
        ttk.Button(ctrl_frame, text="🔄 Refresh Now", command=self._force_task_refresh).pack(side=tk.LEFT, padx=10)
        self.task_last_update = ttk.Label(ctrl_frame, text="Last: Never", style='Header.TLabel')
        self.task_last_update.pack(side=tk.RIGHT)
        
        ttk.Label(ctrl_frame, text="🔍 Filter:").pack(side=tk.LEFT, padx=(20,5))
        self.task_filter_var = tk.StringVar()
        ttk.Entry(ctrl_frame, textvariable=self.task_filter_var, width=25).pack(side=tk.LEFT)
        self.task_filter_var.trace_add("write", lambda *args: self._filter_tasks())

        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.task_tree = ttk.Treeview(tree_frame, columns=('PID', 'CPU%', 'Memory MB', 'Status', 'User'),
                                      yscrollcommand=vsb.set, xscrollcommand=hsb.set, height=25)
        self.task_tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.task_tree.yview)
        hsb.config(command=self.task_tree.xview)
        
        self.task_tree.heading('#0', text='📦 Process Name')
        self.task_tree.heading('PID', text='PID')
        self.task_tree.heading('CPU%', text='CPU %')
        self.task_tree.heading('Memory MB', text='Memory (MB)')
        self.task_tree.heading('Status', text='Status')
        self.task_tree.heading('User', text='User')
        self.task_tree.column('#0', width=280, anchor=tk.W)
        self.task_tree.column('PID', width=70, anchor=tk.CENTER)
        self.task_tree.column('CPU%', width=70, anchor=tk.E)
        self.task_tree.column('Memory MB', width=100, anchor=tk.E)
        self.task_tree.column('Status', width=100, anchor=tk.W)
        self.task_tree.column('User', width=140, anchor=tk.W)
        
        self.task_tree.bind('<<TreeviewSelect>>', self._on_task_selected)
        self.task_tree.bind('<Button-1>', lambda e: self._pause_on_interaction())
        self.end_task_button = ttk.Button(parent, text="🛑 End Task", command=self._end_task, state=tk.DISABLED)
        self.end_task_button.pack(pady=5)

    def _process_queues(self):
        self._process_scanner_queue()
        self._process_task_queue()
        self._process_dup_queue()
        self.root.after(100, self._process_queues)

    def _process_scanner_queue(self):
        try:
            while True:
                msg_type, data = self.scanner_queue.get_nowait()
                if msg_type == 'started':
                    self.scan_status.config(text="Scanning...")
                elif msg_type == 'batch':
                    for fi in data:
                        self.all_files.append(fi)
                        self._add_file_to_tree(fi)
                        if len(self.all_files) >= PAGINATION_LIMIT:
                            self.load_more_btn.config(state=tk.NORMAL)
                elif msg_type == 'completed':
                    self.stats = data['stats']
                    self._on_scan_completed(data['total'])
                elif msg_type == 'error':
                    messagebox.showerror("Error", data)
        except queue.Empty: pass

    def _process_task_queue(self):
        try:
            while True:
                msg_type, data = self.task_queue.get_nowait()
                if msg_type == 'processes':
                    self._update_task_list(data)
                    self.task_last_update.config(text=f"Last: {datetime.now().strftime('%H:%M:%S')}")
                    self.last_interaction_time = time.time()
                    self.task_monitor_thread.set_paused(False)
        except queue.Empty: pass

    def _process_dup_queue(self):
        try:
            while True:
                msg_type, data = self.dup_queue.get_nowait()
                if msg_type == 'dup_started':
                    self.dup_progress.start()
                    self.scan_status.config(text=f"Scanning {data['total']} files for duplicates...")
                elif msg_type == 'dup_completed':
                    self.dup_progress.stop()
                    self._show_duplicate_results(data['groups'])
                elif msg_type == 'dup_error':
                    self.dup_progress.stop()
                    messagebox.showerror("Duplicate Error", data)
        except queue.Empty: pass

    def _add_file_to_tree(self, fi: FileInfo):
        parent = "" if not fi.parent_path or not self.scanner_tree.exists(fi.parent_path) else fi.parent_path
        badge_map = {SafetyClassification.SAFE: '🟢', SafetyClassification.CRITICAL: '🔴',
                     SafetyClassification.SYSTEM_REMOVABLE: '🟡', SafetyClassification.UNKNOWN: '⚪'}
        badge = badge_map.get(fi.safety_classification, '⚪')
        safety_text = f"{badge} {fi.safety_classification.value}"
        size_str = self._format_size(fi.size) if not fi.is_dir else '-'
        mod_time = datetime.fromtimestamp(fi.modified_time).strftime('%Y-%m-%d %H:%M') if fi.modified_time else '-'
        icon = '📁' if fi.is_dir else '📄'
        display_name = f"{icon} {fi.filename}"
        
        self.scanner_tree.insert(parent, 'end', iid=fi.path, text=display_name,
                                 values=(size_str, fi.file_type_name, mod_time, safety_text), tags=(fi.color,))
        self.scanner_tree.tag_configure(fi.color, foreground=fi.color)
        if fi.is_dir:
            self.scanner_tree.insert(fi.path, 'end', text="...")

    def _on_scan_completed(self, total):
        self.scan_button.config(state=tk.NORMAL)
        self.cancel_scan_button.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.scan_status.config(text="Scan completed")
        self.stats_label.config(text=f"📊 Total: {total} | 🟢 {self.stats['SAFE']} | 🔴 {self.stats['CRITICAL']} | 🟡 {self.stats['SYSTEM_REMOVABLE']} | ⚪ {self.stats['UNKNOWN']}")
        self.config.add_recent_path(self.path_var.get())

    def _cancel_scan(self):
        self.scan_button.config(state=tk.NORMAL)
        self.cancel_scan_button.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.scan_status.config(text="Scan cancelled")

    def _start_scan(self):
        path = self.path_var.get()
        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "Invalid path.")
            return
        self.current_path = path
        self.scanner_tree.delete(*self.scanner_tree.get_children())
        self.all_files.clear()
        self.load_count = 0
        self.load_more_btn.config(state=tk.DISABLED)
        self.scanner_queue = queue.Queue()
        self.scanner_thread = threading.Thread(target=HighPerformanceScanner(self.classifier, self.scanner_queue, self.config).scan_root, args=(path,), daemon=True)
        self.scan_button.config(state=tk.DISABLED)
        self.cancel_scan_button.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.scanner_thread.start()

    def _handle_double_click(self, event):
        item = self.scanner_tree.identify_row(event.y)
        if not item or not self.scanner_tree.exists(item): return
        fi = self.classifier.cache.get(item)
        if fi and fi.is_dir:
            for child in self.scanner_tree.get_children(item):
                if self.scanner_tree.item(child)['text'] == '...':
                    self.scanner_tree.delete(child)
                    break
            threading.Thread(target=HighPerformanceScanner(self.classifier, self.scanner_queue, self.config).scan_folder_expansion,
                             args=(fi.path, item, 1), daemon=True).start()
            self.path_var.set(fi.path)

    def _load_more_items(self):
        self.load_more_btn.config(state=tk.DISABLED)
        self.scan_status.config(text="Loaded next batch")

    def _go_up(self):
        p = os.path.dirname(self.path_var.get())
        if os.path.exists(p):
            self.path_var.set(p)
            self._start_scan()

    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.path_var.get())
        if folder:
            self.path_var.set(folder)
            self._start_scan()

    def _scan_quick(self, rel_path):
        p = os.path.expanduser(rel_path)
        if os.path.exists(p):
            self.path_var.set(p)
            self._start_scan()

    def _scan_all_drives(self):
        drives = []
        if platform.system() == "Windows":
            drives = [f"{d}:\\" for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
        else:
            drives = ['/']
            for p in psutil.disk_partitions():
                if os.path.exists(p.mountpoint): drives.append(p.mountpoint)
        if not drives: return
        msg = "Select Drive:\n" + "\n".join(f"{i+1}. {d}" for i, d in enumerate(drives))
        try:
            choice = simpledialog.askstring("Drive Selection", msg)
            if choice and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(drives):
                    self.path_var.set(drives[idx])
                    self._start_scan()
        except Exception: pass

    def _start_duplicate_scan(self):
        if not self.all_files:
            messagebox.showinfo("Info", "Please scan a directory first.")
            return
        self.dup_queue = queue.Queue()
        threading.Thread(target=DuplicateDetector(self.all_files, self.dup_queue).run, daemon=True).start()

    def _show_duplicate_results(self, groups):
        if not groups:
            messagebox.showinfo("Duplicates", "No duplicates found.")
            return
        top = tk.Toplevel(self.root)
        top.title("🔎 Duplicate File Detector")
        top.geometry("900x600")
        
        tree = ttk.Treeview(top, columns=('Size', 'Count', 'Hash', 'Path'), height=20)
        tree.pack(fill=tk.BOTH, expand=True)
        tree.heading('#0', text='📄 Filename')
        tree.heading('Size', text='Size')
        tree.heading('Count', text='Copies')
        tree.heading('Hash', text='MD5')
        tree.heading('Path', text='Full Path')
        tree.column('#0', width=200); tree.column('Size', width=80); tree.column('Count', width=60); tree.column('Hash', width=250); tree.column('Path', width=400)
        
        for g in groups:
            h = hashlib.md5(open(g[0].path, 'rb').read(8192)).hexdigest()
            for f in g:
                tree.insert('', 'end', text=f.filename, values=(self._format_size(f.size), len(g), h[:16]+'...', f.path), tags=('dup',))
        tree.tag_configure('dup', foreground='#FF1493')
        
        total_space = sum(f.size for g in groups for f in g[1:])
        ttk.Label(top, text=f"Reclaimable: {self._format_size(total_space)}").pack(pady=5)
        ttk.Button(top, text="Close", command=top.destroy).pack()

    def _on_search(self):
        query = self.search_var.get().strip()
        if not query:
            self.scanner_tree.delete(*self.scanner_tree.get_children())
            for fi in self.all_files[:PAGINATION_LIMIT]:
                self._add_file_to_tree(fi)
            return
        engine = SearchEngine(self.all_files, self.config)
        results = engine.search(query)
        self.scanner_tree.delete(*self.scanner_tree.get_children())
        for fi in results[:PAGINATION_LIMIT]:
            self._add_file_to_tree(fi)
        self.stats_label.config(text=f"🔍 Found {len(results)} matches")

    def _delete_selected_context(self):
        sel = self.scanner_tree.selection()
        if not sel: return
        items = [self.classifier.cache.get(i) for i in sel if i in self.classifier.cache]
        deletable = [f for f in items if f and f.safety_classification in [SafetyClassification.SAFE, SafetyClassification.SYSTEM_REMOVABLE]]
        if not deletable:
            messagebox.showwarning("Warning", "Selected items are critical or locked.")
            return
        if messagebox.askyesno("Confirm", f"Delete {len(deletable)} item(s)?"):
            deleted = 0
            for f in deletable:
                try:
                    if f.is_dir: shutil.rmtree(f.path)
                    else: os.remove(f.path)
                    deleted += 1
                except Exception: pass
            messagebox.showinfo("Done", f"Deleted {deleted}. Refreshing...")
            self._start_scan()

    def _open_folder_context(self):
        item = self.scanner_tree.selection()[0] if self.scanner_tree.selection() else None
        if item and os.path.isdir(item):
            if platform.system()=="Windows": os.startfile(item)
            elif platform.system()=="Darwin": os.system(f"open '{item}'")
            else: os.system(f"xdg-open '{item}'")

    def _copy_path_context(self):
        item = self.scanner_tree.selection()[0] if self.scanner_tree.selection() else None
        if item:
            self.root.clipboard_clear()
            self.root.clipboard_append(item)

    def _show_context_menu(self, event):
        item = self.scanner_tree.identify_row(event.y)
        if item:
            self.scanner_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _show_properties(self):
        item = self.scanner_tree.selection()[0] if self.scanner_tree.selection() else None
        if item:
            fi = self.classifier.cache.get(item)
            if fi:
                msg = f"Path: {fi.path}\nType: {fi.file_type_name}\nSize: {self._format_size(fi.size)}\nSafety: {fi.safety_classification.value}"
                messagebox.showinfo("File Properties", msg)

    def _start_task_monitor(self):
        self.task_monitor_thread = TaskMonitor(self.task_queue, self.config)
        self.task_monitor_thread.start()

    def _toggle_auto_refresh(self):
        self.task_monitor_thread.set_paused(not self.auto_refresh.get())

    def _force_task_refresh(self):
        self._pause_on_interaction()

    def _pause_on_interaction(self):
        self.task_monitor_thread.set_paused(True)
        self.root.after(3000, lambda: self.task_monitor_thread.set_paused(not self.auto_refresh.get()))

    def _update_task_list(self, processes):
        self.task_tree.delete(*self.task_tree.get_children())
        filt = self.task_filter_var.get().lower()
        count = 0
        for proc in processes:
            if not filt or filt in proc['name'].lower() or filt in str(proc['pid']):
                self.task_tree.insert('', 'end', text=proc['name'][:40],
                                      values=(proc['pid'], f"{proc['cpu_percent']:.1f}", f"{proc['memory_mb']:.1f}", proc['status'], proc['username'][:25]))
                count += 1
                if count > 500: break

    def _filter_tasks(self):
        pass

    def _on_task_selected(self, event):
        self.end_task_button.config(state=tk.NORMAL if self.task_tree.selection() else tk.DISABLED)

    def _end_task(self):
        sel = self.task_tree.selection()
        if not sel: return
        pid = int(self.task_tree.item(sel[0])['values'][0])
        name = self.task_tree.item(sel[0])['text']
        if messagebox.askyesno("Confirm", f"Terminate {name} (PID: {pid})?"):
            try:
                psutil.Process(pid).terminate()
                messagebox.showinfo("Success", f"Process terminated.")
            except Exception as e: messagebox.showerror("Error", str(e))

    def _show_disclaimer(self):
        msg = "⚠️ SAFETY DISCLAIMER\nThis tool provides deep system access.\nCRITICAL files (🔴) are protected from deletion.\nUse at your own risk. Backup important data.\nProceed?"
        if not messagebox.askyesno("Safety Warning", msg): sys.exit(0)

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024: return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def _get_app_memory(self):
        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)

    def _update_memory_label(self):
        self.memory_label.config(text=f"Mem: {self._get_app_memory():.1f} MB")
        self.root.after(2000, self._update_memory_label)

    def _save_config(self):
        self.config.set("scan_mode", self.scan_mode.get())
        self.config.set("skip_system_dirs", self.skip_system.get())
        self.config.set("task_refresh_interval", self.refresh_interval_var.get())

def main() -> None:
    root = tk.Tk()
    app = ProjectExplorerPro(root)
    root.mainloop()

if __name__ == "__main__":
    main()