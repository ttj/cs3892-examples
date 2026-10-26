# Part 5 — three properties, in English

Give an LLM these three sentences, the network's interface (inputs `X_0`..`X_195`, the 14×14
pixels, each in [0, 1]; outputs `Y_0`..`Y_9`, the logits) and the pixel values of the image each
one refers to (`load_images()` in `hw5lib.py`; image *i* is a digit *i*). Ask it for one VNN-LIB file
per property. Save its answers **verbatim** as `P5a_llm.vnnlib`, `P5b_llm.vnnlib`, `P5c_llm.vnnlib`, and
your own corrected versions as `P5a_fixed.vnnlib`, `P5b_fixed.vnnlib`, `P5c_fixed.vnnlib`. Record the
prompt you used in `prompt.md`.

- **P5a.** Image 2 is classified as a 2 for every input within L∞ distance 0.02 of it, with
  pixel values kept in [0, 1].
- **P5b.** No input within L∞ distance 0.05 of image 3, with pixel values kept in [0, 1], makes
  class 8 the top class: no such input gives class 8 a logit at least as high as every other
  class's.
- **P5c.** For every input within L∞ distance 0.01 of image 1, with pixel values kept in [0, 1],
  the logit of class 1 exceeds every other class's logit by at least 2.

`python3 check_hw5.py` parses all six files. For each one it reports a syntax error, a
difference in meaning (with a concrete output vector on which the file and the intended property
disagree), or a match.
