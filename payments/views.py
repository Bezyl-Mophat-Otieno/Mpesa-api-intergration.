import requests
import os
import base64
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from datetime import datetime
from django.views.decorators.http import require_POST, require_GET
#MPESA EXPRESS API
# Configuration constants
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
BASE_URL = os.getenv('BASE_URL')
PASS_KEY = os.getenv('PASS_KEY')
STKPUSH_BUSINESS_SHORTCODE = os.getenv('STKPUSH_BUSINESS_SHORTCODE')
C2B_BUSINESS_SHORTCODE = os.getenv('C2B_BUSINESS_SHORTCODE')
TOKEN_URL = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
STK_PUSH_URL = f"{BASE_URL}/mpesa/stkpush/v1/processrequest"
STKPUSH_STATUS_URL = f"{BASE_URL}/mpesa/stkpushquery/v1/query"
CTB_REGISTER_URL = f"{BASE_URL}/mpesa/c2b/v1/registerurl"

def generate_access_token():
    """Generate access token using consumer key and secret."""
    encoded_credentials = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {encoded_credentials}"}

    response = requests.get(TOKEN_URL, headers=headers, timeout=10)
    response.raise_for_status()  # Raise an error for bad responses
    token = response.json().get('access_token')
    return token

def generate_password():
    """Generate the password for STK push."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{STKPUSH_BUSINESS_SHORTCODE}{PASS_KEY}{timestamp}".encode()).decode()
    return password, timestamp

@require_GET
def get_access_token(request):
    """Get the access token for the application."""
    try:
        access_token = generate_access_token()
        return JsonResponse({'access_token': access_token })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def stk_push(request):
    """Initiate STK push request."""
    access_token = generate_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    password, timestamp = generate_password()
    payload = {
    "BusinessShortCode": STKPUSH_BUSINESS_SHORTCODE,
    "Password": password,
    "Timestamp": timestamp,
    "TransactionType": "CustomerPayBillOnline",
    "Amount": 1,
    "PartyA": 254702715906,
    "PartyB": 174379,
    "PhoneNumber": 254702715906,
    "CallBackURL": "https://webhook.site/735334c9-1c5e-4d96-ba25-df5a688206f8",
    "AccountReference": "1284859458848",
    "TransactionDesc": "Payment of X" 
}

    try:
        response = requests.post(STK_PUSH_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        return JsonResponse(response.json())
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=response.status_code)


def query_stkpush_status(access_token, checkout_request_id):
    """Query the stk push status using the checkout request ID."""
    headers = {"Authorization": f"Bearer {access_token}"}
    password, timestamp = generate_password()
    payload = {
    "BusinessShortCode": STKPUSH_BUSINESS_SHORTCODE,
    "Password": password,
    "Timestamp": timestamp,
    "CheckoutRequestID": checkout_request_id
    }

    response = requests.post(STKPUSH_STATUS_URL, json=payload, headers=headers, timeout=10)
    print(response.json())
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to query stk push status")

@require_GET
def stkpush_status(request):
    """Get the stkpush status using the checkout request ID. 
    Checks whether or not the push was made succcessfully"""
    access_token = generate_access_token()  # Call the function to get the token
    checkout_request_id = request.GET.get('checkout_request_id')

    try:
        response = query_stkpush_status(access_token, checkout_request_id)
        return JsonResponse(response)
    except Exception as e:        
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def stkpush_callback(request):
    """Handle the response from Mpesa back to our system"""
    data = request.body.decode('utf-8')
    print(data)
    return HttpResponse(data, content_type='application/json')
    
# MPESA C2B API
@require_GET
def c2b_url_registration(request):
    """Register the confirmation and validation URLs for C2B payments."""
    access_token = generate_access_token()  # Call the function to get the token
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "ShortCode": C2B_BUSINESS_SHORTCODE,
        "ResponseType": "Completed",
        "ConfirmationURL": "https://webhook.site/b49528e2-c9e7-403b-ad04-77f27c316498",
        "ValidationURL": "https://webhook.site/b49528e2-c9e7-403b-ad04-77f27c316498"
    }

    try:
        response = requests.post(CTB_REGISTER_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        return JsonResponse(response.json())
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)



@require_POST
def c2bpayment_confirmation(request):
    """ For those payments done outside the PTL system 
    mpesa will process the payments and send the processed 
    responses back to our system via this endpoint """

    data = request.body.decode('utf-8')
    print(data)
    return HttpResponse(data, content_type='application/json')
    