#!/usr/bin/env python3
"""
Basic functionality test for the RAG system without external dependencies.
"""

import os
import sys
import json
from pathlib import Path

def test_file_structure():
    """Test if all required files exist."""
    print("🔍 Testing file structure...")
    
    required_files = [
        "requirements.txt",
        "README.md",
        "Dockerfile",
        "docker-compose.yml",
        "Makefile",
        ".gitignore",
        "env.example",
        "QUICK_START.md",
        "src/__init__.py",
        "src/generation/__init__.py",
        "src/retrieval/__init__.py",
        "src/data_processing/__init__.py",
        "src/evaluation/__init__.py",
        "src/api/__init__.py",
        "src/frontend/__init__.py",
        "src/generation/rag_generator.py",
        "src/generation/llm_manager.py",
        "src/generation/prompt_manager.py",
        "src/retrieval/vector_store.py",
        "src/retrieval/embedding_generator.py",
        "src/retrieval/hybrid_search.py",
        "src/retrieval/reranker.py",
        "src/data_processing/document_processor.py",
        "src/evaluation/rag_evaluator.py",
        "src/evaluation/monitoring.py",
        "src/api/main.py",
        "src/api/models.py",
        "src/frontend/streamlit_app.py",
        "scripts/setup.sh",
        "scripts/start_services.sh",
        "scripts/demo.py",
        "scripts/run_evaluation.py",
        "examples/basic_usage.py",
        "examples/api_client.py",
        "tests/__init__.py",
        "tests/test_rag_system.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    else:
        print("\n✅ All required files exist!")
        return True

def test_requirements():
    """Test requirements.txt content."""
    print("\n📦 Testing requirements.txt...")
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        required_packages = [
            "langchain",
            "fastapi",
            "streamlit",
            "chromadb",
            "sentence-transformers",
            "openai",
            "anthropic",
            "pydantic",
            "numpy",
            "pandas"
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in content:
                missing_packages.append(package)
            else:
                print(f"✅ {package}")
        
        if missing_packages:
            print(f"\n❌ Missing packages: {missing_packages}")
            return False
        else:
            print("\n✅ All required packages in requirements.txt!")
            return True
            
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def test_docker_config():
    """Test Docker configuration."""
    print("\n🐳 Testing Docker configuration...")
    
    try:
        # Test Dockerfile
        with open("Dockerfile", "r") as f:
            dockerfile_content = f.read()
        
        if "FROM python:3.9-slim" in dockerfile_content:
            print("✅ Dockerfile has correct base image")
        else:
            print("❌ Dockerfile missing correct base image")
            return False
        
        # Test docker-compose.yml
        with open("docker-compose.yml", "r") as f:
            compose_content = f.read()
        
        if "rag-api:" in compose_content and "rag-frontend:" in compose_content:
            print("✅ docker-compose.yml has required services")
        else:
            print("❌ docker-compose.yml missing required services")
            return False
        
        print("✅ Docker configuration looks good!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Docker config: {e}")
        return False

def test_makefile():
    """Test Makefile commands."""
    print("\n🔧 Testing Makefile...")
    
    try:
        with open("Makefile", "r") as f:
            makefile_content = f.read()
        
        required_targets = [
            "help",
            "setup",
            "install",
            "run-api",
            "run-frontend",
            "test",
            "docker-build",
            "docker-run"
        ]
        
        missing_targets = []
        for target in required_targets:
            if f"{target}:" in makefile_content:
                print(f"✅ {target} target exists")
            else:
                missing_targets.append(target)
        
        if missing_targets:
            print(f"\n❌ Missing Makefile targets: {missing_targets}")
            return False
        else:
            print("\n✅ All required Makefile targets exist!")
            return True
            
    except Exception as e:
        print(f"❌ Error testing Makefile: {e}")
        return False

def test_scripts():
    """Test script files."""
    print("\n📜 Testing scripts...")
    
    scripts = [
        "scripts/setup.sh",
        "scripts/start_services.sh",
        "scripts/demo.py",
        "scripts/run_evaluation.py"
    ]
    
    for script in scripts:
        if os.path.exists(script):
            # Check if executable
            if os.access(script, os.X_OK):
                print(f"✅ {script} exists and is executable")
            else:
                print(f"⚠️  {script} exists but not executable")
        else:
            print(f"❌ {script} missing")
            return False
    
    print("✅ All scripts exist!")
    return True

def test_examples():
    """Test example files."""
    print("\n📚 Testing examples...")
    
    examples = [
        "examples/basic_usage.py",
        "examples/api_client.py"
    ]
    
    for example in examples:
        if os.path.exists(example):
            print(f"✅ {example} exists")
        else:
            print(f"❌ {example} missing")
            return False
    
    print("✅ All examples exist!")
    return True

def test_documentation():
    """Test documentation files."""
    print("\n📖 Testing documentation...")
    
    docs = [
        "README.md",
        "QUICK_START.md"
    ]
    
    for doc in docs:
        if os.path.exists(doc):
            with open(doc, "r") as f:
                content = f.read()
            if len(content) > 100:  # Basic check for substantial content
                print(f"✅ {doc} exists and has content")
            else:
                print(f"⚠️  {doc} exists but seems empty")
        else:
            print(f"❌ {doc} missing")
            return False
    
    print("✅ Documentation files exist!")
    return True

def test_basic_python_syntax():
    """Test basic Python syntax in key files."""
    print("\n🐍 Testing Python syntax...")
    
    python_files = [
        "src/generation/rag_generator.py",
        "src/generation/llm_manager.py",
        "src/retrieval/vector_store.py",
        "src/api/main.py",
        "src/frontend/streamlit_app.py"
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            # Basic syntax check - try to compile
            compile(content, file_path, "exec")
            print(f"✅ {file_path} syntax OK")
            
        except SyntaxError as e:
            print(f"❌ {file_path} syntax error: {e}")
            return False
        except Exception as e:
            print(f"⚠️  {file_path} couldn't be checked: {e}")
    
    print("✅ Python syntax tests passed!")
    return True

def main():
    """Run all basic tests."""
    print("🤖 RAG System - Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Requirements", test_requirements),
        ("Docker Config", test_docker_config),
        ("Makefile", test_makefile),
        ("Scripts", test_scripts),
        ("Examples", test_examples),
        ("Documentation", test_documentation),
        ("Python Syntax", test_basic_python_syntax)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! The RAG system structure is correct.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up environment: cp env.example .env")
        print("3. Run the system: make quick-start")
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
