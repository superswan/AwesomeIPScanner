//scanner functionality 
// Create a connection to the Flask-SocketIO server
function clearTable() {
    document.getElementById('tableBody').innerHTML = '';
}

// Clear table when selected            
document.querySelector('form').addEventListener('submit', clearTable);

const socket = io.connect('http://127.0.0.1:5000');

socket.on('update_progress', function (progress) {
    const progressBar = document.getElementById('progressBar');
    progressBar.style.width = progress + '%';
    progressBar.setAttribute('aria-valuenow', progress);
});

// Event listener for 'scan_data'
socket.on('scan_data', function (entry) {
    console.log('Data received')
    let smbValue = document.getElementById('checkSMB').checked ?
        `<td>${entry.services['445'] === 'open' ? `OPEN <a href="http://${entry.IP}:445" target="_blank"><i class="fa-regular fa-share-from-square" style="color: black;"></i></a>` : (entry.services['445'] || 'N/A').toUpperCase()}</td>` :
        '';
    let httpValue = document.getElementById('checkHTTP').checked ?
        `<td>${entry.services['80'] === 'open' ? `OPEN <a href="http://${entry.IP}" target="_blank"><i class="fa-regular fa-share-from-square" style="color: black;"></i></a>` : (entry.services['80'] || 'N/A').toUpperCase()}</td>` :
        '';
    let httpsValue = document.getElementById('checkHTTPS').checked ?
        `<td>${entry.services['443'] === 'open' ? `OPEN <a href="https://${entry.IP}" target="_blank"><i class="fa-regular fa-share-from-square" style="color: black;"></i></a>` : (entry.services['443'] || 'N/A').toUpperCase()}</td>` :
        '';
    let ftpValue = document.getElementById('checkFTP').checked ?
        `<td>${entry.services['21'] === 'open' ? `OPEN <a href="ftp://${entry.IP}:21" target="_blank"><i class="fa-regular fa-share-from-square" style="color: black;"></i></a>` : (entry.services['21'] || 'N/A').toUpperCase()}</td>` :
        '';
    let rdpValue = document.getElementById('checkRDP').checked ?
        `<td>${entry.services['3389'] === 'open' ? `OPEN <a href="http://${entry.IP}:3389" target="_blank"><i class="fa-regular fa-share-from-square" style="color: black;"></i></a>` : (entry.services['3389'] || 'N/A').toUpperCase()}</td>` :
        '';
    let sshValue = document.getElementById('checkSSH').checked ?
        `<td>${entry.services['22'] === 'open' ? `OPEN <a href="ssh://${entry.IP}:22" target="_blank"><i class="fa-regular fa-share-from-square" style="color: black;"></i></a>` : (entry.services['22'] || 'N/A').toUpperCase()}</td>` :
        '';

    let tableBody = document.getElementById('tableBody');
    let row = `<tr>
            <td>${entry.status}</td>
            <td>${entry.name}</td>
            <td>${entry.IP}</td>
            <td>${entry.manufacturer}</td>
            <td>${entry.mac}</td>
            ${smbValue}
            ${httpValue}
            ${httpsValue}
            ${ftpValue}
            ${rdpValue}
            ${sshValue}
            </tr>`;
    tableBody.innerHTML += row;
});