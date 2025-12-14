# apps/dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from apps import categories
from apps.locations.utils import find_best_matching_location

from apps.workers.models import Worker
from apps.tasks.models import Task
from apps.requirements.models import Requirement
from apps.categories.models import Category
from apps.calling_summary.models import CallingSummary

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from apps.workers.models import Worker

import json
import requests
from django.shortcuts import render, redirect
from apps.workers.models import Worker
from apps.categories.models import Category
from apps.locations.models import Location
from django.http import JsonResponse, HttpResponseBadRequest

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

from django.views.decorators.http import require_POST, require_GET
from apps.dashboard.utils import log_task_change, make_aware_datetime

# ============================================================
# LOGIN/LOGOUT VIEWS
# ============================================================

def admin_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    # Session expired
    msg = None
    if request.GET.get("session_expired"):
        msg = "Your session expired. Please login again."

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            return redirect("dashboard:home")
        else:
            msg = "Invalid username or password."

    return render(request, "dashboard/login.html", {"msg": msg})



@login_required(login_url='dashboard:login')
def admin_logout(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('dashboard:login')


# ============================================================
# DASHBOARD HOME
# ============================================================

@login_required(login_url='dashboard:login')
def dashboard_home(request):
    """Main dashboard - shows three main buckets"""
    
    # Statistics
    total_workers = Worker.objects.count()
    pending_workers = Worker.objects.filter(verification_status='pending').count()
    verified_workers = Worker.objects.filter(verification_status='verified').count()
    
    total_tasks = Task.objects.count()
    pending_tasks = Task.objects.filter(status='pending').count()
    active_tasks = Task.objects.filter(status='active').count()
    completed_tasks = Task.objects.filter(status='completed').count()
    
    total_requirements = Requirement.objects.count()
    pending_requirements = Requirement.objects.filter(status='pending').count()
    
    # Recent activities
    recent_workers = Worker.objects.order_by('-created_at')[:5]
    recent_tasks = Task.objects.order_by('-created_at')[:5]
    recent_requirements = Requirement.objects.order_by('-created_at')[:5]
    
    context = {
        'total_workers': total_workers,
        'pending_workers': pending_workers,
        'verified_workers': verified_workers,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'active_tasks': active_tasks,
        'completed_tasks': completed_tasks,
        'total_requirements': total_requirements,
        'pending_requirements': pending_requirements,
        'recent_workers': recent_workers,
        'recent_tasks': recent_tasks,
        'recent_requirements': recent_requirements,
    }
    
    return render(request, 'dashboard/home.html', context)


# ============================================================
# WORKER MANAGEMENT (BUCKET 1)
# ============================================================

# @login_required(login_url='dashboard:login')
# def worker_list(request):
#     """List all workers with filters"""
#     workers = Worker.objects.all().select_related('primary_category', 'location')
    
#     # Filters
#     status = request.GET.get('status')
#     category = request.GET.get('category')
#     search = request.GET.get('search')
    
#     if status:
#         workers = workers.filter(verification_status=status)
#     if category:
#         workers = workers.filter(primary_category_id=category)
#     if search:
#         workers = workers.filter(
#             Q(name__icontains=search) | 
#             Q(phone__icontains=search) |
#             Q(aadhar_no__icontains=search)
#         )
    
#     categories = Category.objects.filter(category_type='primary')
    
#     context = {
#         'workers': workers,
#         'categories': categories,
#         'selected_status': status,
#         'selected_category': category,
#         'search_query': search,
#     }
    
#     return render(request, 'dashboard/worker_list.html', context)


@login_required(login_url='dashboard:login')
def worker_detail(request, pk):
    """Worker detail view with actions"""
    worker = get_object_or_404(Worker, pk=pk)
    
    # Get worker's tasks
    worker_tasks = Task.objects.filter(worker=worker).order_by('-created_at')
    
    context = {
        'worker': worker,
        'worker_tasks': worker_tasks,
    }
    
    return render(request, 'dashboard/worker_detail.html', context)


@login_required(login_url='dashboard:login')
def worker_verify(request, pk):
    """Verify a worker"""
    worker = get_object_or_404(Worker, pk=pk)
    worker.verification_status = 'verified'
    worker.save()
    messages.success(request, f'Worker {worker.name} has been verified!')
    return redirect('dashboard:worker_detail', pk=pk)


@login_required(login_url='dashboard:login')
def worker_reject(request, pk):
    """Reject a worker"""
    worker = get_object_or_404(Worker, pk=pk)
    worker.verification_status = 'rejected'
    worker.save()
    messages.warning(request, f'Worker {worker.name} has been rejected.')
    return redirect('dashboard:worker_detail', pk=pk)


# ============================================================
# TASK MANAGEMENT (BUCKET 2)
# ============================================================

@login_required(login_url='dashboard:login')
def task_list(request):
    """List all tasks with filters"""
    tasks = Task.objects.all().select_related('category', 'worker')
    
    # Filters
    status = request.GET.get('status')
    category = request.GET.get('category')
    search = request.GET.get('search')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if status:
        tasks = tasks.filter(status=status)
    if category:
        tasks = tasks.filter(category_id=category)
    if search:
        tasks = tasks.filter(
            Q(cust_name__icontains=search) | 
            Q(cust_phone__icontains=search)
        )
    if date_from:
        tasks = tasks.filter(schedule_date__gte=date_from)
    if date_to:
        tasks = tasks.filter(schedule_date__lte=date_to)
    
    tasks = tasks.order_by('-created_at')
    
    categories = Category.objects.filter(category_type='primary')
    
    context = {
        'tasks': tasks,
        'categories': categories,
        'selected_status': status,
        'selected_category': category,
        'search_query': search,
    }
    
    return render(request, 'dashboard/task_list.html', context)


@login_required(login_url='dashboard:login')
def task_detail(request, pk):
    """Task detail view"""
    task = get_object_or_404(Task, pk=pk)
    
    # Get available workers for assignment
    if task.category:
        available_workers = Worker.objects.filter(
            verification_status='verified',
            primary_category=task.category
        )
    else:
        available_workers = Worker.objects.filter(verification_status='verified')
    
    context = {
        'task': task,
        'available_workers': available_workers,
    }
    
    return render(request, 'dashboard/task_detail.html', context)


@login_required(login_url='dashboard:login')
def task_assign_worker(request, pk):
    """Assign worker to task"""
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        worker_id = request.POST.get('worker_id')
        
        if worker_id:
            worker = get_object_or_404(Worker, pk=worker_id)
            task.worker = worker
            task.worker_name = worker.name
            task.status = 'scheduled'
            task.save()
            
            messages.success(request, f'Task assigned to {worker.name}')
        
        return redirect('dashboard:task_detail', pk=pk)
    
    return redirect('dashboard:task_list')


@login_required(login_url='dashboard:login')
def task_update_status(request, pk):
    """Update task status"""
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in ['pending', 'scheduled', 'active', 'completed', 'cancelled']:
            task.status = new_status
            
            if new_status == 'completed':
                task.day_service_done = timezone.now().date()
            
            task.save()
            messages.success(request, f'Task status updated to {new_status}')
        
        return redirect('dashboard:task_detail', pk=pk)
    
    return redirect('dashboard:task_list')


@login_required(login_url='dashboard:login')
def task_create_from_requirement(request, requirement_id):
    """Create task from requirement"""
    requirement = get_object_or_404(Requirement, pk=requirement_id)
    
    # Create new task from requirement
    task = Task()
    task.cust_name = requirement.name
    task.cust_phone = requirement.number
    task.cust_location = requirement.location
    task.category = requirement.category
    task.schedule_date = requirement.scheduled_date or timezone.now()
    task.status = 'pending'
    
    # Parse location for pincode (if format is: "address, city - pincode")
    if ' - ' in requirement.location:
        task.pincode = requirement.location.split(' - ')[-1].strip()
    
    task.save()
    
    # Update requirement status
    requirement.status = 'fulfilled'
    requirement.save()
    
    messages.success(request, f'Task created from requirement #{requirement.requirement_id}')
    return redirect('dashboard:task_detail', pk=task.pk)


# ============================================================
# TASK LOG HISTORY (BUCKET 3)
# ============================================================

@login_required(login_url='dashboard:login')
def task_log_history(request):
    """View all calling summaries and task logs"""
    
    # Get calling summaries
    calling_logs = CallingSummary.objects.all().select_related(
        'task', 'worker', 'category'
    ).order_by('-created_at')
    
    # Get all requirements
    requirements = Requirement.objects.all().select_related(
        'category', 'worker'
    ).order_by('-created_at')
    
    # Filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')
    
    if date_from:
        calling_logs = calling_logs.filter(created_at__gte=date_from)
        requirements = requirements.filter(created_at__gte=date_from)
    
    if date_to:
        calling_logs = calling_logs.filter(created_at__lte=date_to)
        requirements = requirements.filter(created_at__lte=date_to)
    
    if status:
        requirements = requirements.filter(status=status)
    
    context = {
        'calling_logs': calling_logs[:50],  # Limit to 50 recent logs
        'requirements': requirements[:50],
        'date_from': date_from,
        'date_to': date_to,
        'selected_status': status,
    }
    
    return render(request, 'dashboard/task_log_history.html', context)


@login_required(login_url='dashboard:login')
def requirement_detail(request, pk):
    """Requirement detail view"""
    requirement = get_object_or_404(Requirement, pk=pk)
    
    # Check if task already created from this requirement
    related_tasks = Task.objects.filter(
        cust_name=requirement.name,
        cust_phone=requirement.number
    )
    
    context = {
        'requirement': requirement,
        'related_tasks': related_tasks,
    }
    
    return render(request, 'dashboard/requirement_detail.html', context)

@login_required(login_url='dashboard:login')
def worker_pdf(request, pk):
    worker = get_object_or_404(Worker, pk=pk)
    html_string = render_to_string('dashboard/worker_pdf.html', {'worker': worker})
    pdf_file = HTML(string=html_string).write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Worker_{worker.name}.pdf"'
    return response

# Replace these functions in apps/dashboard/views.py

@login_required(login_url='dashboard:login')
def worker_list(request):
    """List all workers with filters"""
    workers = Worker.objects.all().select_related('primary_category', 'location')
    
    # Filters
    status = request.GET.get('status')
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    if status:
        workers = workers.filter(verification_status=status)
    if category:
        workers = workers.filter(primary_category_id=category)
    if search:
        workers = workers.filter(
            Q(name__icontains=search) | 
            Q(phone__icontains=search) |
            Q(aadhar_no__icontains=search)
        )
    
    categories = Category.objects.filter(category_type='primary')
    locations = Location.objects.all()  # ADD THIS LINE!
    
    context = {
        'workers': workers,
        'categories': categories,
        'locations': locations,  # ADD THIS LINE!
        'selected_status': status,
        'selected_category': category,
        'search_query': search,
    }
    
    return render(request, 'dashboard/worker_list.html', context)


@login_required(login_url='dashboard:login')
def worker_add(request):
    """Add new worker with all fields and files"""
    
    if request.method == "POST":
        phone = request.POST.get("phone")
        
        if not phone:
            messages.error(request, "Phone number is required.")
            return redirect("dashboard:worker_list")
        
        try:
            # Create worker instance
            worker = Worker()
            
            # Basic fields
            worker.name = request.POST.get("name")
            worker.phone = phone
            worker.whatsapp_no = request.POST.get("whatsapp_no", "")
            

            print(worker)
            # Age - handle empty value
            age = request.POST.get("age")
            if age:
                worker.age = int(age)
            
            # Aadhar - FIXED FIELD NAME
            worker.aadhar_no = request.POST.get("aadhar_no", "")
            
            # Geo Location Link - NEW!
            worker.geo_location_link = request.POST.get("geo_location_link", "")
            
            # Category
            category_id = request.POST.get("primary_category")
            if category_id:
                worker.primary_category = Category.objects.filter(id=category_id).first()
            
            # Location
            address_input = request.POST.get("address")


             # Apply fuzzy logic
            matched_location = find_best_matching_location(address_input)


            if matched_location:
                worker.location = matched_location
            else:
                messages.error(request, "Service not available for this location. Please enter a correct address.")
                return redirect('dashboard:worker_list')
            
            # Verification Status - NEW!
            worker.verification_status = request.POST.get("verification_status", "pending")
            
            # Ranking Score - NEW!
            ranking_score = request.POST.get("ranking_score")
            if ranking_score:
                worker.ranking_score = float(ranking_score)
            else:
                worker.ranking_score = 0.0
            
            # Handle file uploads - NEW!
            if 'aadhar_img_front' in request.FILES:
                worker.aadhar_img_front = request.FILES['aadhar_img_front']
            
            if 'aadhar_img_back' in request.FILES:
                worker.aadhar_img_back = request.FILES['aadhar_img_back']
            
            if 'selfie_img' in request.FILES:
                worker.selfie_img = request.FILES['selfie_img']
            
            # Save worker first
            worker.save()
            
            # Handle secondary categories (Many-to-Many) - NEW!
            secondary_cats = request.POST.getlist('secondary_categories')
            if secondary_cats:
                worker.secondary_categories.set(secondary_cats)
            
            messages.success(request, f"Worker {worker.name} added successfully!")
            return redirect("dashboard:worker_list")
            
        except Exception as e:
            messages.error(request, f"Error adding worker: {str(e)}")
            return redirect("dashboard:worker_list")
    
    return redirect("dashboard:worker_list")


@login_required(login_url='dashboard:login')
def worker_edit(request, pk):
    """Update worker with all fields and files"""
    worker = get_object_or_404(Worker, pk=pk)
    
    if request.method == "POST":
        phone = request.POST.get('phone')
        
        if not phone:
            messages.error(request, "Phone number is required.")
            return redirect('dashboard:worker_list')
        
        try:
            # Basic fields
            worker.name = request.POST.get('name', worker.name)
            worker.phone = phone
            worker.whatsapp_no = request.POST.get('whatsapp_no', worker.whatsapp_no)
            
            # Age - handle empty value
            age = request.POST.get('age')
            if age:
                worker.age = int(age)
            
            # Aadhar
            worker.aadhar_no = request.POST.get('aadhar_no', worker.aadhar_no)
            
            # Geo Location Link - NEW!
            worker.geo_location_link = request.POST.get('geo_location_link', worker.geo_location_link)
            
            # Category
            category_id = request.POST.get('primary_category')
            if category_id:
                worker.primary_category = Category.objects.filter(id=category_id).first()
            
            # Location
            address_input = request.POST.get('location')
              # Apply fuzzy logic
            matched_location = find_best_matching_location(address_input)

            if matched_location:
                worker.location = matched_location
            else:
                messages.error(request, "Service not available for this location. Please enter a correct address.")
                return redirect('dashboard:worker_list')
            
            # Verification Status - NEW!
            verification_status = request.POST.get('verification_status')
            if verification_status:
                worker.verification_status = verification_status
            
            # Ranking Score - NEW!
            ranking_score = request.POST.get('ranking_score')
            if ranking_score:
                worker.ranking_score = float(ranking_score)
            
            # Handle file uploads - NEW!
            if 'aadhar_img_front' in request.FILES:
                worker.aadhar_img_front = request.FILES['aadhar_img_front']
            
            if 'aadhar_img_back' in request.FILES:
                worker.aadhar_img_back = request.FILES['aadhar_img_back']
            
            if 'selfie_img' in request.FILES:
                worker.selfie_img = request.FILES['selfie_img']
            
            # Save worker
            worker.save()
            
            # Handle secondary categories (Many-to-Many) - NEW!
            secondary_cats = request.POST.getlist('secondary_categories')
            if secondary_cats:
                worker.secondary_categories.set(secondary_cats)
            else:
                worker.secondary_categories.clear()
            
            messages.success(request, f"Worker {worker.name} updated successfully!")
            return redirect('dashboard:worker_list')
            
        except Exception as e:
            messages.error(request, f"Error updating worker: {str(e)}")
            return redirect('dashboard:worker_list')
    
    # GET request - this shouldn't happen with modal, but just in case
    return redirect('dashboard:worker_list')


@login_required(login_url='dashboard:login')
def worker_delete(request, pk):
    """Delete worker"""
    worker = get_object_or_404(Worker, pk=pk)
    worker_name = worker.name
    worker.delete()
    messages.success(request, f"Worker {worker_name} deleted successfully!")
    return redirect('dashboard:worker_list')


@login_required(login_url='dashboard:login')
def task_add(request):
    categories = Category.objects.all()
    workers = Worker.objects.all()

    if request.method == "POST":
        task = Task()

        # ---------- CUSTOMER ----------
        task.cust_name = request.POST.get("cust_name")
        task.cust_phone = request.POST.get("cust_phone")
        task.cust_whatsapp = request.POST.get("cust_whatsapp")
        task.pincode = request.POST.get("pincode")

        address_input = request.POST.get("cust_location")
        matched_location = find_best_matching_location(address_input)

        if not matched_location:
            messages.error(request, "Service not available in this location.")
            return redirect("dashboard:task_list")

        task.location = matched_location
        task.cust_location = address_input

        # ---------- CATEGORY ----------
        category = request.POST.get("category")
        task.category_id = category if category else None

        task.additional_info = request.POST.get("additional_info")
        task.payment_received_amt = request.POST.get("payment_received_amt") or 0

        # ---------- WORKER ----------
        worker_id = request.POST.get("worker")
        if worker_id:
            task.worker_id = worker_id
            task.worker_name = request.POST.get("worker_display")
            task.worker_phone = request.POST.get("worker_phone")
            task.worker_category = request.POST.get("worker_category")

        # ---------- SCHEDULE ----------
        schedule_date = request.POST.get("schedule_date")
        task.schedule_date = make_aware_datetime(schedule_date)

        # ---------- IMAGE ----------
        if request.FILES.get("task_image"):
            task.task_image = request.FILES["task_image"]

        # 🔥 SAVE FIRST
        task.save()

        # ---------- SUBCATEGORIES ----------
        subcat_ids = [
            s for s in request.POST.getlist("subcategories") if s.strip()
        ]
        task.subcategories.set(subcat_ids)

        # ---------- REQUIREMENT ----------
        req_id = request.POST.get("requirement_id")
        if req_id:
            task.requirement_id = req_id
            Requirement.objects.filter(id=req_id).update(status="fulfilled")
            task.save(update_fields=["requirement"])

        # ---------- LOG ----------
        task.save()
        log_task_change(task, action="created")

        messages.success(request, "Task created successfully.")
        return redirect("dashboard:task_list")

    return render(request, "dashboard/task_list.html", {
        "categories": categories,
        "workers": workers,
    })



@login_required(login_url='dashboard:login')
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    categories = Category.objects.all()
    workers = Worker.objects.all()

    if request.method == "POST":
        task.cust_name = request.POST.get("cust_name")
        task.cust_phone = request.POST.get("cust_phone")
        task.cust_whatsapp = request.POST.get("cust_whatsapp")
        task.pincode = request.POST.get("pincode")

        address_input = request.POST.get("cust_location")
        matched_location = find_best_matching_location(address_input)

        if not matched_location:
            messages.error(request, "Service not available in this location.")
            return redirect("dashboard:task_list")

        task.location = matched_location
        task.cust_location = address_input

        task.category_id = request.POST.get("category") or None
        task.additional_info = request.POST.get("additional_info")
        task.payment_received_amt = request.POST.get("payment_received_amt") or 0

        wid = request.POST.get("worker")
        if wid:
            task.worker_id = wid
            task.worker_name = request.POST.get("worker_name")
            task.worker_phone = request.POST.get("worker_phone")
            task.worker_category = request.POST.get("worker_category")

        schedule_date = request.POST.get("schedule_date")
        task.schedule_date = make_aware_datetime(schedule_date)

        task.day_service_done = request.POST.get("day_service_done") or None
        task.status = request.POST.get("status")

        task.feedback = request.POST.get("feedback")
        task.rating = request.POST.get("rating") or None

        if request.FILES.get("task_image"):
            task.task_image = request.FILES["task_image"]

        task.save()

        # SUBCATEGORIES
        task.subcategories.set(request.POST.getlist("subcategories"))

        # LOG
        old_task = Task.objects.get(id=task.id)

        task.save()
        log_task_change(task, action="updated", old_task=old_task)


        messages.success(request, "Task updated successfully.")
        return redirect("dashboard:task_list")

    return render(request, "dashboard/task_edit_form.html", {
        "task": task,
        "categories": categories,
        "workers": workers,
    })


from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='dashboard:login')
def assign_worker_popup(request):

    categories = Category.objects.all()
    workers = Worker.objects.all()

    # ------------------------
    # 🚀 APPLY FILTERS (AJAX)
    # ------------------------
    if request.GET.get("ajax") == "1":

        name = request.GET.get("name", "")
        age_min = request.GET.get("age_min")
        age_max = request.GET.get("age_max")
        category = request.GET.get("category")
        subcategories = request.GET.getlist("subcategories")
        date = request.GET.get("date")
        same_location = request.GET.get("same_location")
        task_location = request.GET.get("task_location")

        # 1️⃣ Name / Phone
        if name:
            workers = workers.filter(
                Q(name__icontains=name) |
                Q(phone__icontains=name)
            )

        # 2️⃣ Age Range
        if age_min:
            workers = workers.filter(age__gte=age_min)
        if age_max:
            workers = workers.filter(age__lte=age_max)

        # 3️⃣ Primary Category
        if category:
            workers = workers.filter(primary_category_id=category)

        # 4️⃣ Secondary Categories
        if subcategories:
            workers = workers.filter(
                secondary_categories__id__in=subcategories
            ).distinct()

        # 5️⃣ Worker Availability
        if date:
            workers = workers.exclude(busy_dates__icontains=date)

        # 6️⃣ Same Location as Task
        if same_location == "1" and task_location:
            workers = workers.filter(location_id=task_location)

        # Return only the table
        return render(request, "dashboard/assign_worker_table.html", {
            "workers": workers
        })

    # ------------------------
    # FIRST MODAL LOAD
    # ------------------------
    return render(request, "dashboard/assign_worker_model.html", {
        "categories": categories,
        "workers": workers,
    })

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, id=pk)

    logs = task.call_logs.all().order_by("-created_at")

    return render(request, "dashboard/task_detail.html", {
        "task": task,
        "logs": logs,
    })



