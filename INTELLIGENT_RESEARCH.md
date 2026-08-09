# Intelligent Framework Research System

The AI Swarm can automatically detect, research, and learn about **ANY** framework - including YOLO, TensorFlow, Flutter, and more!

## How It Works

### 1. **Automatic Detection**
The system scans your project and detects:
- **AI/ML Frameworks**: YOLO, TensorFlow, PyTorch, Keras, scikit-learn
- **Computer Vision**: OpenCV, Ultralytics, PIL
- **Deep Learning**: Transformers, Hugging Face models
- **Web Frameworks**: FastAPI, Flask, Django, React, Vue, Next.js
- **Mobile**: Flutter, React Native, Android, iOS
- **Data Science**: Pandas, NumPy, Matplotlib
- **ANY other library** in your requirements/package files

### 2. **Intelligent Research**
When unknown frameworks are found:
- Automatically searches documentation online
- Uses the Research Agent + Web Tool
- Queries the LLM to understand the framework
- Stores findings in memory for future use

### 3. **Adaptive Learning**
The system learns and remembers:
- What each framework does
- Current versions and best practices
- Common patterns and usage
- Compatibility issues

## Usage

### Quick Check
```bash
python main.py
swarm> check-project
```

**Output:**
```
Project Type: AI/ML Application
Languages: Python
Libraries: 23 detected
  • ultralytics (YOLO)
  • torch (PyTorch)
  • opencv-python
  • numpy
  • pandas
  ...

⚠ Found 3 outdated packages
```

### Intelligent Research
```bash
swarm> research-frameworks
```

**What happens:**
1. Scans all libraries
2. Identifies important/unknown ones
3. Automatically researches each
4. Stores findings in memory
5. Provides recommendations

**Example Output:**
```
Intelligent Framework Research System
======================================================================

Step 1: Analyzing Project
✓ Project Type: Computer Vision Application
✓ Languages: Python
✓ Detected 23 libraries
✓ Detected 0 frameworks

Step 2: Identifying Key Frameworks
Found 5 important frameworks:
  • ultralytics
  • torch
  • opencv-python
  • torchvision
  • pillow

Step 3: Researching Frameworks (AI-Powered)
Researching 1/5: ultralytics...
Researching 2/5: torch...
Researching 3/5: opencv-python...

Framework Research Results
──────────────────────────────────────────────
Framework         Type/Purpose                 Status
──────────────────────────────────────────────
ultralytics       YOLO object detection...     ✓ Researched
torch             PyTorch deep learning...     ✓ Researched
opencv-python     Computer vision library...   ✓ Researched
torchvision       Vision models for PyTorch... ✓ Researched
pillow            Image processing...          ✓ Researched

✓ Stored research in memory for future reference

Step 4: Recommendations

AI/ML Project Detected!
Frameworks: ultralytics, torch, torchvision

Recommendations:
  1. Ensure CUDA/GPU drivers are up to date (if using GPU)
  2. Check model compatibility with framework versions
  3. Monitor model versions and datasets
  4. Use virtual environments to avoid conflicts
```

## Supported Project Types

The system intelligently recognizes:

### AI/ML Projects
- **YOLO** (any version: YOLOv5, YOLOv8, Ultralytics)
- **TensorFlow** / TensorFlow Lite
- **PyTorch** / torchvision
- **Keras**
- **scikit-learn**
- **XGBoost**, **LightGBM**
- **Hugging Face Transformers**
- **ONNX Runtime**

### Computer Vision
- **OpenCV** (cv2, opencv-python)
- **PIL** / Pillow
- **ImageIO**
- **Albumentations**
- **mmdetection**, **detectron2**

### Web Development
- **Python**: FastAPI, Flask, Django, Pyramid
- **JavaScript**: React, Vue, Angular, Next.js, Svelte
- **Node.js**: Express, Koa, Fastify, NestJS

### Mobile Development
- **Flutter** (Dart)
- **React Native**
- **Android** (Kotlin/Java with Gradle)
- **iOS** (Swift with CocoaPods/SwiftPM)

### Data Science
- **Pandas**, **NumPy**
- **Matplotlib**, **Seaborn**, **Plotly**
- **Jupyter**, **IPython**
- **Dask**, **Vaex**

### Backend
- **Databases**: SQLAlchemy, Django ORM, Prisma
- **APIs**: GraphQL, REST frameworks
- **Message Queues**: Celery, RabbitMQ, Redis

## Advanced Features

### 1. Auto-Research Any Library

```python
# Programmatic usage
from tools import get_tool_manager
from agents import ResearchAgent
from core import get_llm_client

tool_manager = get_tool_manager()
research_agent = ResearchAgent()
research_agent.set_llm_client(get_llm_client())
research_agent.set_web_tool(tool_manager.get_tool("web"))

# Research any framework
result = research_agent.process({
    "type": "research_topic",
    "topic": "What is Ultralytics YOLO and how do I use it?",
    "context": "Python computer vision project"
})

print(result['findings'])
```

