from django.core.management.base import BaseCommand
from django.db import transaction
from investments.models import InvestmentItem, InvestmentCategory
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix featured items display and ensure proper setup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--set-featured',
            type=str,
            nargs='+',
            help='Set specific items as featured by name',
        )
        parser.add_argument(
            '--clear-featured',
            action='store_true',
            help='Clear all featured flags',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        set_featured = options.get('set_featured', [])
        clear_featured = options['clear_featured']
        
        self.stdout.write(self.style.SUCCESS('🔧 Fixing Featured Items Display'))
        
        try:
            with transaction.atomic():
                # Get all active items
                all_items = InvestmentItem.objects.filter(is_active=True)
                featured_items = InvestmentItem.objects.filter(is_active=True, is_featured=True)
                
                self.stdout.write(f"📊 Current Status:")
                self.stdout.write(f"   Total active items: {all_items.count()}")
                self.stdout.write(f"   Featured items: {featured_items.count()}")
                
                # List current featured items
                if featured_items.exists():
                    self.stdout.write(f"\n⭐ Current Featured Items:")
                    for item in featured_items:
                        self.stdout.write(f"   - {item.name} (ID: {item.id})")
                else:
                    self.stdout.write(f"\n⚠️  No featured items found!")
                
                # Clear featured flags if requested
                if clear_featured:
                    if not dry_run:
                        InvestmentItem.objects.filter(is_featured=True).update(is_featured=False)
                        self.stdout.write(self.style.SUCCESS("✅ Cleared all featured flags"))
                    else:
                        self.stdout.write("🔍 Would clear all featured flags")
                
                # Set specific items as featured
                if set_featured:
                    for item_name in set_featured:
                        try:
                            item = InvestmentItem.objects.get(name=item_name, is_active=True)
                            if not dry_run:
                                item.is_featured = True
                                item.save()
                                self.stdout.write(self.style.SUCCESS(f"✅ Set '{item_name}' as featured"))
                            else:
                                self.stdout.write(f"🔍 Would set '{item_name}' as featured")
                        except InvestmentItem.DoesNotExist:
                            self.stdout.write(self.style.ERROR(f"❌ Item '{item_name}' not found"))
                
                # Auto-set some items as featured if none are set
                if not featured_items.exists() and not set_featured and not clear_featured:
                    # Get some popular items to feature
                    popular_items = all_items.order_by('-created_at')[:3]
                    
                    if not dry_run:
                        for item in popular_items:
                            item.is_featured = True
                            item.save()
                            self.stdout.write(self.style.SUCCESS(f"✅ Auto-set '{item.name}' as featured"))
                    else:
                        self.stdout.write("🔍 Would auto-set these items as featured:")
                        for item in popular_items:
                            self.stdout.write(f"   - {item.name}")
                
                # Verify the fix
                final_featured = InvestmentItem.objects.filter(is_active=True, is_featured=True)
                self.stdout.write(f"\n📈 Final Status:")
                self.stdout.write(f"   Featured items: {final_featured.count()}")
                
                if final_featured.exists():
                    self.stdout.write(f"\n⭐ Final Featured Items:")
                    for item in final_featured:
                        self.stdout.write(f"   - {item.name} (ID: {item.id})")
                
                # Test the marketplace query
                self.stdout.write(f"\n🧪 Testing Marketplace Query:")
                marketplace_featured = InvestmentItem.objects.filter(
                    is_active=True,
                    is_featured=True
                ).select_related('category').order_by('-created_at')[:6]
                
                self.stdout.write(f"   Marketplace would show: {marketplace_featured.count()} featured items")
                for item in marketplace_featured:
                    self.stdout.write(f"   - {item.name} (Category: {item.category.name})")
                
                if dry_run:
                    self.stdout.write(self.style.WARNING("\n🔍 This was a dry run - no changes were made"))
                else:
                    self.stdout.write(self.style.SUCCESS("\n✅ Featured items fixed successfully!"))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error fixing featured items: {e}"))
            logger.error(f"Error fixing featured items: {e}")
            raise
