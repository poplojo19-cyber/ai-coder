name: AI_Backend
on:
  workflow_dispatch:
    inputs:
      file_path:
        required: true
      prompt:
        required: true
jobs:
  run_ai:
    runs-on: ubuntu-latest
    # This explicitly gives the bot permission to edit your files
    permissions:
      contents: write
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4 # Updated to v4 to fix warning

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Run AI Script
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          FILE_PATH: ${{ github.event.inputs.file_path }}
          PROMPT: ${{ github.event.inputs.prompt }}
        run: |
          pip install requests
          python .github/ai.py

      - name: Commit and Push Changes
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git config user.name "AI-Coder-Bot"
          git config user.email "bot@ai-coder.com"
          git add .
          # This line commits only if there are actual changes
          git commit -m "🤖 AI: ${{ github.event.inputs.prompt }}" || echo "No changes to commit"
          git push origin main
