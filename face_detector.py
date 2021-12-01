import cv2

class FaceDetector:
    def __init__(self,path_of_detector:str) -> None:
        self.path_of_xml = path_of_detector
        self.cv2_detector = cv2.CascadeClassifier(self.path_of_xml)
    
    def __str__(self) -> str:
        return f"path of cv2 xml fiile: {self.path_of_xml}"

    def is_face_exist(self,img_path)->bool:
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.cv2_detector.detectMultiScale(gray, 1.4, 6, minSize=(30, 30))
        # check is answer is numpy array or check len
        if len(faces) > 0:
            return True
        else:
            return False