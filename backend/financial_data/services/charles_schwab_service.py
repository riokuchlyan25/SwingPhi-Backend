from financial_data.config import PHI_RESEARCH_CHARLES_SCHWAB_KEY, PHI_RESEARCH_CHARLES_SCHWAB_SECRET 

# external
import requests
import base64

# built-in
from django.http import JsonResponse

def charles_schwab_api(request):
    """
    Initiate Charles Schwab OAuth 2.0 authentication flow
    """
    if request.method == 'GET':
        # Build the authorization URL
        auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={PHI_RESEARCH_CHARLES_SCHWAB_KEY}&redirect_uri=http://127.0.0.1:8000/charles_schwab_callback"
        
        print(f"auth_url: {auth_url}")
        
        # Return the authorization URL for the client to redirect to
        return JsonResponse({
            'auth_url': auth_url,
            'message': 'Redirect to this URL to authenticate with Charles Schwab'
        })
    
    return JsonResponse({'error': 'GET required'}, status=400)

def charles_schwab_callback(request):
    """
    Handle the OAuth callback from Charles Schwab and exchange authorization code for tokens
    """
    if request.method == 'GET':
        # Get the authorization code from the callback URL
        auth_code = request.GET.get('code')
        
        if not auth_code:
            return JsonResponse({'error': 'Authorization code not found'}, status=400)
        
        # Clean up the authorization code (remove any URL encoding artifacts)
        if '%40' in auth_code:
            auth_code = auth_code.replace('%40', '@')
        
        # Prepare credentials for token exchange
        credentials = f"{PHI_RESEARCH_CHARLES_SCHWAB_KEY}:{PHI_RESEARCH_CHARLES_SCHWAB_SECRET}"
        base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        
        # Prepare headers and payload for token request
        headers = {
            "Authorization": f"Basic {base64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": "http://127.0.0.1:8000/charles_schwab_callback",
        }
        
        try:
            # Exchange authorization code for access and refresh tokens
            token_response = requests.post(
                url="https://api.schwabapi.com/v1/oauth/token",
                headers=headers,
                data=payload,
            )
            
            if token_response.status_code == 200:
                token_data = token_response.json()
                
                # Store tokens securely (in a real application, you'd want to store these in a database or secure storage)
                # For now, we'll just return them in the response
                return JsonResponse({
                    'success': True,
                    'message': 'Successfully authenticated with Charles Schwab',
                    'access_token': token_data.get('access_token'),
                    'refresh_token': token_data.get('refresh_token'),
                    'expires_in': token_data.get('expires_in'),
                    'token_type': token_data.get('token_type')
                })
            else:
                return JsonResponse({
                    'error': 'Failed to exchange authorization code for tokens',
                    'details': token_response.text
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'error': 'An error occurred during token exchange',
                'details': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'GET required'}, status=400)

def charles_schwab_refresh_token(request):
    """
    Refresh Charles Schwab access token using refresh token
    """
    if request.method == 'POST':
        refresh_token = request.POST.get('refresh_token')
        
        if not refresh_token:
            return JsonResponse({'error': 'Refresh token required'}, status=400)
        
        # Prepare credentials
        credentials = f"{PHI_RESEARCH_CHARLES_SCHWAB_KEY}:{PHI_RESEARCH_CHARLES_SCHWAB_SECRET}"
        base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {base64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        
        try:
            refresh_response = requests.post(
                url="https://api.schwabapi.com/v1/oauth/token",
                headers=headers,
                data=payload,
            )
            
            if refresh_response.status_code == 200:
                token_data = refresh_response.json()
                return JsonResponse({
                    'success': True,
                    'message': 'Successfully refreshed access token',
                    'access_token': token_data.get('access_token'),
                    'expires_in': token_data.get('expires_in'),
                    'token_type': token_data.get('token_type')
                })
            else:
                return JsonResponse({
                    'error': 'Failed to refresh access token',
                    'details': refresh_response.text
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'error': 'An error occurred during token refresh',
                'details': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=400)
