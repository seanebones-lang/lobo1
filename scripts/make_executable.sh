#!/bin/bash
# Make all troubleshooting scripts executable

echo "🔧 Making troubleshooting scripts executable..."

# Make Python scripts executable
chmod +x scripts/system_health_monitor.py
chmod +x scripts/test_api_endpoints.py
chmod +x scripts/system_repair_tool.py
chmod +x scripts/master_troubleshooter.py

# Make shell scripts executable
chmod +x scripts/setup.sh
chmod +x scripts/start_services.sh
chmod +x scripts/make_executable.sh

# Make deployment scripts executable
chmod +x deploy/droplet-setup.sh
chmod +x deploy/droplet-deploy.sh
chmod +x deploy/deploy-to-droplet.sh

echo "✅ All scripts are now executable!"
echo ""
echo "Available troubleshooting commands:"
echo "  python3 scripts/system_health_monitor.py     - Continuous health monitoring"
echo "  python3 scripts/test_api_endpoints.py        - Test all API endpoints"
echo "  python3 scripts/system_repair_tool.py        - Repair system issues"
echo "  python3 scripts/master_troubleshooter.py     - Master troubleshooter (all-in-one)"
echo ""
echo "🎯 THE ULTIMATE RAG TROUBLESHOOTER IS READY!"
