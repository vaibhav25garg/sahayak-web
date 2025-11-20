# apps/dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
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

from django.shortcuts import render, redirect
from apps.workers.models import Worker
from apps.categories.models import Category
from apps.locations.models import Location
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
        
        print("help me to run success full")
        try:
            # Create worker instance
            worker = Worker()
            
            print("case 1")
            # Basic fields
            worker.name = request.POST.get("name")
            worker.phone = phone
            worker.whatsapp_no = request.POST.get("whatsapp_no", "")
            
            print("case 2")

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

            print(worker)

            print(address_input)
             # Apply fuzzy logic
            matched_location = find_best_matching_location(address_input)


            print(matched_location)
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