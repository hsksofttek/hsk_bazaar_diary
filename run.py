#!/usr/bin/env python3
"""
Startup script for the Business Management System Web Application
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app import create_app, init_db

def main():
    """Main startup function"""
    print("🚀 Starting Business Management System...")
    print("=" * 50)
    
    # Create the Flask application
    app = create_app()
    
    # Initialize database
    with app.app_context():
        print("📊 Initializing database...")
        init_db()
        print("✅ Database initialized successfully!")
    
    print("\n🌐 Starting web server...")
    print("📍 Application will be available at: http://localhost:5000")
    print("🔑 Default admin credentials: admin / admin123")
    print("\n" + "=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the application
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Business Management System...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 