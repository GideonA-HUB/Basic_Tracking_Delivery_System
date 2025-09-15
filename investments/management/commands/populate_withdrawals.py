from django.core.management.base import BaseCommand
from django.utils import timezone
from investments.models import CryptoWithdrawal
from decimal import Decimal
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate crypto withdrawal list with sample data'

    def handle(self, *args, **options):
        # Sample names for withdrawal list
        names = [
            "Alexander Johnson", "Sarah Williams", "Michael Brown", "Emily Davis", "David Wilson",
            "Jessica Martinez", "Christopher Anderson", "Ashley Taylor", "Matthew Thomas", "Amanda Jackson",
            "Joshua White", "Stephanie Harris", "Andrew Martin", "Jennifer Thompson", "Daniel Garcia",
            "Nicole Martinez", "Ryan Rodriguez", "Samantha Lewis", "James Lee", "Brittany Walker",
            "Kevin Hall", "Megan Allen", "Brandon Young", "Rachel King", "Tyler Wright",
            "Lauren Lopez", "Jacob Hill", "Kayla Scott", "Nathan Green", "Amber Adams",
            "Zachary Baker", "Danielle Gonzalez", "Caleb Nelson", "Heather Carter", "Austin Mitchell",
            "Rebecca Perez", "Ethan Roberts", "Megan Turner", "Noah Phillips", "Stephanie Campbell",
            "Logan Parker", "Samantha Evans", "Connor Edwards", "Jessica Collins", "Lucas Stewart",
            "Ashley Sanchez", "Isaac Morris", "Brittany Rogers", "Owen Reed", "Kayla Cook",
            "Liam Morgan", "Rachel Bell", "Mason Murphy", "Amber Bailey", "Ethan Rivera",
            "Samantha Cooper", "Aiden Richardson", "Heather Cox", "Caleb Ward", "Megan Torres",
            "Logan Peterson", "Stephanie Gray", "Noah Ramirez", "Jessica James", "Lucas Watson",
            "Ashley Brooks", "Connor Kelly", "Brittany Sanders", "Owen Price", "Kayla Bennett",
            "Isaac Wood", "Rachel Barnes", "Mason Ross", "Amber Henderson", "Ethan Coleman",
            "Samantha Jenkins", "Aiden Perry", "Heather Powell", "Caleb Long", "Megan Patterson",
            "Logan Hughes", "Stephanie Flores", "Noah Washington", "Jessica Butler", "Lucas Simmons",
            "Ashley Foster", "Connor Gonzales", "Brittany Bryant", "Owen Alexander", "Kayla Russell",
            "Isaac Griffin", "Rachel Diaz", "Mason Hayes", "Amber Myers", "Ethan Ford",
            "Samantha Hamilton", "Aiden Graham", "Heather Sullivan", "Caleb Wallace", "Megan Woods",
            "Logan Cole", "Stephanie West", "Noah Jordan", "Jessica Owens", "Lucas Reynolds",
            "Ashley Fisher", "Connor Ellis", "Brittany Harrison", "Owen Gibson", "Kayla Mcdonald",
            "Isaac Cruz", "Rachel Marshall", "Mason Ortiz", "Amber Gomez", "Ethan Murray",
            "Samantha Freeman", "Aiden Wells", "Heather Webb", "Caleb Simpson", "Megan Stevens",
            "Logan Tucker", "Stephanie Porter", "Noah Hunter", "Jessica Hicks", "Lucas Crawford",
            "Ashley Boyd", "Connor Mason", "Brittany Morales", "Owen Kennedy", "Kayla Warren",
            "Isaac Dixon", "Rachel Spencer", "Mason Gardner", "Amber Stephens", "Ethan Payne",
            "Samantha Pierce", "Aiden Burns", "Heather Grant", "Caleb Knight", "Megan Hunter",
            "Logan Palmer", "Stephanie Robertson", "Noah Shaw", "Jessica Holmes", "Lucas Rice",
            "Ashley Robertson", "Connor Hunt", "Brittany Black", "Owen Daniels", "Kayla Palmer",
            "Isaac Mills", "Rachel Nichols", "Mason Grant", "Amber Knight", "Ethan Ferguson",
            "Samantha Rose", "Aiden Stone", "Heather Hawkins", "Caleb Dunn", "Megan Perkins",
            "Logan Hudson", "Stephanie Spencer", "Noah Gardner", "Jessica Stephens", "Lucas Payne",
            "Ashley Pierce", "Connor Burns", "Brittany Grant", "Owen Knight", "Kayla Hunter",
            "Isaac Palmer", "Rachel Robertson", "Mason Shaw", "Amber Holmes", "Ethan Rice",
            "Samantha Robertson", "Aiden Hunt", "Heather Black", "Caleb Daniels", "Megan Palmer",
            "Logan Mills", "Stephanie Nichols", "Noah Grant", "Jessica Knight", "Lucas Ferguson",
            "Ashley Rose", "Connor Stone", "Brittany Hawkins", "Owen Dunn", "Kayla Perkins",
            "Isaac Hudson", "Rachel Spencer", "Mason Gardner", "Amber Stephens", "Ethan Payne",
            "Samantha Pierce", "Aiden Burns", "Heather Grant", "Caleb Knight", "Megan Hunter",
            "Logan Palmer", "Stephanie Robertson", "Noah Shaw", "Jessica Holmes", "Lucas Rice"
        ]

        # Clear existing data
        CryptoWithdrawal.objects.all().delete()
        self.stdout.write('Cleared existing withdrawal data.')

        # Create withdrawal entries
        created_count = 0
        for i, name in enumerate(names):
            # Random amount between $100 and $50,000
            amount = Decimal(str(random.randint(100, 50000)))
            
            # Random status (mostly completed for display)
            status_choices = ['completed', 'completed', 'completed', 'processing', 'pending']
            status = random.choice(status_choices)
            
            # Random priority
            priority_choices = ['normal', 'normal', 'normal', 'fast', 'urgent']
            priority = random.choice(priority_choices)
            
            # Random crypto currency
            crypto_currencies = ['BTC', 'ETH', 'USDT', 'USDC', 'BNB']
            crypto_currency = random.choice(crypto_currencies)
            
            # Generate realistic estimated delivery dates
            now = timezone.now()
            if status == 'completed':
                # Completed withdrawals - delivery was in the past
                estimated_delivery = now - timedelta(days=random.randint(1, 30))
            elif status == 'processing':
                # Processing withdrawals - delivery soon
                estimated_delivery = now + timedelta(days=random.randint(1, 7))
            else:
                # Pending withdrawals - various future dates
                delivery_options = [
                    # Short term (1-7 days)
                    (1, 7),
                    # Medium term (1-4 weeks)
                    (7, 28),
                    # Long term (1-3 months)
                    (30, 90)
                ]
                
                # Weight the options (more short/medium term)
                weights = [0.3, 0.5, 0.2]
                selected_range = random.choices(delivery_options, weights=weights)[0]
                days_ahead = random.randint(selected_range[0], selected_range[1])
                estimated_delivery = now + timedelta(days=days_ahead)
            
            withdrawal = CryptoWithdrawal.objects.create(
                name=name,
                amount=amount,
                currency='USD',
                crypto_currency=crypto_currency,
                status=status,
                priority=priority,
                is_public=True,
                order_position=i + 1,
                estimated_delivery=estimated_delivery,
                notes=f"Sample withdrawal #{i + 1}"
            )
            
            # Set timestamps based on status
            if status == 'completed':
                withdrawal.completed_at = timezone.now()
                withdrawal.processed_at = timezone.now() - timezone.timedelta(hours=random.randint(1, 24))
            elif status == 'processing':
                withdrawal.processed_at = timezone.now() - timezone.timedelta(hours=random.randint(1, 12))
            
            withdrawal.save()
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} withdrawal entries.')
        )
