# IR & SCRIPT

**한국·해외 IR 사례 조사부터 슬라이드, 발표대본, 예상 질문까지.**

Codex·Claude Code 등 Agent Skills 지원 환경에서 사용하는 재사용 가능한 스킬입니다. 표시 이름은 **IR & SCRIPT**, 호출 이름과 폴더는 **ir-script**입니다. 특정 회사의 IR 자료나 투자 조언이 아닙니다.

## 작업 흐름

자료 버전 확인 → 사례·시장·경쟁 조사 → 주장과 출처 정리 → 발표 순서 선택 → PPT와 대본 동시 작성 → 예상 질문 → 문체·숫자·순서·렌더링 점검.

인터넷 조사와 판단은 스킬을 읽은 LLM 및 호스트의 검색 도구가 수행합니다. 동봉 Python 코드는 오프라인 생성·검증용입니다. 스킬을 등록했다고 자료가 자동 조사되는 별도 서버가 생기는 것은 아닙니다.

## 구성

| 파일 | 역할 |
|---|---|
| `SKILL.md` | 조사부터 산출물 검증까지 실행 지침 |
| `references/research.md` | 한국·해외 사례·가이드와 기술 문서의 출처·관찰 범위 |
| `references/story-and-copy.md` | 단계별 발표 구성, 제목·대본 문체, 디자인·리허설 기준 |
| `templates/project-state.md` | 원본 버전·결정·다음 작업의 로컬 기록 |
| `templates/deck.example.json` | 본문 3장+부록 1장의 가상 실행 예제 |
| `scripts/pipeline.py` | 편집형 PPTX·대본 DOCX/MD·Q&A·출처표·PDF 생성과 동기화 검사 |
| `scripts/financials.py` | 순매출·누적매출·연환산액·손익분기 계산 도우미 |
| `scripts/install.py` | 덮어쓰기 없는 로컬 설치 도우미 |
| `tests/test_pipeline.py` | 생성·오류 처리·정합성 회귀 테스트 |

## 로컬 설치

Python 3.10 이상에서 저장소를 받은 뒤 실행합니다. 설치 도우미 자체는 네트워크에 접속하지 않고 기존 스킬을 덮어쓰지 않습니다.

```bash
git clone https://github.com/djfksjd/ai-agent-skills.git
cd ai-agent-skills/skills/ir-script
python scripts/install.py codex
# Claude Code에 설치할 때는 대신:
# python scripts/install.py claude
```

기본 위치: Codex `~/.agents/skills/ir-script`, Claude Code `~/.claude/skills/ir-script`. 프로젝트 범위는 `--root /path/to/project/.agents/skills`처럼 부모 skills 폴더를 지정합니다. 설치 후 호스트의 목록에서 확인하고 필요하면 재시작합니다. 공식 경로 근거는 연구 노트 T01–T03에 있습니다.

**GitHub 업로드, 로컬 설치, ChatGPT/Cowork 계정 등록은 서로 다릅니다.** 이 저장소를 올리는 것만으로 모든 앱에 등록되지 않습니다. Cowork의 계정 설정을 이 설치 스크립트가 변경하지 않습니다.

## 호출

Codex: `$ir-script`. Claude Code: `/ir-script`.

```text
$ir-script
첨부한 사업계획서와 이전 PPT를 읽고, 한국·해외의 관련 기업 IR 사례를 조사해줘.
초기 투자자 대상 8분 발표로 구성하고, 기획 이유·문제 근거·경쟁·시장·BM을 포함해줘.
제목은 짧고 담백하게, 대본은 자연스럽게 말하는 존댓말로 작성해줘.
PPTX/PDF, 발표대본 DOCX/PDF, 예상 질문과 출처·검증 보고서를 만들어줘.
참고 영상은 실제 확인한 부분만 사용하고 못 본 부분은 구분해줘.
```

스킬 설치를 지원하지 않는 LLM에는 `SKILL.md`와 필요한 참고문서를 제공할 수 있지만 검색·파일 생성 도구가 없으면 가능한 범위가 제한됩니다.

## 실행 가능한 기본 생성기

