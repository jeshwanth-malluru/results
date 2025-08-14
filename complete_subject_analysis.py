#!/usr/bin/env python3
"""
Complete Subject Code Analysis
Analyze ALL subjects and their grades in the supply merge results
"""

import json
import os
from collections import defaultdict

def complete_subject_analysis():
    """Complete analysis of all subjects for all students"""
    
    print("🔍 COMPLETE SUBJECT CODE ANALYSIS")
    print("=" * 60)
    
    try:
        # Load the fixed results file
        with open('ads_fixed_supply_merge_20250813_231359.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated_students = data.get('updated_students', [])
        print(f"📄 Loaded {len(updated_students)} students")
        
        # Count subjects by code and grade
        subject_stats = defaultdict(lambda: {
            'total': 0, 
            'f_count': 0, 
            'improved': 0, 
            'grades': defaultdict(int),
            'students': []
        })
        
        total_subjects = 0
        f_grades = 0
        improved_subjects = 0
        all_f_students = []
        
        print(f"\n📋 PROCESSING ALL {len(updated_students)} STUDENTS...")
        
        # Process ALL students
        for i, student in enumerate(updated_students):
            htno = student.get('student_id', 'Unknown')
            subjects = student.get('subjectGrades', [])
            
            if (i + 1) % 50 == 0:  # Progress indicator
                print(f"  Processed {i+1}/{len(updated_students)} students...")
            
            student_f_subjects = []
            
            for subject in subjects:
                code = subject.get('code', 'N/A')
                name = subject.get('subject', 'Unknown')
                grade = subject.get('grade', 'N/A')
                attempts = subject.get('attempts', 1)
                improved = subject.get('supplyImproved', False)
                
                # Count for statistics
                total_subjects += 1
                
                if grade == 'F':
                    f_grades += 1
                    student_f_subjects.append({
                        'code': code,
                        'name': name,
                        'attempts': attempts,
                        'improved': improved
                    })
                
                if improved or attempts > 1:
                    improved_subjects += 1
                
                # Track by subject code
                subject_stats[code]['total'] += 1
                if grade == 'F':
                    subject_stats[code]['f_count'] += 1
                if improved or attempts > 1:
                    subject_stats[code]['improved'] += 1
                subject_stats[code]['grades'][grade] += 1
                subject_stats[code]['students'].append(htno)
            
            # Track students with F grades
            if student_f_subjects:
                all_f_students.append({
                    'htno': htno,
                    'f_subjects': student_f_subjects
                })
        
        print(f"✅ Processed all {len(updated_students)} students!")
        
        # Overall statistics
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"  📚 Total subjects processed: {total_subjects}")
        print(f"  👥 Total students: {len(updated_students)}")
        print(f"  📖 Average subjects per student: {total_subjects/len(updated_students):.1f}")
        print(f"  ❌ Total F grades: {f_grades} ({f_grades/total_subjects*100:.1f}%)")
        print(f"  📈 Total improved subjects: {improved_subjects} ({improved_subjects/total_subjects*100:.1f}%)")
        print(f"  📋 Unique subject codes: {len(subject_stats)}")
        print(f"  🚨 Students with F grades: {len(all_f_students)}")
        
        # Show ALL subject codes with F grades (not just top 10)
        print(f"\n🔍 ALL SUBJECT CODES WITH F GRADES:")
        subjects_with_f = [(code, stats) for code, stats in subject_stats.items() if stats['f_count'] > 0]
        subjects_with_f.sort(key=lambda x: x[1]['f_count'], reverse=True)
        
        if subjects_with_f:
            print(f"  Found {len(subjects_with_f)} subject codes with F grades:")
            for i, (code, stats) in enumerate(subjects_with_f):
                f_percent = (stats['f_count'] / stats['total']) * 100
                improved_percent = (stats['improved'] / stats['total']) * 100
                grade_dist = " | ".join([f"{g}:{c}" for g, c in sorted(stats['grades'].items()) if c > 0])
                
                print(f"  {i+1:2d}. {code:12s} | Total:{stats['total']:3d} | F:{stats['f_count']:3d} ({f_percent:4.1f}%) | Improved:{stats['improved']:3d} ({improved_percent:4.1f}%)")
                print(f"      Grades: {grade_dist}")
                
                # Show some students with F in this subject
                f_students_for_code = [s for s in all_f_students if any(fs['code'] == code for fs in s['f_subjects'])]
                if f_students_for_code:
                    sample_students = f_students_for_code[:3]  # Show first 3
                    student_list = ", ".join([s['htno'] for s in sample_students])
                    if len(f_students_for_code) > 3:
                        student_list += f" (+{len(f_students_for_code)-3} more)"
                    print(f"      F Students: {student_list}")
                print()
        else:
            print(f"  🎉 NO SUBJECT CODES HAVE F GRADES! Supply processing worked perfectly!")
        
        # Show subjects with best improvement rates
        print(f"\n✅ SUBJECT CODES WITH BEST IMPROVEMENTS:")
        subjects_with_improvements = [(code, stats) for code, stats in subject_stats.items() if stats['improved'] > 0]
        subjects_with_improvements.sort(key=lambda x: x[1]['improved'], reverse=True)
        
        print(f"  Found {len(subjects_with_improvements)} subject codes with improvements:")
        for i, (code, stats) in enumerate(subjects_with_improvements[:15]):  # Show top 15
            improved_percent = (stats['improved'] / stats['total']) * 100
            f_percent = (stats['f_count'] / stats['total']) * 100
            print(f"  {i+1:2d}. {code:12s} | Total:{stats['total']:3d} | Improved:{stats['improved']:3d} ({improved_percent:4.1f}%) | F:{stats['f_count']:3d} ({f_percent:4.1f}%)")
        
        # Show sample students with F grades for detailed analysis
        if all_f_students:
            print(f"\n🚨 STUDENTS WITH F GRADES (Sample of first 10):")
            for i, student_info in enumerate(all_f_students[:10]):
                htno = student_info['htno']
                f_subjects = student_info['f_subjects']
                print(f"  {i+1:2d}. {htno}:")
                for fs in f_subjects:
                    improved_status = "📈 IMPROVED" if fs['improved'] else "❌ NO IMPROVEMENT"
                    print(f"      {fs['code']:12s} | Att:{fs['attempts']} | {improved_status}")
                    print(f"      {fs['name']}")
                print()
        
        # Final analysis
        print(f"\n💡 DETAILED ANALYSIS SUMMARY:")
        
        success_rate = ((total_subjects - f_grades) / total_subjects) * 100
        improvement_rate = (improved_subjects / total_subjects) * 100
        
        print(f"  📈 Overall success rate: {success_rate:.1f}% ({total_subjects - f_grades}/{total_subjects})")
        print(f"  🔄 Overall improvement rate: {improvement_rate:.1f}% ({improved_subjects}/{total_subjects})")
        print(f"  👥 Students with F grades: {len(all_f_students)}/{len(updated_students)} ({len(all_f_students)/len(updated_students)*100:.1f}%)")
        
        if f_grades == 0:
            print(f"  🎉 PERFECT! No F grades found - supply processing worked excellently!")
        elif f_grades < improved_subjects:
            print(f"  ✅ GOOD: More improvements ({improved_subjects}) than F grades ({f_grades})")
        else:
            print(f"  ⚠️  ATTENTION: More F grades ({f_grades}) than improvements ({improved_subjects})")
            print(f"  🔧 This may indicate supply processing needs review")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = complete_subject_analysis()
    if success:
        print(f"\n🏁 Complete analysis finished!")
    else:
        print(f"\n💥 Analysis failed!")
