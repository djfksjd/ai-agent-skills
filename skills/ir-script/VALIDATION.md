# Validation record — IR & SCRIPT 1.0.0

Tested 2026-09-28 in a Linux working container.

- Python: 3.13.5
- python-pptx: 1.0.2
- python-docx: 1.2.0
- PDF converter: LibreOffice 25.2.3.2 520(Build:2)
- Font used for the synthetic rendering test: installed NanumSquare; no font files distributed.

## Completed

31 unittest cases passed: valid/malformed inputs, duplicate IDs, unknown claims/sources, missing evidence and locators, metadata-only verification rejection, headline style exception, excessive copy, timing limits, slide order, appendix references, JSON nonfinite values, artifact generation and read-back, hash tampering, manifest paths, revenue/run-rate separation, annual allocation, negative costs, nonpositive contribution and safe local installation.

Synthetic end-to-end build: 3 main slides + 1 appendix; PPTX, DOCX, Markdown script, Markdown Q&A, claims CSV, canonical JSON, QA report and manifest generated. LibreOffice converted both PPTX and DOCX to PDF. Verify checked 9 output file hashes and matching PPTX note IDs / DOCX headings. Deck PDF had 4 pages; script PDF had 4 pages.

Visual review: all 4 deck pages and all 4 script pages rendered and inspected. The synthetic example showed readable Korean glyphs and no observed text clipping or overlaps. This applies only to this fixture and environment, not arbitrary content or every PowerPoint installation. The per-project automated report remains visual_review=pending until that project's actual pages are inspected.

Timing is an adjustable estimate, not a recorded rehearsal. The example is a compiler smoke test, not a complete investment deck.

## Not tested or claimed

No live Codex, Claude Code or Cowork account installation/execution; no account registration. No new customer interviews, competitor product trials, investment success, factual validation of future user input, Windows/macOS Office rendering, complete video playback or transcription of the two requested YouTube videos. No paid AI calls or private input publication. The installer was tested only in a temporary local folder.

Re-run `python -m unittest discover -s tests -v` and `python scripts/pipeline.py verify OUTPUT` after changes. Run a fresh visual review for every real deck and script. A file hash is not a signature or an audit guarantee.
