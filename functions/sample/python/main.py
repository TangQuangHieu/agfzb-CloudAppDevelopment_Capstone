"""IBM Cloud Function that gets all reviews for a dealership

Returns:
    List: List of reviews for the given dealership
"""
import cloudant
from cloudant.client import Cloudant
from cloudant.error import CloudantException
import requests


def main(param_dict):
    """Main Function

    Args:
        param_dict (Dict): input paramater

    Returns:
        _type_: _description_ TODO
    """

    try:
        client = Cloudant.iam(
            account_name=param_dict["COUCH_USERNAME"],
            api_key=param_dict["IAM_API_KEY"],
            connect=True,
        )
        
        # Open an existing database
        db = cloudant.database.CloudantDatabase(client,"reviews")
        if param_dict.get("__ow_method")=='post':
            review = param_dict.get("review")
            dealer_id = review.get('dealership')
            for doc in db:
                if doc['id']==dealer_id:
                    doc['another']=review['another']
                    doc['car_make']=review['car_make']
                    doc['car_model']=review['car_model']
                    doc['car_year']=int(review['car_year'])
                    doc['id']=int(review['id'])
                    doc['name']=review['name']
                    doc['purchase']=review['purchase']
                    doc['purchase_date']=review['purchase_date']
                    doc['review']=review['review']
                    doc.save()
                    return {
                    'statusCode': 200,
                    'body': ["Review updated!",doc]
                    } 
            review['car_year']=int(review['car_year'])
            review['id']=int(review['id'])
            review['dealership']=int(dealer_id)
            doc = db.create_document(review)
            # results=[]
            # for doc in db:
            #     results.append(doc)
            return {
                'statusCode': 200,
                    'body': ["Review added!",doc]
            }
        else:
            dealer_id = int(param_dict.get('dealerId'))
            results=[]
            for doc in db:
                #print(document)
                if dealer_id is None:
                    results.append(doc)
                elif int(doc['dealership'])==dealer_id:
                    results.append(doc)
            return {
                'statusCode': 200,
                'body': results
            }
    except CloudantException as cloudant_exception:
        print("unable to connect")
        return {
        'statusCode': 404,
        'body': "Cloud error",
        }
    except (requests.exceptions.RequestException, ConnectionResetError) as err:
        print("connection error")
        return {
        'statusCode': 404,
        'body': "Connection error",
        }

    
