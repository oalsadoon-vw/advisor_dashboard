# 🚀 Streamlit Quick Start

## Run Locally (2 steps)

```bash
# 1. Install Streamlit
pip install streamlit

# 2. Run the app
streamlit run streamlit_app.py
```

**Open:** http://localhost:8501

---

## Deploy to Cloud (FREE - 3 steps)

### 1️⃣ Push to GitHub
```bash
git add streamlit_app.py advisor_layout.py advisor_layout_component/ requirements.txt
git commit -m "Add Streamlit version"
git push
```

### 2️⃣ Go to Streamlit Cloud
Visit: **https://share.streamlit.io**

### 3️⃣ Deploy
- Sign in with GitHub
- Click "New app"
- Select your repository
- Main file: `streamlit_app.py`
- Click "Deploy"

**Done!** Your app will be live at: `https://your-app.streamlit.app`

---

## Usage

### Upload Page
1. Click "📤 Upload"
2. Drop your `.xlsx` file
3. Wait for processing
4. Redirected to dashboard

### Dashboard
- View advisor leaderboard
- Click ▸ to expand advisor details
- 🥇 Gold / 🥈 Silver / 🥉 Bronze ranks
- Circular progress for percentages

---

## Files Created

✅ `streamlit_app.py` - Main dashboard
✅ `advisor_layout.py` - Shared card layout and preference storage
✅ `advisor_layout_component/` - Drag and keyboard layout editor
✅ `requirements.txt` - Just needs `streamlit`
✅ `.streamlit/config.toml` - Dark theme configuration
✅ `run_streamlit.sh` - Quick start script for Mac/Linux
✅ `STREAMLIT_README.md` - Full documentation
✅ `STREAMLIT_MIGRATION_GUIDE.md` - Comparison with original

---

## Need Help?

📖 **Full Docs:** See `STREAMLIT_README.md`
🔄 **Migration Guide:** See `STREAMLIT_MIGRATION_GUIDE.md`
🌐 **Streamlit Cloud:** https://docs.streamlit.io/streamlit-community-cloud

---

## That's It! 🎉

Your dashboard is now ready for Streamlit Cloud deployment!

### Arrange advisor cards

Click **Edit cards** beside Advisors. The editor previews the highest-ranked advisor: drag cards to reorder them, or move a metric from **Expanded details** into the first four **Collapsed view** positions. The arrow buttons and Alt + arrow keys on a drag handle provide the same controls without dragging.

Choose **Save for all advisors** to apply the layout to every advisor. **Cancel** discards the preview; **Reset default** restores the original order in the preview until saved. Each advisor keeps their own metric values. Layout preferences are saved separately in `storage/advisor_layout.json` and reload when the app restarts. Keep `advisor_layout.py` and the `advisor_layout_component` directory beside `streamlit_app.py` when deploying; no frontend build or extra dependency is required.

Run regression checks with `python -m unittest discover -s tests -v` (after installing `requirements.txt`) and `node --test advisor_layout_component/editor.test.cjs`.
