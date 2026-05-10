# 🔍 Project Explorer PRO v1.0

> **Advanced Directory & Process Manager** | Windows • Linux • macOS

---

##  ENGLISH VERSION

###  Overview
**Project Explorer Pro V1** is a high-performance desktop application designed for advanced directory scanning, file management, and real-time system process monitoring. Built with Python and Tkinter, it delivers a professional, dark-themed interface with **enterprise-grade security** mechanisms to prevent accidental modification or deletion of critical system files.

###  Key Features
- **Multi-threaded Performance** - Recursive directory scanning optimized for speed
- **Explorer-Style Interface** - Familiar UI with detailed file metadata & sorting
- **Smart Color Coding** - Visual identification of file types at a glance
- **Triple-Layer Safety** - SAFE | CRITICAL | SYSTEM-REMOVABLE classification
- **Live Process Monitor** - Real-time CPU, memory & status tracking
- **Secure Operations** - Mandatory confirmations for all destructive actions
- **Advanced Search** - Regex support with safety limits
- **Customizable Theme** - Professional dark theme with color customization
- **Batch Processing** - Handle multiple files/folders efficiently
### 💻 System Requirements
| Component | Requirement |
|-----------|-------------|
| **Python** | 3.7+ |
| **OS** | Windows, Linux, macOS |
| **Memory** | 512MB minimum |
| **Dependencies** | tkinter (bundled), psutil |

###  Installation

#### Option 1: Direct Installation
```bash
# Clone the repository
git clone https://github.com/Zheka-GGS/Project_Explorer_V.1.git
cd Project_Explorer_V.1

# Install dependencies
pip install psutil

# Run the application
python explorerV1.py
```

#### Option 2: Using Python Package
```bash
pip install -r requirements.txt
python explorerV1.py
```

###  Quick Start Guide

1. **Launch Application**
   - Run `explorerV1.py`
   - Accept the safety disclaimer

2. **Directory Scanning**
   - Enter path or click **Browse** → Select folder
   - Click **Scan** to analyze directory
   - Results appear in color-coded tree view

3. **File Management**
   - **Copy/Cut/Paste**: Ctrl+C/X/V or right-click context menu
   - **Rename**: F2 or context menu
   - **Delete**: Del or context menu (with safety check)
   - **Drag & Drop**: Move files between directories

4. **Process Management**
   - Switch to **Task Manager** tab
   - View CPU, memory, and process status
   - Select process → **End Task** (with safety lock for critical processes)

###  Security & Safety Features

#### Triple-Layer Protection System
```
┌─────────────────────────────────────┐
│     SAFE FILES                      │
│   • Cache files (.tmp, .bak)        │
│   • Temporary downloads             │
│   • Non-critical directories        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    SYSTEM-REMOVABLE                 │
│   • Windows.old, Prefetch           │
│   • Installation cache              │
│   • Requires manual approval        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    CRITICAL (LOCKED)                │
│   • System32, Windows               │
│   • Running processes               │
│   • System drivers (.dll, .sys)     │
└─────────────────────────────────────┘
```

#### Built-in Safeguards
✅ Critical system directories are **automatically locked**  
✅ Active process paths are **cross-referenced** to prevent file-in-use deletions  
✅ **Double-confirmation** dialogs for destructive operations  
✅ **Zero automatic deletions** - All changes are user-initiated  
✅ ReDoS attack prevention via search limits (100 char max)  
✅ Path validation to prevent traversal attacks  
✅ Thread-safe operations with proper synchronization  
✅ Comprehensive exception handling

###  Advanced Features

#### Search Capabilities
-  **Simple Search**: Plain text matching
-  **Regex Search**: Advanced pattern matching (with safety limits)
-  **Filter Options**: Hidden files, case sensitivity
-  **Live Results**: Updates as you type

#### Process Management
-  Displays: PID, CPU%, Memory, Status, User
-  Safety Classification: Critical/High Resource/Safe
-  Protected: Critical system processes cannot be terminated
-  Auto-refresh: Configurable refresh intervals (1-30s)

#### Customization
-  Theme Colors: Primary, Secondary, Tertiary, Accent
-  Font Size: Adjustable (8-16pt)
-  Persistent Settings: Auto-saved in user home directory

There is also an exe file with which you don't need to install the program and you can just run it right away.

License
MIT License. Free for personal, educational, and commercial use. Refer to the included LICENSE file for full terms.

---

##  РУССКАЯ ВЕРСИЯ

###  Обзор
**Project Explorer Pro V1** — это высокопроизводительное десктопное приложение для расширенного сканирования директорий, управления файлами и мониторинга системных процессов. Разработано на Python с Tkinter. Предоставляет профессиональный интерфейс с **корпоративным уровнем безопасности** для защиты критических файлов системы.

