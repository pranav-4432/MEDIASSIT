document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsList = document.getElementById('results-list');

    // Mock patient data
    const patients = [
        {
            name: 'John Smith',
            age: 45,
            gender: 'Male',
            condition: 'Hypertension'
        },
        {
            name: 'Emma Johnson',
            age: 32,
            gender: 'Female',
            condition: 'Migraine'
        },
        {
            name: 'Michael Brown',
            age: 58,
            gender: 'Male',
            condition: 'Arthritis'
        },
        {
            name: 'Sarah Wilson',
            age: 29,
            gender: 'Female',
            condition: 'Asthma'
        },
        {
            name: 'James Anderson',
            age: 52,
            gender: 'Male',
            condition: 'Diabetes'
        }
    ];

    function searchPatients(searchTerm) {
        return patients.filter(patient => 
            patient.name.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }

    function displayResults(results) {
        if (results.length === 0) {
            resultsList.innerHTML = '<div class="no-results">No patients found</div>';
            return;
        }

        resultsList.innerHTML = results.map(patient => `
            <div class="patient-card">
                <div class="patient-name">${patient.name}</div>
                <div class="patient-info">
                    ${patient.age} years old • ${patient.gender} • ${patient.condition}
                </div>
            </div>
        `).join('');
    }

    function handleSearch() {
        const searchTerm = searchInput.value.trim();
        if (searchTerm === '') {
            resultsList.innerHTML = '';
            return;
        }

        const results = searchPatients(searchTerm);
        displayResults(results);
    }

    // Event listeners
    searchBtn.addEventListener('click', handleSearch);
    
    searchInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });

    // Clear results when search input is cleared
    searchInput.addEventListener('input', () => {
        if (searchInput.value.trim() === '') {
            resultsList.innerHTML = '';
        }
    });
});