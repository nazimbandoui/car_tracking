import numpy as np
import cv2
import time


def foofunction(x, y):
    a = []
    b = []
    c = []
    for i in range(0, len(x)):
        state = False
        for j in range(0, len(y)):
            if np.all(x[i] == y[j]):
                b.append(x[i])
                state = True
        if not state:
            a.append(x[i])

    for i in range(0, len(y)):
        state = False
        for j in range(0, len(x)):
            if np.all(x[j] == y[i]):
                state = True
                break
        if not state:
            c.append(y[i])
    return a, b, c


def labelformat(a):
    a = str(a)
    for i in range(len(a), 4):
        a = "0"+a
    return a


car_cascade = cv2.CascadeClassifier('haar_car.xml')
init = False
car_dataset = []
frame_counter = 1

for i in range(1, 1701):
    img = cv2.imread("highway\\input\\in00"+labelformat(i)+".jpg")
    car_dataset.append(img)

all_cars = []
id_vehicle = 1

for img in car_dataset:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cars = car_cascade.detectMultiScale(gray, 1.1, 5)
    new_cars = []
    # read new detected objects
    for (x, y, w, h) in cars:
        new_cars.append(detected_object(x, y, w, h, "Vehicle TBD"))

    for element in range(len(all_cars)):
        all_cars[element].draw = False

    if not init and len(cars) > 0:
        for element in new_cars:
            element.label = str(id_vehicle)
            id_vehicle += 1
        all_cars = new_cars.copy()
        init = True

    elif init:
        # delete elements with no TTL left and decrements TTL
        for element in range(len(all_cars)):
            # todel = []
            if all_cars[element].TTL <= 0:
                all_cars[element].draw = False
            else:
                all_cars[element].TTL -= 1
                all_cars[element].draw = False
        # Determin object correspendence
        # compute xxo as [a,b] where a is the index of the new object in new_cars and o is the index of the object in all_cars
    if init and len(new_cars) > 0:
        xxo = []
        for new_element in range(len(new_cars)):
            distance = []
            distance_indexes = []
            for old_element in range(len(all_cars)):
                distance.append(new_cars[new_element].distance(
                    all_cars[old_element]))
                distance_indexes.append([new_element, old_element])
            xxo.append(distance_indexes[np.argmin(distance)])
        # Same thing as precedent , but this time we inverse the loop
        oxo = []
        for old_element in range(len(all_cars)):
            distance = []
            distance_indexes = []
            for new_element in range(len(new_cars)):
                distance.append(all_cars[old_element].distance(
                    new_cars[new_element]))
                distance_indexes.append([new_element, old_element])
            oxo.append(distance_indexes[np.argmin(distance)])
        # now we search for the intersection of xxo and oxo :
        # 1- if an element is common , the we update it's position in all_cars
        # 2 - if an element belongs only to xxo , then it's a new element
        # 3 - if an element belongs onlt to oxo , then we don't render it
        only_x, common, only_o = foofunction(xxo, oxo)
        # case 1 :
        for common_element in common:
            all_cars[common_element[1]].TTL = 5
            all_cars[common_element[1]].x = new_cars[common_element[0]].x
            all_cars[common_element[1]].y = new_cars[common_element[0]].y
            all_cars[common_element[1]
                     ].centroid = new_cars[common_element[0]].centroid
            all_cars[common_element[1]].draw = True
        # case 2 :
        for only_x_element in only_x:
            new_cars[only_x_element[0]].label = str(id_vehicle)
            new_cars[only_x_element[0]].draw = True
            id_vehicle += 1
            all_cars = list(all_cars)
            all_cars.append(new_cars[only_x_element[0]])
        # case 3 :
        for only_o_element in only_o:
            all_cars[only_o_element[1]].x = 9999
            all_cars[only_o_element[1]].y = 9999
            all_cars[only_o_element[1]].centroid = (9999, 9999)
            all_cars[only_o_element[1]].draw = False

    showdown = all_cars
    for element in showdown:
        element.history.append(element.centroid)
        print(element.history)
        if element.draw:
            startpoint = element.history[0]
            endpoint = element.history[-1]
            vector = (endpoint[0]-startpoint[0], endpoint[1]-startpoint[1])
            enddraw = (element.centroid[0]+vector[0],
                       element.centroid[1]+vector[1])
            cv2.rectangle(img, (element.x, element.y), (element.x +
                          element.w, element.y+element.h), (0, 0, 255), 2)
            cv2.putText(img, element.label, (element.x, element.y+element.h+50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            try:
                cv2.arrowedLine(img, element.centroid, enddraw, (255, 0, 0), 2)
            except:
                pass
            for i in element.history:
                cv2.circle(img, i, 2, (0, 255, 255), -1)
    cv2.imshow("CAR TRACKING", img)
    time.sleep(0.01)
    frame_counter += 1
    # Stop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
