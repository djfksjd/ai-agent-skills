---
name: ir-script
description: Research Korean and international IR examples, then create or revise evidence-backed investor pitch decks, synchronized speaker scripts and Q&A. Use for IR 발표자료, 발표대본, pitch decks, demo days and earnings presentations. Not for stock recommendations or generic summaries.
license: MIT
metadata:
  display-name: IR & SCRIPT
  version: "1.0.0"
---

# IR & SCRIPT

Create the slides and the spoken story as one versioned product. Respond in the user's language. Read only the references needed: `references/research.md` for sources and access limits, `references/story-and-copy.md` for composition, `README.md` for tools and schemas.

## 1. Recover the project

Read supplied documents, relevant connected files and their actual contents. Do not depend on earlier assistant summaries or claim access to unseen memory. Record filenames, hashes, dates, actual main/appendix counts, script headings and unresolved differences in a local copy of `templates/project-state.md`. Preserve the source's terminology, framing and decisions; separate additions from source-derived content.

A script with 13 main slides and 8 appendices is not synchronized with a PDF with 14 main slides and 10 appendices. Never silently pair them. Identify the canonical version or propose a mapping; ask one focused question only when a substantive choice cannot be resolved from materials. Otherwise continue a clearly labeled draft without destroying either input.

Before producing artifacts, read the host's installed presentation, PDF and document instructions. Prefer the user's actual assets and template. A README is not an execution test, and a filename is not evidence of contents.

## 2. Establish the presentation contract

Identify audience, purpose (fundraising, competition, pilot recruitment or earnings), stage, language, speaking time excluding Q&A, live vs send-ahead use, requested formats and decision/ask. Never invent a funding amount, valuation, biography, customer, interview or founder anecdote. Unknowns remain explicit.

Coverage checks: founder reason; customer problem and evidence; alternatives; solution mechanism; product use; initial buyer; market denominator; pricing and costs; acquisition; traction; execution risks; team; ask. These are not a mandatory slide order. Follow a supplied evaluation rubric.

## 3. Research examples and the actual business

Use supplied links first, then relevant Korean and international primary sources: company decks and founder explanations, official demo-day videos, official earnings slides/transcripts, investor guidance. Match stage and audience before country. Do not transplant an earnings-call sequence into a pre-seed pitch.

For each source record ID, URL, publisher, original date, retrieval date, country, stage, medium, access level, exact observed pages/sections/timestamps, useful pattern and limits. Distinguish the observed sequence from your proposed sequence. Use PDF page images to inspect tables/design.

Video access: `video_and_transcript`, `transcript_only`, `selected_frames`, `metadata_only`, `unavailable`. Titles and third-party AI summaries cannot establish chronology, numbers or wording. Prefer official captions or authorized supplied transcripts. Check machine-transcribed figures against slides. Never invent timestamps or bypass login, payment, CAPTCHA or other controls. If a video is inaccessible, report that and continue with inspected alternatives. Store short original analytical notes and links, not full copyrighted decks/transcripts.

Research founder context, actual customer workflows, current competitor offerings and prices, official market denominators, business-model constraints and relevant regulations. Old reference examples are structural inspiration, not current market facts. Search logs and access failures belong in the research report.

## 4. Maintain a claim ledger

Every substantive slide and script claim has a stable ID and one status: `verified`, `user_provided`, `hypothesis`, `target`, `calculation`, `unverified`. Link source IDs and exact locators. A vendor page verifies what it advertises, not independent effectiveness. Partial access supports only inspected passages. Keep historical metric dates.

