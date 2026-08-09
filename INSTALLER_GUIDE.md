# 🤖 AI-Powered Framework Installation System

## Overview

The AI Swarm includes an **InstallerAgent** that can suggest, research, and install frameworks automatically - adapting to ANY project requirement!

## 🎯 Complete Workflow

```
User Need → AI Suggests → Research Docs → Check Installed → Install → Verify
```

### What It Does

1. **Intelligent Suggestion** - AI analyzes your requirements and suggests the best framework
2. **Automatic Research** - Fetches and understands documentation
3. **Installation Check** - Verifies if already installed
4. **Safe Installation** - Asks for confirmation before installing
5. **Knowledge Storage** - Remembers everything for future use

## 🚀 Quick Start

### Scenario 1: Need a Framework

```bash
python main.py

# Ask AI for suggestions
swarm> suggest object detection for Python

# Output:
AI Recommendation
─────────────────────────────────────────
Framework     ultralytics
Reason        YOLO is the industry standard...
Difficulty    easy
Install       pip install ultralytics
Alternatives  tensorflow, pytorch, opencv

To install: swarm> install ultralytics
```

### Scenario 2: Install a Framework

```bash
swarm> install ultralytics

# System automatically:
# 1. Researches ultralytics
# 2. Shows key information
# 3. Checks if installed
# 4. Asks for confirmation
# 5. Installs it
# 6. Verifies success

Framework Installation: ultralytics

Step 1: Research & Check
✓ Research complete
╭─ Key Information ─────────────────────╮
│ Ultralytics is a computer vision      │
│ framework providing state-of-the-art  │
│ YOLO object detection models...       │
╰────────────────────────────────────────╯

• ultralytics is not installed

Step 2: Installation
Command: pip install ultralytics

Install ultralytics? (yes/no): yes

Installing ultralytics...

✓ Successfully installed ultralytics!
You can now use ultralytics in your project
```

### Scenario 3: Auto-Research Existing Project

```bash
swarm> research-frameworks

# Scans your project
# Detects: ultralytics, torch, opencv-python
# Researches each automatically
# Stores findings in memory
# Provides recommendations
```

## 📋 Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `suggest <purpose>` | AI suggests best framework | `suggest web scraping` |
| `install <framework>` | Research and install | `install fastapi` |
| `research-frameworks` | Auto-research all detected | `research-frameworks` |
| `check-project` | Analyze current project | `check-project` |

## 🎭 Real-World Examples

### Example 1: Computer Vision Project

```bash
swarm> suggest object detection with pre-trained models

# AI Response:
Recommended: ultralytics

Why: YOLOv8 provides excellent accuracy and speed, 
pre-trained models for 80 classes, easy to use API, 
active community, and regular updates.

Alternatives: tensorflow, pytorch, opencv
Install: pip install ultralytics
Difficulty: easy
Docs: https://docs.ultralytics.com

To install: swarm> install ultralytics

# Then install
swarm> install ultralytics

# Researches, confirms, installs, done!
✓ Successfully installed ultralytics!
```

### Example 2: Web Development

```bash
swarm> suggest REST API framework for Python

# AI suggests: fastapi
# Reason: Modern, fast, automatic docs, type hints

swarm> install fastapi

# System installs fastapi + dependencies
```

### Example 3: Unknown Framework Detection

```bash
# Your project has requirements.txt with:
# - ultralytics
# - torch
# - albumentations

swarm> research-frameworks

Intelligent Framework Research System
══════════════════════════════════════

Step 1: Analyzing Project
✓ Project Type: Computer Vision Application
✓ Languages: Python
✓ Detected 15 libraries

Step 2: Identifying Key Frameworks
Found 3 important frameworks:
  • ultralytics
  • torch
  • albumentations

Step 3: Researching Frameworks (AI-Powered)
Researching 1/3: ultralytics...
Researching 2/3: torch...
Researching 3/3: albumentations...

Framework Research Results
──────────────────────────────────────
Framework      Type/Purpose              Status
──────────────────────────────────────
ultralytics    YOLO object detection     ✓ Researched
torch          PyTorch deep learning     ✓ Researched
albumentations Image augmentation        ✓ Researched

✓ Stored research in memory

Step 4: Recommendations
AI/ML Project Detected!
Frameworks: ultralytics, torch, albumentations

Recommendations:
  1. Ensure CUDA/GPU drivers up to date
  2. Check model compatibility
  3. Use virtual environments
  4. Monitor versions
```

## 🧠 How It Works

### 1. Suggestion Engine

```python
# Behind the scenes
installer_agent.process({
    "type": "suggest_framework",
    "purpose": "object detection",
    "language": "python"
})

# AI considers:
# - Popularity and community
# - Ease of use
# - Performance
# - Maintenance
# - Compatibility
```

### 2. Research System

```python
# Automatically researches:
research_agent.process({
    "type": "research_topic",
    "topic": "ultralytics - features and usage"
})

# Fetches from:
# - Official docs
# - PyPI/npm
# - GitHub
# - Web search
```

### 3. Installation Manager

