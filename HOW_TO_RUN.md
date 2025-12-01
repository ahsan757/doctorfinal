# How to Run Doctor AI

## Quick Steps

### 1. Make sure MongoDB is running
```powershell
# If MongoDB is installed as a service
net start MongoDB

# Or run manually
mongod
```

### 2. Open the frontend
Simply open this file in your browser:
```
d:\doctor\frontend\index.html
```

Or right-click on `frontend/index.html` and select "Open with" → Your browser (Chrome, Firefox, Edge, etc.)

### 3. Start the backend (in a separate terminal)
```powershell
cd d:\doctor
python main.py
```

The backend will start at: http://localhost:8000

## What You'll See

1. **Frontend**: A beautiful dark-themed chat interface will open
2. **Backend**: Terminal will show "INFO: Uvicorn running on http://0.0.0.0:8000"

## Testing the Chat

1. Type a message like: "I have a headache and fever"
2. The AI will ask follow-up questions
3. After answering, it will provide a diagnosis
4. Say "yes" to get doctor recommendations near you

## Troubleshooting

**If you get "Connection Error":**
- Make sure the backend is running (`python main.py`)
- Check that MongoDB is running

**If you get "Module not found":**
```powershell
pip install -r requirements.txt
```

**If MongoDB connection fails:**
- Start MongoDB: `net start MongoDB` or `mongod`
- Check `.env` file has correct MongoDB URI

## Project Files

- **Frontend**: `d:\doctor\frontend\index.html` (Open this in browser)
- **Backend**: `d:\doctor\main.py` (Run with Python)
- **Doctors Data**: `d:\doctor\data\doctors.csv` (20 sample doctors)

## API Documentation

Once the backend is running, visit:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

Enjoy your Doctor AI chatbot! 🏥✨
