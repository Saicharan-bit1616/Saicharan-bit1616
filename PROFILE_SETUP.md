# Profile setup

1. Create a public repository whose name is exactly your GitHub username. GitHub will treat it as your profile README repository.
2. Copy the contents of this folder into that repository.
3. In `README.md`, replace the three placeholder social URLs:
   - `https://github.com/USERNAME`
   - `https://www.linkedin.com/in/USERNAME/`
   - `https://YOUR-PORTFOLIO.example`
4. Commit and push to the `main` branch.
5. Open **Actions → Update Profile Activity → Run workflow** once. The scheduled workflow will refresh the activity visualization every six hours.
6. If your default branch is not `main`, either rename it or update `.github/workflows/update_activity.yml`.

The activity workflow discovers the GitHub username from `github.repository_owner`, so there is no username to hard-code into the Python updater.
