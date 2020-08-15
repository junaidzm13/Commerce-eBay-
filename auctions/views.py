from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Comment, Bid
from django import forms


CATEGORY_CHOICES = [("Electronics", "Electronics"),
                     ("Sports Equipment",
                      "Sports Equipment"),
                     ("Sport Equipment", "Sport Equipment"),
    ("Toys", "Toys"), ("Furniture", "Furniture"), ("Cosmetics",
     "Cosmetics"), ("Education", "Education"),
    ("No category", "---"), ("Other", "Other"),
    ("Transport", "Transport")]
CATEGORY_CHOICES.sort()


class ListingForm(forms.Form):
    title = forms.CharField(label='Title', max_length=40)
    description = forms.CharField(label='Description', max_length=128)
    starting_bid = forms.IntegerField(label='Starting bid')
    category = forms.CharField(
        label='Category', max_length=40, required=False, initial="", widget=forms.Select(choices=CATEGORY_CHOICES))
    image_url = forms.CharField(
        label="Image's URL", max_length=200, required=False)


def index(request):
    all_listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": all_listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def new_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        user = request.user
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            category = form.cleaned_data["category"]
            image_url = form.cleaned_data["image_url"]
            listing = Listing(user=user, title=title, description=description,
                          current_bid=starting_bid, category=category, image_url=image_url)
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = ListingForm()
        return render(request, "auctions/newlisting.html", {
            "form": form
        })

def highest_bidder(listing):
    bidders = listing.bids.all()
    maximum = -1
    for bidder in bidders:
        if bidder.bid > maximum:
            maximum = bidder.bid
            user = bidder.user
    return user

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if not request.user.is_authenticated:
        return render(request, "auctions/listing.html", {
            "listing": listing, "comments": listing.comments.all()
        })
        
    watchlist = request.user.watchlist.all()

    winnerhere = False
    if listing.active == False:
        winnerhere = (request.user.username == listing.winner.username)
    ownerhere = (request.user.username == listing.user.username)
    
    inwatchlist = False
    for item in watchlist:
        if item.id == listing_id:
            inwatchlist = True
            
    if request.method == "POST":
        if 'towatchlist' in request.POST:
            request.user.watchlist.add(listing)
            return render(request, "auctions/listing.html", {
                "listing": listing, "comments": listing.comments.all(),
                "inwatch": True, "winner": winnerhere, "owner": ownerhere
            })
        
        elif 'remwatchlist' in request.POST:
            request.user.watchlist.remove(listing)
            return render(request, "auctions/listing.html", {
                "listing": listing, "comments": listing.comments.all(),
                "inwatch": False, "winner": winnerhere, "owner": ownerhere
            })
        
        elif "submitbid" in request.POST:
            bid = request.POST.get("newbid")
            if int(bid) <= int(listing.current_bid):
                return render(request, "auctions/listing.html", {
                    "message": "Error", "listing": listing,
                    "comments": listing.comments.all(), "inwatch": inwatchlist,
                    "winner": winnerhere, "owner": ownerhere
                })
            else:
                listing.current_bid = int(bid)
                listing.save()
                new_bid = Bid(bid=int(bid), user=request.user,
                              listing=listing)
                new_bid.save()
                return render(request, "auctions/listing.html", {
                    "listing": listing, "comments": listing.comments.all(),
                    "inwatch": inwatchlist, "winner": winnerhere, "owner": ownerhere
                })
            
        elif "submitcomment" in request.POST:
            user = request.user
            comment = Comment(user=user, listing=listing,
                              comment=request.POST.get("newcomment"))
            comment.save()
            return render(request, "auctions/listing.html", {
                "listing": listing, "comments": listing.comments.all(),
                "inwatch": inwatchlist, "winner": winnerhere, "owner": ownerhere
            })
        
        elif "closelisting" in request.POST:
            listing.active = False
            listing.winner = highest_bidder(listing)
            listing.save()
            return render(request, "auctions/listing.html", {
                "listing": listing, "comments": listing.comments.all(),
                "inwatch": inwatchlist, "winner": winnerhere, "owner": ownerhere
            })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing, "comments": listing.comments.all(),
            "inwatch": inwatchlist, "winner": winnerhere, "owner": ownerhere
        })

@login_required
def watchlist(request):
    user = request.user

    return render(request, "auctions/watchlist.html", {
        "watchlist": user.watchlist.all()
    })

def categories(request):
    result = []
    for item in CATEGORY_CHOICES:
        result.append(item[0])
    return render(request, "auctions/categories.html", {
        "categories": result
    })

def bycategory(request, category):
    all_listings = Listing.objects.all()
    result = []
    for listing in all_listings:
        if listing.category == category:
            result.append(listing)
    return render(request, "auctions/category.html", {
        "listings": result, "category": category
    })
