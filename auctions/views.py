from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib import messages
from django.urls import reverse

from .models import User,Product,Comment,Bid


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
            starting_price=starting_bid,
            current_price =starting_bid,
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

def bid(request,product_id):
     product = get_object_or_404(Product, id=product_id)
     
     if request.method == "POST":
         bid_amount = float(request.POST["bid_amount"])

         #check if the bid amount is higher
         if bid_amount > product.current_price:
             #save the changes
             new_bid = Bid.objects.create(
                 user = request.user,
                 product = product,
                 amount = bid_amount
             )
             new_bid.save()

             #update the current_price in product
             product.current_price = bid_amount
             product.save()
             messages.success(request, "Your bid has been placed successfully!")
         else:
             messages.error(request, "Your bid must be higher than the current price!")  
             

     return redirect("view_listing", product_id=product.id)

def delete_bid(request, product_id):
    # Get the product
    product = get_object_or_404(Product, id=product_id)

    # Check if the user has placed a bid on the product
    user_bid = Bid.objects.filter(user=request.user, product=product).first()

    if user_bid:
        deleted_bid_amount = user_bid.amount

        # Delete the bid
        user_bid.delete()
        # Check if the deleted bid was the current highest bid
        highest_bid = Bid.objects.filter(product=product).order_by('-amount').first()

        if highest_bid:
            # Update the product's current price to the next highest bid
            product.current_price = highest_bid.amount
        else:
            # If no bids remain, reset the current price to the starting price
            product.current_price = product.starting_price

        product.save()

        # Show a success message
        messages.success(request, f"Your bid of R{deleted_bid_amount} has been deleted. The current price is now R{product.current_price}.")
    else:
        messages.error(request, "You don't have any bids to delete for this product.")

    # Redirect back to the product page
    return redirect('my_bids')

def my_bids(request):
    user_bids = Bid.objects.filter(user=request.user)

     # Add a status to each bid
    bids_with_status = []
    for bid in user_bids:
        statuses = "Winning" if bid.amount == bid.product.current_price else "Outbid"
        bid.status = statuses
        bid.save()
        bids_with_status.append({
            'product': bid.product,
            'amount': bid.amount,
            'date_placed': bid.timestamp,
            'status': bid.status,
        })
    return render(request,"auctions/my_bids.html", {
       "bids_with_status" : bids_with_status
    })

def my_listings(request):
    listings = Product.objects.filter(user=request.user)
    return render(request,"auctions/my_listings.html", {
        "listings":listings
    })

def close_listing(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    user_bid = Bid.objects.filter(user=request.user, product=product).get()

      # Check if the logged-in user is the creator of the listing
    if request.user != product.user:
        return HttpResponseForbidden("You are not allowed to close this listing.")
    

    if user_bid:
        user_bid.status = "Winner"
        user_bid.save()


    return redirect(index)