전문 슬라이드 도구가 있으면 같은 `deck.json`을 바탕으로 그 도구에서 디자인합니다. 동봉 생성기는 편집 가능한 기본 레이아웃이며, 고급 차트·영상·애니메이션·3D 렌더러는 아닙니다.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/pipeline.py lint templates/deck.example.json --strict-style
python scripts/pipeline.py build templates/deck.example.json --out /tmp/ir-demo-v1 --pdf --strict-style
python scripts/pipeline.py verify /tmp/ir-demo-v1
python scripts/financials.py templates/financial.example.json
```

Windows에서는 `/tmp/ir-demo-v1` 대신 새 로컬 경로를 사용합니다. `--pdf`는 별도로 설치한 LibreOffice의 `libreoffice` 또는 `soffice`가 PATH에 있어야 합니다. 없으면 명시적 오류로 중단합니다. `--pdf`를 빼면 원본 형식만 생성합니다. 예제의 `font`는 `NanumGothic`이므로 해당 폰트를 설치하거나 환경에 설치된 한글 폰트명으로 변경합니다. 폰트 파일은 포함하지 않습니다.

출력: `deck.pptx`, `script.docx`, `script.md`, `qa.md`, `claims.csv`, `deck.json`, `qa-report.json`, `manifest.json`. PDF 옵션 사용 시 `deck.pdf`, `script.pdf` 추가. 기존 출력 폴더는 덮어쓰지 않습니다. 가상 예제를 실제 투자자료로 사용하지 않습니다.

## 데이터·정합성 계약

`deck.json`의 `slides`가 슬라이드·발표 노트·대본의 단일 원본입니다. 각 항목에 ID, main/appendix, 역할, 제목, 핵심 메시지, 화면 문구, 대본, 전환, 진행 안내와 배정 시간을 입력합니다. 선택적 `visual_spec` 등 설계 메타데이터는 전문 렌더러가 사용할 수 있으나 기본 생성기는 읽지 않습니다.

주장 상태: `verified`, `user_provided`, `hypothesis`, `target`, `calculation`, `unverified`.
출처 접근: `full_text`, `partial`, `metadata_only`, `unavailable`.

검증된 주장에는 읽은 출처와 정확한 위치가 필요합니다. 제목만 읽은 영상으로 사업 성과를 검증 처리할 수 없습니다. 부분 열람은 해당 위치만 뒷받침하며, 그 의미상 범위는 사람이 따로 검토해야 합니다. 주장 내용이 실제로 출처에 있는지는 컴파일러가 판단하지 않습니다.

기존 대본에서 ID·본문/부록·제목을 추출한 별도 매핑과 비교할 수 있습니다.

```bash
python scripts/pipeline.py check-sync deck.json extracted-script-manifest.json
```

매핑 형식: `{"slides":[{"id":"S01","kind":"main","title":"..."}]}`. 장수뿐 아니라 순서·제목·부록 경계를 비교합니다. 생성 후 파일을 수정하면 해시 검사가 실패하므로 원본 JSON에 반영해 새 버전을 생성합니다. 이 해시는 보안 서명이나 독립 감사 증명이 아닙니다.

## 조사 범위와 제한

Front의 창업자 회고에서 고객 확장·획득경로·자금 사용 논리를, YC에서 목적·청중·명확한 제품 정의와 연습을, NAVER와 Microsoft에서 기간·단위·전망 구분과 대본 전환을 참고했습니다. 정주영 창업경진대회는 공식 행사 기록과 제공된 영상의 확인 가능 범위를 분리했습니다. 관찰과 제안은 `references/research.md`에 따로 기록했습니다.

요청된 두 영상은 이번 조사에서 **제목만 확인**했습니다. 원본 자막·전체 재생·타임코드는 확보하지 못했습니다. 이를 분석 완료로 포장하지 않으며 다음 실행에서 접근 가능하면 이어서 조사합니다. 다른 회사의 슬라이드·대본 원문과 사용자가 첨부한 회사 자료는 동봉하지 않습니다.

자동 검사는 출처 ID, 상태, 문체 패턴, 시간 가정, 순서·파일 정합성을 확인합니다. 고객 인터뷰, 사실 판정, 경쟁 제품 성능 비교, 법률 검토, 시각 검수나 리허설을 대신하지 않습니다. `qa-report.json`의 시각 검수는 렌더링 확인 전까지 pending입니다.

재무 도우미는 월별 활성 고객과 계약기간의 균등 월배분 가정입니다. 현금흐름·환불·이연수익·회계/세무 판단을 모델링하지 않습니다. 고객 수 입력이 이미 이탈을 반영하는지, 급여·획득비가 비용에 포함됐는지 사용자가 명시해야 합니다.

개인 AI 플랜의 공식 CLI 연결과 BYOK를 혼동하지 않습니다. 특정 제공사의 상용 연결 허용·무제한 사용·비학습·무보관은 매번 공식 문서로 확인할 항목입니다.

## 버전·라이선스

1.0.0 · 2026-09-28. 실제 실행한 테스트와 한계는 `TESTED.md`에 기록합니다. Codex·Claude·Cowork의 사용자 계정별 설치/실행 시험은 로컬 생성기 테스트와 별개입니다.

새로 작성한 이 스킬의 코드·지침은 하위 `LICENSE`를 따릅니다. 외부 자료와 저장소의 기존 다른 스킬 및 사용자 원본에는 적용되지 않습니다.
