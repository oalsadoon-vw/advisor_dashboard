#!/bin/bash
# Quick start script for Streamlit dashboard

echo "🚀 Starting Advisor Satisfaction Dashboard (Streamlit)..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit is not installed."
    echo "📦 Installing Streamlit..."
    pip install streamlit
    echo ""
fi

# Run the app
echo "✅ Starting dashboard on http://localhost:8501"
echo "📊 Press Ctrl+C to stop the server"
echo ""

streamlit run streamlit_app.py

