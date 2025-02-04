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
    path("product/<int:product_id>/delete_bid/", views.delete_bid, name="delete_bid"),
    path("my_bids", views.my_bids, name="my_bids"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("product/<int:product_id>/close_listing/", views.close_listing, name="close_listing"),
    path("product/<int:product_id>/add_watchlist/", views.add_watchlist, name="add_watchlist"),
    path("watchlist", views.watchlist,name="watchlist"),
    path("product/<int:product_id>/edit_listing/", views.edit_listing, name="edit_listing"),
]
