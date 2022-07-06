import asyncio
from functools import wraps

import click
from pydub import AudioSegment
from shazamio import Shazam, Serialize


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.command()
@click.argument("file", type=click.Path(exists=True, readable=True, resolve_path=True), nargs=1)
@click.option('-s', '--split-seconds', 'split_seconds', default=60, type=int, show_default=True)
@click.option('-d', '--include-duplicates', 'duplicates', is_flag=True, show_default=True, help='Include duplicates in output')
@coro
async def cli(file, split_seconds, duplicates):
    sound = AudioSegment.from_file(file)
    shazam = Shazam()
    results = []
    for i, chunk in enumerate(sound[::split_seconds * 1000]):
        res = await shazam.recognize_song(chunk)
        ser = Serialize.full_track(res)
        if not ser.track or not ser.track.key:
            continue
        if duplicates:
            if results[-1].track.key == ser.track.key:
                continue
        else:
            if next((x for x in results if x.track.key == ser.track.key), None) is not None:
                continue
        results.append(ser)
        print('%s - %s' % (ser.track.title, ser.track.subtitle))


if __name__ == '__main__':
    cli()
