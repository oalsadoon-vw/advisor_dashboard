# Advisor Satisfaction Dashboard

Full-screen dashboard for the daily Tekion **Service Employee Rank** Excel export (`.xlsx`).

## Install + Run (TV mode) — the only steps most users need

### 1) Install prerequisites (one-time)

- **Node.js (LTS, 18+)**: download from [nodejs.org](https://nodejs.org/)
- **Python 3**: download from [python.org](https://www.python.org/downloads/)
  - On Windows, during install, make sure **“Add Python to PATH”** is checked if you see it.

Verify they work (open PowerShell and run):

```powershell
node -v
npm -v
python --version
```

### 2) Download this project

Option A (recommended, with Git):

```powershell
git clone https://github.com/Seomzo/Advisor_Satisfaction_Dashboard.git
cd Advisor_Satisfaction_Dashboard
```

Option B (no Git): download the ZIP from GitHub, unzip it, then `cd` into the folder.

### 3) Install the app (one-time)

From the project root (in PowerShell):

```powershell
npm install
```

### 4) Run the dashboard (TV mode) — **one command**

```powershell
npm run tv
```

Open:

- Dashboard: `http://localhost:5179/`
- Upload page: `http://localhost:5179/upload`

Stop the app with **Ctrl + C**.

## Setup (beginner-friendly) — Windows PC / “TV mode”

This section assumes you have **never used the terminal** before. Don’t worry — you can follow it like a recipe.

### What you're installing (prerequisites)

- **Node.js (LTS, 18+)**: runs the dashboard app
- **Python 3**: converts the uploaded `.xlsx` into data the dashboard can read (no extra Python packages needed)
- **Git** (optional, but recommended): lets you download the project with one command

### 1) Install prerequisites (Windows)

#### Install Node.js (LTS)

1) Open your web browser and install **Node.js LTS** from [nodejs.org](https://nodejs.org/).
2) During install, keep the default options.
3) Verify it worked (open PowerShell and run):

```powershell
node -v
npm -v
```

If you see version numbers (like `v20.x.x`), you're good.

#### Install Python 3

1) Install **Python 3** from [python.org](https://www.python.org/downloads/).
2) Important during setup: check the box **“Add Python to PATH”** if you see it.
3) Verify it worked (in PowerShell):

```powershell
python --version
```

If you see `Python 3.x.x`, you're good.

#### Install Git (optional, but recommended)

Install **Git for Windows** from [git-scm.com](https://git-scm.com/downloads), then verify (in PowerShell):

```powershell
git --version
```

> If you don't want Git, you can still download the project as a ZIP (explained below).

### 2) Open PowerShell (where you'll type commands)

A **terminal** is a text window where you type commands and press **Enter**. On Windows, we'll use **PowerShell**.

**How to open PowerShell:**

- **Start Menu** → search **"PowerShell"** → click **Windows PowerShell** (or **PowerShell**)
- Or press **Windows key + X**, then choose **Windows PowerShell**
- Or if you use **VS Code**: open the folder, then **Terminal → New Terminal** (it will open PowerShell by default)

> All commands in this README work in PowerShell. You don't need to install anything else!

### 3) Download the project (choose one option)

#### Option A (recommended): download with Git

In PowerShell, copy/paste these lines (paste, then press Enter after each line):

```powershell
git clone https://github.com/Seomzo/Advisor_Satisfaction_Dashboard.git
cd Advisor_Satisfaction_Dashboard
```

#### Option B: download as ZIP (no Git)

1) Download the repo as a ZIP from GitHub, unzip it
2) Open PowerShell
3) Go into the unzipped folder:

```powershell
cd path\to\Advisor_Satisfaction_Dashboard
```

Tip: if your folder path has spaces, wrap it in quotes:

```powershell
cd "C:\Users\YourName\Downloads\Advisor_Satisfaction_Dashboard"
```

### 4) Install the project dependencies (one-time)

Still in the `Advisor_Satisfaction_Dashboard` folder (in PowerShell), run:

```powershell
npm install
```

This can take a few minutes the first time.

### 5) Build + start (recommended "TV mode": single URL)

Run this command (in PowerShell):

```powershell
npm run tv
```

Leave that PowerShell window open (closing it stops the app).

### 6) Open the dashboard

- Dashboard: `http://localhost:5179/`
- Upload page: `http://localhost:5179/upload`

## How to open multiple terminals on a Windows PC (you need this for “dev mode”)

Sometimes you want **two terminals** (one running the server, one running the website).

### Option A: Windows Terminal tabs (easiest)

1) Open **Windows Terminal**
2) Click the **`+`** button to open a **new tab**
3) Use:
   - one tab for “server”
   - the other tab for “client”

### Option B: Split panes (also good)

In Windows Terminal:

- Press `Alt+Shift+D` (splits the window)
- Or open the dropdown next to the tab bar and choose **Split**

### Option C: VS Code integrated terminals

In VS Code:

- Menu: **Terminal → New Terminal**
- Do it twice to get Terminal 1 and Terminal 2

## Dev mode (runs faster, uses 2 terminals)

From the project folder:

### Option A (recommended): one command

```powershell
npm run dev
```

Open the site at `http://localhost:5173/` (the client proxies API calls to the server).

### Option B: 2 terminals (manual)

#### Terminal 1 (server)

```powershell
npm run dev --workspace server
```

#### Terminal 2 (client)

```powershell
npm run dev --workspace client
```

## Daily workflow

1) Open `http://localhost:5179/upload`
2) Upload today’s Tekion `.xlsx`
3) You’ll be redirected back to the dashboard automatically

## Troubleshooting (common first-time issues)

### “node is not recognized” / “npm is not recognized”

- Node.js isn’t installed, or your terminal didn’t refresh its PATH.
- Fix: install Node.js LTS, then **close and reopen** the terminal and try again.

### “python is not recognized”

- Python isn’t installed, or PATH isn’t set.
- Fix: reinstall Python 3 and make sure **“Add Python to PATH”** is checked, then reopen the terminal.

### “Port 5179 is already in use”

- Something else is using that port.
- Fix: close other copies of the app / terminals, then try again.
