import os.path
from playsound import playsound
import asyncio
import time


async def play_voice_clip():
    audio_file = 'voicechair-trimmed.mp3'
    print("playing...")
    playsound(audio_file, block=False)


async def test_multi_in_flight():
    print("play 1")
    await play_voice_clip()
    print("sleep 1")
    time.sleep(1)
    print("play 2")
    await play_voice_clip()
    print("sleep 2")
    time.sleep(5)
    


if __name__ == "__main__":
    asyncio.run(test_multi_in_flight())

