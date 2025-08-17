#!/usr/bin/env python3
"""
Update Firestore student_results records to fix 'Unknown' year by inferring year from semester.
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

def infer_year_from_semester(semester):
    # Accepts 'Semester 1', 'Semester 2', etc.
    try:
        sem_num = int(re.search(r'(\d+)', str(semester)).group(1))
        if sem_num in [1, 2]:
            return 1
        elif sem_num in [3, 4]:
            return 2
        elif sem_num in [5, 6]:
            return 3
        elif sem_num in [7, 8]:
            return 4
    except Exception:
        pass
    return None

def fix_unknown_years():
    print("🔄 Fixing 'Unknown' year in student_results...")
    docs = db.collection('student_results').stream()
    count = 0
    for doc in docs:
        data = doc.to_dict()
        year = data.get('year')
        semester = data.get('semester')
        # Only update if year is missing or 'Unknown'
        if not year or str(year).lower() == 'unknown':
            inferred_year = infer_year_from_semester(semester)
            if inferred_year:
                # Also update year_semester if present
                year_semester = f"{inferred_year}-{semester}" if semester else str(inferred_year)
                update_data = {'year': inferred_year, 'year_semester': year_semester}
                db.collection('student_results').document(doc.id).update(update_data)
                print(f"✅ Updated {doc.id}: year={inferred_year}, year_semester={year_semester}")
                count += 1
    print(f"\n🎉 Done! Fixed {count} records.")

if __name__ == "__main__":
    fix_unknown_years()
