import argparse
import ffmpeg
import os
import sys

from .format import Format
from .logger import warn
from .song import Song

replace = False
quiet = False
MIN_BITRATE = 128

def run():
    parser = argparse.ArgumentParser(description='Convert audio files.')
    parser.add_argument('file',nargs='+',
        help='audio file')
    parser.add_argument('-w', '--wav', action='store_true',
        help='Lossless audio, by converting to wav',
        default=False)
    parser.add_argument('-f', '--flac', action='store_true',
        help='Lossless compress audio, by converting to flac',
        default=False)
    parser.add_argument('-c', '--collection',
        help='Set collection name for output',
        default=None)
    parser.add_argument('-v', '--variant', action='store_true',
        help='Add variant to title',
        default=False)
    parser.add_argument('--bitdepth',
        help='Set bit depth',
        default=None)
    parser.add_argument('--samplerate',
        help='Set sample rate (khz)',
        default=None)
    parser.add_argument('--seconds',
        help='Crop to number of seconds',
        default=None)
    parser.add_argument('--start',
        help='Start at given number of seconds',
        default=None)
    args = parser.parse_args()
    for audioIn in args.file:
        print(f"Converting audio file : {audioIn}")
        if not os.path.exists(audioIn):
            print(f"File {audioIn} does not exist")
            return
        song = Song(audioIn)
        # Enforce 256 bitrate unless input is worse
        bitrate = 256 if song.bitrate > 256 else song.bitrate
        bitdepth = song.bitdepth if args.bitdepth is None else int(args.bitdepth)
        samplerate = song.samplerate if args.samplerate is None else int(args.samplerate)

        if (bitrate < MIN_BITRATE):
            # Bitrate below MIN_BITRATE is limited value
            warn(f"Not converting to {bitrate} since below minumum allowed {MIN_BITRATE}")
            return
        if args.wav:
            destination = Format('wav', bitdepth = bitdepth, samplerate = samplerate)
        elif args.flac:
            destination = Format('flac', bitdepth = bitdepth)
        else:
            destination = Format('mp3', bitrate)

        print(f"Converting audio file : {audioIn} : {song} {song.format}-> {destination}")
        if song.format == destination:
            printf("No conversion necessary")
            return

        title = song.title
        if args.variant:
            title += " (" + str(destination.qualityAsString) + ")"

        if args.collection:
            outFile=f"{song.rootDirectory}/{args.collection}/{song.pathInCollection}/{title} - {song.artist} - {song.album}.{destination.ext}"
        else:
            outFile=f"./{title} - {song.artist} - {song.album}.{destination.ext}"
        ffmpegArgs = {
            **destination.ffmpegArgs,
            **song.ffmpegArgs
        }
        ffmpegArgs['metadata:g:0']:f"title={title}"
        if args.seconds is not None:
            start = int(args.start) if args.start is not None else 0
            end = int(args.seconds) + start
            ffmpegArgs['ss'] = start
            ffmpegArgs['to'] = end

        print(f"ffmpeg args : {ffmpegArgs}")
        (
            ffmpeg
                .input(audioIn)
                .filter_('loudnorm')
                .output(outFile, **ffmpegArgs)
                .run(**{
                    'quiet':quiet,
                    'overwrite_output':replace
                })
        )