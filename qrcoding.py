import cv2
import numpy as np
import sys
import time

import urllib.request
def url_to_image(url):
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

#img = url_to_image(input())

img= url_to_image('https://stepik.org/media/attachments/course/128568/shelfQR0.png')
# cv2.imwrite("result.jpg", img)

qrDecoder = cv2.QRCodeDetector()

def lines_killer(lines): # Без него для каждой линии находятся прямые по краям линии, т.е. две, я убиваю одну из них чтобы точно определить количество
    for i in range(len(lines)):
        for j in range(len(lines)):
            if i!=j:
                if i<len(lines) and j <len(lines):
                    rho1, theta1 = lines [i,0] # Получить угол и расстояние до линии
                    rho2, theta2 = lines [j,0] # Получить угол и расстояние до линии
                    if abs(rho1-rho2) < 20 and abs(theta1-theta2) < 0.01:
                        lines=np.delete(lines,j,axis=0)
    return lines

def xy_lines(lines): # для разделения на массив горизонтальных и вертикальных точек у линий
    x_lines=[]
    y_lines=[]
    for i in range(len(lines)):
        rho, theta = lines [i,0]
        if theta<1:
            x_lines.append(rho)
        else:
            y_lines.append(rho)
    return x_lines,y_lines


def line_detection (image): # заданы прямые линии HoughLines
    gray = cv2.cvtColor (image, cv2.COLOR_BGR2GRAY) # перейти в оттенки серого
    canny = cv2.Canny (gray, 50, 150, apertureSize = 3) # обнаружение ловушек на краю
    lines = cv2.HoughLines (canny, 1, np.pi / 180,200) # Преобразование линии Hough

    #print(lines)
    #print(len(lines))
    lines=lines_killer(lines)
    #print(lines)
    #print(f'Всего линий на фотографии: {len(lines)}')
    
    lines_hor,lines_vert=xy_lines(lines)

    #print(f'Вертикальных линий : {len(lines_vert)}\nГоризонтальных линий : {len(lines_hor)}')
    lines_hor.sort()
    lines_vert.sort()
    #print(lines_vert,lines_hor)

    for i in range(len(lines)):
        rho, theta = lines [i,0] # Получить угол и расстояние до линии
        a = np.cos(theta)
        b = np.sin(theta)
        x0 =a*rho
        y0 =b*rho
        x1 = int(x0+1000*(-b))
        y1 = int(y0+1000*a)
        x2 = int(x0-1000*(-b))
        y2 = int(y0-1000 * a)
        cv2.line (image, (x1, y1), (x2, y2), (0,0,255), 1) # Рисуем линию на изображении
    return lines_vert,lines_hor



def image_splitter(img,x1_dot,y1_dot,x2_dot,y2_dot):
    x1_dot=int(x1_dot)
    y1_dot=int(y1_dot)
    x2_dot=int(x2_dot)
    y2_dot=int(y2_dot)
    img_part=img[y1_dot:y2_dot,x1_dot:x2_dot]
    return img_part

cv2.imshow("source_image",img)
y_dots,x_dots=line_detection(img)
cv2.imshow("changes",img)

img_part=image_splitter(img,x_dots[0],y_dots[0],x_dots[1],y_dots[1])
cv2.imshow("changes2",img_part)

for i in range(len(y_dots)-1):
    for j in range(len(x_dots)-1):
        x1=x_dots[j]
        y1=y_dots[len(y_dots)-2-i]
        x2=x_dots[j+1]
        y2=y_dots[len(y_dots)-1-i]
        #print(f"Границы:\n({x1},{y1}) - ({x2},{y2})")
        img_part=image_splitter(img,x1,y1,x2,y2)
        #cv2.imshow("changes",img_part)
        data,bbox,rectifiedImage = qrDecoder.detectAndDecode(img_part)
        if len(data)>0:
            word=data 
            letter=word.split(";")
            if i+1==int(letter[1]) and j+1==int(letter[2]):
                word=letter[0]+". Расположение верное."
            else: 
                word=letter[0]+". Расположение неверное."
        else:
            word='Товар отсутствует.'
        print(f"{i+1}-я полка {j+1}-й ряд. {word}")
#        
# cv2.imwrite("result.jpg", img)
# print(bbox)




cv2.waitKey(0)
cv2.destroyAllWindows()






# def qr_detect(img):
#     barcodes = pyzbar.decode(img)
#     try:
#         # Проход по найденным Qr-кодам
#         for barcode in barcodes:
#             # Расшифровка данных Qr кода, обязательно необходим split для
#             b_data = barcode.data.decode("utf-8").split(";")
#             # Получение координат центра Qr-кода
#             (x, y, w, h) = barcode.rect
#             xc = x + w//2
#             yc = y + h//2
#             # Вывод данных в необходимом формате
#             print("Qr have pose x= {}, y= {}".format(xc, yc))
#             print("Information decoding from Qr:")
#             # Вывод положения резервуаров, хранящих нефтепродукты, в правильном
#             for i in b_data: print("x= {} y= {} z= {} name={}".format(*i.split()))
#     except: pass
# # Распознаем Qr-код
# qr_detect(img)

                
