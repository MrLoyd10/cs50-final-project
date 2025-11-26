
// Automatic na mawawala and flash or notification below ng nav
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 1s';
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.style.display = 'none';
            }, 1000);
        }, 5000);
    });
});



//ADDING FLASH USING THE JAVASCRIPT:
function addFlashMessage(message, category) {
    let flashContainer = document.getElementById('flashContainer');
    let flashMessage = document.createElement('div');
    flashMessage.classList.add('alert');
    flashMessage.classList.add(`alert-${category}`);
    flashMessage.classList.add('mb-0');
    flashMessage.classList.add('p-2');
    flashMessage.innerText = message;
    flashContainer.appendChild(flashMessage);

    setTimeout(function() {
        flashMessage.style.transition = 'opacity 1s';
        flashMessage.style.opacity = '0';
        setTimeout(function() {
            flashMessage.remove(); // Remove the element
        }, 1000);
    }, 5000);
}