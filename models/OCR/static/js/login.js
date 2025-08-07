document.addEventListener('DOMContentLoaded', () => {
    const emailInput = document.getElementById('email');
    const sendOtpBtn = document.getElementById('sendOtp');
    const sendOtpSection = document.getElementById('sendOtpSection');
    const otpSection = document.getElementById('otpSection');
    const otpInput = document.getElementById('otp');
    const verifyOtpBtn = document.getElementById('verifyOtp');
    const signupLink = document.getElementById('signupLink');

    // Send OTP button click handler
    sendOtpBtn.addEventListener('click', () => {
        const email = emailInput.value.trim();
        
        if (!email || !isValidEmail(email)) {
            alert('Please enter a valid email address');
            return;
        }

        // Here you would typically make an API call to send OTP
        // For demo purposes, we'll just show the OTP section
        otpSection.style.display = 'block';
        sendOtpSection.style.display = 'none';
        emailInput.disabled = true;
        
    
    });

    // Verify OTP button click handler
    verifyOtpBtn.addEventListener('click', () => {
        const otp = otpInput.value.trim();
        
        if (!otp || otp.length !== 6) {
            alert('Please enter a valid 6-digit OTP');
            return;
        }

        // Here you would typically make an API call to verify OTP
        // For demo purposes, we'll just show a success message
        alert('Login successful!');
        // Redirect to main page or dashboard
        window.location.href = 'index.html';
    });

    // Sign up link click handler
    signupLink.addEventListener('click', (e) => {
        e.preventDefault();
        // Here you would typically redirect to the signup page
        alert('Sign up functionality will be implemented soon!');
    });

    // Email validation helper function
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});