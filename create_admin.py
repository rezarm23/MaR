import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MaR_site.settings")
django.setup()


User = get_user_model()

username = "rezaadmin"
email = "reza@reza.com"
password = "Reza8818"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("✅ Superuser created.")
else:
    print("ℹ️ Superuser already exists.")
