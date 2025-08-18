# 🌏 VietCom - Kết nối cộng đồng người Việt tại Nhật Bản

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Django: 4.2](https://img.shields.io/badge/Django-4.2-brightgreen.svg)](https://www.djangoproject.com/)

**VietCom** là nền tảng kết nối người Việt sống tại Nhật Bản thông qua tính năng định vị địa lý, giúp tạo lập cộng đồng offline trong phạm vi gần (5-9km). Ứng dụng tích hợp SNS, chat real-time và hệ thống gamification để tăng tương tác.

**Demo trực tiếp**: [https://vietcom.onrender.com](https://vietcom.onrender.com)  
**Video demo**: [Youtube](#) (link tùy chỉnh)

---

## 📌 Mục lục
- [Tính năng nổi bật](#-tính-năng-nổi-bật)
- [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [Cài đặt & Triển khai](#-cài-đặt--triển-khai)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [API Endpoints](#-api-endpoints)
- [Tác giả](#-tác-giả)
- [Giấy phép](#-giấy-phép)

---

## ✨ Tính năng nổi bật

| Chức năng               | Mô tả                                                                                     |
|--------------------------|------------------------------------------------------------------------------------------|
| **📍 Kết nối địa phương** | Tìm kiếm người Việt trong bán kính 5-9km (tùy level) bằng bản đồ tương tác.              |
| **💬 Chat real-time**     | Nhắn tin 1-1 với WebSocket, hỗ trợ thông báo push.                                       |
| **📱 SNS tích hợp**       | Đăng bài, like, comment, chia sẻ với giao diện 2 cột.                                    |
| **🎮 Gamification**       | Hệ thống level/point (ví dụ: Level 2 mở khóa bán kính 7km).                              |
| **🎯 Quản lý sự kiện**    | Tạo và tham gia event offline (tiệc BBQ, giao lưu văn hóa).                              |

---

## 🛠 Công nghệ sử dụng

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

### **Triển khai**
- ![Render](https://img.shields.io/badge/Render-46E3B7?logo=render&logoColor=white)
- ![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)

---

## 🚀 Cài đặt & Triển khai

### **Yêu cầu hệ thống**
- Python 3.10+
- PostgreSQL 14+
- Redis (cho WebSocket)

### **Cài đặt local**
```bash
# Clone repository
git clone https://github.com/your_username/vietcom.git
cd vietcom

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình biến môi trường (tạo file .env)
cp .env.example .env
# Sửa thông tin database trong .env

# Chạy migrations
python manage.py migrate

# Khởi động server
python manage.py runserver
