# GitHub Workflow Guide

A step-by-step reference for working with branches, pull requests, and merges in TARS-WIZARD.

## The Basic Flow

```
main (stable) ──────────────────────────────────────────────
                \                              /
                 branch (your work) ──────────
                    commit → commit → commit → PR → merge
```

You **never** commit directly to `main`. All changes go through a branch → PR → merge.

---

## 1. Creating a Branch

A branch is a copy of `main` where you make changes without affecting the stable code.

```bash
# Make sure you're on main and up to date
git checkout main
git pull origin main

# Create a new branch
git checkout -b phase/1-cleanup
```

**Naming conventions:**
- `phase/0-setup` — project phases
- `feature/camera-support` — new features
- `fix/voice-timeout` — bug fixes
- `docs/update-readme` — documentation

---

## 2. Making Commits

Commits are checkpoints. Make them small and focused.

```bash
# See what changed
git status
git diff

# Stage specific files (preferred over "git add .")
git add tars/config.py tars/voice/speaker.py

# Commit with a descriptive message
git commit -m "extract shared voice logic into tars/voice/speaker.py"
```

**Good commit messages:**
- `add .env support with python-dotenv`
- `fix weather API using HTTP instead of HTTPS`
- `extract duplicated movement logic into tars/commands/movement.py`

**Bad commit messages:**
- `update stuff`
- `fix bug`
- `WIP`

---

## 3. Pushing to GitHub

Push your branch to the remote repository.

```bash
# First push (sets up tracking)
git push -u origin phase/1-cleanup

# Subsequent pushes
git push
```

---

## 4. Creating a Pull Request

After pushing, go to your repo on GitHub. You'll see a banner:

```
"phase/1-cleanup had recent pushes — Compare & pull request"
```

Click it, then:

1. **Title:** Short summary (under 70 characters)
   - Example: `Phase 1: Deduplicate code and fix bugs`

2. **Description:** Fill out the PR template:
   - What changed and why
   - How you tested it
   - Any hardware testing done

3. Click **"Create pull request"**

---

## 5. Reviewing a PR

Even if you're the only contributor, review your own PRs. It's good practice.

On the PR page:

1. Click the **"Files changed"** tab — shows a diff of all changes
2. **Green lines** = added code
3. **Red lines** = removed code
4. Read through the changes
5. Click on a line number to leave a comment on a specific line
6. When satisfied, go back to the **"Conversation"** tab

---

## 6. Merging

Three merge strategies — when to use each:

### Merge Commit (Default — Recommended)
```
Creates a merge commit that preserves all individual commits.
Best for: Phase branches with multiple meaningful commits.
```
Click **"Merge pull request"** → **"Confirm merge"**

### Squash and Merge
```
Combines all commits into a single commit on main.
Best for: Small PRs or when commit history is messy.
```
Click the dropdown arrow next to merge → **"Squash and merge"**

### Rebase and Merge
```
Replays your commits on top of main (no merge commit).
Best for: Clean, linear history. Avoid if unsure.
```
Click the dropdown arrow → **"Rebase and merge"**

**For TARS-WIZARD phases:** Use **Merge Commit** so each phase's full history is preserved.

---

## 7. After Merging

```bash
# Delete the remote branch (GitHub offers this after merge — click it)

# Back on your local machine:
git checkout main
git pull origin main

# Delete local branch
git branch -d phase/1-cleanup

# Start next phase
git checkout -b phase/2-architecture
```

---

## 8. Branch Protection Rules

Set these up on GitHub to prevent mistakes:

1. Go to: **Settings → Branches → Add rule**
2. Branch name pattern: `main`
3. Check:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass (select the CI workflow)
   - ✅ Require branches to be up to date before merging
4. Click **"Create"**

This prevents anyone (including you) from pushing directly to main.

---

## 9. Handling Merge Conflicts

Conflicts happen when two branches change the same lines.

```bash
# Git will tell you which files conflict
git status
# Shows: "both modified: tars/config.py"

# Open the file — you'll see conflict markers:
<<<<<<< HEAD
your changes
=======
their changes
>>>>>>> branch-name

# Edit the file to keep what you want (remove the markers)
# Then:
git add tars/config.py
git commit -m "resolve merge conflict in config.py"
git push
```

---

## 10. Quick Reference

| Action | Command |
|--------|---------|
| Check current branch | `git branch` |
| Switch to a branch | `git checkout branch-name` |
| Create and switch | `git checkout -b new-branch` |
| See all changes | `git status` |
| See line-level changes | `git diff` |
| Stage files | `git add file1 file2` |
| Commit | `git commit -m "message"` |
| Push | `git push` |
| Pull latest main | `git checkout main && git pull` |
| Delete local branch | `git branch -d branch-name` |
| See commit history | `git log --oneline -10` |

---

## Common Mistakes to Avoid

1. **Committing to main directly** — always use a branch
2. **Force pushing** (`git push --force`) — can delete others' work
3. **Committing `.env` files** — your API keys will be exposed
4. **Giant PRs** — keep them focused. One feature/fix per PR
5. **Not pulling before branching** — always `git pull origin main` first
