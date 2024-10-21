import qrcode
from io import BytesIO
from django.core.files import File
from reportlab.pdfgen import canvas

def generate_qr_code(data):
    qr = qrcode.make(data)
    qr_io = BytesIO()
    qr.save(qr_io, 'PNG')
    qr_io.seek(0)
    return File(qr_io, name=f"{data}.png")
def generate_name_tag(attendee, template_path, start_position):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(91, 128))  # B7 size

    # Load background template
    c.drawImage(template_path, 0, 0, width=91, height=128)

    # Draw attendee details at start_position (tuple: (x, y))
    c.setFont("Helvetica", 12)
    c.drawString(start_position[0], start_position[1], attendee.name)
    c.drawString(start_position[0], start_position[1] - 20, attendee.company)

    c.save()
    buffer.seek(0)
    return buffer