# VideoSynthesis - Quick Start Guide

## For Developers

### 1. Setup

```bash
# Clone/download the project
cd VideoSynthesis

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### 2. First Launch

1. **Settings Tab** → Download FFmpeg (~120 MB)
2. **Settings Tab** → Select Whisper model and download (150 MB - 3 GB)
3. Ready to use!

### 3. Typical Workflow

**Option A: Download from URL**
1. **Download Video** → Paste URL → Download
2. Automatically switches to **Video to Text** → Transcribe
3. Automatically switches to **Synthesis** → Enter API key → Generate

**Option B: Local File**
1. **Video to Text** → Browse file → Transcribe
2. **Synthesis** → Text auto-fills → Enter API key → Generate

### 4. Building Executable

```bash
pip install pyinstaller
python build.py
```

Output: `dist/VideoSynthesis.exe` (~400 MB)

## For End Users

### Installation

1. Download `VideoSynthesis.exe`
2. Run it (Windows may show a warning - click "More info" → "Run anyway")
3. First launch: Go to Settings and download requirements

### Getting API Keys

- **Claude**: https://console.anthropic.com/ ($0.01-0.05 per 2h video)
- **OpenAI**: https://platform.openai.com/ ($0.02-0.10 per 2h video)
- **Gemini**: https://makersuite.google.com/ ($0.01-0.03 per 2h video)
- **DeepSeek**: https://platform.deepseek.com/ ($0.001-0.01 per 2h video)

### Troubleshooting

**"Missing requirements"**
→ Go to Settings tab and download FFmpeg and Whisper

**Transcription is slow**
→ Normal! A 1-hour video takes 10-30 minutes depending on model
→ Use "base" model for faster results

**Download fails**
→ Some videos are private/protected
→ Try a different URL

**API error**
→ Check your API key is correct
→ Verify you have credits/quota

### Performance Tips

- **Base model**: Fast, good for most videos (recommended)
- **Medium model**: Better accuracy, 2x slower
- **Large model**: Best accuracy, 3x slower

GPU users: Automatically faster if CUDA is available

## Common Questions

**Q: Is my data safe?**  
A: Yes! Transcription happens 100% locally. Only the transcribed text is sent to APIs for summary generation.

**Q: Can I use it offline?**  
A: Partially. Download and transcription work offline. Synthesis requires internet (API calls).

**Q: How much does it cost?**  
A: The app is free. You only pay for API usage (typically $0.01-0.10 per 2-hour video).

**Q: Why is the download slow?**  
A: First launch downloads FFmpeg (120 MB) and Whisper model (150 MB - 3 GB). This happens once.

**Q: Can I transcribe multiple videos?**  
A: Yes! Transcribe as many as you want. Each video is independent.

## Support

- Check logs: `%APPDATA%/VideoSynthesis/app.log`
- Website: https://javed.fr
- For technical issues, include the log file when asking for help
