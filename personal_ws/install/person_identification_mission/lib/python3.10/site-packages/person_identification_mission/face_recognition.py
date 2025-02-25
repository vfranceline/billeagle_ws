#!/usr/bin/env python3
import rclpy
import time
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import os
import cv2
import dlib
import numpy as np
from scipy.spatial import distance
from tkinter import *
from sensor_msgs.msg import Image
from bill_interfaces.srv import GetTrained
from bill_interfaces.srv import SearchFor

class FaceRecognitionNode(Node): 
    def __init__(self):
        super().__init__("face_recognition") 
        self.detector = dlib.get_frontal_face_detector()
        self.sp = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        self.facerec = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')
        self.labels, self._descriptors = self.prepare_training_data("images")
        
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            self.get_logger().error("Failed to open camera.")
            self.destroy_node()
            return
        
        self._getTrainedService=self.create_service(GetTrained,"get_trained",self.callback_get_trained) 
        self._searchForService=self.create_service(SearchFor,"search_for",self.callback_search_for) 
        self.image_publisher = self.create_publisher(Image, '/camera/image_raw', 10)
        
        self.get_logger().info("Face Recognition Node has started")
        self.bridge = CvBridge()  # Inicializa o CvBridge para conversão de imagem
        self.reset_capture_state()
        os.makedirs('predict', exist_ok=True)

        self.started = False
        self.recognition_enabled = False  # Active recognition
        self.total_faces_detected = 0
        self.detection_count = {}  # detections count for each person
        self.recognition_count = 0  # recognition counter
        
    def reset_capture_state(self):
        self.current_capture = 0
        self.max_captures = 5
        self.path = ""
        self.is_capturing = False
        self.global_capture_count = 0
        self.timer = None
        self.capture_sequence_count = 0  # Counter for sequences
        self.max_sequences = 3  # Maximum number of capture sequences
        self.can_capture = True  # Flag to control capturing state
        self.ok_sent = False  # Flag to indicate if "ok" has been sent


    def callback_get_trained(self, request, response):
        self.name =request.name
        response.trained=self.get_training("ok")     
        self.path = os.path.join(os.getcwd(), "images", self.name)
        os.makedirs(self.path, exist_ok=True)
        self.get_logger().info(f"Ready to capture images for: {self.name}")
        self.get_training()
        return response
    
    def get_training(self,name_to_train):
        if self.is_capturing and self.current_capture < self.max_captures:
            self.capture_image()

        elif self.current_capture >= self.max_captures:
            self.get_logger().info("All captures done for this sequence.")

            if not self.ok_sent:
                self.ok_sent = True  # indicate "ok" sent

            self.is_capturing = False  # Stop capturing
            self.capture_sequence_count += 1

            # Check if maximum capture sequences reached
            if self.capture_sequence_count >= self.max_sequences:
                self.get_logger().info("Maximum capture sequences reached. Shutting down...")
                self.can_capture = False 

            else:
                self.get_logger().info("Ready for the next sequence.")
                self.current_capture = 0  # Reset for the next sequence
                self.global_capture_count = 0  # Reset global capture count
                self.ok_sent = False  # Reset flag for the next sequence

        return True
    def capture_image(self):
        ret, frame = self.camera.read()
        if not ret:
            self.get_logger().error("Failed to capture image from the camera.")
            return
       # frame = cv2.flip(frame, 0) # SE A CÂMERA ESTIVER DE CABEÇA PARA BAIXO!

        image_path = os.path.join(self.path, f'{self.name}_{self.global_capture_count}_{int(time.time())}.png')
        success = cv2.imwrite(image_path, frame)

        if success:
            self.get_logger().info(f"Image saved as {image_path}")
            self.global_capture_count += 1
            self.current_capture += 1
            self.get_logger().info(f"Captured {self.current_capture} images so far.")

            # Publica a imagem no tópico /camera/image_raw
            msg = self.bridge.cv2_to_imgmsg(frame, "bgr8")
            self.image_publisher.publish(msg)
            self.get_logger().info("Published image to /camera/image_raw")

            if self.current_capture < self.max_captures:
                self.get_logger().info("Waiting before next capture...")

                if self.timer:
                    self.timer.cancel()
                self.timer = self.create_timer(1, self.capture_image)  # Set timer for next capture

        else:
            self.get_logger().error(f"Failed to save image at {image_path}")

    def callback_search_for(self, request, response):
        person_to_search=request.name
        response.found=self.search_for("ok")   
        if not self.started:
            self.get_logger().info("Preparing training data")
            self.labels, self._descriptors = self.prepare_training_data("images")
            self.started = True  # preparation finished

        self.recognition_enabled = True
        self.get_logger().info(f'Recognition enabled: {self.recognition_enabled}')
  
        return response
    
    def prepare_training_data(self, data_folder_path):
        labels = []
        descriptors = []
        if not os.path.exists(data_folder_path):
            self.get_logger().error(f"Data folder {data_folder_path} does not exist.")
            return labels, descriptors

        for label in os.listdir(data_folder_path):
            person_dir = os.path.join(data_folder_path, label)
            if not os.path.isdir(person_dir):
                self.get_logger().warning(f"{person_dir} is not a directory.")
                continue

            for image_name in os.listdir(person_dir):
                image_path = os.path.join(person_dir, image_name)
                img = cv2.imread(image_path)
                if img is None:
                    self.get_logger().warning(f"Could not read image {image_path}. Skipping.")
                    continue

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.detector(gray)

                if len(faces) == 0:
                    self.get_logger().warning(f"No faces detected in image {image_path}.")
                    continue

                for face in faces:
                    shape = self.sp(gray, face)
                    face_descriptor = self.facerec.compute_face_descriptor(img, shape)
                    descriptors.append(np.array(face_descriptor))
                    labels.append(label)

        self.get_logger().info(f"Total labels: {len(labels)}, Total descriptors: {len(descriptors)}")
        return labels, descriptors

    
    def search_for(self,person_to_search):
        if not self.recognition_enabled:
            self.get_logger().info("Recognition is not enabled.")
            return

        bridge = CvBridge()

        try:
            # Convert the mensage recieved e imagem OpenCV
            frame = bridge.imgmsg_to_cv2(request.image, desired_encoding="bgr8")
            # frame = cv2.flip(frame, 0) # SE A CÂMERA ESTIVER DE CABEÇA PARA BAIXO!

        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {e}")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        current_faces_detected = len(faces)

        self.get_logger().info(f"Detected {current_faces_detected} faces on screen.")

        if current_faces_detected == 0:
            return

        for face in faces:
            shape = self.sp(gray, face)
            face_descriptor = self.facerec.compute_face_descriptor(frame, shape)

            if face_descriptor is None:
                self.get_logger().warning("Face descriptor could not be computed.")
                continue  

            name = self.match_face(np.array(face_descriptor), self.labels, self._descriptors)

            # Inicializa contador de detecções para o nome reconhecido
            if name not in self.detection_count: 
                self.detection_count[name] = 0

            if name != "Unknown":
                self.detection_count[name] += 1
                self.get_logger().info(f"Recognized: {name}, Count: {self.detection_count[name]}")
                self.save_recognized_face(frame, name, face)  # Salva a imagem reconhecida

                if self.detection_count[name] == 12:
                    self.recognition_count +=1 
                    self.get_logger().info(f"Recognition limit reached for {name}. Total recognitions: {self.recognition_count}")
                    self.recognition_enabled = False  # Para o reconhecimento
                    self.detection_count[name] = 0
                    return
            else:
                self.detection_count[name] = 0
                self.save_recognized_face(frame, "Unknown", face)  # Salva a imagem desconhecida

            # Desenha o retângulo ao redor da face na imagem
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, name if name != "Unknown" else "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        self.total_faces_detected = current_faces_detected
        self.get_logger().info(f"Total faces detected on screen: {self.total_faces_detected}")

        return True
    
    def save_recognized_face(self, frame, name, face):
        if frame is None or not isinstance(frame, np.ndarray):
            self.get_logger().error("Invalid frame, cannot save.")
            return

        # Desenhar a bounding box na imagem
        x, y, w, h = face.left(), face.top(), face.height(), face.width()
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        file_name = os.path.join('predict', f"{name}.jpg")
        count = 1
        while os.path.exists(file_name):
            file_name = os.path.join('predict', f"{name}_{count}.jpg")
            count += 1

        self.get_logger().info(f"Saving image to: {file_name}")

        if cv2.imwrite(file_name, frame):
            self.get_logger().info(f"Saved recognized face: {file_name}")
        else:
            self.get_logger().error(f"Failed to save image: {file_name}")

    def match_face(self, face_descriptor, labels, descriptors):
        if len(descriptors) == 0:
            self.get_logger().warning("No face descriptors available for matching.")
            return "Unknown"
        
        distances = [distance.euclidean(face_descriptor, descriptor) for descriptor in descriptors]
        min_distance = min(distances)

        if min_distance < 0.9:  # Threshold
            index = distances.index(min_distance)
            return labels[index]
        
        return "Unknown"

def main(args=None):
    rclpy.init(args=args)
    node = FaceRecognitionNode()
    
    root = Tk()
    root.mainloop()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Node interrupted. Shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()
    
if __name__ == '__main__':
    main()