- Problem: distinguish founder reason, documented workflow, interviews and measured cost. Do not invent time waste, failures or testimonials.
- Competition: compare the same job, pricing period, tax basis, seats and output scope; include manual work or generic tools when relevant. 'Not confirmed in reviewed sources' is not 'absent'. No false writing-only competitor when recommendations also exist. Superiority needs a comparable test.
- Market: unique relevant buyers × paid share × actual paid months × price, with justified denominators. Grants, GMV and government budgets are not software revenue. If the denominator is unknown, show a labeled scenario, not invented TAM/SAM/SOM or assumed 1% attainability.
- Business model: separate product subscription, individual AI subscription, managed inference, onboarding and institutional support. Do not silently change official CLI subscription connection into BYOK. Recheck each provider's authentication, commercial integration and data policies; local invocation does not establish permission or unlimited use.
- Finance: distinguish gross billing, tax-exclusive revenue, cash, MRR/annualized run-rate and cumulative revenue. Model acquisition timing, churn, support, inference, fees and compensation. Recalculate assumptions with code. `scripts/financials.py` is a narrow monthly-recognition scenario, not accounting advice.
- Product: local storage does not imply offline inference or zero transmission. Separate implemented, tested, deployed and planned. Stars, downloads, active users and paying customers are different evidence.

Put essential status qualifiers next to the claim and short source IDs on slides. Full evidence goes in notes/appendices. Do not bury a hypothetical result in a footnote or turn the main presentation into an audit report.

## 5. Design the narrative

Draft one concrete product definition and three takeaways. Propose two suitable orders, then choose one based on audience and available evidence. Use problem-, product- or traction-led organization conditionally, not a universal ten-slide formula. Consult `references/story-and-copy.md`.

Storyboard each slide: stable ID, main/appendix, audience question, short title, one takeaway, claim IDs, visual plan, planned seconds including pauses/demo, speaker text, cue and transition. Move detailed methods, provider restrictions and sensitivity analyses to appendices unless they materially change the core proposition.

## 6. Write visible copy and speech differently

Korean headlines default to concise noun phrases or specific short claims. Avoid repetitive '~합니다/~됩니다/~했습니다', editorial statements ('구분했습니다'), generic hype and habitual '~가 아닌' constructions. This is copy editing, not AI detection. Intentional complete-sentence titles are allowed when effective and documented.

Speaker scripts use natural spoken language and appropriate politeness. Explain and connect, do not merely read bullets. Keep spoken text, stage cues, transitions and evidence separate. Show timing assumptions and pauses; estimates are not rehearsals. A shorter version must preserve qualifiers and the same claims.

Q&A includes a direct answer, linked evidence, appendix ID and remaining uncertainty. Cover buyer, competitors, market assumptions, defensibility, retention, unit economics, data handling, execution and ask. Missing evidence requires an honest answer, not improvisation.

## 7. Generate, inspect and synchronize

Use `deck.json` as the canonical content source. A host-native slide engine can use the storyboard for richer editable layouts, diagrams, charts and real product screenshots. Label mockups. Avoid repetitive card walls, tiny type, stock decoration and irrelevant 3D. Do not fabricate screenshots or remove evidence to sound persuasive.

The bundled Python compiler is an offline baseline, not an autonomous search/LLM service or a high-end visual designer. It emits editable PPTX, script DOCX/Markdown, Q&A, claims CSV and a release manifest. PDF additionally requires installed LibreOffice. It makes no network or paid AI calls.

Run:
```
python scripts/pipeline.py lint deck.json --strict-style
python scripts/pipeline.py build deck.json --out NEW_OUTPUT_FOLDER --pdf --strict-style
python scripts/pipeline.py verify NEW_OUTPUT_FOLDER
```

Fix validation errors rather than disabling checks. Render every slide and script page with the host's tools. Inspect Korean glyphs, overflow, overlaps, chart axes, table density, source/status labels and page breaks. Record pages actually reviewed. The automated QA report deliberately starts with visual review pending; lint is not fact verification or visual QA.

After manual editing, reconcile changes into the canonical JSON and rebuild. `check-sync` compares separately extracted script headings with canonical slide IDs, order and main/appendix boundary. A hash manifest detects accidental divergence, not malicious tampering or legal audit integrity.

## 8. Deliver and preserve state

Deliver the requested PPTX/PDF, script DOCX/PDF/Markdown, Q&A, source/claim ledger, structure rationale and QA results. State any unproduced format or untested platform. Save local project state after each phase: versions, choices, sources, open questions and next action. This is not account-memory registration.

Never publish private inputs, customer data, credentials, user decks, full third-party media or font files without explicit authorization for that content. Repository publication, local installation and ChatGPT/Cowork account registration are separate actions. Report only completed ones.
