# Research notes and access ledger

Researched 2026-09-28. Short original analytical notes, not redistributed decks or transcripts. Entries are reference seeds; refresh when used for current facts. Company figures are deliberately not transplanted into templates. 'Observed' below is limited to the stated access; 'Application' is our synthesis, not the source's prescribed universal rule.

## Startup fundraising and presentation guidance

### R01 — YC / A Guide to Demo Day Presentations
- URL: https://www.ycombinator.com/blog/guide-to-demo-day-pitches
- Original: 2016-07-25. US accelerator guidance; text article, not one company pitch.
- Access: article text, sections Presentation Organization, Slides, Preparation and Common Errors.
- Observed: organization is flexible; product clarity, audience, bottom-up opportunity and practice are emphasized. It contrasts telling a story with simply narrating a slide stack.
- Application: choose sequence based on actual evidence; make a concise live talk and put detailed proof in backup material. Do not treat a generic outline or a word limit as a fixed law.

### R02 — YC / How to Design a Better Pitch Deck
- URL: https://www.ycombinator.com/blog/how-to-design-a-better-pitch-deck
- Original: 2015-11-15. US design guidance.
- Access: article text; not a frame-by-frame analysis of embedded media.
- Observed: legibility, simplicity and immediately understandable visual meaning are central.
- Application: design for the person listening in the room; separate the visible slide from what the presenter says. Sparse slides do not remove the need for complete evidence notes.

### R03 — Sequoia / Writing a Business Plan
- URL: https://sequoiacap.com/article/writing-a-business-plan/
- Original date: not confirmed in inspected page. US investor guidance.
- Access: published section sequence: company purpose, problem, solution, why now, market, competition, business model, team, financials, vision.
- Application: use these as coverage questions, not an automatic 10-slide ordering. A concise product definition precedes unexplained market jargon.

### R04 — Front / Inside Front's series A slide deck
- URL: https://front.com/blog/inside-fronts-series-a-slide-deck
- Original: 2016-08-02; article includes later editorial links. US SaaS, Series A.
- Access: founder's retrospective text, especially investor feedback; embedded Slideshare itself was not inspected in this research.
- Observed: founder described capital efficiency and customer expansion as strengths; acquisition channels and projections as weaknesses; more usage and buyer detail as useful additions.
- Application: require distribution, retention, buyer and capital-use reasoning rather than product features alone. No exact slide chronology claimed.

### R05 — Front / Series D deck
- URL: https://front.com/blog/front-series-d-deck
- Original: 2022-06-30. US SaaS, growth-stage fundraising.
- Access: founder article sections The process and The environment; embedded deck not independently inspected.
- Observed: introductory discussion, deck and later diligence are distinct stages; unit economics and the profitability path received attention in this round.
- Application: keep main talk and data room separate; do not copy growth-stage financial standards or historical investor sentiment into a pre-seed company as current fact.

### R06 — YC / How to Pitch Your Company
- URL: https://www.ycombinator.com/blog/how-to-pitch-your-company/
- Original: 2016-07-19. US founder/investor guidance.
- Access: article's seven questions and editing advice.
- Observed question order: product, market, progress, unique insight, BM, team, ask. User-path explanation is offered as an alternative to abstract language.
- Application: finish with a specific request and use a truthful product journey. This is another viable order, not a reason to erase founder motivation or customer evidence.

## Korean examples and event context

### R07 — NAVER / 2025 Q4 earnings presentation
- Landing: https://www.navercorp.com/investment/earnings
- PDF: https://www.navercorp.com/api/article/download/acd6abea-d548-441d-b69c-92ca3dee97b3
- Publication: 2026-02-06. Korea, listed-company earnings; 16 pages.
- Access: parsed PDF headings/content; page images 2, 3 and 4 specifically inspected.
- Observed order: reporting caveat → summary → business segments → costs/profit → segment profit → cash/borrowing → appendices. Page 3 separates quarter/year comparisons and units; page 4 pairs a chart with drivers and definitions.
- Application: date/unit/denominator discipline and a summary-to-drivers structure for earnings. Dense financial tables belong in a startup appendix, not blindly on every live-pitch slide. No video delivery analysis claimed.

