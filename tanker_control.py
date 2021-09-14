from __future__ import print_function
import serial
import requests
import time
import can  # add thư viện canbus
import pymysql  # database
import os
import math
import numpy as np
import RPi.GPIO as GPIO  # add library GPIO
from threading import Thread  # add library threading run multiple def
from datetime import datetime

time.sleep(5) #delay đợi server online 5

error = 0
counter = 0
temp_b = 1
temp_c = 0

# khai báo phương thức và tên của giao thức can bus trong Raspberry
bus = can.interface.Bus(channel='can0', bustype='socketcan_native')

# khai báo các id cần gửi của canbus
id_canbus = [101, 201, 301, 401, 501]
# Khai báo các dư liệu cần gửi qua canbus
data = [(00, 00, 00, 00,  6, 00,  2, 00), (00, 00, 00, 00,  1, 00,  2, 00),  # go up and down
        (00, 00, 00, 00,  8, 00,  2, 00), (00, 00, 00, 00,  7, 00,  2, 00),  # turn left and right
        (00, 00, 00, 00,  9, 00,  2, 00), (00, 00, 00, 00,  4, 00,  2, 00),  # around left and right
        (00, 00, 00, 00, 00, 00, 00, 00),  # stop
        (00, 00, 00, 00,  1,  1, 00, 00), (00, 00, 00, 00,  6,  1, 00, 00),  # screw go up and down
        (00, 00, 00, 00,  10,  00, 2, 00)] # run fast
# khai báo database phpmyadmin
connection = pymysql.connect(
    host="localhost", user="root", passwd="raspberry", database="tanker")
cursor = connection.cursor()

def dextohex(decimal):
    return hex(decimal)[2:]

def take_angle():
    connection = pymysql.connect(
            host="localhost", user="root", passwd="raspberry", database="tanker")
    cursor = connection.cursor()

    retrive_1 = "Select * from GY25;"
    # executing the quires
    cursor.execute(retrive_1)
    rows_1 = cursor.fetchall()
    return rows_1[0][3]

def canbus(data_msg):
    global bus

    msg = can.Message(arbitration_id=301,
                    data=data_msg,
                    is_extended_id=False)  # khai báo id mang giá trị
    bus.send(msg)  # send giá trị với id đã đc khai báo bên trên

