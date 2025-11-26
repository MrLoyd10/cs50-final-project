$(document).ready(function () {
    $(".hide-btn").click(function () {
        const status = $(this).find(".d-flex p");
        const iconElement = $(this).find(".d-flex i");
        
        if (status.text() === 'Hide') {
            status.text("Show");
            iconElement.removeClass("bi-eye-slash-fill");
            iconElement.addClass("bi-eye-fill");
        } else {
            status.text("Hide");
            iconElement.removeClass("bi-eye-fill");
            iconElement.addClass("bi-eye-slash-fill");
        }
    });
});

$(document).ready(function() {
    function FormatTotal(number) {
        total = (number).toFixed(2).toString();
        total = total.replace(/\.(\d)0$/, '.$1');
        return total;
    }

    let currentValue = 0;
    $('.result_table').on('focus', 'input[type="number"]', function() {
        // Store the original value when the input field is focused
        currentValue = $(this).val();
    });

    // Use event delegation to handle dynamic content
    $('.result_table').on('change', 'input[type="number"]', function() {
        const updatedValue = $(this).val();

        // Get the associated data
        const gradeDescription = $(this).data('grade-description');
        const studentId = $(this).data('student-id');
        const column = $(this).data('grade-column');
        const row = $(this).data('row');
        const criteria = $(this).data('criteria');
        const highestScoreText = $('#' + criteria + '-highest-' + column).text();
        // Convert to int
        const highestScore = + highestScoreText;

        const selectedSubject = $('select[name="resultSubject"]').val();
        const selectedGradeLvl = $('select[name="resultGradeLvl"]').val();

        if (updatedValue > highestScore || isNaN(updatedValue) || !updatedValue) {
            addFlashMessage("Grade cannot be higher than the highest score, empty or a letter.", "danger");

            // Restore the original value
            $(this).val(currentValue);
        } else {
            // Update the data attribute to store the current value
            $(this).val(updatedValue);
            

            $.ajax({
                method: "POST",
                url: "/update-grade",
                data: { studentId: studentId, gradeDescription: gradeDescription, grade: updatedValue, 
                    subject: selectedSubject, gradelvl: selectedGradeLvl, criteria: criteria},
                success: function(response) {
                    addFlashMessage(response.updateResponse.message, response.updateResponse.status);
                    const initial = response.updatedInitialTrans.initial;
                    const transmulated = response.updatedInitialTrans.transmulated;

                    $('#initial-'+ studentId).text(initial);
                    $('#transmulated-'+ studentId).text(transmulated)
                }
            });
            
            const targetInputs = $('input[data-criteria="'+ criteria +'"][data-row="'+ row +'"]');
            const targetHighest = $('.'+ criteria +'-highest');

            let totalScore = 0;
            let totalHighest = 0;
            // Get the sum of all of its score
            targetInputs.each(function() {
                totalScore += parseFloat($(this).val()) || 0;
            });
            
            // Get the sum of total highest scores
            targetHighest.each(function() {
                totalHighest += parseFloat($(this).text()) || 0;
            });

            let CurrentTotal = $('#total-'+ criteria +'-'+ row);
            CurrentTotal.text(FormatTotal(totalScore/totalHighest * 100));


        }
    });
});