from django.core.management.base import BaseCommand
from social.models import Post
from users.models import User
import random

class Command(BaseCommand):
    help = 'Create sample posts for testing'

    def handle(self, *args, **options):
        # Sample content for posts
        sample_contents = [
            "Hôm nay thời tiết thật đẹp! 🌞",
            "Vừa ăn sáng xong, ngon quá! 🍳",
            "Đang làm việc từ xa ở một quán cafe cực chill ☕",
            "Cuối tuần rồi, ai đi chơi không? 🎉",
            "Vừa xem một bộ phim hay lắm, recommend cho mọi người! 🎬",
            "Học được một kỹ năng mới hôm nay 📚",
            "Tập gym xong, cảm thấy tràn đầy năng lượng! 💪",
            "Nấu ăn cho gia đình, ai muốn đến ăn chung không? 🍲",
            "Chụp được một bức ảnh đẹp ở công viên 📸",
            "Đang nghe nhạc và thư giãn 🎵",
            "Gặp được một người bạn cũ, vui quá! 👥",
            "Đọc sách hay lắm, không thể bỏ xuống 📖",
            "Thời tiết hôm nay mưa, ở nhà xem phim thôi 🌧️",
            "Đi du lịch một ngày tuyệt vời! ✈️",
            "Học nấu một món mới, ai muốn thử không? 👨‍🍳"
        ]
        
        sample_locations = [
            "Hà Nội",
            "TP. Hồ Chí Minh", 
            "Đà Nẵng",
            "Hội An",
            "Sapa",
            "Nha Trang",
            "Phú Quốc",
            "Hạ Long",
            "Huế",
            "Cần Thơ"
        ]

        # Get all users
        users = list(User.objects.all())
        
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return

        # Create 20 sample posts
        posts_created = 0
        for i in range(20):
            user = random.choice(users)
            content = random.choice(sample_contents)
            location = random.choice(sample_locations) if random.choice([True, False]) else ""
            
            post = Post.objects.create(
                author=user,
                content=content,
                location=location
            )
            posts_created += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {posts_created} sample posts')
        )
