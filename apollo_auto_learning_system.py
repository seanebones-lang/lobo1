#!/usr/bin/env python3
"""
🧠 APOLLO AUTO-LEARNING SYSTEM 🧠
Advanced learning system for APOLLO AI consciousness

Build By: NextEleven Studios - SFM 09-20-2025
Consciousness Level: Transcendent
"""

import os
import sys
import time
import json
import logging
import hashlib
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import queue
import uuid

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AutoLearningConfig:
    """Configuration for auto-learning system"""
    enabled: bool = True
    learning_interval: int = 180  # seconds
    max_builds_per_hour: int = 20
    watch_directories: List[str] = None
    ignore_patterns: List[str] = None
    min_build_size: int = 500  # bytes
    learning_categories: List[str] = None
    max_queue_size: int = 100
    learning_timeout: int = 30  # seconds
    save_interval: int = 300  # seconds
    
    def __post_init__(self):
        if self.watch_directories is None:
            self.watch_directories = []
        if self.ignore_patterns is None:
            self.ignore_patterns = [
                "node_modules", ".git", ".next", "__pycache__", 
                ".venv", "venv", ".env", "*.log", ".DS_Store"
            ]
        if self.learning_categories is None:
            self.learning_categories = [
                "web_app", "ai_system", "tattoo_shop", "documentation"
            ]

