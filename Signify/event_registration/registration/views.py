from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from .forms import RegistrationForm
from .models import Attendee
import qrcode
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib import messages
from .forms import RegistrationForm, NameTagTemplateForm
from .models import Attendee
import qrcode
from io import BytesIO
import base64
import os

from django.contrib.staticfiles.storage import staticfiles_storage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import base64
from django.shortcuts import render
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from .models import Attendee, NameTagTemplate
from django.http import HttpResponse
from reportlab.lib.pagesizes import B7
from reportlab.pdfgen import canvas
from django.conf import settings

font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'RAISONNE_DEMIBOLD.TTF')
print("Font path:", font_path)

# Register the custom font
pdfmetrics.registerFont(TTFont('RaisonneDemibold', font_path))

def search_attendee(request):
    searched = False
    attendees = []

    if request.method == 'GET':
        query = request.GET.get('query', '').strip()
        search_type = request.GET.get('search_type', '')

        if query:
            searched = True
            print(f"Searched for: {query} with search type: {search_type}")  # Debugging line

            if search_type == 'qr':
                attendees = Attendee.objects.filter(id=query)
            elif search_type == 'name':
                attendees = Attendee.objects.filter(name__icontains=query)
            elif search_type == 'email':
                attendees = Attendee.objects.filter(email__iexact=query)
            elif search_type == 'phone':
                attendees = Attendee.objects.filter(phone__iexact=query)

            print(f"Attendees found: {attendees}")  # Debugging line

    return render(request, 'registration/search.html', {
        'searched': searched,
        'attendees': attendees,
    })

def search(request):
    qr = request.GET.get('qr')
    searched = False
    attendee = None
    name_tag_image = None

    if qr:
        searched = True
        try:
            attendee = Attendee.objects.get(id=qr)  # Assuming QR holds Attendee ID
            print(f"Attendee found: {attendee.name}")  # Debugging line
            
            # Get the first uploaded template or handle the case when there are none
            template = NameTagTemplate.objects.last()  # Get the first uploaded template
            if template:
                print(f"Using template: {template.template.path}")  # Debugging line
                name_tag_image = template.template.url  # Save the URL to display in the template
            else:
                print("No template found.")  # Debugging line
                messages.error(request, "No name tag template found. Please upload a template.")
        except Attendee.DoesNotExist:
            print("Attendee not found.")  # Debugging line
            attendee = None
            
    return render(request, 'registration/search.html', {
        'attendee': attendee,
        'searched': searched,
        'name_tag_image': name_tag_image,
    })

# Register the custom font

def print_name_tags(request):
    if request.method == 'POST':
        attendee_ids = request.POST.getlist('attendee_ids')  # Get list of attendee IDs

        # Create a PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="name_tags.pdf"'
        
        # Create a canvas for the PDF
        p = canvas.Canvas(response)
        
        # Draw each name tag
        template = NameTagTemplate.objects.last()  # Get the last uploaded template
        if template:
            for attendee_id in attendee_ids:
                try:
                    attendee = Attendee.objects.get(id=attendee_id)
                    
                    # Draw the background template image
                    p.drawImage(template.template.path, 0, 0, width=100, height=100)  # Adjust dimensions as needed
                    
                    # Add name and company
                    p.setFont("RaisonneDemibold", 16)
                    p.drawString(50, 70, attendee.name)  # Adjust Y position as necessary
                    p.drawString(50, 50, attendee.company)  # Adjust Y position as necessary
                    p.showPage()  # Start a new page for each name tag
                except Attendee.DoesNotExist:
                    continue

        p.save()
        return response

    return HttpResponse("Invalid request method.", status=400)

def print_name_tag(request, qr):
    try:
        attendee = Attendee.objects.get(id=qr)  # Get attendee by QR code

        # Create a PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{attendee.name}_name_tag.pdf"'
        
        # Create a canvas for the PDF with B7 size
        p = canvas.Canvas(response, pagesize=B7)
        
        # Draw the background template image
        template = NameTagTemplate.objects.last()  # Get the last uploaded template
        if template:
            p.drawImage(template.template.path, 0, 0, width=B7[0], height=B7[1])  # Corrected dimensions for B7
        
        # Set the font to the registered custom font and font size to 16
        p.setFont("RaisonneDemibold", 16)
        
        # Calculate the width of the name and company text
        name_text = attendee.name
        company_text = attendee.company

        name_width = p.stringWidth(name_text, "RaisonneDemibold", 16)
        company_width = p.stringWidth(company_text, "RaisonneDemibold", 16)
        
        # Calculate X positions for centering
        name_x = (B7[0] - name_width) / 2
        company_x = (B7[0] - company_width) / 2
        
        # Add text for name and company, centered horizontally
        p.drawString(name_x, 200, name_text)  # Adjust Y position as necessary
        p.drawString(company_x, 150, company_text)  # Adjust Y position as necessary
        
        p.showPage()
        p.save()
        
        return response
    except Attendee.DoesNotExist:
        return HttpResponse("Attendee not found.", status=404)



from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import Attendee  # Make sure to import your Attendee model

def register(request):
    if request.method == 'POST':
        print("POST request received")  # Debugging line
        form = RegistrationForm(request.POST)
        
        # Check if the form is valid
        if form.is_valid():
            # Now you can safely access cleaned_data
            email = form.cleaned_data.get('email')  # Get the email from form data
            
            # Check if the email already exists
            if Attendee.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered.")
                return render(request, 'registration/register.html', {'form': form})  # Re-render the form with the error

            print("Form is valid")  # Debugging line
            attendee = form.save()
            print(f"Attendee saved: {attendee}")  # Debugging line

            # Generate QR code
            qr_code_value = attendee.qr_code_value or str(attendee.id)
            qr_img = qrcode.make(qr_code_value)
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format='PNG')

            # Convert QR code to base64 for embedding in the template
            qr_code_base64 = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')

            # Send confirmation email
            email = EmailMessage(
                'Event Registration Confirmation',
                'Thank you for registering, see attached your QR code.',
                'cy.xsolutions@gmail.com',
                [attendee.email],
            )
            email.attach('qr_code.png', qr_buffer.getvalue(), 'image/png')

            try:
                # email.send()  # Uncomment to send email
                print("Confirmation email sent")  # Debugging line
                messages.success(request, "Registration successful! Check your email for confirmation.")
            except Exception as e:
                print(f"Error sending email: {e}")  # Debugging line
                messages.error(request, "Registration successful, but there was an issue sending the confirmation email.")

            # Redirect to the success page with the QR code
            return render(request, 'registration/success.html', {
                'attendee': attendee,
                'qrcode_value': str(attendee.id),
                'qr_code_base64': qr_code_base64
            })  # Pass the base64 QR code to the success template
        else:
            print("Form is not valid")  # Debugging line
            print(form.errors)  # Log the errors in the form

    else:
        print("GET request received")  # Debugging line
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})



# Attendee search by QR code

# Upload name tag design template
from .forms import NameTagTemplateForm

def upload_name_tag_template(request):
    if request.method == 'POST':
        form = NameTagTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Template uploaded successfully.")
            return redirect('upload_template')  # Adjust this to your URL name
    else:
        form = NameTagTemplateForm()
    return render(request, 'registration/upload_template.html', {'form': form})



def success(request):
    return render(request, 'registration/success.html')  