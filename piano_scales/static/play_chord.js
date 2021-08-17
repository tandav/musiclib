//const host = 'http://0.0.0.0:8001'
const host = 'http://0.0.0.0:8001'

const play_chord = chord => {
    const url = host + '/play_chord/' + chord
    console.log(url)
    fetch(url)
}

//fetch('https://gist.githubusercontent.com/tandav/b1a422d49a41f8364c5a2c862bb0d5b4/raw/n_tabs.json')
//.then(response => response.json())
//.then(json => {
//    document.getElementById('n_tabs').textContent = json.n_tabs
//    document.getElementById('stats').textContent = 'min='+ json.min + ' max=' + json.max + ' mean=' + json.mean + ' std=' + json.std + ' median=' + json.median + ' n=' + json.n
//    document.getElementById('n_windows').textContent = json.n_windows
//    document.getElementById('updated').textContent = 'updated: ' + ago((new Date).getTime() - new Date(json.updated_at))
//    document.getElementById('hosts').textContent = JSON.stringify(json.hosts)
//})