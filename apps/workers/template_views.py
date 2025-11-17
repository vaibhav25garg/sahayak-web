# apps/workers/template_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Worker
from apps.categories.models import Category
from apps.locations.models import Location

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def worker_list(request):
    """List all workers"""
    workers = Worker.objects.all().select_related('primary_category', 'location')
    
    # Filtering
    verification_status = request.GET.get('status')
    category_id = request.GET.get('category')
    search = request.GET.get('search')
    
    if verification_status:
        workers = workers.filter(verification_status=verification_status)
    if category_id:
        workers = workers.filter(primary_category_id=category_id)
    if search:
        workers = workers.filter(name__icontains=search) | workers.filter(phone__icontains=search)
    
    categories = Category.objects.filter(category_type='primary')
    
    context = {
        'workers': workers,
        'categories': categories,
        'selected_status': verification_status,
        'selected_category': category_id,
        'search_query': search,
    }
    return render(request, 'workers/worker_list.html', context)

def worker_detail(request, pk):
    """Worker detail view"""
    worker = get_object_or_404(
        Worker.objects.select_related('primary_category', 'location'),
        pk=pk
    )
    context = {'worker': worker}
    return render(request, 'workers/worker_detail.html', context)

def worker_create(request):
    """Create new worker"""
    if request.method == 'POST':
        try:
            worker = Worker()
            worker.name = request.POST.get('name')
            worker.phone = request.POST.get('phone')
            worker.whatsapp_no = request.POST.get('whatsapp_no')
            worker.age = request.POST.get('age')
            worker.aadhar_no = request.POST.get('aadhar_no')
            
            # Handle category
            primary_category_id = request.POST.get('primary_category')
            if primary_category_id:
                worker.primary_category_id = primary_category_id
            
            # Handle location
            location_id = request.POST.get('location')
            if location_id:
                worker.location_id = location_id
            
            # Handle files
            if 'aadhar_img_front' in request.FILES:
                worker.aadhar_img_front = request.FILES['aadhar_img_front']
            if 'aadhar_img_back' in request.FILES:
                worker.aadhar_img_back = request.FILES['aadhar_img_back']
            if 'selfie_img' in request.FILES:
                worker.selfie_img = request.FILES['selfie_img']
            
            worker.save()
            
            # Handle secondary categories
            secondary_cats = request.POST.getlist('secondary_categories')
            if secondary_cats:
                worker.secondary_categories.set(secondary_cats)
            
            messages.success(request, 'Worker created successfully!')
            return redirect('workers:worker_detail', pk=worker.pk)
        except Exception as e:
            messages.error(request, f'Error creating worker: {str(e)}')
    
    categories = Category.objects.filter(category_type='primary')
    locations = Location.objects.all()
    context = {
        'categories': categories,
        'locations': locations,
    }
    return render(request, 'workers/worker_form.html', context)

def worker_edit(request, pk):
    """Edit existing worker"""
    worker = get_object_or_404(Worker, pk=pk)
    
    if request.method == 'POST':
        try:
            worker.name = request.POST.get('name')
            worker.phone = request.POST.get('phone')
            worker.whatsapp_no = request.POST.get('whatsapp_no')
            worker.age = request.POST.get('age')
            worker.aadhar_no = request.POST.get('aadhar_no')
            
            primary_category_id = request.POST.get('primary_category')
            if primary_category_id:
                worker.primary_category_id = primary_category_id
            
            location_id = request.POST.get('location')
            if location_id:
                worker.location_id = location_id
            
            if 'aadhar_img_front' in request.FILES:
                worker.aadhar_img_front = request.FILES['aadhar_img_front']
            if 'aadhar_img_back' in request.FILES:
                worker.aadhar_img_back = request.FILES['aadhar_img_back']
            if 'selfie_img' in request.FILES:
                worker.selfie_img = request.FILES['selfie_img']
            
            worker.save()
            
            secondary_cats = request.POST.getlist('secondary_categories')
            worker.secondary_categories.set(secondary_cats)
            
            messages.success(request, 'Worker updated successfully!')
            return redirect('workers:worker_detail', pk=worker.pk)
        except Exception as e:
            messages.error(request, f'Error updating worker: {str(e)}')
    
    categories = Category.objects.filter(category_type='primary')
    locations = Location.objects.all()
    context = {
        'worker': worker,
        'categories': categories,
        'locations': locations,
    }
    return render(request, 'workers/worker_form.html', context)

def worker_delete(request, pk):
    """Delete worker"""
    worker = get_object_or_404(Worker, pk=pk)
    
    if request.method == 'POST':
        worker.delete()
        messages.success(request, 'Worker deleted successfully!')
        return redirect('workers:worker_list')
    
    context = {'worker': worker}
    return render(request, 'workers/worker_confirm_delete.html', context)

