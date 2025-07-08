# Merging the Bloomberg Terminal UI Redesign

This document explains how to merge the `feature/bloomberg-terminal-ui` branch (Bloomberg Terminal UI for financial analysts) into `main`.

## 1. GitHub Pull Request (Recommended)

1. Push your branch to GitHub (if not already):
   ```sh
git push origin feature/bloomberg-terminal-ui
   ```
2. Go to your repository on GitHub.
3. Click the "Compare & pull request" button for `feature/bloomberg-terminal-ui`.
4. Review the changes, add a descriptive PR title and summary (e.g., "Bloomberg Terminal UI redesign for financial analysts").
5. Request reviews if needed, then click "Create pull request".
6. After approval and checks pass, click "Merge pull request".
7. Delete the feature branch if desired.

## 2. GitHub CLI (Command Line)

1. Push your branch to GitHub (if not already):
   ```sh
git push origin feature/bloomberg-terminal-ui
   ```
2. Create a pull request from the CLI:
   ```sh
gh pr create --base main --head feature/bloomberg-terminal-ui --title "Bloomberg Terminal UI redesign" --body "This PR implements a Bloomberg Terminal-inspired UI for financial analysts, including PDF upload and Q&A."
   ```
3. Review and merge the PR via the GitHub web UI or:
   ```sh
gh pr merge --merge
   ```

---

**After merging:**
- Pull the latest `main` branch locally:
  ```sh
git checkout main
git pull origin main
  ```
- Delete the feature branch if desired:
  ```sh
git branch -d feature/bloomberg-terminal-ui
git push origin --delete feature/bloomberg-terminal-ui
  ``` 