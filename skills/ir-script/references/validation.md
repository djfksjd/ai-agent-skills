# Validation record — 1.0.0

Executed 2026-09-28 in the authoring Linux container. These results do not certify arbitrary future decks, research quality or a user's installed runtime.

| Check | Actual result |
|---|---|
| Python unittest suite | 24 tests passed |
| Strict-style lint of synthetic example | Passed, no warnings |
| PPTX / DOCX / Markdown generation | Passed |
| Deck/script ID, order and title checks | Passed |
| Changed output detection | Test passed; edited Markdown rejected |
| Missing/metadata-only evidence | Tests passed; cannot be tagged verified |
| Main/appendix boundary and Q&A reference checks | Tests passed |
| Financial scenario | Net cumulative revenue 300000; ending annualized revenue 2400000; distinct by construction |
| LibreOffice conversion | Deck PDF 4 pages; script PDF 4 pages |
| Visual review of synthetic exports | All 4 slide pages and 4 script pages rendered and inspected; no observed clipping/missing Korean glyphs in this fixture |
| Installer copy | Copied to a temporary test root, not user's home or cloud account |

Commands: the README lint/build/verify/financial commands and `python -m unittest discover -s tests -v`.

Not tested: actual Codex/Claude agent invocation, account/Cowork installation, Windows/macOS Office rendering, arbitrary long content, provider authorization, full video playback, live competitor workflows, customer interviews and investment outcomes. Timing is an adjustable text-length estimate, not measured delivery.

The automated QA JSON intentionally leaves visual review pending. This document records the separate review of the synthetic fixture only. Reinspect every new deck after generation. Dependencies are bounded compatibility ranges, not a bit-for-bit locked environment.
