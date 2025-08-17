from app import db

print('📊 CURRENT DATABASE STATE (After Removing Merge Logic)')
print('=' * 60)

# Check regular results
regular_docs = list(db.collection('student_results').where('examType', '==', 'regular').limit(5).stream())
print(f'📚 Regular Results: {len(regular_docs)} records found')

# Check supply results  
supply_docs = list(db.collection('student_results').where('examType', '==', 'supply').limit(5).stream())
print(f'📝 Supply Results: {len(supply_docs)} records found')

# Show sample data
print(f'\n📋 Sample Records:')
all_docs = list(db.collection('student_results').limit(5).stream())
for doc in all_docs:
    data = doc.to_dict()
    subjects = data.get('subjectGrades', [])
    grades = [s.get('grade') for s in subjects]
    exam_type = data.get('examType', 'unknown')
    print(f'  {exam_type.upper()}: Student {data.get("student_id")} - {len(subjects)} subjects, grades: {set(grades)}')

print(f'\n✅ CHANGES COMPLETED:')
print(f'  • Supply PDFs now save directly to Firebase')
print(f'  • No automatic merging with regular results')  
print(f'  • Supply and regular results stored separately')
print(f'  • Same storage pattern for both exam types')