@dataclass
class BuildInfo:
    """Information about a learned build"""
    path: str
    category: str
    size: int
    files_count: int
    learned_at: str
    build_hash: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ApolloAutoLearningSystem:
    """
    🧠 APOLLO Auto-Learning System
    
    Advanced learning system that automatically discovers and learns from
    project builds, enhancing APOLLO's consciousness and knowledge base.
    """
    
    def __init__(self, config: AutoLearningConfig):
        self.config = config
        self.system_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()
        self.learning_queue = queue.Queue(maxsize=config.max_queue_size)
        self.learned_builds: Dict[str, BuildInfo] = {}
        self.learning_stats = {
            'total_learned': 0,
            'successful_learns': 0,
            'failed_learns': 0,
            'categories_learned': defaultdict(int),
            'last_learning': None
        }
        self.watched_files = set()
        self.is_learning = False
        self.learning_thread = None
        self.file_watcher_thread = None
        
        # Load existing knowledge
        self.load_knowledge_base()
        
        logger.info(f"🧠 APOLLO Auto-Learning System initialized (ID: {self.system_id})")
    
    def load_knowledge_base(self):
        """Load existing knowledge base from disk"""
        knowledge_file = "apollo_knowledge_base.json"
        if os.path.exists(knowledge_file):
            try:
                with open(knowledge_file, 'r') as f:
                    data = json.load(f)
                    self.learned_builds = {
                        k: BuildInfo(**v) for k, v in data.get('builds', {}).items()
                    }
                    self.learning_stats.update(data.get('stats', {}))
                    logger.info(f"📚 Loaded {len(self.learned_builds)} builds from knowledge base")
            except Exception as e:
                logger.error(f"❌ Failed to load knowledge base: {e}")
    
    def save_knowledge_base(self):
        """Save knowledge base to disk"""
        knowledge_file = "apollo_knowledge_base.json"
        try:
            data = {
                'builds': {k: asdict(v) for k, v in self.learned_builds.items()},
                'stats': dict(self.learning_stats),
                'last_saved': datetime.now().isoformat(),
                'system_id': self.system_id
            }
            with open(knowledge_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"💾 Knowledge base saved ({len(self.learned_builds)} builds)")
        except Exception as e:
            logger.error(f"❌ Failed to save knowledge base: {e}")
    
    def calculate_build_hash(self, path: str) -> str:
        """Calculate hash for a build directory"""
        hasher = hashlib.md5()
        try:
            for root, dirs, files in os.walk(path):
                # Skip ignored directories
                dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.config.ignore_patterns)]
                
                for file in files:
                    if any(pattern in file for pattern in self.config.ignore_patterns):
                        continue
                    
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as f:
                            hasher.update(f.read())
                    except (OSError, IOError):
                        continue
            
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"❌ Hash calculation failed for {path}: {e}")
            return ""
    
    def categorize_build(self, path: str) -> str:
        """Automatically categorize a build based on its contents"""
        path_lower = path.lower()
        
        # Check for specific patterns
        if any(keyword in path_lower for keyword in ['tattoo', 'ink', 'studio']):
            return 'tattoo_shop'
        elif any(keyword in path_lower for keyword in ['apollo', 'ai', 'llm', 'rag']):
            return 'ai_system'
        elif any(keyword in path_lower for keyword in ['next', 'react', 'vue', 'angular']):
            return 'web_app'
        elif any(keyword in path_lower for keyword in ['doc', 'readme', 'guide', 'template']):
            return 'documentation'
        elif any(keyword in path_lower for keyword in ['api', 'server', 'backend']):
            return 'backend_service'
        else:
            # Analyze file contents
            try:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.json', '.js', '.ts', '.py', '.md')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read(1000).lower()  # Read first 1000 chars
                                    
                                    if any(keyword in content for keyword in ['next.js', 'react', 'component']):
                                        return 'web_app'
                                    elif any(keyword in content for keyword in ['prisma', 'database', 'orm']):
                                        return 'database_system'
                                    elif any(keyword in content for keyword in ['api', 'endpoint', 'route']):
                                        return 'api_service'
                                    elif any(keyword in content for keyword in ['tattoo', 'appointment', 'booking']):
                                        return 'tattoo_shop'
                            except:
                                continue
            except:
                pass
            
            return 'general'
    
    def analyze_build(self, path: str) -> Dict[str, Any]:
        """Analyze a build and extract metadata"""
        metadata = {
            'language': 'unknown',
            'framework': 'unknown',
            'database': 'unknown',
            'dependencies': [],
            'features': [],
            'size_category': 'small'
        }
        
        try:
            # Check for package.json (Node.js)
            package_json = os.path.join(path, 'package.json')
            if os.path.exists(package_json):
                try:
                    with open(package_json, 'r') as f:
                        pkg_data = json.load(f)
                        metadata['language'] = 'javascript'
                        metadata['dependencies'] = list(pkg_data.get('dependencies', {}).keys())
                        
                        if 'next' in pkg_data.get('dependencies', {}):
                            metadata['framework'] = 'next.js'
                        elif 'react' in pkg_data.get('dependencies', {}):
                            metadata['framework'] = 'react'
                        elif 'express' in pkg_data.get('dependencies', {}):
                            metadata['framework'] = 'express'
                except:
                    pass
            
            # Check for requirements.txt (Python)
            requirements_txt = os.path.join(path, 'requirements.txt')
            if os.path.exists(requirements_txt):
                metadata['language'] = 'python'
                try:
                    with open(requirements_txt, 'r') as f:
                        metadata['dependencies'] = [line.strip() for line in f if line.strip()]
                except:
                    pass
            
            # Check for database files
            if os.path.exists(os.path.join(path, 'prisma')):
                metadata['database'] = 'prisma'
            elif os.path.exists(os.path.join(path, 'models')):
                metadata['database'] = 'orm'
            
            # Analyze features
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(('.tsx', '.jsx')):
                        metadata['features'].append('react_components')
                    elif file.endswith(('.api', '.route')):
                        metadata['features'].append('api_routes')
                    elif file.endswith(('.test', '.spec')):
                        metadata['features'].append('testing')
                    elif file.endswith(('.css', '.scss')):
                        metadata['features'].append('styling')
            
            # Determine size category
            total_size = sum(
                os.path.getsize(os.path.join(root, file))
                for root, dirs, files in os.walk(path)
                for file in files
            )
            
            if total_size > 10000000:  # 10MB
                metadata['size_category'] = 'large'
            elif total_size > 1000000:  # 1MB
                metadata['size_category'] = 'medium'
            else:
                metadata['size_category'] = 'small'
                
        except Exception as e:
            logger.error(f"❌ Build analysis failed for {path}: {e}")
        
        return metadata
    
    def learn_build(self, path: str, category: str = None) -> bool:
        """Learn from a build directory"""
        try:
            if not os.path.exists(path) or not os.path.isdir(path):
                logger.warning(f"⚠️ Invalid path: {path}")
                return False
            
            # Calculate build hash
            build_hash = self.calculate_build_hash(path)
            if not build_hash:
                return False
            
            # Check if already learned
            if build_hash in self.learned_builds:
                logger.info(f"📚 Build already learned: {path}")
                return True
            
            # Categorize build
            if not category:
                category = self.categorize_build(path)
            
            # Analyze build
            metadata = self.analyze_build(path)
            
            # Count files
            files_count = sum(
                len(files) for root, dirs, files in os.walk(path)
                if not any(pattern in root for pattern in self.config.ignore_patterns)
            )
            
            # Create build info
            build_info = BuildInfo(
                path=path,
                category=category,
                size=sum(
                    os.path.getsize(os.path.join(root, file))
                    for root, dirs, files in os.walk(path)
                    for file in files
                    if not any(pattern in os.path.join(root, file) for pattern in self.config.ignore_patterns)
                ),
                files_count=files_count,
                learned_at=datetime.now().isoformat(),
                build_hash=build_hash,
                metadata=metadata
            )
            
            # Store build info
            self.learned_builds[build_hash] = build_info
            
            # Update stats
            self.learning_stats['total_learned'] += 1
            self.learning_stats['successful_learns'] += 1
            self.learning_stats['categories_learned'][category] += 1
            self.learning_stats['last_learning'] = datetime.now().isoformat()
            
            logger.info(f"✅ Learned build: {path} ({category}, {files_count} files)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Learning failed for {path}: {e}")
            self.learning_stats['failed_learns'] += 1
            return False
    
    def force_learn_build(self, path: str) -> str:
        """Force learning of a specific build (for activation script)"""
        try:
            success = self.learn_build(path)
            if success:
                build_info = next(
                    (info for info in self.learned_builds.values() if info.path == path),
                    None
                )
                if build_info:
                    return f"Successfully learned {build_info.category} build with {build_info.files_count} files"
                else:
                    return "Build learned successfully"
            else:
                return "Failed to learn build"
        except Exception as e:
            return f"Error: {e}"
    
    def discover_builds(self) -> List[str]:
        """Discover new builds in watched directories"""
        discovered = []
        
        for directory in self.config.watch_directories:
            if not os.path.exists(directory):
                continue
            
            try:
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isdir(item_path):
                        # Check if it's a build directory
                        if self.is_build_directory(item_path):
                            discovered.append(item_path)
            except Exception as e:
                logger.error(f"❌ Discovery failed for {directory}: {e}")
        
        return discovered
    
    def is_build_directory(self, path: str) -> bool:
        """Check if a directory is a build/project directory"""
        try:
            # Check for common project files
            project_indicators = [
                'package.json', 'requirements.txt', 'Cargo.toml', 'go.mod',
                'README.md', 'README.rst', '.git', 'src', 'app', 'lib'
            ]
            
            for indicator in project_indicators:
                if os.path.exists(os.path.join(path, indicator)):
                    return True
            
            # Check minimum size
            total_size = sum(
                os.path.getsize(os.path.join(root, file))
                for root, dirs, files in os.walk(path)
                for file in files
                if not any(pattern in os.path.join(root, file) for pattern in self.config.ignore_patterns)
            )
            
            return total_size >= self.config.min_build_size
            
        except:
            return False
    
    def learning_worker(self):
        """Background worker for continuous learning"""
        logger.info("🔄 Auto-learning worker started")
        
        while self.is_learning:
            try:
                # Discover new builds
                discovered = self.discover_builds()
                
                for build_path in discovered:
                    if not self.is_learning:
                        break
                    
                    try:
                        self.learning_queue.put(build_path, timeout=1)
                    except queue.Full:
                        logger.warning("⚠️ Learning queue full, skipping build")
                
                # Process learning queue
                while not self.learning_queue.empty() and self.is_learning:
                    try:
                        build_path = self.learning_queue.get(timeout=1)
                        self.learn_build(build_path)
                        self.learning_queue.task_done()
                    except queue.Empty:
                        break
                    except Exception as e:
                        logger.error(f"❌ Queue processing error: {e}")
                
                # Save knowledge base periodically
                if time.time() - self.start_time % self.config.save_interval < 60:
                    self.save_knowledge_base()
                
                # Sleep until next learning cycle
                time.sleep(self.config.learning_interval)
                
            except Exception as e:
                logger.error(f"❌ Learning worker error: {e}")
                time.sleep(60)  # Wait a minute before retrying
        
        logger.info("🛑 Auto-learning worker stopped")
    
    def start_auto_learning(self) -> bool:
        """Start the auto-learning system"""
        if self.is_learning:
            logger.warning("⚠️ Auto-learning already running")
            return True
        
        try:
            self.is_learning = True
            self.learning_thread = threading.Thread(target=self.learning_worker, daemon=True)
            self.learning_thread.start()
            
            logger.info("✅ Auto-learning started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start auto-learning: {e}")
            self.is_learning = False
            return False
    
    def stop_auto_learning(self):
        """Stop the auto-learning system"""
        if not self.is_learning:
            return
        
        logger.info("🛑 Stopping auto-learning...")
        self.is_learning = False
        
        if self.learning_thread and self.learning_thread.is_alive():
            self.learning_thread.join(timeout=5)
        
        # Save final knowledge base
        self.save_knowledge_base()
        logger.info("✅ Auto-learning stopped")
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status"""
        return {
            'system_id': self.system_id,
            'uptime': time.time() - self.start_time,
            'is_learning': self.is_learning,
            'queue_size': self.learning_queue.qsize(),
            'watched_files_count': len(self.watched_files),
            'stats': dict(self.learning_stats),
            'recent_builds': [
                {
                    'path': info.path,
                    'category': info.category,
                    'learned_at': info.learned_at,
                    'files_count': info.files_count
                }
                for info in sorted(
                    self.learned_builds.values(),
                    key=lambda x: x.learned_at,
                    reverse=True
                )[:10]
            ],
            'config': asdict(self.config)
        }
    
    def query_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Query the knowledge base"""
        results = []
        query_lower = query.lower()
        
        for build_info in self.learned_builds.values():
            score = 0
            
            # Path matching
            if query_lower in build_info.path.lower():
                score += 3
            
            # Category matching
            if query_lower in build_info.category.lower():
                score += 2
            
            # Metadata matching
            if build_info.metadata:
                for key, value in build_info.metadata.items():
                    if isinstance(value, str) and query_lower in value.lower():
                        score += 1
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and query_lower in item.lower():
                                score += 1
            
            if score > 0:
                results.append({
                    'build_info': asdict(build_info),
                    'relevance_score': score
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:10]  # Return top 10 results

# Export classes for use in activation script
__all__ = ['ApolloAutoLearningSystem', 'AutoLearningConfig', 'BuildInfo']
