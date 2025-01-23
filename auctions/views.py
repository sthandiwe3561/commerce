from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse

from .models import User,Product,Comment


def index(request):
    product = Product.objects.all()
    return render(request, "auctions/index.html",{
        "products": product
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

def add_listing(request):
    if request.method == "POST":
        # Get form data
        name = request.POST.get("name")
        description = request.POST.get("description")
        starting_bid = request.POST.get("starting_bid")
        image_url = request.POST.get("image_url")
        category = request.POST.get("category")

        # Create and save the new product
        Product.objects.create(
            name=name,
            description=description,
            price=starting_bid,
            image_url=image_url,
            category=category,
            user=request.user  # Associate the product with the logged-in user
        )

        return redirect("index")
    categories = ["Electronics", "Clothing", "Books", "Home & Garden", "Sports", "Toys"]
    return render(request, "auctions/add_listing.html",{
        "categories": categories
    })

def view_listing(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "auctions/view_listing.html",{
        "product": product
    })

def comments(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        content = request.POST['content']
        comment = Comment.objects.create(
            user=request.user,
            product=product,
            content=content
        )
        comment.save()
        return redirect('view_listing', product_id=product.id)
    print(product)
    comments = product.comments.all()  # Fetch comments using the related_name

    #comments = Comment.objects.filter(product=product)
    print("context", comments)
    return render(request, "auctions/index.html",{
        "product": product,
        "comments": comments,
    })