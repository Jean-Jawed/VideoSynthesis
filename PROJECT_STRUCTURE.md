# VideoSynthesis - Project Structure

```
VideoSynthesis/
│
├── main.py                      # Main application entry point
├── requirements.txt             # Python dependencies
├── build.py                     # PyInstaller build script
├── README.md                    # Full documentation
├── QUICKSTART.md               # Quick start guide
├── .gitignore                   # Git ignore rules
│
├── ui/                          # User Interface modules
│   ├── __init__.py
│   ├── settings_tab.py         # Settings tab (FFmpeg & Whisper downloads)
│   ├── download_tab.py         # Download video tab
│   ├── videototext_tab.py      # Video to text transcription tab
│   └── synthesis_tab.py        # AI synthesis tab
│
├── core/                        # Core business logic
│   ├── __init__.py
│   ├── downloader.py           # Video/audio downloader (yt-dlp)
│   ├── transcriber.py          # Audio transcription (Whisper)
│   └── synthesizer.py          # Text synthesis (multi-API)
│
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── logger.py               # Application logging
│   ├── ffmpeg_manager.py       # FFmpeg download & management
│   └── whisper_manager.py      # Whisper model management
│
└── assets/                      # Assets (optional)
    └── icon.ico                # Application icon (if available)
```

## Module Descriptions

### main.py
- Application entry point
- Creates main window with CustomTkinter
- Initializes all tabs
- Manages application state
- Handles footer with copyright and website link

### UI Modules

#### settings_tab.py
- Manages FFmpeg download (~120 MB)
- Manages Whisper model download (150 MB - 3 GB)
- Shows installation status
- Provides model selection (base/medium/large)
- Updates global app requirements state

#### download_tab.py
- URL input for video download
- Destination folder selection
- Real-time download logs
- Uses yt-dlp to download audio (mp3)
- Auto-fills path in VideoToText tab

#### videototext_tab.py
- File browser for local audio/video
- Auto-fills from Download tab
- Transcription with progress bar
- Displays transcribed text
- Copy and send to Synthesis options

#### synthesis_tab.py
- Text input (manual or auto-filled)
- API provider selection (Claude/OpenAI/Gemini/DeepSeek)
- API key input (session memory)
- Generates summaries with chunking for long texts
- Copy summary option

### Core Modules

#### downloader.py
- Uses yt-dlp to download videos
- Extracts audio only (mp3)
- Progress callbacks
- Error handling for private/blocked videos
- Threaded downloads

#### transcriber.py
- Uses OpenAI Whisper for transcription
- Loads appropriate model
- Auto-detect language
- Progress callbacks
- Threaded transcription

#### synthesizer.py
- Multi-API support (Claude, OpenAI, Gemini, DeepSeek)
- Smart chunking for long texts (>4000 words)
- Chunk summarization → Final coherent summary
- API-specific implementations
- Error handling

### Utility Modules

#### logger.py
- Configures application logging
- Logs to: %APPDATA%/VideoSynthesis/app.log
- Console output in development
- Timestamped entries

#### ffmpeg_manager.py
- Downloads FFmpeg from GitHub
- Extracts to AppData
- Checks installation status
- Provides FFmpeg path for other modules
- Progress callbacks

#### whisper_manager.py
- Downloads Whisper models
- Checks installation status
- Loads models for transcription
- Supports multiple model sizes

## Data Flow

### Download → Transcribe → Synthesize Flow

```
User enters URL
    ↓
[Download Tab] yt-dlp downloads audio → saves to disk
    ↓
app_state['downloaded_file_path'] = filepath
    ↓
[VideoToText Tab] auto-detects filepath → loads it
    ↓
User clicks Transcribe
    ↓
[Transcriber] Whisper transcribes → returns text
    ↓
app_state['transcribed_text'] = text
    ↓
[Synthesis Tab] auto-detects text → loads it
    ↓
User enters API key → clicks Generate
    ↓
[Synthesizer] chunks text (if long) → calls API → returns summary
    ↓
User copies summary
```

### Application State

Shared state between tabs:
```python
app_state = {
    'requirements': {
        'ffmpeg': bool,       # FFmpeg installed?
        'whisper': bool       # Whisper installed?
    },
    'api_keys': {
        'Claude': str,        # Session-only storage
        'OpenAI': str,
        'Gemini': str,
        'DeepSeek': str
    },
    'downloaded_file_path': str,  # Last downloaded file
    'transcribed_text': str       # Last transcription
}
```

## Threading

All long operations run in separate threads:
- FFmpeg download
- Whisper download
- Video download
- Transcription
- Synthesis

This keeps the UI responsive.

## Error Handling

Each module implements:
- Try/except blocks
- User-friendly error messages
- Logging of technical details
- Callback-based error reporting

## PyInstaller Build

Running `build.py` creates:
- Single .exe file (~300-500 MB)
- No console window (--noconsole)
- Includes all Python dependencies
- Does NOT include: FFmpeg, Whisper models (downloaded on first use)

## Runtime Directories

### Windows
- App data: `%APPDATA%/VideoSynthesis/`
- FFmpeg: `%APPDATA%/VideoSynthesis/ffmpeg.exe`
- Logs: `%APPDATA%/VideoSynthesis/app.log`
- Whisper: `%USERPROFILE%/.cache/whisper/`

### Linux/Mac (Development)
- App data: `~/.VideoSynthesis/`
- Logs: `~/.VideoSynthesis/app.log`
- Whisper: `~/.cache/whisper/`

## Development Workflow

1. **Setup**: `pip install -r requirements.txt`
2. **Run**: `python main.py`
3. **Test**: Download → Transcribe → Synthesize
4. **Build**: `python build.py`
5. **Distribute**: `dist/VideoSynthesis.exe`

## Future Enhancements

Possible additions:
- Multiple language UI
- Dark/light theme toggle
- Batch processing
- Export to PDF/DOCX
- Local LLM support (Ollama)
- Custom synthesis prompts
- Subtitle generation
- Video preview

---

**Copyright © Jawed Tahir 2025**  
Website: https://javed.fr
