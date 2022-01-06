from collections import defaultdict

chromatic_notes = 'CdDeEFfGaAbB'  # todo make variable here, delete from config, reimport everywhere, maybe circular imports
note_i = {note: i for i, note in enumerate(chromatic_notes)}
is_black = {note: bool(int(x)) for note, x in zip(chromatic_notes, '010100101010')}

neighsbors_min_shared = {'diatonic': 0, 'pentatonic': 0}


diatonic = 'major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'minor', 'locrian'
pentatonic = 'p_major', 'p_dorian', 'p_phrygian', 'p_mixolydian', 'p_minor'
sudu = 's_major', 's_dorian', 's_phrygian', 's_lydian', 's_mixolydian', 's_minor'
kinds = {k: 'diatonic' for k in diatonic} | {k: 'pentatonic' for k in pentatonic} | {k: 'sudu' for k in sudu}


# if change: also change in static/main.css
scale_colors = dict(
    major='FFFFFF',
    dorian='54E346',
    phrygian='00FFCC',
    lydian='68A6FC',
    mixolydian='FFF47D',
    minor='D83A56',
    locrian='B980F0',
)
scale_colors['p_major'] = scale_colors['major']
scale_colors['p_dorian'] = scale_colors['dorian']
scale_colors['p_phrygian'] = scale_colors['phrygian']
scale_colors['p_mixolydian'] = scale_colors['mixolydian']
scale_colors['p_minor'] = scale_colors['minor']

scale_colors['s_major'] = scale_colors['major']
scale_colors['s_dorian'] = scale_colors['dorian']
scale_colors['s_phrygian'] = scale_colors['phrygian']
scale_colors['s_lydian'] = scale_colors['lydian']
scale_colors['s_mixolydian'] = scale_colors['mixolydian']
scale_colors['s_minor'] = scale_colors['minor']

WHITE_COLOR = (0xaa,) * 3
BLACK_COLOR = (0x50,) * 3
WHITE = 0xFF, 0xFF, 0xFF
BLACK = 0, 0, 0
RED_COLOR = 0xff, 0, 0
GREEN_COLOR = 0, 0xff, 0
BLUE_COLOR = 0, 0, 0xff

chord_colors = {
    'minor': scale_colors['minor'],
    'major': scale_colors['major'],
    'diminished': scale_colors['locrian'],
}

default_octave = 5
# DEFAULT_TUNING = 440  # default A hz tuning
DEFAULT_TUNING = 500
RANDOM_TUNING_RANGE = 420, 510
tuning = DEFAULT_TUNING


# piano_img_size = 14 * 60, 280
piano_img_size = 14 * 18, 85
beats_per_minute = 120
beats_per_second = beats_per_minute / 60
beats_per_bar = 4
bar_seconds = beats_per_bar / beats_per_second


# daw
sample_rate = 44100  # samples per second
midi_folder = 'static/midi/'
# midi_file = 'weird.mid'
# midi_file = 'overlap.mid'
# midi_file = 'dots.mid'
# midi_file = 'halfbar.mid'
# midi_file = 'halfbar-and-short.mid'
# midi_file = 'bassline.mid'
# midi_file = 'drumloop.mid'
# midi_file = '4-4-8.mid'
# chunk_size = 1024 * 32
chunk_size = 1024
# chunk_size = 1024 * 2
# chunk_size = 1024 * 128
# chunk_size = 1024 * 4
chunk_seconds = chunk_size / sample_rate
wav_output_file = 'out.wav'

# samples
kick = 'static/samples/kick-909.wav'
hat = 'static/samples/open-hat-909.wav'
clap = 'static/samples/clap-909.wav'


# streaming
audio_pipe = 'audio.fifo'
video_pipe = 'video.fifo'

# fps = 24
# fps = 30
# fps = 48
# fps = 50
# fps = 44
# fps = 40
# fps = 30
# fps = 55
fps = 60

# frame_width, frame_height = 2560, 1440
frame_width, frame_height = 1920, 1080  # 1080p, recommended bitrate 4.5M
# frame_width, frame_height = 1280, 720  # 720p
# frame_width, frame_height = 854, 480  # 480p
# frame_width, frame_height = 640, 360 # 360p
# frame_width, frame_height = 426, 240  # 240p
# video_bitrate = '500k'
# video_bitrate = '3000k'
# video_bitrate = '3m'
audio_bitrate = '128k'
# video_bitrate = '12M'
# video_bitrate = '24M'
# keyframe_seconds = 0.05  # drastically changes bitrate
keyframe_seconds = 0.25  # drastically changes bitrate
# keyframe_seconds = 0.5  # drastically changes bitrate

gop = int(keyframe_seconds * fps)
draw_threads = 1
# assert draw_threads == 1

bars_per_screen = 4
screen_seconds = bars_per_screen * bar_seconds

chord_px = frame_height / bars_per_screen
# pxps = frame_height // screen_seconds  # pixels per second
pxps = frame_height / screen_seconds  # pixels per second

# video_queue_item_size = 20
video_queue_item_size = 1
assert video_queue_item_size < fps


# OUTPUT_VIDEO = '/tmp/output.flv'
# OUTPUT_VIDEO = '/dev/null'
OUTPUT_VIDEO = None

log_path = 'logs/log.jsonl'


note_range = None
messages = []

progressions = None
progressions_queue = None


progressions_search_cache = defaultdict(list)

ui_thread = None


# midi explorer ui

# MIDI_UI_FILE = 'static/midi/vespers-04.mid'
MIDI_UI_FILE = 'static/midi/vivaldi-winter.mid'
