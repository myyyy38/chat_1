from django.shortcuts import render


# Create your views here.

def entrance(request):
    print("entrance実行")
    return render(request,'chat/entrance.html')

def chat(request):
    print("chat実行")
    return render(request,'chat/chat.html')