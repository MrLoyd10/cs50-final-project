import sqlite3
from flask import flash

def getNaming(gradelvl, subject, criteria, current_user):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()

        query = f"""
            SELECT MAX(CAST(SUBSTR(title, 2) AS INTEGER)) AS highest_number_title
            FROM grades_description
            WHERE title LIKE '#%'
                AND grade_level = ? 
                AND subject = ? 
                AND criteria = ?
                AND user_id = ?;
        """
        
        cursor.execute(query, (gradelvl, subject, criteria, current_user))

        result = cursor.fetchone()
        if result[0] == 0 or result[0] is None:
            return 1
        else:
            return result[0] + 1
        
    except Exception as e:
        flash(f"Error: {e}", "danger")
    finally:
        conn.close()

def getStudentByGrade(gradeLvl, current_user):
    try:
        conn = sqlite3.connect('schoolManager.db')
        conn.row_factory = sqlite3.Row  # Set make it dictionary
        cursor = conn.cursor()
        
        cursor.execute("SELECT student_id, last_name, first_name FROM students WHERE grade_level = ? AND user_id = ? ORDER BY last_name;", (gradeLvl, current_user))
        dict_students = cursor.fetchall()
        
        return dict_students
        
    except Exception as e:
        flash(f"Error: {e}", "danger")
    finally:
        conn.close()



def createGradeDescription(criteria, subject, gradeLvl, title, highScore, current_user):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO grades_description (subject, criteria, grade_level, title, highest_score, user_id) " +
                       "VALUES (?, ?, ?, ?, ?, ?)", (subject, criteria, gradeLvl, title, highScore, current_user))
        
        # Get the ID of the last inserted row
        grade_description_id = cursor.lastrowid
    
        conn.commit()  # Commit the changes

        return grade_description_id
        
    except Exception as e:
        flash(f"Error: {e}", "danger")
        
    finally:
        conn.close()


def insertGradeToDB(studentID, grade, description_id):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO grades (student_id, grade, grade_description) " +
                       "VALUES (?, ?, ?)", (studentID, grade, description_id))
        
        conn.commit()  # Commit the changes
        
    except Exception as e:
        flash(f"Error: {e}", "danger")
        
    finally:
        conn.close()

def addDefaultGrade(id, lvl, user):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM grades_description WHERE grade_level = ? AND user_id = ?", (lvl, user))
        activities = cursor.fetchall()

        for activity in activities:
            grade_description_id = activity[0]
            
            # Insert the default grade with the retrieved grade_description_id
            cursor.execute("INSERT INTO grades (student_id, grade, grade_description) VALUES (?, ?, ?)",
                           (id, 0, grade_description_id))
            conn.commit()
        
    except Exception as e:
        flash(f"Error: {e}", "danger")
    finally:
        conn.close()

# !! FINISH THIS SECTION

def getCriteria(current_user):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()

        cursor.execute("SELECT performance, recitation, seatwork, exam FROM criteria WHERE user_id = ?", (current_user,))
        result = cursor.fetchone()
        
        if result is None:
            return 0, 0, 0, 0;
        else:
            return result;
        
    except Exception as e:
        flash(f"Error: {e}", "danger")

    finally:
        conn.close()

def putGradeToDB(student_id, current_user, criteria, grade, subject):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM final_grade WHERE student_id = ? AND user_id = ? AND subject = ?", 
                       (student_id, current_user, subject))
        result = cursor.fetchone()
        

        if result:  #UPDATE
            update_query = f"UPDATE final_grade SET {criteria} = ? WHERE id = ?"
            cursor.execute(update_query, (grade, result[0]))

        else:       #INSERT
            insert_query = f"INSERT INTO final_grade (student_id, {criteria}, subject, user_id) VALUES (?, ?, ?, ?)"
            cursor.execute(insert_query, (student_id, grade, subject, current_user))
        
        conn.commit()
        
    except Exception as e:
        flash(f"Error: {e}", "danger")

    finally:
        conn.close()


