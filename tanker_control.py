from __future__ import print_function
import serial
import requests
import time
import can  # add thư viện canbus
import pymysql  # database
import os
import RPi.GPIO as GPIO  # add library GPIO
from threading import Thread  # add library threading run multiple def

time.sleep(5) #delay đợi server online 5

c_arr = 0  # biến counter array
arr = [0.0, 0.0]  # array
error = 0
arr_permission = [0.0, 0.0]  # array


def dextohex(decimal):
    return hex(decimal)[2:]


def action():  # void main
    arr_permission_time = []                                                     
    # biến kết nối vào database cho việc update
    update_conn = pymysql.connect(
        host="localhost", user="root", passwd="raspberry", database="tanker") #localhost is 192.168.30.80
    # biết chạy kết nối vào database cho việc update
    update_cursor = update_conn.cursor()
    # queries for retrievint all rows
    # khai báo lệnh update data vào database
    update_retrive = "UPDATE `move_control` SET `level` = '0' WHERE `move_control`.`id` = 1;"

    # executing the quires
    update_cursor.execute(update_retrive)  # chạy lệnh update
    update_conn.commit()  # xác nhận update

    # khai báo database phpmyadmin
    con_permission = pymysql.connect(
        host="localhost", user="root", passwd="raspberry", database="tanker")
    cursor_permission = con_permission.cursor()

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
    time.sleep(0.5)     #time.sleep(1)
    GPIO.output(17, True)
    time.sleep(1)     #time.sleep(2)
    GPIO.output(17, False)
    time.sleep(1)     #time.sleep(2)

    while True:
        global c_arr  # lấy biến đếm array bên ngoài
        global arr  # lấy biến array từ biên ngoài
        global arr_permission  # lấy biến array từ biên ngoài
        global error  # lấy biến từ biên ngoài

        # khai báo phương thức và tên của giao thức can bus trong Raspberry
        bus = can.interface.Bus(channel='can0', bustype='socketcan_native')

        # khai báo các id cần gửi của canbus
        id_canbus = [101, 201, 301, 401, 501]
        # Khai báo các dư liệu cần gửi qua cacbus
        data = [(00, 00, 00, 00,  6, 00,  2, 00), (00, 00, 00, 00,  1, 00,  2, 00),  # go up and down
                (00, 00, 00, 00,  8, 00,  2, 00), (00, 00, 00, 00,  7, 00,  2, 00),  # turn left and right
                (00, 00, 00, 00,  9, 00,  2, 00), (00, 00, 00, 00,  4, 00,  2, 00),  # around left and right
                (00, 00, 00, 00, 00, 00, 00, 00),  # stop
                (00, 00, 00, 00,  1,  1, 00, 00), (00, 00, 00, 00,  6,  1, 00, 00),  # screw go up and down
                (00, 00, 00, 00,  10,  00, 2, 00)] # run fast
                
     # -------------------------------------------đọc dữ liệu từ database--------------------------------------------
        # khai báo database phpmyadmin
        connection = pymysql.connect(
            host="localhost", user="root", passwd="raspberry", database="tanker")
        cursor = connection.cursor()
        # queries for retrievint all rows
        retrive = "Select * from move_control;"

        # executing the quires
        cursor.execute(retrive)
        rows = cursor.fetchall()

        # lấy giá trị time từ database add vào giá trị mảng thứ 1
        arr[c_arr] = int(rows[0][2])
        # print(arr[c_arr])

        c_arr += 1  # điếm mảng tăng 1
        # hiệu của giá trị thứ 2 và giá trị thứ 1 nhất trong mảng
        check_connection = abs(arr[1] - arr[0])
        # check_connection = rows[0][1] - rows[0][0]
        # print(check_connection)
        
     # ---------------------------------------------sét giá trị từ database chuẩn bị để gửi cho canbus-------------------------------
        if check_connection >= 1:  # nếu hiệu của giá trị mảng thứ 2 và giá trị thứ 1 >= 1 thì :
        # if check_connection != 0:
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
     # ------------------------------------bắt đầu gửi giá trị đến canbus----------------------------------
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
                time.sleep(0.2)  # delay time.sleep(0.2)
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

     # reset biến đếm mảng
        if c_arr >= 2:
            c_arr = 0

        # permission

        # queries for retrievint all rows
        retrive_permission = "SELECT * FROM `home_users` WHERE `status_user` = 1;"

        # executing the quires
        cursor_permission.execute(retrive_permission)
        home_users = cursor_permission.fetchall()

        for i in range(len(home_users)):
            arr_permission_time.insert(i, home_users[i][5])  # add giá trị

        # print(arr_permission_time)
        # print(home_users[1][4])

        if len(arr_permission_time) >= len(home_users) * 2:
            for i in range(len(home_users)):
                detal = int(
                    arr_permission_time[i]) - int(arr_permission_time[i + len(home_users)])
                print("data", i, "=", detal)
                if detal == 0 and error == 0: # detal = 0 khi không có sự hiện diện của khách hàng 
                    if home_users[i][4] == '1' :
                        # queries for retrievint all rows
                        update_retrive = "UPDATE `home_users` SET `status_control` = '0', `permission_level` = '0' WHERE `home_users`.`id` = " + \
                            str(home_users[i][0]) + ";"

                        # executing the quires
                        update_cursor.execute(update_retrive)
                        update_conn.commit()
                        print("tài khoản này là admin")
                    else:
                        update_retrive = "UPDATE `home_users` SET `status_control` = '0' WHERE `home_users`.`id` = " + \
                            str(home_users[i][0]) + ";"

                        update_cursor.execute(update_retrive)
                        update_conn.commit()
                        print("tài khoản này ko phải admin")
                else: # detal != 0 khi có sự hiện diện của khách hàng
                    
                    update_retrive = "UPDATE `home_users` SET `status_control` = '1' WHERE `home_users`.`id` = " + \
                        str(home_users[i][0]) + ";"

                    update_cursor.execute(update_retrive)
                    update_conn.commit()
                    print("khách hàng " +str(i)+ " đang dùng")

            del arr_permission_time[:] # xóa hết các giá trị có trong mảng arr_permisstion_time


if __name__ == '__main__':
    action()

