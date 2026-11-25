#!/usr/bin/env python3
"""Ship the committed front page as the competition entry.

Reads entry.png from beside this file, checks it is a complete,
well-formed PNG inside the competition limits, and writes an exact
byte copy to /output/entry.png. No network, no clock, no randomness:
two runs produce identical bytes.

Usage: python3 main.py [output_dir]   (default /output)
"""

import hashlib
import os
import struct
import sys
import zlib

PNG_SIG = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024
DEFAULT_DIR = "/output"
SOURCE = "entry.png"


def fail(msg):
    sys.stderr.write("main.py: error: %s\n" % msg)
    raise SystemExit(1)


def scan_png(blob):
    """Walk the PNG chunk list; return (width, height, chunks).

    Rejects a bad signature, bad CRCs, a missing or misplaced IHDR,
    missing IDAT/IEND, and any bytes after IEND.
    """
    if len(blob) < 8 or blob[:8] != PNG_SIG:
        fail("not a PNG file (bad signature)")
    pos = 8
    chunks = 0
    width = height = 0
    got_data = False
    got_end = False
    while pos < len(blob):
        if pos + 8 > len(blob):
            fail("truncated chunk header at offset %d" % pos)
        size, kind = struct.unpack(">I4s", blob[pos:pos + 8])
        start = pos + 8
        end = start + size
        if end + 4 > len(blob):
            fail("truncated %s chunk" % kind.decode("latin-1", "replace"))
        body = blob[start:end]
        want_crc = struct.unpack(">I", blob[end:end + 4])[0]
        real_crc = zlib.crc32(kind + body) & 0xFFFFFFFF
        if want_crc != real_crc:
            fail("%s chunk CRC mismatch" % kind.decode("latin-1", "replace"))
        chunks += 1
        if chunks == 1:
            if kind != b"IHDR" or size != 13:
                fail("first chunk must be a 13-byte IHDR")
            width, height = struct.unpack(">II", body[:8])
            depth, ctype = body[8], body[9]
            if depth != 8 or ctype not in (2, 6):
                fail("PNG must be 8-bit RGB or RGBA, got depth %d "
                     "colour %d" % (depth, ctype))
            if width == 0 or height == 0:
                fail("PNG dimensions must be positive")
            if body[12] != 0:
                fail("PNG must not be interlaced (interlace byte %d)"
                     % body[12])
            if width > MAX_SIDE or height > MAX_SIDE:
                fail("PNG is %dx%d, over the %dx%d limit"
                     % (width, height, MAX_SIDE, MAX_SIDE))
        elif kind == b"IDAT":
            got_data = True
        elif kind == b"IEND":
            got_end = True
            if end + 4 != len(blob):
                fail("trailing bytes after IEND")
        pos = end + 4
    if not got_data:
        fail("PNG carries no IDAT chunk")
    if not got_end:
        fail("PNG carries no IEND chunk")
    return width, height, chunks


def main():
    args = sys.argv[1:]
    if len(args) > 1 or (args and args[0] in ("-h", "--help")):
        print("usage: python3 main.py [output_dir]")
        raise SystemExit(0 if args else 2)
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, SOURCE)
    try:
        with open(src, "rb") as fh:
            blob = fh.read()
    except OSError:
        fail("entry.png is not beside main.py")
    if len(blob) > MAX_BYTES:
        fail("PNG is %d bytes, over the %d-byte limit"
             % (len(blob), MAX_BYTES))
    width, height, chunks = scan_png(blob)
    out_dir = args[0] if args else DEFAULT_DIR
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, SOURCE)
    with open(target, "wb") as fh:
        fh.write(blob)
    with open(target, "rb") as fh:
        written = fh.read()
    if hashlib.sha256(written).digest() != hashlib.sha256(blob).digest():
        fail("written entry.png differs from the source bytes")
    print("entry.png: %d bytes, %dx%d, %d chunks, sha256 %s -> %s"
          % (len(blob), width, height, chunks,
             hashlib.sha256(blob).hexdigest()[:16], target))


if __name__ == "__main__":
    main()
