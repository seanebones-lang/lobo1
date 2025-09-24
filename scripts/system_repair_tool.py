#!/usr/bin/env python3
"""
System Repair Tool for RAG System
Automatically detects and repairs common system issues
"""

import os
import sys
import subprocess
import logging
import json
import time
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system_repair.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SystemRepairTool:
    """Comprehensive system repair tool for RAG system"""
    
    def __init__(self):
        self.repair_log = []
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Critical files to backup before repair
        self.critical_files = [
            "src/api/main.py",
            "app/lib/api-pipeline.ts",
            "app/lib/rag-pipeline.ts",
            "deploy/docker-compose.prod.yml",
            "requirements.txt",
            ".env"
        ]
        
        # Repair strategies
        self.repair_strategies = {
            'missing_imports': self.fix_missing_imports,
            'syntax_errors': self.fix_syntax_errors,
            'file_permissions': self.fix_file_permissions,
            'docker_issues': self.fix_docker_issues,
            'dependency_issues': self.fix_dependency_issues,
            'configuration_issues': self.fix_configuration_issues,
            'database_issues': self.fix_database_issues,
            'service_issues': self.fix_service_issues
        }
    
    def run_full_repair(self):
        """Run full system repair"""
        logger.info("🔧 Starting full system repair...")
        
        # Create backup
        self.create_backup()
        
        # Run all repair strategies
        for issue_type, repair_func in self.repair_strategies.items():
            try:
                logger.info(f"Running repair for: {issue_type}")
                result = repair_func()
                self.repair_log.append({
                    'issue_type': issue_type,
                    'status': 'success' if result else 'failed',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Repair failed for {issue_type}: {e}")
                self.repair_log.append({
                    'issue_type': issue_type,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Generate repair report
        self.generate_repair_report()
        
        logger.info("✅ System repair completed")
    
    def create_backup(self):
        """Create backup of critical files"""
        logger.info("📦 Creating backup of critical files...")
        
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{backup_timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        for file_path in self.critical_files:
            if os.path.exists(file_path):
                dest_path = backup_path / Path(file_path).name
                shutil.copy2(file_path, dest_path)
                logger.info(f"Backed up: {file_path}")
        
        logger.info(f"Backup created at: {backup_path}")
    
    def fix_missing_imports(self) -> bool:
        """Fix missing imports in Python files"""
        logger.info("🔍 Fixing missing imports...")
        
        python_files = list(Path("src").rglob("*.py"))
        fixed_files = 0
        
        for file_path in python_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check for common missing imports
                missing_imports = []
                
                if 'import asyncio' not in content and 'asyncio.' in content:
                    missing_imports.append('import asyncio')
                
                if 'import logging' not in content and 'logging.' in content:
                    missing_imports.append('import logging')
                
                if 'import json' not in content and 'json.' in content:
                    missing_imports.append('import json')
                
                if 'from typing import' not in content and ('Dict[' in content or 'List[' in content):
                    missing_imports.append('from typing import Dict, List, Any, Optional')
                
                if missing_imports:
                    # Add imports at the top
                    lines = content.split('\n')
                    import_section = []
                    
                    for import_line in missing_imports:
                        if import_line not in lines:
                            import_section.append(import_line)
                    
                    if import_section:
                        # Find the last import line
                        last_import_idx = 0
                        for i, line in enumerate(lines):
                            if line.strip().startswith(('import ', 'from ')):
                                last_import_idx = i
                        
                        # Insert new imports
                        for j, import_line in enumerate(import_section):
                            lines.insert(last_import_idx + j + 1, import_line)
                        
                        # Write back
                        with open(file_path, 'w') as f:
                            f.write('\n'.join(lines))
                        
                        fixed_files += 1
                        logger.info(f"Fixed imports in: {file_path}")
            
            except Exception as e:
                logger.error(f"Error fixing imports in {file_path}: {e}")
        
        logger.info(f"Fixed imports in {fixed_files} files")
        return True
    
    def fix_syntax_errors(self) -> bool:
        """Fix common syntax errors"""
        logger.info("🔍 Fixing syntax errors...")
        
        python_files = list(Path("src").rglob("*.py"))
        fixed_files = 0
        
        for file_path in python_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix common syntax errors
                fixes = [
                    # Fix incomplete lines
                    (r'=\s*$', '= None'),
                    (r'def\s+\w+\s*\(\s*\):\s*$', 'def method():\n    pass'),
                    (r'class\s+\w+\s*:\s*$', 'class ClassName:\n    pass'),
                    
                    # Fix missing quotes
                    (r'(["\'])([^"\']*)\1\s*$', r'\1\2\1'),
                    
                    # Fix missing colons
                    (r'(if|for|while|def|class|try|except|with)\s+[^:]+$', r'\1 condition:\n    pass'),
                    
                    # Fix incomplete imports
                    (r'from\s+\w+\s+import\s*$', 'from module import component'),
                ]
                
                for pattern, replacement in fixes:
                    import re
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                
                if content != original_content:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    fixed_files += 1
                    logger.info(f"Fixed syntax errors in: {file_path}")
            
            except Exception as e:
                logger.error(f"Error fixing syntax in {file_path}: {e}")
        
        logger.info(f"Fixed syntax errors in {fixed_files} files")
        return True
    
    def fix_file_permissions(self) -> bool:
        """Fix file permissions"""
        logger.info("🔍 Fixing file permissions...")
        
        # Set proper permissions for Python files
        python_files = list(Path(".").rglob("*.py"))
        for file_path in python_files:
            try:
                os.chmod(file_path, 0o644)
            except Exception as e:
                logger.error(f"Error setting permissions for {file_path}: {e}")
        
        # Set executable permissions for scripts
        script_files = [
            "scripts/setup.sh",
            "scripts/start_services.sh",
            "scripts/demo.py",
            "scripts/run_evaluation.py",
            "scripts/system_health_monitor.py",
            "scripts/test_api_endpoints.py",
            "scripts/system_repair_tool.py"
        ]
        
        for script_file in script_files:
            if os.path.exists(script_file):
                try:
                    os.chmod(script_file, 0o755)
                    logger.info(f"Set executable permissions for: {script_file}")
                except Exception as e:
                    logger.error(f"Error setting permissions for {script_file}: {e}")
        
        return True
    
    def fix_docker_issues(self) -> bool:
        """Fix Docker-related issues"""
        logger.info("🔍 Fixing Docker issues...")
        
        try:
            # Check if Docker is running
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning("Docker is not running. Attempting to start...")
                subprocess.run(['sudo', 'systemctl', 'start', 'docker'], check=True)
            
            # Clean up Docker system
            subprocess.run(['docker', 'system', 'prune', '-f'], check=True)
            logger.info("Docker system cleaned up")
            
            # Rebuild containers if needed
            if os.path.exists('docker-compose.yml'):
                subprocess.run(['docker-compose', 'build', '--no-cache'], check=True)
                logger.info("Docker containers rebuilt")
            
            return True
            
        except Exception as e:
            logger.error(f"Error fixing Docker issues: {e}")
            return False
    
    def fix_dependency_issues(self) -> bool:
        """Fix dependency issues"""
        logger.info("🔍 Fixing dependency issues...")
        
        try:
            # Install Python dependencies
            if os.path.exists('requirements.txt'):
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
                logger.info("Python dependencies installed")
            
            # Install Node.js dependencies
            if os.path.exists('package.json'):
                subprocess.run(['npm', 'install'], check=True)
                logger.info("Node.js dependencies installed")
            
            # Install mobile dependencies
            if os.path.exists('mobile/package.json'):
                subprocess.run(['npm', 'install'], cwd='mobile', check=True)
                logger.info("Mobile dependencies installed")
            
            return True
            
        except Exception as e:
            logger.error(f"Error fixing dependency issues: {e}")
            return False
    
    def fix_configuration_issues(self) -> bool:
        """Fix configuration issues"""
        logger.info("🔍 Fixing configuration issues...")
        
        # Create .env file if missing
        if not os.path.exists('.env') and os.path.exists('env.example'):
            shutil.copy('env.example', '.env')
            logger.info("Created .env file from env.example")
        
        # Fix Docker Compose configuration
        docker_compose_files = ['docker-compose.yml', 'deploy/docker-compose.prod.yml']
        for compose_file in docker_compose_files:
            if os.path.exists(compose_file):
                self.fix_docker_compose_config(compose_file)
        
        # Fix Nginx configuration
        nginx_files = ['nginx.conf', 'deploy/nginx.prod.conf']
        for nginx_file in nginx_files:
            if os.path.exists(nginx_file):
                self.fix_nginx_config(nginx_file)
        
        return True
    
    def fix_docker_compose_config(self, compose_file: str):
        """Fix Docker Compose configuration"""
        try:
            with open(compose_file, 'r') as f:
                content = f.read()
            
            # Fix common Docker Compose issues
            fixes = [
                # Fix missing version
                (r'^services:', 'version: "3.8"\n\nservices:'),
                
                # Fix missing restart policies
                (r'(\s+image:\s+[^\n]+)', r'\1\n    restart: unless-stopped'),
                
                # Fix missing health checks
                (r'(\s+ports:\s+[^\n]+)', r'\1\n    healthcheck:\n      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]\n      interval: 30s\n      timeout: 10s\n      retries: 3'),
            ]
            
            for pattern, replacement in fixes:
                import re
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            with open(compose_file, 'w') as f:
                f.write(content)
            
            logger.info(f"Fixed Docker Compose configuration: {compose_file}")
            
        except Exception as e:
            logger.error(f"Error fixing Docker Compose config {compose_file}: {e}")
    
    def fix_nginx_config(self, nginx_file: str):
        """Fix Nginx configuration"""
        try:
            with open(nginx_file, 'r') as f:
                content = f.read()
            
            # Fix common Nginx issues
            fixes = [
                # Fix missing worker_processes
                (r'^events\s*{', 'worker_processes auto;\n\nevents {'),
                
                # Fix missing gzip settings
                (r'(\s+include\s+/etc/nginx/mime\.types;)', r'\1\n    \n    # Gzip compression\n    gzip on;\n    gzip_vary on;\n    gzip_min_length 1024;\n    gzip_proxied any;\n    gzip_comp_level 6;\n    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;'),
            ]
            
            for pattern, replacement in fixes:
                import re
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            with open(nginx_file, 'w') as f:
                f.write(content)
            
            logger.info(f"Fixed Nginx configuration: {nginx_file}")
            
        except Exception as e:
            logger.error(f"Error fixing Nginx config {nginx_file}: {e}")
    
    def fix_database_issues(self) -> bool:
        """Fix database issues"""
        logger.info("🔍 Fixing database issues...")
        
        try:
            # Start Redis if not running
            result = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.info("Starting Redis...")
                subprocess.run(['sudo', 'systemctl', 'start', 'redis-server'], check=True)
            
            # Start Qdrant if not running
            try:
                import requests
                response = requests.get('http://localhost:6333/health', timeout=5)
                if response.status_code != 200:
                    logger.info("Starting Qdrant...")
                    subprocess.run(['docker', 'run', '-d', '-p', '6333:6333', 'qdrant/qdrant'], check=True)
            except:
                logger.info("Starting Qdrant...")
                subprocess.run(['docker', 'run', '-d', '-p', '6333:6333', 'qdrant/qdrant'], check=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Error fixing database issues: {e}")
            return False
    
    def fix_service_issues(self) -> bool:
        """Fix service issues"""
        logger.info("🔍 Fixing service issues...")
        
        try:
            # Restart services
            services = ['docker', 'nginx', 'redis-server']
            
            for service in services:
                try:
                    subprocess.run(['sudo', 'systemctl', 'restart', service], check=True)
                    logger.info(f"Restarted service: {service}")
                except:
                    logger.warning(f"Could not restart service: {service}")
            
            # Restart Docker containers
            if os.path.exists('docker-compose.yml'):
                subprocess.run(['docker-compose', 'restart'], check=True)
                logger.info("Restarted Docker containers")
            
            return True
            
        except Exception as e:
            logger.error(f"Error fixing service issues: {e}")
            return False
    
    def generate_repair_report(self):
        """Generate repair report"""
        logger.info("📊 Generating repair report...")
        
        successful_repairs = len([r for r in self.repair_log if r['status'] == 'success'])
        failed_repairs = len([r for r in self.repair_log if r['status'] == 'failed'])
        error_repairs = len([r for r in self.repair_log if r['status'] == 'error'])
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_repairs': len(self.repair_log),
                'successful': successful_repairs,
                'failed': failed_repairs,
                'errors': error_repairs
            },
            'repair_log': self.repair_log,
            'recommendations': self.generate_recommendations()
        }
        
        # Save report
        with open('logs/system_repair_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📈 Repair Results Summary:")
        logger.info(f"   Total Repairs: {len(self.repair_log)}")
        logger.info(f"   Successful: {successful_repairs}")
        logger.info(f"   Failed: {failed_repairs}")
        logger.info(f"   Errors: {error_repairs}")
        
        if successful_repairs > 0:
            logger.info("🎉 System repair completed with improvements!")
        else:
            logger.warning("⚠️  System repair completed but no issues were fixed")
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on repair results"""
        recommendations = []
        
        failed_repairs = [r for r in self.repair_log if r['status'] == 'failed']
        error_repairs = [r for r in self.repair_log if r['status'] == 'error']
        
        if len(failed_repairs) > 0:
            recommendations.append("Review failed repairs and address manually")
        
        if len(error_repairs) > 0:
            recommendations.append("Check error logs and fix underlying issues")
        
        if len(self.repair_log) == 0:
            recommendations.append("No repairs were attempted - system may be healthy")
        
        recommendations.append("Run system health monitor to verify repairs")
        recommendations.append("Test API endpoints to ensure functionality")
        
        return recommendations

def main():
    """Main repair function"""
    logger.info("🚀 Starting system repair tool...")
    
    repair_tool = SystemRepairTool()
    repair_tool.run_full_repair()
    
    logger.info("✅ System repair tool completed")

if __name__ == "__main__":
    main()
