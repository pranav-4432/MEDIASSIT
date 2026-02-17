// Login is form-based (email + password). Form submits to /login.
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form[action*="login"]');
    if (form) {
        form.addEventListener('submit', () => {
            const email = form.querySelector('input[name="email"]');
            const password = form.querySelector('input[name="password"]');
            if (email && !email.value.trim()) {
                return;
            }
            if (password && !password.value) {
                return;
            }
        });
    }
});
