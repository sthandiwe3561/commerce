from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_listing", views.add_listing, name="add_listing"),
    path("product/<int:product_id>/view_listing/", views.view_listing, name="view_listing"),
    path("product/<int:product_id>/comments/", views.comments, name="comments"),
    path("product/<int:product_id>/bid/", views.bid, name="bid"),

]
