from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from vip_members.models import VIPStaff, VIPMember, VIPBenefit, VIPNotification
from decimal import Decimal


class Command(BaseCommand):
    help = 'Setup VIP Members sample data'

    def handle(self, *args, **options):
        self.stdout.write('Setting up VIP Members sample data...')
        
        # Create VIP Staff
        staff_data = [
            {
                'username': 'john_vip_manager',
                'email': 'john.manager@meridianassetlogistics.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'staff_id': 'VIP001',
                'full_name': 'John Smith',
                'department': 'VIP Services',
                'phone': '+1-555-0101'
            },
            {
                'username': 'sarah_vip_specialist',
                'email': 'sarah.specialist@meridianassetlogistics.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'staff_id': 'VIP002',
                'full_name': 'Sarah Johnson',
                'department': 'VIP Services',
                'phone': '+1-555-0102'
            }
        ]
        
        vip_staff = []
        for staff_info in staff_data:
            user, created = User.objects.get_or_create(
                username=staff_info['username'],
                defaults={
                    'email': staff_info['email'],
                    'first_name': staff_info['first_name'],
                    'last_name': staff_info['last_name'],
                    'is_staff': True,
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
            
            vip_staff_obj, created = VIPStaff.objects.get_or_create(
                user=user,
                defaults={
                    'staff_id': staff_info['staff_id'],
                    'full_name': staff_info['full_name'],
                    'department': staff_info['department'],
                    'phone': staff_info['phone'],
                    'email': staff_info['email']
                }
            )
            vip_staff.append(vip_staff_obj)
            
            if created:
                self.stdout.write(f'Created VIP Staff: {vip_staff_obj.full_name}')
        
        # Create VIP Benefits
        benefits_data = [
            {
                'name': 'Priority Support',
                'description': '24/7 dedicated support with priority response times under 2 hours',
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
                'description': 'Access to pre-launch and exclusive investment opportunities',
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
                'name': 'Premium Analytics',
                'description': 'Advanced portfolio analytics and market insights',
                'membership_tiers': 'gold,platinum,diamond',
                'icon': 'fas fa-chart-line'
            },
            {
                'name': 'White Glove Service',
                'description': 'Concierge-level service with personal assistance',
                'membership_tiers': 'platinum,diamond',
                'icon': 'fas fa-concierge-bell'
            }
        ]
        
        for benefit_info in benefits_data:
            benefit, created = VIPBenefit.objects.get_or_create(
                name=benefit_info['name'],
                defaults={
                    'description': benefit_info['description'],
                    'membership_tiers': benefit_info['membership_tiers'],
                    'icon': benefit_info['icon']
                }
            )
            if created:
                self.stdout.write(f'Created VIP Benefit: {benefit.name}')
        
        # Create sample VIP Members for existing users
        existing_users = User.objects.filter(is_staff=False)[:5]
        
        for i, user in enumerate(existing_users):
            vip_member, created = VIPMember.objects.get_or_create(
                customer=user,
                defaults={
                    'member_id': f'VIP{user.id:06d}',
                    'assigned_staff': vip_staff[i % len(vip_staff)],
                    'membership_tier': ['bronze', 'silver', 'gold', 'platinum'][i % 4],
                    'status': 'active',
                    'phone': f'+1-555-{1000 + user.id:04d}',
                    'total_investments': Decimal('10000.00') + (Decimal('5000.00') * i),
                    'monthly_income': Decimal('5000.00') + (Decimal('2000.00') * i),
                    'net_worth': Decimal('50000.00') + (Decimal('25000.00') * i),
                    'priority_support': True,
                    'dedicated_account_manager': i >= 1,
                    'exclusive_investment_opportunities': i >= 2,
                    'faster_processing': i >= 1,
                    'notes': f'VIP member since setup - tier {["bronze", "silver", "gold", "platinum"][i % 4]}'
                }
            )
            
            if created:
                self.stdout.write(f'Created VIP Member: {vip_member.full_name} ({vip_member.get_membership_tier_display()})')
                
                # Create welcome notification
                VIPNotification.objects.create(
                    member=vip_member,
                    title='Welcome to VIP Membership!',
                    message=f'Welcome to {vip_member.get_membership_tier_display()}! You now have access to exclusive benefits and priority support.',
                    notification_type='success'
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully setup VIP Members sample data!')
        )
        self.stdout.write('You can now access the VIP dashboard at /vip-members/')
