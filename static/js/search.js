function redirectToLink(fileName) {
    var baseUrl = "https://drive.google.com/drive/folders/";
    if (fileName.startsWith("eADP1")) {
        window.open(baseUrl + "1RypsKXLeQKT8OJzLgcEMEzZ_rgxJ3kn4", '_blank').focus();
    } else if (fileName.startsWith("eADP2")) {
        window.open(baseUrl + "1SKv2KJNb-C9VIjHmnsAUqN305TbemuEj", '_blank').focus();
    } else if (fileName.startsWith("eADP3")) {
        window.open(baseUrl + "1SWfjNf5FaVPRC0pw5rwqissy9eRRU3kI", '_blank').focus();
    }
}

function resetSearchFormAndSubmit() {
    document.querySelectorAll('#searchForm select').forEach(select => {
        select.value = "";
    });
    document.getElementById('searchForm').submit();
}

