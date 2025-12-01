from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import openai
import csv
from math import radians, sin, cos, sqrt, atan2
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# FastAPI app
app = FastAPI(
    title="Doctor AI API",
    description="AI-powered medical assistant with doctor recommendations",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration - allow all for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/doctor_ai')
try:
    client = MongoClient(MONGODB_URI)
    db = client['doctor_ai']
    chats_collection = db['chats']
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")

# OpenAI setup
openai.api_key = os.getenv('OPEN_API_SECRET_KEY')

# Pydantic models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation: List[Message] = []
    latitude: float = 0.0
    longitude: float = 0.0
    sessionId: str

class ChatResponse(BaseModel):
    response: str
    conversation: List[Message]

class MessagesResponse(BaseModel):
    messages: List[Dict[str, Any]]

class SessionInfo(BaseModel):
    sessionId: str
    createdAt: datetime

class SessionsResponse(BaseModel):
    sessions: List[SessionInfo]

# Emergency mapping
EMERGENCY_MAP = {
    "heart attack": ["CARDIOLOGIST", "ELECTROPHYSIOLOGIST", "HEART FAILURE"],
    "chest pain": ["CARDIOLOGIST", "ELECTROPHYSIOLOGIST", "HEART FAILURE"],
    "stroke": ["NEUROLOGIST", "PAEDIATRIC NEUROLOGIST"],
    "shortness of breath": ["PULMONOLOGIST", "CARDIOLOGIST"],
    "difficulty breathing": ["PULMONOLOGIST", "CARDIOLOGIST"],
    "loss of consciousness": ["NEUROLOGIST", "PAEDIATRIC NEUROLOGIST", "EMERGENCY MEDICINE"],
    "seizures": ["NEUROLOGIST", "PAEDIATRIC NEUROLOGIST"],
}

# Diagnosis to specialization mapping
DIAGNOSIS_TO_SPECIALIZATIONS = {
    "cold": ["GENERAL PHYSICIAN", "MEDICINE", "FAMILY MEDICINE"],
    "flu": ["GENERAL PHYSICIAN", "MEDICINE", "FAMILY MEDICINE"],
    "respiratory infection": ["GENERAL PHYSICIAN", "MEDICINE", "INFECTIOUS DISEASES"],
    "bronchitis": ["PULMONOLOGIST", "GENERAL PHYSICIAN"],
    "pneumonia": ["PULMONOLOGIST", "INFECTIOUS DISEASES"],
    "asthma": ["PULMONOLOGIST", "ALLERGY CLINIC"],
    "diabetes": ["ENDOCRINOLOGIST", "GENERAL PHYSICIAN"],
    "hypertension": ["CARDIOLOGIST", "GENERAL PHYSICIAN"],
    "migraine": ["NEUROLOGIST"],
    "headache": ["NEUROLOGIST", "GENERAL PHYSICIAN"],
    "depression": ["PSYCHIATRIST", "PSYCHOLOGIST"],
    "anxiety": ["PSYCHIATRIST", "PSYCHOLOGIST"],
}


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


def load_doctors_from_csv():
    """Load doctors from CSV file"""
    doctors = []
    csv_path = 'data/doctors.csv'
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                doctors.append({
                    'name': row['name'].strip(),
                    'specialization': row['specialization'].strip(),
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'hospital': row['hospital_name'].strip()
                })
        logger.info(f"Loaded {len(doctors)} doctors from CSV")
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
    
    return doctors


def match_doctors(doctors, specs, lat=None, lng=None, limit=3):
    """Match doctors based on specialization and location"""
    spec_set = {s.lower() for s in specs}
    matches = []
    
    for doc in doctors:
        if doc['specialization'].lower() in spec_set:
            distance = None
            if lat is not None and lng is not None:
                distance = haversine_distance(lat, lng, doc['latitude'], doc['longitude'])
            matches.append({**doc, 'distance': distance})
    
    matches.sort(key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))
    return matches[:limit]


