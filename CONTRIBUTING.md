# Contributing to TARS-WIZARD

Thanks for your interest in contributing to TARS-WIZARD! Whether you're fixing a bug, adding a feature, or improving docs — every contribution helps the community build better robots.

## Getting Started

### 1. Fork and Clone

```bash
# Fork this repo on GitHub, then:
git clone https://github.com/<your-username>/TARS-WIZARD.git
cd TARS-WIZARD
```

### 2. Set Up Your Environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# or: venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or: git checkout -b fix/your-bug-fix
```

**Branch naming convention:**
- `feature/description` — new features
- `fix/description` — bug fixes
- `docs/description` — documentation changes
- `refactor/description` — code restructuring

### 4. Make Your Changes

- Follow existing code patterns and style
- Keep changes focused — one feature or fix per PR
- Don't change servo angles, timing, or movement sequences unless you've tested on real hardware

### 5. Test Your Changes

```bash
# Lint
ruff check .

# Run tests
pytest

# If you have a Pi, test on real hardware before submitting
```

### 6. Commit and Push

```bash
git add <files-you-changed>
git commit -m "short description of what you changed"
git push origin feature/your-feature-name
```

### 7. Open a Pull Request

Go to your fork on GitHub and click "Compare & pull request". Fill out the PR template.

## Code Style

- **Python 3.10+** — we use modern Python features
- **Linting** — `ruff` is configured in `pyproject.toml`. Run `ruff check .` before committing
- **Imports** — standard library first, then third-party, then local. Sorted alphabetically within each group
- **Naming** — `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants
- **Comments** — only where the logic isn't self-evident. Don't comment obvious code
- **No hardcoded values** — use `config.yaml` for settings, `.env` for secrets

## What to Contribute

### Good First Issues
Look for issues labeled `good first issue` — these are beginner-friendly tasks.

### Feature Ideas
- New voice commands
- Additional language support (AWS Polly voices)
- Sensor integrations (temperature, distance, etc.)
- Better error messages
- Documentation improvements

### Hardware Contributions
If you've built your own TARS and have improvements to the hardware design:
- STL file improvements
- Alternative part suggestions
- Wiring improvements
- New servo configurations

**Important:** Always test hardware changes on a real robot before submitting.

## What NOT to Do

- Don't change servo angles or movement timing without testing on real hardware
- Don't hardcode API keys or secrets — use `.env`
- Don't add large binary files (images, videos, compiled binaries)
- Don't add dependencies without discussing in an issue first
- Don't reformat code you didn't change (keeps diffs clean)

## Reporting Bugs

Use the [Bug Report template](https://github.com/DhruvGoswami10/TARS-WIZARD/issues/new?template=bug_report.md) and include:
1. What you expected to happen
2. What actually happened
3. Steps to reproduce
4. Your setup (Pi model, OS version, Python version)

## Questions?

Open a [Discussion](https://github.com/DhruvGoswami10/TARS-WIZARD/discussions) or reach out via the project's social links.
