document.querySelectorAll('#criteria input[type="number"]').forEach(input => input.setAttribute('disabled', 'true'))

document.getElementById("criteria_switch").addEventListener('change', (event) => {
    const editButton = document.getElementById('criteria_submit');
    const inputs = document.querySelectorAll('#criteria input[type="number"]');

    if (event.target.checked) {
        editButton.style.display = 'block';
        inputs.forEach(input => input.removeAttribute('disabled'));
    } else {
        editButton.style.display = 'none';
        inputs.forEach(input => input.setAttribute('disabled', 'true'));
    }
});
