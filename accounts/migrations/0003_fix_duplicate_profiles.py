from django.db import migrations


def fix_duplicate_profiles(apps, schema_editor):
    """Fix any duplicate customer profiles that might exist"""
    CustomerProfile = apps.get_model('accounts', 'CustomerProfile')
    StaffProfile = apps.get_model('accounts', 'StaffProfile')
    
    # Get all customer profiles
    customer_profiles = CustomerProfile.objects.all()
    seen_users = set()
    duplicates = []
    
    # Find duplicate customer profiles
    for profile in customer_profiles:
        if profile.user_id in seen_users:
            duplicates.append(profile.id)
        else:
            seen_users.add(profile.user_id)
    
    # Delete duplicate customer profiles
    if duplicates:
        CustomerProfile.objects.filter(id__in=duplicates).delete()
        print(f"Deleted {len(duplicates)} duplicate customer profiles")
    
    # Get all staff profiles
    staff_profiles = StaffProfile.objects.all()
    seen_staff_users = set()
    staff_duplicates = []
    
    # Find duplicate staff profiles
    for profile in staff_profiles:
        if profile.user_id in seen_staff_users:
            staff_duplicates.append(profile.id)
        else:
            seen_staff_users.add(profile.user_id)
    
    # Delete duplicate staff profiles
    if staff_duplicates:
        StaffProfile.objects.filter(id__in=staff_duplicates).delete()
        print(f"Deleted {len(staff_duplicates)} duplicate staff profiles")


def reverse_fix_duplicate_profiles(apps, schema_editor):
    """Reverse migration - no action needed"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customerprofile'),
    ]

    operations = [
        migrations.RunPython(fix_duplicate_profiles, reverse_fix_duplicate_profiles),
    ]
