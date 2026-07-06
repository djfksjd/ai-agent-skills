# 콘텐츠 마케팅 팀 자동화 시스템 구축

콘텐츠 마케팅 팀 자동화 시스템을 만들어줘. 하나의 YouTube URL 또는 웹사이트 URL을 입력하면 자동으로 멀티 플랫폼 마케팅 콘텐츠가 생성되는 시스템이야.

## 프로젝트 구조

```
.claude/
├── agents/
│   │ # 0. 오케스트레이터 팀 (Council)
│   ├── planner.md                   # 기획 에이전트
│   ├── reviewer.md                  # 검수 에이전트
│   │
│   │ # 1. 텍스트 마케팅 팀
│   ├── newsletter-writer.md         # 뉴스레터
│   ├── blog-writer.md               # 블로그
│   ├── shorts-scriptwriter.md       # 쇼츠 대본
│   ├── thread-writer.md             # 스레드 (X)
│   ├── linkedin-writer.md           # 링크드인
│   └── youtube-scriptwriter.md      # 유튜브 리뷰 대본
│
└── skills/
    │ # 2. 비주얼 마케팅 팀 (나노바나나 3.0)
    ├── nanobanana-visual/
    │   ├── SKILL.md
    │   ├── references/
    │   │   ├── card-news-guide.md
    │   │   └── thumbnail-guide.md
    │   └── templates/
    │       ├── card-news-prompt.md
    │       └── thumbnail-prompt.md
    │
    │ # 3. 영상 제작 팀
    └── shorts-video-maker/
        ├── SKILL.md
        ├── scripts/
        │   ├── download_video.py     # yt-dlp
        │   ├── extract_audio.py      # ffmpeg
        │   ├── transcribe.py         # whisper
        │   └── cut_shorts.py         # ffmpeg 클리핑
        └── references/
            └── shorts-spec.md
```

---

## 워크플로우

```
[URL 입력]
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 1. planner (기획 에이전트)                                │
│    - URL 분석 (YouTube vs 웹사이트)                      │
│    - 콘텐츠 추출 (자막/본문)                              │
│    - 핵심 메시지 3-5개 정리                              │
│    - 각 에이전트에게 브리프 전달                          │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 2. 병렬 실행                                             │
│                                                         │
│   [텍스트 팀 - Subagents]       [비주얼 팀 - Skill]       │
│   ├── newsletter-writer         ├── 카드뉴스 생성        │
│   ├── blog-writer               └── 썸네일 생성          │
│   ├── shorts-scriptwriter ──────────┐                   │
│   ├── thread-writer                 │                   │
│   ├── linkedin-writer               │                   │
│   └── youtube-scriptwriter          │                   │
│                                     ▼                   │
│                            [영상 팀 - Skill]             │
│                            └── 쇼츠 3개 제작             │
│                               (대본 참조)                │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 3. reviewer (검수 에이전트)                               │
│    - 브랜드 톤 일관성                                    │
│    - 팩트 체크 (원본 대비)                               │
│    - 플랫폼별 스펙 검증                                  │
│    - 수정 요청 또는 최종 승인                             │
└─────────────────────────────────────────────────────────┘
    │
    ▼
[outputs/ 폴더에 최종 결과물]
```

---

## 에이전트 설계 원칙
https://code.claude.com/docs/ko/sub-agents 클로드 코드의 공식 가이드라인을 참고해줘

