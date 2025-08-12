from django.core.management.base import BaseCommand
from users.models import User
import random

class Command(BaseCommand):
    help = 'Create sample users for testing nearby functionality'

    def handle(self, *args, **options):
        # Sample data
        sample_users = [
            {
                'email': 'user1@example.com',
                'phone': '0901234567',
                'full_name': 'Nguyen Van A',
                'hometown': 'Ho Chi Minh City',
                'gender': 'male',
                'bio': 'Tôi là một developer yêu thích công nghệ',
                'latitude': 10.7769,
                'longitude': 106.7009,
                'status': 'online'
            },
            {
                'email': 'user2@example.com',
                'phone': '0902345678',
                'full_name': 'Tran Thi B',
                'hometown': 'Ho Chi Minh City',
                'gender': 'female',
                'bio': 'Tôi thích du lịch và khám phá những điều mới',
                'latitude': 10.7829,
                'longitude': 106.6933,
                'status': 'online'
            },
            {
                'email': 'user3@example.com',
                'phone': '0903456789',
                'full_name': 'Le Van C',
                'hometown': 'Hanoi',
                'gender': 'male',
                'bio': 'Đam mê âm nhạc và thể thao',
                'latitude': 10.7756,
                'longitude': 106.7019,
                'status': 'away'
            },
            {
                'email': 'user4@example.com',
                'phone': '0904567890',
                'full_name': 'Pham Thi D',
                'hometown': 'Da Nang',
                'gender': 'female',
                'bio': 'Yêu thích nấu ăn và làm bánh',
                'latitude': 10.7812,
                'longitude': 106.6956,
                'status': 'online'
            },
            {
                'email': 'user5@example.com',
                'phone': '0905678901',
                'full_name': 'Hoang Van E',
                'hometown': 'Ho Chi Minh City',
                'gender': 'male',
                'bio': 'Chuyên gia marketing digital',
                'latitude': 10.7785,
                'longitude': 106.7043,
                'status': 'busy'
            }
        ]

        created_count = 0
        for user_data in sample_users:
            if not User.objects.filter(email=user_data['email']).exists():
                user = User.objects.create_user(
                    email=user_data['email'],
                    phone=user_data['phone'],
                    full_name=user_data['full_name'],
                    password='123456789'
                )
                user.hometown = user_data['hometown']
                user.gender = user_data['gender']
                user.bio = user_data['bio']
                user.latitude = user_data['latitude']
                user.longitude = user_data['longitude']
                user.status = user_data['status']
                user.level = random.randint(1, 5)
                user.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {user.full_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'User already exists: {user_data["email"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} users!')
        )
