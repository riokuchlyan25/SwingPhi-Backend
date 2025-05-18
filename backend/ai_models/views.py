from django.shortcuts import render, HttpResponse

# Create your views here.
def home(request):
    return HttpResponse("Hello World")

def openai_view(request):
    return render(request, 'ai_models/openai.html')

def claude_view(request):
    return render(request, 'ai_models/claude.html')
