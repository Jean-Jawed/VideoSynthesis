# VideoSynthesis

Desktop application for downloading videos, transcribing audio to text, and generating AI-powered summaries.

**Copyright © Jawed Tahir 2025**  
Website: https://jawed.fr

## Features

- 📥 **Download Video**: Download audio from YouTube and other platforms using yt-dlp
- 🎤 **Video to Text**: Transcribe audio/video files using OpenAI Whisper
- 📝 **AI Synthesis**: Generate summaries using Claude, OpenAI, Gemini, or DeepSeek APIs
- 🔒 **Privacy-focused**: All transcription happens locally on your machine
- 💾 **Persistent Settings**: Downloads FFmpeg and Whisper models once, reuses them

## Requirements

### For Development

- Python 3.8 or higher
- pip

### For End Users

- Windows 10 or higher (64-bit)
- Internet connection (for first-time setup and synthesis)
- ~4 GB free disk space (for models)

## Installation (Development)

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## First Launch

On first launch:

1. Go to the **Settings** tab
2. Download **FFmpeg** (~120 MB)
3. Choose and download a **Whisper model**:
   - Base: 150 MB (recommended for most users)
   - Medium: 1.5 GB (better accuracy)
   - Large: 3 GB (best accuracy, slower)

## Usage

### Download Video

1. Go to **Download Video** tab
2. Paste a video URL (YouTube, Vimeo, etc.)
3. Select destination folder
4. Click **Download Audio**
5. The audio file will be automatically loaded in the VideoToText tab

### Transcribe Audio

1. Go to **Video to Text** tab
2. Select an audio/video file (or use the auto-loaded file from Download)
3. Click **Transcribe Audio**
4. Wait for transcription to complete (this may take time for long videos)
5. Copy the text or send it to Synthesis

### Generate Summary

1. Go to **Synthesis** tab
2. Paste text or use auto-loaded transcription
3. Select AI provider (Claude, OpenAI, Gemini, or DeepSeek)
4. Enter your API key
5. Click **Generate Summary**

For long texts (>4000 words), the application automatically:
- Splits text into chunks
- Summarizes each chunk
- Combines summaries into a coherent final summary

## Building Executable

To create a standalone .exe file:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Run the build script:
```bash
python build.py
```

Or manually:
```bash
pyinstaller --onefile --noconsole --name "VideoSynthesis" main.py
```

The .exe will be in the `dist/` folder.

**Note**: The .exe will be ~300-500 MB. FFmpeg and Whisper models are downloaded on first launch.

## API Keys

You'll need API keys for the synthesis feature:

- **Claude**: https://console.anthropic.com/
- **OpenAI**: https://platform.openai.com/api-keys
- **Gemini**: https://makersuite.google.com/app/apikey
- **DeepSeek**: https://platform.deepseek.com/

API keys are stored in memory during your session and cleared when you close the app.

## Troubleshooting

### "FFmpeg not found"
- Make sure you've downloaded FFmpeg in the Settings tab
- Check the log file: `%APPDATA%/VideoSynthesis/app.log`

### "Transcription failed"
- Ensure Whisper model is downloaded
- Check that the audio/video file is not corrupted
- Try a different Whisper model (base is fastest)

### "API error"
- Verify your API key is correct
- Check your API quota/credits
- Ensure you have internet connection

### Download fails
- Some videos may be private or region-locked
- Try a different video URL
- Check your internet connection

## File Locations

### Windows

- **Application Data**: `%APPDATA%/VideoSynthesis/`
- **FFmpeg**: `%APPDATA%/VideoSynthesis/ffmpeg.exe`
- **Whisper Models**: `%USERPROFILE%/.cache/whisper/`
- **Logs**: `%APPDATA%/VideoSynthesis/app.log`

### Linux/Mac (Development)

- **Application Data**: `~/.VideoSynthesis/`
- **Whisper Models**: `~/.cache/whisper/`
- **Logs**: `~/.VideoSynthesis/app.log`

## Performance

Transcription times (approximate, on modern CPU):
- 1-hour video with base model: ~10-15 minutes
- 1-hour video with medium model: ~20-30 minutes
- 1-hour video with large model: ~30-45 minutes

With GPU (CUDA), transcription is 5-10x faster.

## License

Copyright © Jawed Tahir 2025  
All rights reserved.

## Credits

- UI: CustomTkinter
- Transcription: OpenAI Whisper
- Download: yt-dlp
- Audio Processing: FFmpeg

## Support

For issues or questions, check the log file at `%APPDATA%/VideoSynthesis/app.log`

Website: https://jawed.fr
