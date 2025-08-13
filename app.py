import os
import secrets
import logging
import traceback
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, render_template, session, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename

# -----------------------------------------------------------------------------
# Logging setup
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Setup Python Magic for file type checking
# -----------------------------------------------------------------------------
import magic  # Make sure you have python-magic-bin installed (on Windows)

# Initialize Firebase before importing blueprints
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Check if Firebase is already initialized
if not firebase_admin._apps:
    try:
        # Try to load service account
        if os.path.exists('serviceAccount.json'):
            cred = credentials.Certificate('serviceAccount.json')
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'plant-ec218.firebasestorage.app'
            })
            logger.info("Firebase initialized with service account")
        else:
            logger.warning("serviceAccount.json not found - Firebase features disabled")
    except Exception as e:
        logger.warning(f"Firebase initialization failed: {e} - Disabling Firebase features")
        # Set Firebase as unavailable if there's any error during initialization
        firebase_admin._apps.clear() if hasattr(firebase_admin, '_apps') else None

# Import Blueprints (after Firebase initialization)
from notices import notices

# Import your PDF parsers here (you must define these yourself)
from parser.parser_jntuk import parse_jntuk_pdf
from parser.parser_autonomous import parse_autonomous_pdf

# -----------------------------------------------------------------------------
# Flask app setup
# -----------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Required for sessions
CORS(app)  # Enable CORS for all routes
app.register_blueprint(notices)

@app.route('/')
def index():
    try:
        # Check if user is authenticated
        if 'user_token' not in session:
            return redirect(url_for('admin_login'))
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return jsonify({"error": "Failed to load index"}), 500

@app.route('/dashboard')
def dashboard():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return jsonify({"error": "Failed to load dashboard"}), 500

# Firebase configuration for frontend
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyBYY_k5TK-OaQnkc82w-lxJ54bJGqcWZI4",
    "authDomain": "plant-ec218.firebaseapp.com", 
    "projectId": "plant-ec218",
    "storageBucket": "plant-ec218.appspot.com",
    "messagingSenderId": "451074734549",
    "appId": "1:451074734549:web:abc123def456"
}

@app.route('/admin')
def admin_login():
    try:
        # Check if forced login or logout parameter
        force_login = request.args.get('force') == 'true'
        
        # Check if already authenticated (unless forced)
        if 'user_token' in session and not force_login:
            return redirect(url_for('index'))
        return render_template('login.html', firebase_config=FIREBASE_CONFIG)
    except Exception as e:
        logger.error(f"Error rendering login page: {e}")
        return jsonify({"error": "Failed to load login page"}), 500

@app.route('/api/auth/login', methods=['POST'])
def simple_login():
    """Simple login for testing without Firebase"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # Simple demo credentials
        if email == "admin@scrreddy.edu.in" and password == "admin123456":
            session['user_token'] = "demo_token_" + email
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify_auth():
    """Verify Firebase token and create session"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'error': 'No token provided'}), 400
        
        # In a real app, verify the Firebase token here
        # For demo purposes, we'll just store it in session
        session['user_token'] = id_token
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Auth verification error: {e}")
        return jsonify({'error': 'Authentication failed'}), 401

@app.route('/logout')
def logout():
    """Logout user and clear session"""
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    try:
        # Check if user is authenticated
        if 'user_token' not in session:
            return redirect(url_for('admin_login'))
        return render_template('admin/dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering admin dashboard: {e}")
        return jsonify({"error": "Failed to load admin dashboard"}), 500

@app.route('/upload')
def upload_page():
    try:
        # Check if user is authenticated
        if 'user_token' not in session:
            return redirect(url_for('admin_login'))
        return render_template('upload.html')
    except Exception as e:
        logger.error(f"Error rendering upload page: {e}")
        return jsonify({"error": "Failed to load upload page"}), 500

@app.route('/student-search')
def student_search_page():
    try:
        # Check if user is authenticated
        if 'user_token' not in session:
            return redirect(url_for('admin_login'))
        return render_template('student_search.html')
    except Exception as e:
        logger.error(f"Error rendering student search page: {e}")
        return jsonify({"error": "Failed to load student search page"}), 500

@app.route('/api/firebase-status')
def firebase_status():
    """API endpoint to check Firebase connection status"""
    try:
        status = {
            "available": FIREBASE_AVAILABLE,
            "firestore": False,
            "storage": False,
            "error": None
        }
        
        if FIREBASE_AVAILABLE and db:
            try:
                # Quick test of Firestore connection
                test_ref = db.collection('_connection_test').document('test')
                test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP, 'test': True})
                test_ref.delete()  # Clean up
                status["firestore"] = True
            except Exception as e:
                logger.warning(f"Firestore connection test failed: {e}")
                status["error"] = f"Firestore: {str(e)}"
        
        if FIREBASE_AVAILABLE and bucket:
            try:
                # Test storage bucket access
                bucket.get_blob('test') or True  # Just test access, don't create anything
                status["storage"] = True
            except Exception as e:
                logger.warning(f"Storage connection test failed: {e}")
                if not status["error"]:
                    status["error"] = f"Storage: {str(e)}"
                else:
                    status["error"] += f" | Storage: {str(e)}"
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error checking Firebase status: {e}")
        return jsonify({
            "available": False,
            "firestore": False,
            "storage": False,
            "error": str(e)
        })



# -----------------------------------------------------------------------------
# Firebase variables and setup
# -----------------------------------------------------------------------------
try:
    # Only initialize Firebase clients if Firebase is properly initialized
    if firebase_admin._apps:
        db = firestore.client()
        bucket = storage.bucket()
        FIREBASE_AVAILABLE = True
        logger.info("Firebase Firestore and Storage clients initialized")
    else:
        raise Exception("Firebase not initialized")
