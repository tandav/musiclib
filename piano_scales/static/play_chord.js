const host = 'http://0.0.0.0:8001'

const play_chord = chord => {
    const url = host + '/play_chord/' + chord
    console.log(url)
    fetch(url)
}
