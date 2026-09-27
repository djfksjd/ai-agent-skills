# IR & SCRIPT

**한국·해외 IR 사례 조사부터 슬라이드, 발표대본, 예상 질문까지.**

표시 이름은 **IR & SCRIPT**, 설치·호출 이름은 **ir-script**입니다. Codex·Claude Code 등 Agent Skills 지원 환경에서 사용하는 범용 스킬이며, 특정 회사의 사업계획서나 채팅 기록은 포함하지 않습니다.

## 작업 흐름

원본·버전 확인 → 국내외 사례 및 시장·경쟁 조사 → 주장·출처 정리 → 발표 순서 선택 → PPT·대본 동시 작성 → Q&A → 문체·숫자·순서·렌더링 점검.

조사와 판단은 스킬을 읽은 LLM 및 호스트의 검색 도구가 수행합니다. 동봉 Python 코드는 네트워크나 유료 AI를 호출하지 않는 기본 생성·검증 도구입니다. 최신 웹 조사 기능과 사용 권한은 실행 환경에 필요합니다.

## 포함 파일

| 파일 | 역할 |
|---|---|
| `SKILL.md` | 조사·구성·작성·검증 지침 |
| `references/research.md` | IR 관련 자료 10개와 기술 문서 3개의 URL·관찰 범위·제약 |
| `references/story-and-copy.md` | 단계별 발표 순서, 시장·경쟁·BM, 한국어 문체와 리허설 기준 |
| `templates/project-state.md` | 입력 버전·결정·미확인 항목의 로컬 기록 |
| `templates/deck.example.json` | 가상 제품 본문 3장+부록 1장 실행 예제 |
| `scripts/pipeline.py` | 편집형 PPTX·대본 DOCX/MD·Q&A·출처표·PDF 생성 및 정합성 검사 |
| `scripts/financials.py` | 월별 순매출·누적매출·연환산액·손익분기 계산 도우미 |
| `scripts/install.py` | 기존 파일을 덮어쓰지 않는 로컬 설치 도우미 |
| `tests/test_pipeline.py` | 오류 재현·생성·검증 회귀 테스트 |
| `TEST_REPORT.md` | 실제 수행한 테스트와 미확인 범위 |

## 설치

Python 3.10 이상에서 저장소를 받은 뒤 실행합니다. 설치 도우미 자체는 네트워크에 접속하지 않습니다.

```bash
git clone https://github.com/djfksjd/ai-agent-skills.git
cd ai-agent-skills/skills/ir-script
python scripts/install.py codex
# Claude Code는 대신 다음 실행:
# python scripts/install.py claude
```

Codex 기본 설치 위치는 `~/.agents/skills/ir-script`, Claude Code는 `~/.claude/skills/ir-script`입니다. 프로젝트 범위 설치는 `--root /path/to/project/.agents/skills` 또는 해당 호스트의 skills 폴더를 지정합니다. 기존 대상이 있으면 오류로 멈추며, 업데이트 전 기존 폴더를 별도 보관해야 합니다.

설치 후 호스트의 스킬 목록에서 실제 표시를 확인합니다. 필요하면 호스트를 재시작합니다. 공식 경로 근거는 조사문서 T01–T03에 있습니다. GitHub 업로드, 로컬 설치, ChatGPT/Cowork 계정 등록은 서로 다릅니다. 로컬 폴더 복사로 다른 계정·원격 환경에 자동 등록되지 않습니다.

## 호출 예시

Codex:

```text
$ir-script
첨부한 사업계획서와 이전 PPT·대본을 읽어줘.
한국·해외의 관련 기업 IR과 공식 발표 자료를 조사해 초기 투자자 대상 8분 발표로 구성해줘.
기획 이유, 문제 근거, 경쟁사, 시장, BM, 검증 현황과 다음 실행 계획을 포함해줘.
슬라이드 제목은 짧고 담백하게, 대본은 자연스러운 존댓말로 작성해줘.
PPTX/PDF, 발표대본 DOCX/PDF, Q&A와 출처·검증 보고서까지 만들어줘.
참고 영상은 실제 확인한 부분만 사용하고 못 본 부분은 구분해줘.
```

Claude Code는 `/ir-script`로 호출합니다. 설치를 지원하지 않는 LLM에는 `SKILL.md`와 필요한 참고문서를 제공할 수 있지만, 검색·파일 도구가 없으면 수행 범위가 제한됩니다.

## 기본 생성기 실행

