# GitHub Repository Setup

Status: Public GitHub repository created and initial commits pushed.

This file is for Phase 1 only. Follow these steps after the local repository shell exists.

## Exact Repository Settings

Use these values on GitHub:

- Repository owner: `abdelrahmanfawaz18-cmyk`
- Repository name: `5g-sa-core-protocol-lab`
- Visibility: `Public`
- Description: `Open5GS + UERANSIM 5G SA lab with packet captures, failure scenarios, and Python validation tooling.`

Add these topics after the repository is created:

```text
5g
open5gs
ueransim
telecom
packet-core
wireshark
linux-networking
python
protocol-analysis
network-testing
```

## Create the Public Repository in GitHub

1. Open your web browser.
2. Go to `https://github.com`.
3. Sign in if GitHub asks you to sign in.
4. In the top-right corner, click the `+` button.
5. Click `New repository`.
6. In `Repository name`, type exactly:

```text
5g-sa-core-protocol-lab
```

7. In `Description`, type exactly:

```text
Open5GS + UERANSIM 5G SA lab with packet captures, failure scenarios, and Python validation tooling.
```

8. Under visibility, select `Public`.
9. Do not check `Add a README file`.
10. Do not add a `.gitignore` from GitHub.
11. Do not choose a license yet.
12. Click `Create repository`.

## Connect the Local Repository to GitHub

Open PowerShell.

Run this command to enter the project folder:

```powershell
cd "$HOME\projects\5g-sa-core-protocol-lab"
```

Run this command to connect your local repository to GitHub:

```powershell
git remote add origin https://github.com/abdelrahmanfawaz18-cmyk/5g-sa-core-protocol-lab.git
```

Run this command to push the first commit:

```powershell
git push -u origin main
```

If GitHub asks you to sign in, complete the browser sign-in window, then return to PowerShell.

## Add Repository Topics

After the push succeeds:

1. Go to `https://github.com/abdelrahmanfawaz18-cmyk/5g-sa-core-protocol-lab`.
2. On the right side of the repository page, find the `About` box.
3. Click the gear icon next to `About`.
4. In `Topics`, add each topic listed at the top of this file.
5. Click `Save changes`.

## Completion Gate

Phase 1 is complete only when:

- [x] The GitHub repository page opens successfully.
- [x] The repository is public.
- [x] The README is visible on GitHub.
- [x] The first commit appears on GitHub.
- [x] The repository topics are added.
