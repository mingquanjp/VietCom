from django.core.management.base import BaseCommand
from gamification.models import Mission

class Command(BaseCommand):
    help = 'Create default mission data'

    def handle(self, *args, **options):
        missions_data = [
            # Basic missions
            {
                'title': 'Welcome to VietCom!',
                'description': 'First login to the system',
                'mission_type': 'first_login',
                'target_count': 1,
                'points_reward': 5,
                'frequency': 'once',
                'icon': '👋',
                'order': 1
            },
            {
                'title': 'Complete Profile',
                'description': 'Update full personal information (name, birthday, gender, bio)',
                'mission_type': 'complete_profile',
                'target_count': 1,
                'points_reward': 10,
                'frequency': 'once',
                'icon': '📝',
                'order': 2
            },
            {
                'title': 'Upload Avatar',
                'description': 'Upload profile picture for your account',
                'mission_type': 'upload_avatar',
                'target_count': 1,
                'points_reward': 5,
                'frequency': 'once',
                'icon': '📸',
                'order': 3
            },
            
            # Friend missions
            {
                'title': 'First Friend',
                'description': 'Connect with 1 other user',
                'mission_type': 'add_friend',
                'target_count': 1,
                'points_reward': 5,
                'frequency': 'once',
                'icon': '👥',
                'order': 4
            },
            {
                'title': 'Expand Network',
                'description': 'Connect with 3 users',
                'mission_type': 'add_friend',
                'target_count': 3,
                'points_reward': 10,
                'frequency': 'once',
                'icon': '🤝',
                'order': 5
            },
            {
                'title': 'Build Community',
                'description': 'Connect with 5 users',
                'mission_type': 'add_friend',
                'target_count': 5,
                'points_reward': 15,
                'frequency': 'once',
                'icon': '👫',
                'order': 6
            },
            {
                'title': 'Super Connector',
                'description': 'Connect with 10 users',
                'mission_type': 'add_friend',
                'target_count': 10,
                'points_reward': 25,
                'frequency': 'once',
                'icon': '🌟',
                'order': 7
            },
            
            # Interaction missions
            {
                'title': 'First Message',
                'description': 'Send your first message to friends',
                'mission_type': 'send_message',
                'target_count': 1,
                'points_reward': 3,
                'frequency': 'once',
                'icon': '💬',
                'order': 8
            },
            {
                'title': 'Active Conversation',
                'description': 'Send 10 messages',
                'mission_type': 'send_message',
                'target_count': 10,
                'points_reward': 8,
                'frequency': 'once',
                'icon': '📱',
                'order': 9
            },
            
            # Post missions
            {
                'title': 'First Post',
                'description': 'Create your first post',
                'mission_type': 'create_post',
                'target_count': 1,
                'points_reward': 5,
                'frequency': 'once',
                'icon': '✍️',
                'order': 10
            },
            {
                'title': 'Content Creator',
                'description': 'Create 5 posts',
                'mission_type': 'create_post',
                'target_count': 5,
                'points_reward': 15,
                'frequency': 'once',
                'icon': '📄',
                'order': 11
            },
            {
                'title': 'First Like',
                'description': 'Like 1 post',
                'mission_type': 'like_post',
                'target_count': 1,
                'points_reward': 2,
                'frequency': 'once',
                'icon': '❤️',
                'order': 12
            },
            {
                'title': 'Activity Lover',
                'description': 'Like 20 posts',
                'mission_type': 'like_post',
                'target_count': 20,
                'points_reward': 10,
                'frequency': 'once',
                'icon': '💖',
                'order': 13
            },
            {
                'title': 'First Comment',
                'description': 'Comment on 1 post',
                'mission_type': 'comment_post',
                'target_count': 1,
                'points_reward': 3,
                'frequency': 'once',
                'icon': '💭',
                'order': 14
            },
            
            # Event missions
            {
                'title': 'Join First Event',
                'description': 'Join 1 event',
                'mission_type': 'join_event',
                'target_count': 1,
                'points_reward': 8,
                'frequency': 'once',
                'icon': '🎪',
                'order': 15
            },
            {
                'title': 'Event Organizer',
                'description': 'Create your first event',
                'mission_type': 'create_event',
                'target_count': 1,
                'points_reward': 15,
                'frequency': 'once',
                'icon': '🎉',
                'order': 16
            },
            
            # Level and points missions
            {
                'title': 'First Level Up',
                'description': 'Reach level 2',
                'mission_type': 'level_up',
                'target_count': 2,
                'points_reward': 10,
                'frequency': 'once',
                'icon': '⬆️',
                'order': 17
            },
            {
                'title': 'Expert',
                'description': 'Reach level 5',
                'mission_type': 'level_up',
                'target_count': 5,
                'points_reward': 25,
                'frequency': 'once',
                'icon': '🏆',
                'order': 18
            },
            {
                'title': 'Points Achievement',
                'description': 'Accumulate 100 points',
                'mission_type': 'earn_points',
                'target_count': 100,
                'points_reward': 20,
                'frequency': 'once',
                'icon': '💎',
                'order': 19
            },
            
            # Daily missions
            {
                'title': 'Daily Login',
                'description': 'Login to the system daily',
                'mission_type': 'daily_login',
                'target_count': 1,
                'points_reward': 2,
                'frequency': 'daily',
                'icon': '📅',
                'order': 20
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for mission_data in missions_data:
            mission, created = Mission.objects.get_or_create(
                mission_type=mission_data['mission_type'],
                target_count=mission_data['target_count'],
                frequency=mission_data['frequency'],
                defaults=mission_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created mission: {mission.title}')
                )
            else:
                # Update information if mission already exists
                for key, value in mission_data.items():
                    setattr(mission, key, value)
                mission.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Updated mission: {mission.title}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✨ Complete! Created {created_count} new missions and updated {updated_count} missions.'
            )
        )
