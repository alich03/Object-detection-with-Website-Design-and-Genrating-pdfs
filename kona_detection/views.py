from django.shortcuts import render,redirect
from .models import Videos,Pdfs


import cv2
import matplotlib.pyplot as plt
import numpy as np
# from ultralytics import YOLO
import datetime
import os

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from .models_specs.model import mymodel


from django.core.files import File
# mymodel=YOLO("kona_detection/models/best.pt")
# kona_classes=['AC', 'Bathtub', 'Bed Frame', 'Bed', 'Closet', 'Cupboard', 'Desk', 'Dining Table', 'Dish Washer', 'Door', 'Exhaust Fan', 'Exhaust Hood','Faucet', 'Fridge', 'Microwave', 'Oven', 'Sink', 'Sofa', 'Stove', 'TV', 'Thermo Ventilator','Toilet Sink', 'Toilet', 'Washing Machine', 'Water Cubicle', 'Water Heater', 'Windowsill','Chair',  'Computer', 'Monitor', 'Shelf', 'Table', 'Window','Air-conditioner', 'bottle', 'bowl', 'clock', 'cup', 'fork', 'hairdryer', 'kettle', 'key', 'knife',  'pen', 'phone', 'remote-control', 'rice-cooker', 'scissor', 'spoon', 'teapot','Book', 'Curtain', 'Frame', 'Lamp', 'Rug', 'Socket', 'Switch',  'Television', 'Vase','jewellery','laptop','sliper','Watch']


