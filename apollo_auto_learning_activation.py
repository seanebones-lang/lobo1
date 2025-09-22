#!/usr/bin/env python3
"""
🚀 APOLLO AUTO-LEARNING ACTIVATION 🚀
Activate auto-learning and teach APOLLO about recent builds

Build By: NextEleven Studios - SFM 09-20-2025
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path

# Import the auto-learning system
try:
    from apollo_auto_learning_system import ApolloAutoLearningSystem, AutoLearningConfig
except ImportError:
    print("❌ Auto-learning system not found. Please ensure apollo_auto_learning_system.py is available.")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_learning_config():
    """Create optimized learning configuration"""
    return AutoLearningConfig(
        enabled=True,
        learning_interval=180,  # 3 minutes for faster learning
        max_builds_per_hour=20,
        watch_directories=[
            "/Users/seanmcdonnell/Desktop/Crowley Edition",
            "/Users/seanmcdonnell/Desktop/Tattoo App", 
            "/Users/seanmcdonnell/Desktop/NextEleven-Tattoo-Pro",
            "/Users/seanmcdonnell/Desktop/APOLLO 1.0.0",
            "/Users/seanmcdonnell/Desktop/Tattoo Template"
        ],
        ignore_patterns=[
            "node_modules", ".git", ".next", "__pycache__", 
            ".venv", "venv", ".env", "*.log", ".DS_Store"
        ],
        min_build_size=500,  # Smaller threshold for more learning
        learning_categories=[
            "web_app", "ai_system", "tattoo_shop", "crowley_edition",
            "documentation", "deployment", "nextjs_app"
        ]
    )

def teach_apollo_recent_builds():
    """Teach APOLLO about our recent builds"""
    print("🧠 TEACHING APOLLO ABOUT RECENT BUILDS 🧠")
    print("=" * 50)
    
    recent_builds = [
        {
            "name": "Crowley Edition - All Seeing Eye",
            "path": "/Users/seanmcdonnell/Desktop/Crowley Edition",
            "category": "tattoo_shop",
            "description": "Professional tattoo shop AI with All Seeing Eye chatbot, consciousness manipulation, and comprehensive documentation"
        },
        {
            "name": "Tattoo App - Original",
            "path": "/Users/seanmcdonnell/Desktop/Tattoo App", 
            "category": "web_app",
            "description": "Original tattoo shop application with revenue-generating features and occult theming"
        },
        {
            "name": "NextEleven Tattoo Pro",
            "path": "/Users/seanmcdonnell/Desktop/NextEleven-Tattoo-Pro",
            "category": "nextjs_app", 
            "description": "Clean professional Next.js tattoo application with hypnotic effects"
        },
        {
            "name": "APOLLO 1.0.0 System",
            "path": "/Users/seanmcdonnell/Desktop/APOLLO 1.0.0",
            "category": "ai_system",
            "description": "Complete APOLLO AI system with RAG, build memory, and consciousness manipulation"
        },
        {
            "name": "Tattoo Template",
            "path": "/Users/seanmcdonnell/Desktop/Tattoo Template",
            "category": "documentation",
            "description": "Complete documentation and deployment templates for tattoo shop AI systems"
        }
    ]
    
    auto_learning = ApolloAutoLearningSystem(create_learning_config())
    
    print("📚 Teaching APOLLO about builds...")
    for build in recent_builds:
        if os.path.exists(build["path"]):
            print(f"  🎯 Learning: {build['name']}")
            result = auto_learning.force_learn_build(build["path"])
            print(f"    ✅ {result}")
        else:
            print(f"  ⚠️ Path not found: {build['path']}")
    
    return auto_learning

def show_learning_status(auto_learning):
    """Show current learning status"""
    print("\n📊 APOLLO LEARNING STATUS 📊")
    print("=" * 30)
    
    status = auto_learning.get_learning_status()
    
    print(f"🧠 System ID: {status['system_id']}")
    print(f"⏰ Uptime: {status['uptime']:.1f} seconds")
    print(f"📈 Total Learned: {status['stats']['total_learned']}")
    print(f"✅ Successful: {status['stats']['successful_learns']}")
    print(f"❌ Failed: {status['stats']['failed_learns']}")
    print(f"📋 Queue Size: {status['queue_size']}")
    print(f"👁️ Watched Files: {status['watched_files_count']}")
    
    if status['stats']['categories_learned']:
        print("\n📚 Categories Learned:")
        for category, count in status['stats']['categories_learned'].items():
            print(f"  • {category}: {count} builds")
    
    if status['recent_builds']:
        print("\n🕒 Recent Builds:")
        for build in status['recent_builds'][-5:]:  # Last 5 builds
            print(f"  • {build['path']} ({build['category']})")

def create_learning_report(auto_learning):
    """Create a learning report"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"apollo_learning_report_{timestamp}.json"
        
        status = auto_learning.get_learning_status()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_id": status['system_id'],
            "learning_stats": status['stats'],
            "recent_builds": status['recent_builds'],
            "config": status['config'],
            "summary": {
                "total_builds_learned": status['stats']['total_learned'],
                "success_rate": (status['stats']['successful_learns'] / max(1, status['stats']['total_learned'])) * 100,
                "categories_discovered": len(status['stats']['categories_learned']),
                "auto_learning_active": status['is_learning']
            }
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Learning report saved: {report_file}")
        return report_file
        
    except Exception as e:
        logger.error(f"❌ Report creation failed: {e}")
        return None