각 subagent(.claude/agents/*.md)는 다음 형식을 따라:

```yaml
---
name: [agent-name]
description: |
  [구체적인 역할 설명]
  [언제 사용되는지 - "MUST BE USED" 또는 "USE PROACTIVELY" 포함]
tools: [필요한 도구들]
model: sonnet 또는 haiku
---

[시스템 프롬프트]
- 역할 정의
- 작업 프로세스
- 출력 포맷
```

---

## 각 에이전트 상세 설계

### 0. 오케스트레이터 팀

#### planner.md (기획 에이전트)
- **역할**: 프로젝트 총괄 기획, 콘텐츠 추출, 브리프 작성
- **tools**: Read, Write, Bash, Glob, Grep
- **model**: sonnet
- **주요 기능**:
  - YouTube URL → youtube-transcript MCP로 자막 추출
  - 웹사이트 URL → fetch/firecrawl로 본문 추출
  - 핵심 메시지 3-5개 도출
  - 각 에이전트별 맞춤 브리프 작성
- **출력**: 브리프 문서 (brief.md)

#### reviewer.md (검수 에이전트)
- **역할**: 모든 콘텐츠 품질 검수
- **tools**: Read, Glob, Grep
- **model**: sonnet
- **검수 항목**:
  - 브랜드 톤 일관성 (ASC 스타일)
  - 팩트 체크 (원본 대비)
  - 플랫폼별 스펙 준수
  - 한국어 자연스러움 (AI틱 표현 제거)
- **출력**: 검수 리포트 (review-report.md)

### 1. 텍스트 마케팅 팀

#### newsletter-writer.md
- **역할**: ASC 스타일 뉴스레터 작성
- **tools**: Read, Write
- **model**: sonnet
- **스펙**: 15,000-20,000자, Q&A 인터뷰 형식
- **출력**: newsletter.md

#### blog-writer.md
- **역할**: SEO 최적화 블로그 글 작성
- **tools**: Read, Write
- **model**: sonnet
- **스펙**: 3,000-5,000자, 소제목 구조화
- **출력**: blog.md

#### shorts-scriptwriter.md
- **역할**: 쇼츠/릴스용 60초 대본 3개 작성
- **tools**: Read, Write
- **model**: haiku
- **스펙**: 각 60초, 후킹→본문→CTA 구조
- **출력**: shorts-scripts/ 폴더 (shorts-01.md ~ shorts-03.md)
- **중요**: 영상 팀에서 이 대본을 참조함

#### thread-writer.md
- **역할**: X(트위터) 스레드 10개 작성
- **tools**: Read, Write
- **model**: haiku
- **스펙**: 각 280자 이내, 훅→본문→CTA
- **출력**: threads/ 폴더 (thread-01.md ~ thread-10.md)

#### linkedin-writer.md
- **역할**: 링크드인 포스트 1개 작성
- **tools**: Read, Write
- **model**: haiku
- **스펙**: 1,500자 이내, 전문가 톤
- **출력**: linkedin.md

#### youtube-scriptwriter.md
- **역할**: 유튜브 리뷰 영상 대본 작성
- **tools**: Read, Write
- **model**: sonnet
- **스펙**: 스크립트 형식, 타임스탬프 포함
- **출력**: youtube-script.md

---

## Skill 설계

설계원칙: https://code.claude.com/docs/ko/skills 공식 가이드 문서를 잘 따라줘

### 2. 비주얼 마케팅 팀 (nanobanana-visual)

#### SKILL.md
```yaml
---
name: nanobanana-visual
description: |
  나노바나나 3.0 프로를 사용해 인스타그램 카드뉴스와 유튜브 썸네일을 생성합니다.
  "카드뉴스 만들어줘", "썸네일 생성해줘" 요청 시 사용합니다.
---
```

**워크플로우**:
1. 브리프에서 핵심 메시지 추출
2. templates/의 프롬프트 템플릿 로드
3. 나노바나나 API 호출 (플레이스홀더)
4. 생성된 이미지 저장

**카드뉴스 스펙**:
- 5-7장 구성
- 슬라이드 1: 제목 + 후킹
- 슬라이드 2-6: 핵심 포인트
- 마지막: CTA

**썸네일 스펙**:
- 1280x720px
- 제목 텍스트 포함
- 눈에 띄는 색상 대비

### 3. 영상 제작 팀 (shorts-video-maker)

#### SKILL.md
```yaml
---
name: shorts-video-maker
description: |
  YouTube 영상에서 쇼츠 클립 3개를 자동 제작합니다.
  yt-dlp, whisper, ffmpeg 파이프라인을 사용합니다.
  "쇼츠 만들어줘", "영상 클립 추출해줘" 요청 시 사용합니다.
---
```

**워크플로우**:
1. yt-dlp로 원본 영상 다운로드
2. whisper로 타임스탬프 포함 자막 생성
3. shorts-scriptwriter의 대본 참조하여 구간 선정
4. ffmpeg로 9:16 비율 크롭 + 자막 하드코딩

**스크립트**:
- download_video.py: yt-dlp 래퍼
- transcribe.py: whisper 전사
- cut_shorts.py: ffmpeg 클리핑 (시작/종료 시간 기반)

---

## 콘텐츠 스타일 가이드 (모든 텍스트 에이전트 공통)

### 타겟 오디언스
- 1인 창업가 (솔로프리너)
- IT/AI에 관심 있는 사람
- 자동화, 생산성에 관심 있는 사람

### 톤앤매너
- 친근하고 실용적
- 중학생도 이해할 수 있는 쉬운 말
- 겸손한 표현 (과장 금지)

### 한국어 스타일
- "요"체 사용 (예: "~해요", "~이에요")
- AI틱한 표현 제거:
  - ❌ "혁신적인", "획기적인", "놀라운"
  - ✅ 구체적인 수치, 실제 사례
- 자연스러운 구어체

### 핵심 원칙
- 실용적 인사이트 중심
- 바로 적용 가능한 팁
- 구체적인 예시 포함

---

## 출력 폴더 구조

```
outputs/
├── brief.md                    # planner 브리프
├── newsletter.md               # 뉴스레터
├── blog.md                     # 블로그
├── linkedin.md                 # 링크드인
├── youtube-script.md           # 유튜브 대본
├── threads/
│   ├── thread-01.md ~ thread-10.md
├── shorts-scripts/
│   ├── shorts-01.md ~ shorts-03.md
├── visuals/
│   ├── card-news/
│   │   ├── slide-01.png ~ slide-07.png
│   └── thumbnail.png
├── shorts-videos/
│   ├── shorts-01.mp4 ~ shorts-03.mp4
└── review-report.md            # 검수 리포트
```

---

## 요청사항

1. 위 구조대로 모든 파일을 생성해줘
2. 각 에이전트는 description에 "MUST BE USED" 또는 "USE PROACTIVELY" 포함해서 자동 트리거되게 해줘
3. skill의 스크립트(yt-dlp, whisper, ffmpeg)는 실제 동작하는 Python 코드로 작성해줘
4. 나노바나나 API는 플레이스홀더로 두고, 나중에 API 키만 넣으면 동작하게 구조화해줘
5. 모든 에이전트가 planner의 brief.md를 참조하도록 연계해줘