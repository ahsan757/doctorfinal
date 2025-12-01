# Doctor AI - Quick Start

## ✅ Your Application is RUNNING!

**Backend Server:** http://localhost:8000 ✓  
**Frontend:** file:///D:/doctor/frontend/index.html ✓  
**Database:** MongoDB Connected ✓

## How to Use

### The application is already open in your browser!

1. **Type your symptoms** in the chat box (e.g., "I have a headache and fever")
2. **Answer follow-up questions** from the AI
3. **Get diagnosis** and say "yes" when asked about doctor recommendations
4. **View nearby doctors** with their specializations, hospitals, and distances

### Example Conversation

```
You: I have a headache and fever
AI: How long have you been experiencing these symptoms?
You: About 3 days
AI: Based on your symptoms, you may be experiencing a flu. 
    Would you like me to recommend a specialized doctor?
You: yes
AI: 👨‍⚕️ Here are few nearest doctors specialized for your condition:
    1. Dr. Ahmed Khan - GENERAL PHYSICIAN, Aga Khan University Hospital (0.15 km away)
    2. Dr. Fatima Noor - FAMILY MEDICINE, Ziauddin Hospital (0.23 km away)
    3. Dr. Rashid Mahmood - MEDICINE, Civil Hospital Karachi (0.31 km away)
```

## Features

- 🤖 **AI-Powered Diagnosis** - GPT-3.5 analyzes your symptoms
- 👨‍⚕️ **Doctor Recommendations** - Find specialists near you
- ⚡ **Emergency Detection** - Automatic alerts for critical conditions
- 💬 **Session History** - Your conversations are saved
- 📍 **Location-Based** - Doctors sorted by distance from you

## Stopping the Application

To stop the backend server:
1. Go to the terminal where `python main.py` is running
2. Press `Ctrl + C`

## Restarting Later

To restart the application:
```powershell
# 1. Start MongoDB (if not running)
net start MongoDB

# 2. Start backend
cd d:\doctor
python main.py

# 3. Open frontend
# Open d:\doctor\frontend\index.html in your browser
```

## API Documentation

While the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Project Structure

```
d:\doctor\
├── main.py                 # Backend API (RUNNING)
├── requirements.txt        # Dependencies
├── README.md              # Full documentation
├── HOW_TO_RUN.md          # This guide
├── QUICKSTART.md          # Quick reference
├── .env                   # Configuration
├── .gitignore            # Git ignore rules
├── data/
│   └── doctors.csv       # 20 sample doctors
└── frontend/
    ├── index.html        # Chat interface (OPEN)
    ├── style.css         # Styling
    └── script.js         # Logic
```

## Troubleshooting

**Chat not responding?**
- Check that backend is running (you should see "INFO: Uvicorn running..." in terminal)
- Refresh the browser page

**"Connection Error" message?**
- Make sure MongoDB is running: `net start MongoDB`
- Restart the backend: `python main.py`

**Want to add more doctors?**
- Edit `d:\doctor\data\doctors.csv`
- Add rows with: name, specialization, latitude, longitude, hospital_name

Enjoy your Doctor AI chatbot! 🏥✨
