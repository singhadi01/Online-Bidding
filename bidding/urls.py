from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("list-item/", views.list_item, name="list_item"),
    path("place-bid/", views.place_bid, name="place_bid"),
    path("my-items/", views.list_items_for_user, name="list_items_for_user"),
    path("start-bidding/<int:item_id>/", views.start_bidding, name="start_bidding"),
    path("close-bidding/<int:item_id>/", views.close_bidding, name="close_bidding"),
 
]
