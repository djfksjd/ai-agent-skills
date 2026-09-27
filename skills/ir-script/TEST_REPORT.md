# IR & SCRIPT 1.0.0 — test report

Release date: 2026-09-28. This reports implementation checks, not investment outcomes.

## Executed

- `python -m unittest discover -s tests -v`: **22 tests passed**.
- Strict headline/structural lint of the fictional example: no errors, no warnings.
- Generated editable PPTX (4 slides), DOCX (4 rendered pages), Markdown script/Q&A, claim CSV, canonical JSON, QA report and manifest.
- Generated deck PDF and script PDF with installed LibreOffice.
- Parsed generated PPTX slide identities and DOCX/Markdown headings; ID/order matching passed.
- Deliberate script-file modification detected by manifest verification.
- Duplicate IDs, main-after-appendix, unknown evidence, metadata-only video evidence, missing calculation method, mismatched script titles/kinds/order, duration overrun, nonexistent Q&A appendix, missing PDF tool and existing output/install destination checked.
- Finance checks: monthly versus cumulative versus annualized revenue, zero contribution, negative customers, unequal month-series and zero price period.
- Local installer exercised in a disposable directory; existing destination preserved.
- Rendered all 4 deck pages and all 4 script pages. Visually inspected those 8 images for Korean glyphs, wrapping and clipping; no observed clipping in the synthetic sample.

Environment: Python libraries python-pptx 1.0.2 and python-docx 1.2.0; Linux/LibreOffice; locally installed Noto Sans CJK KR. No font binary included.

## Not established

- Native PowerPoint on Windows/macOS rendering parity; actual Codex/Claude/Cowork account installation and end-to-end agent execution.
- Accuracy of arbitrary future input claims; automatic research from the Python code (it has no search/API calls).
- Full viewing/transcripts of the two user-selected YouTube videos; every page of embedded third-party decks.
- Complex charts, motion/3D design, private company performance, actual customer interviews, legal compliance of individual provider integrations, or measured speaker pacing.

The example is deliberately synthetic and short. The general workflow still requires company-specific research and visual inspection on every real release. A passing automated report is not a fact-check certificate. The generated report's `visual_review` remains pending by default so future users must perform their own check.
