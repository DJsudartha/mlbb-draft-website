# GitHub Issue Upload Pack

This folder contains a one-command script to create the project backlog issues in GitHub.

## Files

- `create_issues.sh`: Creates all prepared issues using GitHub CLI (`gh`).

## How to use on your laptop

1. Open a terminal in this repository.
2. Authenticate GitHub CLI (one time):
   ```bash
   gh auth login
   ```
3. Make sure this repo is the current git remote checkout.
4. Run:
   ```bash
   bash project-management/github-issues/create_issues.sh
   ```

The script will create issues for:

- MVP deployment
- Draft evaluator
- Home page/navigation
- Database foundation for future login/profile/dashboard

## Notes

- You can safely re-run after deleting duplicates manually.
- If you want milestone assignment added later, edit the script and add `--milestone` flags.
