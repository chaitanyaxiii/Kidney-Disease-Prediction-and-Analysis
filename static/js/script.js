document.addEventListener('DOMContentLoaded', function() {
    const uploadInput = document.getElementById('upload-file');
    const predictButton = document.getElementById('predict-btn');
    const clearButton = document.getElementById('clear-btn');
    const showCausesButton = document.getElementById('show-causes-btn');
    const showSolutionButton = document.getElementById('show-solution-btn');
    const enhanceButton = document.getElementById('enhance-btn');
    const exitButton = document.getElementById('exit-btn');

    const selectedImage = document.getElementById('selected-image');
    const enhancedImage = document.getElementById('enhanced-image');
    const predictedClassLabel = document.getElementById('predicted-class');
    const meanCell = document.getElementById('mean');
    const entropyCell = document.getElementById('entropy');
    const contrastCell = document.getElementById('contrast');
    const rmsCell = document.getElementById('rms');
    const kurtosisCell = document.getElementById('kurtosis');
    const skewnessCell = document.getElementById('skewness');
    const sdCell = document.getElementById('sd');

    uploadInput.addEventListener('change', function() {
        const file = uploadInput.files[0];
        const reader = new FileReader();

        reader.onload = function(e) {
            selectedImage.src = e.target.result;
            enhancedImage.src = '';  // Clear enhanced image
        };

        reader.readAsDataURL(file);
    });

    predictButton.addEventListener('click', function() {
        const file = uploadInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            predictedClassLabel.textContent = 'CLASS PREDICTED: ' + data.class_name;

            meanCell.textContent = data.mean.toFixed(2);
            entropyCell.textContent = data.entropy.toFixed(2);
            contrastCell.textContent = data.contrast.toFixed(2);
            rmsCell.textContent = data.rms.toFixed(2);
            kurtosisCell.textContent = data.kurtosis.toFixed(2);
            skewnessCell.textContent = data.skewness.toFixed(2);
            sdCell.textContent = data.sd.toFixed(2);
        })
        .catch(error => console.error('Error:', error));
    });

    enhanceButton.addEventListener('click', function() {
        if (selectedImage.src) {
            fetch('/enhance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ file_path: selectedImage.src })
            })
            .then(response => response.json())
            .then(data => {
                enhancedImage.src = data.enhanced_image_path;
            })
            .catch(error => console.error('Error:', error));
        }
    });

    clearButton.addEventListener('click', function() {
        selectedImage.src = '';
        enhancedImage.src = '';
        predictedClassLabel.textContent = 'CLASS PREDICTED: ';
        meanCell.textContent = '';
        entropyCell.textContent = '';
        contrastCell.textContent = '';
        rmsCell.textContent = '';
        kurtosisCell.textContent = '';
        skewnessCell.textContent = '';
        sdCell.textContent = '';
    });

    showCausesButton.addEventListener('click', function() {
        const predictedClass = predictedClassLabel.textContent.split(': ')[1].trim();
        let causesTextContent;
        switch (predictedClass) {
            case 'Anthracnose': causesTextContent = 'Causes of Anthracnose: Fungal infection caused by Colletotrichum species.'; break;
            case 'Apple Scab': causesTextContent = 'Causes of Apple Scab: Fungal infection caused by Venturia inaequalis.'; break;
            case 'Brown Rot': causesTextContent = 'Causes of Brown Rot: Fungal infection caused by Monilinia fructicola.'; break;
            case 'Black Rot': causesTextContent = 'Causes of Black Rot: Fungal infection caused by Botryosphaeria obtusa.'; break;
            case 'Canker': causesTextContent = 'Causes of Canker: Fungal infection caused by various pathogens.'; break;
            case 'Fruit Rot': causesTextContent = 'Causes of Fruit Rot: Various fungal infections.'; break;
            case 'Normal': causesTextContent = 'No disease detected. The fruit is healthy.'; break;
            default: causesTextContent = 'Please select a proper image.';
        }
        alert(causesTextContent);
    });

    showSolutionButton.addEventListener('click', function() {
        const predictedClass = predictedClassLabel.textContent.split(': ')[1].trim();
        let solutionTextContent;
        switch (predictedClass) {
            case 'Anthracnose': solutionTextContent = 'Solution for Anthracnose: Use fungicides and practice crop rotation.'; break;
            case 'Apple Scab': solutionTextContent = 'Solution for Apple Scab: Apply fungicides and remove fallen leaves.'; break;
            case 'Brown Rot': solutionTextContent = 'Solution for Brown Rot: Use fungicides and prune infected branches.'; break;
            case 'Black Rot': solutionTextContent = 'Solution for Black Rot: Use fungicides and prune infected branches.'; break;
            case 'Canker': solutionTextContent = 'Solution for Canker: Remove and destroy infected plant material.'; break;
            case 'Fruit Rot': solutionTextContent = 'Solution for Fruit Rot: Use fungicides and ensure proper air circulation.'; break;
            case 'Normal': solutionTextContent = 'No treatment needed. The fruit is healthy.'; break;
            default: solutionTextContent = 'Please select a proper image.';
        }
        alert(solutionTextContent);
    });

    exitButton.addEventListener('click', function() {
        fetch('/exit', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            window.location.href = data.redirect_url;
        });
    });
});
