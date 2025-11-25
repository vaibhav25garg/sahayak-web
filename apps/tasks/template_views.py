# apps/tasks/template_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime

from .models import Task
from apps.workers.models import Worker
from apps.categories.models import Category


def _parse_datetime_safe(dt_str):
    """
    Try multiple common datetime formats and return a timezone-aware datetime.
    If parsing fails or dt_str is falsy, return None.
    """
    if not dt_str:
        return None

    # Try common formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",  # iso-like
        "%Y-%m-%dT%H:%M",     # iso-like without seconds
        "%Y-%m-%d",           # date only -> convert to midnight
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(dt_str, fmt)
            # if only date provided, keep as midnight
            if fmt == "%Y-%m-%d":
                parsed = datetime(parsed.year, parsed.month, parsed.day, 0, 0, 0)
            # Make timezone-aware (use current timezone)
            return timezone.make_aware(parsed, timezone.get_current_timezone())
        except Exception:
            continue

    # Try Python 3.7+ fromisoformat as last attempt (handles many ISO variants)
    try:
        parsed = datetime.fromisoformat(dt_str)
        if parsed.tzinfo is None:
            parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
        return parsed
    except Exception:
        return None


def task_list(request):
    """List all tasks"""
    tasks = Task.objects.all().select_related('category', 'worker')

    # Filtering
    status = request.GET.get('status')
    category_id = request.GET.get('category')
    search = request.GET.get('search')

    if status:
        tasks = tasks.filter(status=status)
    if category_id:
        tasks = tasks.filter(category_id=category_id)
    if search:
        # Use Q to combine OR correctly
        tasks = tasks.filter(
            Q(cust_name__icontains=search) |
            Q(cust_phone__icontains=search)
        )

    categories = Category.objects.filter(category_type='primary')

    context = {
        'tasks': tasks,
        'categories': categories,
        'selected_status': status,
        'selected_category': category_id,
        'search_query': search,
    }
    return render(request, 'tasks/task_list.html', context)


def task_detail(request, pk):
    """Task detail view"""
    task = get_object_or_404(
        Task.objects.select_related('category', 'worker'),
        pk=pk
    )
    context = {'task': task}
    return render(request, 'tasks/task_detail.html', context)


def task_create(request):
    """Create new task"""
    if request.method == 'POST':
        try:
            task = Task()

            # Basic fields (strings are ok for Char/Text fields)
            task.cust_name = request.POST.get('cust_name') or ''
            task.cust_phone = request.POST.get('cust_phone') or ''
            task.cust_whatsapp = request.POST.get('cust_whatsapp') or ''
            task.cust_location = request.POST.get('cust_location') or ''
            task.pincode = request.POST.get('pincode') or ''
            task.additional_info = request.POST.get('additional_info') or ''

            # schedule_date (DateTimeField) - parse safely
            schedule_raw = request.POST.get('schedule_date')
            parsed_dt = _parse_datetime_safe(schedule_raw)
            if parsed_dt:
                task.schedule_date = parsed_dt
            else:
                # If no valid schedule provided, default to now (or you can raise error)
                task.schedule_date = timezone.now()

            # category (ForeignKey) - validate integer id
            category_id = request.POST.get('category')
            if category_id and category_id.isdigit():
                task.category_id = int(category_id)
            else:
                task.category = None

            # image handling
            if 'task_image' in request.FILES:
                task.task_image = request.FILES['task_image']

            # save first so ManyToMany can be set
            task.save()

            # Handle subcategories (ManyToMany) - ensure ids are ints or valid
            subcategories = request.POST.getlist('subcategories')
            if subcategories:
                # filter out non-numeric ids
                valid_ids = [int(x) for x in subcategories if str(x).isdigit()]
                if valid_ids:
                    task.subcategories.set(valid_ids)
                else:
                    task.subcategories.clear()

            messages.success(request, 'Task created successfully!')
            return redirect('tasks:task_detail', pk=task.pk)
        except Exception as e:
            # Log exception server-side if you want; for now show message
            messages.error(request, f'Error creating task: {str(e)}')

    categories = Category.objects.filter(category_type='primary')
    context = {'categories': categories}
    return render(request, 'tasks/task_form.html', context)


def task_edit(request, pk):
    """Edit existing task"""
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        try:
            task.cust_name = request.POST.get('cust_name') or task.cust_name
            task.cust_phone = request.POST.get('cust_phone') or task.cust_phone
            task.cust_whatsapp = request.POST.get('cust_whatsapp') or task.cust_whatsapp
            task.cust_location = request.POST.get('cust_location') or task.cust_location
            task.pincode = request.POST.get('pincode') or task.pincode
            task.additional_info = request.POST.get('additional_info') or task.additional_info

            # schedule_date
            schedule_raw = request.POST.get('schedule_date')
            parsed_dt = _parse_datetime_safe(schedule_raw)
            if parsed_dt:
                task.schedule_date = parsed_dt
            # else keep existing schedule_date

            # status
            task.status = request.POST.get('status', task.status)

            # category assignment
            category_id = request.POST.get('category')
            if category_id and category_id.isdigit():
                task.category_id = int(category_id)
            else:
                task.category = None

            # image
            if 'task_image' in request.FILES:
                task.task_image = request.FILES['task_image']

            task.save()

            # subcategories
            subcategories = request.POST.getlist('subcategories')
            if subcategories:
                valid_ids = [int(x) for x in subcategories if str(x).isdigit()]
                task.subcategories.set(valid_ids)
            else:
                task.subcategories.clear()

            messages.success(request, 'Task updated successfully!')
            return redirect('tasks:task_detail', pk=task.pk)
        except Exception as e:
            messages.error(request, f'Error updating task: {str(e)}')

    categories = Category.objects.filter(category_type='primary')
    context = {
        'task': task,
        'categories': categories,
    }
    return render(request, 'tasks/task_form.html', context)


def task_delete(request, pk):
    """Delete task"""
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('tasks:task_list')

    context = {'task': task}
    return render(request, 'tasks/task_confirm_delete.html', context)


def task_assign_worker(request, pk):
    """Assign worker to task"""
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        worker_id = request.POST.get('worker_id')
        if worker_id:
            try:
                worker = Worker.objects.get(id=worker_id)
                task.worker = worker
                task.worker_name = worker.name
                task.status = 'scheduled'
                task.save()
                messages.success(request, f'Worker {worker.name} assigned successfully!')
                return redirect('tasks:task_detail', pk=task.pk)
            except Worker.DoesNotExist:
                messages.error(request, 'Worker not found!')

    # Get available workers
    workers = Worker.objects.filter(
        verification_status='verified',
        primary_category=task.category
    )

    context = {
        'task': task,
        'workers': workers,
    }
    return render(request, 'tasks/task_assign_worker.html', context)
