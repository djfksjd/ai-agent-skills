# 🎙️ claude-qwen-tts

High-quality Korean/multilingual text-to-speech Claude Code plugin based on Qwen3-TTS

[한국어](README.md)

## Overview

When you start TTS-related tasks in Claude Code, the skill automatically activates to generate audio. It naturally handles requests like "read this script" or "convert to TTS".

## Installation

### 1. Register Marketplace

```bash
/plugin marketplace add HariFatherKR/claude-qwen-tts
```

### 2. Install Plugin

```bash
/plugin install claude-qwen-tts@claude-qwen-tts
```

### 3. Setup Environment

```bash
/tts-setup
```

Automatically creates Python virtual environment, installs packages, and downloads models.

### 4. Initialize Configuration

```bash
/tts-init
```

Interactive setup for reference voice and output folder.

## Features

| Feature | Description |
|---------|-------------|
| Voice Clone | Clone voice from reference audio |
| Voice Design | Create virtual voices from text descriptions |
| Script to Audio | Convert markdown/text scripts to narration |
| Auto Detection | Claude automatically recognizes TTS requests |

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/tts` | Text to speech | `/tts "Hello everyone"` |
| `/tts-design` | Generate with designed voice | `/tts-design "Hello" --voice "warm male"` |
| `/tts-script` | Script file to audio | `/tts-script script.md` |
| `/tts-setup` | Setup environment | `/tts-setup` |
| `/tts-init` | Interactive configuration | `/tts-init` |

### /tts Options

```bash
/tts "text" [--output file.wav] [--voice ref.wav]
```

### /tts-design Options

```bash
/tts-design "text" --voice "voice description" [--lang Korean] [--output file.wav]
```

### /tts-script Options

```bash
/tts-script script.md [--output file.wav] [--pause 0.8] [--speed 1.0]
```

## Requirements

- **Python**: 3.10+
- **Disk Space**: ~8GB (for models)
- **GPU**: Recommended (Apple Silicon MPS or NVIDIA CUDA)
- **CPU**: Supported but slower

## Supported Languages

- Korean (한국어)
- English
- Chinese (中文)
- Japanese (日本語)
- Cantonese (粤语)

## Sample Voices

Default samples included (CC0 license):
- `ko_male.wav` - Korean male voice
- `ko_female.wav` - Korean female voice

Use your own voice: Run `/tts-init` and select "Register my own voice"

## Credits

- [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) - TTS model by Alibaba
- [Claude Code](https://claude.ai/code) - AI coding assistant by Anthropic

## License

MIT License

## Issues & Contributions

Please report issues at [GitHub Issues](https://github.com/HariFatherKR/claude-qwen-tts/issues)
