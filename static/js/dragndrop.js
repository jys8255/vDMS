let uploadedFiles = [];
const dropBox = document.getElementById('drop-box');
const messageBox = document.getElementById('message');
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
const fileModal = $('#fileModal');
const successModal = $('#successModal');
const duplicateFileModal = $('#duplicateFileModal');
const removeDuplicatesBtn = document.getElementById('removeDuplicatesBtn');
const uploadBtn = document.getElementById('uploadBtn');
const overwriteBtn = document.getElementById('overwriteBtn');

let baseFolder = '';

dropBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropBox.style.backgroundColor = "#94D8F6";
});

dropBox.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropBox.style.backgroundColor = "#FFFFFF";
});

/////드랍 파일 처리/////
dropBox.addEventListener('drop', async (e) => {
    e.preventDefault();
    dropBox.style.backgroundColor = "#FFFFFF";
    const items = e.dataTransfer.items;
    baseFolder = '';
    messageBox.innerHTML = '';
    uploadedFiles = [];

    await Promise.all(Array.from(items).map(item => processEntry(item.webkitGetAsEntry())));

      if (uploadedFiles.length > 0) {
       console.log('2.uploadedFiles length:',uploadedFiles.length)
        if (uploadedFiles.some(file => file.isDuplicate)) {
        console.log('Uploaded files:', uploadedFiles);
        console.log('Duplicates present:', uploadedFiles.some(file => file.isDuplicate));
            uploadBtn.style.display = 'none';
            overwriteBtn.style.display = 'block';
            removeDuplicatesBtn.style.display = 'block';
        } else {
            uploadBtn.style.display = 'block';
            removeDuplicatesBtn.style.display = 'none';
            overwriteBtn.style.display = 'none';
        }
    } else {
        uploadBtn.style.display = 'none';
        removeDuplicatesBtn.style.display = 'none';
        overwriteBtn.style.display = 'none';
    }
});


async function processEntry(entry, path = "") {
    return new Promise((resolve, reject) => {
        if (entry.isFile) {
            entry.file(async file => {
                await processFile(file, path);
                resolve();
            }, reject);
        } else if (entry.isDirectory) {
            let dirReader = entry.createReader();
            dirReader.readEntries(async (entries) => {
                await Promise.all(entries.map(ent => processEntry(ent, path + entry.name + "/")));
                resolve();
            }, reject);
        }
    });
}


async function processFile(file, path) {
    console.log('AA:Processing file:', file.name);  // 파일 처리 시작 로그

    baseFolder = path.replace(/\/$/, '');
    const completePath = generateFilePath(file.name, baseFolder);

    try {
        const isDuplicate = await checkDuplicate(completePath);
        console.log('Duplicate check for', file.name, ':', isDuplicate);  // 중복 검사 결과 로그

        const displayPath = path + file.name;
        console.log('Display Path:', displayPath);

        if (isDuplicate) {
            console.log('Duplicate file found:', file.name);
            displayFileMessage(displayPath, true);
            uploadedFiles.push({ file: file, path: displayPath, baseFolder: baseFolder, isDuplicate: true });
        } else {
            console.log('No duplicates, file added:', file.name);
            displayFileMessage(displayPath, false);
            uploadedFiles.push({ file: file, path: displayPath, baseFolder: baseFolder, isDuplicate: false });
        }
    } catch (error) {
        console.error("Error processing file", file.name, ":", error);  // 에러 로그
    }
}
/////드랍 파일 처리/////

////////버튼들///////////
uploadBtn.addEventListener('click', () => {
    if (uploadedFiles.length > 0) {
        uploadFiles(uploadedFiles.map(u => u.file), false, baseFolder);
    } else {
        alert('Please drag and drop files first.');
    }
});

removeDuplicatesBtn.addEventListener('click', () => {
    const filesBefore = uploadedFiles.length;
    uploadedFiles = uploadedFiles.filter(file => !file.isDuplicate);
    const filesAfter = uploadedFiles.length;

    messageBox.innerHTML = '';  // 메시지 박스 초기화
    uploadedFiles.forEach(file => {
        displayFileMessage(file.path, false);
    });

    console.log('Files after removing duplicates:', uploadedFiles.map(file => file.path));
    removeDuplicatesBtn.style.display = 'none';
    overwriteBtn.style.display = 'none';

    if (filesBefore > filesAfter) {
        alert(`${filesBefore - filesAfter} 개의 중복 파일이 제거 되었습니다.`);
    } else {
        alert('No duplicates to remove.');
    }

    if (uploadedFiles.length > 0) {
        uploadBtn.style.display = 'block';
    } else {
        uploadBtn.style.display = 'none';
    }
});

overwriteBtn.addEventListener('click', () => {
    if (uploadedFiles.length > 0) {
        uploadFiles(uploadedFiles.map(u => u.file), true, baseFolder);
    } else {
        alert('Please drag and drop files first.');
    }
});
////////버튼들///////////

///중복 검사 위치 생성///
function generateFilePath(filename, baseFolder) {
    const basePath = "G:/공유 드라이브/010_ADUS/220_Development/910_Data/010_LoggingData/";
    let folder = "999_Others";
    if (filename.includes('eADP(eADM1)')) {
        folder = "101_eADP_eADM1";
    } else if (filename.includes('eADP(TCar)')) {
        folder = "100_eADP_TCar";
    } else if (filename.includes('ETC')) {
        folder = "200_Etc";
    }
    const completePath = `${basePath}${folder}/${baseFolder}/${filename}`;
    return completePath;
}
///중복 검사 위치 생성///

async function checkDuplicate(filePath) {
    try {
        const response = await fetch('/register/check-duplicate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ filePath })
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data.isDuplicate;
    } catch (error) {
        console.error("Error checking duplicate:", error);
        return false;  // Assume not duplicate if error occurs
    }
}

function displayUploadedFiles() {
    messageBox.innerHTML = '';
    uploadedFiles.forEach(file => {
        const messageColor = file.isDuplicate ? 'style="color:red;"' : '';
        messageBox.innerHTML += `<li ${messageColor}>${file.path}</li>`;
    });
}

function displayFileMessage(filePath, isDuplicate) {
    const messageColor = isDuplicate ? 'style="color:red;"' : '';
    messageBox.innerHTML += `<li ${messageColor}>${filePath}</li>`;
}
function uploadFiles(files, overwrite, currentBaseFolder) {
    console.log('10.uploadedFiles:',currentBaseFolder)
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files[]', file);
    });
    formData.append('base_folder', currentBaseFolder); //ex)240415
    formData.append('overwrite', overwrite);
    messageBox.innerHTML = '';

    fetch('/register/register/', {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': csrfToken },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            successModal.find('.modal-body').text('파일이 성공적으로 업로드 됐습니다.');
            successModal.modal('show');
            uploadBtn.style.display = 'none';
            overwriteBtn.style.display = 'none';
            removeDuplicatesBtn.style.display = 'none';
        } else if (data.error) {
            displayDuplicateFilesModal(data.duplicate_files, files);
        }
    })
    .catch(error => {
        uploadBtn.style.display = 'none';
        console.error('Error:', error);
        alert('G드라이브가 연결되어있지 않습니다.');

    })
}
