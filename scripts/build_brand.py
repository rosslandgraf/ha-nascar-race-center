"""Render the project's original geometric NRC monogram; no fonts or media inputs."""

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = (
    (32, 168, 32, 88),
    (32, 88, 76, 168),
    (76, 168, 76, 88),
    (104, 168, 104, 88),
    (104, 88, 140, 88),
    (140, 88, 140, 126),
    (140, 126, 104, 126),
    (112, 126, 146, 168),
    (220, 88, 176, 88),
    (176, 88, 176, 168),
    (176, 168, 220, 168),
)


def render() -> tuple[bytes, str]:
    rows = bytearray()
    for y in range(256):
        rows.append(0)
        for x in range(256):
            color = (21, 37, 52, 255)
            # Rounded square, with transparent corners.
            dx, dy = max(36 - x, x - 219, 0), max(36 - y, y - 219, 0)
            if dx * dx + dy * dy > 36 * 36:
                color = (0, 0, 0, 0)
            for x1, y1, x2, y2 in PATHS:
                ratio = max(
                    0,
                    min(
                        1,
                        ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1))
                        / ((x2 - x1) ** 2 + (y2 - y1) ** 2),
                    ),
                )
                if (x - x1 - ratio * (x2 - x1)) ** 2 + (
                    y - y1 - ratio * (y2 - y1)
                ) ** 2 <= 25:
                    color = (233, 242, 253, 255)
                    break
            rows.extend(color)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data))
        )

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 256, 256, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows, 9))
        + chunk(b"IEND", b"")
    )
    lines = " ".join(f"M{x1} {y1}L{x2} {y2}" for x1, y1, x2, y2 in PATHS)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">'
        '<rect width="256" height="256" rx="36" fill="#152534"/>'
        f'<path d="{lines}" fill="none" stroke="#e9f2fd" '
        'stroke-width="10" stroke-linecap="round"/></svg>\n'
    )
    return png, svg


if __name__ == "__main__":
    target = ROOT / "custom_components/nascar_race_center/brand"
    target.mkdir(exist_ok=True)
    png, svg = render()
    (target / "icon.png").write_bytes(png)
    (target / "icon.svg").write_text(svg)