### ✨ Ключевые Возможности
-  **Многопоточность** - Быстрое сканирование директорий рекурсивно
-  **Интерфейс Проводника** - Знакомый UI с метаданными файлов
-  **Цветовое Кодирование** - Быстрая визуальная идентификация
-  **Тройная Защита** - БЕЗОПАСНЫЕ | КРИТИЧЕСКИЕ | СИСТЕМНО-УДАЛЯЕМЫЕ
-  **Монитор Процессов** - ЦП, память, статус в реальном времени
-  **Безопасные Операции** - Подтверждение для всех деструктивных действий
-  **Продвинутый Поиск** - Regex с защитой от ReDoS
-  **Кастомизация** - Тема с цветовой настройкой
-  **Пакетная Обработка** - Работа с множественными файлами

### Системные Требования
| Компонент | Требование |
|-----------|-----------|
| **Python** | 3.7+ |
| **ОС** | Windows, Linux, macOS |
| **Память** | 512MB минимум |
| **Зависимости** | tkinter (встроен), psutil |

###  Установка

#### Вариант 1: Прямая установка
```bash
# Клонируем репозиторий
git clone https://github.com/Zheka-GGS/Project_Explorer_V.1.git
cd Project_Explorer_V.1

# Устанавливаем зависимости
pip install psutil

# Запускаем приложение
python explorerV1.py
```

#### Вариант 2: Через requirements.txt
```bash
pip install -r requirements.txt
python explorerV1.py
```

###  Краткое Руководство

1. **Запуск**
   - Запустите `explorerV1.py`
   - Подтвердите предупреждение о безопасности

2. **Сканирование Директорий**
   - Введите путь или нажмите **Обзор** → Выберите папку
   - Нажмите **Сканировать** для анализа
   - Результаты отобразятся в дереве файлов

3. **Управление Файлами**
   - **Копировать/Вырезать/Вставить**: Ctrl+C/X/V или контекстное меню
   - **Переименовать**: F2 или контекстное меню
   - **Удалить**: Del или контекстное меню (с проверкой безопасности)
   - **Перетаскивание**: Переместить файлы между директориями

4. **Управление Процессами**
   - Перейдите на вкладку **Диспетчер Задач**
   - Просмотрите ЦП, память и статус процесса
   - Выберите процесс → **Завершить Задачу** (с блокировкой для критичных)

###  Функции Безопасности

#### Система Тройной Защиты
```
┌─────────────────────────────────────┐
│    БЕЗОПАСНЫЕ ФАЙЛЫ                 │
│   • Кеш файлы (.tmp, .bak)          │
│   • Временные загрузки              │
│   • Некритичные директории          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│     СИСТЕМНО-УДАЛЯЕМЫЕ              │
│   • Windows.old, Prefetch           │
│   • Кеш установки                   │
│   • Требуют ручного подтверждения   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│     КРИТИЧЕСКИЕ (ЗАБЛОКИРОВАНЫ)     │
│   • System32, Windows               │
│   • Активные процессы               │
│   • Системные драйверы (.dll, .sys) │
└─────────────────────────────────────┘
```

#### Встроенные Защиты
✅ Критические системные директории **автоматически заблокированы**  
✅ Пути активных процессов **проверяются** во избежание удаления  
✅ **Двойное подтверждение** для опасных операций  
✅ **Нет автоматических удалений** - Все действия инициирует пользователь  
✅ Защита от ReDoS через ограничение поиска (макс. 100 символов)  
✅ Валидация путей против атак обхода  
✅ Потокобезопасные операции с синхронизацией  
✅ Полная обработка исключений

###  Продвинутые Возможности

#### Поиск
-  **Простой Поиск**: Обычное сопоставление текста
-  **Regex Поиск**: Продвинутые шаблоны (с защитой)
-  **Фильтры**: Скрытые файлы, чувствительность к регистру
-  **Живые Результаты**: Обновление при вводе

#### Управление Процессами
-  Отображает: PID, ЦП%, Память, Статус, Пользователь
-  Классификация: Критичный/Большая нагрузка/Безопасный
-  Защита: Критичные процессы нельзя завершить
-  Авто-обновление: Интервалы 1-30 сек

#### Кастомизация
-  Цвета: Основной, Вторичный, Третичный, Акцент
-  Размер Шрифта: Настраивается (8-16пт)
-  Сохранение: Автосохранение в домашней директории

Также есть exe файл, с помощью которого вам не нужно устанавливать приложение и вы можете просто запустить его сразу.


License
MIT License. Свободное использование в личных, образовательных и коммерческих целях. Полные условия см. в файле LICENSE.
