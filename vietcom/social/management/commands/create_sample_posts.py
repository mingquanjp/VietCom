from django.core.management.base import BaseCommand
from social.models import Post
from users.models import User
import random

class Command(BaseCommand):
    help = 'Create sample posts for testing'

    def handle(self, *args, **options):
        # Sample content for posts
        sample_contents = [
            "What a beautiful day today! 🌞",
            "Just finished breakfast, it was delicious! 🍳",
            "Working remotely from a super chill cafe ☕",
            "It's weekend, anyone want to hang out? 🎉",
            "Just watched an amazing movie, highly recommend! 🎬",
            "Learned a new skill today 📚",
            "Finished my workout, feeling energized! 💪",
            "Cooking for the family, anyone want to join? 🍲",
            "Took a beautiful photo at the park 📸",
            "Listening to music and relaxing 🎵",
            "Met an old friend, so happy! 👥",
            "Reading an amazing book, can't put it down 📖",
            "It's raining today, staying home and watching movies 🌧️",
            "Had a wonderful day trip! ✈️",
            "Learning to cook a new dish, anyone want to try? 👨‍🍳"
        ]
        
        sample_locations = [
            "Hanoi",
            "Ho Chi Minh City", 
            "Da Nang",
            "Hoi An",
            "Sapa",
            "Nha Trang",
            "Phu Quoc",
            "Ha Long",
            "Hue",
            "Can Tho"
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
