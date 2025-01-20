import cv2
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import csv
import glob


def generate_result(filename):
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    datetime_object = datetime.strptime(filename.split('/')[-1].split('.')[0].split('A')[0], "%Y%m%d_%H%M%S")
    print(datetime_object)
    csv_file = str(datetime_object) + '.csv'

    video = cv2.VideoCapture(filename)
    frame_rate = int(video.get(cv2.CAP_PROP_FPS))
    print(frame_rate)
    frame_count = 0
    box_buffer = defaultdict(list) 
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'detected', 'distance'])  
        
        while True:
            ret, frame = video.read()
            frame_count += 1
            if not ret:
                break
            timestamp = datetime_object + timedelta(seconds=frame_count / frame_rate)

            height, width, _ = frame.shape
            scale = 0.00392
            blob = cv2.dnn.blobFromImage(frame, scale, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)
            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    if class_id != 2:
                        continue
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            unique_classes = defaultdict(list)
            result = {}

            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    if w > 1200 or class_ids[i] == 0:
                        continue
                    unique_classes[class_ids[i]].append(boxes[i])
                    result = {class_id: len(det_boxes) for class_id, det_boxes in unique_classes.items()}

           
            for class_id, det_boxes in unique_classes.items():
                for box in det_boxes:
                    box_buffer[class_id].append(box)

            real_width_meters = 1.69  

            
            focal_length_pixels = 700 
            if frame_count % (0.5 * frame_rate) == 0:
                for class_id, boxes in box_buffer.items():
                    if boxes:
                        median_x = int(np.median([box[0] for box in boxes]))
                        median_y = int(np.median([box[1] for box in boxes]))
                        median_w = int(np.median([box[2] for box in boxes]))
                        median_h = int(np.median([box[3] for box in boxes]))

                        label = f'car: {class_id}'
                        print(f'Class ID: {class_id}, Median Box: [{median_x}, {median_y}, {median_w}, {median_h}]')

                        
                        distance_m = (real_width_meters * focal_length_pixels) / median_w
                        print(f"Estimated Distance: {distance_m:.2f} meters")

                        # Draw the median bounding box and the estimated distance
                        # cv2.rectangle(frame, (median_x, median_y), (median_x + median_w, median_y + median_h), (0, 255, 0), 2)
                        # cv2.putText(frame, f"{distance_m:.2f}m", (median_x, median_y + 30), cv2.FONT_HERSHEY_COMPLEX, 3, (0, 255, 0), 3)

                        # Write timestamp, detected classes, and distance to the CSV file
                        writer.writerow([timestamp.strftime('%Y-%m-%d %H:%M:%S'), result, f"{distance_m:.2f}m"])

                
                box_buffer.clear()
                # cv2.imshow("frame", frame)
                # WaitKey to allow for quitting during display
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break

    video.release()
    cv2.destroyAllWindows()


files = glob.glob('day3_nexar/*.mp4')
for file in files:
    generate_result(file)