def TRANSMULATED_GRADE(initial_grade):
    grade_ranges = {
        (0, 3.99): 60,
        (4, 7.99): 61,
        (8, 11.99): 62,
        (12, 15.99): 63,
        (16, 19.99): 64,
        (20, 23.99): 65,
        (24, 27.99): 66,
        (28, 31.99): 67,
        (32, 35.99): 68,
        (36, 39.99): 69,
        (40, 43.99): 70,
        (44, 47.99): 71,
        (48, 51.99): 72,
        (52, 55.99): 73,
        (56, 59.99): 74,
        (60, 61.59): 75,
        (61.6, 63.19): 76,
        (63.2, 64.79): 77,
        (64.8, 66.39): 78,
        (66.4, 67.99): 79,
        (68, 69.59): 80,
        (69.6, 71.19): 81,
        (71.2, 72.79): 82,
        (72.8, 74.39): 83,
        (74.4, 75.99): 84,
        (76, 77.59): 85,
        (77.6, 79.19): 86,
        (79.2, 80.79): 87,
        (80.8, 82.39): 88,
        (82.4, 83.99): 89,
        (84, 85.59): 90,
        (85.6, 87.19): 91,
        (87.2, 88.79): 92,
        (88.8, 90.39): 93,
        (90.4, 91.99): 94,
        (92, 93.59): 95,
        (93.6, 95.19): 96,
        (95.2, 96.79): 97,
        (96.8, 98.39): 98,
        (98.4, 99.99): 99,
        (100, 100): 100
    }

    for grade_range, transmuted_grade in grade_ranges.items():
        start, end = grade_range
        if start <= initial_grade <= end:
            return transmuted_grade

    return None  # Default value if the initial grade doesn't match any specified range

def InitialAndTransmulatedUpdater(current_user):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id, performance, seatwork, recitation, exam FROM final_grade WHERE user_id = ?", (current_user,))
        results = cursor.fetchall()
        
        for result in results:
            id, perf, seat, reci, exam = result
            initial_grade = round(perf + seat + reci + exam, 2)
            transmulated_grade = TRANSMULATED_GRADE(initial_grade)
            
            cursor.execute("UPDATE final_grade SET initial_grade = ?, transmulated_grade = ? WHERE id = ?", 
                           (initial_grade, transmulated_grade, id))
            conn.commit()

    except Exception as e:
        flash(f"Error: {e}", "danger")

    finally:
        conn.close()


def getGrades(grade_level, subject, current_user, criteria):

    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()
        
        activity_query = (
            "SELECT id, title, highest_score FROM grades_description WHERE grade_level = ? AND subject = ? AND user_id = ? AND criteria = ?",
            (grade_level, subject, current_user, criteria)
        )
        cursor.execute(*activity_query)
        results = cursor.fetchall()
        
        activities = [{'id': id, 'title': title, 'highest': highest_score} for id, title, highest_score in results]
        total_highest_score = sum(activity['highest'] for activity in activities)


        # Assuming activities is a list of dictionaries with 'id' as the key
        activity_ids = [activity['id'] for activity in activities]

        # Convert the list of activity IDs to a string for the SQL query
        activity_ids_str = ','.join(map(str, activity_ids))
        
        # Get student grades and names
        grades_query = (
            "SELECT grades.student_id, students.first_name, students.last_name, grades.grade, grades.grade_description "
            "FROM grades "
            "JOIN students ON grades.student_id = students.student_id "
            "WHERE grades.grade_description IN ({}) "
            "ORDER BY students.last_name"
            .format(activity_ids_str)
        )
        cursor.execute(grades_query)
        grades_results = cursor.fetchall()

        # Organize data into a dictionary
        student_grades = {}
        for result in grades_results:
            student_id, first_name, last_name, grade, grade_description = result
            student_name = f"{last_name}, {first_name}"

            if student_name not in student_grades:
                student_grades[student_name] = {'grades': [], 'student_id': student_id}

            student_grades[student_name]['grades'].append({
                'grade_description': grade_description,
                'grade': grade
            })

        for student_name, grades_data in student_grades.items():
            total_grade = sum(grade['grade'] for grade in grades_data['grades'])
            format_total = round(total_grade/total_highest_score * 100, 2)
            grades_data['total_grade'] = format_total
        
        return activities, student_grades

    except Exception as e:
        flash(f"Error: {e}", "danger")
        return [], {}
        
    finally:
        conn.close()


