"""Rebuild the FLEX film card from the bundled NASA clip and a local vision model.

    py -m pip install Pillow imageio-ffmpeg
    py server/analyze_flex_clip.py

Ollama must already be running with gemma4:12b installed. The original video is
the 960 x 540 WebM download at https://svs.gsfc.nasa.gov/11318/.
"""

import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import urllib.request
from zipfile import ZipFile, ZipInfo

import imageio_ffmpeg
from PIL import Image

from film_review import INPUTS, SAMPLE_COUNT, candidate_pair, classify_samples

MEDIA = Path(__file__).resolve().parents[1] / "console" / "lab-media"
CLIP = MEDIA / "flex-iss.webm"
SHA256 = "7b2d822fff1f2794887dc042c4de42f8754490fc2cfc8ac4201962319558ab58"
MODEL = "gemma4:12b"
OLLAMA = "http://127.0.0.1:11434/api/"
WIDTH, HEIGHT = 480, 270


def sample_clip():
    # The source is 30 fps. Keep every 30th decoded frame, with no frame interpolation.
    raw = subprocess.check_output([
        imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(CLIP),
        "-vf", rf"select=not(mod(n\,30)),scale={WIDTH}:{HEIGHT}",
        "-fps_mode", "passthrough", "-pix_fmt", "rgb24", "-f", "rawvideo", "-",
    ])
    size = WIDTH * HEIGHT * 3
    if len(raw) % size or len(raw) // size != SAMPLE_COUNT:
        raise ValueError("Expected 24 whole-second samples from the verified source")
    return [Image.frombytes("RGB", (WIDTH, HEIGHT), raw[i:i + size]) for i in range(0, len(raw), size)]


def model_image(frame):
    # Crop the same fixed camera region in every sample and lift faint pixel values.
    # The stills shown beside the original video do not receive this enhancement.
    detail = frame.crop((145, 55, 315, 215)).resize((340, 320))
    detail = detail.point([round(255 * (i / 255) ** 0.65) for i in range(256)] * 3)
    stream = io.BytesIO()
    detail.save(stream, format="JPEG", quality=95)
    return stream.getvalue()


def local_api(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(OLLAMA + path, data, {"Content-Type": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=180) as response:
        return json.load(response)


def main():
    if hashlib.sha256(CLIP.read_bytes()).hexdigest() != SHA256:
        raise ValueError("Clip differs from the NASA source used to build this card")
    frames = sample_clip()
    # Finish generation before replacing the bundled result.
    with tempfile.TemporaryDirectory(dir=MEDIA) as staging:
        stage = Path(staging)
        archive = stage / INPUTS.name
        with ZipFile(archive, "w") as output:
            for second, frame in enumerate(frames):
                output.writestr(ZipInfo(f"{second:02}.jpg"), model_image(frame))
        visible = classify_samples(MODEL, local_api, archive)
        result = candidate_pair(visible)
        before, after = result["before"], result["after"]
        if before is None:
            raise ValueError("No unambiguous frame pair was found. Saved results were left intact.")
        digest = next(tag["digest"] for tag in local_api("tags")["models"] if tag["name"] == MODEL)
        record = {
            "source": "https://svs.gsfc.nasa.gov/11318/", "sourceSha256": SHA256,
            "model": MODEL, "modelDigest": digest, "ollamaVersion": local_api("version")["version"],
            "sampleIntervalSeconds": 1, "rimVisible": visible, **result,
        }
        for label, index in (("before", before), ("after", after)):
            frames[index].save(stage / f"flex-{label}.jpg", quality=92)
        (stage / "flex-analysis.js").write_text(
            "window.FLEX_FILM_ANALYSIS = " + json.dumps(record, indent=2) + ";\n", encoding="utf-8", newline="\n",
        )
        archive.replace(INPUTS)
        for file in stage.iterdir():
            file.replace(MEDIA / file.name)
    print(f"{MODEL} selected {before}s and {after}s. Inspect these frames against the clip before publishing.")


if __name__ == "__main__":
    main()
