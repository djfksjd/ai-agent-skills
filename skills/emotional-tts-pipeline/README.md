# 🎙️ claude-qwen-tts

Qwen3-TTS 기반 고품질 한국어/다국어 음성 합성 Claude Code 플러그인

[English](README_EN.md)

## 개요

Claude Code에서 TTS 관련 작업을 시작하면, 스킬이 자동으로 활성화되어 음성을 생성합니다. "이 대본 읽어줘", "TTS로 변환해줘" 같은 요청을 자연스럽게 처리합니다.

## 설치

### 1. Marketplace 등록

```bash
/plugin marketplace add HariFatherKR/claude-qwen-tts
```

### 2. 플러그인 설치

```bash
/plugin install claude-qwen-tts@claude-qwen-tts
```

### 3. 환경 구축

```bash
/tts-setup
```

Python 가상환경 생성, 패키지 설치, 모델 다운로드를 자동으로 진행합니다.

### 4. 초기 설정

```bash
/tts-init
```

대화형으로 레퍼런스 음성과 출력 폴더를 설정합니다.

## 주요 기능

| 기능 | 설명 |
|------|------|
| Voice Clone | 레퍼런스 음성을 복제하여 TTS 생성 |
| Voice Design | 텍스트 설명으로 가상 목소리 생성 |
| Script to Audio | 마크다운/텍스트 대본을 나레이션으로 변환 |
| 자동 인식 | Claude가 TTS 요청을 자동으로 인식 |

## 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `/tts` | 텍스트 → 음성 | `/tts "안녕하세요 여러분"` |
| `/tts-design` | 가상 목소리로 생성 | `/tts-design "안녕" --voice "따뜻한 남성"` |
| `/tts-script` | 대본 파일 → 음성 | `/tts-script script.md` |
| `/tts-setup` | 환경 구축 | `/tts-setup` |
| `/tts-init` | 대화형 설정 | `/tts-init` |

### /tts 옵션

```bash
/tts "텍스트" [--output file.wav] [--voice ref.wav]
```

### /tts-design 옵션

```bash
/tts-design "텍스트" --voice "목소리 설명" [--lang Korean] [--output file.wav]
```

### /tts-script 옵션

```bash
/tts-script script.md [--output file.wav] [--pause 0.8] [--speed 1.0]
```

## 요구사항

- **Python**: 3.10 이상
- **디스크 공간**: 약 8GB (모델용)
- **GPU**: 권장 (Apple Silicon MPS 또는 NVIDIA CUDA)
- **CPU**: 지원하지만 느림

## 지원 언어

- 한국어 (Korean)
- 영어 (English)
- 중국어 (Chinese)
- 일본어 (Japanese)
- 광동어 (Cantonese)

## 샘플 음성

기본 제공 샘플 (CC0 라이선스):
- `ko_male.wav` - 한국어 남성 목소리
- `ko_female.wav` - 한국어 여성 목소리

본인 목소리 사용: `/tts-init` 실행 후 "내 음성 파일 등록" 선택

## 크레딧

- [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) - Alibaba의 TTS 모델
- [Claude Code](https://claude.ai/code) - Anthropic의 AI 코딩 어시스턴트

## 라이선스

MIT License

## 이슈 & 기여

이슈는 [GitHub Issues](https://github.com/HariFatherKR/claude-qwen-tts/issues)에 등록해주세요.
