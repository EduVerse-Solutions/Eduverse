"""Views for the core app."""

from django.contrib import messages
from django.shortcuts import redirect, render

from core.forms import InstitutionUpdateForm


def home(request):
    return render(
        request, template_name="core/home.html", context={"name": "Home"}
    )


def institution(request):
    return render(request, "core/institution.html", {"name": "Institution"})


def add_institution(request):
    if request.method == "POST":
        form = InstitutionUpdateForm(
            request.POST, instance=request.user.institution
        )
        if form.is_valid():
            institution = form.save(commit=False)
            institution.owner = request.user
            institution.save()
            messages.success(request, "Institution updated successfully.")
            return redirect("core:institution")
    else:
        form = InstitutionUpdateForm(instance=request.user.institution)

    return render(
        request,
        "core/institution_change_form.html",
        {
            "form": form,
            "name": "Update Institution",
        },
    )
