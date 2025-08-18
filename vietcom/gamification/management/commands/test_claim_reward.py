from django.core.management.base import BaseCommand
from users.models import User
from gamification.models import UserMission, Mission, UserPoints

class Command(BaseCommand):
    help = 'Test claim reward for user'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='User ID')
        parser.add_argument('mission_id', type=int, help='Mission ID')

    def handle(self, *args, **options):
        user_id = options['user_id']
        mission_id = options['mission_id']
        
        try:
            user = User.objects.get(id=user_id)
            mission = Mission.objects.get(id=mission_id)
            
            self.stdout.write(
                self.style.SUCCESS(f'🎯 Test claim reward for user: {user.full_name}')
            )
            self.stdout.write(f'📋 Mission: {mission.title}')
            
            # Get or create user mission
            user_mission, created = UserMission.objects.get_or_create(
                user=user,
                mission=mission
            )
            
            if created:
                self.stdout.write('➕ Created new UserMission')
            
            self.stdout.write(f'📊 Current status: {user_mission.status}')
            self.stdout.write(f'🔢 Progress: {user_mission.current_count}/{mission.target_count}')
            
            # If not completed, complete the mission
            if user_mission.status == 'in_progress':
                user_mission.current_count = mission.target_count
                completed = user_mission.check_completion()
                if completed:
                    self.stdout.write('✅ Mission completed')
                else:
                    self.stdout.write('❌ Cannot complete mission')
            
            # Try to claim reward
            if user_mission.status == 'completed':
                old_points = user.points
                old_level = user.level
                
                success = user_mission.claim_reward()
                
                if success:
                    user.refresh_from_db()
                    points_gained = user.points - old_points
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'🎉 Claim successful!')
                    )
                    self.stdout.write(f'💎 Old points: {old_points} → New points: {user.points} (+{points_gained})')
                    self.stdout.write(f'🏆 Old level: {old_level} → New level: {user.level}')
                    
                    # Check if UserPoints was created
                    latest_point = UserPoints.objects.filter(
                        user=user,
                        action='mission_complete'
                    ).order_by('-created_at').first()
                    
                    if latest_point:
                        self.stdout.write(f'📝 Created UserPoints: {latest_point}')
                    else:
                        self.stdout.write('⚠️ No UserPoints created found')
                        
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Claim failed!')
                    )
            else:
                self.stdout.write(f'⚠️ Mission not in completed status: {user_mission.status}')
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ User not found with ID: {user_id}')
            )
        except Mission.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Mission not found with ID: {mission_id}')
            )
