#!/usr/bin/env python3
"""
Quick Fix for Advanced Data Structures Issue
This analyzes the existing results and shows what the issue is
"""

import json
import os
from datetime import datetime

def analyze_ads_issue():
    """Analyze the Advanced Data Structures issue in the existing results"""
    
    print("🔍 ANALYZING ADVANCED DATA STRUCTURES ISSUE")
    print("=" * 60)
    
    # Load the existing results file
    results_file = "complete_supply_merge_20250813_230558.json"
    
    if not os.path.exists(results_file):
        print(f"❌ Results file not found: {results_file}")
        return
    
    try:
        print(f"📄 Loading existing results: {results_file}")
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated_students = data.get('updated_students', [])
        print(f"  ✓ Found {len(updated_students)} updated students")
        
        # Look for Advanced Data Structures issues
        ads_issues = []
        ads_fixed = []
        
        for student in updated_students:
            htno = student.get('student_id', 'Unknown')
            subjects = student.get('subjectGrades', [])
            
            # Find ADS subjects
            ads_subjects = []
            for subject in subjects:
                subject_name = str(subject.get('subject', '')).upper()
                subject_code = str(subject.get('code', '')).upper()
                
                if 'ADVANCED DATA STRUCTURES' in subject_name or 'R2321121' in subject_code:
                    ads_subjects.append({
                        'code': subject.get('code', 'N/A'),
                        'name': subject.get('subject', 'N/A'),
                        'grade': subject.get('grade', 'N/A'),
                        'result': subject.get('result', 'N/A'),
                        'attempts': subject.get('attempts', 1),
                        'improved': subject.get('supplyImproved', False)
                    })
            
            if ads_subjects:
                if len(ads_subjects) > 1:
                    # Multiple ADS entries - this is the issue
                    ads_issues.append({
                        'htno': htno,
                        'name': student.get('student_name', 'N/A'),
                        'ads_count': len(ads_subjects),
                        'ads_subjects': ads_subjects
                    })
                else:
                    # Single ADS entry - check if it was improved
                    ads_subject = ads_subjects[0]
                    if ads_subject['improved'] or ads_subject['attempts'] > 1:
                        ads_fixed.append({
                            'htno': htno,
                            'name': student.get('student_name', 'N/A'),
                            'ads_subject': ads_subject
                        })
        
        print(f"\n🎯 ANALYSIS RESULTS:")
        print(f"  🔴 Students with ADS duplicate issues: {len(ads_issues)}")
        print(f"  🟢 Students with ADS properly fixed: {len(ads_fixed)}")
        
        if ads_issues:
            print(f"\n❌ DUPLICATE ADS ISSUES (showing first 5):")
            for i, issue in enumerate(ads_issues[:5]):
                print(f"  {i+1}. {issue['htno']} ({issue['name']}): {issue['ads_count']} ADS entries")
                for j, ads in enumerate(issue['ads_subjects']):
                    print(f"     Entry {j+1}: {ads['code']} - {ads['grade']} ({ads['result']}) - Attempts: {ads['attempts']}")
        
        if ads_fixed:
            print(f"\n✅ PROPERLY FIXED ADS (showing first 5):")
            for i, fixed in enumerate(ads_fixed[:5]):
                ads = fixed['ads_subject']
                print(f"  {i+1}. {fixed['htno']} ({fixed['name']}): {ads['code']} - {ads['grade']} ({ads['result']}) - Attempts: {ads['attempts']}")
        
        # Create a simple fix
        print(f"\n🔧 CREATING SIMPLE FIX...")
        
        fixed_students = []
        fixes_applied = 0
        
        for student in updated_students:
            student_copy = student.copy()
            subjects = student.get('subjectGrades', [])
            
            # Group subjects by normalized code
            subject_groups = {}
            for subject in subjects:
                code = str(subject.get('code', '')).strip().upper()
                if code:
                    if code not in subject_groups:
                        subject_groups[code] = []
                    subject_groups[code].append(subject)
            
            # Fix duplicates by keeping the best grade
            fixed_subjects = []
            student_had_fixes = False
            
            for code, subject_list in subject_groups.items():
                if len(subject_list) == 1:
                    # No duplicates
                    fixed_subjects.append(subject_list[0])
                else:
                    # Multiple entries - keep the one with best grade
                    grade_hierarchy = ['F', 'D', 'C', 'B', 'B+', 'A', 'A+', 'O']
                    
                    best_subject = subject_list[0]
                    for subject in subject_list[1:]:
                        current_grade = best_subject.get('grade', 'F')
                        new_grade = subject.get('grade', 'F')
                        
                        try:
                            current_index = grade_hierarchy.index(current_grade)
                            new_index = grade_hierarchy.index(new_grade)
                            if new_index > current_index:
                                best_subject = subject
                        except ValueError:
                            pass
                    
                    # Mark as fixed
                    best_subject['duplicateFixed'] = True
                    best_subject['duplicateCount'] = len(subject_list)
                    fixed_subjects.append(best_subject)
                    student_had_fixes = True
                    fixes_applied += 1
            
            student_copy['subjectGrades'] = fixed_subjects
            if student_had_fixes:
                student_copy['duplicatesFixed'] = True
                student_copy['fixedAt'] = datetime.now().isoformat()
            
            fixed_students.append(student_copy)
        
        # Save fixed results
        fixed_data = data.copy()
        fixed_data['updated_students'] = fixed_students
        fixed_data['metadata']['fixes_applied'] = f"Removed {fixes_applied} duplicate subjects"
        fixed_data['metadata']['fixed_at'] = datetime.now().isoformat()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"ads_fixed_supply_merge_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Applied {fixes_applied} duplicate fixes")
        print(f"  ✓ Fixed results saved to: {output_file}")
        
        print(f"\n🎉 ANALYSIS COMPLETE!")
        print(f"📄 Fixed file: {output_file}")
        print(f"🔧 Fixes applied: {fixes_applied} duplicate subjects removed")
        print(f"📋 Advanced Data Structures should now show correct grades!")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result_file = analyze_ads_issue()
    if result_file:
        print(f"\n🏁 Analysis and fix complete! Check: {result_file}")
    else:
        print(f"\n💥 Analysis failed.")
