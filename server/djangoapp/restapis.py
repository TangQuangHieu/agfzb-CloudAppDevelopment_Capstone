import requests
import json
from .models import CarDealer,DealerView
from requests.auth import HTTPBasicAuth
import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
# def get_request(url, **kwargs):
#     print(kwargs)
#     print("GET from {}".format(url))
#     try:
#         #if api_key == "":
#         #    # Call get method of requests library with URL and parameters 
#         response = requests.get(url, headers={'Content-Type':'application/json'},
#         params=kwargs)
#         # else:
#         #     params=dict()
#         #     params["text"]=kwargs["text"]
#         #     params["version"]=kwargs["version"]
#         #     params["features"]=kwargs["features"]
#         #     params["return_analyzed_text"]=kwargs["return_analyzed_text"]
#         #     response = requests.get(url, headers={'Content-Type':'application/json'},
#         #     aut=HTTPBasicAuth('apikey',api_key),params=params)
#     except:
#         # If any error occurs 
#         print("Network exception occured")
#     status_code = response.status_code 
#     print("With status {}".format(status_code))
#     json_data = json.loads(response.text)
#     return json_data 


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url,json_payload,**kwargs):
    return requests.post(url,params=kwargs,json=json_payload)



# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url,**kwargs):
    results=[] 
    # Call get_request with a URL parameter 
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers 
        dealers = json_result["allRecords"]["result"]
        # For each dealer object 
        for dealer in dealers:
            # Get its content in `doc` object 
            #dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object 
            dealer_obj = CarDealer(address = dealer['address'],
            city=dealer['city'],full_name=dealer['full_name'],
            id=dealer['id'],lat=dealer['lat'],long=dealer['long'],
            short_name=dealer['short_name'],st=dealer['st'],zip=dealer['zip'])
            results.append(dealer_obj)
    return results



# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
# def get_dealer_by_id_from_dc(url,dealerId):
def get_request(url,dealerID=None,**kwargs):
    #print("dealerID:",dealerID)
    #print("GET from {}".format(url))
    if dealerID is not None:
        url="{}?dealerId={}".format(url,dealerID)
    #print("Full url: ",url)
    try:
        # Call get method of requests library with URL and parameters 
        response = requests.get(url, headers={'Content-Type':'application/json'},
        params=kwargs)
    except:
        # If any error occurs 
        print("Network exception occured")
    status_code = response.status_code 
    print("With status {}".format(status_code))
    json_data = json.loads(response.text)
    return json_data 

def get_dealer_reviews_from_cf(url,dealerId):
    results=[] 
    # Call get_request with a URL parameter 
    json_result = get_request(url,dealerId)
    if json_result:
        # Get the row list in JSON as reviews 
        # dealers = json_result["allRecords"]["result"]
        # For each dealer object 
        for review in json_result:
            # Get its content in `doc` object 
            #dealer_doc = dealer
            # Create a DealerView object with values in `doc` object 
            #         def __init__(self,dealership,name,purchase,
            # review,purchase_date,car_make,car_model,car_year,sentiment,id)
            #print(review)
            sentiment = analyze_review_sentiments(review['review'])
            review_obj = DealerView(dealership=review['dealership'],name=review['name'],
            purchase=review['purchase'],review=review['review'],purchase_date=review['purchase_date'],
            car_make=review['car_make'],car_model=review['car_model'],car_year=review['car_year'],
            sentiment=sentiment,id=review['id'])
            results.append(review_obj)
    return results



# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    #TODO 
    api_key="jKw__MirWb0dXfj2qjQgQ34T4dxd6PZQZ1LUiUiZzo0l"
    url="https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/89b8efb0-cea1-4696-a2d7-549652c81aad"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze(
        text=text,features=Features(sentiment=SentimentOptions()),language='en').get_result()
    #print(response)
    return response['sentiment']['document']['label']

