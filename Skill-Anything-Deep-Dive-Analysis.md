# Skill-Anything (SYuan03/Skill-Anything ★257) — Deep Dive Analysis

**Generated for 墨麟AI集团 (Molin AI Group) — Global Education Research Report**

---

## 1. Project Identity

| Attribute | Value |
|-----------|-------|
| **Name** | Skill-Anything |
| **Author** | SYuan03 |
| **GitHub** | https://github.com/SYuan03/Skill-Anything |
| **Stars** | ~257 |
| **Current Version** | v0.2.0 |
| **License** | MIT |
| **Python** | 3.10+ |
| **PyPI** | `skill-anything` |
| **CLI Entry** | `sa` (alias for `skill-anything`) |
| **Tagline** | Turn source material into reusable learning systems. |

---

## 2. Architecture (MECE Breakdown)

### 2.1 Overall Pipeline

```
Source Material
  |
  v
PARSER LAYER                    <- 6 parsers, 1 base abstraction
  (PDF / Video / Web / Text / Audio / Repo)
  Output: List[KnowledgeChunk]
  |
  v
GENERATOR LAYER                 <- 5 generators
  (Knowledge / Quiz / Flashcard / Practice / Visual)
  Uses: LLM (OpenAI-compatible) or fallback (rule-based)
  Output: SkillPack dataclass
  |
  v
EXPORT LAYER                    <- 2 formats + 1 combined
  Study format: .yaml + .md + .png (concept map)
  Skill format: SKILL.md directory (Claude Code / Cursor / Codex)
  All format: both simultaneously
  |
  v
INTERACTIVE LAYER               <- 3 modes
     QuizRunner / ReviewRunner / Info
```

### 2.2 Code Module Map

```
skill_anything/
  __init__.py          Exports: Engine, __version__
  cli.py               Typer CLI (sa <command>) - 15+ commands
  engine.py            Core orchestrator: from_*, write, load, _build
  llm.py               OpenAI-compatible client (chat, generate_image)
  models.py            Dataclasses: SkillPack, QuizQuestion, Flashcard, ...
  linting.py           Skill package validator (SkillLinter)
  parsers/
    base.py            Abstract BaseParser + _split_into_chunks
    pdf_parser.py      PDF -> pages -> chunks (3 backends)
    video_parser.py    YouTube / .srt / .vtt -> timestamped segments
    web_parser.py      URL -> HTML -> BeautifulSoup -> chunks
    text_parser.py     .txt/.md -> heading-aware sectioning -> chunks
    audio_parser.py    .mp3/.wav/etc -> Whisper -> chunks
    repo_parser.py     Local/GitHub repo -> docs-first scan -> chunks
    skill_parser.py    SKILL.md dir -> reverse export -> SkillPack
  generators/
    knowledge_gen.py   Summary, notes, glossary, cheat sheet, learning path
    quiz_gen.py        6 question types (MCQ, T/F, Fill, Short, Scenario, Compare)
    flashcard_gen.py   Q/A flashcards with tags
    practice_gen.py    5 exercise types
    visual_gen.py      DALL-E concept map
  exporters/
    skill_exporter.py  SkillPack -> SKILL.md directory
  interactive/
    quiz_runner.py     CLI quiz: A-F grading, 6 types
    review_runner.py   CLI flashcard: multi-round spaced repetition
  tests/
    test_engine.py, test_parsers.py, test_generators.py, ...
```

### 2.3 Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| CLI | Typer (Rich integration) |
| Formatting | Rich (tables, panels, progress, trees) |
| Serialization | PyYAML |
| Config | python-dotenv (.env files) |
| LLM Client | openai (OpenAI, DeepSeek, Qwen, Ollama, vLLM) |
| HTTP | httpx (primary), urllib (fallback) |
| PDF | pdfplumber (primary), pymupdf/fitz, pypdf |
| Video | youtube-transcript-api, yt-dlp |
| Web | beautifulsoup4 (primary), regex (fallback) |
| Audio | openai-whisper (local), OpenAI Whisper API |
| Image Gen | DALL-E 3 or any OpenAI-compatible API |
| Build | Hatchling |
| Lint/Test | Ruff, pytest |

---

## 3. Innovation Points

### 3.1 First Unified Multi-Source Pipeline
The only open-source tool accepting PDF, YouTube URL, SRT/VTT, webpage, audio, text, local repos, and GitHub repos via a single `sa auto <source>` command. Auto-detection dispatches by file extension or URL pattern.

### 3.2 Dual-Format Output (Human + AI Agent)
- **Study format**: .yaml + .md + concept map PNG (human-readable, quizzable)
- **Skill format**: SKILL.md directory (Claude Code / Cursor / Codex compatible)
- Bidirectional round-trip: generate -> export -> import-skill -> lint -> re-export

### 3.3 Double Backend: LLM + Rule-Based Fallback
Every generator has two modes:
1. LLM mode (high-quality via structured JSON prompts)
2. Offline mode (no API key needed, basic extraction)

The tool always works regardless of API key availability.

### 3.4 12-Section Study Guide
Summary, Concept Map, Outline, Detailed Notes, Key Concepts, Glossary, Cheat Sheet, Takeaways, Quiz, Flashcards, Exercises, Learning Path.

### 3.5 6 Quiz Types Across 3 Difficulty Levels
Multiple Choice, True/False, Fill in the Blank, Short Answer, Scenario, Comparison.
Difficulty distribution: 20% easy, 50% medium, 30% hard.

