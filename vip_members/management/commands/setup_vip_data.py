from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from vip_members.models import VIPStaff, VIPBenefit


class Command(BaseCommand):
    help = 'Set up initial VIP staff and benefits data'

    def handle(self, *args, **options):
        self.stdout.write('Setting up VIP data...')
        
        # Create VIP Benefits
        benefits_data = [
            {
                'name': 'Priority Customer Support',
                'description': '24/7 dedicated customer support with priority response times',
                'membership_tiers': 'bronze,silver,gold,platinum,diamond',
                'icon': 'fas fa-headset'
            },
            {
                'name': 'Dedicated Account Manager',
                'description': 'Personal account manager for all your investment needs',
                'membership_tiers': 'silver,gold,platinum,diamond',
                'icon': 'fas fa-user-tie'
            },
            {
                'name': 'Exclusive Investment Opportunities',
                'description': 'Access to exclusive investment opportunities and early access to new products',
                'membership_tiers': 'gold,platinum,diamond',
                'icon': 'fas fa-star'
            },
            {
                'name': 'Faster Processing',
                'description': 'Expedited processing for all transactions and withdrawals',
                'membership_tiers': 'silver,gold,platinum,diamond',
                'icon': 'fas fa-bolt'
            },
            {
                'name': 'Higher Investment Limits',
                'description': 'Increased investment limits and withdrawal amounts',
                'membership_tiers': 'gold,platinum,diamond',
                'icon': 'fas fa-chart-line'
            },
            {
                'name': 'Personal Investment Advisor',
                'description': 'One-on-one investment advisory sessions with financial experts',
                'membership_tiers': 'platinum,diamond',
                'icon': 'fas fa-user-graduate'
            },
            {
                'name': 'VIP Events & Networking',
                'description': 'Invitation to exclusive VIP events and networking opportunities',
                'membership_tiers': 'platinum,diamond',
                'icon': 'fas fa-calendar-star'
            },
            {
                'name': 'Premium Research Reports',
                'description': 'Access to premium market research and analysis reports',
                'membership_tiers': 'gold,platinum,diamond',
                'icon': 'fas fa-file-alt'
            },
            {
                'name': 'Custom Investment Strategies',
                'description': 'Tailored investment strategies based on your financial goals',
                'membership_tiers': 'platinum,diamond',
                'icon': 'fas fa-cogs'
            },
            {
                'name': 'White-Glove Service',
                'description': 'Concierge-level service for all your investment needs',
                'membership_tiers': 'diamond',
                'icon': 'fas fa-concierge-bell'
            }
        ]
        
        for benefit_data in benefits_data:
            benefit, created = VIPBenefit.objects.get_or_create(
                name=benefit_data['name'],
                defaults=benefit_data
            )
            if created:
                self.stdout.write(f'Created benefit: {benefit.name}')
            else:
                self.stdout.write(f'Benefit already exists: {benefit.name}')
        
        # Create VIP Staff (if admin user exists)
        try:
            admin_user = User.objects.get(username='admin')
            
            staff_data = [
                {
                    'user': admin_user,
                    'staff_id': 'VIP001',
                    'full_name': 'Sarah Johnson',
                    'phone': '+1-555-0101',
                    'email': 'sarah.johnson@meridianassetlogistics.com',
                    'department': 'VIP Services'
                },
                {
                    'staff_id': 'VIP002',
                    'full_name': 'Michael Chen',
                    'phone': '+1-555-0102',
                    'email': 'michael.chen@meridianassetlogistics.com',
                    'department': 'VIP Services'
                },
                {
                    'staff_id': 'VIP003',
                    'full_name': 'Emily Rodriguez',
                    'phone': '+1-555-0103',
                    'email': 'emily.rodriguez@meridianassetlogistics.com',
                    'department': 'VIP Services'
                }
            ]
            
            for staff_info in staff_data:
                # Create user if it doesn't exist (for staff without existing users)
                if 'user' not in staff_info:
                    username = staff_info['full_name'].lower().replace(' ', '.')
                    email = staff_info['email']
                    
                    # Create user
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        first_name=staff_info['full_name'].split()[0],
                        last_name=' '.join(staff_info['full_name'].split()[1:])
                    )
                    staff_info['user'] = user
                
                staff, created = VIPStaff.objects.get_or_create(
                    staff_id=staff_info['staff_id'],
                    defaults=staff_info
                )
                if created:
                    self.stdout.write(f'Created VIP staff: {staff.full_name}')
                else:
                    self.stdout.write(f'VIP staff already exists: {staff.full_name}')
                    
        except User.DoesNotExist:
            self.stdout.write('Admin user not found. Skipping VIP staff creation.')
        
        self.stdout.write(
            self.style.SUCCESS('VIP data setup completed successfully!')
        )