### R08 — Asan Nanum Foundation / 10th startup competition recap
- URL: https://asan-nanum.org/press/아산나눔재단-정주영-창업경진대회-온라인-데모데-2/
- Original: 2021-08-27. Korea, early-stage demo-day context.
- Access: official press recap, not individual slide decks or transcript.
- Observed: multiple teams presented after a business-execution phase; the event was streamed through the foundation's YouTube channel.
- Application: locate original company recordings and stage/rubric before comparison. A competition award or organizer's description is not evidence of a specific slide order or independently measured product superiority.

### R09 — dcamp / batch program description
- URL: https://dcamp.kr/program/batch
- Date: dynamic page, accessed 2026-09-28. Korea, scale-up program context.
- Access: official search-extracted program text, not a recorded company pitch.
- Observed: this program targets already launched companies preparing to scale and describes coaching, investment and business connections.
- Application: separate a scale-up presentation's proof requirements from an idea-stage pitch. Marketing outcome claims are not reproduced as benchmarks. This entry is context, not a talk-sequence analysis.

## Public-company spoken IR

### R10 — Microsoft / FY2025 Q4 earnings call
- URL: https://www.microsoft.com/en-us/investor/events/fy-2025/earnings-fy-2025-q4
- Original: 2025-07-30. US public-company investor/analyst call.
- Access: official text transcript. Audio/video pacing and gestures not analyzed.
- Observed: IR introduction and reporting/forward-looking qualifications, CEO business discussion, CFO results/outlook, Q&A. The introduction distinguishes reporting bases and comparisons.
- Application: synchronize numbers, definitions and spoken handoffs; separate realized results from guidance. Do not borrow earnings-call length or listed-company legal text wholesale for a short founder pitch.

## User-supplied video access, not analyzed talks

| ID | URL | Confirmed access | Not confirmed |
|---|---|---|---|
| V01 | https://www.youtube.com/watch?v=w4n9Y_5msuo | A third-party search result labels it a 10th competition Sylvia 5-minute highlight | Original title verification, captions, full playback, slide order, delivery and timecodes |
| V02 | https://www.youtube.com/watch?v=PWY_TQYMNBY | User-supplied URL only | Title, company, transcript, playback and sequence |

Watch-page and oEmbed access attempts failed in this environment. V01 is `metadata_only` with a secondary discovery source; V02 is `unavailable`. Neither is evidence for a talk's content. Discovery for V01: https://serieamania.com/g2/bbs/board.php?bo_table=freetalk&wr_id=21370857 . This secondary page is not used to validate product facts. Retry through authorized host tools or use a user-provided transcript in a later run; do not invent an analysis from the title.

## Technical specifications (checked 2026-09-28)

- T01 OpenAI skills: https://developers.openai.com/codex/skills (redirects to https://learn.chatgpt.com/docs/build-skills). Inspected required SKILL.md, `.agents/skills` discovery, optional `agents/openai.yaml` and explicit invocation. The installer uses the documented personal directory; no claim of account registration.
- T02 Claude Code skills: https://code.claude.com/docs/en/skills . Inspected personal `.claude/skills`, `/skill-name`, and Cowork/cloud differences. Local directory installation does not enable account skills in remote sessions; follow the official account/project route separately.
- T03 Agent Skills format: https://agentskills.io/specification . Inspected name/description, metadata strings, optional scripts/references. Canonical name `ir-script`; UI metadata `IR & SCRIPT`.

## Search/review log and limits

Queries included the two exact video IDs, official YC pitch/deck guidance, Front funding decks, NAVER earnings, Microsoft FY25 Q4 transcript and Korean official demo-day/program pages. Unrelated results were excluded. Official pages and founder articles were preferred over recycled deck galleries. We inspected one Korean company PDF and official foreign IR text; we did not watch complete videos, subscribe to competitor products, independently reproduce company metrics, or conduct customer interviews.

For each new user project add its own current competitor/market sources and relevant actual-company examples. This historical reference set is not enough to substantiate a new company's market or claims. Sources differ in purpose and access; do not advertise them as ten fully watched company pitches.
