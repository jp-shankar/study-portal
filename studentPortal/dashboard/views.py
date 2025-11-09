from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from django.views import generic
from yt_dlp import YoutubeDL
from datetime import datetime
import requests
import wikipedia
from wikipedia.exceptions import DisambiguationError
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, "dashboard/home.html")


@login_required
def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(
                user=request.user,
                title=request.POST["title"],
                description=request.POST["description"],
            )
            notes.save()
        messages.success(
            request, f"Notes Added from {request.user.username} Successfully!"
        )
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {"notes": notes, "form": form}
    return render(request, "dashboard/notes.html", context)


@login_required
def delete_note(request, pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")


class NotesDetailView(generic.DetailView):
    model = Notes


@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == "on":
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks = Homework(
                user=request.user,
                subject=request.POST["subject"],
                title=request.POST["title"],
                description=request.POST["description"],
                due=request.POST["due"],
                is_finished=finished,
            )
            homeworks.save()
            messages.success(request, f"Homework Added from {request.user.username}!!")

            return redirect("homework")
    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context = {"homeworks": homework, "homeworks_done": homework_done, "form": form}
    return render(request, "dashboard/homework.html", context)


@login_required
def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect("homework")


@login_required
def delete_homework(request, pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")


def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST.get("text", "").strip()

        if not text:
            context = {"form": form, "error": "Please enter a search query."}
            return render(request, "dashboard/youtube.html", context)

        ydl_opts = {
            "quiet": True,
            "extract_flat": False,
            "skip_download": True,
            "ffmpeg_location": r"D:\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin",
            "format": "best[height<=720]",
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch5:{text}", download=False)

            result_list = []
            for i in info.get("entries", []):
                duration_seconds = int(i.get("duration", 0) or 0)

                formatted_duration = (
                    f"{duration_seconds // 3600}:{(duration_seconds % 3600) // 60:02d}:{duration_seconds % 60:02d}"
                    if duration_seconds >= 3600
                    else f"{duration_seconds // 60}:{duration_seconds % 60:02d}"
                )

                upload_date = i.get("upload_date")
                formatted_date = (
                    datetime.strptime(upload_date, "%Y%m%d").strftime("%d %B %Y")
                    if upload_date
                    else "Unknown Date"
                )

                description = (
                    i.get("description", "").strip() or "No Description Available"
                )
                thumbnail = i.get("thumbnail") or i.get("thumbnails", [{}])[0].get(
                    "url", ""
                )

                result_dict = {
                    "title": i.get("title", "No Title"),
                    "thumbnail": thumbnail,
                    "channel": i.get("uploader", "Unknown Channel"),
                    "views": (
                        f"{i.get('view_count', 0):,} views"
                        if i.get("view_count")
                        else "No Views"
                    ),
                    "duration": formatted_duration,
                    "published": formatted_date,
                    "link": i.get("webpage_url", "#"),
                    "description": (
                        description[:300] + "..."
                        if len(description) > 300
                        else description
                    ),
                }
                result_list.append(result_dict)

            context = {"form": form, "results": result_list}

        except Exception as e:
            context = {"form": form, "error": f"An error occurred: {str(e)}"}

        return render(request, "dashboard/youtube.html", context)

    else:
        form = DashboardForm()

    context = {"form": form}
    return render(request, "dashboard/youtube.html", context)


@login_required
def todo(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == "on":
                    finished = True
                else:
                    finished = False
            except:
                finished = False

            todos = Todo(
                user=request.user, title=request.POST["title"], is_finished=finished
            )
            todos.save()
            messages.success(request, f"Todo added from {request.user.username}!!")
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {"todos": todo, "form": form, "todos_done": todos_done}
    return render(request, "dashboard/todo.html", context)


@login_required
def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    todo.is_finished = not todo.is_finished
    todo.save()
    return redirect("todo")


@login_required
def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")


def books(request):
    form = DashboardForm(request.POST or None)
    results = []
    message = ""

    if request.method == "POST" and form.is_valid():
        text = form.cleaned_data.get("text", "")
        url = f"https://www.googleapis.com/books/v1/volumes?q={text}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if "items" in data:
                for item in data["items"][:10]:
                    info = item.get("volumeInfo", {})
                    results.append(
                        {
                            "title": info.get("title", "N/A"),
                            "subtitle": info.get("subtitle", "N/A"),
                            "description": info.get(
                                "description", "No description available"
                            ),
                            "count": info.get("pageCount", "N/A"),
                            "categories": info.get("categories", []),
                            "rating": info.get("averageRating", "N/A"),
                            "thumbnail": info.get("imageLinks", {}).get(
                                "thumbnail", ""
                            ),
                            "preview": info.get("previewLink", "#"),
                        }
                    )
            else:
                message = "No results found"
        else:
            message = "Failed to fetch data from API"

    return render(
        request,
        "dashboard/books.html",
        {"form": form, "results": results, "message": message},
    )


def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST.get("text", "").strip()

        url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            entry = data[0] if data else {}

            phonetics = entry.get("phonetics", [{}])[0].get("text", "N/A")
            audio = entry.get("phonetics", [{}])[0].get("audio", "")

            meaning = entry.get("meanings", [{}])[0]

            definition = meaning.get("definitions", [{}])[0].get(
                "definition", "No definition available"
            )
            example = meaning.get("definitions", [{}])[0].get(
                "example", "No example available"
            )

            context = {
                "form": form,
                "input": text,
                "phonetics": phonetics,
                "audio": audio,
                "definition": definition,
                "example": example,
            }
        else:
            context = {"form": form, "error": "Word not found. Try again!"}

        return render(request, "dashboard/dictionary.html", context)

    else:
        form = DashboardForm()
        return render(request, "dashboard/dictionary.html", {"form": form})


def wiki(request):
    if request.method == "POST":
        text = request.POST["text"]
        form = DashboardForm(request.POST)

        try:
            search = wikipedia.page(text)
            context = {
                "form": form,
                "title": search.title,
                "link": search.url,
                "details": search.summary,
            }
        except DisambiguationError as e:
            context = {
                "form": form,
                "error": f"The term '{text}' may refer to: {', '.join(e.options)}",
            }
        except wikipedia.exceptions.HTTPTimeoutError:
            context = {
                "form": form,
                "error": "Request timed out. Please try again later.",
            }
        except wikipedia.exceptions.PageError:
            context = {
                "form": form,
                "error": f"Page for '{text}' not found. Please check the term and try again.",
            }

        return render(request, "dashboard/wiki.html", context)
    else:
        form = DashboardForm()
        context = {"form": form}
    return render(request, "dashboard/wiki.html", context)


def conversion(request):
    answer = ""
    measurement_form = None

    length_factors = {
        "yard": 0.9144,
        "foot": 0.3048,
        "meter": 1,
        "kilometer": 1000,
        "centimeter": 0.01,
        "inch": 0.0254,
    }

    mass_factors = {
        "pound": 0.453592,
        "kilogram": 1,
        "ton": 1000,
        "gram": 0.001,
        "milligram": 0.000001,
    }

    if request.method == "POST":
        form = ConversionForm(request.POST)

        if form.is_valid():
            measurement_type = form.cleaned_data["measurement"]

            if measurement_type == "length":
                measurement_form = ConversionLengthForm(request.POST)

                if measurement_form.is_valid():
                    first = measurement_form.cleaned_data["measure1"].lower()
                    second = measurement_form.cleaned_data["measure2"].lower()
                    input_value = measurement_form.cleaned_data["input"]

                    if input_value and float(input_value) >= 0:
                        value = float(input_value)

                        if first in length_factors and second in length_factors:
                            result = (value * length_factors[first]) / length_factors[
                                second
                            ]
                            answer = f"{input_value} {first} = {result:.6f} {second}"
                        else:
                            answer = "Invalid length conversion pair selected."

            elif measurement_type == "mass":
                measurement_form = ConversionMassForm(request.POST)

                if measurement_form.is_valid():
                    first = measurement_form.cleaned_data["measure1"].lower()
                    second = measurement_form.cleaned_data["measure2"].lower()
                    input_value = measurement_form.cleaned_data["input"]

                    if input_value and float(input_value) >= 0:
                        value = float(input_value)

                        if first in mass_factors and second in mass_factors:
                            result = (value * mass_factors[first]) / mass_factors[
                                second
                            ]
                            answer = f"{input_value} {first} = {result:.6f} {second}"
                        else:
                            answer = "Invalid mass conversion pair selected."

    else:
        form = ConversionForm()

    context = {
        "form": form,
        "m_form": measurement_form,
        "input": request.method == "POST",
        "answer": answer,
    }

    return render(request, "dashboard/conversion.html", context)


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Account Created for {username}!!")
            return redirect("login")
    else:
        form = UserRegistrationForm()
    context = {"form": form}
    return render(request, "dashboard/register.html", context)


@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)
    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False
    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
        "homeworks": homeworks,
        "todos": todos,
        "homework_done": homework_done,
        "todos_done": todos_done,
    }

    return render(request, "dashboard/profile.html", context)


def custom_logout(request):
    logout(request)
    return render(request, "dashboard/logout.html")
