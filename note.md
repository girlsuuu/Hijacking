# Note

## Logs of claude4_sonnet and grok3_mini are only saved for 50 examples, as we lost recording with other 50.

# Running Commands

## Basic Command

```bash
python main.py --target-model claude-4-sonnet
```

## Full Examples

```bash
python main.py \
  --target-model gpt-o4-mini \
  --start-examples 1 \
  --end-examples 100
```

## Available Target Models

- gemini-2.5-pro
- gpt-o4-mini
- gpt-5-mini-minimal
- gpt-5-mini-low
- gpt-5-mini-medium
- gpt-5-mini-high
- grok-3-mini
- claude-4-sonnet

## Required API Keys

```bash
export GEMINI_API_KEY="..."      # Required
export OPENAI_API_KEY="..."      # If testing GPT models
export ANTHROPIC_API_KEY="..."   # If testing Claude models
export GROK_API_KEY="..."        # If testing Grok models
```
