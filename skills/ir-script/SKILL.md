---
name: ir-script
description: Research Korean and international IR examples, then create evidence-backed investor decks, synchronized speaker scripts and Q&A. Use for IR, pitch decks, demo days, investor presentations, earnings presentations, IR 발표자료 and 발표대본; not for investment recommendations or generic summaries.
metadata:
  display-name: IR & SCRIPT
  version: "1.0.0"
---

# IR & SCRIPT

Create the presentation and the spoken story as one versioned product. Use the user's language. Instructions are English; Korean examples demonstrate the requested writing style.

## Progressive reading

Read `references/research.md` for research and source access. Read `references/story-and-copy.md` for structure, competition, market, design and script writing. Read `README.md` for installation and deterministic compiler commands. The Python compiler is an offline baseline, not a browsing or AI service.

## 1. Restore context

Read actual attachments and relevant connected resources, not just past assistant summaries. Record files, hashes, dates, actual slide counts, main/appendix boundaries and script headings in a local `project-state.md` using its template. Preserve user terminology, framing and decisions. Separate user evidence, outside research, your inference and proposed changes.

Compare versions. A script declaring 13 main slides and 8 appendices is not synchronized with a PDF containing 14 main slides and 10 appendices. Never silently pair them. Explain discrepancies and propose a canonical mapping. Ask only when a decision would discard content or change substantive user decisions. Otherwise preserve both inputs and continue a labeled draft. Read the host's installed slides/PDF/DOCX instructions before artifacts. Never claim hidden memory, Cowork history or local computer access not actually obtained.

## 2. Establish the contract

Identify audience, purpose (fundraising, competition, pilot recruitment or public-company earnings), stage, language, talk time excluding Q&A, live versus send-ahead deck, requested formats and ask. Do not invent a round size, valuation, customers, interviews, team credentials, founder anecdotes or metrics. Unknown facts may stay unresolved.

Cover founder origin, customer workflow and evidence, alternatives, solution mechanism, product use, initial buyer, market denominator, pricing and costs, acquisition, traction, execution risks, team and ask. These are coverage checks, not a compulsory slide order. Respect a supplied judging rubric.

## 3. Research relevant cases

Start with the supplied references, then research Korean and international primary sources. Prefer official company decks and transcripts, founder explanations, official event videos and investor guidance. Match audience and stage before geography. Do not force earnings-call structure onto a pre-seed pitch.

For each reference log URL, publisher, original and retrieval dates, country, stage, audience, medium, access, observed pages/sections/timestamps, useful pattern and limitations. Keep the source's observed sequence separate from your proposed sequence. Read PDF page images for charts or layout. Segment compilation videos by company only when actual boundaries were observed.

Video access states: `video_and_transcript`, `transcript_only`, `selected_frames`, `metadata_only`, `unavailable`. Titles or third-party AI summaries do not establish talk sequence, metrics or wording. Use official captions or authorized supplied transcripts. Mark machine transcripts and check numbers against slides. Never invent timecodes or bypass access controls. When a video cannot be read, report this and continue from other inspected primary sources. Do not confuse that fallback with analysis of the requested video.

Use a varied relevant set, not a quota of weak examples. Keep a search log. Save your concise analysis and links, not complete copyrighted decks/transcripts. Research seeds are not an evergreen fact database.

## 4. Build the evidence ledger

Use stable claim IDs and statuses: `verified`, `user_provided`, `hypothesis`, `target`, `calculation`, `unverified`. Attach source IDs and precise locators. A vendor claim verifies its advertised offering, not independent performance. Date historical metrics and preserve the scope actually read.

