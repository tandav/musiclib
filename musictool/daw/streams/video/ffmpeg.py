import subprocess

from musictool import config


def make_process(output):
    cmd = (
        'ffmpeg',
        # '-loglevel', 'trace',
        '-threads', '6',
        # '-threads', '7',
        # '-y', '-r', '60', # overwrite, 60fps
        # '-re',
        '-y',

        # '-err_detect', 'ignore_err',
        '-f', 's16le',  # means 16bit input
        '-acodec', 'pcm_s16le',  # means raw 16bit input
        '-r', str(config.sample_rate),  # the input will have 44100 Hz
        '-ac', '1',  # number of audio channels (mono1/stereo=2)
        # '-thread_queue_size', thread_queue_size,
        '-thread_queue_size', '1024',
        '-i', config.audio_pipe,

        '-s', f'{config.frame_width}x{config.frame_height}',  # size of image string
        '-f', 'rawvideo',
        '-pix_fmt', 'rgba',  # format
        # '-pix_fmt', 'rgb24',  # format
        '-r', str(config.fps),  # input framrate. This parameter is important to stream w/o memory overflow
        # '-vsync', 'cfr', # kinda optional but you can turn it on
        # '-f', 'image2pipe',
        # '-i', 'pipe:', '-', # tell ffmpeg to expect raw video from the pipe
        # '-i', '-',  # tell ffmpeg to expect raw video from the pipe
        '-thread_queue_size', '128',
        # '-thread_queue_size', '8',
        # '-blocksize', '2048',
        '-i', config.video_pipe,  # tell ffmpeg to expect raw video from the pipe

        # '-filter:v', f'fps={config.fps}', # tryna get very stable fps?? maybe this is useless
        # '-c:a', 'libvorbis',
        # '-ac', '1',  # number of audio channels (mono1/stereo=2)
        # '-c:v', 'h264_videotoolbox',
        # '-c:v', 'h264_vaapi',
        '-c:v', 'libx264',
        # '-c:v', 'libx264rgb',
        '-pix_fmt', 'yuv420p',
        # '-pix_fmt', 'rgba',
        '-tune', 'animation',

        # ultrafast or zerolatency kinda makes audio and video out of sync when save to file (but stream to yt is kinda OK)
        # '-preset', 'ultrafast',
        # '-preset', 'slow',
        # '-preset', 'slower',
        # '-crf', '18',
        # '-tune', 'zerolatency',

        # '-g', '150',  #  GOP: group of pictures
        '-g', str(config.gop),  # GOP: group of pictures
        # '-g', str(config.fps // 2),  # GOP: group of pictures
        # '-x264opts', 'no-scenecut',
        # '-x264-params', f'keyint={keyframe_seconds * config.fps}:scenecut=0',
        '-vsync', 'cfr',
        # '-vsync', 'drop',
        # '-vsync', 'vfr',
        # '-async', '1',
        # '-tag:v', 'hvc1', '-profile:v', 'main10',
        '-b:a', config.audio_bitrate,
        # '-b:v', config.video_bitrate,
        '-deinterlace',
        # '-r', str(config.fps),

        '-r', str(config.fps),  # output framerate

        # '-blocksize', '2048',
        # '-flush_packets', '1',

        '-f', 'flv',
        '-flvflags', 'no_duration_filesize',
        # '-f', 'mp4',

        output,
    )
    return subprocess.Popen(cmd)
