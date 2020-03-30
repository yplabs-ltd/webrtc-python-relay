
import asyncio
import os
import logging
from aiortc import (
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
    RTCConfiguration,
    RTCIceServer
)
from aiortc.mediastreams import AudioStreamTrack, VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
#logging.basicConfig(level=logging.DEBUG)

ROOT = os.path.dirname(__file__)
logger = logging.getLogger("pc")

async def create_connection(is_caller=True, desc=None):
    # def add_tracks():
    #     if player and player.audio:
    #         print("ADD AUDIO")
    #         pc.addTrack(player.audio)

    #     if player and player.video:
    #         print("ADD VIDEO")
    #         pc.addTrack(player.video)

    pc = RTCPeerConnection(
        configuration=RTCConfiguration(
        iceServers=[RTCIceServer(
        urls=['stun:stun.l.google.com:19302'])]))
    player = MediaPlayer("output.wav")
    recorder = MediaRecorder('/Users/pjc/Server/webrtc-connection-test/result.wav')
    pc.addTrack(player.audio)

    @pc.on("track")
    def on_track(track):
        print(f"Track received {track.kind}")
        if track.kind == "audio":
            recorder.addTrack(track)
        @track.on("ended")
        async def on_ended():
            print(f"Track {track.kind} ended")
            await recorder.stop()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc.on('icecandidate')
    def icecandidate(item):
        print("icecandidate")
    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print(f"ICE connection state is {pc.iceConnectionState}")
        if pc.iceConnectionState == "failed":
            await pc.close()

    if is_caller:
        print("createOffer With Bind")
        sd = await pc.createOffer()
        await pc.setLocalDescription(sd)
        await recorder.start()
    else:
        print("Bind Offer With Create Answer")
        await pc.setRemoteDescription(desc)
        sd = await pc.createAnswer()
        await pc.setLocalDescription(sd)
        await recorder.start()

    return pc.localDescription, pc, recorder

async def main():
    offer, pc, recorder = await create_connection(is_caller=True, desc=None)
    answer, pc2, recorder2 = await create_connection(is_caller=False, desc=offer)
    await pc.setRemoteDescription(answer)
    print("FINISH")
    await asyncio.sleep(10)

if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  try:
    loop.run_until_complete(
      main()
    )
  except KeyboardInterrupt:
    pass
