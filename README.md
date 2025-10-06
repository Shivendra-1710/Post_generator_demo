# LinkedIn Post Generator

A professional web application that generates engaging LinkedIn posts using Google's Gemini AI. Perfect for companies wanting to create viral content about their events and announcements.

## Features

- 🤖 AI-powered post generation using Google Gemini
- ✨ Professional formatting with emojis and hashtags
- 🎯 Tailored for company events and announcements
- 📱 Responsive design with Tailwind CSS
- 🔒 Secure API key handling

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

4. Start the backend server:
   ```bash
   uvicorn backend.main:app --reload
   ```

5. Open `frontend/index.html` in your browser

## Usage

1. Enter your company name
2. Describe your event or announcement
3. Click "Generate Post"
4. Copy the generated post to clipboard
5. Share on LinkedIn!

## Tech Stack

- Backend: FastAPI
- AI: Google Gemini
- Frontend: HTML + Tailwind CSS
- Styling: Custom responsive design

## Security Notes

- Store your API key securely in `.env`
- Configure CORS settings for production
- Never expose your API key in client-side code

## License

MIT License
