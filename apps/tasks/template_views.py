# apps/tasks/template_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Task
from apps.workers.models import Worker
from apps.categories.models import Category

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
        tasks = tasks.filter(cust_name__icontains=search) | tasks.filter(cust_phone__icontains=search)
    
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
            task.cust_name = request.POST.get('cust_name')
            task.cust_phone = request.POST.get('cust_phone')
            task.cust_whatsapp = request.POST.get('cust_whatsapp')
            task.cust_location = request.POST.get('cust_location')
            task.pincode = request.POST.get('pincode')
            task.additional_info = request.POST.get('additional_info')
            task.schedule_date = request.POST.get('schedule_date')
            
            category_id = request.POST.get('category')
            if category_id:
                task.category_id = category_id
            
            if 'task_image' in request.FILES:
                task.task_image = request.FILES['task_image']
            
            task.save()
            
            # Handle subcategories
            subcategories = request.POST.getlist('subcategories')
            if subcategories:
                task.subcategories.set(subcategories)
            
            messages.success(request, 'Task created successfully!')
            return redirect('tasks:task_detail', pk=task.pk)
        except Exception as e:
            messages.error(request, f'Error creating task: {str(e)}')
    
    categories = Category.objects.filter(category_type='primary')
    context = {'categories': categories}
    return render(request, 'tasks/task_form.html', context)

def task_edit(request, pk):
    """Edit existing task"""
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        try:
            task.cust_name = request.POST.get('cust_name')
            task.cust_phone = request.POST.get('cust_phone')
            task.cust_whatsapp = request.POST.get('cust_whatsapp')
            task.cust_location = request.POST.get('cust_location')
            task.pincode = request.POST.get('pincode')
            task.additional_info = request.POST.get('additional_info')
            task.schedule_date = request.POST.get('schedule_date')
            task.status = request.POST.get('status', task.status)
            
            category_id = request.POST.get('category')
            if category_id:
                task.category_id = category_id
            
            if 'task_image' in request.FILES:
                task.task_image = request.FILES['task_image']
            
            task.save()
            
            subcategories = request.POST.getlist('subcategories')
            task.subcategories.set(subcategories)
            
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