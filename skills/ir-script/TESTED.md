# Test record — 1.0.0

Date: 2026-09-28. This records observed tests, not a certification.

## Environment

Linux container; Python 3.13.5; python-pptx 1.0.2; python-docx 1.2.0; LibreOffice 25.2.3.2. NanumGothic was installed in this environment, but no font files are shipped.

## Completed

- `python -m unittest discover -s tests -v`: **22 tests passed**.
- Strict lint on `templates/deck.example.json`: no errors or warnings.
- Generated editable PPTX (4 slides), script DOCX, Markdown script and Q&A, claim CSV, canonical JSON and release manifest.
- Converted both Office files to PDF: **deck 4 pages; speaker script 5 pages**.
- Rendered the four slides and all five script pages and visually inspected them for clipping, missing Korean glyphs, overlap and page breaks. The synthetic example was clean in the tested renderer.
- Ran `verify`: matching output hashes, slide count, PPTX titles/notes and DOCX heading order.
- Tested deliberate output modification, duplicate slide IDs, unknown claims, invalid claim verification, missing calculation assumptions, metadata-only evidence, incorrect appendix references, over-budget time, non-finite input and unsafe manifest paths.
- Tested preservation of pre-existing output directories and no-overwrite installation to a temporary custom skills directory.
- Financial fixture: cumulative net revenue 4,950,000.00; ending-month annualized net revenue 10,800,000.00; single-plan break-even 67 under the explicitly synthetic assumptions.

## Not tested / not implied

No execution inside the user's actual Codex, Claude Code, ChatGPT or Cowork account. No Windows/macOS native PowerPoint or Keynote round-trip. No promise that arbitrary-length user copy fits the baseline layout; every real output requires rendering and inspection. No live research-agent benchmark, factual verification of generated company claims, customer interviews, competitor performance tests or investor-success outcome.

The two supplied YouTube references were metadata-only in this research pass. The generic compiler reports visual review as pending by default: inspecting this sample does not inspect future decks. The financial helper is a scenario tool, not a cash-flow or tax/accounting system.

## Reproduction

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/pipeline.py lint templates/deck.example.json --strict-style
python scripts/pipeline.py build templates/deck.example.json --out /tmp/ir-script-example-new --pdf --strict-style
python scripts/pipeline.py verify /tmp/ir-script-example-new
python scripts/financials.py templates/financial.example.json
```

Use a fresh output path. LibreOffice is required for `--pdf`. Fonts are the caller's responsibility. No private company examples or input documents are included in the repository.
