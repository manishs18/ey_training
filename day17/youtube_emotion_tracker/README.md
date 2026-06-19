# YouTube Emotion Analysis Tool

[cite_start]An automated utility to analyze multi-modal human emotions in YouTube videos and Shorts using the Hume.ai API[cite: 2, 3].

## 🔄 Execution Workflow

1. [cite_start]**Download Phase:** The tool takes a public YouTube URL and uses `yt-dlp` to download the video into a local directory[cite: 4, 41].
2. [cite_start]**API Dispatch:** The local file is prepared and uploaded asynchronously to the Hume.ai server infrastructure[cite: 5, 55, 56].
3. [cite_start]**Remote Processing:** Hume's servers run active AI evaluation models (`face`, `prosody`, `burst`, `language`) on the stream[cite: 39, 41].
4. [cite_start]**Polling loop:** The script continuously queries (`polls`) the Hume API for completion using the unique `Job ID`[cite: 61, 131].
5. [cite_start]**Output Generation:** Once completed, results are parsed and printed directly to your console, or saved down as a localized JSON record[cite: 6, 41].

## ⚙️ Setup & Execution

### 1. Set API Key
[cite_start]Get your key from beta.hume.ai and export it[cite: 8, 9, 12]:
* [cite_start]**macOS/Linux:** `export HUME_API_KEY="your_actual_api_key"` [cite: 21, 22]
* [cite_start]**Windows (PowerShell):** `$env:HUME_API_KEY = "your_actual_api_key"` [cite: 23, 24]

### 2. Install Packages
```bash
pip install -r requirements.txt