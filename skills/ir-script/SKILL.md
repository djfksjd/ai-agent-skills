---
name: ir-script
description: Research Korean and international IR examples, then create evidence-backed investor pitch decks, synchronized speaker scripts and Q&A. Use for IR 자료, 투자제안서, 발표대본, demo-day pitches, fundraising decks and earnings presentations. Not for stock recommendations or generic document summaries.
license: MIT; see LICENSE for scope
metadata:
  display-name: IR & SCRIPT
  version: "1.0.0"
---

# IR & SCRIPT

Create the deck and its spoken story as one versioned deliverable. Use the user's language. This is an agent workflow: the host supplies web, document and execution tools. The bundled Python code is an offline baseline, not an autonomous research service.

## Load progressively

- Research and reference access: `references/research.md`.
- Story, style, business checks: `references/story-and-copy.md`.
- Baseline contract: `templates/deck.example.json` and `README.md`.
- Reusable local state: `templates/project-state.md`.
- Final review: `templates/release-checklist.md`.

## 1. Restore the actual project

Read the supplied source files and relevant connected resources before drafting. Treat them as the requested basis, preserving terminology and decisions. Distinguish source-derived content, new external research, inference and your proposed changes. Do not replace unseen user content with general advice.

Record input filenames, hashes, dates, actual slide counts, main/appendix boundary, script headings and read scope in a LOCAL project-state file. Compare slide and script order, not just filenames. When versions conflict, report the mismatch; preserve both. Ask a focused question if choosing one would discard or alter a substantive decision. Otherwise propose a mapping as a clearly labeled draft. Do not pretend to have read hidden memory, local disks or Cowork sessions.

Before creating files, read the host's installed presentation/PDF/document guidance. Do not publish user inputs or local project-state to a public repository.

## 2. Define the presentation contract

Establish audience, company stage, goal, language, talk duration excluding Q&A, live versus send-ahead delivery and requested formats. Distinguish fundraising, competition scoring, pilot recruitment and public-company earnings. Preserve an actual judging rubric when provided. Do not invent a round size, valuation, customers, credentials, quotes, founder anecdotes or traction. Leave missing essentials explicitly unresolved.

Coverage: why the founder started; the customer's current workflow and documented problem; alternatives; mechanism and product journey; buyer and market denominator; business model and costs; acquisition and retention; traction and development status; team; milestones and ask. These are coverage questions, not a fixed slide order.

## 3. Research examples and the business

Start with the user's references, then search current primary sources. Select comparable Korean and international cases by stage, audience and business model, not nationality alone. Use actual company decks, founder retrospectives, official event videos/transcripts and investor guidance. Separate earnings calls from early-stage pitches.

For each source record publisher, original date, retrieval date, URL, country, stage, audience, medium, access level, observed pages/sections/timestamps, useful pattern and limits. Record search queries and failed access. A source list is not an analysis: explain what was observed, why it helps this project, what should not be copied, and the proposed adaptation.

Video access: `video_and_transcript`, `transcript_only`, `selected_frames`, `metadata_only`, `unavailable`. Use official captions or user-authorized transcripts; label machine transcripts and check numbers against visuals. A title or third-party summary cannot establish chronology, tone, slides, metrics or exact words. Never invent timestamps or bypass access controls. For compilation videos, identify company boundaries only when observed. Continue useful work from accessible primary material and disclose any video gap.

Inspect PDF page images when interpreting tables, charts or design. Keep short original notes and links, not complete copyrighted decks/transcripts. References in this package are research seeds with dated access, not an evergreen factual database.

## 4. Build an evidence ledger

Give every substantive claim a stable ID and status: `verified`, `user_provided`, `hypothesis`, `target`, `calculation`, `unverified`. Link sources and exact locators. Vendor marketing verifies what a vendor advertises, not independent performance. Partial access supports only the observed passage. Recheck prices, plan policies, market figures and live product functions when used.

Verify problems through distinct layers: founder motivation, official workflow, customer interviews and measured cost. Compare competitors on the same task, output, seats, period, tax basis and usage scope. 'Not confirmed in reviewed sources' is not 'absent'. State superiority only with a fair test. Do not remove a competitor's recommendation function to claim it only writes documents.

Use relevant unique buyers, willingness to pay and paid months for market size. Government budgets, GMV and industry turnover are not software revenue. Unsupported denominators belong in a labeled scenario, not a claimed TAM. Separate tax-inclusive billings, net revenue, monthly/annualized run-rate and cumulative revenue. Show acquisition timing, retention, inference/support/fees and founder/team costs. Recompute formulas with code; the financial helper is a limited scenario model, not accounting advice.

