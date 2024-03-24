
let uploadedFiles = [];
const dropBox = document.getElementById('drop-box');
const messageBox = document.getElementById('message');
const saveBtn = document.getElementById('save-btn');
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

const basePath = "G:/공유 드라이브/010_ADUS/220_Development/910_Data/010_LoggingData/vDMS_TEST/";

dropBox.addEventListener('dragover', (e) => {
    e.preventDefault();
});

dropBox.addEventListener('drop', (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length) {
        uploadedFiles = [...files];
        messageBox.innerHTML = 'Uploaded File: <br>';
        Array.from(files).forEach(file => {
            messageBox.innerHTML += `<div>${file.name}</div>`;
        });
        saveBtn.style.display = 'block';
    }
});

saveBtn.addEventListener('click', () => {
    if (!uploadedFiles.length) {
        alert('파일을 먼저 업로드해주세요.');
        return;
    }

    const formData = new FormData();
    uploadedFiles.forEach(file => {
        formData.append('files[]', file);

        formData.append('path', basePath);
    });

    fetch('/register/register/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        },
    })
    .then(response => response.json())
    .then(data => {
        messageBox.innerText = '모든 파일이 성공적으로 저장되었습니다!';
        saveBtn.style.display = 'none';
    })
    .catch(error => {
        console.error('Error:', error);
        messageBox.innerText = '파일 저장에 실패했습니다.';
    });
});