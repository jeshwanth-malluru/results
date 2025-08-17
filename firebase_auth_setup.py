#!/usr/bin/env python3
"""
Firebase Authentication User Management
Create and manage users for your Student Result System
"""

import firebase_admin
from firebase_admin import auth
from app import FIREBASE_AVAILABLE
import sys

def create_admin_user(email, password, display_name="Admin User"):
    """Create an admin user in Firebase Authentication"""
    
    if not FIREBASE_AVAILABLE:
        print("❌ Firebase is not available. Please check your configuration.")
        return False
    
    try:
        # Check if user already exists
        try:
            existing_user = auth.get_user_by_email(email)
            print(f"⚠️ User {email} already exists with UID: {existing_user.uid}")
            return True
        except auth.UserNotFoundError:
            pass  # User doesn't exist, we can create it
        
        # Create the user
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
            email_verified=True
        )
        
        print(f"✅ Successfully created user: {email}")
        print(f"   UID: {user.uid}")
        print(f"   Display Name: {display_name}")
        print(f"   Email Verified: True")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

def list_users():
    """List all users in Firebase Authentication"""
    
    if not FIREBASE_AVAILABLE:
        print("❌ Firebase is not available. Please check your configuration.")
        return
    
    try:
        # List all users
        page = auth.list_users()
        users = list(page.users)
        
        if not users:
            print("📭 No users found in Firebase Authentication")
            return
        
        print(f"👥 Found {len(users)} users in Firebase Authentication:")
        print("=" * 60)
        
        for user in users:
            print(f"📧 Email: {user.email}")
            print(f"   UID: {user.uid}")
            print(f"   Display Name: {user.display_name or 'Not set'}")
            print(f"   Email Verified: {user.email_verified}")
            print(f"   Created: {user.user_metadata.creation_timestamp}")
            print(f"   Last Sign In: {user.user_metadata.last_sign_in_timestamp or 'Never'}")
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")

def delete_user(email):
    """Delete a user from Firebase Authentication"""
    
    if not FIREBASE_AVAILABLE:
        print("❌ Firebase is not available. Please check your configuration.")
        return False
    
    try:
        # Get user by email
        user = auth.get_user_by_email(email)
        
        # Delete the user
        auth.delete_user(user.uid)
        
        print(f"✅ Successfully deleted user: {email}")
        return True
        
    except auth.UserNotFoundError:
        print(f"❌ User {email} not found")
        return False
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return False

def main():
    print("🔐 FIREBASE AUTHENTICATION USER MANAGEMENT")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python firebase_auth_setup.py create <email> <password> [display_name]")
        print("  python firebase_auth_setup.py list")
        print("  python firebase_auth_setup.py delete <email>")
        print("")
        print("Examples:")
        print("  python firebase_auth_setup.py create admin@scrreddy.edu.in admin123456 'Admin User'")
        print("  python firebase_auth_setup.py list")
        print("  python firebase_auth_setup.py delete admin@scrreddy.edu.in")
        return
    
    command = sys.argv[1].lower()
    
    if command == "create":
        if len(sys.argv) < 4:
            print("❌ Usage: python firebase_auth_setup.py create <email> <password> [display_name]")
            return
        
        email = sys.argv[2]
        password = sys.argv[3]
        display_name = sys.argv[4] if len(sys.argv) > 4 else "Admin User"
        
        print(f"Creating user: {email}")
        create_admin_user(email, password, display_name)
        
    elif command == "list":
        list_users()
        
    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ Usage: python firebase_auth_setup.py delete <email>")
            return
        
        email = sys.argv[2]
        confirm = input(f"⚠️ Are you sure you want to delete user {email}? (y/N): ")
        
        if confirm.lower() == 'y':
            delete_user(email)
        else:
            print("❌ Deletion cancelled")
            
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: create, list, delete")

if __name__ == "__main__":
    main()
