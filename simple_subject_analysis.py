#!/usr/bin/env python3
"""
Simple Subject Code Analysis
Check all subjects and their grades in the supply merge results
"""

import json
import os

def simple_subject_analysis():
    """Simple analysis of all subjects"""
    
    print("🔍 SIMPLE SUBJECT CODE ANALYSIS")
    print("=" * 50)
    
    try:
        # Load the fixed results file
        with open('ads_fixed_supply_merge_20250813_231359.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated_students = data.get('updated_students', [])
        print(f"📄 Loaded {len(updated_students)} students")
        
        # Count subjects by code and grade
        subject_stats = {}
        total_subjects = 0
        f_grades = 0
        improved_subjects = 0
        
        # Sample a few students to see the pattern
        print(f"\n📋 SAMPLE STUDENTS (first 3):")
        
        for i, student in enumerate(updated_students[:3]):
            htno = student.get('student_id', 'Unknown')
            subjects = student.get('subjectGrades', [])
            
            print(f"\n  {i+1}. Student {htno}:")
            print(f"     Total subjects: {len(subjects)}")
            
            for j, subject in enumerate(subjects):
                code = subject.get('code', 'N/A')
                name = subject.get('subject', 'Unknown')
                grade = subject.get('grade', 'N/A')
                attempts = subject.get('attempts', 1)
                improved = subject.get('supplyImproved', False)
                
                # Show first few subjects
                if j < 5:  # Show first 5 subjects
                    status = "📈 IMPROVED" if improved or attempts > 1 else ("❌ F" if grade == 'F' else "✓")
                    print(f"     {j+1:2d}. {code:12s} | {grade:2s} | Att:{attempts} | {status}")
                    if len(name) > 30:
                        name_short = name[:27] + "..."
                    else:
                        name_short = name
                    print(f"         {name_short}")
                
                # Count for statistics
                total_subjects += 1
                if grade == 'F':
                    f_grades += 1
                if improved or attempts > 1:
                    improved_subjects += 1
                
                # Track by subject code
                if code not in subject_stats:
                    subject_stats[code] = {'total': 0, 'f_count': 0, 'improved': 0, 'grades': {}}
                
                subject_stats[code]['total'] += 1
                if grade == 'F':
                    subject_stats[code]['f_count'] += 1
                if improved or attempts > 1:
                    subject_stats[code]['improved'] += 1
                if grade not in subject_stats[code]['grades']:
                    subject_stats[code]['grades'][grade] = 0
                subject_stats[code]['grades'][grade] += 1
            
            if len(subjects) > 5:
                print(f"         ... and {len(subjects) - 5} more subjects")
        
        # Overall statistics
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"  📚 Total subjects: {total_subjects}")
        print(f"  ❌ F grades: {f_grades} ({f_grades/total_subjects*100:.1f}%)")
        print(f"  📈 Improved subjects: {improved_subjects} ({improved_subjects/total_subjects*100:.1f}%)")
        print(f"  📋 Unique subject codes: {len(subject_stats)}")
        
        # Show subject codes with most F grades
        print(f"\n🔍 SUBJECT CODES WITH MOST F GRADES (Top 10):")
        sorted_by_f = sorted(subject_stats.items(), key=lambda x: x[1]['f_count'], reverse=True)
        
        for i, (code, stats) in enumerate(sorted_by_f[:10]):
            f_percent = (stats['f_count'] / stats['total']) * 100
            improved_percent = (stats['improved'] / stats['total']) * 100
            print(f"  {i+1:2d}. {code:12s} | Total:{stats['total']:3d} | F:{stats['f_count']:3d} ({f_percent:4.1f}%) | Improved:{stats['improved']:3d} ({improved_percent:4.1f}%)")
        
        # Show subject codes with best improvement rates
        print(f"\n✅ SUBJECT CODES WITH BEST IMPROVEMENTS (Top 10):")
        sorted_by_improved = sorted(subject_stats.items(), key=lambda x: x[1]['improved'], reverse=True)
        
        for i, (code, stats) in enumerate(sorted_by_improved[:10]):
            if stats['improved'] > 0:
                improved_percent = (stats['improved'] / stats['total']) * 100
                print(f"  {i+1:2d}. {code:12s} | Total:{stats['total']:3d} | Improved:{stats['improved']:3d} ({improved_percent:4.1f}%)")
        
        # Check specific problematic codes
        print(f"\n🎯 CHECKING SPECIFIC SUBJECT CODES:")
        
        problematic_codes = ['R2321121', 'R2321053', 'R2321055', 'R2321019', 'R2321051']  # Common 2-1 codes
        
        for code in problematic_codes:
            if code in subject_stats:
                stats = subject_stats[code]
                f_percent = (stats['f_count'] / stats['total']) * 100
                improved_percent = (stats['improved'] / stats['total']) * 100
                grade_dist = " | ".join([f"{g}:{c}" for g, c in sorted(stats['grades'].items())])
                
                print(f"  {code:12s} | Total:{stats['total']:3d} | F:{stats['f_count']:3d} ({f_percent:4.1f}%) | Improved:{stats['improved']:3d} ({improved_percent:4.1f}%)")
                print(f"               Grades: {grade_dist}")
            else:
                print(f"  {code:12s} | NOT FOUND")
        
        print(f"\n💡 ANALYSIS SUMMARY:")
        if f_grades > improved_subjects:
            print(f"  ⚠️  More F grades ({f_grades}) than improvements ({improved_subjects})")
            print(f"  🔧 This suggests supply merging may need attention")
        else:
            print(f"  ✅ More improvements ({improved_subjects}) than F grades ({f_grades})")
            print(f"  🎉 Supply merging appears to be working well")
        
        if f_grades > total_subjects * 0.3:  # More than 30% F grades
            print(f"  🚨 High F grade percentage ({f_grades/total_subjects*100:.1f}%) indicates potential issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = simple_subject_analysis()
    if success:
        print(f"\n🏁 Analysis complete!")
    else:
        print(f"\n💥 Analysis failed!")