### 2. Version Checking

```bash
swarm> check-project
```

Automatically checks:
- Current installed versions
- Latest available versions
- Update recommendations
- Breaking change warnings

### 3. Documentation Fetching

The system can fetch docs from:
- Official framework websites
- PyPI package pages
- npm registry
- GitHub repositories
- Documentation sites

### 4. Memory Storage

All research is stored for future use:
```python
from memory import get_memory_manager

memory = get_memory_manager()

# Retrieve past research
results = memory.search_knowledge(
    query="YOLO object detection",
    category="frameworks"
)
```

## Workflow Examples

### Example 1: New YOLO Project

```bash
# 1. Check what's in the project
swarm> check-project

# Output: Detects YOLO, OpenCV, PyTorch

# 2. Research frameworks
swarm> research-frameworks

# System automatically:
# - Researches YOLO documentation
# - Checks PyTorch compatibility
# - Verifies OpenCV version
# - Stores findings

# 3. Get specific help
swarm> goal How do I use YOLOv8 for custom object detection?

# Research agent uses stored knowledge +
# fetches latest YOLO docs to answer
```

### Example 2: Update Dependencies

```bash
# 1. Check current state
swarm> check-project

# Shows: ultralytics 8.0.100 (current), 8.0.200 (latest)

# 2. Research changes
swarm> goal What's new in Ultralytics 8.0.200?

# Research agent:
# - Fetches changelog
# - Highlights breaking changes
# - Provides update recommendation

# 3. Update if safe
pip install --upgrade ultralytics
```

### Example 3: Multi-Framework Project

```bash
swarm> research-frameworks

# Detects and researches:
# - FastAPI (web framework)
# - YOLO (computer vision)
# - PostgreSQL (database)
# - Redis (caching)

# Provides integrated recommendations:
# - API design patterns
# - Async compatibility
# - Performance optimization
# - Deployment strategy
```

## Configuration

### Enable Web Research
```bash
# In .env
ENABLE_WEB_RESEARCH=true
```

### Configure Research Depth
```python
# Modify agents/research.py
# Adjust temperature for more/less creative research
research_agent.query_llm(prompt, temperature=0.7)
```

## Extending the System

### Add Custom Framework Detection

Edit `tools/project_analyzer.py`:
```python
def _detect_project_type(self, analysis: Dict) -> str:
    # Add your custom detection
    if 'my_framework' in libraries:
        return "My Custom Framework"
```

### Add Custom Research Sources

Edit `tools/web_tool.py`:
```python
doc_urls = {
    "my_framework": "https://my-framework-docs.com",
}
```

## Benefits

✅ **Never Hardcoded**: Adapts to ANY framework
✅ **Automatically Updated**: Fetches current documentation
✅ **Learns Over Time**: Stores knowledge for reuse
✅ **Context-Aware**: Understands your specific project
✅ **Multi-Language**: Python, JavaScript, Dart, Swift, etc.
✅ **Offline Capable**: Uses LLM knowledge when web unavailable

## Comparison

### Traditional Approach
```
1. Manually check requirements.txt
2. Google each unknown library
3. Read documentation
4. Check versions manually
5. Repeat for each project
```

### AI Swarm Approach
```
1. swarm> research-frameworks
2. ☕ (system does everything automatically)
3. Review intelligent summary
4. Done!
```

## Real-World Examples

### YOLO Object Detection Project
```
Detected: ultralytics, opencv-python, torch
Researched: Current YOLO best practices
Recommendation: Use YOLOv8 with latest ultralytics
Warning: torch 2.0+ required for optimal performance
```

### Flutter Mobile App
```
Detected: Flutter, Dart packages
Researched: Current Flutter version, widget libraries
Recommendation: Update to Flutter 3.x for better performance
Warning: Breaking changes in navigation APIs
```

### Full-Stack Web App
```
Detected: FastAPI, React, PostgreSQL
Researched: API design patterns, frontend state management
Recommendation: Use async endpoints, React Query for data
Compatibility: Verified FastAPI + Pydantic v2 support
```

## Summary

The AI Swarm provides an **intelligent, adaptive framework research system** that:

1. **Detects** any framework (YOLO, TensorFlow, Flutter, anything!)
2. **Researches** documentation automatically
3. **Learns** and stores knowledge
4. **Recommends** best practices
5. **Checks** for updates and compatibility

**No hardcoding required** - the system adapts to YOUR project! 🚀

---

**Quick Start:**
```bash
python main.py
swarm> research-frameworks
```

Let the AI learn about your frameworks automatically! 🤖✨
