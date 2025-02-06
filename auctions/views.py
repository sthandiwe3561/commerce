from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib import messages
from django.urls import reverse

from .models import User,Product,Comment,Bid,Watchlist


def index(request):
     # Define your category list
    categories = ["Electronics", "Clothing", "Books", "Home & Garden", "Sports", "Toys"]

    # Get the selected category from the query parameters
    selected_category = request.GET.get('category')
     # Filter products based on the selected category
    if selected_category and selected_category in categories:
        product = Product.objects.filter(category=selected_category,is_active=True)
    else:
        product = Product.objects.filter(is_active=True)
    return render(request, "auctions/index.html",{
        "products": product,
        "categories": categories,
        "selected_category": selected_category,
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
    comments = product.comments.all()  # Fetch all comments for this product

    return render(request, "auctions/view_listing.html",{
        "product": product,
        "comments": comments
    })

def comments(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == "POST":
        content = request.POST["content"]

        # Check if the user already has a comment on this product
        existing_comment = Comment.objects.filter(user=request.user, product=product).first()
        
        if existing_comment:
            existing_comment.content = content  # Update the existing comment
            existing_comment.save()
        else:
            Comment.objects.create(
                user=request.user,
                product=product,
                content=content
            )

        return redirect("view_listing", product_id=product.id)

    

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

        # Check if the product is not active and if the user's bid is the same as when they placed it
        if not bid.product.is_active and bid.amount == bid.product.current_price:
             statuses = "Winner"  
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
    listings = Product.objects.filter(user=request.user, is_active= True)

    return render(request,"auctions/my_listings.html", {
        "listings":listings,
    })


def close_listing(request,product_id):
    product = get_object_or_404(Product, pk=product_id)
    products = Product.objects.filter(user=request.user,is_active=True)
    
    product.is_active = False
    product.save()

    return render(request,"auctions/my_listings.html", {
        "listings":products,
    })

def add_watchlist(request,product_id):
    product =get_object_or_404(Product,id=product_id)
    #save the changes
     # Check if the product is already in the user's watchlist
    if Watchlist.objects.filter(user=request.user, product=product).exists():
        messages.info(request, "This product is already in your watchlist.")
    else:
        try:
            # Add to watchlist
            new_watchlist = Watchlist.objects.create(
                user=request.user,
                product=product,
            )
            new_watchlist.save()
            messages.success(request, "Product added to your watchlist.")
        except IntegrityError:
            messages.error(request, "An error occurred while adding the product to your watchlist.")
   
    return redirect("watchlist")

@login_required(login_url="login")  # Redirects to login page if not logged in
def watchlist(request):
     # Get the watchlist items for the logged-in user
    watchlist_items = Watchlist.objects.filter(user=request.user)

    return render(request,"auctions/watchlist.html",{
        "watchlist_items": watchlist_items
    })

def edit_listing(request,product_id):
    product = get_object_or_404(Product, pk=product_id)
    products = Product.objects.filter(user=request.user,is_active=True)

    if request.method == "POST":
         # Get form data
        name = request.POST.get("name")
        description = request.POST.get("description")
        starting_bid = float(request.POST.get("starting_bid", 0))  # Convert to float
        image_url = request.POST.get("image_url")
        category = request.POST.get("category")
        
        product.name =name
        product.description = description
        product.starting_price = starting_bid
        product.image_url = image_url
        product.category = category

        if starting_bid > product.current_price:
            product.current_price
        product.save()

        return render(request,"auctions/my_listing.html", {
            "listings":products
        }) 
 
    categories = ["Electronics", "Fashion", "Home", "Toys", "Sports"]  # Example categories
    return render(request,"auctions/add_listing.html",{
        "product":product,
        "categories": categories  # Pass categories to the template
    })

def edit_comments(request,comment_id):
    commentt = get_object_or_404(Comment, id=comment_id)
    product = get_object_or_404(Product, id=commentt.product.id, is_active=True)  # Get single product
    
    # Fetch all comments related to the product
    comments = Comment.objects.filter(product=product)  

    if request.method == "POST":
        comment = request.POST.get("content")
        if comment:  
            commentt.content = comment  # Update the comment content
            commentt.save()  # Save changes
            return redirect("view_listing", product_id=product.id)  # Redirect back to the product page

    return render(request,"auctions/view_listing.html",{
        "comment":commentt,
        "product":product,
        "comments":comments

    })

def delete_comments(request, comment_id):
    # Get the comment or return 404 if not found
    comment = get_object_or_404(Comment, id=comment_id)

    # Get the associated product
    product = comment.product  # No need to check `is_active=True`

    # Delete the comment
    comment.delete()

    # Redirect to the correct product page
    return redirect("view_listing", product_id=product.id)  