@login_required(login_url='dashboard:login')
def task_log_history(request):

    calling_logs = CallingSummary.objects.select_related(
        'task', 'worker', 'category'
    ).order_by('-created_at')[:50]

    requirements = Requirement.objects.order_by('-created_at')[:50]

    return render(request, "dashboard/task_log_history.html", {
        "calling_logs": calling_logs,
        "requirements": requirements,
    })


@csrf_exempt
def filter_workers(request):
    data = json.loads(request.body)
    workers = Worker.objects.all()

    # Name or Phone filter
    if data.get("name"):
        workers = workers.filter(
            Q(name__icontains=data["name"]) |
            Q(phone__icontains=data["name"])
        )

    # Age range
    if data.get("age_min"):
        workers = workers.filter(age__gte=data["age_min"])
    if data.get("age_max"):
        workers = workers.filter(age__lte=data["age_max"])

    # Primary Category
    if data.get("category"):
        workers = workers.filter(primary_category_id=data["category"])

    # Secondary Categories
    if data.get("subcategories"):
        workers = workers.filter(secondary_categories__id__in=data["subcategories"]).distinct()

    # Location match with task location
    if data.get("match_location") and data.get("task_location"):
        workers = workers.filter(location_id=data["task_location"])

    # Date availability filter
    if data.get("date"):
        selected_date = data["date"]
        workers = workers.exclude(busy_dates__icontains=selected_date)

    html = render_to_string("dashboard/assign_worker_table.html", {"workers": workers})
    return JsonResponse({"html": html})

