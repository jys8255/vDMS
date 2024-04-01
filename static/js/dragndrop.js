let uploadedFiles = [];
const dropBox = document.getElementById('drop-box');
const messageBox = document.getElementById('message');
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
const fileModal = $('#fileModal');
const successModal = $('#successModal');
const duplicateFileModal = $('#duplicateFileModal');
const uploadBtn = document.getElementById('uploadBtn');

dropBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropBox.style.backgroundColor = "#94D8F6";
});

dropBox.addEventListener('dragleave', (e) => {
    dropBox.style.backgroundColor = "#F7F7F7";
});

dropBox.addEventListener('drop', (e) => {
    e.preventDefault();
    dropBox.style.backgroundColor = "#F7F7F7";
    const files = e.dataTransfer.files;
    if (files.length) {
        handleFiles(files);
    }
});

function handleFiles(files) {
    uploadedFiles = [...files];
    checkFilePairsAndUpload(uploadedFiles);

}

//파일쌍 체크 함수
function checkFilePairsAndUpload(files) {
    const jsonFiles = new Set();
    const matFiles = new Set();
    const missingPairs = [];

    files.forEach(file => {
        const baseName = file.name.split('.').slice(0, -1).join('.');
        if (file.name.endsWith('.json')) {
            jsonFiles.add(baseName);
        } else if (file.name.endsWith('.mat')) {
            matFiles.add(baseName);
        }
    });

    jsonFiles.forEach(baseName => {
        if (!matFiles.has(baseName)) {
            missingPairs.push(`${baseName}.mat 파일이 필요합니다.`);
        }
    });

    matFiles.forEach(baseName => {
        if (!jsonFiles.has(baseName)) {
            missingPairs.push(`${baseName}.json 파일이 필요합니다.`);
        }
    });

    if (missingPairs.length > 0) {
        displayMissingPairsModal(missingPairs);
    } else {
        updateMessageBox(files);
    }
}


//업로드 파일:
function updateMessageBox(files) {
    messageBox.innerHTML = '업로드 예정 파일: <br>';
    files.forEach(file => {
        messageBox.innerHTML += `<div>${file.name}</div>`;
    });
    // 파일이 올바르게 드롭된 후에만 업로드 버튼을 표시
    uploadBtn.style.display = 'block';
}

//파일쌍 경고 모달
function displayMissingPairsModal(missingPairs) {
    const missingPairsList = document.getElementById('missingPairs');
    missingPairsList.innerHTML = missingPairs.join('<br>');
    fileModal.modal('show');
}
//save 클릭 리스너
uploadBtn.addEventListener('click', () => {
    if (uploadedFiles.length > 0) {
        uploadFiles(uploadedFiles, false);
    } else {
        alert('업로드할 파일을 먼저 드래그 앤 드롭하세요.');
    }
});
//main 파일 업로드 로직
function uploadFiles(files, overwrite) {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files[]', file);
    });
    formData.append('overwrite', overwrite ? 'true' : 'false');


    messageBox.innerHTML = ''; // 중복 검사 전 메시지 박스 초기화
    uploadBtn.style.display = 'none'; // 중복 검사 중엔 Save 버튼 숨김

    fetch('/register/register/', {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': csrfToken },
    })
    .then(response => {
        if (response.status === 409) {
            // 중복 파일이 존재하면, 중복 파일 처리 모달을 표시
            return response.json().then(data => {
                showDuplicateFilesModal(data.duplicate_files, files);
            });

        } else if (response.ok) {
            return response.json();

        } else {
            alert('서버 오류가 발생했습니다. 관리자에게 문의하세요.');
            throw new Error('서버가 200이 아닌 상태 코드로 응답했습니다');

        }
    })
    .then(data => {
        if (data && data.success) {
            // 중복 파일이 없고 파일 업로드가 성공했을 때만 "업로드된 파일:" 문구를 업데이트하고 성공 모달을 표시
            updateMessageBox(uploadedFiles);
            uploadBtn.style.display = 'none';
            displaySuccessModal(data.uploadedFiles);

        }
    })
    .catch(error => {
    console.error('오류:', error);
    alert('처리 중 문제가 발생했습니다. 다시 시도해 주세요.');
  });
}

//중복파일 선택받는 모달
function showDuplicateFilesModal(duplicateFiles, allFiles) {
    let message = "<ul>" + duplicateFiles.map(file => `<li>${file}</li>`).join("") + "</ul><br>파일이 이미 존재합니다.<br>저장 방식을 선택하세요.";
    $('#duplicateFileModal .modal-body').html(message);
    $('#duplicateFileModal').modal('show');

    // 'Skip Duplicates' 버튼 이벤트 핸들러
    $('#duplicateFileModal #skipDuplicates').off('click').on('click', function() {
        // 중복되지 않은 파일만 필터링하여 업로드
        const filteredFiles = allFiles.filter(file => !duplicateFiles.includes(file.name));
        if(filteredFiles.length > 0) {
            uploadFiles(filteredFiles, false);
            uploadBtn.style.display = 'none';// 중복되지 않은 파일만 업로드
        } else {
            alert('모든 파일이 이미 존재합니다.');
        }
        $('#duplicateFileModal').modal('hide');
        uploadBtn.style.display = 'none';// 중복되지 않은 파일만 업로드
    });

    // 'Overwrite' 버튼 이벤트 핸들러
    $('#duplicateFileModal #overwriteDuplicates').off('click').on('click', function() {
        uploadFiles(uploadedFiles, true);
        $('#duplicateFileModal').modal('hide');
        uploadBtn.style.display = 'none';
    });

}

//파일 성공 모달
function displaySuccessModal(uploadedFiles) {
    const successMessage = '파일 업로드가 성공적으로 완료되었습니다.';
    $('#successModal .modal-body').text(successMessage);
    messageBox.innerHTML = '';
    uploadBtn.style.display = 'none';
    successModal.modal('show');

}