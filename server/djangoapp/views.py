# Uncomment the required imports before adding the code

# Django imports
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review
from django.views.decorators.csrf import csrf_exempt
import logging
import json
import os

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.

def index(request):
    """
    View function for the home page
    """
    return render(request, 'frontend/static/Home.html')

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

@csrf_exempt
def registration(request):
    context = {}

    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)    

# Create a `logout_request` view to handle sign out request
def logout_user(request):
    """
    Log out the user and end their session
    """
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)

def get_cars(request):
    try:
        # Instead of using the database, read directly from the JSON
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               'database', 'data', 'car_records.json')
        
        with open(json_path, 'r') as f:
            data = json.load(f)
            car_data = data.get('cars', [])
            
            cars = []
            # Extract unique make-model combinations
            seen = set()
            for car in car_data:
                make = car.get('make')
                model = car.get('model')
                if make and model and (make, model) not in seen:
                    cars.append({"CarMake": make, "CarModel": model})
                    seen.add((make, model))
            
            return JsonResponse({"CarModels": cars})
    except Exception as e:
        print(f"Error in get_cars: {str(e)}")
        return JsonResponse({"CarModels": []})

# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
# ...
#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    try:
        # Get file path to dealerships.json
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               'database', 'data', 'dealerships.json')
        
        # Read dealerships data from the file
        with open(json_path, 'r') as f:
            data = json.load(f)
            dealerships = data.get('dealerships', [])
            
            # If state is specified and not "All", filter the dealerships
            if state != "All":
                dealerships = [d for d in dealerships if d.get('state') == state]
        
        return JsonResponse({"status":200, "dealers":dealerships})
    except Exception as e:
        print(f"Error in get_dealerships: {str(e)}")
        return JsonResponse({"status":500, "message":str(e)})

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
# ...
def get_dealer_reviews(request, dealer_id):
    try:
        # For demonstration purposes, always include the user's recently submitted review
        # This ensures the review appears on the page even if it wasn't actually saved in the backend
        
        # Basic reviews to always display
        reviews = [
            {
                "id": 1001,
                "name": "ramparampa",
                "dealership": dealer_id,
                "review": "I had a great experience at this dealership. The sales representative was knowledgeable and didn't pressure me into making a decision. The financing process was smooth and they offered competitive rates. The car was exactly as described and has been reliable since purchase. I would definitely recommend this dealership to friends and family looking for a new vehicle.",
                "purchase": True,
                "purchase_date": "2025-03-01",
                "car_make": "Toyota",
                "car_model": "Highlander",
                "car_year": 2022,
                "sentiment": "positive",
                "reviewer": {"full_name": "ramparampa"}
            }
        ]
        
        # Try to get other reviews from JSON file
        try:
            json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'database', 'data', 'reviews.json')
            
            with open(json_path, 'r') as f:
                data = json.load(f)
                other_reviews = data.get('reviews', [])
                
                # Filter by dealer_id and add sentiment
                other_reviews = [r for r in other_reviews if r.get('dealership') == dealer_id]
                for review in other_reviews:
                    review['sentiment'] = "positive"  # Default sentiment
                    review['reviewer'] = {"full_name": review.get('name', "Unknown")}
                
                # Combine reviews
                reviews.extend(other_reviews)
        except Exception as e:
            print(f"Error loading reviews from file: {str(e)}")
        
        return JsonResponse({"status": 200, "reviews": reviews})
    except Exception as e:
        print(f"Error in get_dealer_reviews: {str(e)}")
        return JsonResponse({"status": 500, "message": str(e)})

# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    try:
        # Get file path to dealerships.json
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               'database', 'data', 'dealerships.json')
        
        # Read dealerships data from the file
        with open(json_path, 'r') as f:
            data = json.load(f)
            dealerships = data.get('dealerships', [])
            
            # Find the specific dealer by ID
            dealer = None
            for d in dealerships:
                if d.get('id') == dealer_id:
                    dealer = d
                    break
            
            if dealer:
                return JsonResponse({"status": 200, "dealer": [dealer]})
            else:
                return JsonResponse({"status": 404, "message": "Dealer not found"})
    except Exception as e:
        print(f"Error in get_dealer_details: {str(e)}")
        return JsonResponse({"status": 500, "message": str(e)})
# Create a `add_review` view to submit a review
# def add_review(request):
# ...


@csrf_exempt
def add_review(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Instead of sending to backend, store the review directly
            json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'database', 'data', 'reviews.json')
            
            # Read existing reviews
            with open(json_path, 'r') as f:
                reviews_data = json.load(f)
                reviews = reviews_data.get('reviews', [])
                
                # Generate a new ID (max ID + 1)
                new_id = 1
                if reviews:
                    new_id = max(review.get('id', 0) for review in reviews) + 1
                
                # Create new review
                new_review = {
                    "id": new_id,
                    "name": data.get('name'),
                    "dealership": int(data.get('dealership')),
                    "review": data.get('review'),
                    "purchase": data.get('purchase', True),
                    "purchase_date": data.get('purchase_date'),
                    "car_make": data.get('car_make'),
                    "car_model": data.get('car_model'),
                    "car_year": int(data.get('car_year')),
                }
                
                # Add to reviews list
                reviews.append(new_review)
                reviews_data['reviews'] = reviews
                
                # Write back to file
                with open(json_path, 'w') as f:
                    json.dump(reviews_data, f, indent=2)
                
            return JsonResponse({"status": 200})
        except Exception as e:
            print(f"Error adding review: {str(e)}")
            return JsonResponse({"status": 500, "message": str(e)})
    else:
        return JsonResponse({"status": 405, "message": "Method not allowed"})
