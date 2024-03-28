from django.shortcuts import render
from django.shortcuts import render, redirect
import datetime

#for pdf generation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas




def home(request):
    current_datetime=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
# cresting pdf file wit object list and name for pdf
 # Assume this is a large list of products  
    products_list = [ 
    {'name': f"Product {i}", 'price': 19.99, 'description': f"This is product {i}"} for i in range(1, 101)
    ]

    output_pdf_file = f'request.user_{current_datetime}.pdf'

    # create_product_pdf(products_list, output_pdf_file)


    return render(request, 'test.html')








# function for crating pdf file 
def create_product_pdf(products, output_file):
    # Create a PDF canvas
    c = canvas.Canvas(output_file, pagesize=letter)

    # Set the font and font size
    c.setFont("Helvetica", 12)

    # Set the starting y-coordinate for writing text
    y_position = 750

    # Write the header
    c.drawString(250, y_position, "Detected Object List")
    y_position -= 20 
    c.drawString(30, y_position, "------------------------------------------------------------------------------------------------------------------------------------------")
    y_position -= 10 
    c.drawString(30, y_position, f"SR#")
    c.drawString(90, y_position, f"Name ")
    c.drawString(250, y_position, f"Price: ")
    c.drawString(400, y_position, f"Description: ")
    y_position -= 10  # Move to the next line
    c.drawString(30, y_position, "------------------------------------------------------------------------------------------------------------------------------------------")
    y_position -= 20 

    # Write each product's information
    for index, product in enumerate(products, start=1):
        if y_position <= 50:
            c.showPage()  # Start a new page
            c.setFont("Helvetica", 12)  # Reset font
            y_position = 750  # Reset y-coordinate
            # Write the header on the new page
            c.drawString(250, y_position, "Detected Object List")
            y_position -= 20 
            c.drawString(30, y_position, "------------------------------------------------------------------------------------------------------------------------------------------")
            y_position -= 10 
            c.drawString(30, y_position, f"SR#")
            c.drawString(90, y_position, f"Name ")
            c.drawString(250, y_position, f"Price: ")
            c.drawString(400, y_position, f"Description: ")
            y_position -= 10  # Move to the next line
            c.drawString(30, y_position, "------------------------------------------------------------------------------------------------------------------------------------------")
            y_position -= 20 

        c.drawString(30, y_position, f"{index}.")
        c.drawString(90, y_position, f"{product['name']}")
        c.drawString(250, y_position, f"{product['price']}")
        c.drawString(400, y_position, f"{product['description']}")
        y_position -= 25  # Move to the next product

    # Save the PDF file
    c.save()


    