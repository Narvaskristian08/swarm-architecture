"""
Project Analyzer Tool
Detects frameworks, libraries, and technologies used in a project.
"""
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import logging

from .base_tool import BaseTool

logger = logging.getLogger(__name__)


class ProjectAnalyzerTool(BaseTool):
    """
    Analyzes a project to detect frameworks and libraries.
    Checks package files, imports, and configuration files.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        super().__init__(
            tool_id="project_analyzer",
            name="Project Analyzer",
            description="Detects frameworks and libraries used in a project"
        )
        self.project_root = project_root or Path.cwd()
    
    def execute(self, operation: str = "analyze", **kwargs) -> Dict[str, Any]:
        """Execute project analysis"""
        if operation == "analyze":
            return self._analyze_project(**kwargs)
        elif operation == "check_file":
            return self._check_package_file(kwargs.get("file_path"))
        elif operation == "scan_imports":
            return self._scan_imports(**kwargs)
        elif operation == "check_versions":
            return self._check_versions(**kwargs)
        elif operation == "check_outdated":
            return self._check_outdated(**kwargs)
        else:
            return {
                "status": "error",
                "error": f"Unknown operation: {operation}"
            }
    
    def validate_params(self, operation: str = "analyze", **kwargs) -> tuple[bool, Optional[str]]:
        """Validate parameters"""
        return True, None
    
    def _analyze_project(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive project analysis"""
        project_path = Path(path) if path else self.project_root
        
        if not project_path.exists():
            return {
                "status": "error",
                "error": f"Project path not found: {project_path}"
            }
        
        analysis = {
            "status": "success",
            "project_path": str(project_path),
            "languages": set(),
            "frameworks": set(),
            "libraries": set(),
            "tools": set(),
            "package_managers": set(),
            "config_files": [],
            "details": {}
        }
        
        # Check for various package/config files
        package_files = {
            "requirements.txt": self._parse_requirements,
            "Pipfile": self._parse_pipfile,
            "pyproject.toml": self._parse_pyproject,
            "package.json": self._parse_package_json,
            "composer.json": self._parse_composer_json,
            "Gemfile": self._parse_gemfile,
            "go.mod": self._parse_go_mod,
            "Cargo.toml": self._parse_cargo_toml,
            "pom.xml": self._parse_pom_xml,
            "pubspec.yaml": self._parse_pubspec,  # Flutter/Dart
            "build.gradle": self._parse_gradle,   # Android
            "Podfile": self._parse_podfile,       # iOS
            "Package.swift": self._parse_swift_package,  # Swift
        }
        
        for filename, parser in package_files.items():
            file_path = project_path / filename
            if file_path.exists():
                analysis["config_files"].append(filename)
                result = parser(file_path)
                
                # Merge results
                if result.get("language"):
                    analysis["languages"].add(result["language"])
                if result.get("frameworks"):
                    analysis["frameworks"].update(result["frameworks"])
                if result.get("libraries"):
                    analysis["libraries"].update(result["libraries"])
                if result.get("tools"):
                    analysis["tools"].update(result["tools"])
                if result.get("package_manager"):
                    analysis["package_managers"].add(result["package_manager"])
                
                analysis["details"][filename] = result
        
        # Scan source files for imports
        import_analysis = self._scan_all_imports(project_path)
        if import_analysis.get("libraries"):
            analysis["libraries"].update(import_analysis["libraries"])
        if import_analysis.get("frameworks"):
            analysis["frameworks"].update(import_analysis["frameworks"])
        
        # Convert sets to sorted lists for JSON serialization
        analysis["languages"] = sorted(analysis["languages"])
        analysis["frameworks"] = sorted(analysis["frameworks"])
        analysis["libraries"] = sorted(analysis["libraries"])
        analysis["tools"] = sorted(analysis["tools"])
        analysis["package_managers"] = sorted(analysis["package_managers"])
        
        # Detect project type
        analysis["project_type"] = self._detect_project_type(analysis)
        
        return analysis
    
    def _parse_requirements(self, file_path: Path) -> Dict[str, Any]:
        """Parse Python requirements.txt"""
        try:
            content = file_path.read_text()
            libraries = set()
            frameworks = set()
            
            # Known framework patterns
            known_frameworks = {
                'django', 'flask', 'fastapi', 'pyramid', 'tornado',
                'bottle', 'cherrypy', 'web2py', 'turbogears', 'falcon',
                'sanic', 'starlette', 'aiohttp', 'quart', 'responder'
            }
            
            # Framework indicators in names
            framework_indicators = ['framework', 'web', 'api', 'server', 'app']
            
            for line in content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Extract package name (before ==, >=, etc.)
                match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                if match:
                    package = match.group(1).lower()
                    libraries.add(package)
                    
                    # Identify frameworks
                    if package in known_frameworks:
                        frameworks.add(package)
                    # Check for framework-like names
                    elif any(indicator in package for indicator in framework_indicators):
                        frameworks.add(package)
            
            return {
                "language": "Python",
                "package_manager": "pip",
                "libraries": libraries,
                "frameworks": frameworks,
                "file": "requirements.txt"
            }
        except Exception as e:
            logger.error(f"Error parsing requirements.txt: {e}")
            return {}
    
    def _parse_pipfile(self, file_path: Path) -> Dict[str, Any]:
        """Parse Python Pipfile"""
        try:
            content = file_path.read_text()
            # Simple parsing (full TOML parser would be better)
            libraries = set()
            for line in content.split('\n'):
                if '=' in line and not line.strip().startswith('['):
                    package = line.split('=')[0].strip().strip('"')
                    libraries.add(package.lower())
            
            return {
                "language": "Python",
                "package_manager": "pipenv",
                "libraries": libraries,
                "file": "Pipfile"
            }
        except Exception as e:
            logger.error(f"Error parsing Pipfile: {e}")
            return {}
    
    def _parse_pyproject(self, file_path: Path) -> Dict[str, Any]:
        """Parse Python pyproject.toml"""
        try:
            content = file_path.read_text()
            libraries = set()
            
            # Look for dependencies section
            in_deps = False
            for line in content.split('\n'):
                if '[tool.poetry.dependencies]' in line or '[project.dependencies]' in line:
                    in_deps = True
                    continue
                if in_deps and line.strip().startswith('['):
                    in_deps = False
                if in_deps and '=' in line:
                    package = line.split('=')[0].strip().strip('"')
                    if package != 'python':
                        libraries.add(package.lower())
            
            return {
                "language": "Python",
                "package_manager": "poetry" if "poetry" in content else "pip",
                "libraries": libraries,
                "file": "pyproject.toml"
            }
        except Exception as e:
            logger.error(f"Error parsing pyproject.toml: {e}")
            return {}
    
    def _parse_package_json(self, file_path: Path) -> Dict[str, Any]:
        """Parse Node.js package.json"""
        try:
            data = json.loads(file_path.read_text())
            libraries = set()
            frameworks = set()
            
            # Known frameworks
            known_frameworks = {
                'react', 'vue', 'angular', 'svelte', 'next', 'nuxt', 'gatsby',
                'express', 'koa', 'fastify', 'nestjs', 'hapi', 'restify',
                'meteor', 'sails', 'adonis', 'loopback', 'feathers'
            }
            
            # Framework indicators
            framework_indicators = ['framework', 'web', 'api', 'server', 'app']
            
            # Get dependencies
            for dep_type in ['dependencies', 'devDependencies']:
                if dep_type in data:
                    for package in data[dep_type].keys():
                        package_lower = package.lower()
                        libraries.add(package_lower)
                        
                        # Identify frameworks
                        if package_lower in known_frameworks:
                            frameworks.add(package_lower)
                        # Check package name
                        elif any(indicator in package_lower for indicator in framework_indicators):
                            frameworks.add(package_lower)
            
            return {
                "language": "JavaScript/TypeScript",
                "package_manager": "npm",
                "libraries": libraries,
                "frameworks": frameworks,
                "file": "package.json"
            }
        except Exception as e:
            logger.error(f"Error parsing package.json: {e}")
            return {}
    
    def _parse_composer_json(self, file_path: Path) -> Dict[str, Any]:
        """Parse PHP composer.json"""
        try:
            data = json.loads(file_path.read_text())
            libraries = set()
            frameworks = set()
            
            if 'require' in data:
                for package in data['require'].keys():
                    if package != 'php':
                        libraries.add(package)
                        if 'laravel' in package or 'symfony' in package:
                            frameworks.add(package.split('/')[0])
            
            return {
                "language": "PHP",
                "package_manager": "composer",
                "libraries": libraries,
                "frameworks": frameworks,
                "file": "composer.json"
            }
        except Exception as e:
            logger.error(f"Error parsing composer.json: {e}")
            return {}
    
    def _parse_gemfile(self, file_path: Path) -> Dict[str, Any]:
        """Parse Ruby Gemfile"""
        try:
            content = file_path.read_text()
            libraries = set()
            frameworks = set()
            
            for line in content.split('\n'):
                if line.strip().startswith('gem '):
                    match = re.search(r"gem ['\"]([^'\"]+)['\"]", line)
                    if match:
                        gem = match.group(1)
                        libraries.add(gem)
                        if gem == 'rails':
                            frameworks.add('rails')
            
            return {
                "language": "Ruby",
                "package_manager": "bundler",
                "libraries": libraries,
                "frameworks": frameworks,
                "file": "Gemfile"
            }
        except Exception as e:
            logger.error(f"Error parsing Gemfile: {e}")
            return {}
    
    def _parse_go_mod(self, file_path: Path) -> Dict[str, Any]:
        """Parse Go go.mod"""
        try:
            content = file_path.read_text()
            libraries = set()
            
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('//') and '/' in line:
                    parts = line.split()
                    if len(parts) >= 1:
                        libraries.add(parts[0])
            
            return {
                "language": "Go",
                "package_manager": "go modules",
                "libraries": libraries,
                "file": "go.mod"
            }
        except Exception as e:
            logger.error(f"Error parsing go.mod: {e}")
            return {}
    
    def _parse_cargo_toml(self, file_path: Path) -> Dict[str, Any]:
        """Parse Rust Cargo.toml"""
        try:
            content = file_path.read_text()
            libraries = set()
            
            in_deps = False
            for line in content.split('\n'):
                if '[dependencies]' in line:
                    in_deps = True
                    continue
                if in_deps and line.strip().startswith('['):
                    in_deps = False
                if in_deps and '=' in line:
                    package = line.split('=')[0].strip()
                    libraries.add(package)
            
            return {
                "language": "Rust",
                "package_manager": "cargo",
                "libraries": libraries,
                "file": "Cargo.toml"
            }
        except Exception as e:
            logger.error(f"Error parsing Cargo.toml: {e}")
            return {}
    
    def _parse_pom_xml(self, file_path: Path) -> Dict[str, Any]:
        """Parse Java pom.xml (basic)"""
        try:
            content = file_path.read_text()
            libraries = set()
            
            # Simple regex for artifactId
            artifacts = re.findall(r'<artifactId>([^<]+)</artifactId>', content)
            libraries.update(artifacts)
            
            return {
                "language": "Java",
                "package_manager": "maven",
                "libraries": libraries,
                "file": "pom.xml"
            }
        except Exception as e:
            logger.error(f"Error parsing pom.xml: {e}")
            return {}
    
    def _parse_pubspec(self, file_path: Path) -> Dict[str, Any]:
        """Parse Flutter/Dart pubspec.yaml"""
        try:
            content = file_path.read_text()
            libraries = set()
            frameworks = set()
            
            # Detect Flutter
            if 'flutter:' in content or 'sdk: flutter' in content:
                frameworks.add('flutter')
            
            # Parse dependencies (simple parsing, not full YAML)
            in_deps = False
            for line in content.split('\n'):
                if line.strip().startswith('dependencies:'):
                    in_deps = True
                    continue
                if in_deps:
                    if line.strip().startswith('dev_dependencies:') or (line and not line.startswith(' ')):
                        in_deps = False
                        continue
                    if ':' in line:
                        package = line.strip().split(':')[0].strip()
                        if package and package != 'sdk':
                            libraries.add(package)
            
            return {
                "language": "Dart/Flutter",
                "package_manager": "pub",
                "libraries": libraries,
                "frameworks": frameworks,
                "file": "pubspec.yaml"
            }
        except Exception as e:
            logger.error(f"Error parsing pubspec.yaml: {e}")
            return {}
    
    def _parse_gradle(self, file_path: Path) -> Dict[str, Any]:
        """Parse Android build.gradle"""
        try:
            content = file_path.read_text()
            libraries = set()
            frameworks = set()
            
            # Detect Android
            if 'com.android.application' in content or 'com.android.library' in content:
                frameworks.add('android')
            
            # Parse dependencies
            dependencies = re.findall(r'implementation\s+["\']([^"\']+)["\']', content)
            for dep in dependencies:
                # Extract library name (e.g., "androidx.core:core-ktx:1.9.0" -> "androidx.core")
                if ':' in dep:
                    lib_name = dep.split(':')[0]
                    libraries.add(lib_name)
            
            return {
                "language": "Kotlin/Java",
                "package_manager": "gradle",
                "libraries": libraries,
                "frameworks": frameworks,
                "file": "build.gradle"
            }
        except Exception as e:
            logger.error(f"Error parsing build.gradle: {e}")
            return {}
    
    def _parse_podfile(self, file_path: Path) -> Dict[str, Any]:
        """Parse iOS Podfile"""
        try:
            content = file_path.read_text()
            libraries = set()
            frameworks = set()
            
            # This is an iOS project
            frameworks.add('ios')
            
            # Parse pods
            pods = re.findall(r"pod\s+['\"]([^'\"]+)['\"]", content)
            libraries.update(pods)
            
            return {
                "language": "Swift/Objective-C",
                "package_manager": "cocoapods",
                "libraries": libraries,
                "frameworks": frameworks,
                "file": "Podfile"
            }
        except Exception as e:
            logger.error(f"Error parsing Podfile: {e}")
            return {}
    
    def _parse_swift_package(self, file_path: Path) -> Dict[str, Any]:
        """Parse Swift Package.swift"""
        try:
            content = file_path.read_text()
            libraries = set()
            
            # Parse package dependencies
            packages = re.findall(r'\.package\([^)]*url:\s*"([^"]+)"', content)
            for url in packages:
                # Extract package name from URL
                if '/' in url:
                    lib_name = url.split('/')[-1].replace('.git', '')
                    libraries.add(lib_name)
            
            return {
                "language": "Swift",
                "package_manager": "swift-pm",
                "libraries": libraries,
                "file": "Package.swift"
            }
        except Exception as e:
            logger.error(f"Error parsing Package.swift: {e}")
            return {}
    
    def _scan_all_imports(self, project_path: Path) -> Dict[str, Any]:
        """Scan source files for import statements"""
        libraries = set()
        frameworks = set()
        
        # Python files
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text(errors='ignore')
                # Find imports
                imports = re.findall(r'^(?:from|import)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
                for imp in imports:
                    if imp not in ['os', 'sys', 'json', 're', 'time', 'datetime']:  # Skip stdlib
                        libraries.add(imp.lower())
                        
                        # Check for frameworks
                        if imp.lower() in ['django', 'flask', 'fastapi', 'tornado']:
                            frameworks.add(imp.lower())
            except Exception:
                continue
        
        return {
            "libraries": libraries,
            "frameworks": frameworks
        }
    
    def _check_package_file(self, file_path: str) -> Dict[str, Any]:
        """Check a specific package file"""
        path = Path(file_path)
        if not path.exists():
            return {
                "status": "error",
                "error": f"File not found: {file_path}"
            }
        
        parsers = {
            "requirements.txt": self._parse_requirements,
            "package.json": self._parse_package_json,
            "Pipfile": self._parse_pipfile,
            "pyproject.toml": self._parse_pyproject,
        }
        
        parser = parsers.get(path.name)
        if parser:
            result = parser(path)
            result["status"] = "success"
            return result
        
        return {
            "status": "error",
            "error": f"No parser for file type: {path.name}"
        }
    
    def _scan_imports(self, directory: str = ".", pattern: str = "*.py") -> Dict[str, Any]:
        """Scan specific directory for imports"""
        dir_path = self.project_root / directory
        
        if not dir_path.exists():
            return {
                "status": "error",
                "error": f"Directory not found: {directory}"
            }
        
        imports = set()
        
        for file_path in dir_path.rglob(pattern):
            try:
                content = file_path.read_text(errors='ignore')
                found_imports = re.findall(r'^(?:from|import)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
                imports.update(found_imports)
            except Exception:
                continue
        
        return {
            "status": "success",
            "imports": sorted(imports),
            "count": len(imports)
        }
    
    def _detect_project_type(self, analysis: Dict) -> str:
        """Detect the type of project"""
        frameworks = set(analysis.get("frameworks", []))
        libraries = set(analysis.get("libraries", []))
        languages = set(analysis.get("languages", []))
        
        # Use LLM to intelligently classify if we have many libraries
        # For now, use heuristics
        
        # Mobile/Cross-platform
        if 'flutter' in frameworks:
            return "Flutter Mobile App"
        if 'android' in frameworks:
            return "Android App"
        if 'ios' in frameworks:
            return "iOS App"
        if 'react-native' in libraries or 'react-native' in frameworks:
            return "React Native Mobile App"
        
        # AI/ML frameworks
        ai_ml_libs = ['yolo', 'ultralytics', 'tensorflow', 'pytorch', 'keras', 
                      'scikit-learn', 'sklearn', 'opencv', 'transformers']
        if any(lib in libraries for lib in ai_ml_libs):
            return "AI/ML Application"
        
        # Computer Vision
        cv_libs = ['opencv', 'cv2', 'pillow', 'imageio', 'yolo']
        if any(lib in libraries for lib in cv_libs):
            return "Computer Vision Application"
        
        # Web frameworks
        if any(f in frameworks for f in ['django', 'flask', 'fastapi']):
            return "Python Web API"
        if any(f in frameworks for f in ['react', 'vue', 'angular']):
            return "JavaScript Frontend"
        if any(f in frameworks for f in ['express', 'koa', 'fastify']):
            return "Node.js Backend"
        if 'rails' in frameworks:
            return "Ruby on Rails Web App"
        if 'nextjs' in libraries or 'next' in frameworks:
            return "Next.js Web App"
        
        # Data science
        if any(lib in libraries for lib in ['pandas', 'numpy']):
            return "Data Science Application"
        
        # General by language
        if "Dart/Flutter" in languages:
            return "Flutter Application"
        if "Swift" in languages or "Swift/Objective-C" in languages:
            return "iOS Application"
        if "Kotlin/Java" in languages and 'android' in frameworks:
            return "Android Application"
        if 'Python' in languages:
            return "Python Application"
        if 'JavaScript/TypeScript' in languages:
            return "JavaScript Application"
        
        return "Unknown"
    
    def get_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate a human-readable summary"""
        if analysis.get("status") != "success":
            return "Analysis failed"
        
        lines = [
            f"Project Type: {analysis.get('project_type', 'Unknown')}",
            f"Languages: {', '.join(analysis.get('languages', []))}",
        ]
        
        if analysis.get("frameworks"):
            lines.append(f"Frameworks: {', '.join(analysis['frameworks'][:5])}")
        
        if analysis.get("libraries"):
            lib_count = len(analysis["libraries"])
            lib_list = ', '.join(sorted(analysis['libraries'])[:10])
            if lib_count > 10:
                lib_list += f" ... ({lib_count - 10} more)"
            lines.append(f"Libraries: {lib_list}")
        
        if analysis.get("package_managers"):
            lines.append(f"Package Managers: {', '.join(analysis['package_managers'])}")
        
        return "\n".join(lines)
    
    def _check_versions(self, package_file: Optional[str] = None) -> Dict[str, Any]:
        """Check installed versions of packages"""
        import subprocess
        
        result = {
            "status": "success",
            "versions": {},
            "language": None
        }
        
        try:
            # Python packages
            if package_file and "requirements" in package_file:
                result["language"] = "Python"
                
                # Use pip list to get installed versions
                proc = subprocess.run(
                    ["pip", "list", "--format=json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if proc.returncode == 0:
                    import json
                    packages = json.loads(proc.stdout)
                    for pkg in packages:
                        result["versions"][pkg["name"].lower()] = pkg["version"]
            
            # Node.js packages
            elif package_file and "package.json" in package_file:
                result["language"] = "JavaScript"
                
                # Read package-lock.json if available
                lock_file = self.project_root / "package-lock.json"
                if lock_file.exists():
                    data = json.loads(lock_file.read_text())
                    if "packages" in data:
                        for pkg_name, pkg_info in data["packages"].items():
                            if pkg_name:  # Skip root package
                                clean_name = pkg_name.split("/")[-1]
                                result["versions"][clean_name] = pkg_info.get("version", "unknown")
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking versions: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _check_outdated(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Check for outdated packages"""
        import subprocess
        
        result = {
            "status": "success",
            "outdated": [],
            "command_used": None,
            "language": language
        }
        
        try:
            # Auto-detect language if not provided
            if not language:
                if (self.project_root / "requirements.txt").exists():
                    language = "python"
                elif (self.project_root / "package.json").exists():
                    language = "javascript"
            
            # Python
            if language and language.lower() == "python":
                result["command_used"] = "pip list --outdated"
                
                proc = subprocess.run(
                    ["pip", "list", "--outdated", "--format=json"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(self.project_root)
                )
                
                if proc.returncode == 0:
                    import json
                    outdated = json.loads(proc.stdout)
                    
                    for pkg in outdated:
                        result["outdated"].append({
                            "name": pkg["name"],
                            "current": pkg["version"],
                            "latest": pkg["latest_version"],
                            "type": pkg.get("latest_filetype", "wheel")
                        })
            
            # Node.js
            elif language and language.lower() in ["javascript", "nodejs", "node"]:
                result["command_used"] = "npm outdated"
                
                proc = subprocess.run(
                    ["npm", "outdated", "--json"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(self.project_root)
                )
                
                # npm outdated returns exit code 1 if there are outdated packages
                if proc.stdout:
                    import json
                    try:
                        outdated_data = json.loads(proc.stdout)
                        
                        for pkg_name, pkg_info in outdated_data.items():
                            result["outdated"].append({
                                "name": pkg_name,
                                "current": pkg_info.get("current", "unknown"),
                                "latest": pkg_info.get("latest", "unknown"),
                                "wanted": pkg_info.get("wanted", "unknown")
                            })
                    except json.JSONDecodeError:
                        pass
            
            else:
                result["status"] = "error"
                result["error"] = "Could not determine language or unsupported language"
            
            result["total_outdated"] = len(result["outdated"])
            return result
            
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "Command timed out"
            }
        except FileNotFoundError as e:
            return {
                "status": "error",
                "error": f"Package manager not found: {e}"
            }
        except Exception as e:
            logger.error(f"Error checking outdated packages: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    
    def research_unknown_libraries(self, libraries: List[str], limit: int = 5) -> Dict[str, Any]:
        """
        Automatically research unknown/unfamiliar libraries.
        This can be used by the Research Agent to learn about new frameworks.
        
        Args:
            libraries: List of library names to research
            limit: Max number of libraries to research
            
        Returns:
            Dictionary with research results for each library
        """
        results = {
            "status": "success",
            "researched": {},
            "total": len(libraries[:limit])
        }
        
        for lib in libraries[:limit]:
            results["researched"][lib] = {
                "name": lib,
                "needs_research": True,
                "search_query": f"{lib} framework documentation",
                "pypi_url": f"https://pypi.org/project/{lib}/",
                "npm_url": f"https://www.npmjs.com/package/{lib}",
                "github_search": f"https://github.com/search?q={lib}",
            }
        
        return results
