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
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
from datetime import datetime
import psutil
import ctypes

# ============================================================================
# CONFIGURATION MANAGER
# ============================================================================
class ConfigManager:
    """Handles loading/saving user preferences with advanced UI settings."""
    CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".explorer_pro_config.json")
    DEFAULTS = {
        "theme": "Modern Dark",
        "scan_mode": "quick",
        "skip_system_dirs": False,
        "task_refresh_interval": 2,
        "recent_paths": [],
        "search_case_sensitive": False,
        "search_regex": False,
        "search_include_hidden": True,
        "tree_depth_limit": 5,
        "font_size": 10,
        "window_geometry": "1450x850"
    }

    def __init__(self):
        self.config = self.DEFAULTS.copy()
        self.load()

    def load(self):
        if os.path.exists(self.CONFIG_PATH):
            try:
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        self.config.update(loaded)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Config load error: {e}")

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
# THEME SYSTEM
# ============================================================================
THEMES = {
    "Modern Dark": {
        "bg_primary": "#0A0A0F",
        "bg_secondary": "#16161F",
        "bg_tertiary": "#1F1F2E",
        "fg_primary": "#67E8F9",
        "fg_secondary": "#A5F3FC",
        "accent": "#22D3EE",
        "file_colors": {
            '.pdf': '#3B82F6', '.docx': '#3B82F6', '.doc': '#3B82F6', '.txt': '#60A5FA',
            '.xlsx': '#10B981', '.xls': '#10B981', '.csv': '#10B981', '.md': '#F97316',
            '.png': '#EC4899', '.jpg': '#EC4899', '.jpeg': '#EC4899', '.mp3': '#F59E0B',
            '.mp4': '#8B5CF6', '.mkv': '#8B5CF6', '.py': '#10B981', '.js': '#F59E0B',
            '.html': '#EF4444', '.css': '#3B82F6', '.zip': '#FBBF24', '.exe': '#EF4444',
            '.sys': '#6B7280', '.dll': '#6B7280', '.log': '#ECA5A5', '.db': '#DC2626',
            "folder": "#F59E0B", "folder_system": "#7F1D1D", "default": "#F472B6"
        }
    },
    "Deep Indigo": {
        "bg_primary": "#0F0F23",
        "bg_secondary": "#1A1A3E",
        "bg_tertiary": "#2D2D5F",
        "fg_primary": "#A8D8FF",
        "fg_secondary": "#C7E9FF",
        "accent": "#7C3AED",
        "file_colors": {
            '.pdf': '#4F46E5', '.docx': '#4F46E5', '.doc': '#4F46E5', '.txt': '#818CF8',
            '.xlsx': '#06B6D4', '.xls': '#06B6D4', '.csv': '#06B6D4', '.md': '#FB923C',
            '.png': '#EC4899', '.jpg': '#EC4899', '.jpeg': '#EC4899', '.mp3': '#FBBF24',
            '.mp4': '#A78BFA', '.mkv': '#A78BFA', '.py': '#10B981', '.js': '#F97316',
            '.html': '#F87171', '.css': '#4F46E5', '.zip': '#FCD34D', '.exe': '#EF4444',
            '.sys': '#4B5563', '.dll': '#6B7280', '.log': '#FECACA', '.db': '#DC2626',
            "folder": "#A78BFA", "folder_system": "#4C0519", "default": "#C084FC"
        }
    },
    "Cyber Neon": {
        "bg_primary": "#000000",
        "bg_secondary": "#0D1117",
        "bg_tertiary": "#161B22",
        "fg_primary": "#00FF88",
        "fg_secondary": "#00FFCC",
        "accent": "#00FF00",
        "file_colors": {
            '.pdf': '#00FF00', '.docx': '#00FF00', '.doc': '#00FF00', '.txt': '#00FFCC',
            '.xlsx': '#FF00FF', '.xls': '#FF00FF', '.csv': '#FF00FF', '.md': '#FFFF00',
            '.png': '#FF0080', '.jpg': '#FF0080', '.jpeg': '#FF0080', '.mp3': '#00FFFF',
            '.mp4': '#00FF88', '.mkv': '#00FF88', '.py': '#00FF00', '.js': '#FFFF00',
            '.html': '#FF0000', '.css': '#00FF00', '.zip': '#FFFF00', '.exe': '#FF0000',
            '.sys': '#00FFCC', '.dll': '#00FFCC', '.log': '#FF00FF', '.db': '#FF0000',
            "folder": "#00FF88", "folder_system": "#660000", "default": "#FF00FF"
        }
    },
    "Soft Warm": {
        "bg_primary": "#FBF8F3",
        "bg_secondary": "#F5F1E8",
        "bg_tertiary": "#EFE9E0",
        "fg_primary": "#5A4A42",
        "fg_secondary": "#7B6B63",
        "accent": "#D4876C",
        "file_colors": {
            '.pdf': '#8B6F47', '.docx': '#8B6F47', '.doc': '#8B6F47', '.txt': '#A0826D',
            '.xlsx': '#7FB069', '.xls': '#7FB069', '.csv': '#7FB069', '.md': '#D4876C',
            '.png': '#D4876C', '.jpg': '#D4876C', '.jpeg': '#D4876C', '.mp3': '#C89D5A',
            '.mp4': '#B8956A', '.mkv': '#B8956A', '.py': '#7FB069', '.js': '#D4876C',
            '.html': '#C85A54', '.css': '#8B6F47', '.zip': '#D4A574', '.exe': '#C85A54',
            '.sys': '#9B9B9B', '.dll': '#A0A0A0', '.log': '#E6B5A8', '.db': '#A94432',
            "folder": "#C89D5A", "folder_system": "#5A3A2A", "default": "#D4A574"
        }
    },
    "Ocean Blue": {
        "bg_primary": "#0D1B2A",
        "bg_secondary": "#1B3A52",
        "bg_tertiary": "#265C84",
        "fg_primary": "#90E0EF",
        "fg_secondary": "#CAF0F8",
        "accent": "#00B4D8",
        "file_colors": {
            '.pdf': '#0077B6', '.docx': '#0077B6', '.doc': '#0077B6', '.txt': '#0096C7',
            '.xlsx': '#00D9FF', '.xls': '#00D9FF', '.csv': '#00D9FF', '.md': '#03045E',
            '.png': '#FF006E', '.jpg': '#FF006E', '.jpeg': '#FF006E', '.mp3': '#FB5607',
            '.mp4': '#00B4D8', '.mkv': '#00B4D8', '.py': '#00D9FF', '.js': '#FB5607',
            '.html': '#FF006E', '.css': '#0077B6', '.zip': '#FFB703', '.exe': '#D62828',
            '.sys': '#4A90E2', '.dll': '#4A90E2', '.log': '#90E0EF', '.db': '#D62828',
            "folder": "#00B4D8", "folder_system": "#03045E", "default": "#90E0EF"
        }
    },
    "White": {
        "bg_primary": "#FFFFFF",
        "bg_secondary": "#F9F9F9",
        "bg_tertiary": "#F0F0F0",
        "fg_primary": "#1F2937",
        "fg_secondary": "#4B5563",
        "accent": "#3B82F6",
        "file_colors": {
            '.pdf': '#1E40AF', '.docx': '#1E40AF', '.doc': '#1E40AF', '.txt': '#1E40AF',
            '.xlsx': '#059669', '.xls': '#059669', '.csv': '#059669', '.md': '#D97706',
            '.png': '#DC2626', '.jpg': '#DC2626', '.jpeg': '#DC2626', '.mp3': '#EA580C',
            '.mp4': '#7C3AED', '.mkv': '#7C3AED', '.py': '#059669', '.js': '#D97706',
            '.html': '#DC2626', '.css': '#1E40AF', '.zip': '#D97706', '.exe': '#DC2626',
            '.sys': '#6B7280', '.dll': '#6B7280', '.log': '#991B1B', '.db': '#991B1B',
            "folder": "#D97706", "folder_system": "#7F1D1D", "default": "#9CA3AF"
        }
    }
}

