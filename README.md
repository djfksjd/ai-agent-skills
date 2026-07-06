# AI Agent Skills

프로덕션 자동화를 위해 직접 설계·구현한 **AI 에이전트 스킬 모음**입니다.
LLM 코딩 에이전트(Claude Code)가 실무를 수행하도록 만든 재사용 가능한 모듈이며,
각 스킬은 실제 서비스·업무 파이프라인에서 동작하도록 만들어졌습니다.

## 수록 스킬

| 스킬 | 한 줄 | 엔지니어링 포인트 |
|---|---|---|
| **[hwpx-document-engine](skills/hwpx-document-engine)** | 한글(HWPX) 문서 생성·읽기·편집 | OWPML XML을 직접 조작해 **서식을 보존**하며 내용만 치환. 템플릿·검증 테스트 포함 |
| **[content-marketing-team](skills/content-marketing-team)** | URL 1개 → 전 플랫폼 마케팅 콘텐츠 자동 생성 | **멀티 에이전트 오케스트레이션**(리서치→기획→카피→비주얼)으로 숏폼·스레드·카드뉴스 동시 산출 |
| **[emotional-tts-pipeline](skills/emotional-tts-pipeline)** | Qwen3-TTS 기반 한국어/다국어 음성 합성 | 감정 나레이션 생성 파이프라인. 플러그인 구조로 배포 가능 |

## 설계 원칙

- **서식·데이터 무결성** — 문서 스킬은 원본 서식을 파괴하지 않는 XML 레벨 편집을 택함
- **에이전트 조합성** — 각 스킬은 독립 실행 + 파이프라인 체이닝 모두 지원
- **시크릿 비반입** — API 키·토큰은 코드에 하드코딩하지 않고 `.env`(gitignore) / `.env.example` 패턴으로 분리

## 구조

```
skills/
├── hwpx-document-engine/      # Python + OWPML XML, scripts/templates/tests
├── content-marketing-team/    # 멀티 에이전트 프롬프트 + 산출 파이프라인
└── emotional-tts-pipeline/    # Qwen3-TTS 플러그인 + 요구사항
```

---

> 각 스킬 하위 폴더의 `README.md` / `SKILL.md`에 상세 사용법이 있습니다.
> 생성 산출물(오디오·영상·이미지)과 시크릿은 저장소에 포함하지 않습니다.
