#!/usr/bin/env python3
"""Convert an owned MP4 or other video into a silent X36V test clip.

Requires ffmpeg on the PC. X36V is intentionally simple, with raw RGB frames.
Audio, MP4/H.264 decoding on Xbox 360 and hardware acceleration are NOT provided.
"""
import argparse
import shutil
import struct
import subprocess
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("input",type=Path)
    p.add_argument("output",type=Path)
    p.add_argument("--width",type=int,default=320)
    p.add_argument("--height",type=int,default=180)
    p.add_argument("--fps",type=int,default=12)
    p.add_argument("--seconds",type=int,default=20)
    args=p.parse_args()
    if not args.input.is_file():p.error("Input media file not found")
    if args.width not in range(16,641) or args.height not in range(16,361):
        p.error("Allowed dimensions: 16..640 by 16..360")
    if not 1<=args.fps<=30 or not 1<=args.seconds<=30:
        p.error("Allowed FPS: 1..30 and clip length: 1..30 seconds")
    if not shutil.which("ffmpeg"):p.error("Install ffmpeg to convert existing videos on the PC")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    size=args.width*args.height*3
    max_frames=args.fps*args.seconds
    cmd=["ffmpeg","-nostdin","-v","error","-i",str(args.input),
         "-t",str(args.seconds),"-vf",f"fps={args.fps},scale={args.width}:{args.height}:flags=fast_bilinear",
         "-an","-pix_fmt","rgb24","-f","rawvideo","pipe:1"]
    proc=subprocess.Popen(cmd,stdout=subprocess.PIPE)
    frames=0
    try:
        with args.output.open("wb") as out:
            out.write(struct.pack("<4sHHII",b"X36V",args.width,args.height,args.fps,0))
            while frames<max_frames:
                data=bytearray()
                while len(data)<size:
                    piece=proc.stdout.read(size-len(data))
                    if not piece:break
                    data.extend(piece)
                if len(data)!=size:break
                out.write(data)
                frames+=1
            proc.stdout.close()
            proc.wait(timeout=20)
            if not frames:raise ValueError("ffmpeg did not decode any complete RGB frame")
            out.seek(0)
            out.write(struct.pack("<4sHHII",b"X36V",args.width,args.height,args.fps,frames))
    except Exception:
        proc.kill()
        args.output.unlink(missing_ok=True)
        raise
    print(f"Created {args.output}: {frames} video-only frames at {args.fps} FPS, no audio")
if __name__=="__main__":
    main()
