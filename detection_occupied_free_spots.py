from ultralytics import YOLO
import cv2
import configparser
import logging

logging.getLogger('ultralytics').setLevel(logging.CRITICAL)

config = configparser.ConfigParser()
config.read('config.ini')
rtsp = config['DEFAULT']['rtsp']
model = config['DEFAULT']['model']
threshold_value_iou = float(config['DEFAULT']['threshold_value_iou'])
path_to_file = config['DEFAULT']['path_to_file']

model = YOLO(model)

def load_parking_spots(file):

    parking_spots = {}

    with open(file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            spot_id = int(parts[0])
            x_center, y_center, width, height = map(float, parts[1:])
            parking_spots[spot_id] = (x_center, y_center, width, height)

    return parking_spots

def convert_to_pixel_coordinates(parking_spots, frame_width, frame_height):

    pixel_parking_spots = {}

    for spot_id, (x_center, y_center, width, height) in parking_spots.items():
        x1 = int((x_center - width / 2) * frame_width)
        y1 = int((y_center - height / 2) * frame_height)
        x2 = int((x_center + width / 2) * frame_width)
        y2 = int((y_center + height / 2) * frame_height)
        pixel_parking_spots[spot_id] = (x1, y1, x2, y2)

    return pixel_parking_spots

def intersection_calculation(box_car, box_place):

    x_c1, y_c1, x_c2, y_c2 = box_car
    x_p1, y_p1, x_p2, y_p2 = box_place
    
    inter_x1 = max(x_c1, x_p1)
    inter_y1 = max(y_c1, y_p1)
    inter_x2 = min(x_c2, x_p2)
    inter_y2 = min(y_c2, y_p2)
    
    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    boxA_area = (x_c2 - x_c1) * (y_c2 - y_c1)
    boxB_area = (x_p2 - x_p1) * (y_p2 - y_p1)
    
    iou = inter_area / float(boxA_area + boxB_area - inter_area)

    return iou

def object_detection(frame, results, pixel_parking_spots, occupied_spots):
    
    global threshold_value_iou

    for result in results:
        for box in result.boxes:
            coords = box.xyxy[0].int().tolist()
            left, top, right, bottom = coords
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
            
            for spot, (x1, y1, x2, y2) in pixel_parking_spots.items():
                iou = intersection_calculation((left, top, right, bottom), (x1, y1, x2, y2))                
                if iou > threshold_value_iou:
                    occupied_spots.add(spot)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, f'Occupied: {spot}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    return frame

def draw_parking_spots(frame, pixel_parking_spots, occupied_spots):

    for spot, (x1, y1, x2, y2) in pixel_parking_spots.items():
        color = (0, 255, 0) if spot not in occupied_spots else (0, 0, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, str(spot), (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return frame

def print_occupied_free_spots(occupied_spots, prev_occupied_spots, parking_spots):

    if occupied_spots != prev_occupied_spots:

        list_occupied_spots = set_formatting(occupied_spots)
        print('Occupied parking spaces:', list_occupied_spots)
        free_spots = set(parking_spots.keys()) - occupied_spots
        list_free_spots = set_formatting(free_spots)
        print('Free parking spaces:', list_free_spots)

        return occupied_spots.copy()
    
    return prev_occupied_spots

def set_formatting(spot_set:set) -> str:

    return ','.join(map(str, sorted(spot_set)))


def main():

    camera = cv2.VideoCapture(rtsp)

    if not camera.isOpened():
        print('Error connecting to camera')
        return

    ret, frame = camera.read()

    if not ret:
        print('Error capturing video stream')
        return

    frame_height, frame_width = frame.shape[:2]
    parking_spots = load_parking_spots(path_to_file)
    pixel_parking_spots = convert_to_pixel_coordinates(parking_spots, frame_width, frame_height)

    occupied_spots = set()
    prev_occupied_spots = set()

    while camera.isOpened():
        
        ret, frame = camera.read()

        if not ret:
            break

        results = model(frame)
        occupied_spots.clear()

        detected_objects_frame = object_detection(frame, results, pixel_parking_spots, occupied_spots)
        frame_with_boxes = draw_parking_spots(detected_objects_frame, pixel_parking_spots, occupied_spots)

        prev_occupied_spots = print_occupied_free_spots(occupied_spots, prev_occupied_spots, parking_spots)

        cv2.imshow('Parking Detection', frame_with_boxes)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()