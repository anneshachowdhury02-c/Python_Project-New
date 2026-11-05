"""
main.py
CLI driver for the Student Performance & Attendance Analyzer.
"""

import sys
from analyzer import (
    load_data,
    add_student_record,
    display_all,
    display_sorted_by_marks,
    filter_low_attendance,
    generate_visual_reports,
)


def print_menu() -> None:
    menu = """
==================================================
   STUDENT PERFORMANCE & ATTENDANCE ANALYZER
==================================================
 [1] Add New Student Record
 [2] View All Student Records
 [3] Rank Students by Total Marks (Sorted)
 [4] Identify Low Attendance Defaulters
 [5] Generate Graphical Reports (Bar, Line, Hist)
 [6] Exit
--------------------------------------------------"""
    print(menu)


def main():
    records_df = load_data()

    while True:
        print_menu()
        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            records_df = add_student_record(records_df)
        elif choice == "2":
            display_all(records_df)
        elif choice == "3":
            display_sorted_by_marks(records_df)
        elif choice == "4":
            filter_low_attendance(records_df)
        elif choice == "5":
            generate_visual_reports(records_df)
        elif choice == "6":
            print("\nExiting system. Have a great day!\n")
            sys.exit(0)
        else:
            print("\n[Error] Invalid option. Please choose a number between 1 and 6.")


if __name__ == "__main__":
    main()