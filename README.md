# Doctor AI - Medical Assistant

An AI-powered medical assistant that provides symptom analysis, health consultations, and location-based doctor recommendations.

## Features

- 🤖 **AI-Powered Consultations**: Intelligent symptom analysis using OpenAI GPT-3.5
- 👨‍⚕️ **Doctor Recommendations**: Find specialized doctors near your location
- ⚡ **Emergency Detection**: Automatic detection of critical conditions
- 💬 **Conversation History**: Persistent chat sessions with MongoDB
- 📍 **Location-Based**: Distance calculation using geolocation
- 🎨 **Modern UI**: Beautiful glassmorphism design with dark theme

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- OpenAI API (GPT-3.5)
- MongoDB (Database)
- Python 3.8+

**Frontend:**
- Vanilla HTML/CSS/JavaScript
- Modern ES6+ features
- Responsive design

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or cloud instance)
- OpenAI API key

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd doctor
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   
   Edit the `.env` file with your credentials:
   ```env
   MONGODB_URI=mongodb://localhost:27017/doctor_ai
   OPEN_API_SECRET_KEY=your_openai_api_key_here
   ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

   Get your OpenAI API key from: https://platform.openai.com/api-keys

4. **Start MongoDB:**
   
   Make sure MongoDB is running on your system:
   ```bash
   # For local MongoDB
   mongod
   ```

5. **Run the backend server:**
   ```bash
   python main.py
   ```
   
   The API will be available at: http://localhost:8000
   
   API Documentation: http://localhost:8000/docs

6. **Open the frontend:**
   
   Simply open `frontend/index.html` in your web browser, or use a local server:
   ```bash
   # Using Python's built-in server
   cd frontend
   python -m http.server 3000
   ```
   
   Then visit: http://localhost:3000

## Usage

1. **Start a conversation**: Describe your symptoms in the chat interface
2. **Answer follow-up questions**: The AI may ask clarifying questions
3. **Get diagnosis**: After gathering information, the AI provides a possible diagnosis
4. **Find doctors**: Accept the doctor recommendation to see nearby specialists
5. **Emergency cases**: Critical conditions are automatically detected with immediate doctor suggestions

## API Endpoints

### `GET /`
Health check endpoint

### `POST /api/chat`
Send a message to the AI assistant
- **Body**: `{ message, conversation, latitude, longitude, sessionId }`
- **Response**: `{ response, conversation }`

### `GET /api/loadchat?sessionId={id}`
Load chat history for a session

### `GET /api/sessions`
Get all chat sessions

### `GET /api/disclaimer`
Get medical disclaimer

## Project Structure

```
doctor/
├── main.py                 # FastAPI backend
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore rules
├── data/
│   └── doctors.csv       # Doctor database
└── frontend/
    ├── index.html        # Main HTML file
    ├── style.css         # Styles
    └── script.js         # JavaScript logic
```

## Security Notes

- Never commit your `.env` file to version control
- Use environment-specific CORS settings in production
- Rotate your OpenAI API key regularly
- Use HTTPS in production environments

## Medical Disclaimer

⚠️ **Important**: This AI assistant provides general health information only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. In case of emergency, call your local emergency services immediately.

## License

This project is for educational and demonstration purposes.

## Support

For issues or questions, please check the API documentation at `/docs` when the server is running.
"# doctorfinal" 
