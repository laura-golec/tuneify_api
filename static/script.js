const apiUrl = 'https://tuneify.lauragolec.com/'

function getConfirmation() {
    fetch(`${apiUrl}confirm/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(response_data => {
            document.getElementById('confirmation').innerText = 'Connection to server is established'
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('confirmation').innerText = 'Server Down'
        });
}