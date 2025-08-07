document.addEventListener('DOMContentLoaded', () => {
    // Navigation buttons
    const specificDiseaseBtn = document.getElementById('specific-disease-btn');
    const generalHealthBtn = document.getElementById('general-health-btn');
    const specificDiseaseSection = document.getElementById('specific-disease-section');

    // Disease selection elements
    const diseaseCards = document.querySelectorAll('.disease-card');
    const inputSection = document.getElementById('input-forms');
    const diseaseForms = document.querySelectorAll('.disease-form');

    // File input elements
    const fileInputs = document.querySelectorAll('.file-input');

    // Maximum file size (5MB)
    const MAX_FILE_SIZE = 5 * 1024 * 1024;

    // Allowed file types
    const ALLOWED_IMAGE_TYPES = [
        'image/jpeg',
        'image/png'
    ];

    // Navigation handling
    if (specificDiseaseBtn && generalHealthBtn) {
        specificDiseaseBtn.addEventListener('click', () => {
            specificDiseaseBtn.classList.add('active');
            generalHealthBtn.classList.remove('active');
            specificDiseaseSection.classList.remove('hidden');
        });

        generalHealthBtn.addEventListener('click', () => {
            generalHealthBtn.classList.add('active');
            specificDiseaseBtn.classList.remove('active');
            specificDiseaseSection.classList.add('hidden');
        });
    }

    // Disease card selection
    diseaseCards.forEach(card => {
        card.addEventListener('click', () => {
            // Remove selected class from all cards
            diseaseCards.forEach(c => c.classList.remove('selected'));
            // Add selected class to clicked card
            card.classList.add('selected');

            // Show input section
            inputSection.classList.remove('hidden');

            // Hide all forms
            diseaseForms.forEach(form => form.classList.add('hidden'));

            // Show the selected disease form
            const diseaseType = card.getAttribute('data-disease');
            const selectedForm = document.getElementById(`${diseaseType}-form`);
            if (selectedForm) {
                selectedForm.classList.remove('hidden');
                // Scroll to the form
                selectedForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Validate file
    function validateFile(file) {
        const errors = [];

        // Check file size
        if (file.size > MAX_FILE_SIZE) {
            errors.push('File size exceeds 5MB limit');
        }

        // Check file type
        if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
            errors.push('Invalid file type. Allowed types: JPG, PNG');
        }

        return errors;
    }

    // Show error message
    function showError(input, message) {
        const container = input.closest('.file-upload-container');
        const existingError = container.querySelector('.error-message');
        
        if (existingError) {
            existingError.remove();
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        container.appendChild(errorDiv);
    }

    // Clear error message
    function clearError(input) {
        const container = input.closest('.file-upload-container');
        const existingError = container.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
    }

    // Handle image preview
    function handleImagePreview(input, previewId, previewImageId) {
        const file = input.files[0];
        const preview = document.getElementById(previewId);
        const previewImage = document.getElementById(previewImageId);
        const fileInfo = input.parentElement.querySelector('.file-info');

        if (file) {
            // Validate file
            const errors = validateFile(file);
            if (errors.length > 0) {
                showError(input, errors.join('. '));
                input.value = '';
                fileInfo.textContent = 'No file chosen';
                preview.classList.add('hidden');
                return;
            }

            // Clear previous errors
            clearError(input);

            // Update file info
            fileInfo.textContent = `Selected: ${file.name}`;
            
            // Show preview
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                preview.classList.remove('hidden');
            };
            reader. onerror = () => {
                showError(input, 'Error reading file');
                preview.classList.add('hidden');
            };
            reader.readAsDataURL(file);
        } else {
            fileInfo.textContent = 'No file chosen';
            preview.classList.add('hidden');
            clearError(input);
        }
    }

    // Set up file input handlers
    const fracturefile = document.getElementById('fracture-file');
    if (fracturefile) {
        fracturefile.addEventListener('change', (e) => {
            handleImagePreview(e.target, 'fracture-preview', 'fracture-preview-image');
        });
    }

    const brainTumorFile = document.getElementById('brain-tumor-file');
    if (brainTumorFile) {
        brainTumorFile.addEventListener('change', (e) => {
            handleImagePreview(e.target, 'brain-tumor-preview', 'brain-tumor-preview-image');
        });
    }

    // Function to show prediction results
    function showPredictionResult(diseaseType, data) {
        // Hide all output sections
        document.querySelectorAll('.output-section').forEach(section => {
            section.classList.add('hidden');
        });

        // Show the relevant output section
        const outputSection = document.getElementById(`${diseaseType}-output`);
        if (!outputSection) return;

        outputSection.classList.remove('hidden');
        
        const resultIndicator = outputSection.querySelector('.result-indicator');
        const predictionText = outputSection.querySelector('.prediction-text');
        const confidenceScore = outputSection.querySelector('.confidence-score');
        const riskFactors = outputSection.querySelector('.risk-factors, .detection-details');

        // Clear previous content
        resultIndicator.className = 'result-indicator';
        predictionText.textContent = '';
        confidenceScore.textContent = '';
        riskFactors.innerHTML = '';

        // Update with new prediction results
        switch (diseaseType) {
            case 'heart':
                resultIndicator.classList.add(data.risk > 0.5 ? 'positive' : 'negative');
                predictionText.textContent = `Heart Disease Risk: ${data.risk > 0.5 ? 'High' : 'Low'}`;
                confidenceScore.textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
                if (data.riskFactors?.length) {
                    riskFactors.innerHTML = `
                        <h4>Key Risk Factors:</h4>
                        <ul>
                            ${data.riskFactors.map(factor => `<li>${factor}</li>`).join('')}
                        </ul>
                    `;
                }
                break;

            case 'diabetes':
                resultIndicator.classList.add(data.risk > 0.5 ? 'positive' : 'negative');
                predictionText.textContent = `Diabetes Risk: ${data.risk > 0.5 ? 'High' : 'Low'}`;
                confidenceScore.textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
                if (data.riskFactors?.length) {
                    riskFactors.innerHTML = `
                        <h4>Contributing Factors:</h4>
                        <ul>
                            ${data.riskFactors.map(factor => `<li>${factor}</li>`).join('')}
                        </ul>
                    `;
                }
                break;

            case 'cancer':
                resultIndicator.classList.add(data.risk > 0.5 ? 'positive' : 'negative');
                predictionText.textContent = `Cancer Risk: ${data.risk > 0.5 ? 'High' : 'Low'}`;
                confidenceScore.textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
                if (data.riskFactors?.length) {
                    riskFactors.innerHTML = `
                        <h4>Risk Indicators:</h4>
                        <ul>
                            ${data.riskFactors.map(factor => `<li>${factor}</li>`).join('')}
                        </ul>
                    `;
                }
                break;

            case 'fracture':
                resultIndicator.classList.add(data.detected ? 'positive' : 'negative');
                predictionText.textContent = `Fracture ${data.detected ? 'Detected' : 'Not Detected'}`;
                confidenceScore.textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
                if (data.details) {
                    riskFactors.innerHTML = `
                        <h4>Detection Details:</h4>
                        <p>${data.details}</p>
                    `;
                }
                break;

            case 'brain-tumor':
                resultIndicator.classList.add(data.detected ? 'positive' : 'negative');
                predictionText.textContent = `Brain Tumor ${data.detected ? 'Detected' : 'Not Detected'}`;
                confidenceScore.textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
                if (data.details) {
                    riskFactors.innerHTML = `
                        <h4>Detection Details:</h4>
                        <p>${data.details}</p>
                    `;
                }
                break;
        }

        // Scroll to the output section
        outputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Handle form submissions
    diseaseForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const diseaseType = form.id.replace('-form', '');
            
            try {
                // Validate required fields
                const requiredFields = form.querySelectorAll('[required]');
                let isValid = true;
                
                requiredFields.forEach(field => {
                    if (!field.value) {
                        isValid = false;
                        field.classList.add('error');
                    } else {
                        field.classList.remove('error');
                    }
                });

                if (!isValid) {
                    alert('Please fill in all required fields');
                    return;
                }

                // Simulate API call with mock data (replace with actual API call)
                const mockPrediction = {
                    heart: {
                        risk: Math.random(),
                        confidence: 0.85 + Math.random() * 0.1,
                        riskFactors: ['High blood pressure', 'Elevated cholesterol', 'Family history']
                    },
                    diabetes: {
                        risk: Math.random(),
                        confidence: 0.88 + Math.random() * 0.1,
                        riskFactors: ['High BMI', 'Elevated glucose levels', 'Age factor']
                    },
                    cancer: {
                        risk: Math.random(),
                        confidence: 0.82 + Math.random() * 0.1,
                        riskFactors: ['Abnormal cell growth', 'Genetic markers', 'Environmental factors']
                    },
                    fracture: {
                        detected: Math.random() > 0.5,
                        confidence: 0.90 + Math.random() * 0.1,
                        details: 'Potential fracture detected in the proximal region'
                    },
                    'brain-tumor': {
                        detected: Math.random() > 0.5,
                        confidence: 0.95 + Math.random() * 0.05,
                        details: 'Abnormal mass detected in the frontal lobe region'
                    }
                };

                // Show the prediction result
                showPredictionResult(diseaseType, mockPrediction[diseaseType]);
                
            } catch (error) {
                console.error(`Error processing ${diseaseType} assessment:`, error);
                alert(`Error processing the ${diseaseType.replace('-', ' ')} assessment. Please try again.`);
            }
        });
    });
});