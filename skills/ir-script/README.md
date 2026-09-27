# IR & SCRIPT

**한국·해외 사례 조사부터 IR 자료, 발표대본, 예상 질문까지.**

표시 이름은 **IR & SCRIPT**, 호출용 이름은 **ir-script**입니다. Codex·Claude Code 등 Agent Skills 지원 환경을 위한 범용 스킬입니다. 특정 회사의 비공개 자료는 포함하지 않습니다.

## 작업 흐름

원본·버전 확인 → 국내외 사례와 시장·경쟁 조사 → 근거 정리 → 발표 순서 선택 → 슬라이드·대본 동시 작성 → Q&A → 문체·숫자·순서·렌더링 점검.

기획 이유, 실제 고객 문제, 경쟁 솔루션, 시장, BM을 먼저 확인합니다. '경쟁사는 문서만 작성한다' 같은 편의적인 단정이나, 근거 없는 시장 점유율·사용자 수를 넣지 않습니다. 제목은 짧고 구체적으로, 대본은 자연스러운 존댓말로 구분합니다.

**조사와 작성은 호스트 LLM·검색 도구가 수행합니다.** 동봉 Python은 오프라인 기본 생성·검증기입니다. 자체적으로 유튜브를 시청하거나 AI를 호출하는 서비스가 아닙니다. 현재 호스트의 전문 슬라이드 도구가 있으면 그 도구를 우선 사용합니다.

## 설치

Python 3.10 이상. 저장소를 처음 받을 때:

```bash
git clone https://github.com/djfksjd/ai-agent-skills.git
cd ai-agent-skills/skills/ir-script
python scripts/install.py codex
# Claude Code용은 대신 다음 실행:
# python scripts/install.py claude
```

Codex 개인 경로는 `~/.agents/skills/ir-script`, Claude Code는 `~/.claude/skills/ir-script`입니다. `--root /원하는/skills/폴더`로 프로젝트 범위를 지정할 수도 있습니다. 설치 도우미는 네트워크·계정 변경·패키지 설치를 하지 않으며 기존 폴더를 덮어쓰지 않습니다.

GitHub 업로드, 로컬 설치, ChatGPT/Cowork 계정 활성화는 별개입니다. Cowork·클라우드가 개인 컴퓨터의 폴더를 자동으로 읽는다고 가정하지 마세요. 공식 근거는 `references/research.md` T01–T03에 있습니다.

## 호출

Codex에서:

```text
$ir-script
첨부한 사업계획서와 이전 발표자료를 읽고 관련 한국·해외 IR 사례를 조사해줘.
초기 투자자 대상 8분 발표로, 기획 배경·문제 확인·경쟁 비교·시장·BM을 포함해줘.
제목은 짧고 담백하게, 대본은 자연스럽게 말하는 존댓말로 작성해줘.
PPTX/PDF, 발표대본 DOCX/PDF, Q&A와 출처·검증 보고서를 만들어줘.
참고 영상은 실제 확인한 범위만 사용하고, 슬라이드와 대본의 순서를 맞춰줘.
```

Claude Code에서는 `/ir-script`로 호출합니다. 설치 후 실제 호스트 목록에서 나타나는지 확인하세요. 검색·파일 생성 도구가 없는 LLM에서는 가능한 범위가 제한됩니다.

## 파일 구성

| 파일 | 역할 |
|---|---|
| `SKILL.md` | 실행 지침과 품질 기준 |
| `references/research.md` | 공식 사례·지침 10건, 요청 영상 2건의 접근 상태, 기술 문서 3건 |
| `references/story-and-copy.md` | 단계별 발표 구성, 시장·경쟁·BM 검토와 문체 |
| `templates/project-state.md` | 버전·결정·근거·미확인 항목을 남기는 로컬 기록 |
| `templates/release-checklist.md` | 전수 검수 체크리스트 |
| `templates/deck.example.json` | 실제 기업과 무관한 본문 3장·부록 1장 실행 예제 |
| `scripts/pipeline.py` | PPTX·DOCX·Markdown·Q&A·PDF 생성과 정합성 검사 |
| `scripts/financials.py` | 부가세·사용기간을 명시한 월별 매출·손익 시나리오 |
| `scripts/install.py` | 로컬 설치 도우미 |
| `tests/test_pipeline.py` | 잘못된 출처·문체·동기화·계산·파일 변경 회귀 검사 |

