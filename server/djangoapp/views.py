from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer,CarModel,CarMake
from .restapis import get_dealers_from_cf,get_dealer_reviews_from_cf,post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)
dealership_list=[]

# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context={}
    if request.method=="GET":
        return render(request,'djangoapp/about.html',context)


# Create a `contact` view to return a static contact page
def contact(request):
    context={}
    if request.method=="GET":
        return render(request,'djangoapp/contact.html',context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username,password = password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message']="Invalid username or password."
            return render(request,'djangoapp/login.html',context)
    else:
        return render(request,'djangoapp/login.html',context)

# ...

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')
# ...

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context={}
    if request.method=='GET':
        return render(request,'djangoapp/registration.html',context)
    elif request.method=='POST':
        #Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True 
        except:
            logger.error('New user')
        if not user_exist:
            user  = User.objects.create_user(username=username, first_name = first_name, last_name = last_name, password=password)
            login(request,user)
            return redirect('djangoapp:index')
        else:
            context['message']="User already exists!"
            return render(request,'djangoapp/registration.html',context)
# ...

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    global dealership_list
    context = {}
    if request.method == "GET":
        url="https://us-south.functions.appdomain.cloud/api/v1/web/90a255d5-a3d1-4958-9023-9390b8c80688/dealership-package/get-dealership"
        dealership_list = get_dealers_from_cf(url)
        # Concat all dealer's short name 
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        context["dealership_list"]=dealership_list
        # return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request,dealer_id):
    global dealership_list
    context={}
    if request.method=="GET":
        url="https://us-south.functions.appdomain.cloud/api/v1/web/90a255d5-a3d1-4958-9023-9390b8c80688/dealership-package/get-review"
        dealer_reviews = get_dealer_reviews_from_cf(url,int(dealer_id))
        dealer_name = dealership_list[dealer_id-1].full_name
        context={"review_list":dealer_reviews,
                 "dealer_name":dealer_name,
                 "dealer_id":dealer_id}
        return render(request,'djangoapp/dealer_details.html',context)
        #return render(request, 'djangoapp/index.html', context)


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request,dealer_id):
    context = {}
    #if request.method=="POST":
    # username = request.POST['username']
    # password = request.POST['psw']
    # user = authenticate(username=username,password = password)
    if request.user.is_authenticated:
        
        #print(cars)
        if request.method == "GET":
            cars=CarModel.objects.filter(dealerId=dealer_id).values()
            context["cars"]=cars
            dealer_name = dealership_list[dealer_id-1].full_name
            context["dealer_id"]=dealer_id
            context["dealer_name"]=dealer_name
            return render(request,'djangoapp/add_review.html',context)
        elif request.method == "POST":
            #print("Go here")
            review=dict()
            print(request.POST)
            #review["time"]=datetime.utcnow().isoformat()
            cars=CarModel.objects.filter(dealerId=dealer_id)
            review["dealership"]=dealer_id
            review['id']=1111
            review["review"]=request.POST['content']
            car = cars[int(request.POST['car'])-1]
            #carMake = CarMake.objects.get(id=car.carMake_id)
            review["car_make"]=  car.carMake.name
            review["car_model"]= car.name
            review["car_year"]= car.year.strftime("%Y")
            #review["dealership"]= 15
            review["name"]= "Hieu Tang"
            review["purchase"]= request.POST['purchasecheck']
            # {{car.name}}-{{car.make.name}}-{{ car.year|date:"Y" }}
            review["purchase_date"]= request.POST['purchasedate']
            json_payload=dict()
            json_payload["review"]=review
            url="https://us-south.functions.appdomain.cloud/api/v1/web/90a255d5-a3d1-4958-9023-9390b8c80688/dealership-package/get-review"
            post_request(url,json_payload)            
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
    else:
        context['message']="Only logged in users can post"
        return render(request,'djangoapp/login.html',context)
    


