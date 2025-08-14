#!/usr/bin/env python3
"""
Firebase Direct Analysis
Check Firebase directly to verify the perfect merge results
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase if not already done
if not firebase_admin._apps:
    try:
        if os.path.exists('serviceAccount.json'):
            cred = credentials.Certificate('serviceAccount.json')
            firebase_admin.initialize_app(cred)
            print("🔥 Firebase initialized successfully!")
        else:
            print("❌ serviceAccount.json not found")
            exit(1)
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        exit(1)

db = firestore.client()

def analyze_firebase_direct():
    """Analyze Firebase results directly to see the perfect merge impact"""
    
    print("🔍 FIREBASE DIRECT ANALYSIS")
    print("=" * 60)
    
    # Get students with perfect merge applied
    print("📊 Checking students with perfectMergeApplied...")
    
    perfect_merge_query = db.collection('student_results').where('perfectMergeApplied', '==', True)
    perfect_merge_docs = list(perfect_merge_query.stream())
    
    print(f"✅ Found {len(perfect_merge_docs)} students with perfect merge applied")
    
    # Analyze F grades in these students
    total_subjects = 0
    f_grades = 0
    improved_subjects = 0
    f_to_pass_conversions = 0
    
    sample_improvements = []
    
    for doc in perfect_merge_docs[:10]:  # Sample first 10
        doc_data = doc.to_dict()
        student_id = doc_data.get('student_id', 'Unknown')
        subjects = doc_data.get('subjectGrades', [])
        merge_report = doc_data.get('mergeReport', {})
        
        print(f"\n📋 {student_id}:")
        print(f"   Total subjects: {len(subjects)}")
        print(f"   Improvements: {merge_report.get('subjects_improved', 0)}")
        print(f"   F→Pass conversions: {merge_report.get('f_to_pass_conversions', 0)}")
        
        for subject in subjects:
            total_subjects += 1
            grade = subject.get('grade', 'F')
            
            if grade.upper() == 'F':
                f_grades += 1
            
            if subject.get('supplyImproved', False):
                improved_subjects += 1
                improvement_reason = subject.get('improvementReason', 'Unknown')
                if 'F→' in improvement_reason:
                    f_to_pass_conversions += 1
                
                sample_improvements.append({
                    'student': student_id,
                    'subject': subject.get('code', 'Unknown'),
                    'original': subject.get('originalGrade', 'Unknown'),
                    'supply': subject.get('supplyGrade', 'Unknown'),
                    'reason': improvement_reason
                })
    
    print(f"\n📊 SAMPLE ANALYSIS (first 10 students):")
    print(f"  📚 Total subjects: {total_subjects}")
    print(f"  ❌ F grades remaining: {f_grades}")
    print(f"  📈 Supply improved subjects: {improved_subjects}")
    print(f"  🎯 F→Pass conversions: {f_to_pass_conversions}")
    
    print(f"\n✨ SAMPLE IMPROVEMENTS:")
    for i, imp in enumerate(sample_improvements[:5]):
        print(f"  {i+1}. {imp['student']}: {imp['subject']} {imp['original']}→{imp['supply']} ({imp['reason']})")
    
    # Get overall statistics
    print(f"\n🔍 GETTING OVERALL FIREBASE STATISTICS...")
    
    all_students = db.collection('student_results').stream()
    
    total_firebase_students = 0
    total_firebase_f_grades = 0
    total_firebase_subjects = 0
    perfect_merge_count = 0
    
    for doc in all_students:
        doc_data = doc.to_dict()
        total_firebase_students += 1
        
        if doc_data.get('perfectMergeApplied', False):
            perfect_merge_count += 1
        
        subjects = doc_data.get('subjectGrades', [])
        for subject in subjects:
            total_firebase_subjects += 1
            if subject.get('grade', '').upper() == 'F':
                total_firebase_f_grades += 1
    
    print(f"\n📊 FIREBASE OVERALL STATISTICS:")
    print(f"  👥 Total students in Firebase: {total_firebase_students}")
    print(f"  ✅ Students with perfect merge: {perfect_merge_count}")
    print(f"  📚 Total subjects: {total_firebase_subjects}")
    print(f"  ❌ Total F grades: {total_firebase_f_grades}")
    print(f"  📈 Success rate: {((total_firebase_subjects - total_firebase_f_grades) / total_firebase_subjects * 100):.1f}%")
    
    if total_firebase_f_grades < 1000:  # Much lower than before
        print(f"  🎉 SIGNIFICANT IMPROVEMENT! F grades reduced substantially!")
    else:
        print(f"  ⚠️  F grades still high - may need further investigation")

if __name__ == "__main__":
    analyze_firebase_direct()
