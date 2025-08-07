document.addEventListener('DOMContentLoaded', () => {
    // Search functionality
    const searchBar = document.querySelector('.search-bar');
    searchBar.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        // Add search functionality here
        console.log('Searching for:', searchTerm);
    });

    // Medical Prediction link
    document.querySelector('.nav-link').addEventListener('click', (e) => {
        e.preventDefault();
        console.log('Navigating to Medical Prediction page');
    });

    // OCR Scanner button
    document.querySelector('.ocr-card .card-btn').addEventListener('click', (e) => {
        e.preventDefault();
        console.log('Opening OCR Scanner');
    });

    // View All buttons
    document.querySelectorAll('.card-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const cardType = e.target.closest('.dashboard-card').classList[1];
            console.log('Viewing all for:', cardType);
        });
    });
});