const apiUrl = 'https://api.lauragolec.com/tuneify/'

var apiKey = ''

function updateApiKey() {
    apiKey = document.getElementById('apiKey').value
}

function displayBrowse(jsonData, requestedDir) {
    let html = 'Items:';
    root = jsonData[0]
    console.log(requestedDir)
    
    var previousDirectory = requestedDir.substring(0, requestedDir.lastIndexOf('/'))
    previousDirectory === '' ? previousDirectory = '/' : previousDirectory;
    console.log(previousDirectory);
    (requestedDir != '/')? html += `<div onclick="getBrowse('${previousDirectory}')"><strong>Go Back</strong></div>`: null;

    jsonData.forEach(item => {
        html += `<div class='item'>`;
        for (const key in item) {
            if (item.hasOwnProperty(key)) {
                    path = item[key][0].path
                    html += `<div onclick="console.log('${path}'); getBrowse('${path}')"><strong>${path}:</strong></div>`;
                const values = item[key];
                
                if (Array.isArray(values)) {
                    values.forEach(value => {
                        if (value.name != undefined){
                            html += `<div class='value'">${value.name}</div>`;
                        }
                    });
                } else {
                    if (values.name != undefined){
                        html += `<div class='value'">${values.name}</div>`;
                    }   
                }
            }
        }
        html += `</div>`;
    });

    document.getElementById('browseList').innerHTML = html;
}


function displayAlbums(jsonData) {
    const albums = extractAlbums(jsonData);
    let html = 'Albums:';

    albums.forEach(album => {
        html += `
            <div class='track'>
                <img src="${album.cover}" alt="Album Cover">
                <div>
                    <p>${album.title}</p>
                </div>
            </div>
        `;
    });

    document.getElementById('albumList').innerHTML = html;
}

function displayArtists(jsonData) {
    const artists = extractArtists(jsonData);
    let html = 'Artists:';

    artists.forEach(artist => {
        html += `
            <div class='track'>
                <img src="${artist.picture}" alt="Artist Image">
                <div>
                    <p>${artist.name}</p>
                </div>
            </div>
        `;
    });

    document.getElementById('artistList').innerHTML = html;
}

function displayTracks(jsonData) {
    const tracks = jsonData.data;
    let html = 'Tracks:';

    tracks.forEach(track => {
        html += `
            <div class='track'>
                <img src="${track.album.cover_medium}" alt="Album Cover">
                <div>
                    <p>${track.title} - ${track.artist.name}</p>
                </div>
            </div>
        `;
    });

    document.getElementById('trackList').innerHTML = html;
}

function extractArtists(jsonData) {
    const data = jsonData.data;

    const uniqueArtists = new Set();
    data.forEach(track => {
        const artistObject = track.artist;
        const isUnique = [...uniqueArtists].every(artist => {
            return artist.name !== artistObject.name && artist.id !== artistObject.id;
        });
        if (isUnique) {
            uniqueArtists.add(artistObject);
        }
    });
    return [...uniqueArtists];
}

function extractAlbums(jsonData) {
    const data = jsonData.data;

    const uniqueAlbums= new Set();
    data.forEach(track => {
        const albumObject = track.album;
        const isUnique = [...uniqueAlbums].every(album => {
            return album.title !== albumObject.title && album.id !== albumObject.id;
        });
        if (isUnique) {
            uniqueAlbums.add(albumObject);
        }
    });
    return [...uniqueAlbums];
}

function getSearch(query) {
    var query = document.getElementById('search').value;
    fetch(`${apiUrl}search/?q=${query}&api_key=${apiKey}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(response_data => {
            console.log(response_data)
            displayArtists(response_data)
            displayAlbums(response_data);
            displayTracks(response_data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function getBrowse(query) {
    if(query == undefined){
        query = document.getElementById('browse').value;
    }
    console.log('searching for ', query)
    fetch(`${apiUrl}browse/?q=${query}&api_key=${apiKey}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(response_data => {
            console.log(response_data)
            displayBrowse(response_data, query)
        })
        .catch(error => {
            console.error('Error:', error);
        });
}