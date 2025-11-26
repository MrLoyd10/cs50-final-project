import sqlite3
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash

def isStudentExist(lname, fname, grade, current_user):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.execute('SELECT count(*) FROM students WHERE last_name LIKE ? ' + 
                              'AND first_name LIKE ? AND grade_level LIKE ? AND user_id = ?',
                              (lname, fname, grade, current_user))
        count = cursor.fetchone()[0]
        
        if count > 0:
            return True
        else:
            return False
    except Exception as e:
        return flash(f"Error: {e}", "danger")
    finally:
        conn.close()

def isUserExist(username, password):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_info = cursor.fetchone()

        # Check if user exists first
        if user_info is None:
            return None
        
        # Then check if the password is correct
        if check_password_hash(user_info[2], password):
            return user_info  # Return user information as a tuple
        else:
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def getUserById(user_id):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_info = cursor.fetchone()

        if user_info is not None:
            return {
                'id': user_info[0],
                'username': user_info[1],
                'password': user_info[2],
                'name': user_info[3],
                'profile': user_info[4]
            }
        else:
            return None

    except Exception as e:
        # You should handle the exception appropriately, e.g., logging the error
        print(f"Error: {e}")
        return None

    finally:
        conn.close()

def registerUser(name, username, password, profile_path):
    conn = None  # initialize conn
    try:
        secured_pass = generate_password_hash(password, method='pbkdf2:sha256')
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (name, username, password, picture) VALUES (?, ?, ?, ?)',
            (name, username, secured_pass, profile_path)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:  # only close if conn exists
            conn.close()

def isUsernameExist(username):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user is not None:
            return True
        else:
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

    finally:
        conn.close()

#CRITERIA SECTION
def insertCriteria(user_id, perf, reci, seat, exam):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO criteria (user_id, performance, recitation, seatwork, exam) VALUES (?, ?, ?, ?, ?)",
                       (user_id, perf, reci, seat, exam))
        conn.commit()
        flash("Criteria is inserted successfully.", "success")

    except Exception as e:
        flash(f"Error: {e}", "danger")

    finally:
        conn.close()

def isCriteriaSet(user_id):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()

        # Check if user Criteria exist
        cursor.execute("SELECT * FROM criteria WHERE user_id = ?", (user_id,))
        exist_user = cursor.fetchone()
        
        # If it's empty, it's not set, so we return False so we can insert.
        if exist_user is None:
            return False
        return exist_user

    except Exception as e:
        flash(f"Error: {e}", "danger")

    finally:
        conn.close()

def updateCriteria(user_id, perf, reci, seat, exam):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()

        # Update
        cursor.execute("UPDATE criteria SET performance = ?, recitation = ?, seatwork = ?, exam = ? WHERE user_id = ?",
                       (perf, reci, seat, exam, user_id))
        conn.commit()
        flash("Criteria is updated successfully.", "success")

    except Exception as e:
        flash(f"Error: {e}", "danger")

    finally:
        conn.close()
# --------------