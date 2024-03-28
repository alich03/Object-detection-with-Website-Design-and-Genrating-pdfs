from django.shortcuts import render,redirect
from .models import Videos


import cv2
import numpy as np
from ultralytics import YOLO
from io import BytesIO
import datetime
import os

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


mymodel=YOLO("kona_detection/models/best.pt")
kona_classes=['AC', 'Bathtub', 'Bed Frame', 'Bed', 'Closet', 'Cupboard', 'Desk', 'Dining Table', 'Dish Washer', 'Door', 'Exhaust Fan', 'Exhaust Hood','Faucet', 'Fridge', 'Microwave', 'Oven', 'Sink', 'Sofa', 'Stove', 'TV', 'Thermo Ventilator','Toilet Sink', 'Toilet', 'Washing Machine', 'Water Cubicle', 'Water Heater', 'Windowsill','Chair',  'Computer', 'Monitor', 'Shelf', 'Table', 'Window','Air-conditioner', 'bottle', 'bowl', 'clock', 'cup', 'fork', 'hairdryer', 'kettle', 'key', 'knife',  'pen', 'phone', 'remote-control', 'rice-cooker', 'scissor', 'spoon', 'teapot','Book', 'Curtain', 'Frame', 'Lamp', 'Rug', 'Socket', 'Switch',  'Television', 'Vase','jewellery','laptop','sliper','Watch']



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
            print(video_url)
            print(video_file_)

            cap = cv2.VideoCapture(video_url)  

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

            current_datetime=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            if len(objects_list) != 0:
                output_pdf_file = f'request.user_{current_datetime}.pdf'
                create_product_pdf(objects_list, output_pdf_file)

    return render(request,'run_on_video.html')



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
            c.drawString(90, y_position, f"Class ")
            c.drawString(250, y_position, f"Confidence ")
            c.drawString(400, y_position, f"Class+Confidence ")
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