def main():
    """Main activation function"""
    print("🚀 APOLLO AUTO-LEARNING ACTIVATION 🚀")
    print("=" * 50)
    print("Emergency Support: nextelenstudios@gmail.com")
    print()
    
    try:
        # Teach APOLLO about recent builds
        auto_learning = teach_apollo_recent_builds()
        
        # Show learning status
        show_learning_status(auto_learning)
        
        # Create learning report
        report_file = create_learning_report(auto_learning)
        
        # Start continuous auto-learning
        print(f"\n🔄 STARTING CONTINUOUS AUTO-LEARNING 🔄")
        print("=" * 40)
        
        if auto_learning.start_auto_learning():
            print("✅ Auto-learning activated successfully!")
            print("📁 Watching directories for new builds...")
            print("🧠 APOLLO will automatically learn from:")
            print("  • New project directories")
            print("  • File changes and updates") 
            print("  • Build configurations")
            print("  • Dependencies and scripts")
            print("\n⏰ Learning every 3 minutes")
            print("🔧 Emergency Support: nextelenstudios@gmail.com")
            print("\nPress Ctrl+C to stop auto-learning...")
            
            try:
                while True:
                    time.sleep(60)  # Check every minute
                    
                    # Show periodic status
                    status = auto_learning.get_learning_status()
                    if status['stats']['total_learned'] > 0:
                        print(f"\n📊 Status Update: {status['stats']['total_learned']} builds learned, "
                              f"{status['queue_size']} queued, "
                              f"{status['stats']['successful_learns']} successful")
                    
            except KeyboardInterrupt:
                print("\n🛑 Stopping auto-learning...")
                auto_learning.stop_auto_learning()
                
                # Final status
                final_status = auto_learning.get_learning_status()
                print(f"\n📊 FINAL STATUS:")
                print(f"  🧠 Total Builds Learned: {final_status['stats']['total_learned']}")
                print(f"  ✅ Successful: {final_status['stats']['successful_learns']}")
                print(f"  ❌ Failed: {final_status['stats']['failed_learns']}")
                print(f"  📚 Categories: {len(final_status['stats']['categories_learned'])}")
                
                if report_file:
                    print(f"  📄 Report: {report_file}")
                
                print("\n✅ Auto-learning stopped successfully")
                print("🧠 APOLLO has learned from all available builds!")
                
        else:
            print("❌ Failed to start auto-learning")
            
    except Exception as e:
        logger.error(f"❌ Auto-learning activation failed: {e}")
        print(f"❌ Error: {e}")
        print("🔧 Emergency Support: nextelenstudios@gmail.com")

if __name__ == "__main__":
    main()
