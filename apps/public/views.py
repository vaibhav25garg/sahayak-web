# ============================================================
# apps/public/views.py - Simplified without new models
# ============================================================
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from apps.workers.models import Worker
from apps.requirements.models import Requirement
from apps.categories.models import Category
from apps.locations.models import Location
from apps.locations.utils import find_best_matching_location

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def home(request):
    """Public home page - no authentication required"""
    return render(request, 'public/home.html')


def about(request):
    """About us page"""
    return render(request, 'public/about.html')


def contact(request):
    """Contact us page"""
    if request.method == 'POST':
        # Handle contact form submission
        # You can add email sending logic here if needed
        messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
        return redirect('public:contact')
    return render(request, 'public/contact.html')


@require_http_methods(["GET", "POST"])
def worker_registration(request):

    if request.method == 'POST':
        try:
            worker = Worker()

            # ---------------- BASIC INFO ----------------
            worker.name = request.POST.get('name', '').strip()
            worker.phone = request.POST.get('phone', '').strip()

            if not worker.phone.isdigit() or len(worker.phone) != 10:
                messages.error(request, "Enter a valid 10-digit phone number.")
                return redirect('public:worker_registration')

            # WhatsApp
            whatsapp_same = request.POST.get('same_as_phone')
            worker.whatsapp_no = worker.phone if whatsapp_same else request.POST.get('whatsapp_no', '').strip()

            # Age (optional but numeric)
            age = request.POST.get('age')
            if age:
                if not age.isdigit():
                    messages.error(request, "Age must be a number.")
                    return redirect('public:worker_registration')
                worker.age = int(age)

            # ---------------- AADHAR ----------------
            raw_aadhar = request.POST.get('aadhar_no', '')
            aadhar = raw_aadhar.replace(" ", "")  # 🔥 REMOVE SPACES

            if not aadhar.isdigit() or len(aadhar) != 12:
                messages.error(request, "Enter a valid 12-digit Aadhar number.")
                return redirect('public:worker_registration')

            worker.aadhar_no = aadhar

            # ---------------- CATEGORY ----------------
            category_id = request.POST.get('category')
            if not category_id:
                messages.error(request, "Please select a category.")
                return redirect('public:worker_registration')

            worker.primary_category_id = category_id

            # ---------------- LOCATION ----------------
            address_input = request.POST.get('address', '').strip()
            matched_location = find_best_matching_location(address_input)

            if not matched_location:
                messages.error(
                    request,
                    "Service not available for this location. Please enter a correct address."
                )
                return redirect('public:worker_registration')

            worker.location = matched_location

            # ---------------- FILES ----------------
            worker.aadhar_img_front = request.FILES.get('aadhar_img_front')
            worker.aadhar_img_back = request.FILES.get('aadhar_img_back')
            worker.selfie_img = request.FILES.get('selfie_img')

            # ---------------- SAVE ----------------
            worker.save()

            # Secondary categories (M2M)
            secondary_cats = request.POST.getlist('secondary_categories')
            if secondary_cats:
                worker.secondary_categories.set(secondary_cats)

            messages.success(request, "Registration Successful! Our team will verify your details.")
            return redirect('public:home')

        except Exception as e:
            messages.error(request, "Something went wrong. Please try again.")
            print("Worker Registration Error:", e)

    # GET REQUEST
    categories = Category.objects.filter(category_type='primary')

    return render(request, 'public/worker_registration.html', {
        'categories': categories
    })


@require_http_methods(["GET", "POST"])
def requirement_form(request):
    """Service requirement - directly creates Requirement record"""
    
    if request.method == 'POST':
        try:
            # Generate unique requirement ID
            import uuid
            requirement_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
            
            # Create requirement directly
            requirement = Requirement()
            requirement.requirement_id = requirement_id
            requirement.name = request.POST.get('name')
            requirement.number = request.POST.get('phone')
            
            # Location information
            city = request.POST.get('city')
            pincode = request.POST.get('pincode')
            address = request.POST.get('address')
            landmark = request.POST.get('landmark', '')
            
            requirement.location = f"{address}, {landmark}, {city} - {pincode}"
            
            # Category
            category_id = request.POST.get('category')
            if category_id:
                requirement.category_id = category_id
            
            # Set status as pending
            requirement.status = 'pending'
            
            # Scheduled date
            preferred_date = request.POST.get('preferred_date')
            if preferred_date:
                from django.utils import timezone
                from datetime import datetime
                requirement.scheduled_date = timezone.make_aware(
                    datetime.strptime(preferred_date, '%Y-%m-%d')
                )
            
            requirement.save()
            
            messages.success(
                request,
                f'Requirement submitted successfully! Your requirement ID is {requirement_id}. Our team will contact you shortly.'
            )
            return redirect('public:home')
            
        except Exception as e:
            messages.error(request, f'Error submitting requirement: {str(e)}')
    
    # Get categories for the form
    categories = Category.objects.filter(category_type='primary')
    context = {'categories': categories}
    return render(request, 'public/requirement_form.html', context)