Preserve the user's AI connection model: official CLI subscription is not BYOK. Recheck provider authentication, commercial integration and data rules. Local invocation does not prove permission. Separate workflow fee, external AI plan and managed inference. Local storage does not imply offline processing or zero outbound data. Code existence, implementation, tested deployment, stars, installs and paid customers are different evidence levels.

Keep essential qualifiers next to claims. Put short source/status labels on slides and full references in notes plus the shared PDF's reference appendix. Do not bury material caveats. Do not make the whole main deck sound like an audit report.

## 5. Choose a story and synchronize it

Write a one-sentence product definition and three takeaways. Compare two plausible orders, select one with a project-specific reason, then create a storyboard. Consider problem-led, product-led or traction-led order; do not imply a universal winning sequence. Use the actual rubric when required.

Each slide has stable ID, main/appendix kind, audience question or role, concrete title, one takeaway, claims, visual plan, planned seconds, spoken text, cue and transition. Main slides carry the case. Detailed calculations, legal/provider conditions, full competitor tables and methodology generally belong in appendices unless essential to the central claim. No unsupported investment ask.

Keep final copy, order, scripts and Q&A in canonical `deck.json`. Main and appendix slides must have distinct IDs. Q&A points to real appendix IDs. After edits, regenerate all exports; do not silently pair an old script with a revised deck. Rich host renderers may extend this data model, but must retain IDs and verify synchronization.

## 6. Edit the slide and spoken layers separately

Headlines: short concrete phrases or deliberate short assertions. For Korean, review repeated '~합니다/~됩니다/~했습니다', editorial narration ('자료를 정리했습니다'), empty superlatives and repetitive '~가 아닌' contrasts. This is a style preference, not proof of AI authorship. Do not mechanically turn every sentence into awkward nouns. Keep informative existing titles.

Body: a visible point needs a purpose and evidence, not a paragraph copied from the business plan. Script: natural spoken language with short sentences; polite Korean is appropriate here. Explain the evidence, connect slides and pause; do not read every bullet. Keep spoken words, stage cues, transitions and verification notes separate.

Estimate time with an explicit adjustable rate and demo/pause allowance. A word-count calculation is not rehearsal. Provide shorter variants when requested without changing facts. Prepare Q&A on buyer, alternatives, moat, market, retention, costs, team, data, milestones and ask; answer missing-data questions honestly.

## 7. Build, render and test

Prefer the host's capable editable slide engine and preserve user branding/templates. Use product evidence, diagrams and charts where informative; label mockups. Avoid identical card walls, decorative 3D, tiny caveats, broken Korean glyphs, ornamental 'AI' visuals and made-up screenshots. Do not force 3D onto software IR.

Fallback commands (run from this skill folder):

```bash
python scripts/pipeline.py lint deck.json --strict-style
python scripts/pipeline.py build deck.json --out /path/to/new-release --pdf --strict-style
python scripts/pipeline.py verify /path/to/new-release
```

The baseline emits editable PPTX, DOCX speaker script, Markdown script/Q&A, claim CSV, canonical JSON, QA report and checksummed manifest. PDF requires separately installed LibreOffice. It supports cover/columns/process layouts and small copy budgets; use a richer host engine for charts, real screenshots and complex tables. Do not degrade a good deck to fit the fallback.

Fix lint failures; do not simply disable guards. Render every slide and script page, inspect all at useful size, correct clipping/overlap/contrast/labels/flow and rerender. Automated validation is not fact checking, visual QA or rehearsal. Do not report an unexecuted test as passed. Missing conversion/render tools must be disclosed.

`check-sync deck.json extracted-script-manifest.json` compares IDs, kinds, titles and order. For existing PDFs/scripts, first extract their actual headings; do not infer a mapping from similar filenames. Hash validation detects changes, not malicious tampering or source truth. A manual PowerPoint edit requires reconciliation and a new release.

## 8. Handoff

Deliver requested PPTX/PDF, script DOCX/PDF/Markdown, Q&A, research and structure rationale, sources and QA status. State what is missing. Persist local state after research, storyboard and release: decisions, source IDs, unresolved claims, canonical version, tests, next action. This is local continuity, not an account-memory update.

Do not upload user/company documents, credentials or third-party media without explicit publication scope. Publishing this skill to GitHub, installing on a local machine, and enabling in ChatGPT/Cowork/cloud sessions are separate operations. Report only the operations actually completed.
