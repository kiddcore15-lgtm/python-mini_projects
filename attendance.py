
import sqlite3
from datetime import date, datetime


class AttendanceSystem:

    def __init__(self):
        self.conn = sqlite3.connect("attendance.db")
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            course TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL,
            UNIQUE(student_id, attendance_date),
            FOREIGN KEY(student_id) REFERENCES students(id)
        );
        """)
        self.conn.commit()

    def add_student(self, name, roll_no, course):
        if not name.strip() or not roll_no.strip() or not course.strip():
            raise ValueError("All student details are required.")

        cursor = self.conn.execute("""
            INSERT INTO students(name, roll_no, course)
            VALUES (?, ?, ?)
        """, (name, roll_no, course))

        self.conn.commit()
        return cursor.lastrowid

    def view_students(self):
        return self.conn.execute(
            "SELECT * FROM students ORDER BY id"
        ).fetchall()

    def mark_attendance(self, student_id, status, attendance_date):
        try:
            datetime.strptime(attendance_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be YYYY-MM-DD.")

        status = status.capitalize()

        if status not in ["Present", "Absent"]:
            raise ValueError("Status must be Present or Absent.")

        student = self.conn.execute(
            "SELECT id FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

        if not student:
            raise ValueError("Student ID not found.")

        self.conn.execute("""
            INSERT INTO attendance
            (student_id, attendance_date, status)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, attendance_date)
            DO UPDATE SET status = excluded.status
        """, (student_id, attendance_date, status))

        self.conn.commit()

    def daily_attendance(self, attendance_date):
        return self.conn.execute("""
            SELECT students.name, students.roll_no,
                   students.course, attendance.status
            FROM attendance
            JOIN students ON students.id = attendance.student_id
            WHERE attendance.attendance_date = ?
            ORDER BY students.roll_no
        """, (attendance_date,)).fetchall()

    def student_report(self, student_id):
        student = self.conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

        if not student:
            raise ValueError("Student not found.")

        records = self.conn.execute("""
            SELECT attendance_date, status
            FROM attendance
            WHERE student_id = ?
            ORDER BY attendance_date
        """, (student_id,)).fetchall()

        total = len(records)
        present = sum(1 for r in records if r["status"] == "Present")
        absent = total - present

        percentage = (present / total * 100) if total else 0

        return student, records, total, present, absent, percentage

    def monthly_report(self, month):
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise ValueError("Enter month in YYYY-MM format.")

        return self.conn.execute("""
            SELECT students.name, students.roll_no,
                   COUNT(*) AS total,
                   SUM(CASE WHEN attendance.status = 'Present'
                       THEN 1 ELSE 0 END) AS present
            FROM attendance
            JOIN students ON students.id = attendance.student_id
            WHERE substr(attendance.attendance_date, 1, 7) = ?
            GROUP BY students.id
            ORDER BY students.roll_no
        """, (month,)).fetchall()

    def close(self):
        self.conn.close()


system = AttendanceSystem()


def menu():
    print("\n" + "=" * 48)
    print("       STUDENT ATTENDANCE MANAGEMENT")
    print("=" * 48)
    print("1. Add Student")
    print("2. View All Students")
    print("3. Mark Attendance")
    print("4. View Daily Attendance")
    print("5. Student Attendance Report")
    print("6. Monthly Attendance Report")
    print("0. Exit")
    print("=" * 48)


def main():
    print("Welcome to Attendance Management System!")

    while True:
        menu()
        choice = input("Enter your choice: ").strip()

        try:

            if choice == "1":
                name = input("Student Name: ")
                roll = input("Roll Number: ")
                course = input("Course: ")

                student_id = system.add_student(
                    name, roll, course
                )

                print("Student added successfully!")
                print("Student ID:", student_id)

            elif choice == "2":
                students = system.view_students()

                print("\nSTUDENT DETAILS")

                for s in students:
                    print(
                        "ID:", s["id"],
                        "| Name:", s["name"],
                        "| Roll No:", s["roll_no"],
                        "| Course:", s["course"]
                    )

                if not students:
                    print("No students registered.")

            elif choice == "3":
                student_id = int(input("Student ID: "))

                status = input(
                    "Attendance (Present/Absent): "
                )

                attendance_date = input(
                    "Date (YYYY-MM-DD) [Enter for today]: "
                ).strip()

                if not attendance_date:
                    attendance_date = date.today().isoformat()

                system.mark_attendance(
                    student_id, status, attendance_date
                )

                print("Attendance saved successfully!")

            elif choice == "4":
                attendance_date = input(
                    "Enter Date (YYYY-MM-DD): "
                )

                records = system.daily_attendance(
                    attendance_date
                )

                print("\nDAILY ATTENDANCE")

                for r in records:
                    print(
                        r["roll_no"],
                        r["name"],
                        r["course"],
                        r["status"]
                    )

                if not records:
                    print("No attendance records found.")

            elif choice == "5":
                student_id = int(input("Student ID: "))

                student, records, total, present, absent, percentage = (
                    system.student_report(student_id)
                )

                print("\nSTUDENT ATTENDANCE REPORT")
                print("Name:", student["name"])
                print("Roll Number:", student["roll_no"])
                print("Course:", student["course"])
                print("Total Classes:", total)
                print("Present:", present)
                print("Absent:", absent)
                print("Attendance Percentage: {:.2f}%".format(percentage))

                for r in records:
                    print(r["attendance_date"], r["status"])

            elif choice == "6":
                month = input("Enter Month (YYYY-MM): ")

                records = system.monthly_report(month)

                print("\nMONTHLY ATTENDANCE REPORT")

                for r in records:
                    percentage = (
                        r["present"] / r["total"] * 100
                        if r["total"] else 0
                    )

                    print(
                        "Roll:", r["roll_no"],
                        "| Name:", r["name"],
                        "| Present:", r["present"],
                        "| Total:", r["total"],
                        "| Percentage: {:.2f}%".format(percentage)
                    )

                if not records:
                    print("No monthly records found.")

            elif choice == "0":
                print("Thank you for using the system!")
                break

            else:
                print("Invalid choice!")

        except ValueError as error:
            print("Input Error:", error)

        except sqlite3.IntegrityError:
            print("This student or attendance record already exists.")

        except sqlite3.Error as error:
            print("Database Error:", error)

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    finally:
        system.close()
