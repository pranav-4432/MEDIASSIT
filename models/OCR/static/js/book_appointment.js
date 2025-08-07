console.log('Hello!');

// Handle form submission
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('appointmentForm');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      
      // Collect form data
      const formData = {
        name: form.name.value,
        age: form.age.value,
        appointmentDate: form.appointmentDate.value,
        appointmentTime: form.appointmentTime.value,
        description: form.description.value
      };
      
      // Log the appointment details (replace with actual submission logic)
      console.log('Appointment Details:', formData);
      alert('Appointment booked successfully!');
      form.reset();
    });
  }
});