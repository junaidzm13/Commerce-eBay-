from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=128)
    current_bid = models.IntegerField()
    category = models.CharField(max_length=40)
    image_url = models.CharField(max_length=200, blank=True)
    watchlist = models.ManyToManyField(
        User, blank=True, related_name="watchlist")
    winner = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, default=None, null=True, related_name="wins")
    active=models.BooleanField(default=True)

class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=128)

class Bid(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids")
    bid = models.IntegerField()



