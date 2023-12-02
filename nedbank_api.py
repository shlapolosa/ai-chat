import time
import uuid
import decimal
import random

import requests
from django.conf import settings
import json

from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse


# Retrieve the client_id and client_secret from the .env file

# Create your views here.
def token_light(scope: str) -> str:
    # Define the URL and the payload
    url = "https://api.nedbank.co.za/apimarket/sandbox/nboauth/oauth20/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": settings.NB_CLIENT_ID,
        "client_secret": settings.NB_CLIENT_SECRET,
        "scope": scope
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=payload, headers=headers)
    return response.json().get('access_token')


def create_account_intent(bearer_token: str) -> (str, str):
    url = "https://api.nedbank.co.za/apimarket/sandbox/open-banking/v3.1/aisp/account-access-consents"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}",
        "x-fapi-financial-id": settings.NB_FINANCIAL_ID,
        "x-fapi-interaction-id": f"account-list",  # TODO: add counter / identifier?
        "x-ibm-client-id": settings.NB_CLIENT_ID,
        "x-ibm-client-secret": settings.NB_CLIENT_SECRET
    }

    body = {
        "Data": {
            "Permissions": [
                "ReadAccountsDetail",
                "ReadBalances",
                "ReadProducts",
                "ReadTransactionsCredits",
                "ReadTransactionsDebits",
                "ReadTransactionsDetail"
            ],
            "ExpirationDateTime": "2024-10-26T00:00:00.000Z",
            "TransactionFromDateTime": "2022-05-03T00:00:00.000Z",
            "TransactionToDateTime": "2022-12-03T00:00:00.000Z"
        },
        "Risk": {}
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    data = response.json()
    consent_id = data.get("Data").get("ConsentId")
    redirect_url = data.get('Links').get("SCARedirectURL")
    return consent_id, redirect_url


def create_payment_intent(bearer_token: str, amount: decimal.Decimal) -> (str, str):
    url = 'https://api.nedbank.co.za/apimarket/sandbox/open-banking/v3.1/pisp/domestic-payment-consents'
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}",
        "x-fapi-financial-id": settings.NB_FINANCIAL_ID,
        "x-idempotency-key": str(random.randint(0, 1_000_000_000)),
        "x-ibm-client-id": settings.NB_CLIENT_ID,
        "x-ibm-client-secret": settings.NB_CLIENT_SECRET
    }
    body = {
        "Data": {
            "ReadRefundAccount": "Yes",
            "Initiation": {
                "InstructionIdentification": "payment-request",  # TODO: add identifier
                "EndToEndIdentification": "payment-end-end",
                "InstructedAmount": {
                    "Amount": f"{amount}",
                    "Currency": "ZAR"
                },
                "CreditorAccount": {
                    "SchemeName": "SortCodeAccountNumber",
                    "Identification": "1987651009427726",
                    "Name": "ACME Inc",
                    "SecondaryIdentification": "1009427726"
                },
                "RemittanceInformation": {
                    "Unstructured": "Instant EFT - RAND-I",
                    "Reference": "PAYMENT REF FOR RANDI"
                }
            }
        },
        "Risk": {
            "PaymentContextCode": "EcommerceMerchantInitiatedPayment",
            "ContractPresentInidicator": False,
            "PaymentPurposeCode": "EPAY",
            "BeneficiaryPrepopulatedIndicator": False,
            "BeneficiaryAccountType": "Business",
            "MerchantCustomerIdentification": "1234567891",
            "DeliveryAddress": {
                "AddressLine": [
                    "25 Queen Victoria Street",
                    "Acacia Lodge"
                ],
                "StreetName": "Kromdraai Road",
                "BuildingNumber": "25",
                "PostCode": "7872",
                "TownName": "Hout Bay",
                "CountrySubDivision": "Gauteng",
                "Country": "ZA"
            }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    data = response.json()
    consent_id = data.get("Data").get("ConsentId")
    redirect_url = data.get('Links').get("SCARedirectURL")
    return consent_id, redirect_url


def get_intent(consent_id: str, bearer_token: str) -> str:
    url = f"https://api.nedbank.co.za/apimarket/sandbox/open-banking/v3.1/aisp/account-access-consents/{consent_id}"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "x-fapi-financial-id": settings.NB_FINANCIAL_ID,
        "x-ibm-client-id": settings.NB_CLIENT_ID,
        "x-ibm-client-secret": settings.NB_CLIENT_SECRET,
    }
    response = requests.get(url, headers=headers)
    data = response.json().get("Data")
    return data.get('ConsentId')


def funds_available(consent_id: str, bearer_token: str) -> str:
    url = f"https://api.nedbank.co.za/apimarket/sandbox/open-banking/v3.1/pisp/domestic-payment-consents/{consent_id}/funds-confirmation"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "x-fapi-financial-id": settings.NB_FINANCIAL_ID,
        "x-ibm-client-id": settings.NB_CLIENT_ID,
        "x-ibm-client-secret": settings.NB_CLIENT_SECRET,
    }
    response = requests.get(url, headers=headers)
    return response.json().get("Data").get('FundsAvailable')


def submit_payment(bearer_token):
    # funds_available

    url = 'https://api.nedbank.co.za/apimarket/sandbox/open-banking/v3.1/pisp/domestic-payments'
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}",
        "x-fapi-financial-id": settings.NB_FINANCIAL_ID,
        "x-idempotency-key": int(time.time()),
        "x-ibm-client-id": settings.NB_CLIENT_ID,
        "x-ibm-client-secret": settings.NB_CLIENT_SECRET
    }