# ============================================================================
# CONSTANTS & DATA CLASSES
# ============================================================================

SAFE_PATTERNS = {
    'extensions': {'.tmp', '.bak', '.temp', '.cache', '.crdownload', '.part', '.downloading', '.~tmp'},
    'directories': {'pycache', '.cache', '.pytest_cache', '.mypy_cache', 'node_modules', 'Cache'},
    'path_segments': {'temp', 'tmp', 'cache', 'downloads', '$Recycle.Bin', '.cache'},
}
CRITICAL_PATTERNS = {
    'directories': {'Windows', 'System32', 'SysWOW64', 'Program Files', 'Program Files (x86)', 'ProgramData', 'Recovery', 'Boot', 'WinSxS', 'etc', 'bin', 'lib', 'sbin', 'var'},
    'path_prefixes': {'C:\\Windows', 'C:\\System32', 'C:\\Program Files', 'C:\\ProgramData', '/usr/bin', '/usr/lib', '/etc', '/System', '/Library', '/bin', '/sbin', '/var'},
}

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
        if self.is_dir != other.is_dir: return self.is_dir
        return self.filename.lower() < other.filename.lower()

class ProcessSafety(Enum):
    CRITICAL_SYSTEM = "Critical System"
    HIGH_RESOURCE = "High Resource"
    SAFE = "Safe to End"
    UNKNOWN = "Unknown"

# ============================================================================
# CACHING & CLASSIFIERS
# ============================================================================
class LRU_Cache:
    def __init__(self, maxsize=5000):
        self.cache = OrderedDict()
        self.maxsize = max(100, maxsize)  # Ensure minimum size
        self.lock = threading.Lock()

    def get(self, key, default=None):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            return default

    def set(self, key, value):
        with self.lock:
            if key in self.cache:
                del self.cache[key]  # Remove to update position
            self.cache[key] = value
            self.cache.move_to_end(key)
            while len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)
    
    def clear(self):
        with self.lock:
            self.cache.clear()