def is_followup_question(content):
    """Check if message is a follow-up question"""
    phrases = [
        "how long", "can you describe", "are you experiencing",
        "any other symptoms", "please tell me more", "could you specify"
    ]
    return any(phrase in content.lower() for phrase in phrases)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Doctor AI API is running",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with AI medical assistant"""
    try:
        latitude = request.latitude
        longitude = request.longitude
        message = request.message.strip()
        conversation = [msg.dict() for msg in request.conversation]
        session_id = request.sessionId
        
        if not message:
            raise HTTPException(status_code=400, detail='Message is required')
        
        logger.info(f"Chat request from session {session_id}")
        
        # Count follow-up questions
        followup_count = sum(
            1 for msg in conversation 
            if msg['role'] == 'assistant' and is_followup_question(msg['content'])
        )
        
        # If 2+ follow-ups, provide diagnosis
        if followup_count >= 2:
            diagnosis_prompt = {
                'role': 'system',
                'content': 'You are Doctor AI, a medical assistant. Based on previous conversation, give a brief possible diagnosis and ask if the user wants doctor recommendation.'
            }
            
            messages = [diagnosis_prompt] + conversation + [{'role': 'user', 'content': message}]
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=400,
                temperature=0.7
            )
            
            diagnosis_reply = response.choices[0].message.content.strip()
            conversation.append({'role': 'user', 'content': message})
            conversation.append({'role': 'assistant', 'content': diagnosis_reply})
            
            # Save to database
            chats_collection.update_one(
                {'sessionId': session_id},
                {
                    '$push': {
                        'messages': {
                            '$each': [
                                {'sender': 'user', 'type': 'text', 'text': message},
                                {'sender': 'bot', 'type': 'text', 'text': diagnosis_reply}
                            ]
                        }
                    },
                    '$setOnInsert': {'createdAt': datetime.now()}
                },
                upsert=True
            )
            
            return ChatResponse(response=diagnosis_reply, conversation=[Message(**m) for m in conversation])
        
        # Main AI response
        system_prompt = {
            'role': 'system',
            'content': '''You are Doctor AI, a helpful virtual healthcare assistant.

Rules:
1. Based on user symptoms, identify possible medical conditions.
2. If symptoms are unclear, ask 1-2 follow-up questions.
3. If the condition is clear, immediately say: "Based on your symptoms, you may be experiencing X. Would you like me to recommend a specialized doctor?"
4. If it's critical (heart attack, stroke, chest pain), say: "⚠️ This could be a medical emergency. Please seek immediate help."
5. Do NOT list doctor names yourself.
6. Be brief, clear, and avoid non-medical topics.'''
        }
        
        messages = [system_prompt] + conversation + [{'role': 'user', 'content': message}]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=400,
            temperature=0.7
        )
        
        ai_reply = response.choices[0].message.content.strip()
        conversation.append({'role': 'user', 'content': message})
        conversation.append({'role': 'assistant', 'content': ai_reply})
        
        lower_reply = ai_reply.lower()
        user_message_lower = message.lower()
        
        # Check for critical keywords
        critical_keywords = ["heart attack", "stroke", "chest pain"]
        is_critical = any(term in lower_reply or term in user_message_lower for term in critical_keywords)
        
        if is_critical:
            matched_specs = set()
            for keyword, specs in EMERGENCY_MAP.items():
                if keyword in lower_reply or keyword in user_message_lower:
                    matched_specs.update(specs)
            
            all_doctors = load_doctors_from_csv()
            matched_doctors = match_doctors(all_doctors, list(matched_specs), latitude, longitude, 3)
            
            if matched_doctors:
                suggestion = "\n\n👨‍⚕️ Since this might be critical, here are few nearest specialized doctors:\n"
                for i, doc in enumerate(matched_doctors, 1):
                    name = doc['name'] if doc['name'].lower().startswith('dr.') else f"Dr. {doc['name']}"
                    distance_str = f"{doc['distance']:.2f}" if doc['distance'] else 'N/A'
                    suggestion += f"{i}. {name} - {doc['specialization']}, {doc['hospital']} ({distance_str} km away)\n"
                
                chats_collection.update_one(
                    {'sessionId': session_id},
                    {
                        '$push': {
                            'messages': {
                                '$each': [
                                    {'sender': 'user', 'type': 'text', 'text': message},
                                    {'sender': 'bot', 'type': 'doctor-suggestion', 'text': ai_reply + suggestion}
                                ]
                            }
                        },
                        '$setOnInsert': {'createdAt': datetime.now()}
                    },
                    upsert=True
                )
                
                return ChatResponse(
                    response=ai_reply + suggestion, 
                    conversation=[Message(**m) for m in conversation]
                )
        
        # Check for user wanting doctor recommendation
        yes_words = ["yes", "yeah", "yep", "please", "sure", "ok", "okay"]
        if any(word in user_message_lower for word in yes_words):
            diagnosis = None
            for msg in reversed(conversation):
                if msg['role'] == 'assistant':
                    content_lower = msg['content'].lower()
                    if 'based on your symptoms' in content_lower:
                        start = content_lower.index('based on your symptoms') + len('based on your symptoms')
                        diagnosis = content_lower[start:].split('.')[0].strip()
                        break
            
            matched_specs = set()
            if diagnosis:
                for key, specs in DIAGNOSIS_TO_SPECIALIZATIONS.items():
                    if key in diagnosis:
                        matched_specs.update(specs)
            
            all_doctors = load_doctors_from_csv()
            matched_doctors = match_doctors(all_doctors, list(matched_specs), latitude, longitude, 3)
            
            if matched_doctors:
                suggestion = "\n\n👨‍⚕️ Here are few nearest doctors specialized for your condition:\n"
                for i, doc in enumerate(matched_doctors, 1):
                    name = doc['name'] if doc['name'].lower().startswith('dr.') else f"Dr. {doc['name']}"
                    distance_str = f"{doc['distance']:.2f}" if doc['distance'] else 'N/A'
                    suggestion += f"{i}. {name} - {doc['specialization']}, {doc['hospital']} ({distance_str} km away)\n"
                
                chats_collection.update_one(
                    {'sessionId': session_id},
                    {
                        '$push': {
                            'messages': {
                                '$each': [
                                    {'sender': 'user', 'type': 'text', 'text': message},
                                    {'sender': 'bot', 'type': 'doctor-suggestion', 'text': suggestion}
                                ]
                            }
                        },
                        '$setOnInsert': {'createdAt': datetime.now()}
                    },
                    upsert=True
                )
                
                return ChatResponse(
                    response=suggestion, 
                    conversation=[Message(**m) for m in conversation]
                )
        
        # Save normal conversation
        chats_collection.update_one(
            {'sessionId': session_id},
            {
                '$push': {
                    'messages': {
                        '$each': [
                            {'sender': 'user', 'type': 'text', 'text': message},
                            {'sender': 'bot', 'type': 'text', 'text': ai_reply}
                        ]
                    }
                },
                '$setOnInsert': {'createdAt': datetime.now()}
            },
            upsert=True
        )
        
        return ChatResponse(
            response=ai_reply, 
            conversation=[Message(**m) for m in conversation]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/loadchat", response_model=MessagesResponse)
async def load_chat(sessionId: str = Query(..., description="Session ID to load chat history")):
    """Load chat history for a specific session"""
    try:
        if not sessionId:
            raise HTTPException(status_code=400, detail='Session ID is required')
        
        chat = chats_collection.find_one({'sessionId': sessionId})
        
        if not chat:
            return MessagesResponse(messages=[])
        
        return MessagesResponse(messages=chat.get('messages', []))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions", response_model=SessionsResponse)
async def get_sessions():
    """Get all chat sessions"""
    try:
        sessions = list(chats_collection.find(
            {}, 
            {'sessionId': 1, '_id': 0, 'createdAt': 1}
        ).sort('createdAt', -1))
        
        return SessionsResponse(sessions=[SessionInfo(**s) for s in sessions])
        
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)