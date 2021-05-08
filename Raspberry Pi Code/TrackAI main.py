import cv2, pyrebase, socket,struct
import numpy as np
from tracker import CentroidTracker
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(33,GPIO.IN)
GPIO.setup(34,GPIO.IN)
GPIO.setup(36,GPIO.OUT)
GPIO.setup(37,GPIO.OUT)


RollOut = GPIO.PWM(36,300)
PitchOut = GPIO.PWM(37,300)
RollOut.start(50)
PitchOut.start(50)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

print('HOST IP:', host_ip)
port = 9999
socket_address = (host_ip, port)
server_socket.bind(socket_address)
server_socket.listen(5)
print("LISTENING AT:", socket_address)

#=============== Video Streamer ===============#
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = '192.168.137.33' #RPi ip
port = 9000
client_socket.connect((host_ip, port))
data = b""
payload_size = struct.calcsize("Q")
#==============================================#

tracker = CentroidTracker(maxDisappeared=80)
config = {
############ Firebase details
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
# ========= Variables =========#
ROI_dif = 100
counter = 0
Move_Dir = "null"
FrameCentre = 640
PreArea = 0
# =============================#
# ===== Getting Video =====#
cap = cv2.VideoCapture("rtsp://192.168.137.33:8554")
# cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('TrackAI.avi',fourcc, 3.2, (640,480), True)
# =========================#
# =========== Obj_Detection_Config ===========#
configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'
net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)
# ============================================#

RpiSocket, addr = server_socket.accept()
print("Got connection from", addr)

while True:

#################################
RollIN = 50  # note:
PitchIN = 50 # note:
#NOTE: The method I use to read PWM signals from the receiver is not even close to accurate. So, please suggest a better way.
# RollIN reads PWM on pin 33
# PitchIN reads PWM on pin 34 
#################################


    try:

        trackstatus = db.child("checkpoint").get().val()
        if (trackstatus == "track_proceed"):

            if (counter == 0):
                Detected_ClassId = 0
                RoiX1 = int(db.child("coordinates").child("Xa1").get().val()
                RoiY1 = int(db.child("coordinates").child("Ya1").get().val()
				RoiX2 = int(db.child("coordinates").child("Xa2").get().val()
                RoiY2 = int(db.child("coordinates").child("Ya2").get().val()
				PreArea = abs((RoiX1-RoiX2)*(RoiY1-RoiY2))

                # ================ ROI & ObjD Initially  =================#
                rects = []
                success, img = cap.read()
                classIds, confs, bbox = net.detect(img, confThreshold=0.4)
                bbox = list(bbox)
                confs = list(np.array(confs).reshape(1, -1)[0])
                confs = list(map(float, confs))
                indicies = cv2.dnn.NMSBoxes(bbox, confs, 0.2, 0.1)

                if len(classIds) != 0:
                    i = indicies[0][0]
                    box = bbox[i]
                    rects.append(box)
                    object = tracker.update(rects)
                    X = object[1][0][0]
                    Y = object[1][0][1]
                    W = object[1][0][2]
                    H = object[1][0][3]
                    X2 = X + W)
                    Y2 =(Y + H)
                    if abs(RoiX1 - X) <= ROI_dif and abs(RoiY1 - Y) <= ROI_dif abs(RoiX2 - X2) <= ROI_dif and abs(RoiY2 - Y2) <= ROI_dif :
                        Detected_ClassId = classIds[0][0]

                # =========================================================#
                counter = (counter + 1)

            elif (counter == 1):
                rects = []
                success, img = cap.read()
                classIds, confs, bbox = net.detect(img, confThreshold=0.4)
                if len(classIds) != 0:

                    if classIds[0][0] == Detected_ClassId:
                        bbox = list(bbox)
                        confs = list(np.array(confs).reshape(1, -1)[0])
                        confs = list(map(float, confs))
                        indicies = cv2.dnn.NMSBoxes(bbox, confs, 0.2, 0.1)
        
                        for i in indicies:
                            i = i[0]
                            box = bbox[i]
                            rects.append(box)
                            object = tracker.update(rects)
                            X = object[1][0][0]
                            Y = object[1][0][1]
                            W = object[1][0][2]
                            H = object[1][0][3]
							PostArea = (W*H)
							
                            #print("ClassID:-", classIds[0][0])
                            cv2.rectangle(img, (X, Y), (X + W, Y + H), (0, 255, 0), 2)
                            cX = (X + (X + W)) / 2
                            # extreme diff = 310
                            # minimum diff = 150
                            # RIGHT
                            if((cX - FrameCentre) >= 150 and (cX - FrameCentre) < 310):
                                Move_Dir = "right"
								RollOut.ChangeDutyCycle(58)
			
								
                            elif((cX - FrameCentre) >= 310):
                                Move_Dir = "Right"
								RollOut.ChangeDutyCycle(32)
								
                            # LEFT
                            elif ((FrameCentre - cX) >= 150 and (FrameCentre - cX) < 310):
                                Move_Dir = "left"
								RollOut.ChangeDutyCycle(42)
								
								
                            elif ((FrameCentre - cX) >= 310):
                                Move_Dir = "Left"
								RollOut.ChangeDutyCycle(68)
								
							else:
								RollOut.ChangeDutyCycle(RollIN)
								
			#######################################################################				
							
                        if(PreArea - PostArea >= 50):
							PitchOut.ChangeDutyCycle(58)
						
						elif(PostArea - PreArea >= 50):
							PitchOut.ChangeDutyCycle(42)
						else:
							PitchOut.ChangeDutyCycle(PitchIN)
							
					  

        elif (trackstatus == "track_abort"):
            success, img = cap.read()
            counter = 0
        # out.write(img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except:
        pass
cap.release()
# out.release() # save whole video on raspberry pi storage
cv2.destroyAllWindows()