### 3.6 Repo-to-Skill Toolchain (v0.2)
Docs-first codebase scanning, GitHub API integration, smart file selection (~30 files), CI-compatible linting.

### 3.7 Skill Import/Lint (Round-Trip Validation)
- `sa import-skill` rebuilds SkillPack from SKILL.md directory
- `sa lint` validates frontmatter, referenced files, asset YAML schema, content quality

### 3.8 LLM Provider Agnosticism
Any OpenAI-compatible endpoint: OpenAI, DeepSeek, Qwen, Ollama, vLLM. Proxy support. Separate image gen config.

---

## 4. How Conversion Works (Per Source Type)

### 4.1 PDF
```
file -> pdfplumber -> page-by-page text -> _split_into_chunks
  (paragraph-aware, overlapping, max_chars=2000) -> KnowledgeChunk[] with source_page -> Generators
```

### 4.2 Video
```
YouTube URL -> youtube-transcript-api -> (timestamp, text) segments -> chunks -> Generators
Local .srt/.vtt -> VTT/SRT parser -> same flow
Local .mp4 -> looks for .srt/.vtt alongside -> same flow
```

### 4.3 Web
```
URL -> httpx GET -> BeautifulSoup (strip script/style/nav) -> <article>/<main>/<body>
  -> paragraphs -> chunks with title metadata -> Generators
```

### 4.4 Audio
```
.mp3/.wav/etc -> Whisper (local model "base") -> segments with timestamps -> chunks -> Generators
Fallback -> OpenAI Whisper API -> same flow
```

### 4.5 Text
```
.txt/.md -> heading-aware splitting (#/##/###) -> sectioned content -> chunks -> Generators
```

### 4.6 Repo
```
Local dir or GitHub URL -> file walk/GitHub API -> file classification (docs > manifest > code)
  -> priority selection (~30 files) -> read content -> KnowledgeChunk[] with section=relpath :: heading -> Generators
```

### 4.7 Generator Internals
- **KnowledgeGenerator**: Concatenates chunks (<15K chars), sends structured prompt requesting 7-section JSON, parses response into KnowledgeOutput. Also generates timeline from chunk metadata.
- **QuizGenerator**: Per-chunk generation (4 questions each, max 40), prompt requests type+difficulty distribution, parses JSON array.
- **FlashcardGenerator**: Per-chunk (5 cards each, max 50), varied styles requested.
- **PracticeGenerator**: Single combined prompt, 5 exercise types.
- **VisualGenerator**: DALL-E prompt from title + concepts, generates PNG.

---

## 5. Unique Features (Not in Alternatives)

| Feature | Skill-Anything | Typical Alternatives |
|---------|---------------|---------------------|
| Multi-source unified pipeline | 7 source types | Usually single-source |
| Dual output (human + AI agent) | Study Pack + SKILL.md export | Human-only or agent-only |
| Round-trip import/export | sa import-skill reverses export | One-directional |
| Skill validation/linting | sa lint (CI-compatible) | None |
| LLM + offline fallback | Works without API key | API-gated |
| 6 quiz types, 3 difficulty levels | Yes | Usually 1-2 types |
| Multi-round spaced repetition | Yes (up to 5 rounds) | Single-pass |
| Rich CLI formatting | Colors, tables, panels, trees | Plain text |
| AI-generated concept map | DALL-E integration | None |
| Repo onboarding packs | Docs-first scanning | None |
| 12-section MECE study guide | Yes | 3-5 sections typical |
| Provider-agnostic LLM | Any OpenAI-compatible | Usually locked |
| CI-compatible linter | Yes | None |

---

## 6. Potential Gaps

1. **No Web UI**: CLI-only, limits non-technical users
2. **No persistent spaced repetition**: Session-only, no Anki-like scheduling
3. **No mobile support**
4. **LLM quality dependent**: No human-in-the-loop refinement
5. **English-centric prompts**: Chinese input works, output quality for non-English untested
6. **No learning analytics**: No progress tracking, no adaptive difficulty
7. **Small community**: 257 stars, single maintainer
8. **Beta maturity**: v0.2, Development Status 4 - Beta

---

## 7. Strategic Relevance for 墨麟AI集团

### Strengths:
- Complete content generation pipeline ready to use
- Agent-compatible SKILL.md format aligns with AI ecosystem trends
- Zero API-key barrier, pip installable
- Clean extensible architecture (plugin-like parsers/generators)
- Repo parser directly useful for developer education

### Integration Points:
1. Backend content generator microservice wrapping Engine
2. Content enrichment pipeline feeding LMS or Anki
3. Agent skill marketplace generating tradeable SKILL.md assets
4. CI/CD integration for automated onboarding docs

---

## 8. Competitor Landscape

| Tool | Sources | Quiz/Flashcards | Export | LLM Required | Repo |
|------|---------|----------------|--------|-------------|------|
| **Skill-Anything** | 7 types | 6 types + flashcards | YAML+MD+SKILL.md | Optional | Full |
| LangChain loaders | Many | No | Raw text | - | Limited |
| LlamaIndex readers | Many | No | Nodes/docs | - | Limited |
| Anki auto-generators | 1-2 types | Basic | APKG | Usually | No |
| ChatGPT/Claude | N/A | Manual | Chat text | Required | No |
| Quizlet | Image/PDF | Yes | Proprietary | No | No |

---

*Analysis generated for 墨麟AI集团 - Global Education Research Report. Based on full source code analysis of SYuan03/Skill-Anything v0.2.0.*
