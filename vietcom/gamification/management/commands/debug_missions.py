from django.core.management.base import BaseCommand
from users.models import User
from gamification.models import UserMission, Mission, UserPoints

class Command(BaseCommand):
    help = 'Debug missions system for user'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='User ID to debug')

    def handle(self, *args, **options):
        user_id = options['user_id']
        
        try:
            user = User.objects.get(id=user_id)
            self.stdout.write(
                self.style.SUCCESS(f'🔍 Debug for user: {user.full_name} ({user.email})')
            )
            
            # Display user information
            self.stdout.write(f'📊 Level: {user.level}')
            self.stdout.write(f'💎 Points: {user.points}')
            self.stdout.write(f'🎯 Points needed for next level: {user.get_points_for_next_level()}')
            self.stdout.write(f'📈 Progress: {user.get_progress_to_next_level():.1f}%')
            
            self.stdout.write('\n' + '='*50)
            
            # Display missions
            user_missions = UserMission.objects.filter(user=user).select_related('mission')
            
            self.stdout.write(f'📋 Total missions: {user_missions.count()}')
            
            for status in ['in_progress', 'completed', 'claimed']:
                count = user_missions.filter(status=status).count()
                status_display = {
                    'in_progress': '🔄 In Progress',
                    'completed': '✅ Completed',
                    'claimed': '🎁 Claimed'
                }
                self.stdout.write(f'{status_display[status]}: {count}')
            
            self.stdout.write('\n📝 Mission details:')
            for user_mission in user_missions.order_by('mission__order'):
                status_icon = {
                    'in_progress': '🔄',
                    'completed': '✅',
                    'claimed': '🎁'
                }
                
                self.stdout.write(
                    f'{status_icon[user_mission.status]} {user_mission.mission.title} '
                    f'({user_mission.current_count}/{user_mission.mission.target_count}) '
                    f'+{user_mission.mission.points_reward}pts'
                )
            
            # Display points history
            self.stdout.write('\n' + '='*50)
            self.stdout.write('💰 Points history (last 10):')
            
            recent_points = UserPoints.objects.filter(user=user).order_by('-created_at')[:10]
            for point in recent_points:
                sign = '+' if point.points > 0 else ''
                self.stdout.write(
                    f'{point.created_at.strftime("%d/%m %H:%M")} | '
                    f'{sign}{point.points}pts | {point.description}'
                )
            
            if not recent_points:
                self.stdout.write('No points history yet')
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ User not found with ID: {user_id}')
            )