def updateGrade(student_id, grade_description, updated_grade):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()

        cursor.execute("UPDATE grades SET grade = ? WHERE student_id = ? AND grade_description = ?", 
                       (updated_grade, student_id, grade_description))

        conn.commit()
        return {'message': 'Grade updated successfully', 'status': 'success'}

    except Exception as e:
        return {'message': f'Error: {e}', 'status': 'danger'}

    finally:
        conn.close()

def getUpdatedInitialAndTransmulated(student_id, subject, user_id):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()

        cursor.execute("SELECT initial_grade, transmulated_grade FROM final_grade final "
               "WHERE student_id = ? AND subject = ? AND user_id = ?", (student_id, subject, user_id))

        results = cursor.fetchone()

        return {'initial': str(results[0]), 'transmulated': str(results[1])}

    except Exception as e:
        flash(f"Error: {e}", "danger")

    finally:
        conn.close()
    
    


def getFinalGrade(gradelvl, subject, current_user):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()

        cursor.execute("SELECT st.last_name, st.first_name, final.initial_grade, final.transmulated_grade, final.student_id "
               "FROM final_grade final "
               "JOIN students st ON st.student_id = final.student_id "
               "WHERE st.grade_level = ? AND final.subject = ? AND final.user_id = ? "
               "ORDER BY st.last_name",
               (gradelvl, subject, current_user))

        results = cursor.fetchall()

        return results

    except Exception as e:
        flash(f"Error: {e}", "danger")

    finally:
        conn.close()



def UpdateFinalGrade(subject, criteria, gradelvl, current_user, student_id):
    
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id, highest_score FROM grades_description "
                       "WHERE subject = ? AND criteria LIKE ? AND grade_level = ? AND user_id = ?", 
                       (subject, criteria, gradelvl, current_user))

        grade_desc = cursor.fetchall()
        HighestScore = sum(desc[1] for desc in grade_desc)      #Highest score possible
        
        # WE DO THIS SO WE CAN ADD IT IN THE QUERY.
        grade_desc_ids = [desc[0] for desc in grade_desc]
        idToQuery = ','.join(map(str, grade_desc_ids))
        

        queryForGrade = f"SELECT grade FROM grades WHERE student_id = ? AND grade_description IN ({idToQuery})";
        cursor.execute(queryForGrade, (student_id,));
        grades = cursor.fetchall()
        UserScore = sum(grade[0] for grade in grades)        #User score

        if (criteria == "examination"):
            criteria = "exam"

        queryCriteria = f"SELECT {criteria.lower()} FROM criteria WHERE user_id = ?"
        cursor.execute(queryCriteria, (current_user,))
        criteriPercent = cursor.fetchone();

        updatedGrade = round((UserScore/HighestScore * 100) * (criteriPercent[0]/100), 2)

        queryUpdateFinalGrade = f"UPDATE final_grade SET {criteria} = ? WHERE student_id = ? AND subject = ? AND user_id = ?"
        cursor.execute(queryUpdateFinalGrade, (updatedGrade, student_id, subject, current_user))

        conn.commit()

    except Exception as e:
        flash(f"Error: {e}", "danger")

    finally:
        conn.close()


def getTopThree(current):
    try:
        conn = sqlite3.connect('schoolManager.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT st.first_name, st.last_name, fg.transmulated_grade
            FROM final_grade fg 
            JOIN students st ON fg.student_id = st.student_id 
            WHERE fg.user_id = ?
            ORDER BY fg.initial_grade DESC
            LIMIT 3;
        """, (current,))

        # Fetch the results
        results = cursor.fetchall()
        return results

    except Exception as e:
        flash(f"Error: {e}", "danger")

    finally:
        conn.close()