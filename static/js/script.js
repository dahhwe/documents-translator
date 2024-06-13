const fileInput = document.querySelector('input[type="file"]');
const uploadButton = document.querySelector('input[type="submit"]');
const downloadButton = document.querySelector('#download-form button');
const progressBar = document.getElementById('progress-bar');
const defaultPrompt = 'You are a highly skilled translator specializing in IT literature. Your task is to translate the following text to Turkish, maintaining its professional tone and keeping all technical terms and object names intact. Your response should only contain the translated text without any extra information such as specifying the language of the document and so on. If you are unable to provide the translation or text contains some kind of not alphabetic symbols or text seems to be a code fragment keep text as it is.';
const promptTextArea = document.querySelector('textarea[name="prompt"]');

promptTextArea.value = defaultPrompt;

uploadButton.disabled = true;
downloadButton.disabled = true;

fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    if (['docx', 'odt', 'doc'].includes(fileExtension)) {
        uploadButton.disabled = false;
    } else {
        uploadButton.disabled = true;
        alert('Invalid file type. Only .docx, .odt, and .doc files are allowed.');
    }
    downloadButton.disabled = true;
    progressBar.value = 0;
});

document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('prompt', document.querySelector('textarea[name="prompt"]').value);

    console.log('Form data:', [...formData.entries()]);

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