from django.shortcuts import render, HttpResponse

# Create your views here.
def home(request):
    return HttpResponse("Hello World")

def openai_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')

        openai_api_key = 'YOUR_AZURE_OPENAI_API_KEY'
        openai_endpoint = 'YOUR_AZURE_OPENAI_ENDPOINT'
        deployment_name = 'YOUR_DEPLOYMENT_NAME'

        try:

            client = AzureOpenAI(
                api_key=openai_api_key,
                api_version="2023-05-15",
                azure_endpoint=openai_endpoint
            )

            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "user", "content": user_input}
                ]
            )
            
            ai_response = response.choices[0].message.content
            return render(request, 'ai_models/openai.html', {'response': ai_response, 'input': user_input})
            
        except Exception as e:
            return render(request, 'ai_models/openai.html', {'error': str(e)})
            
    return render(request, 'ai_models/openai.html')

def claude_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        

        claude_api_key = 'YOUR_ANTHROPIC_API_KEY'
        
        try:
        
            client = anthropic.Client(api_key=claude_api_key)
            
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": user_input}
                ]
            )
            
            ai_response = response.content[0].text
            return render(request, 'ai_models/claude.html', {'response': ai_response, 'input': user_input})
            
        except Exception as e:
            return render(request, 'ai_models/claude.html', {'error': str(e)})
            
    return render(request, 'ai_models/claude.html')
