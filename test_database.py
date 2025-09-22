#!/usr/bin/env python3
"""
Test script to verify database migration results
"""
import sqlite3
import sys

def test_database():
    try:
        # Connect to database
        conn = sqlite3.connect('sky_hr_payslips.db')
        cursor = conn.cursor()

        # Check employee count
        cursor.execute('SELECT COUNT(*) FROM employees')
        count = cursor.fetchone()[0]
        print(f"✅ Total employees in database: {count}")

        # Test specific employee 985
        cursor.execute('SELECT hrid, name, nid FROM employees WHERE hrid = "985" LIMIT 1')
        employee = cursor.fetchone()
        if employee:
            print(f"✅ Employee 985 data: HRID={employee[0]}, Name={employee[1]}, NID={employee[2]}")
        else:
            print("❌ Employee 985 not found")

        # Show first 3 employees
        cursor.execute('SELECT hrid, name, nid FROM employees LIMIT 3')
        employees = cursor.fetchall()
        print("✅ Sample employee data:")
        for emp in employees:
            print(f"   HRID: {emp[0]}, Name: {emp[1]}, NID: {emp[2]}")

        # Check table structure
        cursor.execute('PRAGMA table_info(employees)')
        columns = cursor.fetchall()
        print("✅ Database table structure:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")

        conn.close()
        print("✅ Database test completed successfully")
        return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