def action():  # void main              
                                      
    # biến kết nối vào database cho việc update
    update_conn = pymysql.connect(
        host="localhost", user="root", passwd="raspberry", database="tanker")
    # biết chạy kết nối vào database cho việc update
    update_cursor = update_conn.cursor()
    # queries for retrievint all rows
    # khai báo lệnh update data vào database
    update_retrive = "UPDATE `move_control` SET `level` = '0' WHERE `move_control`.`id` = 1;"

    # executing the quires
    update_cursor.execute(update_retrive)  # chạy lệnh update
    update_conn.commit()  # xác nhận update

    # khai báo database phpmyadmin
    # con_permission = pymysql.connect(
    #     host="localhost", user="root", passwd="raspberry", database="tanker")
    # cursor_permission = con_permission.cursor()

    arr = np.array([0.0])

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
    time.sleep(1)     #time.sleep(1)
    GPIO.output(17, True)
    time.sleep(2)     #time.sleep(2)
    GPIO.output(17, False)
    time.sleep(2)     #time.sleep(2)

    while True:
        global arr_permission  # lấy biến array từ biên ngoài
        global error  # lấy biến từ biên ngoài
        global counter
        global temp_b
        global temp_c
    
    # -----------------------------------------------đọc dữ liệu từ database--------------------------------------------------------
        # khai báo database phpmyadmin
        connection = pymysql.connect(
            host="localhost", user="root", passwd="raspberry", database="tanker")
        cursor = connection.cursor()
        # queries for retrievint all rows
        retrive = "Select * from move_control;"
        # executing the quires
        cursor.execute(retrive)
        rows = cursor.fetchall()

        check_connection = rows[0][1] - rows[0][0]
        # print("level=",rows[0][1])
        if rows[0][1] == 0:
            counter = 0
            temp_b = 1
        
    # ---------------------------------------------sét giá trị từ database chuẩn bị để gửi cho canbus-------------------------------
        if check_connection >= 0:  # nếu hiệu của giá trị mảng thứ 2 và giá trị thứ 1 >= 1 thì :
            if rows[0][1] == 6:
                data_msg = data[0]
            #wheel go down
            elif rows[0][1] == 1:
                data_msg = data[1]
            # wheel turn left
            elif rows[0][1] == 8:
                data_msg = data[2]
            # wheel turn right
            elif rows[0][1] == 7:
                data_msg = data[3]
            # wheel turn around left
            elif rows[0][1] == 9:
                data_msg = data[4]
            # wheel turn around right
            elif rows[0][1] == 4:
                data_msg = data[5]
            # screw go up
            elif rows[0][1] == 11:
                data_msg = data[7]
            # screw go down
            elif rows[0][1] == 12:
                data_msg = data[8]
            # RUN FAST
            elif rows[0][1] == 10:
                data_msg = data[9]
            else:
                data_msg = data[6]
        else:  # nếu hiệu của giá trị mảng thứ 2 và giá trị thứ 1 <= 0 thì :
            data_msg = data[6]
            # queries for retrievint all rows
            update_retrive = "UPDATE `move_control` SET `level` = '0' WHERE `move_control`.`id` = 1;"
            # executing the quires
            update_cursor.execute(update_retrive)
            update_conn.commit()
    # ------------------------------------go race ----------------------------------
        if check_connection >= 0:
            if rows[0][1] == 13 and counter == 0:
                # canbus(data[0])
                # time.sleep(8)
                # while True:
                #     if temp_c == 0:
                #         arr = np.append(arr, take_angle())
                #         temp_c = 1
                #     # print("arr[1]=",arr[1])
                #     if float(arr[1]) > 0:
                #         meas = float(arr[1]) - float(take_angle())
                #         # print("meas1=",meas)
                #         if meas > 154 and meas < 206:
                #             canbus(data[6])
                #             temp_c = 0
                #             arr = np.array([0.0])
                #             break
                #         else:
                #             canbus(data[4])
                #             time.sleep(0.2)
                #     else:
                #         meas = float(take_angle()) - float(arr[1])
                #         # print("meas2=",meas)
                #         if meas > 154 and meas < 206:
                #             canbus(data[6])
                #             temp_c = 0
                #             arr = np.array([0.0])
                #             break
                #         else:
                #             canbus(data[4])
                #             time.sleep(0.2)
                # canbus(data[6])
                # time.sleep(0.6)
                canbus(data[0])
                time.sleep(10)
                while True:
                    if temp_c == 0:
                        arr = np.append(arr, take_angle())
                        temp_c = 1
                    # print("arr[1]=",arr[1])
                    if float(arr[1]) > 0:
                        meas = float(arr[1]) - float(take_angle())
                        # print("meas1=",meas)
                        if meas > 154 and meas < 206:
                            canbus(data[6])
                            temp_c = 0
                            arr = np.array([0.0])
                            break
                        else:
                            canbus(data[4])
                            time.sleep(0.2)
                    else:
                        meas = float(take_angle()) - float(arr[1])
                        # print("meas2=",meas)
                        if meas > 154 and meas < 206:
                            canbus(data[6])
                            temp_c = 0
                            arr = np.array([0.0])
                            break
                        else:
                            canbus(data[4])
                            time.sleep(0.2)
                canbus(data[6])
                time.sleep(0.6)
                canbus(data[0])
                time.sleep(10)
                while True:
                    if temp_c == 0:
                        arr = np.append(arr, take_angle())
                        temp_c = 1
                    # print("arr[1]=",arr[1])
                    if float(arr[1]) > 0:
                        meas = float(arr[1]) - float(take_angle())
                        # print("meas1=",meas)
                        if meas > 154 and meas < 206:
                            canbus(data[6])
                            temp_c = 0
                            arr = np.array([0.0])
                            break
                        else:
                            canbus(data[5])
                            time.sleep(0.2)
                    else:
                        meas = float(take_angle()) - float(arr[1])
                        # print("meas2=",meas)
                        if meas > 154 and meas < 206:
                            canbus(data[6])
                            temp_c = 0
                            arr = np.array([0.0])
                            break
                        else:
                            canbus(data[5])
                            time.sleep(0.2)
                canbus(data[6])
                time.sleep(0.6)
                canbus(data[0])
                time.sleep(10)
                while True:
                    if temp_c == 0:
                        arr = np.append(arr, take_angle())
                        temp_c = 1
                    # print("arr[1]=",arr[1])
                    if float(arr[1]) > 0:
                        meas = float(arr[1]) - float(take_angle())
                        # print("meas1=",meas)
                        if meas > 154 and meas < 206:
                            canbus(data[6])
                            temp_c = 0
                            arr = np.array([0.0])
                            break
                        else:
                            canbus(data[4])
                            time.sleep(0.2)
                    else:
                        meas = float(take_angle()) - float(arr[1])
                        # print("meas2=",meas)
                        if meas > 154 and meas < 206:
                            canbus(data[6])
                            temp_c = 0
                            arr = np.array([0.0])
                            break
                        else:
                            canbus(data[4])
                            time.sleep(0.2)
                canbus(data[6])
                time.sleep(0.6)
                canbus(data[0])
                time.sleep(10)
                while True:
                    if temp_c == 0:
                        arr = np.append(arr, take_angle())
                        temp_c = 1
                    # print("arr[1]=",arr[1])
                    if float(arr[1]) > 0:
                        meas = float(arr[1]) - float(take_angle())
                        # print("meas1=",meas)
                        if meas > 154 and meas < 206:
                            canbus(data[6])
                            temp_c = 0
                            arr = np.array([0.0])
                            break
                        else:
                            canbus(data[5])
                            time.sleep(0.2)
                    else:
                        meas = float(take_angle()) - float(arr[1])
                        # print("meas2=",meas)
                        if meas > 154 and meas < 206:
                            canbus(data[6])
                            temp_c = 0
                            arr = np.array([0.0])
                            break
                        else:
                            canbus(data[5])
                            time.sleep(0.2)
                canbus(data[6])
                time.sleep(0.6)
                canbus(data[0])
                time.sleep(3)
                canbus(data[6])
                time.sleep(0.6)
                counter = counter + 1     
        for i in range(len(id_canbus)):  # send giá trị data đến địa chỉ ID đã định sẵn
                if id_canbus[i] == 101 or id_canbus[i] == 201:
                    msg = can.Message(arbitration_id=id_canbus[i],
                                    data=[00, 00, 00, 00, 00, 00, 00, 00],
                                    is_extended_id=False)  # khai báo id mang giá trị
                else:
                    msg = can.Message(arbitration_id=id_canbus[i],
                                    data=data_msg,
                                    is_extended_id=False)  # khai báo id mang giá trị
                try:
                    bus.send(msg)  # send giá trị với id đã đc khai báo bên trên
                    # delay khoảng 1s nếu có 5 địa chỉ dc gửi 0.182s
                    time.sleep(0.09)  # delay time.sleep(0.2)
                    dataCanbus = bus.recv(0.0)
                    #duy
                    if dataCanbus is None:
                        print("Don't Have Any Response From CANBUS")

                        # queries for retrievint all rows
                        update_retrive = "UPDATE `move_control` SET `error_can` = 'OK' WHERE `move_control`.`id` = 1;"

                        # executing the quires
                        update_cursor.execute(update_retrive)
                        update_conn.commit()

                    else:
                        if dataCanbus.arbitration_id == 102:
                            voltage = "0x" + \
                                dextohex(dataCanbus.data[5]) + \
                                dextohex(dataCanbus.data[4])
                            voltage2 = int(voltage, 16)

                            # queries for retrievint all rows

                            update_retrive = "UPDATE `move_control` SET `battery` = " + \
                                str(voltage2) + \
                                ",  `error_can` = 'OK' WHERE `move_control`.`id` = 1;"
                            update_cursor.execute(update_retrive)
                            update_conn.commit()
                    error = 0

                except can.CanError:
                    print(can.CanError)
                    # queries for retrievint all rows
                    update_retrive = "UPDATE `move_control` SET `error_can` = 'OK' WHERE `move_control`.`id` = 1;"

                    # executing the quires
                    update_cursor.execute(update_retrive)
                    update_conn.commit()
                    error = 1 

if __name__ == '__main__':
    action()

