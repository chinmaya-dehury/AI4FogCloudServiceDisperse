import os
import cv2
import time
import uuid
import psutil
import traceback
import logging
from logging.handlers import RotatingFileHandler
import numpy as np
from time import perf_counter
from flask import Flask, request, Response, jsonify

YOLO_CONFIG_PATH = os.getenv('YOLO_CONFIG')
YOLO_WEIGHTS_PATH = os.getenv('YOLO_WEIGHTS')
YOLO_LABELS_PATH = os.getenv('YOLO_COCO_NAMES')

# Initialize the Flask application
app = Flask(__name__)

# Configure logging to a file
handler = RotatingFileHandler('flask_error.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)

# Define an error handler for all exceptions
@app.errorhandler(Exception)
def handle_exception(error):
    trace = traceback.format_exc()
    app.logger.error('Unhandled exception! Error: %s, Trace: %s', error, trace)
    return f'Internal Server Error: {error}', 500

@app.route('/api/sync', methods=['POST'])
def detect():
    mainfolder = '..'
    
    unique_filename = str(uuid.uuid4())
    
    unique_input_video_name = f'{mainfolder}/input-{unique_filename}.mp4'
    unique_output_video_name = f'{mainfolder}/output-{unique_filename}.mp4'

    video_file = request.files["video"].read()

    # save video in fs
    with open(unique_input_video_name, "wb") as binary_file:
        # Write bytes to file
        binary_file.write(video_file)
        app.logger.error('LINE 196. Video file is written to the disk!!!')
    
    video_file = cv2.VideoCapture(unique_input_video_name)

    # initialize minimum probability to eliminate weak predictions
    p_min = 0.5

    # threshold when applying non-maxia suppression
    thres = 0.

    # Preparing variable for writer
    # that we will use to write processed frames
    writer = None

    # Preparing variables for spatial dimensions of the frames
    h, w = None, None

    # Create labels into list
    with open(YOLO_LABELS_PATH) as f:
        labels = [line.strip() for line in f]
        app.logger.error(f'LINE 216. LABELS are loaded succesfully ({labels})')
    # Initialize colours for representing every detected object
    colours = np.random.randint(0, 255, size=(len(labels), 3), dtype='uint8')

    # Loading trained YOLO v3 Objects Detector
    # with the help of 'dnn' library from OpenCV
    # Reads a network model stored in Darknet model files.
    network = cv2.dnn.readNetFromDarknet(YOLO_CONFIG_PATH, YOLO_WEIGHTS_PATH)
    app.logger.error(f'LINE 224. Config and Weights are loaded succesfully ({network})')

    # Getting only output layer names that we need from YOLO
    ln = network.getLayerNames()
    ln = [ln[i - 1] for i in network.getUnconnectedOutLayers()]

    # Defining loop for catching frames
    while True:
        ret, frame = video_file.read()
        if not ret:
            app.logger.error('LINE 106. RET IS NULL!!!')
            break

        # Getting dimensions of the frame for once as everytime dimensions will be same
        if w is None or h is None:
            # Slicing and get height, width of the image
            h, w = frame.shape[:2]

        # frame preprocessing for deep learning
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)

        # perform a forward pass of the YOLO object detector, giving us our bounding boxes
        # and associated probabilities.
        network.setInput(blob)
        output_from_network = network.forward(ln)

        # Preparing lists for detected bounding boxes, confidences and class numbers.
        bounding_boxes = []
        confidences = []
        class_numbers = []

        # Going through all output layers after feed forward pass
        for result in output_from_network:
            for detected_objects in result:
                scores = detected_objects[5:]
                class_current = np.argmax(scores)
                confidence_current = scores[class_current]

                if confidence_current > p_min:
                    box_current = detected_objects[0:4] * np.array([w, h, w, h])

                    # Now, from YOLO data format, we can get top left corner coordinates
                    # that are x_min and y_min
                    x_center, y_center, box_width, box_height = box_current
                    x_min = int(x_center - (box_width / 2))
                    y_min = int(y_center - (box_height / 2))

                    # Adding results into prepared lists
                    bounding_boxes.append([x_min, y_min, int(box_width), int(box_height)])
                    confidences.append(float(confidence_current))
                    class_numbers.append(class_current)

        # Implementing non-maximum suppression of given bounding boxes
        # With this technique we exclude some of bounding boxes if their
        # corresponding confidences are low or there is another
        # bounding box for this region with higher confidence
        results = cv2.dnn.NMSBoxes(bounding_boxes, confidences, p_min, thres)

        # At-least one detection should exists
        if len(results) > 0:
            for i in results.flatten():
                # Getting current bounding box coordinates, its width and height
                x_min, y_min = bounding_boxes[i][0], bounding_boxes[i][1]
                box_width, box_height = bounding_boxes[i][2], bounding_boxes[i][3]

                # Preparing colour for current bounding box
                colour_box_current = colours[class_numbers[i]].tolist()

                # Drawing bounding box on the original image
                cv2.rectangle(frame, (x_min, y_min), (x_min + box_width, y_min + box_height), colour_box_current, 2)

                # Preparing text with label and confidence for current bounding box
                text_box_current = '{}: {:.4f}'.format(labels[int(class_numbers[i])],
                                                    confidences[i])

                # Putting text with label and confidence on the original image
                cv2.putText(frame, text_box_current, (x_min, y_min - 5), cv2.FONT_HERSHEY_COMPLEX, 0.7, colour_box_current, 2)

        """Store proccessed frames into result video."""
        # Initialize writer
        if writer is None:
            resultVideo = cv2.VideoWriter_fourcc(*'mp4v')

            # Writing current processed frame into the video file
            writer = cv2.VideoWriter(unique_output_video_name, resultVideo, 30,(frame.shape[1], frame.shape[0]), True)
            app.logger.error('LINE 182. Writer is created')

        # Write processed current frame to the file
        writer.write(frame)

    # Releasing video reader and writer
    video_file.release()
    if writer is not None:
        writer.release()
        app.logger.error('LINE 189. Writer is released')

    # Return video
    output = []
    file = open(unique_output_video_name, "rb")
    byte = file.read(1)
    output.append(byte)
    while byte:
        byte = file.read(1)
        output.append(byte)
    file.close()

    if os.path.exists(unique_input_video_name):
        os.remove(unique_input_video_name)
        app.logger.error('LINE 332. Input Video file is removed from the disk!!!')
    if os.path.exists(unique_output_video_name):
        os.remove(unique_output_video_name)
        app.logger.error('LINE 335. Output Video file is removed from the disk!!!')

    return Response(response=output, status=200,mimetype="video/mp4")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)