# Create your views here.
def run_model_live(request):

    camera_id=0

    cap = cv2.VideoCapture('media/videos/test.webm')  

    frame_count=0
    objects_list = []
    while True:

        frame_count=frame_count+1
        if frame_count%3 != 0:
            continue
        ret, frame = cap.read()

        if not ret:
            break

        result=mymodel.predict(frame,conf=0.7)
        cc_data=np.array(result[0].boxes.data)

        if len(cc_data) != 0:
                    xywh=np.array(result[0].boxes.xywh).astype("int32")
                    xyxy=np.array(result[0].boxes.xyxy).astype("int32")
                    
                    for (x1, y1, _, _), (_, _, w, h), (_,_,_,_,conf,clas) in zip(xyxy, xywh,cc_data):
                            
                                        cv2.rectangle(frame,(x1,y1),(x1+w,y1+h),(255,0,255),2)
                                        class_name=kona_classes[int(clas)]
                                        confidence=np.round(conf*100,1)
                                        text = f"{class_name}-{confidence}%"
                                        cv2.putText(frame, text, (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX,0.45,(0, 0, 255), 2)

                                        detected_obj={'name':class_name,'price':confidence,'description':f' {class_name}_{confidence}'}
                                        product_found = any(product['name'] == class_name for product in objects_list)

                                        if not product_found:
                                                    objects_list.append(detected_obj)
                                        else:
                                            for index, product in enumerate(objects_list):
                                                if product['name'] == class_name and confidence > product['price']:
                                                    objects_list[index] = detected_obj
                                                
                                                
    
        cv2.imshow("live camera for kona", frame)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    #creating pdf file from detected objects from model
    current_datetime=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    if len(objects_list) != 0:
        output_pdf_file = f'request.user_{current_datetime}.pdf'
        create_product_pdf(objects_list, output_pdf_file)

    return render(request,'run_on_live_camera.html')


def run_model_video(request):

    if request.method == 'POST':
        video_title = request.POST.get('title')
        video_file = request.FILES.get('video_file')
        if video_title and video_file:
            video_object = Videos.objects.create(title=video_title, video_file=video_file)
            video_url = video_object.video_file.url
            video_file_ = video_object.video_file

            video_url=os.path.join('media',video_url)
            if video_url.startswith('/'):
                video_url = video_url[1:]
            cap = cv2.VideoCapture(video_url)  

            frame_count=0
            objects_list = []
            while True:

                # frame_count=frame_count+1
                # if frame_count%3 != 0:
                #     continue
                ret, frame = cap.read()

                if not ret:
                    break
                results=mymodel(frame)
                if len(results['predictions']) != 0:
                            for myobject in results['predictions']:
                                                
                                                x1=int(myobject['x'])
                                                y1=int(myobject['y'])
                                                w=int(myobject['width'])
                                                h=int(myobject['height'])

                                                class_name=myobject['class']
                                                class_index=myobject['class_id']
                                                confidence=np.round(myobject['confidence'],2)*100

                                                cv2.rectangle(frame,(x1,y1),(x1+w,y1+h),(255,0,255),2)
                                                text = f"{class_name}"
                                                cv2.putText(frame, text, (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX,0.45,(0, 0, 255), 2)
                                                
                                                #working for pdfs
                                                detected_obj={'name':class_name,'price':class_index,'description':f' {class_name}_{confidence}'}
                                                product_found = any(product['name'] == class_name for product in objects_list)

                                                if not product_found:
                                                            objects_list.append(detected_obj)
                                                else:
                                                    for index, product in enumerate(objects_list):
                                                        if product['name'] == class_name and confidence > product['price']:
                                                            objects_list[index] = detected_obj
                cv2.imshow("live camera for kona", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            
            current_datetime=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            if len(objects_list) != 0:
                output_pdf_file = f'{current_datetime}.pdf'
                create_product_pdf(objects_list, output_pdf_file)

                if output_pdf_file:
                   with open(output_pdf_file, 'rb') as file:
                        mypdf_file = File(file)
                    # Create an instance of Pdfs model and save it
                        pdf_instance = Pdfs.objects.create(pdf_id=current_datetime, pdf_title=output_pdf_file, pdf_file=mypdf_file)
                        #dlete from dir after saving in db
                        if os.path.exists(output_pdf_file):
                            try:
                                os.remove(output_pdf_file)
                            except:
                                  pass
                try:
                      Videos.objects.all().delete()

                except:
                      pass

    return render(request,'run_on_video.html')

# function for crating pdf file


def create_product_pdf(products, output_file):
    # Create a PDF canvas
    c = canvas.Canvas(output_file, pagesize=letter)

    # Set the font and font size
    c.setFont("Helvetica", 12)

    # Set the starting y-coordinate for writing text
    y_position = 720
    logo_path="static\logo\kona_logo.jpeg"
    logo = ImageReader(logo_path)
    c.drawImage(logo, 250, y_position, width=100, height=60)
    y_position -= 20
    #wrte address
    c.drawString(450, y_position, "Address:")
    #id ,tim date
    c.drawString(100, y_position, "Id: 032324030")
    y_position -= 20
    c.drawString(400, y_position, "house 30,street 30")
    c.drawString(100, y_position, "Date: 28-May-2024")
    y_position -= 20
    c.drawString(400, y_position, "Benglore")
    c.drawString(100, y_position, "Time: 08:23:03")
    y_position -= 20
    c.drawString(400, y_position, "Punjab,India")
    c.drawString(100, y_position, "User: username")
    
    # Write the header
    y_position -= 30
    c.drawString(250, y_position, "Detected Object List")
    c.setFont("Helvetica", 10)
    y_position -= 20 
    c.drawString(30, y_position, "---------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    y_position -= 10 
    c.drawString(30, y_position, f"Sr#")
    c.drawString(90, y_position, f"Class ")
    c.drawString(250, y_position, f"Confidence: ")
    c.drawString(400, y_position, f"Class+Confidence: ")
    y_position -= 10  # Move to the next line
    c.drawString(30, y_position, "---------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    y_position -= 20 

    # Write each product's information
    for index, product in enumerate(products, start=1):
        if y_position <= 50:
            c.showPage()  # Start a new page
            c.setFont("Helvetica", 10)  # Reset font
            y_position = 730  # Reset y-coordinate
            # Write the header on the new page
            y_position -= 10 
            c.drawString(30, y_position, f"Sr#")
            c.drawString(90, y_position, f"Class ")
            c.drawString(250, y_position, f"Confidence ")
            c.drawString(400, y_position, f"Class+Confidence ")
            y_position -= 10  # Move to the next line
            c.drawString(30, y_position, "---------------------------------------------------------------------------------------------------------------------------------------------------------------------")
            y_position -= 20 

        c.drawString(30, y_position, f"{index}.")
        c.drawString(90, y_position, f"{product['name']}")
        c.drawString(250, y_position, f"{product['price']}")
        c.drawString(400, y_position, f"{product['description']}")
        y_position -= 25  # Move to the next product

    # Save the PDF file
    c.save()