class FileClassifier:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.is_windows = platform.system() == "Windows"
        self.running_process_paths = self._get_running_process_paths()
        self.cache = LRU_Cache(maxsize=8000)
        self.current_theme = THEMES.get(self.config.get("theme", "Modern Dark"), THEMES["Modern Dark"])

    def _get_color_for_file(self, ext: str, is_dir: bool, is_critical: bool) -> str:
        """Get file color based on current theme"""
        theme_colors = self.current_theme.get("file_colors", {})
        
        if is_dir:
            return theme_colors.get("folder_system") if is_critical else theme_colors.get("folder", "#FFD700")
        
        ext_lower = ext.lower()
        return theme_colors.get(ext_lower, theme_colors.get("default", "#A0A0A0"))

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

    def classify(self, path: str, use_cache: bool = True, scan_mode: str = "quick") -> FileInfo:
        if use_cache:
            cached = self.cache.get(path)
            if cached: return cached

        try:
            stat_info = os.stat(path)
            is_dir = os.path.isdir(path)
            size = stat_info.st_size if not is_dir else 0
            mtime = stat_info.st_mtime
        except (OSError, PermissionError):
            theme_colors = self.current_theme.get("file_colors", {})
            color = theme_colors.get("default", "#A0A0A0")
            fi = FileInfo(path, os.path.basename(path), '', False, 0, SafetyClassification.UNKNOWN, color, parent_path=os.path.dirname(path))
            self.cache.set(path, fi)
            return fi

        filename = os.path.basename(path)
        ext = os.path.splitext(filename)[1].lower()
        path_lower = path.lower()

        safety = SafetyClassification.UNKNOWN
        if scan_mode == "full":
            safety = self._classify_safety(path, path_lower, filename, ext)

        is_critical = (safety == SafetyClassification.CRITICAL or 
                       filename in CRITICAL_PATTERNS.get('directories', set()))
        color = self._get_color_for_file(ext, is_dir, is_critical)
        file_type_name = 'Folder' if is_dir else self._get_file_type_name(ext)

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

    def _is_critical(self, path, path_lower, filename, ext):
        if path_lower in self.running_process_paths: return True
        if filename in CRITICAL_PATTERNS.get('directories', set()): return True
        if ext.lower() in {'.dll', '.sys', '.exe', '.vbs', '.bat', '.ps1'}: return True
        for prefix in CRITICAL_PATTERNS.get('path_prefixes', set()):
            if path_lower.startswith(prefix.lower()): return True
        return False

    def _is_system_removable(self, path, path_lower, filename):
        if filename in {'Windows.old', 'Prefetch', '$WINDOWS.~BT', 'installer', 'backup'}: return True
        return any(seg in path_lower.split(os.sep) for seg in {'windows.old', 'prefetch', 'installer_cache', 'old_windows'})

    def _is_safe(self, path, path_lower, filename, ext):
        if ext.lower() in SAFE_PATTERNS.get('extensions', set()): return True
        if filename in SAFE_PATTERNS.get('directories', set()): return True
        return any(seg in path_lower.split(os.sep) for seg in SAFE_PATTERNS.get('path_segments', set()))

    @staticmethod
    def _get_file_type_name(ext: str) -> str:
        type_map = {
            '.pdf': 'PDF Document', '.docx': 'Word Document', '.xlsx': 'Excel Spreadsheet',
            '.py': 'Python Script', '.js': 'JavaScript', '.html': 'Web Page',
            '.jpg': 'JPEG Image', '.png': 'PNG Image', '.zip': 'ZIP Archive',
            '.exe': 'Application', '.mp4': 'MP4 Video', '.mp3': 'MP3 Audio',
        }
        return type_map.get(ext, f'{ext[1:].upper()} File' if ext else 'File')