except Exception as e:
    logger.warning(f"Firebase client initialization failed: {e} - Running without Firebase")
    db = None
    bucket = None
    FIREBASE_AVAILABLE = False

# -----------------------------------------------------------------------------
# Firebase helper functions
# -----------------------------------------------------------------------------
def save_to_firebase(student_results, year, semesters, exam_types, format_type, doc_id, upload_id=None):
    """Save parsed results to Firebase Firestore with progress tracking"""
    if not FIREBASE_AVAILABLE or not db:
        logger.warning("Firebase not available - skipping Firebase upload")
        if upload_id:
            update_progress(upload_id, "firebase_disabled", firebase={"status": "disabled", "message": "Firebase not available"})
        return 0
    
    if upload_id:
        update_progress(upload_id, "firebase_uploading", firebase={"status": "uploading", "progress": 0, "batches": 0, "students_saved": 0})
    
    students_saved = 0
    students_skipped = 0
    batch = db.batch()
    batch_count = 0
    batch_number = 0
    MAX_BATCH_SIZE = 500
    total_students = len(student_results)
    
    try:
        for i, student_data in enumerate(student_results):
            student_id = student_data.get('student_id', '')
            if not student_id:
                continue
            
            # Detect semester from student data
            detected_semester = student_data.get('semester', semesters[0] if semesters else 'Unknown')
            detected_exam_type = exam_types[0] if exam_types else 'regular'
            
            # Create unique document ID
            student_doc_id = f"{student_id}_{year.replace(' ', '_')}_{detected_semester.replace(' ', '_')}_{detected_exam_type}"
            
            # Check for duplicates (with option to skip duplicate checking for fresh uploads)
            try:
                existing_doc = db.collection('student_results').document(student_doc_id).get()
                if existing_doc.exists:
                    students_skipped += 1
                    # Log first few duplicates to help user understand
                    if students_skipped <= 5:
                        logger.info(f"Duplicate found: {student_id} already exists in database")
                    elif students_skipped == 6:
                        logger.info(f"... and {total_students - i} more duplicates (suppressing further duplicate logs)")
                    continue
            except Exception as e:
                # Handle Firebase authentication errors gracefully
                if "invalid_grant" in str(e).lower() or "jwt signature" in str(e).lower():
                    logger.error(f"Firebase authentication error: {e}")
                    if upload_id:
                        update_progress(upload_id, "firebase_auth_error", firebase={"status": "auth_error", "message": "Firebase authentication failed - invalid service account key"})
                    return 0
                logger.warning(f"Error checking duplicate for {student_id}: {e}")
                continue
            
            # Create a copy for Firebase to avoid modifying original data
            firebase_student_data = student_data.copy()
            firebase_student_data.update({
                'year': year,
                'semester': detected_semester,
                'examType': detected_exam_type,
                'availableSemesters': semesters,
                'availableExamTypes': exam_types,
                'format': format_type,
                'uploadId': doc_id,
                'attempts': 0,
                'uploadedAt': firestore.SERVER_TIMESTAMP,
                'supplyExamTypes': [],
                'isSupplyOnly': False
            })
            
            # Add to batch
            student_ref = db.collection('student_results').document(student_doc_id)
            batch.set(student_ref, firebase_student_data)
            students_saved += 1
            batch_count += 1
            
            # Commit batch when reaching limit
            if batch_count >= MAX_BATCH_SIZE:
                try:
                    batch.commit()
                    batch_number += 1
                    logger.info(f"Committed Firebase batch {batch_number}: {batch_count} records")
                    
                    # Update progress
                    if upload_id:
                        progress = (i + 1) / total_students * 100
                        update_progress(upload_id, "firebase_uploading", firebase={
                            "status": "uploading",
                            "progress": progress,
                            "batches": batch_number,
                            "students_saved": students_saved,
                            "total_students": total_students,
                            "message": f"Batch {batch_number} uploaded: {students_saved} students saved"
                        })
                    
                    batch = db.batch()
                    batch_count = 0
                except Exception as e:
                    # Handle Firebase authentication errors gracefully
                    if "invalid_grant" in str(e).lower() or "jwt signature" in str(e).lower():
                        logger.error(f"Firebase authentication error during batch commit: {e}")
                        if upload_id:
                            update_progress(upload_id, "firebase_auth_error", firebase={"status": "auth_error", "message": "Firebase authentication failed during upload"})
                        return students_saved - batch_count
                    logger.error(f"Error committing Firebase batch: {e}")
                    batch = db.batch()
                    batch_count = 0
                    students_saved -= batch_count
        
        # Commit remaining records
        if batch_count > 0:
            try:
                batch.commit()
                batch_number += 1
                logger.info(f"Committed final Firebase batch {batch_number}: {batch_count} records")
            except Exception as e:
                # Handle Firebase authentication errors gracefully
                if "invalid_grant" in str(e).lower() or "jwt signature" in str(e).lower():
                    logger.error(f"Firebase authentication error during final batch commit: {e}")
                    if upload_id:
                        update_progress(upload_id, "firebase_auth_error", firebase={"status": "auth_error", "message": "Firebase authentication failed during final upload"})
                    return students_saved - batch_count
                logger.error(f"Error committing final Firebase batch: {e}")
                students_saved -= batch_count
        
        logger.info(f"Firebase upload complete: {students_saved} saved, {students_skipped} skipped")
        
        # Update final progress
        if upload_id:
            update_progress(upload_id, "firebase_complete", firebase={
                "status": "completed",
                "progress": 100,
                "batches": batch_number,
                "students_saved": students_saved,
                "students_skipped": students_skipped,
                "total_students": total_students,
                "message": f"Firebase upload complete: {students_saved} saved, {students_skipped} duplicates skipped"
            })
        
        return students_saved
        
    except Exception as e:
        # Handle Firebase authentication errors gracefully
        if "invalid_grant" in str(e).lower() or "jwt signature" in str(e).lower():
            logger.error(f"Firebase authentication error: {e}")
            if upload_id:
                update_progress(upload_id, "firebase_auth_error", firebase={"status": "auth_error", "message": "Firebase authentication failed - service account key may be invalid or expired"})
        else:
            logger.error(f"Firebase upload error: {e}")
            if upload_id:
                update_progress(upload_id, "firebase_error", firebase={"status": "error", "message": str(e)})
        return 0

