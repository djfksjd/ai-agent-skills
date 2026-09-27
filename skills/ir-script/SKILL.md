---
name: ir-script
description: Research Korean and international IR examples, then create or revise evidence-backed investor decks, synchronized speaker scripts and Q&A. Use for IR, pitch decks, demo days, investor presentations, earnings presentations, IR 발표자료 and 발표대본; not for investment recommendations or generic document summaries.
license: MIT (newly authored skill files only; see LICENSE)
metadata:
  display-name: IR & SCRIPT
  version: "1.0.0"
---

# IR & SCRIPT

Create the slides and spoken story as one versioned product. Use the user's language. Instructions are English; Korean examples illustrate editorial preferences.

Read `references/research.md` for sources and access limits; `references/story-and-copy.md` for narrative, research coverage, copy and delivery; `README.md` for installation and commands. Read only the parts needed. Use the host's installed presentation/PDF/document instructions before artifact work.

## 1. Recover the actual project

Read supplied files and relevant authorized connected sources, not only assistant summaries or memory. Record input filenames, hashes, dates, actual main/appendix counts and script headings in a local `project-state.md` based on `templates/project-state.md`. Preserve the user's terms and decisions. Distinguish user sources, outside research and your proposals.

Compare versions before pairing a deck and script. Matching filenames do not prove synchronization. Record count, order, title and appendix-boundary mismatches. Keep originals. Propose a canonical version and mapping; ask before a material change would discard source content or alter user decisions. Do not claim access to missing chats, local files, remote history or Cowork memory.

## 2. Define the presentation contract

Identify company stage, audience, objective, language, live versus send-ahead format, speaking time excluding Q&A, output formats and next decision/ask. Investor fundraising, startup competitions, pilot recruitment and listed-company earnings need different narratives. Do not invent a funding amount, team credential, founder anecdote, customer or test result. Mark unspecified inputs rather than fabricate them.

For a full IR, cover founder reason, problem evidence, current alternatives, solution mechanism, product use, first buyer, market denominator, revenue model, economics, acquisition, traction, execution, team and ask. Coverage does not mandate one slide per topic or a rigid order.

## 3. Research Korean and international references

Start with supplied references, then inspect relevant primary sources: actual company decks, official event videos, founder retrospectives, investor guidance and official transcripts. Match stage, audience and business model before geography. Use current official sources for volatile facts. Record queries and access failures; do not pad a reference quota with irrelevant links.

For each source record URL, publisher, publication/retrieval dates, country, stage, audience, medium, access, observed pages/sections/timestamps, actual sequence, usable pattern and limits. Separate observed source order from your proposed deck order. A company article about a deck does not establish every slide's sequence. Read page images for visual layout, tables and charts.

Video access states: `video_and_transcript`, `transcript_only`, `selected_frames`, `metadata_only`, `unavailable`. Prefer official captions or user-authorized transcripts; mark automatic transcription and cross-check numbers with slides. A title or third-party AI summary is not full viewing. Never invent timecodes, speaker quotations, metrics or segment boundaries. Do not bypass authentication, payment, CAPTCHA or access controls. When access fails, report it and use other inspected primary sources without pretending to analyze the inaccessible talk.

Store original analytical notes and links, not complete third-party decks or transcripts. Reference seeds are historical observations, not evergreen verification of current facts.

## 4. Research the business and audit claims

Create stable claim IDs and a source ledger. Status: `verified`, `user_provided`, `hypothesis`, `target`, `calculation`, `unverified`. Verification requires actual inspected support and exact locators. Marketing copy establishes what a vendor advertises, not independent performance. Preserve historical metric dates.

Problem: distinguish founder motivation, documented workflow, customer interviews and measured cost. Do not invent time saved or turn an anecdote into a market fact.

Competition: compare direct alternatives, manual work and relevant general tools on the same task, plan, period, tax/seat basis and output scope. Use 'not confirmed in reviewed material' rather than 'absent'. Never suppress a competitor's existing recommendation feature to create a writing-only straw man. Superiority needs a comparable test.

Market: estimate unique relevant buyers, willingness to pay and paid periods. Support TAM/SAM/SOM denominators or show a labeled scenario. Government grants, GMV and industry budgets are not software revenue. Avoid double counting and arbitrary '1% share'.

