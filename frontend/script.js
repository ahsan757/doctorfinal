// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State Management
let conversation = [];
let sessionId = generateSessionId();
let userLocation = { latitude: 0, longitude: 0 };

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    getUserLocation();
});

function initializeApp() {
    // Load session from localStorage
    const savedSessionId = localStorage.getItem('currentSessionId');
    if (savedSessionId) {
        sessionId = savedSessionId;
        loadChatHistory(sessionId);
    }
}

function setupEventListeners() {
    const sendBtn = document.getElementById('sendBtn');
    const messageInput = document.getElementById('messageInput');
    const newChatBtn = document.getElementById('newChatBtn');

    // Send button click
    sendBtn.addEventListener('click', sendMessage);

    // Enter key to send (Shift+Enter for new line)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    });

    // New chat button
    newChatBtn.addEventListener('click', startNewChat);
}

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation.latitude = position.coords.latitude;
                userLocation.longitude = position.coords.longitude;
                console.log('Location detected:', userLocation);
            },
            (error) => {
                console.warn('Location access denied, using default location');
                // Default to Karachi coordinates
                userLocation.latitude = 24.8607;
                userLocation.longitude = 67.0011;
            }
        );
    } else {
        console.warn('Geolocation not supported');
        userLocation.latitude = 24.8607;
        userLocation.longitude = 67.0011;
    }
}

async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();

    if (!message) return;

    // Hide welcome screen
    const welcomeScreen = document.getElementById('welcomeScreen');
    if (welcomeScreen) {
        welcomeScreen.classList.add('hidden');
    }

    // Add user message to UI
    addMessageToUI('user', message);

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation: conversation,
                latitude: userLocation.latitude,
                longitude: userLocation.longitude,
                sessionId: sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Update conversation
        conversation = data.conversation;

        // Hide typing indicator
        hideTypingIndicator();

        // Add bot response to UI
        const isEmergency = data.response.includes('⚠️') || data.response.includes('emergency');
        const isDoctorSuggestion = data.response.includes('👨‍⚕️');
        addMessageToUI('bot', data.response, isEmergency, isDoctorSuggestion);

        // Save session
        localStorage.setItem('currentSessionId', sessionId);

    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        addMessageToUI('bot', '❌ Sorry, I encountered an error. Please try again later.', false, false);
    }
}

function addMessageToUI(sender, text, isEmergency = false, isDoctorSuggestion = false) {
    const messagesContainer = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    if (isDoctorSuggestion) {
        messageDiv.classList.add('doctor-suggestion');
    }

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';

    const content = document.createElement('div');
    content.className = 'message-content';
    if (isEmergency) {
        content.classList.add('emergency');
    }
    
    // Format text with line breaks
    content.innerHTML = formatMessage(text);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    scrollToBottom();
}

function formatMessage(text) {
    // Convert line breaks to <br>
    let formatted = text.replace(/\n/g, '<br>');
    
    // Make bold text for doctor names and specializations
    formatted = formatted.replace(/Dr\. [A-Za-z\s]+/g, (match) => `<strong>${match}</strong>`);
    
    return formatted;
}

function showTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.classList.add('active');
    scrollToBottom();
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.classList.remove('active');
}

function scrollToBottom() {
    const messagesContainer = document.getElementById('messages');
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 100);
}

function startNewChat() {
    // Clear current chat
    conversation = [];
    sessionId = generateSessionId();
    localStorage.setItem('currentSessionId', sessionId);

    // Clear messages
    const messagesContainer = document.getElementById('messages');
    messagesContainer.innerHTML = '';

    // Show welcome screen
    const welcomeScreen = document.getElementById('welcomeScreen');
    if (welcomeScreen) {
        welcomeScreen.classList.remove('hidden');
    }

    // Clear input
    const messageInput = document.getElementById('messageInput');
    messageInput.value = '';
    messageInput.style.height = 'auto';
}

async function loadChatHistory(sessionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/loadchat?sessionId=${sessionId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.messages && data.messages.length > 0) {
            // Hide welcome screen
            const welcomeScreen = document.getElementById('welcomeScreen');
            if (welcomeScreen) {
                welcomeScreen.classList.add('hidden');
            }

            // Load messages
            data.messages.forEach(msg => {
                const isDoctorSuggestion = msg.type === 'doctor-suggestion';
                const isEmergency = msg.text.includes('⚠️') || msg.text.includes('emergency');
                addMessageToUI(msg.sender === 'user' ? 'user' : 'bot', msg.text, isEmergency, isDoctorSuggestion);
            });

            // Rebuild conversation for API
            for (let i = 0; i < data.messages.length; i += 2) {
                if (data.messages[i] && data.messages[i + 1]) {
                    conversation.push({
                        role: 'user',
                        content: data.messages[i].text
                    });
                    conversation.push({
                        role: 'assistant',
                        content: data.messages[i + 1].text
                    });
                }
            }
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

// Error handling for API connection
window.addEventListener('online', () => {
    console.log('Connection restored');
});

window.addEventListener('offline', () => {
    console.warn('Connection lost');
    addMessageToUI('bot', '⚠️ You appear to be offline. Please check your internet connection.', false, false);
});
