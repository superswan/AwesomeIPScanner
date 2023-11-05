// table options and service selection
function toggleColumn(serviceId, isChecked) {
    const column = document.getElementById(serviceId);
    if (column) {
        column.style.display = isChecked ? "" : "none";

        // Also hide or show the data cells in the column
        let rows = document.getElementById('tableBody').rows;
        for (let i = 0; i < rows.length; i++) {
            rows[i].cells[column.cellIndex].style.display = isChecked ? "" : "none";
        }
    }
}

document.getElementById('checkSMB').addEventListener('change', function () {
    toggleColumn('smbColumn', this.checked);
});

document.getElementById('checkHTTP').addEventListener('change', function () {
    toggleColumn('httpColumn', this.checked);
});

document.getElementById('checkHTTPS').addEventListener('change', function () {
    toggleColumn('httpsColumn', this.checked);
});

document.getElementById('checkFTP').addEventListener('change', function () {
    toggleColumn('ftpColumn', this.checked);
});

document.getElementById('checkRDP').addEventListener('change', function () {
    toggleColumn('rdpColumn', this.checked);
});

document.getElementById('checkSSH').addEventListener('change', function () {
    toggleColumn('sshColumn', this.checked);
});

document.addEventListener('DOMContentLoaded', function () {
    toggleColumn('smbColumn', document.getElementById('checkSMB').checked);
    toggleColumn('httpColumn', document.getElementById('checkHTTP').checked);
    toggleColumn('httpsColumn', document.getElementById('checkHTTPS').checked);
    toggleColumn('ftpColumn', document.getElementById('checkFTP').checked);
    toggleColumn('rdpColumn', document.getElementById('checkRDP').checked);
    toggleColumn('sshColumn', document.getElementById('checkSSH').checked);
});