Business model: separate workflow subscription, personal third-party AI subscription, managed inference, onboarding and institutional support. Do not silently substitute BYOK API keys for the user's official CLI subscription connection. Recheck provider authentication, commercial integration and data conditions. Local invocation alone does not establish permission.

Financials: separate VAT-inclusive billings, net revenue, cash receipts, MRR/annualized run-rate and cumulative revenue. Include cohort timing, churn, AI costs, fees, acquisition, support and founder/team compensation. Recalculate; do not manufacture precision. `scripts/financials.py` is a limited monthly-recognition scenario helper, not a full cash-flow or accounting model.

Product: local storage does not mean offline inference or zero outbound data. Separate implemented, tested, deployed and planned. Source code, stars, downloads, active users, customers and renewals are distinct evidence.

Keep essential uncertainty next to the claim, with full references in notes/appendix. Do not fill the main presentation with internal audit commentary or remove material caveats for persuasion.

## 5. Build a story before slides

Write a plain product definition and three takeaways. Consider two plausible orders, select one based on evidence/audience, and explain the choice in a structure report. Use conditional recipes in `references/story-and-copy.md`; follow a supplied evaluation rubric where applicable.

Storyboard each slide with stable ID, main/appendix kind, audience question, role, title, one takeaway, supporting claim IDs, visual specification, planned seconds, spoken text, cue and transition. Main slides carry the business case. Put detailed methods, evidence tables and sensitivities in the appendix unless needed to understand a material central constraint. Do not pad with generic 'Executive Summary / Problem / Solution' placeholders.

## 6. Write slide copy and spoken copy differently

Visible Korean headings should normally be concrete short phrases or meaningful short claims. Audit every title, subtitle, table, caption and note. Remove repetitive '~합니다/~됩니다/~했습니다', author narration ('구분했습니다'), empty superlatives and repetitive '~가 아닌'. This is an editorial choice, not AI-authorship detection. Allow an intentional sentence with a recorded reason; do not replace precise claims with vague nouns.

Speaker text should be complete, conversational and naturally polite, not a list of slide fragments. Explain evidence rather than reading all bullets. Separate words to say from cues, transitions, sources and non-spoken qualifications. Include pauses and demos. Timing is an adjustable estimate until an actual rehearsal. A short-script variant must retain the same fact limits.

Prepare Q&A with a direct answer, supporting claims, actual appendix ID and unresolved issue. Cover customer, alternatives, market assumptions, defensibility, retention, costs, data, execution, team and ask. Never bluff missing evidence.

## 7. Generate and verify one canonical release

Use `deck.json` as the single source of slide IDs/order/copy/script/Q&A. Prefer the host's specialized artifact engine for rich editable visuals while preserving these IDs. Label mockups, never fabricate screenshots; use 3D only where it explains a product. Respect supplied branding and avoid identical card layouts throughout.

The bundled Python compiler is an **offline baseline**, not a web-research agent, advanced visualization tool or API wrapper. It produces editable PPTX, script DOCX/Markdown, Q&A Markdown, claim CSV, QA report and hash manifest; optional PDF conversion requires installed LibreOffice. It performs no paid AI calls or credential handling.

Run `python scripts/pipeline.py lint deck.json --strict-style`, then `build`. The baseline rejects copy too dense for its layout; shorten it or use a custom renderer rather than disabling validation. Render and inspect **every** slide and script page with host tools. Check Korean glyphs, clipping, overlap, scales, contrast, source labels, pagination and main/appendix order. Automated lint is not fact verification, visual inspection or rehearsal. When rendering is unavailable, state the gap, not 'visually checked'.

Run `verify` after generation. After manual PPT/DOCX edits, reconcile back into canonical JSON and rebuild. Use `check-sync` against extracted script IDs/kinds/titles when comparing old versions. A manifest detects consistency changes, not tamper-proof authenticity.

## 8. Deliver and persist honestly

Deliver requested files, research/structure rationale, Q&A, claim sources and a QA report naming tests actually run and missing checks. Persist local project state after each stage: inputs, decisions, sources, outstanding questions and next action. Do not claim durable account memory was updated.

Never publish private originals, customer data, credentials, generated company decks, third-party full media or font files without explicit scope approval. Keep only synthetic examples in a public skill repository. GitHub publication, local installation and ChatGPT/Cowork account registration are separate operations. Report only completed actions.
