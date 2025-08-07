document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const previewImage = document.getElementById('preview-image');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultsSection = document.getElementById('result');

    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = () => {
                previewImage.src = reader.result;
                document.getElementById('report-preview').classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    });

    analyzeBtn.addEventListener('click', async (e) => {
        e.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            alert("Please upload a blood report image.");
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        analyzeBtn.textContent = 'Analyzing...';
        analyzeBtn.disabled = true;

        const response = await fetch('/upload/ocr', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (result.error) {
            alert(result.error);
        } else {
            document.getElementById("abnormal-values").innerHTML = result["Abnormal Values"];
            document.getElementById("key-findings").innerHTML = result["Possible Disease"];
            document.getElementById("recommendations").innerHTML = result["Remedies"];

            resultsSection.classList.remove('hidden');
        }

        analyzeBtn.textContent = 'Analyze Report';
        analyzeBtn.disabled = false;
    });
});


document.getElementById("upload-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    let formData = new FormData();
    let fileInput = document.getElementById("file-upload");

    if (!fileInput.files.length) {
        alert("Please select a file.");
        return;
    }

    formData.append("file", fileInput.files[0]);

    try {
        let response = await fetch("/upload/ocr", {
            method: "POST",
            body: formData
        });

        let result = await response.json();

        if (result.error) {
            document.getElementById("result").innerHTML = `<p class='error'>${result.error}</p>`;
        } else {
            document.getElementById("result").innerHTML = `
                <h3>Abnormal Values</h3>
                <p>${result["Abnormal Values"]}</p>
                <h3>Key Findings</h3>
                <p>${result["Key Findings"]}</p>
                <h3>Recommendations</h3>
                <p>${result["Recommendations"]}</p>
            `;
        }
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("result").innerHTML = "<p class='error'>An error occurred. Please try again.</p>";
    }
});