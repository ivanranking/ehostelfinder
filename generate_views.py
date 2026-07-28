#!/usr/bin/env python3
"""Generate a complete, clean views.py with all functions properly indented."""
import ast

funcs_code = '''from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Avg
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json, os, urllib.request, urllib.error, uuid
from .forms import UserRegistrationForm, UserLoginForm, ForgotPasswordForm, ResetPasswordForm, ProfileUpdateForm, HostelUploadForm
from .models import Hostel, User, ContactMessage, Profile, Room, Booking, Review, Favorite, Message, Notification, Payment, RoomStatus, BookingStatus
from .local_ai import get_local_ai_response

KAMPALA_AREA_UNIVERSITIES = ["Makerere University", "Makerere University Business School", "Kyambogo University", "Kampala International University", "Uganda Christian University", "Ndejje University", "Bugema University", "Cavendish University Uganda", "St. Lawrence University Uganda", "Mutesa I Royal University"]
'''

with open('hostels/views_header.py', 'w', encoding='utf-8') as f:
    f.write(funcs_code)

print("Header written. Now writing all functions to views_funcs.py...")

# Read the gen_views_all.py to extract the function list but clean it
lines = open('gen_views_all.py', 'r', encoding='utf-8').readlines()

# Extract all lines that are function definitions
func_lines = []
for line in lines:
    if line.lstrip().startswith('def ') and '(' in line:
        func_lines.append(line.strip())

print("Functions to include:")
for f in func_lines:
    print(f"  {f}")
