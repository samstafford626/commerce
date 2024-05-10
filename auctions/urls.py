from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("your_listings", views.your_listings, name="your_listings"),
    path("remove_listing", views.remove_listing, name="remove_listing"),
    path("relist", views.relist, name="relist"),
]
