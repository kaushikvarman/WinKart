
from .models import Category

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)

# later we will update this in the templates section of settings.py file of winkart
# Then we can use this links in every template