```python
# Safe installation workflow:
1. Check if already installed
2. Get installation command
3. Ask user confirmation
4. Execute installation
5. Verify success
6. Store knowledge
```

## 🎨 Supported Ecosystems

### Python
- **Package Files**: requirements.txt, Pipfile, pyproject.toml
- **Manager**: pip, pipenv, poetry
- **Examples**: ultralytics, tensorflow, fastapi, django

### JavaScript/Node.js
- **Package Files**: package.json
- **Manager**: npm, yarn, pnpm
- **Examples**: react, express, next.js

### Flutter/Dart
- **Package Files**: pubspec.yaml
- **Manager**: flutter pub
- **Examples**: flutter packages

### Others
- **Ruby**: Gemfile (gem)
- **Go**: go.mod (go get)
- **Rust**: Cargo.toml (cargo)
- **PHP**: composer.json (composer)

## 🔒 Safety Features

### 1. Confirmation Required
```python
# ALWAYS asks before installing
Install ultralytics? (yes/no): _
```

### 2. Research First
```python
# Shows what will be installed
✓ Research complete
Framework: ultralytics
Purpose: Object detection
Version: 8.x.x
Dependencies: torch, numpy, opencv-python
```

### 3. Verification
```python
# Verifies installation succeeded
✓ Successfully installed ultralytics!
# Checks: pip show ultralytics
```

## 📚 Integration with Memory

All research is stored automatically:

```python
# Stored in ChromaDB + SQLite
memory.store_knowledge(
    category="frameworks",
    title="Ultralytics YOLO Overview",
    content="...",
    tags=["yolo", "object-detection"],
    source="installer_workflow"
)

# Retrieved later
results = memory.search_knowledge(
    query="YOLO usage",
    category="frameworks"
)
```

## 🎯 Use Cases

### 1. Starting New Project
```bash
swarm> suggest web scraping framework
swarm> install beautifulsoup4
swarm> goal Write web scraper for news sites
```

### 2. Adding Features
```bash
swarm> suggest adding authentication to FastAPI
swarm> install python-jose
swarm> goal Implement JWT authentication
```

### 3. Updating Dependencies
```bash
swarm> check-project
# Shows outdated packages
swarm> install ultralytics  # Gets latest version
```

### 4. Exploring Alternatives
```bash
swarm> suggest alternatives to TensorFlow
# AI: Consider PyTorch, JAX, or ONNX Runtime
swarm> research-frameworks  # Compare them
```

## 🔧 Advanced Usage

### Programmatic Access

```python
from agents import InstallerAgent
from core import get_llm_client

installer = InstallerAgent()
installer.set_llm_client(get_llm_client())

# Get suggestion
result = installer.process({
    "type": "suggest_framework",
    "purpose": "real-time object detection",
    "language": "python",
    "context": "Need to process video at 30fps"
})

framework = result['suggestion']['framework']

# Research and install
installer.process({
    "type": "research_and_install",
    "framework": framework,
    "auto_install": False  # Requires confirmation
})
```

### Custom Research

```python
from agents import ResearchAgent

research = ResearchAgent()
research.set_llm_client(get_llm_client())

# Deep dive into specific framework
result = research.process({
    "type": "research_topic",
    "topic": "YOLOv8 custom model training",
    "context": "Need to detect custom objects"
})

print(result['findings'])
```

## 🚦 Workflow Visualization

```
┌─────────────────┐
│  User Request   │
│ "Need object    │
│  detection"     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ InstallerAgent  │
│ Suggests: YOLO  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ ResearchAgent   │
│ Fetches docs    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Check Installed │
│ Not found       │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Ask User        │
│ Confirmation    │
└────────┬────────┘
         │ yes
         v
┌─────────────────┐
│ TerminalTool    │
│ pip install     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Verify Success  │
│ Store Knowledge │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Ready to Code!  │
└─────────────────┘
```

## 📊 Benefits

| Feature | Benefit |
|---------|---------|
| **AI-Powered** | Intelligent suggestions based on requirements |
| **Adaptive** | Works with ANY framework, not hardcoded |
| **Safe** | Always asks confirmation before installing |
| **Knowledge Storage** | Remembers research for future use |
| **Up-to-Date** | Fetches current documentation |
| **Time-Saving** | Automates the entire workflow |
| **Educational** | Learn about frameworks as you use them |

## 🎓 Learning Feature

The system learns and improves:

```python
# First time:
swarm> install ultralytics
# Researches online, takes time

# Later:
swarm> goal How do I use YOLO?
# Uses stored knowledge, instant response

# Memory contains:
# - Framework overview
# - Installation notes
# - Usage patterns
# - Common issues
# - Best practices
```

## 🌟 Summary

The AI Swarm's installation system is:

- ✅ **Intelligent** - AI suggests best options
- ✅ **Adaptive** - Works with any framework
- ✅ **Safe** - Requires confirmation
- ✅ **Educational** - Explains what it's doing
- ✅ **Efficient** - Automates research & installation
- ✅ **Memory-Backed** - Learns and remembers

**Try it now:**
```bash
python main.py
swarm> suggest your-need-here
swarm> install suggested-framework
```

🚀 **Let the AI handle framework management!** 🤖
