import re

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import DynamicNamesForm
from .models import Submission


_NAME_KEY_RE = re.compile(r"^name(\d+)?$")


def _extract_inputs(post_data) -> list[str]:
    pairs: list[tuple[int, str]] = []
    for key, value in post_data.items():
        match = _NAME_KEY_RE.match(key)
        if not match:
            continue

        suffix = match.group(1)
        index = -1 if suffix is None else int(suffix)
        if value is None:
            continue
        normalized = str(value).strip()
        if normalized == "":
            continue
        pairs.append((index, normalized))
    pairs.sort(key=lambda p: p[0])
    return [v for _, v in pairs]


def submit(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = DynamicNamesForm(request.POST)
        if form.is_valid():
            inputs = _extract_inputs(request.POST)
            submission = Submission.objects.create(data={"inputs": inputs})
            return redirect(reverse("dynamicjson:result", args=[submission.pk]))
    else:
        form = DynamicNamesForm()

    return render(request, "dynamicjson/submit.html", {"form": form})


def result(request: HttpRequest, pk: int) -> HttpResponse:
    submission = get_object_or_404(Submission, pk=pk)
    inputs = (submission.data or {}).get("inputs", [])
    return render(
        request,
        "dynamicjson/result.html",
        {"submission": submission, "inputs": inputs},
    )
