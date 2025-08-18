# 🌏 VietCom - Connect Vietnamese Communities Abroad

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Django: 4.2](https://img.shields.io/badge/Django-4.2-brightgreen.svg)](https://www.djangoproject.com/)

**VietCom** is a location-based social platform designed to help Vietnamese people living abroad (initially in Japan) discover and build offline communities within their local areas (5-9km radius). It combines SNS features, real-time chat, and gamification to enhance engagement.

**Live Demo**: [https://vietcom.onrender.com](https://vietcom.onrender.com)  
**Video Demo**: [Youtube](#) (*add your link*)

---

## 📌 Table of Contents
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Contributors](#-contributors)
- [License](#-license)

---

## ✨ Key Features

| Feature                | Description                                                                               |
|------------------------|------------------------------------------------------------------------------------------|
| **📍 Local Discovery**  | Interactive map showing Vietnamese users within a configurable radius (5km/7km/9km by level). |
| **💬 Real-time Chat**  | 1-on-1 messaging with WebSocket support and push notifications.                          |
| **📱 Social Feed**     | Post updates, photos, and interact via likes/comments with a 2-column layout.            |
| **🎮 Gamification**    | Level/point system (e.g., Level 2 unlocks 7km search radius).                            |
| **🎯 Event Management**| Join offline events (meetups, cultural exchanges).                            |

---

## 🛠 Tech Stack

### **Backend**
- ![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
- ![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)
- ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
- ![Django Channels](https://img.shields.io/badge/Django_Channels-46D2B0?logo=django&logoColor=white)

### **Frontend**
- ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
- ![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
- ![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?logo=javascript&logoColor=black)
- ![Geolocation API](https://img.shields.io/badge/Geolocation_API-4285F4?logo=google-maps&logoColor=white)

### **Infrastructure**
- ![Render](https://img.shields.io/badge/Render-46E3B7?logo=render&logoColor=white)
- ![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)

---

## 🚀 Installation

### **Prerequisites**
- Python 3.10+
- PostgreSQL 14+
- Redis (for WebSocket)

### **Local Setup**
```bash
# Clone repository
git clone https://github.com/your_username/vietcom.git
cd vietcom

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit database settings in .env

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```
## Contributors
- [Nguyen Minh Quan](https://github.com/mingquanjp)
- [Imai Momone](https://github.com/nyankororin)
- [Ha Trong Thang](https://github.com/hazeth-htt)
- [Hosoya Moka](https://github.com/sqn7c)
 

