function redirectToLink(fileName) {
    var baseUrl = "https://drive.google.com/drive/folders/";
    if (fileName.startsWith("eADP1")) {
        window.open(baseUrl + "1RypsKXLeQKT8OJzLgcEMEzZ_rgxJ3kn4", '_blank').focus();
    } else if (fileName.startsWith("eADP2")) {
        window.open(baseUrl + "1SKv2KJNbeee-C9VIjHmnsAUqN305TbemuEj", '_blank').focus();
    } else if (fileName.startsWith("eADP3")) {
        window.open(baseUrl + "1SWfjNf5FaVPRC0pw5rwqissy9eRRU3kI", '_blank').focus();
    }
}

function resetSearchFormAndSubmit() {
    // 폼의 select 요소를 찾아 각각의 값을 초기화합니다.
    document.querySelectorAll('#searchForm select').forEach(select => {
        select.value = ""; // 각 select 요소의 값을 빈 문자열로 설정하여 초기화
    });

    // 모든 select 입력이 초기화된 상태에서 폼을 제출합니다.
    document.getElementById('searchForm').submit();
}
