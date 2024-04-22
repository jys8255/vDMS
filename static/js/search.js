
function redirectToLink(fileName) {
    console.log("Received fileName:", fileName);  // 로깅 추가

    var baseUrl = "https://drive.google.com/drive/folders/";
    if (fileName.startsWith("ETC")) {
        console.log("Handling special case for ETC");
        window.open(baseUrl + "1haCzEhJ4FcMTT7xUjemghG73nFbth9Ye", '_blank').focus();
    } else {
        var match = fileName.match(/^eADP\(([^)]+)\)/);
        console.log("Regex match result:", match);  // 로깅 추가

        if (match) {
            var projectCode = match[1];
            console.log("Extracted projectCode:", projectCode);  // 로깅 추가

            switch (projectCode) {
                case "eADM1":
                    window.open(baseUrl + "1M2Xb2EJlgxgpC4j7urB9J_Hiz3vTaEIF", '_blank').focus();
                    break;
                case "TCar":
                    window.open(baseUrl + "107ja2ER22gw3hfGQKzQycUy1xYrdYSh2", '_blank').focus();
                    break;
                default:
                    alert("No matching folder found for this project code: " + projectCode);
            }
        } else {
            alert("Invalid file name format for eADP pattern.");
        }
    }
}

