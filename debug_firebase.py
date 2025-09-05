#!/usr/bin/env python3
"""
Firebase Debug Script
Run this on the VM to diagnose Firebase initialization issues
"""

import sys
import os
import json

print("🔍 Firebase Debugging Script")
print("=" * 50)

# Check 1: Current working directory
print(f"📁 Current working directory: {os.getcwd()}")

# Check 2: Firebase config file exists
config_file = "firebase_admin_config.json"
if os.path.exists(config_file):
    print(f"✅ {config_file} exists")
    stat_info = os.stat(config_file)
    print(f"   Size: {stat_info.st_size} bytes")
    print(f"   Owner: UID {stat_info.st_uid}, GID {stat_info.st_gid}")
    print(f"   Permissions: {oct(stat_info.st_mode)[-3:]}")
else:
    print(f"❌ {config_file} NOT FOUND")
    print("   Files in current directory:")
    for f in os.listdir('.'):
        if f.endswith('.json'):
            print(f"     {f}")

# Check 3: Can read the file
try:
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    print(f"✅ Can read and parse {config_file}")
    print(f"   Project ID: {config_data.get('project_id', 'Not found')}")
    print(f"   Client email: {config_data.get('client_email', 'Not found')}")
except Exception as e:
    print(f"❌ Cannot read {config_file}: {e}")

# Check 4: Firebase Admin SDK installation
try:
    import firebase_admin
    print("✅ firebase-admin package is installed")
    print(f"   Version: {firebase_admin.__version__}")
except ImportError as e:
    print("❌ firebase-admin package is NOT installed")
    print(f"   Error: {e}")
    print("   Install with: pip install firebase-admin")

# Check 5: Try to import our Firebase module
try:
    sys.path.append('.')
    from firebase_push_notifications import initialize_firebase, FirebasePushNotificationManager
    print("✅ firebase_push_notifications module imports successfully")
except ImportError as e:
    print(f"❌ Cannot import firebase_push_notifications: {e}")

# Check 6: Try to initialize Firebase
if os.path.exists(config_file):
    try:
        from firebase_admin import credentials
        cred = credentials.Certificate(config_file)
        print("✅ Firebase credentials loaded successfully")
        
        # Try to initialize (this might fail if already initialized)
        try:
            import firebase_admin
            # Delete any existing app first
            try:
                firebase_admin.delete_app(firebase_admin.get_app())
            except:
                pass
            
            app = firebase_admin.initialize_app(cred)
            print("✅ Firebase app initialized successfully")
            print(f"   App name: {app.name}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("⚠️  Firebase app already initialized (this is okay)")
            else:
                print(f"❌ Firebase initialization failed: {e}")
                
    except Exception as e:
        print(f"❌ Firebase credentials error: {e}")

# Check 7: Network connectivity
try:
    import urllib.request
    urllib.request.urlopen('https://google.com', timeout=5)
    print("✅ Network connectivity is working")
except Exception as e:
    print(f"❌ Network connectivity issue: {e}")

# Check 8: Python version
print(f"🐍 Python version: {sys.version}")

print("\n" + "=" * 50)
print("🎯 Debug Summary Complete")
print("Run this script with: python3 debug_firebase.py")