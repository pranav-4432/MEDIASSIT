(function () {
    'use strict';

    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsList = document.getElementById('results-list');
    const resultsPlaceholder = document.getElementById('results-placeholder');
    const resultsLoading = document.getElementById('results-loading');
    const resultsError = document.getElementById('results-error');

    let debounceTimer = null;
    const DEBOUNCE_MS = 300;

    function setLoading(loading) {
        if (loading) {
            resultsPlaceholder.style.display = 'none';
            resultsList.innerHTML = '';
            resultsLoading.style.display = 'block';
            resultsError.style.display = 'none';
        } else {
            resultsLoading.style.display = 'none';
        }
    }

    function showError(message) {
        resultsError.textContent = message;
        resultsError.style.display = 'block';
        resultsList.innerHTML = '';
    }

    function hideError() {
        resultsError.style.display = 'none';
    }

    function renderPatients(patients) {
        if (!patients || patients.length === 0) {
            resultsList.innerHTML = (
                '<div class="results-empty">' +
                '<i class="fas fa-user-slash"></i>' +
                '<p>No patients found. Try a different name.</p>' +
                '</div>'
            );
            return;
        }

        const fragment = document.createDocumentFragment();
        patients.forEach(function (p) {
            const name = p.Name || p.name || 'Unknown';
            const meta = [p.Age && 'Age: ' + p.Age, p.Email && p.Email, p.Phone && p.Phone]
                .filter(Boolean)
                .join(' · ') || 'No extra details';
            const card = document.createElement('div');
            card.className = 'patient-card';
            card.innerHTML = (
                '<div class="patient-name">' + escapeHtml(name) + '</div>' +
                '<div class="patient-meta">' + escapeHtml(meta) + '</div>'
            );
            card.addEventListener('click', function (e) {
                e.preventDefault();
                // Optional: could link to a patient detail page later
            });
            fragment.appendChild(card);
        });
        resultsList.innerHTML = '';
        resultsList.appendChild(fragment);
    }

    function escapeHtml(text) {
        if (text == null) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function doSearch() {
        const q = (searchInput.value || '').trim();
        if (!q) {
            resultsList.innerHTML = '';
            resultsPlaceholder.style.display = 'block';
            hideError();
            return;
        }

        setLoading(true);
        fetch('/api/patient_search?q=' + encodeURIComponent(q), {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        })
            .then(function (res) {
                if (res.status === 401) {
                    window.location.href = '/login';
                    return null;
                }
                return res.json();
            })
            .then(function (data) {
                setLoading(false);
                if (data == null) return;
                if (data.error) {
                    showError(data.error);
                    return;
                }
                renderPatients(data.patients || []);
            })
            .catch(function () {
                setLoading(false);
                showError('Failed to search. Please try again.');
            });
    }

    function onInput() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(doSearch, DEBOUNCE_MS);
    }

    if (searchInput) {
        searchInput.addEventListener('input', onInput);
        searchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                clearTimeout(debounceTimer);
                doSearch();
            }
        });
    }
    if (searchBtn) {
        searchBtn.addEventListener('click', function () {
            clearTimeout(debounceTimer);
            doSearch();
        });
    }
})();
