"""
analyzer.py
Contains core logic: calculations, validations, file I/O, and data visualization.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = "data"
REPORT_DIR = "reports"
FILE_NAME = os.path.join(DATA_DIR, "student_records.csv")

# Configurable subject list
SUBJECTS = ["Math", "Science", "English", "History", "Computer"]
MAX_MARKS_PER_SUBJECT = 100
TOTAL_MAX_MARKS = len(SUBJECTS) * MAX_MARKS_PER_SUBJECT


def initialize_directories() -> None:
    """Ensure data and report directories exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)


def calculate_grade(percentage: float) -> str:
    """Assigns letter grades using an if-elif-else ladder."""
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"


def get_valid_float(prompt: str, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Prompt user for a float with input boundary checks and exception handling."""
    while True:
        try:
            raw = input(prompt).strip()
            val = float(raw)
            if min_val <= val <= max_val:
                return val
            print(f"[Error] Value must be between {min_val} and {max_val}.")
        except ValueError:
            print("[Error] Invalid entry. Please enter a valid decimal or integer number.")


def get_valid_int(prompt: str, min_val: int = 0) -> int:
    """Prompt user for an integer with input boundary checks and exception handling."""
    while True:
        try:
            raw = input(prompt).strip()
            val = int(raw)
            if val >= min_val:
                return val
            print(f"[Error] Value must be at least {min_val}.")
        except ValueError:
            print("[Error] Invalid entry. Please enter a whole integer.")


def load_data() -> pd.DataFrame:
    """Loads student records from CSV into a pandas DataFrame."""
    initialize_directories()
    columns = [
        "Roll_No",
        "Name",
        *SUBJECTS,
        "Total_Marks",
        "Average",
        "Percentage",
        "Grade",
        "Classes_Attended",
        "Total_Classes",
        "Attendance_Pct",
    ]

    if os.path.exists(FILE_NAME):
        try:
            df = pd.read_csv(FILE_NAME)
            return df
        except Exception as e:
            print(f"[Warning] Failed to read {FILE_NAME}: {e}. Initializing empty dataset.")

    return pd.DataFrame(columns=columns)


def save_data(df: pd.DataFrame) -> None:
    """Saves DataFrame records back to CSV."""
    initialize_directories()
    df.to_csv(FILE_NAME, index=False)
    print(f"[Success] Data successfully synchronized to '{FILE_NAME}'.")


def add_student_record(df: pd.DataFrame) -> pd.DataFrame:
    """Collects student metrics, applies NumPy/Pandas analysis, and appends the row."""
    print("\n" + "=" * 40)
    print("      ADD NEW STUDENT RECORD")
    print("=" * 40)

    # Unique Roll Number Validation
    while True:
        roll_no = input("Enter Roll Number / ID: ").strip()
        if not roll_no:
            print("[Error] Roll number cannot be blank.")
            continue
        if not df.empty and str(roll_no) in df["Roll_No"].astype(str).values:
            print(f"[Error] Student with Roll No '{roll_no}' already exists.")
            continue
        break

    # Student Name
    while True:
        name = input("Enter Student Name: ").strip()
        if name:
            break
        print("[Error] Student name cannot be blank.")

    # Collect Marks per Subject
    marks = {}
    print("\n--- Enter Subject Marks (Out of 100) ---")
    for sub in SUBJECTS:
        marks[sub] = get_valid_float(f"  {sub}: ", 0.0, float(MAX_MARKS_PER_SUBJECT))

    # Collect Attendance
    print("\n--- Enter Attendance Details ---")
    total_classes = get_valid_int("  Total Classes Held: ", min_val=1)
    while True:
        classes_attended = get_valid_int("  Classes Attended: ", min_val=0)
        if classes_attended <= total_classes:
            break
        print(f"[Error] Classes attended ({classes_attended}) cannot exceed total classes ({total_classes}).")

    # NumPy calculations
    marks_array = np.array(list(marks.values()), dtype=float)
    total_marks = float(np.sum(marks_array))
    average = float(np.mean(marks_array))
    percentage = (total_marks / TOTAL_MAX_MARKS) * 100.0
    grade = calculate_grade(percentage)
    attendance_pct = (classes_attended / total_classes) * 100.0

    new_record = {
        "Roll_No": roll_no,
        "Name": name,
        **marks,
        "Total_Marks": round(total_marks, 2),
        "Average": round(average, 2),
        "Percentage": round(percentage, 2),
        "Grade": grade,
        "Classes_Attended": classes_attended,
        "Total_Classes": total_classes,
        "Attendance_Pct": round(attendance_pct, 2),
    }

    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    save_data(df)
    print(f"\n[Success] Record for '{name}' (Roll No: {roll_no}) saved.")
    return df


def display_all(df: pd.DataFrame) -> None:
    """Formats and prints entire dataset."""
    if df.empty:
        print("\n[Notice] No student records on file.")
        return
    print("\n" + "=" * 80)
    print("                     CURRENT STUDENT DATABASE")
    print("=" * 80)
    print(df.to_string(index=False))


def display_sorted_by_marks(df: pd.DataFrame) -> None:
    """Ranks students by total marks descending."""
    if df.empty:
        print("\n[Notice] Database is empty. Nothing to rank.")
        return
    sorted_df = df.sort_values(by="Total_Marks", ascending=False).reset_index(drop=True)
    display_cols = ["Roll_No", "Name", "Total_Marks", "Percentage", "Grade", "Attendance_Pct"]
    print("\n" + "=" * 60)
    print("            LEADERBOARD (SORTED BY TOTAL MARKS)")
    print("=" * 60)
    print(sorted_df[display_cols].to_string(index=True))


def filter_low_attendance(df: pd.DataFrame) -> None:
    """Identifies and displays students below a custom attendance threshold."""
    if df.empty:
        print("\n[Notice] Database is empty. Cannot filter attendance.")
        return

    threshold = get_valid_float("\nEnter Minimum Attendance Cutoff (%) [e.g., 75]: ", 0.0, 100.0)
    defaulters = df[df["Attendance_Pct"] < threshold].copy()

    print("\n" + "=" * 60)
    print(f"       STUDENTS WITH ATTENDANCE BELOW {threshold:.1f}%")
    print("=" * 60)

    if defaulters.empty:
        print(f"Great news! All students met or exceeded {threshold:.1f}% attendance.")
    else:
        cols = ["Roll_No", "Name", "Classes_Attended", "Total_Classes", "Attendance_Pct", "Grade"]
        print(defaulters[cols].to_string(index=False))


def generate_visual_reports(df: pd.DataFrame) -> None:
    """
    Renders 3 side-by-side plots:
    1. Bar Chart: Student Marks Comparison
    2. Line Graph: Subject-wise Class Averages
    3. Histogram: Overall Percentage Distribution
    """
    if df.empty:
        print("\n[Notice] Not enough records available to plot graphs.")
        return

    # Create figure layout
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.canvas.manager.set_window_title("Student Analytics Dashboard")
    fig.suptitle("Student Academic & Attendance Analytics", fontsize=15, fontweight="bold")

    # 1. Bar Chart: Total Marks per Student
    names = df["Name"].astype(str)
    bars = axes[0].bar(names, df["Total_Marks"], color="#2b5c8f", edgecolor="black", width=0.5)
    axes[0].set_title("Total Marks per Student", fontweight="semibold")
    axes[0].set_xlabel("Student Name")
    axes[0].set_ylabel(f"Total Marks (Max {TOTAL_MAX_MARKS})")
    axes[0].tick_params(axis="x", rotation=35)
    axes[0].grid(axis="y", linestyle="--", alpha=0.6)
    
    # Add data labels atop bars
    for bar in bars:
        height = bar.get_height()
        axes[0].annotate(f"{height:.0f}",
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3),
                         textcoords="offset points",
                         ha="center", va="bottom", fontsize=8)

    # 2. Line Graph: Subject-Wise Class Average
    subject_means = [df[sub].mean() for sub in SUBJECTS]
    axes[1].plot(SUBJECTS, subject_means, marker="o", color="#d9534f", linewidth=2.5, markersize=8)
    axes[1].set_title("Subject-wise Class Average", fontweight="semibold")
    axes[1].set_xlabel("Subject")
    axes[1].set_ylabel("Average Score (%)")
    axes[1].set_ylim(0, 105)
    axes[1].grid(True, linestyle="--", alpha=0.6)
    
    for x, y in zip(SUBJECTS, subject_means):
        axes[1].annotate(f"{y:.1f}", xy=(x, y), xytext=(0, 6),
                         textcoords="offset points", ha="center", fontsize=8, fontweight="bold")

    # 3. Histogram: Percentage Distribution
    bins = [0, 40, 50, 60, 70, 80, 90, 100]
    axes[2].hist(df["Percentage"], bins=bins, color="#5cb85c", edgecolor="black")
    axes[2].set_title("Distribution of Student Percentages", fontweight="semibold")
    axes[2].set_xlabel("Percentage Range (%)")
    axes[2].set_ylabel("Number of Students")
    axes[2].set_xticks(bins)
    axes[2].grid(axis="y", linestyle="--", alpha=0.6)

    plt.tight_layout()

    # Save export and present interactive window
    export_path = os.path.join(REPORT_DIR, "performance_summary.png")
    plt.savefig(export_path, dpi=300)
    print(f"\n[Success] Report graphic saved locally to '{export_path}'.")
    plt.show()