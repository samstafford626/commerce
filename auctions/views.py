from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from .models import User, Listing, Bid, Comment
from datetime import datetime
from decimal import Decimal

class CreateListingForm(forms.Form):
    title = forms.CharField(label="Title")
    description = forms.CharField(label="Description")
    starting_bid = forms.DecimalField(label="Starting Bid")
    image_url = forms.URLField(label="Image URL")
    category = forms.CharField(label="Category")


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True)
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
def create(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]
            current_bid = starting_bid
            user = request.user
            date = datetime.now()
            listing = Listing(title=title, description=description, starting_bid=starting_bid, image_url=image_url, category=category, user=user, current_bid=current_bid, date=date)
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })
    
    return render(request, "auctions/create.html", {
        "form": CreateListingForm()
    })

@login_required
def your_listings(request):
    return render(request, "auctions/your_listings.html", {
        "listings": Listing.objects.filter(user=request.user)
    })

@login_required
def remove_listing(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(id=listing_id)
        listing.active = False

        listing.save()
        return HttpResponseRedirect(reverse("your_listings"))
    
@login_required
def relist(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(id=listing_id)
        listing.active = True
        listing.save()
        return HttpResponseRedirect(reverse("your_listings"))


def listing(request,  listing_id):
    listing = Listing.objects.get(id=listing_id)
    comments = listing.comments.all()
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments
    })

@login_required
def make_bid(request):
    if request.method == "POST":
        bid = Decimal(request.POST["bid"])
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(id=listing_id)
        current_bid = listing.current_bid
        user = request.user

        if bid > current_bid:
            listing.current_bid = bid
            listing.winner = user
            listing.save()
            new_bid = Bid(bid=bid, user=request.user, listing=listing)
            new_bid.save()
        
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
    

@login_required
def make_comment(request):
    if request.method == "POST":
        comment = request.POST["comment"]
        user = request.user
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(id=listing_id)
        date = datetime.now()

        new_data = Comment(comment=comment, user=user, listing=listing, date=date)
        new_data.save()

        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
    
