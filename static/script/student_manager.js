document.addEventListener('DOMContentLoaded', function() {
    // Get all the input elements in create account form
    const reg = document.querySelectorAll('#form_create_account input, #form_create_account select');

    // Iterates thru the inputs.
    reg.forEach((input, index) => {
        input.addEventListener('keydown', (event) => {
            // If the user hit Enter prevent it from submitting and focus to the next input
            if (event.key === 'Enter') {
                event.preventDefault();
                const nextIndex = (index + 1);
                if (nextIndex < reg.length) {
                    reg[nextIndex].focus();
                } else {
                    // If its in the last input submit the form.
                    document.getElementById('form_create_account').submit();
                }
            }
        })
    })
    
})
