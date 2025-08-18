"""
Script để tạo sample events cho VietCom
"""
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vietcom.settings')
django.setup()

from events.models import Event
from users.models import User

def create_sample_events():
    """Tạo các sự kiện mẫu"""
    
    # Lấy admin user làm creator
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("Không tìm thấy admin user. Vui lòng tạo superuser trước.")
            return
    except Exception as e:
        print(f"Lỗi khi lấy admin user: {e}")
        return
    
    # Sample events data
    events_data = [
        {
            'name': 'Vietnamese Food Festival 2025',
            'description': '''Tham gia lễ hội ẩm thực Việt Nam năm 2025! 
            
🍜 Thưởng thức các món ăn truyền thống như phở, bánh mì, gỏi cuốn
🎭 Xem biểu diễn văn nghệ truyền thống
🎪 Tham gia các trò chơi dân gian
🛍️ Mua sắm các sản phẩm thủ công truyền thống

Đây là cơ hội tuyệt vời để kết nối với cộng đồng người Việt và chia sẻ văn hóa với bạn bè quốc tế!''',
            'time': timezone.now() + timedelta(days=7, hours=10),
            'location_desc': 'Công viên Central Park, Melbourne',
            'max_participants': 100,
            'latitude': -37.8136,
            'longitude': 144.9631,
        },
        {
            'name': 'Language Exchange Meetup',
            'description': '''Buổi gặp mặt trao đổi ngôn ngữ hàng tuần!

🗣️ Luyện tập tiếng Anh với người bản xứ
🇻🇳 Dạy tiếng Việt cho bạn bè quốc tế
☕ Thưởng thức cà phê và trò chuyện
📚 Chia sẻ kinh nghiệm học tập

Mọi level đều được chào đón! Không cần kinh nghiệm, chỉ cần đam mê học hỏi.''',
            'time': timezone.now() + timedelta(days=3, hours=18),
            'location_desc': 'Starbucks Collins Street, Melbourne CBD',
            'max_participants': 30,
            'latitude': -37.8174,
            'longitude': 144.9667,
        },
        {
            'name': 'Mid-Autumn Festival Celebration',
            'description': '''Đón Tết Trung Thu cùng cộng đồng người Việt!

🥮 Thưởng thức bánh trung thu truyền thống
🏮 Làm đèn lồng cho trẻ em
🎭 Xem múa lân và biểu diễn văn nghệ
🌕 Ngắm trăng và kể chuyện cổ tích

Mang theo gia đình và bạn bè để cùng tận hưởng không khí lễ hội!''',
            'time': timezone.now() + timedelta(days=14, hours=17),
            'location_desc': 'Community Hall, Box Hill',
            'max_participants': 80,
            'latitude': -37.8197,
            'longitude': 145.1286,
        },
        {
            'name': 'Career Networking Evening',
            'description': '''Buổi tối networking cho các chuyên gia người Việt!

💼 Kết nối với các chuyên gia trong ngành
📈 Chia sẻ cơ hội việc làm
🎯 Thảo luận về phát triển sự nghiệp
🤝 Xây dựng mạng lưới quan hệ

Phù hợp cho sinh viên và người đi làm muốn phát triển sự nghiệp tại Úc.''',
            'time': timezone.now() + timedelta(days=5, hours=19),
            'location_desc': 'Crown Conference Centre, Southbank',
            'max_participants': 50,
            'latitude': -37.8226,
            'longitude': 144.9589,
        },
        {
            'name': 'Vietnamese Cooking Class',
            'description': '''Học nấu ăn Việt Nam cùng đầu bếp chuyên nghiệp!

👨‍🍳 Học từ đầu bếp người Việt có kinh nghiệm
🍲 Nấu phở, bánh mì, gỏi cuốn, chả cá
📖 Nhận công thức nấu ăn chi tiết
🍽️ Thưởng thức thành quả sau buổi học

Thích hợp cho mọi trình độ, từ người mới bắt đầu đến có kinh nghiệm.''',
            'time': timezone.now() + timedelta(days=10, hours=14),
            'location_desc': 'Vietnam Kitchen Academy, Richmond',
            'max_participants': 20,
            'latitude': -37.8197,
            'longitude': 144.9989,
        },
        {
            'name': 'Vietnamese Student Orientation',
            'description': '''Chào mừng sinh viên Việt Nam mới!

🎓 Hướng dẫn cuộc sống du học tại Úc
🏠 Tìm nhà ở và phòng trọ
💳 Mở tài khoản ngân hàng
🚌 Sử dụng phương tiện công cộng
📚 Tips học tập hiệu quả

Dành cho sinh viên mới đến Úc hoặc chuyển trường.''',
            'time': timezone.now() + timedelta(days=2, hours=10),
            'location_desc': 'University of Melbourne, Union Building',
            'max_participants': 60,
            'latitude': -37.7964,
            'longitude': 144.9612,
        }
    ]
    
    created_count = 0
    
    for event_data in events_data:
        try:
            # Kiểm tra xem event đã tồn tại chưa
            if not Event.objects.filter(name=event_data['name']).exists():
                event = Event.objects.create(
                    creator=admin_user,
                    **event_data
                )
                print(f"✅ Đã tạo sự kiện: {event.name}")
                created_count += 1
            else:
                print(f"⚠️ Sự kiện đã tồn tại: {event_data['name']}")
        except Exception as e:
            print(f"❌ Lỗi khi tạo sự kiện {event_data['name']}: {e}")
    
    print(f"\n🎉 Hoàn thành! Đã tạo {created_count} sự kiện mới.")
    print(f"📊 Tổng cộng có {Event.objects.count()} sự kiện trong hệ thống.")

if __name__ == '__main__':
    create_sample_events()