호스트에 전문 슬라이드 도구가 있으면 그 도구로 디자인하고 같은 `deck.json`을 기준으로 대본을 만듭니다. 동봉 생성기는 편집 가능한 기본 텍스트 레이아웃이며, 고급 차트·3D·영상·애니메이션 렌더러는 아닙니다.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/pipeline.py lint templates/deck.example.json --strict-style
python scripts/pipeline.py build templates/deck.example.json --out /tmp/ir-demo-v1 --pdf --strict-style
python scripts/pipeline.py verify /tmp/ir-demo-v1
python scripts/financials.py templates/financial.example.json
```

Windows에서는 `/tmp/ir-demo-v1` 대신 새 로컬 폴더 경로를 사용합니다. `--pdf`는 별도 설치한 LibreOffice의 `libreoffice` 또는 `soffice`가 PATH에 있어야 합니다. 없으면 오류로 중단합니다. PDF가 필요 없으면 `--pdf`를 뺍니다. 지정 글꼴은 환경에 설치되어 있어야 하며 글꼴 파일은 배포하지 않습니다.

출력은 `deck.pptx`, `script.docx`, `script.md`, `qa.md`, `claims.csv`, `deck.json`, `qa-report.json`, `manifest.json`입니다. PDF 옵션 사용 시 `deck.pdf`, `script.pdf`도 생성합니다. 기존 출력 폴더를 덮어쓰지 않습니다. 실패 시 부분 출력이 남을 수 있으며 완료 manifest가 없는 폴더는 출시본으로 취급하지 않습니다.

예제는 실제 기업이 아닌 가상 제품이고, 연구나 성능 결과를 의미하지 않습니다.

## 입력·검증 계약

`slides`의 ID·kind·title·role·takeaway·points·speaker_text·seconds를 기본으로 사용합니다. `cue`, `transition`, `pause_seconds`와 `claim_ids`도 예제처럼 명시합니다. 각 슬라이드는 하나의 핵심 메시지를 가집니다. `sources`의 URL·날짜·접근 범위와 `claims`의 상태·근거를 연결합니다.

주장 상태: `verified`, `user_provided`, `hypothesis`, `target`, `calculation`, `unverified`.
출처 접근: `full_text`, `partial`, `metadata_only`, `unavailable`.
영상 접근은 `video_access`에 더 세밀하게 기록할 수 있습니다. 제목만 읽은 영상으로 주장을 검증 처리할 수 없습니다. 실제 의미상 근거가 충분한지는 별도 검토가 필요합니다.

본문은 부록보다 앞에 배치하며, 부록 시간은 본문 발표시간에 합산하지 않습니다. 기본 레이아웃에 너무 긴 문구는 생성 전에 차단합니다. `--strict-style`은 설명문형 제목을 오류로 표시하며, 의도한 문장형 제목은 `title_style_exception`에 이유를 남길 수 있습니다. 이것은 AI 작성 여부를 판별하는 기능이 아닙니다.

이전 대본을 비교할 때는 본문·부록·제목을 실제 원본에서 추출한 JSON을 사용합니다.

```bash
python scripts/pipeline.py check-sync deck.json extracted-script-manifest.json
```

대조 파일은 `{"slides":[{"id":"S01","kind":"main","title":"..."}]}` 형태입니다. 장수뿐 아니라 순서·제목·본문/부록 경계까지 비교합니다. 파일명을 보고 동일 버전이라고 추정하지 않습니다. 생성 뒤 직접 수정하면 해시 검사가 실패하므로 원본 JSON에 반영해 새 버전을 생성합니다. 해시는 보안 서명이나 변조 방지 보증이 아닙니다.

## 조사 결과 반영

Sequoia는 핵심 내용 점검, YC는 제품 정의·청중·발표 흐름·가독성, Front의 창업자 회고는 고객 행동·획득·마일스톤과 자금 필요, NAVER와 Microsoft는 기간·단위·결과와 전망 및 대본 전환의 참고자료로 사용했습니다. 상장사 실적발표 형식을 초기 창업 피치에 그대로 적용하지 않습니다.

요청된 두 정주영 창업경진대회 영상은 이번 환경에서 제목만 확인했습니다. 원본 자막·전체 재생·타임코드는 확인하지 못했으며, 전체 분석을 완료한 사례로 표시하지 않았습니다. 연구문서에 링크와 접근 한계를 남겨 다음 실행에서 이어 확인하도록 했습니다.

## 한계와 데이터 보호

자동 검사는 ID·상태·문체 패턴·시간 가정·장수·순서·파일 정합성을 확인합니다. 사실판정, 고객 인터뷰, 경쟁 제품 성능 비교, 법률 검토, 시각 검수와 리허설을 대신하지 않습니다. `qa-report.json`의 시각 검수는 실제 렌더 확인 전까지 pending입니다.

재무 도우미는 가정한 월별 활성 고객과 계약가격의 균등 월배분 계산입니다. 현금흐름·환불·이연수익·회계/세무 판단을 모델링하지 않습니다. 개인 AI 구독의 공식 CLI 연결을 API 키 방식과 혼동하지 않으며, 제공사별 상용 연결·사용한도·학습·보관 조건은 매 실행에서 확인합니다.

개인 원본·고객정보·키·완전한 외부 슬라이드/대본·폰트는 공개 저장소에 포함하지 않습니다. 공개 예제에는 합성 데이터만 사용합니다. 새로 작성한 이 스킬의 코드·지침만 하위 `LICENSE`를 따르며 기존 다른 스킬과 외부 원문에는 적용되지 않습니다.