def upload_pdf_to_storage(file, filename):
    """Upload PDF file to Firebase Storage"""
    if not FIREBASE_AVAILABLE or not bucket:
        logger.warning("Firebase Storage not available - skipping file upload")
        return None
    
    try:
        file.seek(0)
        blob = bucket.blob(filename)
        content = file.read()
        
        blob.upload_from_string(content, content_type='application/pdf')
        blob.make_public()
        
        logger.info(f"PDF uploaded to Firebase Storage: {filename}")
        return blob.public_url
    except Exception as e:
        # Handle Firebase authentication errors gracefully
        if "invalid_grant" in str(e).lower() or "jwt signature" in str(e).lower():
            logger.error(f"Firebase Storage authentication error: {e}")
            logger.error("Service account key may be invalid or expired")
        else:
            logger.error(f"Error uploading PDF to storage: {e}")
        return None

# -----------------------------------------------------------------------------
# Progress tracking for upload operations
# -----------------------------------------------------------------------------
upload_progress = {}

@app.route('/api/upload-progress/<upload_id>', methods=['GET'])
def get_upload_progress(upload_id):
    """Get real-time upload progress"""
    progress = upload_progress.get(upload_id, {
        "status": "not_found",
        "message": "Upload not found"
    })
    return jsonify(progress)

def update_progress(upload_id, status, **kwargs):
    """Update progress for an upload"""
    if upload_id not in upload_progress:
        upload_progress[upload_id] = {
            "status": "starting",
            "timestamp": time.time(),
            "parsing": {"status": "pending", "progress": 0},
            "firebase": {"status": "pending", "progress": 0, "batches": 0, "students_saved": 0},
            "storage": {"status": "pending"},
            "json": {"status": "pending"}
        }
    
    upload_progress[upload_id]["status"] = status
    upload_progress[upload_id]["timestamp"] = time.time()
    
    for key, value in kwargs.items():
        if key in upload_progress[upload_id]:
            if isinstance(upload_progress[upload_id][key], dict) and isinstance(value, dict):
                upload_progress[upload_id][key].update(value)
            else:
                upload_progress[upload_id][key] = value

# -----------------------------------------------------------------------------
# API key setup for authorization (store keys safely in production!)
# -----------------------------------------------------------------------------
VALID_API_KEYS = {"my-very-secret-admin-api-key"}