## 기본 생성기 실행

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/pipeline.py lint templates/deck.example.json --strict-style
python scripts/pipeline.py build templates/deck.example.json --out /tmp/ir-demo-v1 --pdf --strict-style
python scripts/pipeline.py verify /tmp/ir-demo-v1
python scripts/financials.py templates/financial.example.json
```

Windows에서는 `/tmp/ir-demo-v1` 대신 새 로컬 폴더 경로를 사용합니다. `--pdf`는 별도 설치된 LibreOffice/soffice가 PATH에 있어야 합니다. 없으면 오류로 중단합니다. `--pdf`를 빼면 PPTX·DOCX·Markdown 생성은 가능합니다. 글꼴은 시스템에 설치된 이름을 `project.font`에 지정하며, 폰트 파일을 배포하지 않습니다.

기본 레이아웃은 `cover`, `columns`, `process`입니다. 제목 55자, 핵심문구 90자, 본문 최대 3개·각 70자 제한을 두며 수동 줄바꿈을 받지 않습니다. 이 제한은 기본 엔진의 밀도 관리일 뿐 시각적 완성 보장이 아닙니다. 복잡한 표·차트·실제 제품 화면은 전문 호스트 엔진을 사용하세요.

출력: `deck.pptx`, `script.docx`, `script.md`, `qa.md`, `claims.csv`, `deck.json`, `qa-report.json`, `manifest.json`. PDF 옵션 시 `deck.pdf`, `script.pdf` 추가. 기존 출력 폴더는 덮어쓰지 않습니다.

## 동기화와 검증

`deck.json`이 제목·장수·순서·본문/부록·낭독문·Q&A의 공통 원본입니다. 자동 검사는 ID 참조, 상태, 문체 패턴, 시간 예산, 파일 해시, PPT 노트 ID, DOCX 제목과 Markdown 순서를 확인합니다. 해시는 변경 감지용이며 보안 서명이나 사실 확인이 아닙니다.

기존 자료의 실제 제목과 장 순서를 추출한 뒤 비교할 수도 있습니다:

```bash
python scripts/pipeline.py check-sync deck.json extracted-script-manifest.json
```

별도 manifest 형식: `{"slides":[{"id":"S01","kind":"main","title":"실제 제목"}]}`. 원본에 ID가 없으면 먼저 대응표를 작성해야 하며, 생성기가 임의로 의미를 추정하지 않습니다. 수동 PPT 수정은 원본 JSON에 반영하고 새 버전으로 다시 생성합니다.

`verified` 상태에는 읽은 출처와 위치가 필요합니다. 영상 제목만 확인한 자료는 검증된 주장으로 연결할 수 없습니다. 다만 존재하는 출처가 실제 주장을 뒷받침하는지는 별도 검토해야 합니다. 자동 검사 통과는 사실·디자인·리허설 통과가 아닙니다.

## 조사 범위와 한계

YC·Sequoia의 발표 지침, Front 창업자의 투자유치 회고, NAVER 실적발표 PDF와 Microsoft 공식 대본, 국내 데모데이·배치 운영 자료를 참고했습니다. 각각의 관찰 범위와 적용·제외 기준을 연구 노트에 담았습니다. 초기 투자유치와 상장기업 실적발표를 같은 목차로 만들지 않습니다.

요청된 두 유튜브는 원본 자막·전체 재생을 확인하지 못했습니다. 첫 영상은 2차 검색 결과의 제목만 확인했고, 두 번째는 제목도 미확인입니다. 연구 노트에서 이를 분석 완료로 표기하지 않았습니다. 공식 사례 10건에도 지침·회고·행사 맥락 자료가 섞여 있으며, 회사 발표 10편을 모두 시청했다는 뜻이 아닙니다.

재무 도우미는 월별 활성 고객과 계약금액의 균등 월배분 시나리오입니다. 현금흐름·환불·이연수익·회계/세무 판단은 모델링하지 않습니다. 실제 고객 수와 비용은 사용자가 제공해야 합니다.

자동 검사 뒤에도 모든 슬라이드와 대본 페이지를 렌더링해 확인하고, 실제 낭독으로 시간을 재야 합니다. `qa-report.json`의 시각 검수 상태는 자동으로 통과 처리하지 않습니다.

## 라이선스

새로 작성한 스킬 지침·코드는 하위 `LICENSE`의 MIT 범위를 따릅니다. 연결한 외부 자료와 사용자 원본, 기존 저장소의 다른 스킬에는 적용되지 않습니다. 회사 문서·자격증명·외부 영상/슬라이드 원문은 동봉하지 않습니다.
