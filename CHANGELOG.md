# 📝 CHANGELOG

## v1.1 Security Hardened (2025-05-08)

### 🔐 Security Fixes (12 Total)

#### Critical
- **Fixed**: NameError in TaskMonitor - undefined `username` variable
- **Fixed**: Unsafe `os.system()` calls - now using `subprocess.run()` with list-based args

#### High Priority
- **Fixed**: Race condition in multi-threaded file access
- **Fixed**: Path traversal vulnerability in paste operations
- **Added**: Path normalization to prevent escaping restricted directories

#### Medium Priority
- **Fixed**: ReDoS vulnerability in regex search
- **Fixed**: Font size validation (8-16pt range)
- **Fixed**: Color format validation (hex color check)
- **Fixed**: Filename validation to prevent dangerous characters
- **Added**: Search result limiting (1000 max display)

#### Low Priority
- **Improved**: Exception handling specificity
- **Fixed**: Resource cleanup on application exit
- **Added**: LRU cache minimum size enforcement

###  User Experience Enhancements
- Better error messages with specific feedback
- Confirmation dialogs for dangerous operations
- Visual indicators for safety classification (🟢🟡🔴)
- Improved status messages with emoji indicators
- Thread-safe clipboard operations
---

**Version History**:
- v1.0: Initial release with security hardening
- v1.1 Security Hardened: All 12 vulnerabilities fixed

---

## v1.2 THEMES apdate
## What's new?

### ✅ Added a full theme system with 6 beautiful styles:

1. **Modern Dark** - Modern dark style (default)
2. **Deep Indigo** - Elegant purple style
3. **Cyber ​​Neon** - Bright neon style
4. **Soft Warm** - Comfortable warm style
5. **Ocean Blue** - Fresh nautical style
6. **White** - Classic light style

##  Key Features:

✨ **Adaptive File Colors**
- Each theme has a unique set of colors for 24+ file types
- Colors are perfectly matched to each theme
- All colors are readable and distinguishable

🎨 **Unified Consistency**
- Primary theme colors are aligned with file colors
- The palette is chosen based on UX design principles
- Professional appearance

⚡ **Quick Switching**
- Theme Switching Instantly clears cache when changing themes
- Saves selection across program restarts

🔍 **Full functionality**
- All file types are supported
- System folders are highlighted separately
- Built-in theme preview in settings

## 📋 How to use

### Changing themes:
1. Open **File** → **Open Settings**
2. Select a theme from the **Theme** drop-down list
3. The preview will update automatically
4. Click **Apply & Close**

### Adjusting the font size:
- In the same Settings window, use the **Font Size** field
- The size will be saved when you close the program

## 📊 Theme statistics

Each theme contains:
- 7 primary colors (background, text, accents)
- 27 specialized colors for files:
- 24 file extensions (PDF, DOC, XLS, PNG, MP4, PY, JS, HTML, ZIP, EXE, etc.)
- 3 special colors (regular folder, system folder, unknown type)
