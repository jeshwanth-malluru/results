#!/usr/bin/env python3
"""
Test Firebase Connection and Batch Processing
"""

import os
import sys
import json
from datetime import datetime

def test_firebase_connection():
    """Test Firebase connection"""
    print("🔥 Testing Firebase Connection...")
    
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore, storage
        
        # Check if service account file exists
        if not os.path.exists('serviceAccount.json'):
            print("❌ serviceAccount.json not found!")
            print("💡 Please ensure your Firebase service account key is in the backend directory")
            return False
        
        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate('serviceAccount.json')
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'plant-ec218.firebasestorage.app'
                })
                print("✅ Firebase initialized successfully")
            except Exception as e:
                print(f"❌ Firebase initialization failed: {e}")
                return False
        else:
            print("✅ Firebase already initialized")
        
        # Test Firestore connection
        try:
            db = firestore.client()
            test_doc = db.collection('_connection_test').document('test')
            test_doc.set({
                'timestamp': firestore.SERVER_TIMESTAMP,
                'test': True,
                'message': 'Connection test from batch processor'
            })
            test_doc.delete()  # Clean up
            print("✅ Firestore connection successful")
        except Exception as e:
            print(f"❌ Firestore connection failed: {e}")
            return False
        
        # Test Storage connection
        try:
            bucket = storage.bucket()
            print("✅ Storage bucket connection successful")
        except Exception as e:
            print(f"⚠️ Storage bucket connection failed: {e}")
            print("ℹ️ This is OK - storage is optional for PDF processing")
        
        return True
        
    except ImportError as e:
        print(f"❌ Firebase SDK not installed: {e}")
        print("💡 Run: pip install firebase-admin")
        return False
    except Exception as e:
        print(f"❌ Firebase connection test failed: {e}")
        return False

def list_pdf_files():
    """List available PDF files"""
    print("\n📁 Scanning for PDF files...")
    
    pdf_files = []
    for filename in os.listdir('.'):
        if filename.lower().endswith('.pdf'):
            pdf_files.append(filename)
    
    if pdf_files:
        print(f"✅ Found {len(pdf_files)} PDF files:")
        for i, pdf in enumerate(pdf_files, 1):
            size = os.path.getsize(pdf) / (1024 * 1024)  # Size in MB
            print(f"   {i}. {pdf} ({size:.1f} MB)")
    else:
        print("❌ No PDF files found in current directory")
        print("💡 Please copy your JNTUK or Autonomous PDF files to this directory")
    
    return pdf_files

def detect_pdf_format(pdf_path):
    """Detect if PDF is JNTUK or Autonomous"""
    filename = os.path.basename(pdf_path).lower()
    
    jntuk_keywords = ['jntuk', 'b.tech', 'btech', 'jawaharlal nehru technological university']
    autonomous_keywords = ['autonomous', 'college', 'engineering', 'degree', 'affiliated']
    
    if any(keyword in filename for keyword in jntuk_keywords):
        return "JNTUK"
    elif any(keyword in filename for keyword in autonomous_keywords):
        return "Autonomous"
    else:
        return "Unknown (will try JNTUK parser)"

def main():
    """Main test function"""
    print("🚀 Firebase Connection & PDF Processing Test")
    print("=" * 50)
    
    # Test Firebase connection
    firebase_ok = test_firebase_connection()
    
    # List PDF files
    pdf_files = list_pdf_files()
    
    if pdf_files:
        print(f"\n📋 PDF Format Detection:")
        for pdf in pdf_files:
            format_type = detect_pdf_format(pdf)
            print(f"   📄 {pdf} → {format_type}")
    
    print(f"\n🎯 System Status:")
    print(f"   🔥 Firebase: {'✅ Connected' if firebase_ok else '❌ Failed'}")
    print(f"   📁 PDF Files: {'✅ Found' if pdf_files else '❌ None'}")
    
    if firebase_ok and pdf_files:
        print(f"\n🚀 Ready to process PDFs!")
        print(f"💡 Run: python batch_pdf_processor.py")
    elif firebase_ok:
        print(f"\n⚠️ Firebase ready but no PDFs found")
        print(f"💡 Copy your PDF files to this directory first")
    elif pdf_files:
        print(f"\n⚠️ PDFs found but Firebase not connected")
        print(f"💡 Check your serviceAccount.json file")
    else:
        print(f"\n❌ Setup required:")
        if not firebase_ok:
            print(f"   • Fix Firebase connection")
        if not pdf_files:
            print(f"   • Add PDF files to process")

if __name__ == "__main__":
    main()
