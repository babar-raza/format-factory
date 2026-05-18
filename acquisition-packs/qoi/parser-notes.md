# QOI Parser Notes
# Format: Quite OK Image Format (.qoi)
# Gate: 4 — Parser Planning
# Sprint: FORMAT-FACTORY-R25-AI-PHASE1-GATE4-FORWARD-TRAIN-AND-R24-METADATA-SYNC-001
# Date: 2026-05-18
# Authorization: Gate 4 prototype planning only — no production source authorized

## Binary Structure

QOI header (14 bytes):
- Bytes 0-3:  magic = b'qoif'
- Bytes 4-7:  width  (uint32 big-endian)
- Bytes 8-11: height (uint32 big-endian)
- Byte  12:   channels (3=RGB, 4=RGBA)
- Byte  13:   colorspace (0=sRGB+linear alpha, 1=all-linear)

QOI chunks (variable length after header):
- QOI_OP_RGB   (0b11111110): 3 bytes R G B
- QOI_OP_RGBA  (0b11111111): 4 bytes R G B A
- QOI_OP_INDEX (0b00xxxxxx): 1 byte, index into 64-color running array
- QOI_OP_DIFF  (0b01xxxxxx): 1 byte, small delta from previous pixel
- QOI_OP_LUMA  (0b10xxxxxx): 2 bytes, medium luma delta
- QOI_OP_RUN   (0b11xxxxxx): 1 byte, run-length encode (1-62 pixels)

QOI end marker (8 bytes): 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x01

## Python stdlib parsing approach

```python
import struct

QOI_OP_RGB   = 0xFE
QOI_OP_RGBA  = 0xFF
QOI_OP_INDEX = 0b00000000
QOI_OP_DIFF  = 0b01000000
QOI_OP_LUMA  = 0b10000000
QOI_OP_RUN   = 0b11000000
QOI_MASK_2   = 0b11000000

def probe_qoi(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:4] != b'qoif':
        raise ValueError('Not a QOI file')
    width, height = struct.unpack('>II', data[4:12])
    channels, colorspace = data[12], data[13]
    return {
        'width': width, 'height': height,
        'channels': channels, 'colorspace': colorspace,
        'pixel_count': width * height,
        'data_bytes': len(data) - 14 - 8,
    }
```

Full decoder loop (prototype):
```python
def decode_qoi(path):
    with open(path, 'rb') as f:
        data = f.read()
    w, h = struct.unpack('>II', data[4:12])
    channels = data[12]
    pixels = []
    seen = [(0, 0, 0, 0)] * 64
    prev = (0, 0, 0, 255)
    pos = 14
    while len(pixels) < w * h:
        b = data[pos]; pos += 1
        if b == QOI_OP_RGB:
            r, g, b_ = data[pos:pos+3]; pos += 3
            prev = (r, g, b_, prev[3])
        elif b == QOI_OP_RGBA:
            r, g, b_, a = data[pos:pos+4]; pos += 4
            prev = (r, g, b_, a)
        elif (b & QOI_MASK_2) == QOI_OP_INDEX:
            prev = seen[b & 0x3F]
        elif (b & QOI_MASK_2) == QOI_OP_DIFF:
            dr = ((b >> 4) & 3) - 2
            dg = ((b >> 2) & 3) - 2
            db = (b & 3) - 2
            prev = ((prev[0]+dr)%256, (prev[1]+dg)%256, (prev[2]+db)%256, prev[3])
        elif (b & QOI_MASK_2) == QOI_OP_LUMA:
            b2 = data[pos]; pos += 1
            dg = (b & 0x3F) - 32
            dr = dg + ((b2 >> 4) & 0xF) - 8
            db_ = dg + (b2 & 0xF) - 8
            prev = ((prev[0]+dr)%256, (prev[1]+dg)%256, (prev[2]+db_)%256, prev[3])
        else:  # QOI_OP_RUN
            run = (b & 0x3F) + 1
            pixels.extend([prev] * run)
            continue
        hash_idx = (prev[0]*3 + prev[1]*5 + prev[2]*7 + prev[3]*11) % 64
        seen[hash_idx] = prev
        pixels.append(prev)
    return w, h, channels, pixels
```

## Gate 4 Prototype Scope

| Feature | Planned |
|---------|---------|
| Header probe (dimensions, channels) | YES |
| Magic/format validation | YES |
| Pixel decode (all 6 chunk types) | YES |
| Raw pixel array output | YES |
| PNG export (via stdlib only — not available) | NO (needs Pillow) |
| Animation | NO (QOI is still-only) |
| Write/encode | NO (phase 2) |

## Status
gate_4_parser_notes: ready_for_prototype_planning
production_source_authorized: false
