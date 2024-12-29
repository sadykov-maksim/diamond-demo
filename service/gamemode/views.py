from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse

from .models import Room
# Create your views here.

def index(request):
    return render(request, 'gamemode/index.html')

def get_room(request):
    if request.method == "POST":
        name = request.POST.get("name", None)
        if name:
            room = Room.objects.create(name=name, host=request.user)
            HttpResponseRedirect(reverse("room", args=[room.pk]))
    return render(request, 'chat/index.html')

def room(request, pk):
    room: Room = get_object_or_404(Room, pk=pk)
    return render(request, 'chat/room.html', {
        "room":room,
    })

def check_spin_history(request):
    # Здесь вы можете передать какие-либо данные в контекст, если необходимо
    return render(request, 'gamemode/check_spin_history.html')