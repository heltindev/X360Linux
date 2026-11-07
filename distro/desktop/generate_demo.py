#!/usr/bin/env python3
"""Make original demo photo and silent X36V clip for X360Linux's framebuffer UI."""
import argparse
from pathlib import Path
import struct
import zlib

def png_chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(
        ">I", zlib.crc32(kind + data) & 0xffffffff
    )

def photo(path):
    w,h=240,135
    rows=[]
    for y in range(h):
        line=bytearray(b"\x00")
        for x in range(w):
            bar=28<x<212 and 28<y<106
            line.extend(((15+x//6) if not bar else 36,
                         (25+y//4) if not bar else 130+x//8,
                         (45+x//8) if not bar else 77))
        rows.append(bytes(line))
    ihdr=struct.pack(">IIBBBBB",w,h,8,2,0,0,0)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"+png_chunk(b"IHDR",ihdr)
        +png_chunk(b"IDAT",zlib.compress(b"".join(rows),9))
        +png_chunk(b"IEND",b"")
    )

def video(path):
    w,h,fps,frames=160,90,10,30
    with path.open("wb") as f:
        f.write(struct.pack("<4sHHII",b"X36V",w,h,fps,frames))
        for frame in range(frames):
            b=bytearray()
            for y in range(h):
                for x in range(w):
                    moving=abs(x-(frame*6)%(w+30)+15)<14
                    b.extend((
                        min(255,15+x//2+(150 if moving else 0)),
                        min(255,30+y+(80 if moving else 0)),
                        min(255,55+frame*3+(24 if moving else 0))
                    ))
            f.write(b)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    photos=args.output_dir/"photos"
    videos=args.output_dir/"videos"
    photos.mkdir(parents=True,exist_ok=True)
    videos.mkdir(parents=True,exist_ok=True)
    photo(photos/"x360linux-demo.png")
    video(videos/"x360linux-demo.x360v")
    print("Original X360Linux demo media generated (silent video).")
if __name__=="__main__":
    main()