# ============================================================================
# SCANNER & TASK MONITOR
# ============================================================================
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
        depth = max_depth or self.config.get("tree_depth_limit", 5)
        self.result_queue.put(('started', {'path': root_path}))
        self._scan_recursive(root_path, 0, depth, scan_mode, skip_sys)
        self._flush_batch()
        self.result_queue.put(('completed', {'total': self._total_scanned, 'stats': self.stats.copy()}))

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
                if len(self._batch_buffer) >= 500: self._flush_batch()
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
        critical_names = {'explorer.exe', 'svchost.exe', 'csrss.exe', 'wininit.exe', 'winlogon.exe', 
                          'lsass.exe', 'system', 'Idle', 'kernel_task', 'systemd', 'launchd'}
        for proc in psutil.process_iter(['pid', 'name', 'status', 'username', 'cpu_percent', 'memory_info']):
            try:
                with proc.oneshot():
                    mem_mb = proc.memory_info().rss / (1024 * 1024)
                    cpu = proc.cpu_percent(interval=0)
                    name = proc.name() or "Unknown"
                    username = proc.username() if hasattr(proc, 'username') and proc.username() else 'System'
                    
                    # Classification Logic
                    if name.lower() in critical_names or username.lower() in ('system', 'local system', 'root'):
                        safety = ProcessSafety.CRITICAL_SYSTEM
                    elif cpu > 50.0 or mem_mb > 1500:
                        safety = ProcessSafety.HIGH_RESOURCE
                    else:
                        safety = ProcessSafety.SAFE

                    processes.append({
                        'pid': proc.pid, 'name': name, 'cpu_percent': cpu,
                        'memory_mb': mem_mb, 'status': proc.status(),
                        'username': username,
                        'safety': safety.value
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError): pass
        processes.sort(key=lambda x: x['memory_mb'], reverse=True)
        return processes

# ============================================================================
# FILE OPERATIONS & DRAG-DROP
# ============================================================================
class FileClipboard:
    def __init__(self):
        self.mode = None  # 'copy' or 'cut'
        self.paths: List[str] = []
        self.lock = threading.Lock()
    
    def _validate_paths(self, paths: List[str]) -> bool:
        """Validate paths exist and are accessible"""
        if not isinstance(paths, list):
            return False
        for p in paths:
            if not isinstance(p, str) or not os.path.exists(p):
                return False
        return True

    def copy(self, paths: List[str]):
        if not self._validate_paths(paths):
            return False
        with self.lock:
            self.mode = 'copy'
            self.paths = paths[:]
        return True

    def cut(self, paths: List[str]):
        if not self._validate_paths(paths):
            return False
        with self.lock:
            self.mode = 'cut'
            self.paths = paths[:]
        return True

    def paste(self, dest_dir: str) -> Tuple[int, int]:
        if not isinstance(dest_dir, str) or not os.path.isdir(dest_dir):
            return 0, 0
        
        with self.lock:
            if not self.paths:
                return 0, 0
            paths_to_process = self.paths[:]
        
        moved, failed = 0, 0
        for src in paths_to_process:
            try:
                if not os.path.exists(src):
                    failed += 1
                    continue
                    
                dest = os.path.join(dest_dir, os.path.basename(src))
                
                # Prevent path traversal
                dest = os.path.normpath(dest)
                if not dest.startswith(os.path.normpath(dest_dir)):
                    failed += 1
                    continue
                
                if os.path.exists(dest):
                    dest = f"{dest}_{int(time.time())}"
                
                if self.mode == 'cut':
                    shutil.move(src, dest)
                else:
                    if os.path.isdir(src):
                        shutil.copytree(src, dest)
                    else:
                        shutil.copy2(src, dest)
                moved += 1
            except (OSError, PermissionError, shutil.Error) as e:
                failed += 1
        
        if self.mode == 'cut':
            with self.lock:
                self.paths.clear()
                self.mode = None
        
        return moved, failed

    def delete_selected(self, paths: List[str]) -> int:
        deleted = 0
        for p in paths:
            try:
                if not isinstance(p, str) or not os.path.exists(p):
                    continue
                # Prevent deletion of critical paths
                p_lower = os.path.normpath(p).lower()
                if any(p_lower.startswith(cp.lower()) for cp in CRITICAL_PATTERNS.get('path_prefixes', set())):
                    continue
                if os.path.isdir(p):
                    shutil.rmtree(p)
                else:
                    os.remove(p)
                deleted += 1
            except (OSError, PermissionError, shutil.Error):
                pass
        return deleted

class DragDropManager:
    """Internal drag & drop manager for Tkinter Treeview"""
    def __init__(self, tree: ttk.Treeview, classifier: FileClassifier, on_drop_callback):
        self.tree = tree
        self.classifier = classifier
        self.on_drop = on_drop_callback
        self.drag_start = None
        self.drag_items = []
        self.drag_preview = None
        self.drop_target = None

        self.tree.bind('<Button-1>', self._on_press)
        self.tree.bind('<B1-Motion>', self._on_drag)
        self.tree.bind('<ButtonRelease-1>', self._on_release)
        self.tree.bind('<Motion>', self._on_hover)

    def _on_press(self, event):
        item = self.tree.identify_row(event.y)
        if not item: return
        self.drag_start = (event.x, event.y)
        self.drag_items = [item]

    def _on_drag(self, event):
        if not self.drag_start: return
        dx, dy = event.x - self.drag_start[0], event.y - self.drag_start[1]
        if abs(dx) > 10 or abs(dy) > 10:
            if not self.drag_preview:
                self.drag_preview = tk.Label(self.tree.master, text=f"📦 Dragging {len(self.drag_items)} item(s)", 
                                             bg="#FFD700", fg="#000", padx=10, pady=5, borderwidth=1, relief=tk.SOLID)
                self.drag_preview.place(x=event.x_root, y=event.y_root)

    def _on_hover(self, event):
        if not self.drag_preview: return
        target = self.tree.identify_row(event.y)
        if target != self.drop_target:
            if self.drop_target: self.tree.item(self.drop_target, tags=())
            self.drop_target = target
            if self.drop_target and self.classifier.cache.get(self.drop_target, FileInfo('', '', '', True, 0, SafetyClassification.UNKNOWN, '')).is_dir:
                self.tree.item(self.drop_target, tags=('drop_target',))
                self.tree.tag_configure('drop_target', background='#E0F7FA')

    def _on_release(self, event):
        if self.drag_preview:
            self.drag_preview.destroy()
            self.drag_preview = None
        
        if self.drop_target and self.drag_items:
            fi = self.classifier.cache.get(self.drop_target)
            if fi and fi.is_dir:
                self.on_drop(self.drag_items, fi.path)
        
        if self.drop_target: self.tree.item(self.drop_target, tags=())
        self.drag_start = None
        self.drag_items = []
        self.drop_target = None

# ============================================================================
# MAIN APPLICATION
# ============================================================================
class ProjectExplorerPro:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PROJECT EXPLORER PRO - v1.0")
        self.config = ConfigManager()
        
        # DPI Awareness (Windows)
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception: pass

        # State
        self.classifier = FileClassifier(self.config)
        self.scanner_queue = queue.Queue()
        self.task_queue = queue.Queue()
        self.dup_queue = queue.Queue()
        self.all_files: List[FileInfo] = []
        self.stats = {'SAFE': 0, 'CRITICAL': 0, 'SYSTEM_REMOVABLE': 0, 'UNKNOWN': 0}
        self.clipboard = FileClipboard()
        self.scanner_thread = None
        self.task_monitor_thread = None
        
        recent_paths = self.config.get("recent_paths", [])
        self.current_path = recent_paths[0] if recent_paths else (str(Path.home()) if platform.system() != "Windows" else "C:\\")
        
        self.scan_mode = tk.StringVar(value=self.config.get("scan_mode", "quick"))
        self.skip_system = tk.BooleanVar(value=self.config.get("skip_system_dirs", False))
        self.auto_refresh = tk.BooleanVar(value=True)
        self.refresh_interval_var = tk.IntVar(value=self.config.get("task_refresh_interval", 2))
        self.load_count = 0

        self._setup_theme()
        self._build_ui()
        self._show_disclaimer()
        self._start_task_monitor()
        self._process_queues()
        
        self.root.geometry(self.config.get("window_geometry", "1450x850"))
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_theme(self):
        c = self.config
        theme_name = c.get("theme", "Modern Dark")
        self.current_theme = THEMES.get(theme_name, THEMES["Modern Dark"])
        
        self.bg_primary = self.current_theme["bg_primary"]
        self.bg_secondary = self.current_theme["bg_secondary"]
        self.bg_tertiary = self.current_theme["bg_tertiary"]
        self.fg_primary = self.current_theme["fg_primary"]
        self.fg_secondary = self.current_theme["fg_secondary"]
        self.accent = self.current_theme["accent"]
        
        self.font_size = c.get("font_size", 10)
        self.default_font = ("Segoe UI", self.font_size)
        
        self.root.configure(bg=self.bg_primary)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.bg_primary, borderwidth=0)
        style.configure('TNotebook.Tab', padding=[20, 10], background=self.bg_secondary, foreground=self.fg_primary, font=self.default_font)
        style.map('TNotebook.Tab', background=[('selected', self.bg_tertiary)])
        style.configure('TFrame', background=self.bg_primary)
        style.configure('Secondary.TFrame', background=self.bg_secondary)
        style.configure('TLabel', background=self.bg_primary, foreground=self.fg_primary, font=self.default_font)
        style.configure('Header.TLabel', background=self.bg_primary, foreground=self.accent, font=('Segoe UI', self.font_size + 1, 'bold'))
        style.configure('TButton', background=self.bg_tertiary, foreground=self.fg_primary, font=self.default_font)
        style.map('TButton', background=[('active', self.accent)])
        style.configure('Treeview', background=self.bg_secondary, foreground=self.fg_primary, fieldbackground=self.bg_secondary, font=self.default_font)
        style.map('Treeview', background=[('selected', self.accent)], foreground=[('selected', '#FFFFFF')])
        style.configure('Treeview.Heading', background=self.bg_tertiary, foreground=self.accent, font=('Segoe UI', self.font_size, 'bold'))

    def _build_ui(self):
        menubar = tk.Menu(self.root, bg=self.bg_tertiary, fg=self.fg_primary)
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_tertiary, fg=self.fg_primary)
        file_menu.add_command(label="Open Settings", command=self._open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Copy", command=self._clipboard_copy, accelerator="Ctrl+C")
        file_menu.add_command(label="Cut", command=self._clipboard_cut, accelerator="Ctrl+X")
        file_menu.add_command(label="Paste", command=self._clipboard_paste, accelerator="Ctrl+V")
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        self.root.bind('<Control-c>', lambda e: self._clipboard_copy())
        self.root.bind('<Control-x>', lambda e: self._clipboard_cut())
        self.root.bind('<Control-v>', lambda e: self._clipboard_paste())
        self.root.bind('<Delete>', lambda e: self._delete_selected_context())
        self.root.bind('<F2>', lambda e: self._rename_selected())
        self.root.bind('<F5>', lambda e: self._start_scan())

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)

        self._build_scanner_tab(notebook)
        self._build_task_manager_tab(notebook)

        status_frame = ttk.Frame(self.root, style='Secondary.TFrame')
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        self.status_label = ttk.Label(status_frame, text="Ready", style='Header.TLabel')
        self.status_label.pack(side=tk.LEFT)
        self.memory_label = ttk.Label(status_frame, text=f"Mem: 0.0 MB", style='Header.TLabel')
        self.memory_label.pack(side=tk.RIGHT, padx=10)
        self.root.after(2000, self._update_memory_label)

    def _build_scanner_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Directory Scanner")

        ctrl = ttk.Frame(frame, style='Secondary.TFrame')
        ctrl.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(ctrl, text="Up", command=self._go_up).pack(side=tk.LEFT, padx=2)
        
        self.path_var = tk.StringVar(value=self.current_path)
        self.path_entry = ttk.Entry(ctrl, textvariable=self.path_var, width=60, font=self.default_font)
        self.path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.path_entry.bind('<Return>', lambda e: self._start_scan())
        
        ttk.Button(ctrl, text="Browse", command=self._browse_folder).pack(side=tk.LEFT, padx=2)
        self.scan_button = ttk.Button(ctrl, text="Scan", command=self._start_scan)
        self.scan_button.pack(side=tk.LEFT, padx=2)
        self.cancel_scan_button = ttk.Button(ctrl, text="Cancel", command=self._cancel_scan, state=tk.DISABLED)
        self.cancel_scan_button.pack(side=tk.LEFT, padx=2)

        quick = ttk.Frame(frame, style='Secondary.TFrame')
        quick.pack(fill=tk.X, padx=10, pady=5)
        for txt, cmd in [("Drives", self._scan_all_drives), ("Desktop", lambda: self._scan_quick("~\\Desktop")), ("Docs", lambda: self._scan_quick("~\\Documents"))]:
            ttk.Button(quick, text=txt, command=cmd).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(quick, text="Skip System", variable=self.skip_system, command=self._save_config).pack(side=tk.LEFT, padx=15)
        ttk.Label(quick, text="Mode: ").pack(side=tk.LEFT)
        scan_combo = ttk.Combobox(quick, textvariable=self.scan_mode, values=["quick", "full"], width=6, state="readonly", font=self.default_font)
        scan_combo.pack(side=tk.LEFT, padx=5)
        scan_combo.bind('<<ComboboxSelected>>', lambda e: self._save_config())

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.scanner_tree = ttk.Treeview(tree_frame, columns=('Size', 'Type', 'Modified', 'Safety'), yscrollcommand=vsb.set, xscrollcommand=hsb.set, height=20)
        self.scanner_tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.scanner_tree.yview)
        hsb.config(command=self.scanner_tree.xview)

        for col, w, anchor in [('#0', 350, tk.W), ('Size', 90, tk.E), ('Type', 110, tk.W), ('Modified', 140, tk.W), ('Safety', 110, tk.CENTER)]:
            self.scanner_tree.heading(col, text=col if col != '#0' else 'Filename')
            self.scanner_tree.column(col, width=w, anchor=anchor)

        DragDropManager(self.scanner_tree, self.classifier, self._handle_drop)
        
        self.scanner_tree.bind('<Double-1>', self._handle_double_click)
        self.scanner_tree.bind('<Button-3>', self._show_context_menu)
        
        self._build_context_menu()

        bottom = ttk.Frame(frame, style='Secondary.TFrame')
        bottom.pack(fill=tk.X, padx=10, pady=5)
        self.stats_label = ttk.Label(bottom, text="Stats: Ready", style='Header.TLabel')
        self.stats_label.pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(bottom, textvariable=self.search_var, width=30, font=self.default_font)
        search_entry.pack(side=tk.RIGHT, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self._on_search())
        search_entry.bind('<Return>', lambda e: self._on_search())

    def _build_task_manager_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Task Manager")

        ctrl = ttk.Frame(frame, style='Secondary.TFrame')
        ctrl.pack(fill=tk.X, padx=10, pady=10)
        ttk.Checkbutton(ctrl, text="Auto-refresh", variable=self.auto_refresh, command=self._toggle_auto_refresh).pack(side=tk.LEFT)
        ttk.Label(ctrl, text="Interval: ").pack(side=tk.LEFT, padx=(15,5))
        self.interval_combo = ttk.Combobox(ctrl, textvariable=self.refresh_interval_var, values=[1, 2, 5, 10, 30], width=4, state="readonly", font=self.default_font)
        self.interval_combo.pack(side=tk.LEFT)
        self.interval_combo.bind('<<ComboboxSelected>>', lambda e: self._save_config())
        ttk.Button(ctrl, text="Refresh Now", command=self._force_task_refresh).pack(side=tk.LEFT, padx=10)
        self.task_last_update = ttk.Label(ctrl, text="Last: Never", style='Header.TLabel')
        self.task_last_update.pack(side=tk.RIGHT)
        ttk.Label(ctrl, text="Filter: ").pack(side=tk.LEFT, padx=(20,5))
        self.task_filter_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.task_filter_var, width=25, font=self.default_font).pack(side=tk.LEFT)
        self.task_filter_var.trace_add("write", lambda *args: self._filter_tasks())

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.task_tree = ttk.Treeview(tree_frame, columns=('PID', 'CPU%', 'Memory MB', 'Status', 'User', 'Safety'), yscrollcommand=vsb.set, xscrollcommand=hsb.set, height=25)
        self.task_tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.task_tree.yview)
        hsb.config(command=self.task_tree.xview)
        
        self.task_tree.heading('#0', text='Process Name')
        for col, w, anchor in [('PID', 70, tk.CENTER), ('CPU%', 70, tk.E), ('Memory MB', 100, tk.E), ('Status', 100, tk.W), ('User', 140, tk.W), ('Safety', 130, tk.CENTER)]:
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=w, anchor=anchor)

        self.task_tree.tag_configure('critical', foreground='#FF4500')
        self.task_tree.tag_configure('high_res', foreground='#FFD700')
        self.task_tree.tag_configure('safe', foreground='#32CD32')
        
        self.task_tree.bind('<<TreeviewSelect>>', self._on_task_selected)
        self.end_task_button = ttk.Button(frame, text="End Task", command=self._end_task, state=tk.DISABLED)
        self.end_task_button.pack(pady=5)

    def _build_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.bg_secondary, fg=self.fg_primary, font=self.default_font)
        self.context_menu.add_command(label="Open", command=self._open_folder_context)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy", command=self._clipboard_copy, accelerator="Ctrl+C")
        self.context_menu.add_command(label="Cut", command=self._clipboard_cut, accelerator="Ctrl+X")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Paste Here", command=self._clipboard_paste, accelerator="Ctrl+V")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Rename", command=self._rename_selected, accelerator="F2")
        self.context_menu.add_command(label="Delete", command=self._delete_selected_context, accelerator="Del")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy Path", command=self._copy_path_context)
        self.context_menu.add_command(label="Properties", command=self._show_properties)

    def _show_context_menu(self, event):
        item = self.scanner_tree.identify_row(event.y)
        if item:
            self.scanner_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    # ==================== FILE OPERATIONS ====================
    def _clipboard_copy(self):
        sel = self.scanner_tree.selection()
        if sel:
            self.clipboard.copy(sel)
            self.status_label.config(text=f"Copied {len(sel)} item(s) to clipboard")

    def _clipboard_cut(self):
        sel = self.scanner_tree.selection()
        if sel:
            self.clipboard.cut(sel)
            self.status_label.config(text=f"Cut {len(sel)} item(s) to clipboard")

    def _clipboard_paste(self):
        target = self.current_path
        sel = self.scanner_tree.selection()
        if sel:
            fi = self.classifier.cache.get(sel[0])
            if fi and fi.is_dir: target = fi.path
        if not self.clipboard.paths: return
        moved, failed = self.clipboard.paste(target)
        self.status_label.config(text=f"Pasted {moved} items. {failed} failed.")
        self._start_scan()

    def _rename_selected(self):
        sel = self.scanner_tree.selection()
        if not sel: return
        old_path = sel[0]
        if not isinstance(old_path, str) or not os.path.exists(old_path):
            return
        
        new_name = simpledialog.askstring("Rename", "New name:", initialvalue=os.path.basename(old_path))
        if not new_name or new_name == os.path.basename(old_path):
            return
        
        # Validate new name
        if any(c in new_name for c in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            messagebox.showerror("Error", "Invalid characters in filename")
            return
        
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        try:
            os.rename(old_path, new_path)
            self.status_label.config(text=f"Renamed to {new_name}")
            self._start_scan()
        except (OSError, PermissionError) as e:
            messagebox.showerror("Error", f"Rename failed: {e}")

    def _handle_drop(self, source_items, dest_path):
        self.clipboard.cut(source_items)
        moved, _ = self.clipboard.paste(dest_path)
        self.status_label.config(text=f"Drag-dropped {moved} item(s)")
        self._start_scan()

    # ==================== SCANNER LOGIC ====================
    def _start_scan(self):
        path = self.path_var.get().strip()
        if not path or not isinstance(path, str):
            messagebox.showerror("Error", "Invalid path.")
            return
        
        path = os.path.normpath(path)
        if not os.path.exists(path) or not os.path.isdir(path):
            messagebox.showerror("Error", "Path does not exist or is not a directory.")
            return
        
        self.current_path = path
        self.scanner_tree.delete(*self.scanner_tree.get_children())
        self.all_files.clear()
        self.load_count = 0
        self.scanner_queue = queue.Queue()
        self.scanner_thread = threading.Thread(
            target=HighPerformanceScanner(self.classifier, self.scanner_queue, self.config).scan_root,
            args=(path,),
            daemon=True
        )
        self.scan_button.config(state=tk.DISABLED)
        self.cancel_scan_button.config(state=tk.NORMAL)
        self.status_label.config(text="Scanning...")
        self.scanner_thread.start()

    def _cancel_scan(self):
        if self.scanner_thread and self.scanner_thread.is_alive():
            self.scanner_thread.join(0.1) # Soft stop
        self.scan_button.config(state=tk.NORMAL)
        self.cancel_scan_button.config(state=tk.DISABLED)
        self.status_label.config(text="Scan cancelled")

    def _handle_double_click(self, event):
        item = self.scanner_tree.identify_row(event.y)
        if not item or not self.scanner_tree.exists(item): return
        fi = self.classifier.cache.get(item)
        if not fi or not os.path.exists(fi.path): return
        
        if fi.is_dir:
            self.path_var.set(fi.path)
            self._start_scan()
        else:
            try:
                if platform.system() == "Windows":
                    os.startfile(fi.path)
                elif platform.system() == "Darwin":
                    subprocess.run(["open", fi.path], check=False, timeout=5)
                else:
                    subprocess.run(["xdg-open", fi.path], check=False, timeout=5)
            except (subprocess.TimeoutExpired, OSError) as e:
                messagebox.showerror("Error", f"Cannot open file: {e}")

    def _on_search(self):
        query = self.search_var.get().strip()
        self.scanner_tree.delete(*self.scanner_tree.get_children())
        if not query:
            for fi in self.all_files: self._add_file_to_tree(fi)
            return
        
        # Limit query length to prevent ReDoS attacks
        if len(query) > 100:
            messagebox.showwarning("Warning", "Search query too long (max 100 chars)")
            return
        
        case_sens = self.config.get("search_case_sensitive", False)
        use_regex = self.config.get("search_regex", False)
        include_hidden = self.config.get("search_include_hidden", True)
        pattern = query if use_regex else re.escape(query)
        flags = 0 if case_sens else re.IGNORECASE
        
        try:
            # Set timeout for regex compilation
            compiled = re.compile(pattern, flags)
        except re.error as e:
            messagebox.showerror("Error", f"Invalid search pattern: {e}")
            return

        matches = [f for f in self.all_files if (include_hidden or not f.filename.startswith('.')) and compiled.search(f.filename)]
        for fi in matches[:1000]:  # Limit display results
            self._add_file_to_tree(fi)
        self.status_label.config(text=f"🔍 Found {len(matches)} matches (showing first 1000)")

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

    # ==================== TASK MANAGER LOGIC ====================
    def _update_task_list(self, processes):
        self.task_tree.delete(*self.task_tree.get_children())
        filt = self.task_filter_var.get().lower()
        for proc in processes:
            if not filt or filt in proc['name'].lower() or filt in str(proc['pid']):
                tag = 'critical' if 'Critical' in proc['safety'] else ('high_res' if 'High' in proc['safety'] else 'safe')
                self.task_tree.insert('', 'end', text=proc['name'][:40],
                                      values=(proc['pid'], f"{proc['cpu_percent']:.1f}", f"{proc['memory_mb']:.1f}", 
                                              proc['status'], proc['username'][:20], proc['safety']), tags=(tag,))

    def _filter_tasks(self): pass # Handled in update
    
    def _on_task_selected(self, event):
        self.end_task_button.config(state=tk.NORMAL if self.task_tree.selection() else tk.DISABLED) 

    def _end_task(self):
        sel = self.task_tree.selection()
        if not sel: return
        vals = self.task_tree.item(sel[0])['values']
        pid, name, safety = int(vals[0]), self.task_tree.item(sel[0])['text'], vals[5]
        if 'Critical' in safety:
            messagebox.showwarning("Warning", f"Cannot terminate critical system process: {name}")
            return
        if messagebox.askyesno("Confirm", f"Terminate {name} (PID: {pid})?"):
            try:
                psutil.Process(pid).terminate()
                self.status_label.config(text=f"Terminated {name}")
            except Exception as e: messagebox.showerror("Error", str(e))

    # ==================== UI HELPERS & SETTINGS ====================
    def _open_settings(self):
        top = tk.Toplevel(self.root)
        top.title("⚙️ Settings & Appearance")
        top.geometry("500x500")
        top.resizable(False, False)
        
        frame = ttk.Frame(top, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Theme Selection
        ttk.Label(frame, text="Theme:", font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        theme_var = tk.StringVar(value=self.config.get("theme", "Modern Dark"))
        theme_combo = ttk.Combobox(frame, textvariable=theme_var, values=list(THEMES.keys()), 
                                    width=40, state="readonly", font=self.default_font)
        theme_combo.pack(anchor=tk.W, pady=5, fill=tk.X)
        
        # Theme Preview
        preview_frame = ttk.LabelFrame(frame, text="Theme Preview", padding=10)
        preview_frame.pack(fill=tk.X, pady=10)
        
        def update_preview(*args):
            theme = THEMES.get(theme_var.get(), THEMES["Modern Dark"])
            preview_label.config(
                text="Sample Text",
                foreground=theme["fg_primary"],
                background=theme["bg_secondary"]
            )
            preview_frame.configure(style='Secondary.TFrame')
        
        preview_label = ttk.Label(preview_frame, text="Sample Text", font=('Segoe UI', 12, 'bold'),
                                   background=self.bg_secondary, foreground=self.fg_primary)
        preview_label.pack(pady=15)
        theme_var.trace_add('write', update_preview)
        
        # Font Size
        ttk.Label(frame, text="Font Size:", font=self.default_font).pack(anchor=tk.W, pady=(15, 5))
        font_spin = ttk.Spinbox(frame, from_=8, to=16, width=5, font=self.default_font)
        font_spin.set(self.font_size)
        font_spin.pack(anchor=tk.W, pady=5)
        
        # Apply Button
        def apply_settings():
            theme_name = theme_var.get()
            if theme_name in THEMES:
                self.config.set("theme", theme_name)
                self.classifier.current_theme = THEMES[theme_name]
                
            try:
                font_size = int(font_spin.get())
                if 8 <= font_size <= 16:
                    self.config.set("font_size", font_size)
                    self.font_size = font_size
            except ValueError:
                pass
            
            self._setup_theme()
            self.classifier.cache.clear()
            self._start_scan()
            top.destroy()
        
        ttk.Button(frame, text="💾 Apply & Close", command=apply_settings).pack(pady=20)

    def _show_disclaimer(self):
        msg = "⚠️ SAFETY DISCLAIMER\nThis tool provides deep system access.\nCRITICAL files/processes are protected.\nUse at your own risk. Backup important data.\nProceed?"
        if not messagebox.askyesno("Safety Warning", msg): sys.exit(0)

    def _save_config(self):
        self.config.set("scan_mode", self.scan_mode.get())
        self.config.set("skip_system_dirs", self.skip_system.get())
        self.config.set("task_refresh_interval", self.refresh_interval_var.get())

    def _process_queues(self):
        self._process_scanner_queue()
        self._process_task_queue()
        self.root.after(100, self._process_queues)

    def _process_scanner_queue(self):
        try:
            while True:
                msg_type, data = self.scanner_queue.get_nowait()
                if msg_type == 'started': self.status_label.config(text="Scanning...")
                elif msg_type == 'batch':
                    for fi in data:
                        self.all_files.append(fi)
                        self._add_file_to_tree(fi)
                elif msg_type == 'completed':
                    self.stats = data['stats']
                    self.scan_button.config(state=tk.NORMAL)
                    self.cancel_scan_button.config(state=tk.DISABLED)
                    self.status_label.config(text=f"📊 Total: {data['total']} | 🟢 {self.stats['SAFE']} | 🔴 {self.stats['CRITICAL']} | 🟡 {self.stats['SYSTEM_REMOVABLE']}")
                    self.config.add_recent_path(self.path_var.get())
                elif msg_type == 'error': messagebox.showerror("Error", data)
        except queue.Empty: pass

    def _process_task_queue(self):
        try:
            while True:
                msg_type, data = self.task_queue.get_nowait()
                if msg_type == 'processes':
                    self._update_task_list(data)
                    self.task_last_update.config(text=f"Last: {datetime.now().strftime('%H:%M:%S')}")
                    self.task_monitor_thread.set_paused(False)
        except queue.Empty: pass

    def _start_task_monitor(self):
        self.task_monitor_thread = TaskMonitor(self.task_queue, self.config)
        self.task_monitor_thread.start()

    def _toggle_auto_refresh(self): self.task_monitor_thread.set_paused(not self.auto_refresh.get())
    def _force_task_refresh(self):
        self.task_monitor_thread.set_paused(True)
        self.root.after(3000, lambda: self.task_monitor_thread.set_paused(not self.auto_refresh.get()))

    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.path_var.get())
        if folder: self.path_var.set(folder); self._start_scan()
    def _scan_quick(self, rel):
        p = os.path.expanduser(rel)
        if os.path.exists(p): self.path_var.set(p); self._start_scan()
    def _scan_all_drives(self):
        drives = [f"{d}:\\" for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")] if platform.system()=="Windows" else ['/']
        if drives:
            choice = simpledialog.askstring("Drive", "\n".join(f"{i+1}. {d}" for i,d in enumerate(drives)))
            if choice and choice.isdigit():
                idx = int(choice)-1
                if 0<=idx<len(drives): self.path_var.set(drives[idx]); self._start_scan()
    def _go_up(self):
        p = os.path.dirname(self.path_var.get())
        if os.path.exists(p): self.path_var.set(p); self._start_scan()
    def _open_folder_context(self):
        sel = self.scanner_tree.selection()
        if sel and os.path.isdir(sel[0]):
            if platform.system()=="Windows": os.startfile(sel[0])
            elif platform.system()=="Darwin": os.system(f"open '{sel[0]}'")
            else: os.system(f"xdg-open '{sel[0]}'")
    def _copy_path_context(self):
        sel = self.scanner_tree.selection()
        if sel: self.root.clipboard_clear(); self.root.clipboard_append(sel[0])
    def _delete_selected_context(self):
        sel = self.scanner_tree.selection()
        if not sel: return
        deleted = self.clipboard.delete_selected(sel)
        self.status_label.config(text=f"Deleted {deleted} items")
        self._start_scan()
    def _show_properties(self):
        sel = self.scanner_tree.selection()
        if sel:
            fi = self.classifier.cache.get(sel[0])
            if fi:
                messagebox.showinfo("Properties", f"Path: {fi.path}\nSize: {self._format_size(fi.size)}\nType: {fi.file_type_name}\nSafety: {fi.safety_classification.value}")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024: return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def _get_app_memory(self): return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    def _update_memory_label(self):
        self.memory_label.config(text=f"Mem: {self._get_app_memory():.1f} MB")
        self.root.after(2000, self._update_memory_label)

    def _on_close(self):
        try:
            # Stop all threads gracefully
            if self.scanner_thread and self.scanner_thread.is_alive():
                self._stop_event = threading.Event()
                self._stop_event.set()
                self.scanner_thread.join(timeout=2)
            
            if self.task_monitor_thread and self.task_monitor_thread.is_alive():
                self.task_monitor_thread.stop()
                self.task_monitor_thread.join(timeout=2)
            
            # Clear cache
            self.classifier.cache.clear()
            
            # Save config
            self.config.set("window_geometry", self.root.geometry())
            self.config.save()
        except Exception as e:
            print(f"Cleanup error: {e}")
        finally:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectExplorerPro(root)
    root.mainloop()