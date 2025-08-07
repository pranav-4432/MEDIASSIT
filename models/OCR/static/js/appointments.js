document.addEventListener('DOMContentLoaded', () => {
    // Add click event listeners for booking buttons
    document.querySelectorAll('.book-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const doctorName = e.target.closest('.doctor-card').querySelector('h2').textContent;
            alert(`Booking functionality for ${doctorName} will be implemented soon!`);
        });
    });

    // Add click event listener for the login button
    document.querySelector('.login-btn').addEventListener('click', () => {
        window.location.href = 'login.html';
    });
});