def require_api_key(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if key not in VALID_API_KEYS:
            return jsonify({'error': 'Unauthorized'}), 401
        return func(*args, **kwargs)
    return wrapper

# -----------------------------------------------------------------------------
# File validation class
# -----------------------------------------------------------------------------
class PDFValidator:
    MAX_SIZE = 50 * 1024 * 1024  # 50 MB
    MIN_SIZE = 128  # Accept very tiny PDFs for testing

    @staticmethod
    def validate_file(file):
        """Validates that the file is a valid PDF"""
        if not file or not file.filename:
            return False, "No file provided"
            
        if not file.filename.lower().endswith('.pdf'):
            return False, "Only PDF files are allowed"
            
        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        if size > PDFValidator.MAX_SIZE:
            return False, f"File too large. Maximum size is {PDFValidator.MAX_SIZE / 1024 / 1024}MB"
            
        if size < PDFValidator.MIN_SIZE:
            return False, "File too small or possibly corrupted"
            
        # Check PDF header
        header = file.read(1024)
        file.seek(0)
        
        if not header.startswith(b'%PDF-'):
            return False, "Invalid PDF file format"
            
        return True, None

# -----------------------------------------------------------------------------
# Secure temp file path helper
# -----------------------------------------------------------------------------
def secure_file_handling(file):
    if not file.filename:
        raise ValueError("No filename provided.")
    safe_name = secure_filename(file.filename)
    if not safe_name:
        raise ValueError("Invalid filename.")
    ext = Path(safe_name).suffix.lower()
    unique_filename = f"{secrets.token_hex(16)}{ext}"
    temp_dir = Path("temp").resolve()
    temp_dir.mkdir(exist_ok=True)
    secure_path = temp_dir / unique_filename
    if not str(secure_path).startswith(str(temp_dir)):
        raise ValueError("Security violation: Path traversal detected.")
    return str(secure_path), unique_filename

# -----------------------------------------------------------------------------
# Custom application error for consistent JSON error results
# -----------------------------------------------------------------------------
class AppError(Exception):
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

@app.errorhandler(AppError)
def handle_app_error(error):
    logger.error(f"AppError: {error.message}")
    return jsonify({'error': error.message}), error.status_code

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled Exception: {e}\n{traceback.format_exc()}")
    return jsonify({'error': 'Internal server error'}), 500

# -----------------------------------------------------------------------------
# Serve favicon.ico to avoid browser console 404s
# -----------------------------------------------------------------------------
@app.route('/favicon.ico')
def favicon():
    path = os.path.join(app.root_path, 'static')
    return send_from_directory(path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# -----------------------------------------------------------------------------
# View saved JSON files endpoint
# -----------------------------------------------------------------------------
@app.route('/data-files', methods=['GET'])
def list_data_files():
    try:
        data_dir = Path("data")
        if not data_dir.exists():
            return jsonify({"files": [], "message": "No data directory found"}), 200
            
        json_files = []
        for file_path in data_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    file_info = {
                        "filename": file_path.name,
                        "size": file_path.stat().st_size,
                        "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                        "metadata": data.get("metadata", {}),
                        "firebase_status": data.get("firebase_status", {})
                    }
                    json_files.append(file_info)
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
        
        json_files.sort(key=lambda x: x["created"], reverse=True)
        return jsonify({"files": json_files}), 200
    except Exception as e:
        logger.error(f"Error listing data files: {e}")
        return jsonify({"error": "Failed to list data files"}), 500

@app.route('/data-files/<filename>', methods=['GET'])
def get_data_file(filename):
    try:
        file_path = Path("data") / filename
        if not file_path.exists() or not filename.endswith('.json'):
            return jsonify({"error": "File not found"}), 404
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error reading data file {filename}: {e}")
        return jsonify({"error": "Failed to read data file"}), 500

# -----------------------------------------------------------------------------
# Helper function to extract year and semester from semester string
# -----------------------------------------------------------------------------
def extract_year_sem_from_semester(semester_str):
    """
    Extract year and semester from semester string
    Examples:
    - "II B.Tech I Semester" -> year="2", sem="1"
    - "III B.Tech II Semester" -> year="3", sem="2"
    - "1-1" -> year="1", sem="1"
    - "2-2" -> year="2", sem="2"
    """
    try:
        semester_str = semester_str.strip().lower()
        
        # Handle format like "1-1", "2-2", etc.
        if '-' in semester_str and len(semester_str.split('-')) == 2:
            parts = semester_str.split('-')
            return parts[0], parts[1]
        
        # Handle format like "II B.Tech I Semester"
        # Roman numeral mapping
        roman_to_num = {
            'i': '1', 'ii': '2', 'iii': '3', 'iv': '4', 'v': '5',
            'vi': '6', 'vii': '7', 'viii': '8', 'ix': '9', 'x': '10'
        }
        
        # Extract year (first roman numeral before "b.tech")
        year = "unknown"
        sem = "unknown"
        
        words = semester_str.split()
        for i, word in enumerate(words):
            if word in roman_to_num:
                if i + 1 < len(words) and words[i + 1] == 'b.tech':
                    year = roman_to_num[word]
                elif 'semester' in words and word in roman_to_num:
                    # This might be the semester part
                    if year != "unknown":  # We already found year
                        sem = roman_to_num[word]
                    else:
                        # If no year found yet, this might be year
                        year = roman_to_num[word]
        
        # If we found year but not semester, try to find semester
        if year != "unknown" and sem == "unknown":
            for word in words:
                if word in roman_to_num and roman_to_num[word] != year:
                    sem = roman_to_num[word]
                    break
        
        # Default values if parsing fails
        if year == "unknown":
            year = "1"
        if sem == "unknown":
            sem = "1"
            
        return year, sem
        
    except Exception as e:
        logger.warning(f"Failed to parse semester '{semester_str}': {e}")
        return "1", "1"  # Default fallback

# -----------------------------------------------------------------------------
# Student Results Query Functions
# -----------------------------------------------------------------------------
def get_student_results(student_id, semester=None, exam_type=None, format_type=None):
    """Get student results from JSON files"""
    results = []
    data_dir = Path("data")
    
    if not data_dir.exists():
        return {"error": None, "data": []}
        
    for json_file in data_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                file_format = data.get("metadata", {}).get("format", "").lower()
                file_exam_type = data.get("metadata", {}).get("exam_type", "").lower()
                
                # Filter by format and exam type if specified
                if (format_type and file_format != format_type.lower()) or \
                   (exam_type and file_exam_type != exam_type.lower()):
                    continue
                
                # Filter students by ID and semester
                for student in data.get("students", []):
                    if student.get("student_id") == student_id:
                        if not semester or student.get("semester") == semester:
                            # Add source file info
                            student["source_file"] = json_file.name
                            results.append(student)
        except Exception as e:
            logger.warning(f"Could not read {json_file}: {e}")
    
    return {"error": None, "data": results}

def get_all_students_by_semester(semester, exam_type=None, format_type=None):
    """Get all students for a specific semester from JSON files"""
    results = []
    data_dir = Path("data")
    
    if not data_dir.exists():
        return {"error": None, "data": []}
        
    for json_file in data_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                file_format = data.get("metadata", {}).get("format", "").lower()
                file_exam_type = data.get("metadata", {}).get("exam_type", "").lower()
                
                # Filter by format and exam type if specified
                if (format_type and file_format != format_type.lower()) or \
                   (exam_type and file_exam_type != exam_type.lower()):
                    continue
                
                # Filter students by semester
                for student in data.get("students", []):
                    if student.get("semester") == semester:
                        # Add source file info
                        student["source_file"] = json_file.name
                        results.append(student)
        except Exception as e:
            logger.warning(f"Could not read {json_file}: {e}")
    
    return {"error": None, "data": results}

# -----------------------------------------------------------------------------
# Student Results API Endpoints
# -----------------------------------------------------------------------------
@app.route('/students/<student_id>/results', methods=['GET'])
def get_student_results_api(student_id):
    """Get results for a specific student"""
    try:
        semester = request.args.get('semester')
        exam_type = request.args.get('exam_type')
        format_type = request.args.get('format')
        
        result = get_student_results(student_id, semester, exam_type, format_type)
        
        if result["error"]:
            return jsonify({"error": result["error"]}), 500
        
        return jsonify({
            "student_id": student_id,
            "results": result["data"],
            "count": len(result["data"])
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_student_results_api: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/results/semester/<semester>', methods=['GET'])
def get_semester_results_api(semester):
    """Get all students results for a specific semester"""
    try:
        exam_type = request.args.get('exam_type')
        format_type = request.args.get('format')
        
        result = get_all_students_by_semester(semester, exam_type, format_type)
        
        if result["error"]:
            return jsonify({"error": result["error"]}), 500
        
        return jsonify({
            "semester": semester,
            "results": result["data"],
            "count": len(result["data"])
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_semester_results_api: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/results/semesters', methods=['GET'])
def get_available_semesters():
    """Get list of available semesters from JSON files"""
    try:
        # Get unique semesters from all JSON files
        semesters = set()
        data_dir = Path("data")
        if not data_dir.exists():
            return jsonify({"semesters": [], "count": 0}), 200
            
        for json_file in data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for student in data.get("students", []):
                        if "semester" in student:
                            semesters.add(student["semester"])
            except Exception as e:
                logger.warning(f"Could not read {json_file}: {e}")
        
        return jsonify({
            "semesters": sorted(list(semesters)),
            "count": len(semesters)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting available semesters: {e}")
        return jsonify({"error": "Internal server error"}), 500

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Firebase-based Student Results API Endpoints
# -----------------------------------------------------------------------------
@app.route('/api/students/<student_id>/results', methods=['GET'])
def get_student_results_from_firebase(student_id):
    """Get results for a specific student from Firebase Firestore"""
    try:
        if not FIREBASE_AVAILABLE or not db:
            return jsonify({"error": "Firebase not available"}), 503
        
        # Get query parameters
        semester = request.args.get('semester')
        year = request.args.get('year')
        exam_type = request.args.get('exam_type')
        limit = int(request.args.get('limit', 50))  # Default limit to 50 results
        
        # Start with basic query
        query = db.collection('student_results').where('student_id', '==', student_id)
        
        # Add filters if provided
        if semester:
            query = query.where('semester', '==', semester)
        if year:
            query = query.where('year', '==', year)
        if exam_type:
            query = query.where('exam_type', '==', exam_type)
        
        # Execute query with limit
        docs = query.limit(limit).stream()
        
        results = []
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['document_id'] = doc.id
            results.append(doc_data)
        
        return jsonify({
            "student_id": student_id,
            "results": results,
            "count": len(results),
            "filters": {
                "semester": semester,
                "year": year,
                "exam_type": exam_type,
                "limit": limit
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching student results from Firebase: {e}")
        return jsonify({"error": f"Failed to fetch results: {str(e)}"}), 500

@app.route('/api/students/search', methods=['GET'])
def search_students_from_firebase():
    """Search students by various criteria from Firebase Firestore"""
    try:
        if not FIREBASE_AVAILABLE or not db:
            return jsonify({"error": "Firebase not available"}), 503
        
        # Get query parameters
        student_name = request.args.get('name')
        student_id = request.args.get('student_id')
        semester = request.args.get('semester')
        year = request.args.get('year')
        exam_type = request.args.get('exam_type')
        min_sgpa = request.args.get('min_sgpa')
        max_sgpa = request.args.get('max_sgpa')
        limit = int(request.args.get('limit', 50))
        deduplicate = request.args.get('deduplicate', 'true').lower() == 'true'
        
        # Start with the collection
        query = db.collection('student_results')
        
        # Build query based on parameters
        if student_id:
            query = query.where('student_id', '==', student_id)
        if semester:
            query = query.where('semester', '==', semester)
        if year:
            query = query.where('year', '==', year)
        if exam_type:
            query = query.where('exam_type', '==', exam_type)
        if min_sgpa:
            try:
                query = query.where('sgpa', '>=', float(min_sgpa))
            except ValueError:
                pass
        if max_sgpa:
            try:
                query = query.where('sgpa', '<=', float(max_sgpa))
            except ValueError:
                pass
        
        # Execute query
        docs = query.limit(limit).stream()
        
        results = []
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['document_id'] = doc.id
            
            # Filter by name if provided (Firestore doesn't support case-insensitive contains)
            if student_name:
                name_in_doc = doc_data.get('student_name', '').lower()
                if student_name.lower() not in name_in_doc:
                    continue
            
            results.append(doc_data)
        
        # Deduplicate and consolidate results if requested (especially for student ID searches)
        if deduplicate and student_id:
            results = consolidate_student_records(results)
        elif deduplicate:
            results = remove_duplicate_students(results)
        
        return jsonify({
            "results": results,
            "count": len(results),
            "search_criteria": {
                "name": student_name,
                "student_id": student_id,
                "semester": semester,
                "year": year,
                "exam_type": exam_type,
                "min_sgpa": min_sgpa,
                "max_sgpa": max_sgpa,
                "limit": limit,
                "deduplicated": deduplicate
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching students in Firebase: {e}")
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

def consolidate_student_records(records):
    """Consolidate multiple records for the same student into a single comprehensive record"""
    if not records:
        return []
    
    # Group records by student_id
    student_groups = {}
    for record in records:
        student_id = record.get('student_id')
        if student_id:
            if student_id not in student_groups:
                student_groups[student_id] = []
            student_groups[student_id].append(record)
    
    consolidated_results = []
    
    for student_id, student_records in student_groups.items():
        if not student_records:
            continue
            
        # Sort records by semester and upload date for logical ordering
        student_records.sort(key=lambda x: (
            x.get('semester', 'Semester 0'),
            x.get('upload_date', ''),
            x.get('examType', x.get('exam_type', 'regular'))
        ))
        
        # Create consolidated record starting with the most recent/complete record
        base_record = student_records[-1].copy()
        
        # Consolidate all subject grades from all semesters
        all_subjects = []
        all_semesters = set()
        all_exam_types = set()
        total_credits = 0
        sgpa_records = []
        
        for record in student_records:
            semester = record.get('semester', 'Unknown')
            exam_type = record.get('examType', record.get('exam_type', 'regular'))
            sgpa = record.get('sgpa', 0)
            
            all_semesters.add(semester)
            all_exam_types.add(exam_type)
            
            if sgpa and sgpa > 0:
                sgpa_records.append({
                    'semester': semester,
                    'sgpa': sgpa,
                    'exam_type': exam_type
                })
            
            # Add subjects with semester and exam type context
            subjects = record.get('subjectGrades', [])
            for subject in subjects:
                subject_with_context = subject.copy()
                subject_with_context['semester'] = semester
                subject_with_context['exam_type'] = exam_type
                all_subjects.append(subject_with_context)
                total_credits += subject.get('credits', 0)
        
        # Remove duplicate subjects (same code in same semester)
        unique_subjects = []
        seen_combinations = set()
        
        for subject in all_subjects:
            key = (
                subject.get('code', ''),
                subject.get('semester', ''),
                subject.get('exam_type', '')
            )
            if key not in seen_combinations:
                seen_combinations.add(key)
                unique_subjects.append(subject)
        
        # Calculate overall statistics
        total_sgpa_points = sum(record.get('sgpa', 0) for record in sgpa_records)
        avg_sgpa = round(total_sgpa_points / len(sgpa_records), 2) if sgpa_records else 0
        
        # Update the consolidated record
        base_record.update({
            'subjectGrades': unique_subjects,
            'totalCredits': total_credits,
            'consolidatedSGPA': avg_sgpa,
            'semesterData': sgpa_records,
            'allSemesters': sorted(list(all_semesters)),
            'allExamTypes': sorted(list(all_exam_types)),
            'recordCount': len(student_records),
            'consolidatedRecord': True,
            'lastUpdated': max(record.get('upload_date', '') for record in student_records),
            'totalSubjects': len(unique_subjects)
        })
        
        # Set display semester to show range if multiple
        if len(all_semesters) > 1:
            sem_numbers = []
            for sem in all_semesters:
                try:
                    # Extract number from "Semester X" format
                    if 'Semester' in sem:
                        num = int(sem.split()[-1])
                        sem_numbers.append(num)
                except:
                    pass
            
            if sem_numbers:
                sem_numbers.sort()
                base_record['semester'] = f"Semesters {min(sem_numbers)}-{max(sem_numbers)}"
            else:
                base_record['semester'] = f"Multiple Semesters ({len(all_semesters)})"
        
        consolidated_results.append(base_record)
    
    return consolidated_results

def remove_duplicate_students(records):
    """Remove duplicate student records, keeping the most recent/complete one"""
    if not records:
        return []
    
    # Group by student_id
    student_groups = {}
    for record in records:
        student_id = record.get('student_id')
        if student_id:
            if student_id not in student_groups:
                student_groups[student_id] = []
            student_groups[student_id].append(record)
    
    unique_results = []
    
    for student_id, student_records in student_groups.items():
        if not student_records:
            continue
            
        # Sort by completeness and recency
        def record_score(record):
            score = 0
            # Prefer records with more subjects
            score += len(record.get('subjectGrades', [])) * 100
            # Prefer records with SGPA
            if record.get('sgpa', 0) > 0:
                score += 50
            # Prefer more recent uploads
            upload_date = record.get('upload_date', '')
            if upload_date:
                try:
                    # Simple date scoring (more recent = higher)
                    score += int(upload_date.replace('-', '')) / 100000000
                except:
                    pass
            return score
        
        # Keep the best record for each student
        best_record = max(student_records, key=record_score)
        best_record['duplicatesRemoved'] = len(student_records) - 1
        unique_results.append(best_record)
    
    return unique_results

@app.route('/api/results/statistics', methods=['GET'])
def get_results_statistics():
    """Get overall statistics from Firebase Firestore"""
    try:
        if not FIREBASE_AVAILABLE or not db:
            return jsonify({"error": "Firebase not available"}), 503
        
        # Get query parameters
        semester = request.args.get('semester')
        year = request.args.get('year')
        exam_type = request.args.get('exam_type')
        
        # Start with the collection
        query = db.collection('student_results')
        
        # Add filters if provided
        if semester:
            query = query.where('semester', '==', semester)
        if year:
            query = query.where('year', '==', year)
        if exam_type:
            query = query.where('exam_type', '==', exam_type)
        
        # Get all documents (be careful with large datasets)
        docs = list(query.stream())
        
        if not docs:
            return jsonify({
                "statistics": {
                    "total_students": 0,
                    "average_sgpa": 0,
                    "pass_percentage": 0,
                    "grade_distribution": {},
                    "semester_distribution": {},
                    "year_distribution": {}
                }
            }), 200
        
        # Calculate statistics
        total_students = len(docs)
        sgpa_values = []
        passed_students = 0
        grade_counts = {}
        semester_counts = {}
        year_counts = {}
        
        for doc in docs:
            doc_data = doc.to_dict()
            
            # SGPA statistics
            sgpa = doc_data.get('sgpa', 0)
            if sgpa and sgpa > 0:
                sgpa_values.append(float(sgpa))
                if float(sgpa) >= 4.0:  # Assuming 4.0 is pass grade
                    passed_students += 1
            
            # Grade distribution
            for subject, grade in doc_data.get('subjects', {}).items():
                if isinstance(grade, str):
                    grade_counts[grade] = grade_counts.get(grade, 0) + 1
            
            # Semester distribution
            sem = doc_data.get('semester', 'Unknown')
            semester_counts[sem] = semester_counts.get(sem, 0) + 1
            
            # Year distribution
            yr = doc_data.get('year', 'Unknown')
            year_counts[yr] = year_counts.get(yr, 0) + 1
        
        # Calculate averages
        avg_sgpa = sum(sgpa_values) / len(sgpa_values) if sgpa_values else 0
        pass_percentage = (passed_students / total_students * 100) if total_students > 0 else 0
        
        return jsonify({
            "statistics": {
                "total_students": total_students,
                "average_sgpa": round(avg_sgpa, 2),
                "pass_percentage": round(pass_percentage, 2),
                "grade_distribution": grade_counts,
                "semester_distribution": semester_counts,
                "year_distribution": year_counts
            },
            "filters": {
                "semester": semester,
                "year": year,
                "exam_type": exam_type
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        return jsonify({"error": f"Statistics calculation failed: {str(e)}"}), 500

# -----------------------------------------------------------------------------
# PDF upload endpoint (no student_id required, all extracted by parser)
# -----------------------------------------------------------------------------
@app.route('/upload-pdf', methods=['POST'])
@require_api_key
def upload_pdf():
    file_path = None
    try:
        file = request.files.get('pdf')
        format_type = request.form.get('format')
        exam_type = request.form.get('exam_type')
        # Only require the fields you actually use:
        if not all([file, format_type, exam_type]):
            raise AppError("Missing required fields.", 400)
        if format_type.lower() not in ('jntuk', 'autonomous'):
            raise AppError("Invalid format type. Must be 'jntuk' or 'autonomous'.", 400)
        if exam_type.lower() not in ('regular', 'supply'):
            raise AppError("Invalid exam type. Must be 'regular' or 'supply'.", 400)
        valid, error_msg = PDFValidator.validate_file(file)
        if not valid:
            raise AppError(error_msg, 400)
        file_path, _ = secure_file_handling(file)
        file.save(file_path)
        # Parse all student results from the PDF using the selected parser:
        if format_type.lower() == 'autonomous':
            results = parse_autonomous_pdf(file_path)
        else:
            results = parse_jntuk_pdf(file_path)
        if not results:
            raise AppError("No valid student results found in PDF.", 400)
        
        # Save parsed data to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"parsed_results_{format_type}_{exam_type}_{timestamp}.json"
        json_filepath = os.path.join("data", json_filename)
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Generate unique document ID for Firebase
        doc_id = f"{format_type}_{exam_type}_{timestamp}"
        
        # Upload to Firebase
        firebase_start_time = time.time()
        students_saved = save_to_firebase(results, "Unknown", [exam_type], [exam_type], format_type, doc_id)
        firebase_time = time.time() - firebase_start_time
        
        # Upload PDF to Firebase Storage
        storage_url = None
        if file:
            file.seek(0)  # Reset file pointer
            storage_filename = f"pdfs/{format_type}_{exam_type}_{timestamp}_{file.filename}"
            storage_url = upload_pdf_to_storage(file, storage_filename)
        
        # Prepare data for JSON file with Firebase status
        json_data = {
            "metadata": {
                "format": format_type.lower(),
                "exam_type": exam_type.lower(),
                "processed_at": datetime.now().isoformat(),
                "total_students": len(results),
                "original_filename": file.filename
            },
            "students": results,
            "firebase_status": {
                "firebase_available": FIREBASE_AVAILABLE,
                "saved_count": students_saved,
                "failed_count": len(results) - students_saved if students_saved else len(results),
                "errors": [],
                "firebase_error": None,
                "status": "success" if students_saved > 0 else ("failed" if FIREBASE_AVAILABLE else "disabled"),
                "upload_time": firebase_time
            },
            "cloud_storage": {
                "uploaded": storage_url is not None,
                "url": storage_url or "",
                "filename": json_filename,
                "upload_completed_at": datetime.now().isoformat() if storage_url else ""
            }
        }
        
        # Save to JSON file
        with open(json_filepath, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved parsed data to {json_filepath}")
        logger.info(f"Firebase upload: {students_saved}/{len(results)} students saved")
        
        return jsonify({
            "message": f"Successfully processed {len(results)} result(s). Saved to JSON file.",
            "processed_count": len(results),
            "json_file": json_filename,
            "firebase": {
                "enabled": FIREBASE_AVAILABLE,
                "students_saved": students_saved,
                "students_total": len(results),
                "upload_time": firebase_time,
                "storage_url": storage_url
            }
        }), 200
    except AppError:
        raise
    except Exception as ex:
        logger.error(f"Upload processing error: {ex}\n{traceback.format_exc()}")
        raise AppError("Internal server error while processing upload.", 500)
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {file_path}: {e}")

# -----------------------------------------------------------------------------
# API endpoints for frontend compatibility
# -----------------------------------------------------------------------------
@app.route('/api/uploaded-results', methods=['GET'])
def api_uploaded_results():
    """API endpoint for getting uploaded results (frontend compatibility)"""
    return list_data_files()

@app.route('/api/upload-result', methods=['POST'])
def api_upload_result():
    """API endpoint for uploading results (frontend compatibility) - Async version"""
    try:
        file = request.files.get('pdf') or request.files.get('file')
        format_type = request.form.get('format') or request.form.get('resultType', 'jntuk')
        exam_type = request.form.get('exam_type') or request.form.get('examType', 'regular')
        
        if not all([file, format_type, exam_type]):
            return jsonify({"error": "Missing required fields", "required": ["file", "format", "exam_type"]}), 400
            
        if format_type.lower() not in ('jntuk', 'autonomous'):
            return jsonify({"error": "Invalid format type. Must be 'jntuk' or 'autonomous'"}), 400
            
        if exam_type.lower() not in ('regular', 'supply'):
            return jsonify({"error": "Invalid exam type. Must be 'regular' or 'supply'"}), 400
            
        valid, error_msg = PDFValidator.validate_file(file)
        if not valid:
            return jsonify({"error": error_msg}), 400
            
        # Generate upload ID immediately
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        upload_id = f"upload_{timestamp}"
        
        # Save file temporarily
        file_path, _ = secure_file_handling(file)
        file.save(file_path)
        
        # Initialize progress tracking
        update_progress(upload_id, "started", parsing={"status": "started", "message": "Upload started, processing PDF..."})
        
        # Start background processing using threading
        import threading
        thread = threading.Thread(target=process_upload_background, args=(file_path, format_type, exam_type, file.filename, upload_id))
        thread.daemon = True
        thread.start()
        
        # Return immediately with upload_id
        return jsonify({
            "success": True,
            "message": "Upload started successfully",
            "upload_id": upload_id,
            "status": "processing"
        }), 200
        
    except Exception as ex:
        logger.error(f"Upload start error: {ex}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error while starting upload"}), 500


def process_upload_background(file_path, format_type, exam_type, original_filename, upload_id):
    """Background processing function for file uploads"""
    try:
        # Step 1: Parse PDF
        update_progress(upload_id, "parsing", parsing={"status": "parsing", "message": "Extracting student data from PDF..."})
        
        if format_type.lower() == 'autonomous':
            results = parse_autonomous_pdf(file_path)
        else:
            results = parse_jntuk_pdf(file_path)
            
        if not results:
            update_progress(upload_id, "error", parsing={"status": "error", "message": "No valid student results found in PDF"})
            return
        
        # Update parsing complete
        update_progress(upload_id, "parsing_complete", parsing={
            "status": "completed", 
            "message": f"Extracted {len(results)} student records",
            "total_students": len(results)
        })
        
        # Step 2: Upload to Firebase
        firebase_start_time = time.time()
        
        # Generate document ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_id = f"{format_type}_{exam_type}_{timestamp}"
        
        students_saved = save_to_firebase(results, "Unknown", [exam_type], [exam_type], format_type, doc_id, upload_id)
        firebase_time = time.time() - firebase_start_time
        
        # Step 3: Upload PDF to Firebase Storage
        update_progress(upload_id, "storage_uploading", storage={"status": "uploading", "message": "Uploading PDF to cloud storage..."})
        storage_url = None
        try:
            with open(file_path, 'rb') as pdf_file:
                storage_filename = f"pdfs/{format_type}_{exam_type}_{timestamp}_{original_filename}"
                storage_url = upload_pdf_to_storage(pdf_file, storage_filename)
        except Exception as storage_error:
            logger.warning(f"PDF storage failed: {storage_error}")
            
        if storage_url:
            update_progress(upload_id, "storage_complete", storage={"status": "completed", "url": storage_url, "message": "PDF uploaded to cloud storage"})
        else:
            update_progress(upload_id, "storage_complete", storage={"status": "skipped", "message": "PDF storage skipped"})
        
        # Step 4: Save to JSON
        update_progress(upload_id, "json_saving", json={"status": "saving", "message": "Saving data to JSON file..."})
        
        # Prepare data for JSON file with Firebase status
        json_filename = f"parsed_results_{format_type}_{exam_type}_{timestamp}.json"
        json_filepath = os.path.join("data", json_filename)
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        json_data = {
            "metadata": {
                "format": format_type.lower(),
                "exam_type": exam_type.lower(),
                "processed_at": datetime.now().isoformat(),
                "total_students": len(results),
                "original_filename": original_filename,
                "processing_status": "completed",
                "upload_id": upload_id
            },
            "students": results,
            "firebase_status": {
                "firebase_available": FIREBASE_AVAILABLE,
                "saved_count": students_saved,
                "failed_count": len(results) - students_saved if students_saved else len(results),
                "errors": [],
                "firebase_error": None,
                "status": "success" if students_saved > 0 else ("failed" if FIREBASE_AVAILABLE else "disabled"),
                "upload_time": firebase_time
            },
            "cloud_storage": {
                "uploaded": storage_url is not None,
                "url": storage_url or "",
                "filename": json_filename,
                "upload_completed_at": datetime.now().isoformat() if storage_url else ""
            }
        }
        
        # Save to JSON file
        with open(json_filepath, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=2, ensure_ascii=False)
        
        update_progress(upload_id, "completed", json={"status": "completed", "file": json_filename, "message": "JSON file saved successfully"})
        
        # Store final result in progress for frontend to retrieve
        final_result = {
            "success": True,
            "message": f"Successfully processed {len(results)} result(s)",
            "processed_count": len(results),
            "json_file": json_filename,
            "file_id": json_filename.replace('.json', ''),
            "upload_id": upload_id,
            "firebase": {
                "enabled": FIREBASE_AVAILABLE,
                "students_saved": students_saved,
                "students_total": len(results),
                "upload_time": firebase_time,
                "storage_url": storage_url
            },
            "data": {
                "total_students": len(results),
                "format": format_type.lower(),
                "exam_type": exam_type.lower(),
                "original_filename": original_filename
            }
        }
        
        # Store the final result in upload_progress for the frontend to access
        upload_progress[upload_id]["final_result"] = final_result
        
        logger.info(f"Saved parsed data to {json_filepath}")
        logger.info(f"Firebase upload: {students_saved}/{len(results)} students saved")
        
    except Exception as ex:
        logger.error(f"Background processing error: {ex}\n{traceback.format_exc()}")
        update_progress(upload_id, "error", error={"status": "error", "message": f"Processing failed: {str(ex)}"})
    finally:
        # Clean up temp file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {file_path}: {e}")


# -----------------------------------------------------------------------------
# Run server if script is run directly
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)


#Copyright (c) 2023 Nene