@require_POST
@login_required(login_url='dashboard:login')
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return JsonResponse({"success": True})


@login_required(login_url='dashboard:login')
def calling_log_detail(request, log_id):
    log = get_object_or_404(CallingSummary, id=log_id)

    return render(request, "dashboard/calling_log_detail.html", {
        "log": log
    })

from django.core.paginator import Paginator

@login_required(login_url='dashboard:login')
def task_log_history(request):
    logs_qs = CallingSummary.objects.select_related(
        "task", "worker", "category"
    ).order_by("-created_at")
    
    categories = Category.objects.all()

    paginator = Paginator(logs_qs, 10)  # 🔥 10 rows
    page_number = request.GET.get("page")
    calling_logs = paginator.get_page(page_number)

    requirements = Requirement.objects.all().order_by('-created_at')[:10]

    return render(request, "dashboard/task_log_history.html", {
        "calling_logs": calling_logs,
        "requirements": requirements,
        "categories": categories,
    })

from django.shortcuts import render

def home(request):
    context = {
        "cleaning_subcategories": [
            "Full Home", "Kitchen", "Bathroom", "Sofa", "Mattress", "Office"
        ],
        "cleaning_services": [
            {"name": "Home Cleaning", "desc": "Complete house cleaning"},
            {"name": "Kitchen Deep Clean", "desc": "Oil & grease removal"},
            {"name": "Bathroom Deep Clean", "desc": "Tiles & fittings"},
            {"name": "Sofa Shampoo", "desc": "Fabric care"},
        ],
        "handyman_subcategories": [
            "Electrician", "Plumber", "Carpenter", "Painter", "AC Service"
        ],
        "handyman_services": [
            {"name": "Home Painting", "desc": "Interior & exterior"},
            {"name": "Electrical Repair", "desc": "Switches & wiring"},
            {"name": "Minor Plumbing", "desc": "Leak & tap repair"},
        ],
        "faqs": [
            {"q": "What is SahayakCircle?", "a": "We connect customers with verified local workers."},
            {"q": "Is it safe?", "a": "Workers go through basic verification."},
            {"q": "How do I pay?", "a": "Pay directly after service confirmation."},
        ],
        "popular_tags": [
            "Home Cleaning", "Electrician", "Plumber", "AC Service",
            "Pest Control", "Carpenter", "Salon at Home"
        ]
    }
    return render(request, "public/home.html", context)
