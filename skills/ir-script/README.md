# IR & SCRIPT

**한국·해외 IR 사례 조사부터 발표자료, 대본, 예상 질문까지.**

표시 이름은 **IR & SCRIPT**, 스킬 식별자는 **ir-script**입니다. Codex·Claude Code 등 Agent Skills 지원 환경에서 사용하는 재사용 가능한 조사·기획·제작 절차입니다. 특정 회사의 사업계획서나 원본 대본은 포함하지 않습니다.

## 작업 흐름

자료·버전 확인 → 사례·시장·경쟁 조사 → 주장과 출처 정리 → 발표 순서 선택 → 슬라이드·대본 동시 작성 → Q&A → 문체·수치·순서·렌더링 검수.

LLM과 호스트의 검색 도구가 조사·분석을 수행합니다. Python 코드는 오프라인 생성·검증 도구입니다. 제목만 확인한 영상을 분석했다고 쓰거나, 경쟁사의 확인되지 않은 기능을 없다고 표시하지 않도록 설계했습니다.

## 포함 파일

| 파일 | 역할 |
|---|---|
| `SKILL.md` | 에이전트 실행 지침 |
| `references/research.md` | IR 참고자료 14개·기술 문서 3개의 출처, 관찰 범위, 적용 원칙 |
| `references/story-and-copy.md` | 기업 단계별 발표 흐름, 문체, 대본·디자인·검수 기준 |
| `templates/project-state.md` | 버전·결정·미확인 사항·다음 작업의 로컬 기록 |
| `templates/deck.example.json` | 본문 3장·부록 1장의 가상 실행 예제 |
| `scripts/pipeline.py` | 편집형 PPTX, 대본 DOCX/MD, Q&A, 출처표, PDF 생성과 정합성 검사 |
| `scripts/financials.py` | 월배분 순매출·누적매출·연환산액·손익분기 계산 |
| `scripts/install.py` | 덮어쓰지 않는 로컬 설치 도우미 |
| `tests/test_pipeline.py` | 데이터·생성·동기화·원가·설치 회귀 테스트 |

## 설치

Python 3.10 이상. 저장소를 받은 뒤 사용자 컴퓨터에서 실행합니다.

```bash
git clone https://github.com/djfksjd/ai-agent-skills.git
cd ai-agent-skills/skills/ir-script
python scripts/install.py codex
# Claude Code는 대신:
# python scripts/install.py claude
```

Codex 기본 설치 위치는 `~/.agents/skills/ir-script`, Claude Code는 `~/.claude/skills/ir-script`입니다. `--root /path/to/project/.agents/skills`처럼 호스트의 프로젝트 폴더를 지정할 수도 있습니다. `--dry-run`은 복사 경로만 표시합니다. 기존 폴더는 덮어쓰지 않습니다. 설치 후 호스트 목록에서 발견되는지 확인하고, 필요하면 재시작합니다.

**GitHub 업로드, 로컬 복사, ChatGPT/Cowork 계정 등록은 별개입니다.** 이 도구는 계정 설정을 바꾸지 않습니다. 경로와 등록 범위의 공식 문서는 연구 노트 T01–T03에 있습니다.

## 호출

Codex:

```text
$ir-script
첨부 사업계획서와 기존 PPT·대본을 확인해줘.
한국·해외의 관련 IR 사례를 조사하고, 초기 투자자 대상 8분 발표로 구성해줘.
기획 이유, 문제 근거, 경쟁사, 시장, BM, 검증 현황과 다음 요청을 포함해줘.
제목은 짧고 담백하게, 발표대본은 자연스러운 존댓말로 써줘.
PPTX/PDF, 대본 DOCX/PDF, 예상 질문, 출처와 검증 보고서를 만들어줘.
영상은 실제 확인한 내용만 사용하고 못 본 범위는 표시해줘.
```

Claude Code에서는 `/ir-script`로 호출합니다. 직접 스킬을 지원하지 않는 환경에서는 `SKILL.md`와 필요한 참고문서를 제공할 수 있지만 검색·파일 생성 능력은 해당 환경에 달려 있습니다.

