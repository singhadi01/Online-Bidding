from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Item, Bid, UserProfile
from django.db.models import Max

@login_required(login_url='login')
def home(request):
    items = Item.objects.all()
    highest_bids = {}

    for item in items:
        highest_bid = Bid.objects.filter(item=item).order_by('-amount').first()
        if highest_bid:
            highest_bids[item.id] = {
                "amount": highest_bid.amount,
                "bidder": highest_bid.bidder.username,
                "email": highest_bid.bidder.email
            }

    return render(request, 'home.html', {'items': items, 'highest_bids': highest_bids})
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.utils import IntegrityError
from bidding.models import UserProfile

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        full_name = request.POST['full_name']
        age = request.POST['age']
        state = request.POST['state']
        aadhaar_number = request.POST['aadhaar_number']
        gmail = request.POST['gmail']
        mobile_number = request.POST['mobile_number']

        # 🚨 Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return redirect('signup')

        # 🚨 Check if Gmail already exists
        if UserProfile.objects.filter(gmail=gmail).exists():
            messages.error(request, "This Gmail is already registered.")
            return redirect('signup')

        # 🚨 Check if mobile number already exists
        if UserProfile.objects.filter(mobile_number=mobile_number).exists():
            messages.error(request, "This mobile number is already registered.")
            return redirect('signup')

        # 🚨 Check if Aadhaar number already exists
        if UserProfile.objects.filter(aadhaar_number=aadhaar_number).exists():
            messages.error(request, "This Aadhaar number is already registered.")
            return redirect('signup')

        try:
            # Create the User
            user = User.objects.create_user(username=username, password=password)

            # Create the UserProfile
            UserProfile.objects.create(
                user=user,
                full_name=full_name,
                age=age,
                state=state,
                aadhaar_number=aadhaar_number,
                gmail=gmail,
                mobile_number=mobile_number
            )

            # Automatically log in the user
            login(request, user)
            messages.success(request, "Account created successfully! Welcome.")
            return redirect('home')

        except IntegrityError:
            messages.error(request, "An error occurred. Please try again.")
            return redirect('signup')

    return render(request, 'signup.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect("home")

@login_required
@login_required
def list_item(request):
    print("✅ list_item view called") 
    if request.method == "POST":
        print("Received POST request:", request.POST)
        name = request.POST['name']
        description = request.POST['description']
        base_price = float(request.POST['base_price'])
        

        Item.objects.create(
            seller=request.user,
            name=name,
            description=description,
            base_price=base_price
        )

        return redirect('list_items_for_user')  # ✅ Redirect after POST

    items = Item.objects.filter(seller=request.user)
    highest_bids = {
        bid['item']: bid['max_amount']
        for bid in Bid.objects.values('item').annotate(max_amount=Max('amount'))
    }

    return render(request, 'list_item.html', {'items': items, 'highest_bids': highest_bids})


@login_required
def place_bid(request):
    items = Item.objects.filter(status="live")

    if request.method == "POST":
        item_id = request.POST['item_id']
        bid_amount = float(request.POST['bid_amount'])
        item = Item.objects.get(id=item_id)

        highest_bid = item.bid_set.order_by('-amount').first()
        if highest_bid is None or bid_amount > highest_bid.amount:
            Bid.objects.create(item=item, bidder=request.user, amount=bid_amount)
        else:
            messages.error(request, "Bid must be higher than the current highest bid.")

    return render(request, 'place_bid.html', {'items': items})

@login_required
def list_items_for_user(request):
    print("✅ list_items_for_user view called")  
    items = Item.objects.filter(seller=request.user)

    # Create a dictionary mapping each item ID to its highest bid
    highest_bids = {
        bid['item']: bid['max_amount']
        for bid in Bid.objects.values('item').annotate(max_amount=Max('amount'))
        if bid['max_amount'] is not None  # Ensure we only include valid bids
    }

    return render(request, 'list_item.html', {'items': items, 'highest_bids': highest_bids})
@login_required
def start_bidding(request, item_id):
    item = get_object_or_404(Item, id=item_id, seller=request.user)
    if item.status == 'upcoming':
        item.status = 'live'
        item.save()
        messages.success(request, f"Bidding started for {item.name}.")
    else:
        messages.error(request, "Bidding can only be started for 'Open Soon' items.")
    return redirect('list_items_for_user')

def close_bidding(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.status = "closed"
    item.save()
    return redirect("list_items_for_user")
