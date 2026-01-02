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

from app import create_app
from database import db

def main():
    """Main startup function"""
    print("Starting Business Management System...")
    print("=" * 50)

    # Create the Flask application
    app = create_app()

    # Initialize database only when explicitly requested
    initialize_db = os.environ.get('INITIALIZE_DB', 'false').lower() == 'true'
    if initialize_db:
        with app.app_context():
            print("Initializing database (INITIALIZE_DB=true)...")
            db.create_all()
            print("Database initialized successfully.")
    else:
        print("Skipping automatic database creation (set INITIALIZE_DB=true to enable).")

    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'

    print(f"\nStarting web server on {host}:{port} (debug={debug})...")
    print("Default admin credentials: admin / admin123")
    print("\n" + "=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)

    # Run the application
    try:
        app.run(
            debug=debug,
            host=host,
            port=port,
            use_reloader=debug
        )
    except KeyboardInterrupt:
        print("\n\nShutting down Business Management System...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
