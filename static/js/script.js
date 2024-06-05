const fileInput = document.querySelector('input[type="file"]');
const uploadButton = document.querySelector('input[type="submit"]');
const downloadButton = document.querySelector('#download-form button');
const progressBar = document.getElementById('progress-bar');

uploadButton.disabled = true;
downloadButton.disabled = true;

fileInput.addEventListener('change', () => {
    uploadButton.disabled = !fileInput.files.length;
    downloadButton.disabled = true;
    progressBar.value = 0;
});

document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fileInput.disabled = true;
    uploadButton.disabled = true;


    const intervalId = setInterval(() => {
        if (progressBar.value < 100) {
            progressBar.value += 2;
        }
    }, 3000);

    try {
        const response = await fetch('/upload/', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            clearInterval(intervalId);
            progressBar.value = 100;

            const data = await response.json();
            alert(data.message);

            if (data.filename) {
                const filename = data.filename;
                const downloadForm = document.getElementById('download-form');
                downloadForm.action = `/download/${filename}`;
                downloadButton.disabled = false;
            } else {
                alert('Filename could not be determined');
            }
        } else {
            alert('File upload failed');
        }
    } catch (error) {
        alert('An error occurred during the file upload.');
    } finally {
        fileInput.disabled = false;
        uploadButton.disabled = false;
    }
});