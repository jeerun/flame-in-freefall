import base64
import hashlib
import json
from pathlib import Path
import unittest

from server import film_review


MEDIA = Path(__file__).resolve().parents[1] / "console" / "lab-media"


class FilmReviewTests(unittest.TestCase):
    def test_bundled_frames_and_clip_match_the_saved_analysis(self):
        text = (MEDIA / "flex-analysis.js").read_text(encoding="utf-8").strip()
        record = json.loads(text.removeprefix("window.FLEX_FILM_ANALYSIS = ").removesuffix(";"))
        self.assertEqual(record["sourceSha256"], hashlib.sha256((MEDIA / "flex-iss.webm").read_bytes()).hexdigest())
        responses = iter(record["rimVisible"])
        received = []

        def ollama(path, payload):
            self.assertEqual(path, "chat")
            self.assertEqual(payload["model"], record["model"])
            jpeg = base64.b64decode(payload["messages"][0]["images"][0], validate=True)
            self.assertTrue(jpeg.startswith(b"\xff\xd8"))
            received.append(jpeg)
            return {"message": {"content": json.dumps({"rim_visible": next(responses)})}}

        selected = film_review.review_clip(record["model"], ollama)
        self.assertEqual(selected, film_review.validate_pair(record))
        self.assertEqual(len(received), film_review.SAMPLE_COUNT)
        for label in ("before", "after"):
            self.assertTrue((MEDIA / f"flex-{label}.jpg").read_bytes().startswith(b"\xff\xd8"))

    def test_ambiguous_and_flickering_visibility_abstain(self):
        for readings in ([True, False], [False] * 24, [True, True, False, False] * 2):
            self.assertEqual(film_review.candidate_pair(readings), {"before": None, "after": None})

    def test_single_sustained_change(self):
        self.assertEqual(film_review.candidate_pair([False, True, True, False, False]), {"before": 2, "after": 3})

    def test_peer_pair_validation(self):
        self.assertEqual(film_review.validate_pair({"before": None, "after": None}), {"before": None, "after": None})
        for pair in (None, {}, {"before": True, "after": 2}, {"before": 5, "after": 22},
                     {"before": None, "after": 5}, {"before": 22, "after": 23}):
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                film_review.validate_pair(pair)


if __name__ == "__main__":
    unittest.main()
