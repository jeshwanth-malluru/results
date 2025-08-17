#!/usr/bin/env python3
"""
Update old Firestore student_results records to add numeric year, semester, and year_semester fields (e.g., 1-1, 2-2, etc.)
"""
import firebase_admin
from firebase_admin import credentials, firestore
import re

# Initialize Firebase
try:
    app = firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate('serviceAccount.json')
    app = firebase_admin.initialize_app(cred)
db = firestore.client()

def parse_year_semester(data):
    # Try to extract year and semester as numbers
    year = data.get('year')
    semester = data.get('semester')
    # Try to parse year as int
    year_num = None
    sem_num = None
    try:
        year_num = int(str(year).strip()[0])
    except Exception:
        year_num = None
    # Try to extract semester number from string
    sem_match = re.search(r'(\d+)', str(semester))
    if sem_match:
        sem_num = int(sem_match.group(1))
    else:
        sem_num = None
    # Compose year_semester string
    if year_num and sem_num:
        year_semester = f"{year_num}-{sem_num}"
    else:
        year_semester = f"{year}_{semester}"
    return year_num, sem_num, year_semester

def update_all_records():
    print("🔄 Updating all student_results records with year, semester, year_semester fields...")
    docs = db.collection('student_results').stream()
    count = 0
    for doc in docs:
        data = doc.to_dict()
        year_num, sem_num, year_semester = parse_year_semester(data)
        update_data = {}
        if year_num:
            update_data['year'] = year_num
        if sem_num:
            update_data['semester'] = sem_num
        update_data['year_semester'] = year_semester
        if update_data:
            db.collection('student_results').document(doc.id).update(update_data)
            print(f"✅ Updated {doc.id}: year={year_num}, semester={sem_num}, year_semester={year_semester}")
            count += 1
    print(f"\n🎉 Done! Updated {count} records.")

if __name__ == "__main__":
    update_all_records()