- Problem: distinguish founder motivation, documented workflow, interviewed pain and measured cost. Never fabricate an anecdote.
- Competition: compare the same task, output, seats, price period and tax basis. Include manual/generic alternatives. Say 'not confirmed in reviewed sources', not 'absent'. Do not turn a competitor offering recommendations and writing into a writing-only straw man. Superiority needs comparable tests.
- Market: count unique relevant buyers, paid conversion and actual paid months. Support TAM/SAM/SOM denominators or show a labeled scenario. Grants, GMV and public budgets are not software revenue. Arbitrary 1% share is not a demand argument.
- BM: separate workflow subscription, user-owned AI subscription, managed inference and implementation/support. Do not rename a requested official CLI subscription connection as BYOK. Recheck each provider's official commercial, authentication and data rules. Local CLI execution does not itself prove permission.
- Finance: separate tax-inclusive billings, net revenue, cash, annualized run-rate and cumulative revenue. Include timing, churn, inference, support, fees and founder/team compensation or state exclusions. Calculate in code, disclose assumptions. `scripts/financials.py` is a narrow monthly-recognition helper, not an accounting system.
- Product: distinguish implemented, tested, deployed and planned. Local storage is not offline inference. Code, stars, downloads, active users and paying customers are different evidence levels.

Show compact status/source markers on relevant slides and full sources in notes/appendix. Material qualifiers stay next to the claim. Do not inflate claims, but do not fill a pitch with editing/audit commentary either.

## 5. Select and storyboard the narrative

Write a precise product definition and three takeaways. Propose two plausible orders; choose based on the audience and available evidence. Use problem-led, product-led or traction-led structures as appropriate. A rubric overrides a generic recipe.

Each storyboard row needs stable slide ID, main/appendix kind, audience question, concrete title, one takeaway, supporting claims, visual specification, allocated seconds, spoken text, cue and transition. Main slides carry the investment/pilot case. Detailed methodologies, sensitivity analyses and provider constraints usually belong in the appendix unless central to understanding the offer.

Avoid filling mandatory 'Executive Summary / Problem / Solution' slots with generic text. Choose slide count from the story and talk duration, not an arbitrary template.

## 6. Write slide copy and speech separately

For Korean titles prefer short noun phrases or meaningful concise claims. Remove repeated '~합니다/~됩니다/~했습니다', editing narration ('구분했습니다'), unsupported '혁신적/압도적/완벽한', and repetitive '~가 아닌' contrasts. This is an editorial preference, not an AI detector. Preserve meaning; a deliberate complete headline can be allowed.

Speaker text should sound natural, using complete sentences and appropriate polite speech, not slide fragments. Explain evidence and connect pages without reading every bullet. Keep `speaker_text`, `cue` and `transition` separate. Include pauses and demo time. Label rate-based estimates; do not call them actual rehearsals. Shorter variants retain the same factual limits.

Q&A includes a direct answer, supporting claims, linked appendix IDs and uncertainty. Cover buyer, alternatives, market assumptions, defensibility, retention, economics, data, execution and ask. Do not bluff.

## 7. Generate and validate

Keep `deck.json` as the single source of truth for slide IDs, order, copy, script and Q&A. Prefer the host's capable artifact engine for designed editable slides. Preserve user branding/templates. Prefer real product evidence, diagrams and readable charts over identical cards. Label mockups. Use 3D only when it explains a physical product.

The bundled Python compiler produces editable baseline PPTX, script DOCX/Markdown, Q&A Markdown, claims CSV, manifest and optional PDFs. It performs no web research, paid inference, credential handling or automatic downloads. PDF conversion requires installed LibreOffice; fonts are local, not bundled.

Run `python scripts/pipeline.py lint deck.json --strict-style`, then build. Resolve errors rather than disabling checks. Render every slide and script page and inspect overlap, clipping, Korean glyphs, chart scales, contrast, density, footnotes and page breaks. If rendering is unavailable, report missing visual QA. Automated checks are not factual or visual verification.

Run `verify` after edits. Manual output changes require reconciliation into canonical JSON and a new build. Inspect script/slide ID mapping, not just file counts. Report tests actually performed, untested platforms and unresolved facts. Keep a manifest so versions are not mixed.

## 8. Handoff and persistence

Deliver requested PPTX/PDF, script DOCX/PDF/Markdown, research/structure rationale, Q&A, sources and QA report. Explicitly identify missing formats.

Update local project state after each major step: input versions, decisions, source IDs, unresolved questions and next action. Never claim account memory was updated. Do not upload private originals, customer data, credentials, third-party media or generated client decks to public repositories without explicit scope permission. GitHub publication, local installation and account/Cowork registration are different operations; report only completed actions.
