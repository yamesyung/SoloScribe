import os
import shutil
import tempfile
import subprocess
from datetime import datetime

from django.contrib import messages
from django.shortcuts import redirect
from django.http import FileResponse, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.conf import settings


@login_required()
def export_db(request):
    db = settings.DATABASES["default"]
    filename = f"backup_{datetime.now():%Y%m%d_%H%M%S}.dump"
    tmp_path = os.path.join(tempfile.gettempdir(), filename)

    cmd = [
        "pg_dump",
        "-h", db["HOST"],
        "-p", str(db["PORT"] or 5432),
        "-U", db["USER"],
        "-d", db["NAME"],
        "-F", "c",
        "-f", tmp_path,
    ]
    result = subprocess.run(cmd, env={"PGPASSWORD": db["PASSWORD"]}, capture_output=True, text=True)

    if result.returncode != 0:
        return HttpResponseServerError(f"Export failed: {result.stderr}")

    response = FileResponse(open(tmp_path, "rb"), as_attachment=True, filename=filename)
    return response


@login_required()
def import_db(request):
    if request.method != "POST":
        return redirect("settings")

    uploaded = request.FILES.get("backup-file")
    if not uploaded:
        messages.error(request, "No file selected.")
        return redirect("settings")

    tmp_path = os.path.join(tempfile.gettempdir(), uploaded.name)
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(uploaded, f)

    db = settings.DATABASES["default"]
    cmd = [
        "pg_restore",
        "-h", db["HOST"],
        "-p", str(db["PORT"] or 5432),
        "-U", db["USER"],
        "-d", db["NAME"],
        "--clean", "--if-exists", "-1",
        tmp_path,
    ]
    result = subprocess.run(cmd, env={"PGPASSWORD": db["PASSWORD"]}, capture_output=True, text=True)
    os.remove(tmp_path)

    if result.returncode != 0:
        messages.error(request, f"Import failed: {result.stderr}")
    else:
        messages.success(request, "Database imported successfully.")

    return redirect("login_page")