# def get_authorisation_url(consent_id: str) -> str:
#     url = "https://api.nedbank.co.za/apimarket/sandbox/nboauth/oauth20/authorize"
#     params = {
#         "client_id": settings.NB_CLIENT_ID,
#         "intentId": consent_id,
#         "redirect_url": settings.NB_REDIRECT_URL,
#         "scope": "openid,accounts",
#         "state": "accounts",  # I can name for internal use
#         "response_type": "code",
#         "itype": "accounts",
#     }
#     return f'{url}?{urlencode(params)}'


def token_heavy(code: str) -> dict[str, str]:
    url = "https://api.nedbank.co.za/apimarket/sandbox/nboauth/oauth20/token"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "client_id": settings.NB_CLIENT_ID,
        "client_secret": settings.NB_CLIENT_SECRET,
        "redirect_uri": settings.NB_REDIRECT_URL,
        "code": code,
        "grant_type": "authorization_code",
    }
    response = requests.post(url, data=payload, headers=headers)
    return response.json()


def account_authorisation_view(request):
    bearer_token = token_light("accounts")
    consent_id, redirect_url = create_account_intent(bearer_token)
    # consent_id = get_intent(consent_id, bearer_token)
    # url = get_authorisation_url(consent_id)
    return redirect(to=redirect_url)


def payment_authorisation_view(request):
    bearer_token = token_light("payments")

    amount = decimal.Decimal('53.6')
    consent_id, redirect_url = create_payment_intent(bearer_token, amount)
    request.session['payment_amount'] = str(amount)
    request.session['payment_consent_id'] = consent_id
    # consent_id = get_intent(consent_id, bearer_token)
    # url = get_authorisation_url(consent_id)
    return redirect(to=redirect_url)



def oauth_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    if code:
        if state == "payment-request":
            token_response = token_heavy(code)
            access_token = token_response.get("access_token")
            request.session['payment_refresh_token'] = token_response.get("refresh_token")
            request.session['payment_access_token'] = token_response.get("access_token")
            amount = request.session['payment_amount']
            consent_id = request.session['payment_consent_id']
            make_payment_function(amount, consent_id, access_token)
        else:
            token_response = token_heavy(code)
            request.session['refresh_token'] = token_response.get("refresh_token")
            request.session['access_token'] = token_response.get("access_token")
        # request.session.set_expiry(token_response.get("expires_id"))
        return HttpResponseRedirect(redirect_to=reverse('randi'))
    return render(request=request, template_name='randi/home.html', context={
        'error': request.GET.get('error'),
        'error_description': request.GET.get('error_description'),
    })


def get_accounts(request):
    url = "https://api.nedbank.co.za/apimarket/sandbox/open-banking/v3.1/aisp/accounts"
    headers = {
        "x-fapi-financial-id": settings.NB_FINANCIAL_ID,
        "Authorization": f"Bearer {request.session['access_token']}",
        "x-ibm-client-id": settings.NB_CLIENT_ID,
        "x-ibm-client-secret": settings.NB_CLIENT_SECRET,
    }
    response = requests.get(url, headers=headers)
    data = response.json().get("Data").get("Account")
    return render(request=request, template_name='randi/accounts.html', context={"data": data})



def make_payment_function(amount, consent_id, payment_access_token):
    url = "https://api.nedbank.co.za/apimarket/sandbox/open-banking/v3.1/pisp/domestic-payments"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-fapi-financial-id": settings.NB_FINANCIAL_ID,
        "Authorization": f"Bearer {payment_access_token}",
        "x-ibm-client-id": settings.NB_CLIENT_ID,
        "x-ibm-client-secret": settings.NB_CLIENT_SECRET,
        "x-idempotency-key": str(random.randint(0, 1_000_000_000)),
    }

    body = {
        "Data": {
            "ConsentId": consent_id,
            "Initiation": {
                "InstructionIdentification": "payment-request",  # TODO: add identifier same as intent
                "EndToEndIdentification": "payment-end-end",
                "InstructedAmount": {
                    "Amount": f"{amount}",
                    "Currency": "ZAR"
                },
                "CreditorAccount": {
                    "SchemeName": "SortCodeAccountNumber",
                    "Identification": "1987651009427726",
                    "Name": "ACME Inc",
                    "SecondaryIdentification": "1009427726"
                },
                "RemittanceInformation": {
                    "Reference": "PAYMENT REF FOR RANDI",
                    "Unstructured": "Instant EFT - RAND-I",
                }
            }
        },
        "Risk": {
            "PaymentContextCode": "EcommerceMerchantInitiatedPayment",
            "MerchantCustomerIdentification": "1234567891",
            "ContractPresentInidicator": False,
            "BeneficiaryPrepopulatedIndicator": False,
            "PaymentPurposeCode": "EPAY",
            "BeneficiaryAccountType": "Business",
            "DeliveryAddress": {
                "AddressLine": [
                    "25 Queen Victoria Street",
                    "Acacia Lodge"
                ],
                "StreetName": "Kromdraai Road",
                "BuildingNumber": "25",
                "PostCode": "7872",
                "TownName": "Hout Bay",
                "CountrySubDivision": "Gauteng",
                "Country": "ZA"
            }
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))
    data = response.json()
    return data


def make_payment(request):
    amount = request.session.get('payment_amount')
    consent_id = request.session.get('payment_consent_id')
    make_payment_function(amount, consent_id, payment_access_token=request.session['payment_access_token'])


def read_cache(key):
    with open('cache.json', 'r') as file:
        data = json.loads(file.read())
    return data[key]

def write_cache(key, value):
    try:
        with open('cache.json', 'r') as file:
            data = json.loads(file.read())
    except:
        data = {}

    data[key] = value
    with open('cache.json', 'w') as file:
        file.write(json.dumps(data))
    return data
