// Form search validation
(() => {
    'use strict'
  
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation')
  
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
      form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }
  
        form.classList.add('was-validated')
      }, false)
    })
})()


//Clear search function
function resetForm() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => form.classList.remove('was-validated'));
    $("#student_record_table").addClass("d-none");
    $('select[name="recordCriteria"]').val('');
    $('select[name="recordSubject"]').val('');
    $('select[name="recordGradeLvl"]').val('');
    $('input[name="recordTitle"]').val('');
    $('input[name="recordHighScore"]').val('');
    $('#studentRecordGrade tbody').empty();
    $('#submitGradesDisplay').remove();

    $('input[name="ShowRecordTitle"]').val('');
}

// Clear search button (reset)
$(document).ready(function(){
    $('#addRecord').click(function() {
        resetForm()
    });
});

//searching the student to add grade
$(document).ready(function() {
    function searchAndDisplay(data) {
        // Clear existing table content
        $('#studentRecordGrade tbody').empty();
        $('#submitGradesDisplay').remove();

        // If the data is empty
        if (data.length === 0) {
            let tableRow =
            '<tr>'+
                '<td colspan="8" class="text-center">' + "No student list available" + '</td>' +
            '</tr>';
            $('#studentRecordGrade tbody').append(tableRow);
        }

        else {
            // Iterate through the received data and update the table
            data.forEach(function(student) {
                // Generate HTML for a table row
                let tableRow =
                '<tr>'+
                    '<td class="d-none student_id">' + student.student_id + '</td>' +
                    '<td>' + student.last_name + '</td>' +
                    '<td>' + student.first_name + '</td>' + 
                    '<td class="p-0 align-middle bg-white">' +
                        '<input class="form-control form-control-sm rounded-0 shadow-none text-center bg-light-subtle border-0" type="text" pattern="[0-9]*" autocomplete="new-password">' +
                    '</td>' +
                '</tr>';
                // Append the row to the table body
                $('#studentRecordGrade tbody').append(tableRow);
            });
            const submitbtn =   
            '<div class="d-flex justify-content-center m-2" id="submitGradesDisplay">' +
                '<button type="button" class="btn btn-warning w-75" id="submitGrades">Submit Grades</button>' +
            '</div>';
            $('#studentRecordGrade').after(submitbtn);
        } 
    }

    $("#searchStudentForRecord").submit(function(event) {
        event.preventDefault();
        if (this.checkValidity()) {
            $("#student_record_table").removeClass("d-none");
            $.ajax({
                type: 'POST',
                url: '/search_student',
                data: $(this).serialize(),
                dataType: 'json',
                success: function(data) {
                    searchAndDisplay(data);
                },
                error: function(error) {
                    console.error('Error searching students:', error);
                }
            });
        } else {
            console.error('Form is not valid please fill all required field');
        }
    })
})



// Function for checking INPUTS if its valid for grades.
function validateInputsForGrades() {
    let inputsNotEmpty = true;
    const highestScore = parseInt($('input[name="recordHighScore"]').val())

    $('#studentRecordGrade tbody tr').each(function() {
        let input = $(this).find('input');
        let grade = parseInt($(this).find('input').val());

        if (input.val() === "" || grade > highestScore || grade < 0 || isNaN(grade)) {
            inputsNotEmpty = false;
            input.addClass('is-invalid'); // Add red border to empty input
        } else {
            input.removeClass('is-invalid'); // Remove red border from filled input
            input.addClass('is-valid')
        }
    });

    return inputsNotEmpty;
}


// GRADE SUBMITION
$(document).on('click', '#submitGrades', function() {

    // Check if its Valide inputs
    if (!validateInputsForGrades()) {
        addFlashMessage('Grades should not be higher than the highest score, not letters or not be empty.', "warning");
        return;
    }
    
    // Serialize the form data
    let formData = $('#searchStudentForRecord').serializeArray();

    // Prepare the grades data
    let gradesData = [];
    $('#studentRecordGrade tbody tr').each(function() {
        let studentID = $(this).find('.student_id').text();
        let grade = $(this).find('input').val();
        gradesData.push({ studentID: studentID, grade: grade });
    });

    // Combine both data into a single object
    formData.push({ name: 'gradesData', value: JSON.stringify(gradesData) });


    // Make an AJAX request to submit the grade to the server
    $.ajax({
        type: 'POST',
        url: '/record',
        data: formData,
        dataType: 'json',
        success: function(response) {
            console.log(response.message);
            addFlashMessage('The grades have been successfully recorded for all students.', 'success');
        },
        error: function(error) {
            console.error('Error submitting grade:', error);
            addFlashMessage(`Theres an error submitting grades: ${error}`, "danger");
        }
    });

    //clear table and some inputs.
    resetForm();
});



// Naming
function performCheck() {
    // Get the values of criteria, subject, and grade level
    let criteria = document.getElementsByName('recordCriteria')[0].value;
    let subject = document.getElementsByName('recordSubject')[0].value;
    let gradeLevel = document.getElementsByName('recordGradeLvl')[0].value;

    // Check if criteria, subject, and grade level are not empty
    if (criteria !== '' && subject !== '' && gradeLevel !== '') {
        $.ajax({
            type: 'POST',
            url: '/naming',
            data: { criteria: criteria, subject: subject, gradeLevel: gradeLevel},
            success: function(response) {
                named = "#" + response;
                document.querySelector('[name="recordTitle"]').value = named;
                document.querySelector('[name="ShowRecordTitle"]').value = named;
            },
            error: function(error) {
                addFlashMessage(f`Error generating grade: ${error}`, 'danger');
            }
        });
    }
}
document.getElementsByName('recordCriteria')[0].addEventListener('change', performCheck);
document.getElementsByName('recordSubject')[0].addEventListener('change', performCheck);
document.getElementsByName('recordGradeLvl')[0].addEventListener('change', performCheck);