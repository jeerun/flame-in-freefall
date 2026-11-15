"""Classify the fixed FLEX clip samples with a local, image-capable Ollama model."""

import base64
import json
from pathlib import Path
from zipfile import ZipFile


INPUTS = Path(__file__).with_name("flex-vision-inputs.zip")
SAMPLE_COUNT = 24
PROMPT = ("Inspect the center of this frame from a NASA fuel-droplet experiment. "
          "Is there a large roughly spherical bubble-like shape with a continuous round outline, even if faint? "
          "Set rim_visible to true only for a continuous round outer boundary around the central point. "
          "A diffuse cloud, arc, or point alone does not count.")


def classify_samples(model, ollama, archive=INPUTS):
    schema = {"type": "object", "properties": {"rim_visible": {"type": "boolean"}},
              "required": ["rim_visible"]}
    visible = []
    with ZipFile(archive) as frames:
        for second in range(SAMPLE_COUNT):
            sample = base64.b64encode(frames.read(f"{second:02}.jpg")).decode("ascii")
            reply = ollama("chat", {
                "model": model, "stream": False, "think": False, "format": schema,
                "options": {"temperature": 0, "seed": 42, "num_predict": 40},
                "messages": [{"role": "user", "content": PROMPT, "images": [sample]}],
            })
            value = json.loads(reply["message"]["content"])["rim_visible"]
            if type(value) is not bool:
                raise ValueError("Invalid frame classification")
            visible.append(value)
    return visible


def candidate_pair(visible):
    # Require two consecutive positive samples followed by two negatives. Decline
    # ambiguous clips rather than choosing between multiple candidate events.
    transitions = [i for i in range(1, len(visible) - 2)
                   if visible[i - 1:i + 3] == [True, True, False, False]]
    if len(transitions) != 1:
        return {"before": None, "after": None}
    return {"before": transitions[0], "after": transitions[0] + 1}


def validate_pair(result):
    if not isinstance(result, dict) or "before" not in result or "after" not in result:
        raise ValueError("Missing frame-pair result")
    before, after = result["before"], result["after"]
    if before is None and after is None:
        return {"before": None, "after": None}
    if type(before) is not int or type(after) is not int or not 1 <= before <= SAMPLE_COUNT - 3 or after != before + 1:
        raise ValueError("Invalid clip-local sample indices")
    return {"before": before, "after": after}


def review_clip(model, ollama):
    """Return clip-local seconds or an abstention. No caller supplies images or file paths."""
    return candidate_pair(classify_samples(model, ollama))