## 오프라인 생성기 실행

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/pipeline.py lint templates/deck.example.json --strict-style
python scripts/pipeline.py build templates/deck.example.json --out /tmp/ir-demo-v1 --pdf --strict-style
python scripts/pipeline.py verify /tmp/ir-demo-v1
python scripts/financials.py templates/financial.example.json
```

Windows에서는 `/tmp/ir-demo-v1` 대신 새 로컬 경로를 사용합니다. `--pdf`에는 별도로 설치한 LibreOffice의 `libreoffice` 또는 `soffice`가 PATH에 필요합니다. 없으면 오류로 중단하며 PDF를 만들었다고 처리하지 않습니다. 옵션을 빼면 PPTX·DOCX·Markdown만 생성합니다. 글꼴은 설치된 것을 `font`에 지정합니다. 폰트 파일은 배포하지 않습니다.

출력 파일은 `deck.pptx`, `script.docx`, `script.md`, `qa.md`, `claims.csv`, `deck.json`, `qa-report.json`, `manifest.json`입니다. PDF 옵션을 사용하면 `deck.pdf`, `script.pdf`도 생성합니다. 기존 출력 폴더는 덮어쓰지 않습니다. 예제는 실제 기업이 아닌 가상 자료이며 완성된 투자제안서가 아닙니다.

## JSON 계약

`deck.example.json`을 시작점으로 사용합니다. 필수 상위 값: `schema_version: 1`, `company`, `language`, `audience`, `purpose`, `version`, 설치된 `font`, `talk_seconds`, `sources`, `claims`, `slides`, `qa`. `speech_rate_per_minute`는 조정 가능한 추정값입니다. 한국어는 공백 제외 문자, 기타 언어는 단어 수 기준이며 리허설 결과가 아닙니다.

슬라이드 필수 값: `id`, `kind`(main/appendix), `role`, `title`, `takeaway`, `bullets`, `speaker_text`, `cue`, `transition`, `seconds`, `claim_ids`. `pause_seconds`는 추정 낭독시간에 더하며 `seconds`에는 발표자가 계획한 멈춤·시연 시간을 포함합니다. 선택 `layout`은 cover/content입니다. 더 풍부한 도형·차트·표는 호스트의 전문 제작 도구로 같은 스토리보드를 사용합니다. 기본 생성기는 가독성을 위해 제목 70자, 본문 0–4항목·항목당 110자 제한이 있습니다. 한국어 문장형 제목을 의도적으로 유지할 때만 `allow_sentence_title: true`를 기록합니다.

주장 상태: `verified`, `user_provided`, `hypothesis`, `target`, `calculation`, `unverified`. `verified`에는 읽은 출처와 정확한 `locator`가 필요합니다. 나머지에는 `qualifier`, 계산에는 `method`가 필요합니다. `evidence`는 `source_id`와 `locator` 객체 배열입니다. 출처 접근 상태는 `full_text`, `partial`, `metadata_only`, `unavailable`입니다. 제목만 확인한 영상은 그 내용의 검증 근거가 될 수 없습니다. 부분 열람의 의미상 범위는 사람이 추가 확인해야 합니다.

Q&A에는 `id`, `question`, `answer`, `uncertainty`, `claim_ids`, 실제 부록을 가리키는 `appendix_id`가 필요합니다. 대본·발표 노트·Q&A가 동일 ID를 공유합니다.

별도 대본의 제목을 직접 추출한 뒤 대조할 수 있습니다:

```bash
python scripts/pipeline.py check-sync deck.json extracted-script-manifest.json
```

비교 파일 형식: `{"slides":[{"id":"S01","kind":"main","title":"..."}]}`. 개수뿐 아니라 순서, 제목, 본문/부록 경계를 비교합니다. 자동으로 모든 원본 의미를 추정하지 않습니다. 수동 수정 후에는 원본 JSON을 갱신해 새 버전으로 빌드합니다. 해시는 우발적 버전 혼선을 찾는 장치이지 보안 서명이나 법적 감사 증명이 아닙니다.

## 조사 반영과 한계

YC·Sequoia는 발표 목적과 사업 논리, Front·Buffer는 구매자·경쟁·고객 확장·획득 경로, NAVER·Microsoft·Kia는 기간·단위·실적/전망 구분과 전환을 참고했습니다. 실제 읽은 범위와 참고 적용은 연구 노트에 따로 적었습니다.

요청된 두 정주영 창업경진대회 영상은 **제목만 확인**했습니다. 전체 재생·자막·시간대별 분석을 완료했다고 표현하지 않습니다. 공식 행사 기사 역시 발표 대본은 아닙니다. 새로운 실행에서 접근 가능한 자막·영상을 확보하면 관찰 범위를 갱신합니다.

자동 검사는 실제 시장 검증, 고객 인터뷰, 법률 검토, 비교 성능 시험, 시각 검수나 리허설을 대신하지 않습니다. `qa-report.json`은 시각 검수를 pending으로 시작합니다. 호스트에서 모든 슬라이드·대본 페이지를 렌더링해 확인한 별도 검수 기록을 남겨야 합니다.

재무 도우미는 활성 고객 수와 계약기간의 균등 월배분 가정입니다. 현금흐름, 환불, 이연수익과 회계·세무 판단을 모델링하지 않습니다. 개인 AI 플랜의 CLI 연결과 BYOK를 구분하며, 제공사 약관·상용 연결·비학습·무보관 조건은 매 작업에서 최신 공식 자료로 확인합니다.

버전 1.0.0 / 2026-09-28. 실제 실행한 테스트와 한계는 `VALIDATION.md`를 참고하세요. 이 스킬의 새 코드와 지침만 MIT 라이선스 대상이며, 사용자 입력·제3자 자료·기존 저장소의 다른 파일에는 적용되지 않습니다.

## 초기 저장소 초안과의 차이

같은 날 올라온 초기 커밋 `faf3da3`의 자료와 현재 검증본을 대조했습니다. 기존 연구에 있던 Front Series B/C, YC 디자인 안내와 Dcamp 행사 자료는 R11–R14로 보존했습니다. 다른 세 스킬은 변경하지 않습니다.

초기 초안 JSON을 이미 작성했다면 현재 `templates/deck.example.json`에 맞춰 명시적으로 옮겨야 합니다. `duration_seconds`는 `talk_seconds`, `points`는 `bullets`로 바뀌었고 `schema_version: 1`과 `version`이 필요합니다. `speech_units_per_minute`는 `speech_rate_per_minute`와 단위가 다를 수 있으므로 숫자를 그대로 복사하지 않습니다. 출처의 `retrieved`는 `retrieved_at`, 주장 `source_ids`와 `locator`는 `evidence`의 `source_id`·`locator` 항목으로 옮깁니다. 미검증 주장에는 `qualifier`를 붙입니다. 초기 산출물은 원본을 보존하고 새 출력 폴더로 재생성합니다. 이 전환은 자동으로 실행하지 않습니다.

현재 테스트는 `VALIDATION.md`를 기준으로 합니다. 초기 22개 테스트 기록은 `TEST_REPORT.md`에서 이전 커밋으로 연결합니다.
