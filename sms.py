import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import sys
import re

# Constants
DATA_FILE = "student_data.json"
DATE_FORMAT = "%Y-%m-%d"


class MenuOption(Enum):
    ADD_STUDENT = 1
    VIEW_STUDENTS = 2
    UPDATE_STUDENT = 3
    DELETE_STUDENT = 4
    ENROLL_COURSE = 5
    RECORD_GRADE = 6
    GENERATE_REPORT = 7
    SEARCH_STUDENTS = 8
    EXIT = 9


@dataclass
class Grade:
    course_id: str
    grade: float
    date_recorded: str


@dataclass
class Enrollment:
    course_id: str
    enrollment_date: str
    completed: bool = False


@dataclass
class Student:
    student_id: str
    first_name: str
    last_name: str
    email: str
    date_of_birth: str
    enrollments: List[Enrollment] = None
    grades: List[Grade] = None

    def __post_init__(self):
        if self.enrollments is None:
            self.enrollments = []
        if self.grades is None:
            self.grades = []


class StudentManagementSystem:
    def __init__(self):
        self.students: Dict[str, Student] = {}
        self.load_data()

    def load_data(self):
        """Load student data from JSON file if it exists"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as file:
                    data = json.load(file)
                    for student_id, student_data in data.items():
                        enrollments = [Enrollment(**e) for e in student_data.get('enrollments', [])]
                        grades = [Grade(**g) for g in student_data.get('grades', [])]
                        self.students[student_id] = Student(
                            student_id=student_id,
                            first_name=student_data['first_name'],
                            last_name=student_data['last_name'],
                            email=student_data['email'],
                            date_of_birth=student_data['date_of_birth'],
                            enrollments=enrollments,
                            grades=grades
                        )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading data: {e}. Starting with empty database.")

    def save_data(self):
        """Save student data to JSON file"""
        data = {student_id: asdict(student) for student_id, student in self.students.items()}
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file, indent=2)

    def generate_student_id(self) -> str:
        """Generate a unique student ID"""
        existing_ids = [int(sid) for sid in self.students.keys() if sid.isdigit()]
        new_id = max(existing_ids) + 1 if existing_ids else 1000
        return str(new_id)

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_date(self, date_str: str) -> bool:
        """Validate date format (YYYY-MM-DD)"""
        try:
            datetime.strptime(date_str, DATE_FORMAT)
            return True
        except ValueError:
            return False

    def add_student(self):
        """Add a new student to the system"""
        print("\n" + "=" * 50)
        print("ADD NEW STUDENT".center(50))
        print("=" * 50)

        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()

        while True:
            email = input("Email: ").strip()
            if self.validate_email(email):
                break
            print("Invalid email format. Please try again.")

        while True:
            dob = input("Date of Birth (YYYY-MM-DD): ").strip()
            if self.validate_date(dob):
                break
            print("Invalid date format. Please use YYYY-MM-DD.")

        student_id = self.generate_student_id()
        new_student = Student(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            date_of_birth=dob
        )

        self.students[student_id] = new_student
        self.save_data()

        print(f"\nStudent added successfully! Student ID: {student_id}")
        self._press_enter_to_continue()

    def view_students(self, students: Optional[List[Student]] = None):
        """Display a list of students"""
        students_to_display = students if students is not None else list(self.students.values())

        print("\n" + "=" * 100)
        print("STUDENT RECORDS".center(100))
        print("=" * 100)
        print(f"{'ID':<10}{'Name':<25}{'Email':<30}{'DOB':<15}{'Courses':<20}")
        print("-" * 100)

        for student in students_to_display:
            name = f"{student.first_name} {student.last_name}"
            course_count = len(student.enrollments)
            print(f"{student.student_id:<10}{name:<25}{student.email:<30}{student.date_of_birth:<15}{course_count:<20}")

        print("=" * 100)
        self._press_enter_to_continue()

    def update_student(self):
        """Update student information"""
        student_id = input("Enter student ID to update: ").strip()
        student = self.students.get(student_id)

        if not student:
            print("Student not found!")
            self._press_enter_to_continue()
            return

        print("\nCurrent Student Information:")
        print(f"1. First Name: {student.first_name}")
        print(f"2. Last Name: {student.last_name}")
        print(f"3. Email: {student.email}")
        print(f"4. Date of Birth: {student.date_of_birth}")

        field = input("\nEnter field number to update (1-4) or '0' to cancel: ").strip()

        if field == '0':
            return

        if field == '1':
            student.first_name = input("Enter new first name: ").strip()
        elif field == '2':
            student.last_name = input("Enter new last name: ").strip()
        elif field == '3':
            while True:
                new_email = input("Enter new email: ").strip()
                if self.validate_email(new_email):
                    student.email = new_email
                    break
                print("Invalid email format. Please try again.")
        elif field == '4':
            while True:
                new_dob = input("Enter new date of birth (YYYY-MM-DD): ").strip()
                if self.validate_date(new_dob):
                    student.date_of_birth = new_dob
                    break
                print("Invalid date format. Please use YYYY-MM-DD.")
        else:
            print("Invalid field number!")
            self._press_enter_to_continue()
            return

        self.save_data()
        print("Student information updated successfully!")
        self._press_enter_to_continue()

    def delete_student(self):
        """Delete a student from the system"""
        student_id = input("Enter student ID to delete: ").strip()

        if student_id in self.students:
            confirm = input(f"Are you sure you want to delete student {student_id}? (y/n): ").lower()
            if confirm == 'y':
                del self.students[student_id]
                self.save_data()
                print("Student deleted successfully!")
            else:
                print("Deletion cancelled.")
        else:
            print("Student not found!")

        self._press_enter_to_continue()

    def enroll_course(self):
        """Enroll a student in a course"""
        student_id = input("Enter student ID: ").strip()
        student = self.students.get(student_id)

        if not student:
            print("Student not found!")
            self._press_enter_to_continue()
            return

        course_id = input("Enter course ID: ").strip()
        today = datetime.now().strftime(DATE_FORMAT)

        # Check if already enrolled
        if any(e.course_id == course_id for e in student.enrollments):
            print("Student is already enrolled in this course!")
            self._press_enter_to_continue()
            return

        student.enrollments.append(Enrollment(course_id=course_id, enrollment_date=today))
        self.save_data()
        print(f"Student {student_id} enrolled in course {course_id} successfully!")
        self._press_enter_to_continue()

    def record_grade(self):
        """Record a grade for a student in a course"""
        student_id = input("Enter student ID: ").strip()
        student = self.students.get(student_id)

        if not student:
            print("Student not found!")
            self._press_enter_to_continue()
            return

        # Check if student is enrolled in any courses
        if not student.enrollments:
            print("Student is not enrolled in any courses!")
            self._press_enter_to_continue()
            return

        print("\nCourses enrolled:")
        for i, enrollment in enumerate(student.enrollments, 1):
            print(f"{i}. {enrollment.course_id} (Enrolled: {enrollment.enrollment_date})")

        try:
            selection = int(input("Select course to record grade for (number): ")) - 1
            if 0 <= selection < len(student.enrollments):
                course_id = student.enrollments[selection].course_id

                # Check if grade already exists for this course
                existing_grade = next((g for g in student.grades if g.course_id == course_id), None)
                if existing_grade:
                    print(f"Grade already recorded for this course: {existing_grade.grade}")
                    confirm = input("Overwrite? (y/n): ").lower()
                    if confirm != 'y':
                        return

                while True:
                    try:
                        grade = float(input("Enter grade (0-100): "))
                        if 0 <= grade <= 100:
                            break
                        print("Grade must be between 0 and 100.")
                    except ValueError:
                        print("Invalid grade. Please enter a number.")

                today = datetime.now().strftime(DATE_FORMAT)

                # Remove existing grade if it exists
                student.grades = [g for g in student.grades if g.course_id != course_id]

                student.grades.append(Grade(
                    course_id=course_id,
                    grade=grade,
                    date_recorded=today
                ))

                self.save_data()
                print("Grade recorded successfully!")
            else:
                print("Invalid selection!")
        except ValueError:
            print("Please enter a valid number.")

        self._press_enter_to_continue()

    def generate_report(self):
        """Generate a detailed report for a student"""
        student_id = input("Enter student ID: ").strip()
        student = self.students.get(student_id)

        if not student:
            print("Student not found!")
            self._press_enter_to_continue()
            return

        print("\n" + "=" * 70)
        print(f"STUDENT REPORT: {student.first_name} {student.last_name}".center(70))
        print("=" * 70)
        print(f"Student ID: {student.student_id}")
        print(f"Email: {student.email}")
        print(f"Date of Birth: {student.date_of_birth}")
        print("\n" + "-" * 70)
        print("COURSE ENROLLMENTS & GRADES".center(70))
        print("-" * 70)

        if not student.enrollments:
            print("No course enrollments found.")
        else:
            print(f"{'Course ID':<15}{'Enrollment Date':<20}{'Grade':<10}{'Status':<15}")
            print("-" * 70)

            for enrollment in student.enrollments:
                grade = next((g for g in student.grades if g.course_id == enrollment.course_id), None)
                grade_str = f"{grade.grade:.1f}" if grade else "N/A"
                status = "Completed" if grade else "In Progress"
                print(f"{enrollment.course_id:<15}{enrollment.enrollment_date:<20}{grade_str:<10}{status:<15}")

        # Calculate GPA if grades exist
        if student.grades:
            gpa = sum(g.grade for g in student.grades) / len(student.grades)
            print("\n" + "-" * 70)
            print(f"Overall GPA: {gpa:.2f}".center(70))

        print("=" * 70)
        self._press_enter_to_continue()

    def search_students(self):
        """Search for students by name or email"""
        search_term = input("Enter search term (name or email): ").strip().lower()

        if not search_term:
            print("Please enter a search term.")
            self._press_enter_to_continue()
            return

        results = []
        for student in self.students.values():
            full_name = f"{student.first_name} {student.last_name}".lower()
            if (search_term in full_name or
                    search_term in student.email.lower() or
                    search_term == student.student_id.lower()):
                results.append(student)

        if results:
            self.view_students(results)
        else:
            print("No matching students found.")
            self._press_enter_to_continue()

    def _press_enter_to_continue(self):
        """Utility method to pause execution until user presses Enter"""
        input("\nPress Enter to continue...")

    def display_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 50)
        print("STUDENT MANAGEMENT SYSTEM".center(50))
        print("=" * 50)
        print(f"{MenuOption.ADD_STUDENT.value}. Add New Student")
        print(f"{MenuOption.VIEW_STUDENTS.value}. View Students")
        print(f"{MenuOption.UPDATE_STUDENT.value}. Update Student Information")
        print(f"{MenuOption.DELETE_STUDENT.value}. Delete Student")
        print(f"{MenuOption.ENROLL_COURSE.value}. Enroll in Course")
        print(f"{MenuOption.RECORD_GRADE.value}. Record Grade")
        print(f"{MenuOption.GENERATE_REPORT.value}. Generate Student Report")
        print(f"{MenuOption.SEARCH_STUDENTS.value}. Search Students")
        print(f"{MenuOption.EXIT.value}. Exit")
        print("=" * 50)

    def run(self):
        """Main application loop"""
        while True:
            self.display_menu()

            try:
                choice = int(input("Enter your choice (1-9): "))
                menu_option = MenuOption(choice)

                if menu_option == MenuOption.ADD_STUDENT:
                    self.add_student()
                elif menu_option == MenuOption.VIEW_STUDENTS:
                    self.view_students()
                elif menu_option == MenuOption.UPDATE_STUDENT:
                    self.update_student()
                elif menu_option == MenuOption.DELETE_STUDENT:
                    self.delete_student()
                elif menu_option == MenuOption.ENROLL_COURSE:
                    self.enroll_course()
                elif menu_option == MenuOption.RECORD_GRADE:
                    self.record_grade()
                elif menu_option == MenuOption.GENERATE_REPORT:
                    self.generate_report()
                elif menu_option == MenuOption.SEARCH_STUDENTS:
                    self.search_students()
                elif menu_option == MenuOption.EXIT:
                    print("Exiting Student Management System. Goodbye!")
                    break

            except ValueError:
                print("Invalid input. Please enter a number between 1 and 9.")
                self._press_enter_to_continue()


def main():
    """Entry point for the application"""
    system = StudentManagementSystem()
    try:
        system.run()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Saving data...")
        system.save_data()
        sys.exit(0)


if __name__ == "__main__":
    main()