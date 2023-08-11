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
from flask import Flask, request, Response, jsonify, send_file, after_this_request

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
# Run Detection
def run_detection(video_file):
    unique_filename = str(uuid.uuid4())
    unique_input_video_name = f'input-{unique_filename}.mp4'
    unique_output_video_name = f'output-{unique_filename}.mp4'

    # save video in fs
    with open(unique_input_video_name, "wb") as binary_file:
        binary_file.write(video_file)
        app.logger.error('LINE 196. Video file is written to the disk!!!')
    
    video_file = cv2.VideoCapture(unique_input_video_name)

    p_min = 0.5
    thres = 0.
    writer = None
    h, w = None, None
    with open(YOLO_LABELS_PATH) as f:
        labels = [line.strip() for line in f]
        app.logger.error(f'LINE 216. LABELS are loaded succesfully ({labels})')
    colours = np.random.randint(0, 255, size=(len(labels), 3), dtype='uint8')

    network = cv2.dnn.readNetFromDarknet(YOLO_CONFIG_PATH, YOLO_WEIGHTS_PATH)
    app.logger.error(f'LINE 224. Config and Weights are loaded succesfully ({network})')

    ln = network.getLayerNames()
    ln = [ln[i - 1] for i in network.getUnconnectedOutLayers()]

    frames_len = 0 
    while True:
        ret, frame = video_file.read()
        if not ret:
            app.logger.error('LINE 106. RET IS NULL!!!')
            break
        frames_len += 1
        if w is None or h is None:
            h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        network.setInput(blob)
        output_from_network = network.forward(ln)
        bounding_boxes = []
        confidences = []
        class_numbers = []
        for result in output_from_network:
            for detected_objects in result:
                scores = detected_objects[5:]
                class_current = np.argmax(scores)
                confidence_current = scores[class_current]
                if confidence_current > p_min:
                    box_current = detected_objects[0:4] * np.array([w, h, w, h])
                    x_center, y_center, box_width, box_height = box_current
                    x_min = int(x_center - (box_width / 2))
                    y_min = int(y_center - (box_height / 2))
                    bounding_boxes.append([x_min, y_min, int(box_width), int(box_height)])
                    confidences.append(float(confidence_current))
                    class_numbers.append(class_current)
        results = cv2.dnn.NMSBoxes(bounding_boxes, confidences, p_min, thres)
        if len(results) > 0:
            for i in results.flatten():
                x_min, y_min = bounding_boxes[i][0], bounding_boxes[i][1]
                box_width, box_height = bounding_boxes[i][2], bounding_boxes[i][3]
                colour_box_current = colours[class_numbers[i]].tolist()
                cv2.rectangle(frame, (x_min, y_min), (x_min + box_width, y_min + box_height), colour_box_current, 2)
                text_box_current = '{}: {:.4f}'.format(labels[int(class_numbers[i])],
                                                    confidences[i])
                cv2.putText(frame, text_box_current, (x_min, y_min - 5), cv2.FONT_HERSHEY_COMPLEX, 0.7, colour_box_current, 2)

        if writer is None:
            resultVideo = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(unique_output_video_name, resultVideo, 30,(frame.shape[1], frame.shape[0]), True)
            app.logger.error('LINE 182. Writer is created')
        writer.write(frame)

    video_file.release()
    if writer is not None:
        writer.release()
        app.logger.error('LINE 189. Writer is released')

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
    
    return unique_output_video_name, frames_len
# Run metrics normalizer
def metrics_normalizer(start, end):
	return abs(max(start, end) - min(start, end))
# Run measure metrics
def measure_metrics(func, value):
    # measure CPU usage during the function call
    start_cpu_usage = psutil.cpu_percent(interval=None)
    start_cpu_time = time.perf_counter()

    # measure memory usage during the function call
    start_mem_info = psutil.Process().memory_info()

    # measure throughput
    start_throughput_time = time.time()
    output_video_name, frames_len = func(value)
    end_throughput_time = time.time()
    total_throughput = frames_len / (end_throughput_time-start_throughput_time)

    # get cpu usage
    end_cpu_usage = psutil.cpu_percent(interval=None)
    end_cpu_time = time.perf_counter()
    total_cpu_usage = metrics_normalizer(start_cpu_usage, end_cpu_usage)

    # get memory usage
    end_mem_info = psutil.Process().memory_info()
    total_memory_usage = metrics_normalizer(start_mem_info.rss, end_mem_info.rss) / 1_000_000 # convert bytes to MB

    return output_video_name, round(total_cpu_usage, 3), round(total_memory_usage, 3), round(total_throughput,3)

@app.route('/api/sync', methods=['POST'])
def detect():
    # measure communication time    
    request_receive_time = time.time()
 
    request_id = request.form.get('request_id')
    video_file = request.files["video"].read()

    output_video_name, total_cpu_usage, total_memory_usage, total_throughput = measure_metrics(run_detection, video_file)

    response = { 
        'request_id': request_id,
		'output_video_name': output_video_name,
		'total_cpu_usage': total_cpu_usage, 
		'total_memory_usage': total_memory_usage,
        'total_throughput': total_throughput,
        'request_receive_time': request_receive_time
	}

    return jsonify(response)

@app.route('/api/sync/<video_name>')
def get_video(video_name):
    if os.path.exists(video_name):
        @after_this_request
        def delete_file(response):
            try:
                os.remove(video_name)
            except Exception as e:
                app.logger.error('LINE 176. Output Video file is removed from the disk!!!')
            return response
        return send_file(video_name, mimetype='video/mp4')
    else:
        return "Video not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)