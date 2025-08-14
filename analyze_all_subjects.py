#!/usr/bin/env python3
"""
Complete Subject Analysis - Check All Subjects and Their Codes
This will analyze all subjects to ensure supply grades are properly merged
"""

import json
import os
from datetime import datetime
from collections import defaultdict

def analyze_all_subjects():
    """Analyze all subjects in the supply merge results"""
    
    print("🔍 COMPLETE SUBJECT ANALYSIS - ALL SUBJECTS & CODES")
    print("=" * 70)
    
    # Load the fixed results file
    results_file = "ads_fixed_supply_merge_20250813_231359.json"
    
    if not os.path.exists(results_file):
        print(f"❌ Fixed results file not found: {results_file}")
        return
    
    try:
        print(f"📄 Loading fixed results: {results_file}")
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated_students = data.get('updated_students', [])
        print(f"  ✓ Found {len(updated_students)} updated students")
        
        # Analyze all subjects
        subject_analysis = {
            'total_subjects': 0,
            'subjects_with_supply_grades': 0,
            'subjects_still_showing_f': 0,
            'subject_code_summary': defaultdict(lambda: {
                'total_count': 0,
                'supply_improved': 0,
                'still_f_grade': 0,
                'grade_distribution': defaultdict(int),
                'subject_names': set()
            }),
            'problematic_students': [],
            'successful_improvements': []
        }
        
        print(f"\n🔍 Analyzing all subjects...")
        
        for student in updated_students:
            htno = student.get('student_id', 'Unknown')
            subjects = student.get('subjectGrades', [])
            student_issues = []
            student_improvements = []
            
            for subject in subjects:
                subject_code = str(subject.get('code', '')).strip().upper()
                subject_name = str(subject.get('subject', 'Unknown'))
                grade = str(subject.get('grade', 'N/A'))
                result = str(subject.get('result', 'N/A'))
                attempts = subject.get('attempts', 1)
                improved = subject.get('supplyImproved', False)
                
                # Update analysis
                subject_analysis['total_subjects'] += 1
                
                if subject_code:
                    summary = subject_analysis['subject_code_summary'][subject_code]
                    summary['total_count'] += 1
                    summary['grade_distribution'][grade] += 1
                    summary['subject_names'].add(subject_name)
                    
                    if improved or attempts > 1:
                        summary['supply_improved'] += 1
                        subject_analysis['subjects_with_supply_grades'] += 1
                        student_improvements.append({
                            'code': subject_code,
                            'name': subject_name,
                            'grade': grade,
                            'attempts': attempts
                        })
                    elif grade == 'F':
                        summary['still_f_grade'] += 1
                        subject_analysis['subjects_still_showing_f'] += 1
                        student_issues.append({
                            'code': subject_code,
                            'name': subject_name,
                            'grade': grade,
                            'result': result
                        })
            
            if student_issues:
                subject_analysis['problematic_students'].append({
                    'htno': htno,
                    'name': student.get('student_name', 'N/A'),
                    'issues': student_issues,
                    'total_subjects': len(subjects)
                })
            
            if student_improvements:
                subject_analysis['successful_improvements'].append({
                    'htno': htno,
                    'name': student.get('student_name', 'N/A'),
                    'improvements': student_improvements
                })
        
        # Display analysis results
        print(f"\n📊 OVERALL ANALYSIS:")
        print(f"  📚 Total subjects analyzed: {subject_analysis['total_subjects']}")
        print(f"  ✅ Subjects with supply improvements: {subject_analysis['subjects_with_supply_grades']}")
        print(f"  ❌ Subjects still showing F grades: {subject_analysis['subjects_still_showing_f']}")
        print(f"  📈 Success rate: {(subject_analysis['subjects_with_supply_grades'] / subject_analysis['total_subjects'] * 100):.1f}%")
        
        # Show most problematic subject codes
        print(f"\n🔍 SUBJECT CODE ANALYSIS (Top 10 codes):")
        sorted_codes = sorted(
            subject_analysis['subject_code_summary'].items(),
            key=lambda x: x[1]['still_f_grade'],
            reverse=True
        )
        
        for i, (code, summary) in enumerate(sorted_codes[:10]):
            subject_names = list(summary['subject_names'])
            main_name = subject_names[0] if subject_names else 'Unknown'
            if len(main_name) > 40:
                main_name = main_name[:37] + "..."
            
            print(f"  {i+1:2d}. {code:12s} ({main_name})")
            print(f"      Total: {summary['total_count']:3d} | Improved: {summary['supply_improved']:3d} | Still F: {summary['still_f_grade']:3d}")
            
            # Show grade distribution
            grades = sorted(summary['grade_distribution'].items())
            grade_str = " | ".join([f"{g}:{c}" for g, c in grades])
            print(f"      Grades: {grade_str}")
        
        # Show students with most issues
        if subject_analysis['problematic_students']:
            print(f"\n❌ STUDENTS WITH MOST F GRADES (Top 5):")
            sorted_problems = sorted(
                subject_analysis['problematic_students'],
                key=lambda x: len(x['issues']),
                reverse=True
            )
            
            for i, student in enumerate(sorted_problems[:5]):
                print(f"  {i+1}. {student['htno']} ({student['name']}): {len(student['issues'])} F grades out of {student['total_subjects']} subjects")
                for issue in student['issues'][:3]:  # Show first 3 issues
                    print(f"     - {issue['code']}: {issue['grade']} ({issue['name'][:30]}...)")
                if len(student['issues']) > 3:
                    print(f"     ... and {len(student['issues']) - 3} more F grades")
        
        # Show successful improvements
        if subject_analysis['successful_improvements']:
            print(f"\n✅ SUCCESSFUL SUPPLY IMPROVEMENTS (Top 5):")
            sorted_successes = sorted(
                subject_analysis['successful_improvements'],
                key=lambda x: len(x['improvements']),
                reverse=True
            )
            
            for i, student in enumerate(sorted_successes[:5]):
                print(f"  {i+1}. {student['htno']} ({student['name']}): {len(student['improvements'])} improvements")
                for improvement in student['improvements'][:3]:  # Show first 3
                    print(f"     ✓ {improvement['code']}: {improvement['grade']} (Attempt #{improvement['attempts']})")
                if len(student['improvements']) > 3:
                    print(f"     ... and {len(student['improvements']) - 3} more improvements")
        
        # Create detailed report
        print(f"\n💾 Creating detailed report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"subject_analysis_report_{timestamp}.json"
        
        # Convert defaultdict to regular dict for JSON serialization
        subject_code_summary = {}
        for code, summary in subject_analysis['subject_code_summary'].items():
            subject_code_summary[code] = {
                'total_count': summary['total_count'],
                'supply_improved': summary['supply_improved'],
                'still_f_grade': summary['still_f_grade'],
                'grade_distribution': dict(summary['grade_distribution']),
                'subject_names': list(summary['subject_names']),
                'success_rate': (summary['supply_improved'] / summary['total_count'] * 100) if summary['total_count'] > 0 else 0
            }
        
        report_data = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'source_file': results_file,
                'analysis_type': 'complete_subject_analysis'
            },
            'summary': {
                'total_subjects': subject_analysis['total_subjects'],
                'subjects_with_supply_grades': subject_analysis['subjects_with_supply_grades'],
                'subjects_still_showing_f': subject_analysis['subjects_still_showing_f'],
                'success_rate_percentage': (subject_analysis['subjects_with_supply_grades'] / subject_analysis['total_subjects'] * 100) if subject_analysis['total_subjects'] > 0 else 0,
                'total_students_analyzed': len(updated_students),
                'students_with_issues': len(subject_analysis['problematic_students']),
                'students_with_improvements': len(subject_analysis['successful_improvements'])
            },
            'subject_code_analysis': subject_code_summary,
            'problematic_students': subject_analysis['problematic_students'],
            'successful_improvements': subject_analysis['successful_improvements']
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Detailed report saved to: {report_file}")
        
        # Provide recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if subject_analysis['subjects_still_showing_f'] > 0:
            print(f"  🔧 {subject_analysis['subjects_still_showing_f']} subjects still show F grades")
            print(f"  📋 This could be because:")
            print(f"     - Students actually failed in supply exams too")
            print(f"     - Subject codes don't match between regular and supply PDFs")
            print(f"     - Supply PDF parsing issues")
            print(f"     - Different subject naming conventions")
            
            # Find most problematic codes
            worst_codes = sorted(
                subject_analysis['subject_code_summary'].items(),
                key=lambda x: x[1]['still_f_grade'],
                reverse=True
            )[:3]
            
            print(f"\n  🎯 Priority codes to investigate:")
            for code, summary in worst_codes:
                if summary['still_f_grade'] > 0:
                    main_name = list(summary['subject_names'])[0] if summary['subject_names'] else 'Unknown'
                    print(f"     - {code}: {summary['still_f_grade']} F grades ({main_name})")
        
        if subject_analysis['subjects_with_supply_grades'] > 0:
            print(f"\n  ✅ {subject_analysis['subjects_with_supply_grades']} subjects successfully improved!")
            print(f"  🎉 System is working correctly for these subjects")
        
        print(f"\n🏁 Analysis complete! Check the report: {report_file}")
        
        return report_file
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result_file = analyze_all_subjects()
    if result_file:
        print(f"\n📋 Complete subject analysis done! Check: {result_file}")
        print(f"🔍 This shows which subject codes are working and which need attention.")
    else:
        print(f"\n💥 Analysis failed.")
