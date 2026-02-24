# Maintaining an Open Source Project

A practical guide for managing TARS-WIZARD as an open source project.

---

## Reviewing Contributor PRs

When someone submits a pull request, here's what to check:

### 1. Read the PR Description
Does it explain what changed and why? If not, ask for more context.

### 2. Review the Code (Files Changed tab)
Look for:
- **Does it work?** — Does the logic make sense?
- **Security** — No hardcoded API keys? No unsafe input handling?
- **Style** — Does it match existing code patterns?
- **Scope** — Is it focused on one thing, or trying to do too much?
- **Tests** — Did they add tests for new functionality?
- **Hardware safety** — If it changes servo code, did they test on real hardware?

### 3. Leave Feedback
- Be specific: "This variable should use snake_case" not "fix the style"
- Be kind: "Nice approach! One suggestion..." not "This is wrong"
- Explain why: "We use config.yaml for settings because..." not just "Move this to config"

### 4. Request Changes or Approve
- **Approve** — everything looks good, merge it
- **Request changes** — leave comments on what needs fixing
- **Comment** — ask questions without blocking the PR

### 5. Merge
Once approved and CI passes, merge using the strategy described in the workflow guide.

---

## Using GitHub Issues

### Labels
Set up these labels on your repo (Settings → Labels):

| Label | Color | Use For |
|-------|-------|---------|
| `bug` | red | Something is broken |
| `enhancement` | blue | New feature requests |
| `good first issue` | green | Beginner-friendly tasks |
| `help wanted` | yellow | Looking for contributors |
| `documentation` | purple | Docs improvements |
| `hardware` | orange | Physical build related |
| `wontfix` | gray | Intentionally not fixing |
| `duplicate` | gray | Already reported |

### Milestones
Group issues by release version:
- **v2.0** — Core upgrade (Phases 0-2)
- **v2.1** — Voice + Camera (Phases 3-4)
- **v2.2** — Dev Tools + Tests (Phases 5-6)
- **v2.3** — OpenClaw (Phase 7)

To create: **Issues → Milestones → New milestone**

### Assigning Issues
- Assign yourself to issues you're actively working on
- Leave unassigned issues open for contributors
- Label beginner-friendly tasks with `good first issue`

---

## Writing Good Issue Responses

### When someone reports a bug:
```
Thanks for reporting this! A few questions to help debug:
1. What Raspberry Pi model are you using?
2. Can you paste the full error message?
3. Are you running main.py or TARSmaster.py?

I'll look into this once I can reproduce it.
```

### When someone requests a feature:
```
Interesting idea! This could work well with the existing
command router. Let me think about the best approach.

If you'd like to take a crack at implementing it, the
relevant code is in tars/commands/router.py.
```

### When closing an issue:
```
Fixed in #42. This will be included in the next release.
Thanks for reporting!
```
or:
```
Closing this as a duplicate of #15. The discussion continues there.
```

---

## When to Close vs Keep Open

**Close when:**
- Fixed by a merged PR
- Duplicate of another issue
- Not reproducible after asking for more info
- Out of scope for the project
- Stale (no response after 30+ days)

**Keep open when:**
- Valid bug that hasn't been fixed yet
- Feature request that the community wants
- Good first issue for new contributors

---

## Managing Releases

### When to Release
- After each major phase is merged and stable
- When a critical bug fix is ready

### How to Create a Release

1. Go to: **Releases → Draft a new release**
2. Click **"Choose a tag"** → type `v2.0.0` → **"Create new tag"**
3. **Title:** `v2.0.0 — Unified Architecture`
4. **Description:** Summarize what changed (can auto-generate from PRs)
5. Click **"Publish release"**

### Version Numbering (Semantic Versioning)
- `v2.0.0` — Major: breaking changes or complete overhaul
- `v2.1.0` — Minor: new features, backwards compatible
- `v2.1.1` — Patch: bug fixes only

---

## GitHub Discussions

Enable Discussions for community Q&A (separate from Issues):

1. Go to: **Settings → Features → Discussions → Enable**
2. Categories to create:
   - **Q&A** — "How do I..." questions
   - **Show & Tell** — People showing their TARS builds
   - **Ideas** — Feature discussions before they become issues
   - **Help** — Troubleshooting

This keeps Issues clean for actual bugs and tracked features.

---

## Code of Conduct

Consider adding a `CODE_OF_CONDUCT.md` (GitHub has a template):

1. Go to: **Add file → Create new file**
2. Name it `CODE_OF_CONDUCT.md`
3. GitHub will suggest the Contributor Covenant template
4. Customize and commit

The basic rules:
- Be respectful and constructive
- No harassment or discrimination
- Focus on what's best for the community
- Welcome newcomers

---

## Quick Checklist for Maintainers

When a new PR comes in:
- [ ] Read the description
- [ ] Review the code diff
- [ ] Check that CI passes (green checkmark)
- [ ] Test locally if it's a significant change
- [ ] Leave feedback or approve
- [ ] Merge and delete the branch
- [ ] Close related issues

When a new issue comes in:
- [ ] Add appropriate labels
- [ ] Assign to a milestone if applicable
- [ ] Respond within a few days
- [ ] Assign to someone or label as `help wanted`
