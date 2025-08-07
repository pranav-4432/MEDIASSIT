document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('appointmentForm');

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        // Get form data
        const formData = {
            patientName: form.patientName.value,
            age: form.age.value,
            appointmentTime: form.appointmentTime.value,
            doctorName: form.doctorName.value,
            description: form.description.value
        };

        // Log form data (replace with your actual submission logic)
        console.log('Appointment Details:', formData);

        // Show success message
        alert('Appointment booked successfully!');
        form.reset();
    });

    // Set minimum date for appointment time
    const appointmentTimeInput = document.getElementById('appointmentTime');
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    
    appointmentTimeInput.min = `${year}-${month}-${day}T${hours}:${minutes}`;

    // Add input validation
    const ageInput = document.getElementById('age');
    ageInput.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        if (value < 0) {
            e.target.value = 0;
        } else if (value > 150) {
            e.target.value = 150;
        }
    });
});