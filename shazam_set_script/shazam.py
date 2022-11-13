from aiomultiprocess import Pool
from click import ClickException
from pydub import AudioSegment
from shazamio import Shazam, Serialize


class ShazamException(ClickException):
    pass


class ShazamProcessor:
    def __init__(self, sound: AudioSegment, split_seconds=60, duplicates=False):
        self.split_seconds = split_seconds
        self.duplicates = duplicates
        self.sound = sound
        self.shazam = Shazam()
        self.results = []

    async def process_chunk(self, chunk: AudioSegment):
        res = await self.shazam.recognize_song(chunk)
        ser = Serialize.full_track(res)
        if not ser.track or not ser.track.key:
            return
        return ser

    async def process(self):
        tasks = ()
        async with Pool(processes=4) as pool:
            async for result in pool.map(self.process_chunk, self.sound[::self.split_seconds * 1000]):
                if not result:
                    continue
                if self.duplicates and self.results:
                    if self.results[-1].track.key == result.track.key:
                        continue
                else:
                    if next((x for x in self.results if x.track.key == result.track.key), None) is not None:
                        continue
                self.results.append(result)
                print('%s - %s' % (result.track.title, result.track.subtitle))
