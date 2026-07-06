# 썸네일 프롬프트 템플릿

## 기본 프롬프트 구조

```
Create a YouTube thumbnail that drives clicks.

Size: 1280x720px (16:9 ratio)
Style: {THUMBNAIL_STYLE}

Main text: "{TITLE_TEXT}"
Text style: Bold, large, high contrast with stroke/shadow

Background: {BACKGROUND_TYPE}
Color scheme: {COLOR_SCHEME}

Additional elements:
- {EMPHASIS_ELEMENTS}
- {PERSON_OR_OBJECT}

Design requirements:
- Readable on mobile (small size)
- 3-second comprehension
- High visual impact
- No clickbait
```

## 스타일별 템플릿

### 스타일 1: 인물 중심

```
Create a YouTube thumbnail featuring a person.

Person: {PERSON_DESCRIPTION}
Expression: {EXPRESSION} (surprised, excited, curious, etc.)
Position: {POSITION} (left/right/center)

Text: "{MAIN_TEXT}"
Text position: {TEXT_POSITION}
Text style: Bold white with black stroke

Background: {BACKGROUND}
Accent elements: {ARROWS_OR_CIRCLES}

Size: 1280x720px
```

### 스타일 2: 텍스트 중심

```
Create a bold text-focused YouTube thumbnail.

Main text: "{HEADLINE}"
Subtext: "{SUBHEADLINE}" (optional)

Typography:
- Font: Extra bold sans-serif
- Size: Fills 40-60% of frame
- Color: {TEXT_COLOR}
- Effect: {TEXT_EFFECT} (shadow, stroke, 3D)

Background: {GRADIENT_OR_SOLID}
Decorative elements: {ICONS_OR_GRAPHICS}

Size: 1280x720px
```

### 스타일 3: Before/After

```
Create a split comparison YouTube thumbnail.

Layout: 50/50 vertical split

Left side (Before):
- Label: "Before" or "전"
- Visual: {BEFORE_STATE}
- Color tone: Muted, dull

Right side (After):
- Label: "After" or "후"
- Visual: {AFTER_STATE}
- Color tone: Vibrant, bright

Divider: {DIVIDER_STYLE}
Title overlay: "{COMPARISON_TEXT}"

Size: 1280x720px
```

### 스타일 4: 리스트형

```
Create a listicle-style YouTube thumbnail.

Main text: "{NUMBER} {THINGS}"
Example: "5 Ways to..." or "7가지 방법"

Number styling:
- Large, prominent number
- Contrasting color
- Possible circle/box around it

Supporting visual: {RELATED_ICONS}
Background: {CLEAN_BACKGROUND}

Size: 1280x720px
```

### 스타일 5: 제품/도구 리뷰

```
Create a product review YouTube thumbnail.

Product: {PRODUCT_NAME_OR_IMAGE}
Product position: Center or prominent

Verdict indicator:
- Rating stars/score
- Or reaction (thumbs up/down, emoji)

Text: "{REVIEW_HEADLINE}"
Example: "솔직 리뷰" or "1년 사용 후기"

Background: Gradient or product-complementary color

Size: 1280x720px
```

## 변수 설명

| 변수 | 설명 | 예시 |
|------|------|------|
| {THUMBNAIL_STYLE} | 썸네일 스타일 | "bold and energetic" |
| {TITLE_TEXT} | 메인 텍스트 | "이거 모르면 손해" |
| {BACKGROUND_TYPE} | 배경 유형 | "gradient blue to purple" |
| {EXPRESSION} | 인물 표정 | "surprised with open mouth" |
| {EMPHASIS_ELEMENTS} | 강조 요소 | "red arrow pointing right" |
| {TEXT_EFFECT} | 텍스트 효과 | "3D with shadow" |

## 감정별 색상 가이드

### 긴급/중요
- 배경: 빨강, 주황
- 텍스트: 흰색, 노랑
- 느낌: "지금 바로!", "놓치지 마세요"

### 교육/정보
- 배경: 파랑, 네이비
- 텍스트: 흰색
- 느낌: 신뢰, 전문성

### 재미/엔터테인먼트
- 배경: 밝은 색상, 그라데이션
- 텍스트: 다양한 색상
- 느낌: 활기, 에너지

### 고급/프리미엄
- 배경: 검정, 골드
- 텍스트: 흰색, 골드
- 느낌: 럭셔리, 가치

## 사용 예시

```
[인물 중심 썸네일]
Create a YouTube thumbnail featuring a person.

Person: Korean male in business casual, looking at camera
Expression: Surprised with raised eyebrows
Position: Right side of frame

Text: "월 500만원"
Text position: Left side, large
Text style: Bold yellow with black stroke

Background: Dark blue gradient
Accent elements: Yellow arrow pointing to person, money emoji

Size: 1280x720px
```

## 체크 포인트

프롬프트 작성 전 확인:
- [ ] 메인 메시지가 명확한가?
- [ ] 3-5단어 이내인가?
- [ ] 감정/톤이 정해졌는가?
- [ ] 모바일에서 잘 보일 구성인가?
