# -*- coding: utf-8 -*-
"""
File logic / thuật toán điều khiển robot.
Toàn bộ phần giao diện (widget, layout, font, style...) nằm ở file test_ui_8.py
(được sinh ra giống như từ Qt Designer / pyuic5).

File này chỉ chứa:
- Kết nối serial, camera, YOLO
- Động học thuận / nghịch (forward_kinematics / inverse_kinematics)
- Xử lý sự kiện, luồng (thread) đọc serial và camera
- Toàn bộ logic nghiệp vụ của chương trình
"""

import sys
import time

import cv2
import serial

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime

from kinematics import forward_kinematics, inverse_kinematics
from image_yolo import detect_colors

from test_ui_8 import Ui_MainWindow


# ==================== CẤU HÌNH / BIẾN TOÀN CỤC ====================
ser = serial.Serial('COM7', 115200)  # Đổi cổng COM theo Device Manager, baudrate = 115200 cho UI và Arduino

cam_index = 0

numb_red = 0
numb_yellow = 0
numb_blue = 0

mode = 0
t1_manual = 0
t2_manual = 0
t3_manual = 0
tb_manual = 0
the1 = 0
the2 = 0
the3 = 0
base = 0

pos_R = f"X92Y-22Z-30A0;X92Y-47Z-55A0M0;X92Y-2Z-30A0;X0Y-2Z-30A0;X0Y-32Z-66A0;X0Y-60Z-60A0;X0Y-77Z-70A0M1;X0Y-60Z-60A0\n"
pos_B = f"X92Y-22Z-30A0;X92Y-47Z-55A0M0;X92Y-2Z-30A0;X0Y-2Z-30A0;X0Y-32Z-66A140;X0Y-60Z-60A140;X0Y-77Z-70A140M1;X0Y-60Z-60A120\n"
pos_Y = f"X92Y-22Z-30A0;X92Y-47Z-55A0M0;X92Y-2Z-30A0;X0Y-2Z-30A0;X0Y-32Z-66A280;X0Y-60Z-60A280;X0Y-77Z-70A280M1;X0Y-60Z-60A280\n"


# ==================== THREAD CAMERA / YOLO ====================
class camera_ui(QThread, object):
    imageUpdate = pyqtSignal(QImage)
    redRise = pyqtSignal()     # phát 1 lần khi numb_red: 0 -> 1
    yellowRise = pyqtSignal()
    blueRise = pyqtSignal()
    noneSeen = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.threadActive = False
        self.cap = None

    def run(self):
        global numb_red, numb_blue, numb_yellow, cam_index
        self.threadActive = True
        self.cap = cv2.VideoCapture(cam_index)

        while self.threadActive:
            ret, frame = self.cap.read()
            if not ret:
                continue

            annotated, numb_red, numb_blue, numb_yellow = detect_colors(frame)
            # ===== BGR -> RGB =====
            rgb_image = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(
                rgb_image.data,
                w,
                h,
                bytes_per_line,
                QImage.Format_RGB888
            ).copy()   # tránh lỗi bộ nhớ

            self.imageUpdate.emit(qt_image)

            # ===== Rising edge =====
            if numb_red == 1:
                self.redRise.emit()
            if numb_yellow == 1:
                self.yellowRise.emit()
            if numb_blue == 1:
                self.blueRise.emit()
            if numb_red == 0 and numb_blue == 0 and numb_yellow == 0:
                self.noneSeen.emit()

    def stop(self):
        self.threadActive = False
        self.wait()


# ==================== THREAD ĐỌC SERIAL ====================
class SerialReader(QThread):
    """Thread chỉ đọc serial - nhận serial_port từ UI"""
    signal_received = pyqtSignal(str)  # Signal gửi tín hiệu nhận được

    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = ser  # Nhận serial port từ UI
        self.running = False

    def run(self):
        """Đọc serial và gửi signal"""
        self.running = True
        try:
            while self.running:
                if self.serial_port and self.serial_port.is_open:
                    if self.serial_port.in_waiting > 0:
                        data = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                        if data:
                            self.signal_received.emit(data)
        except Exception:
            pass

    def stop(self):
        """Dừng thread"""
        self.running = False
        self.wait()


# ==================== CỬA SỔ CHÍNH: GIAO DIỆN + LOGIC ====================
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)   # dựng giao diện từ file test_ui_8.py

        self.FK = forward_kinematics
        self.IK = inverse_kinematics

        # ---- Thread đọc serial ----
        self.reader = SerialReader(ser)
        self.reader.signal_received.connect(self.update_label)
        self.reader.start()

        # TOGGLE PAGES
        # page main
        self.main.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_main))
        # page control
        self.control.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_control))
        # page camera
        self.camera.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_camera))
        # page slot
        self.slot.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_slot))

        # button
        self.bt_exit.clicked.connect(lambda: self.exit_page())
        self.bt_cal_FK.clicked.connect(lambda: self.on_calc_fk_clicked())
        self.bt_cal_IK.clicked.connect(lambda: self.on_cal_ik_clicked())
        self.bt_setHome.clicked.connect(lambda: self.set_home())
        self.bt_conv_start.clicked.connect(lambda: self.conveyor_on())
        self.bt_conv_stop.clicked.connect(lambda: self.conveyor_off())
        self.bt_mag_attract.clicked.connect(lambda: self.namcham_on())
        self.bt_mag_release.clicked.connect(lambda: self.namcham_off())
        self.bt_go_IK.clicked.connect(lambda: self.go_IK())
        self.bt_manual.clicked.connect(lambda: self.manual_mode())
        self.bt_auto.clicked.connect(lambda: self.auto_mode())
        self.bt_R1.clicked.connect(lambda: self.set_slot_R1())
        self.bt_B1.clicked.connect(lambda: self.set_slot_R2())
        self.bt_Y1.clicked.connect(lambda: self.set_slot_Y3())
        self.bt_reset_slot.clicked.connect(lambda: self.return_style())

        # slider
        self.theta1_slid.setRange(-90, 180)         # min/max
        self.theta1_slid.setValue(0)                 # giá trị khởi tạo
        self.theta1_slid.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.theta1_slid.setTickInterval(27)

        self.theta2_slid.setRange(-100, 50)          # min/max
        self.theta2_slid.setValue(0)                 # giá trị khởi tạo
        self.theta2_slid.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.theta2_slid.setTickInterval(15)

        self.theta3_slid.setRange(-120, 20)          # min/max
        self.theta3_slid.setValue(0)                 # giá trị khởi tạo
        self.theta3_slid.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.theta3_slid.setTickInterval(10)

        self.base_slid.setRange(0, 15)               # min/max
        self.base_slid.setValue(0)                   # giá trị khởi tạo
        self.base_slid.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.base_slid.setTickInterval(1)

        # lấy data tức thời
        # theta1
        current1 = self.theta1_slid.value()
        if self.sl_theta1_dis:
            self.sl_theta1_dis.setText(str(current1))
        self.theta1_slid.valueChanged.connect(self.on_slider_changedX)
        # theta2
        current2 = self.theta2_slid.value()
        if self.sl_theta2_dis:
            self.sl_theta2_dis.setText(str(current2))
        self.theta2_slid.valueChanged.connect(self.on_slider_changedY)
        # theta3
        current3 = self.theta3_slid.value()
        if self.sl_theta3_dis:
            self.sl_theta3_dis.setText(str(current3))
        self.theta3_slid.valueChanged.connect(self.on_slider_changedZ)
        # base
        current4 = self.base_slid.value()
        if self.base_sl_dis:
            self.base_sl_dis.setText(str(current4))
        self.base_slid.valueChanged.connect(self.on_slider_changedA)

        # camera monitor
        self.camera_ui = camera_ui()
        self.bt_cn_cam.clicked.connect(lambda: self.startcam())
        self.camera_ui.imageUpdate.connect(self.imageupdateSlot)
        self.num_green.setText(str(numb_yellow))
        self.bt_dcn_cam.clicked.connect(lambda: self.stopcam())
        self.camera_ui.redRise.connect(self.on_red_once)
        self.camera_ui.blueRise.connect(self.on_blue_once)
        self.camera_ui.yellowRise.connect(self.on_yellow_once)
        self.camera_ui.noneSeen.connect(self.return_trig)

        self.detected = False
        self.done_motion = True
        self.bool_color = False
        self.curren_color = None
        self.count_red = 0
        self.count_blue = 0
        self.count_yellow = 0
        self.bool_R = True
        self.bool_B = True
        self.bool_Y = True

    # ==================== CAMERA ====================
    def imageupdateSlot(self, image):
        self.camera_dis.setPixmap(QPixmap.fromImage(image))

    def startcam(self):
        global cam_index
        cam_index = self.cb_sl_cam.currentIndex()
        self.camera_ui.start()
        self.write_his("Camera connect")

    def stopcam(self):
        self.camera_ui.stop()
        self.write_his("Camera disconnect")

    def on_red_once(self):
        self.change_trig_red()
        self.curren_color = "R"
        print(self.curren_color)
        self.num_red.setText(str(self.count_red))
        if self.detected:
            self.count_red += 1
            print(self.detected)
            self.set_slot_R1()
            print("co goiR1")

    def on_blue_once(self):
        self.change_trig_blue()
        self.curren_color = "B"
        self.num_blue.setText(str(self.count_blue))
        if self.detected:
            self.count_blue += 1
            print(self.curren_color)
            self.process_auto()

    def on_yellow_once(self):
        self.change_trig_yellow()
        self.curren_color = "Y"
        self.num_green.setText(str(self.count_yellow))
        if self.detected:
            self.count_yellow += 1
            print(self.curren_color)
            self.process_auto()

    def process_auto(self):
        # Lấy nhóm task theo màu hiện tại
        if self.curren_color == "R":
            if self.bool_R and self.done_motion:
                self.set_slot_R1()
                print("co goiR1")
                self.curren_color = None
        # auto for blue
        elif self.curren_color == "B":
            if self.bool_B and self.done_motion:
                self.set_slot_R2()
                print("co goiBBB")
                self.curren_color = None
        # auto for yellow
        elif self.curren_color == "Y":
            if self.bool_Y and self.done_motion:
                self.set_slot_Y3()
                print("co goiyyyyy")
                self.curren_color = None

    # ==================== SERIAL ====================
    def update_label(self, data):
        if data == "D" and self.curren_color is not None:
            print("detect")
            self.detected = True  # dữ liệu báo phát hiện
        elif data == "D":
            self.detected = False

        if data == "R":
            print("move done")
            self.done_motion = True
            self.bool_R = True
            self.bool_B = True
            self.bool_Y = True

    def exit_page(self):
        mang1 = f'C{1}\n'
        print(mang1)
        ser.write(mang1.encode())
        time.sleep(1)
        sys.exit()

    # ==================== SLIDER MANUAL ====================
    def on_slider_changedX(self, val: int):
        global t1_manual
        if self.sl_theta1_dis:
            self.sl_theta1_dis.setText(str(val))
            if mode == 1:
                t1_manual = val
                mang = f'X{t1_manual}Y{t2_manual}Z{t3_manual}A{tb_manual * 20}\n'
                print(mang)
                ser.write(mang.encode())
                time.sleep(0.1)

    def on_slider_changedY(self, val: int):
        global t2_manual
        if self.sl_theta2_dis:
            self.sl_theta2_dis.setText(str(val))
            if mode == 1:
                t2_manual = val
                mang = f'X{t1_manual}Y{t2_manual}Z{t3_manual}A{tb_manual * 20}\n'
                print(mang)
                ser.write(mang.encode())
                time.sleep(0.1)

    def on_slider_changedZ(self, val: int):
        global t3_manual
        if self.sl_theta3_dis:
            self.sl_theta3_dis.setText(str(val))
            if mode == 1:
                t3_manual = val
                mang = f'X{t1_manual}Y{t2_manual}Z{t3_manual}A{tb_manual * 20}\n'
                print(mang)
                ser.write(mang.encode())
                time.sleep(0.1)

    def on_slider_changedA(self, val: int):
        global tb_manual
        if self.base_sl_dis:
            self.base_sl_dis.setText(str(val))
            if mode == 1:
                tb_manual = val
                mang = f'X{t1_manual}Y{t2_manual}Z{t3_manual}A{tb_manual * 20}\n'
                print(mang)
                ser.write(mang.encode())
                time.sleep(0.1)

    # ==================== ĐỘNG HỌC ====================
    def on_calc_fk_clicked(self):
        self.fk = forward_kinematics
        t1 = self.theta1_slid.value()
        t2 = self.theta2_slid.value()
        t3 = self.theta3_slid.value()
        t_base = self.base_slid.value()
        x, y, z = self.fk(t1, -t2, -t3, t_base)   # deg=True vì spin nhập độ
        if self.px_dis:
            self.px_dis.setText(f"{x:.2f}")
        if self.py_dis:
            self.py_dis.setText(f"{y:.2f}")
        if self.pz_dis_2:
            self.pz_dis_2.setText(f"{z:.2f}")
        if self.base_slid:
            self.pa_dis.setText(f"{t_base:.2f}")

    def on_cal_ik_clicked(self):
        global the1, the2, the3, base
        self.IK = inverse_kinematics
        px = float(self.Px_inv.text())
        py = float(self.Py_inv.text())
        pz = float(self.Pz_inv.text())
        base_sld = self.base_slid.value()
        the1, the2, the3, base = self.IK(px, py, pz, base_sld)
        if self.Px_inv:
            self.theta1_dis.setText(f"{the1:.2f}")
        if self.Py_inv:
            self.theta2_dis.setText(f"{-the2:.2f}")
        if self.Pz_inv:
            self.theta3_dis.setText(f"{-the3:.2f}")
            self.base_dis.setText(f"{base:.2f}")

    # ==================== LỊCH SỬ ====================
    def write_his(self, text):
        self.text_history.setReadOnly(True)
        self.text_history.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                font-family: Consolas, monospace;
                font-size: 14px;
            }
        """)
        current = QDateTime.currentDateTime()
        formated_time = current.toString("dd/MM/yyyy HH:mm:ss")
        self.text_history.insertPlainText(f"[{formated_time}] {str(text)}\n")

    # ==================== ĐÈN BÁO MÀU ====================
    def change_trig_red(self):
        self.trig_red.setPixmap(QtGui.QPixmap("red_rec.png"))
        self.trig_green.setScaledContents(True)

    def change_trig_blue(self):
        self.trig_blue.setPixmap(QtGui.QPixmap("blue_rec.png"))
        self.trig_green.setScaledContents(True)

    def change_trig_yellow(self):
        self.trig_green.setPixmap(QtGui.QPixmap("yellow_rec.png"))
        self.trig_green.setScaledContents(True)

    def return_trig(self):
        self.trig_red.setPixmap(QtGui.QPixmap("gray_rec.png"))
        self.trig_blue.setPixmap(QtGui.QPixmap("gray_rec.png"))
        self.trig_green.setPixmap(QtGui.QPixmap("gray_rec.png"))

    # ==================== CHẾ ĐỘ VẬN HÀNH ====================
    def manual_mode(self):
        global mode
        mode = 1
        self.bt_manual.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.bt_auto.setStyleSheet("")
        self.write_his("Manual mode")

    def auto_mode(self):
        global mode
        mode = 0
        mang = f"C{0}\n"
        print(mang)
        ser.write(mang.encode())
        time.sleep(0.01)
        self.write_his("Conveyor run")
        self.bt_auto.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.bt_manual.setStyleSheet("")
        self.write_his("Auto mode")

    def set_home(self):
        self.theta1_slid.setValue(0)
        self.theta2_slid.setValue(0)
        self.theta3_slid.setValue(0)
        self.base_slid.setValue(0)
        self.write_his("Set home")
        mang = f"H\n"
        print(mang)
        ser.write(mang.encode())
        time.sleep(0.01)

    # ==================== NAM CHÂM / BĂNG TẢI ====================
    def namcham_on(self):
        global mode
        if mode == 1:
            mang = f"M{0}\n"
            print(mang)
            ser.write(mang.encode())
            time.sleep(0.01)
            self.write_his("Electromagnet ON")

    def namcham_off(self):
        global mode
        if mode == 1:
            mang = f"M{1}\n"
            print(mang)
            ser.write(mang.encode())
            time.sleep(0.01)
            self.write_his("Electromagnet OFF")

    def conveyor_on(self):
        global mode
        if mode == 1:
            mang = f"C{0}\n"
            print(mang)
            ser.write(mang.encode())
            time.sleep(0.01)
            self.write_his("Conveyor run")

    def conveyor_off(self):
        global mode
        if mode == 1:
            mang = f"C{1}\n"
            print(mang)
            ser.write(mang.encode())
            time.sleep(0.01)
            self.write_his("Conveyor stop")

    def go_IK(self):
        global the1, the2, the3, base
        if mode == 1:
            if base != 0:
                mang = f'X{0}Y{0}Z{0}A{base * 20}\n'
                print(mang)
                ser.write(mang.encode())
                time.sleep(0.1)
                mang = f'X{the1}Y{-the2}Z{-the3}A{base * 20}\n'
                print(mang)
                ser.write(mang.encode())
                time.sleep(0.1)
            else:
                mang = f'X{the1}Y{-the2}Z{-the3}A{base * 20}\n'
                print(mang)
                ser.write(mang.encode())
                time.sleep(0.1)

    # ==================== SLOT PHÂN LOẠI ====================
    def set_slot_R1(self):
        global pos_R
        if self.detected:
            mang = pos_R
            print(mang)
            ser.write(mang.encode())
            time.sleep(0.01)
            self.bt_R1.setStyleSheet("""
                QPushButton {
                    background-color: #FF0000;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 14px;
                }
            """)
            self.detected = False
            self.bool_R = False
            self.done_motion = False
            self.write_his("Set at slot R")

    def set_slot_R2(self):
        global pos_B
        if self.detected:
            mang = pos_B
            print(mang)
            ser.write(mang.encode())
            time.sleep(0.01)
            self.bt_B1.setStyleSheet("""
                QPushButton {
                    background-color: #0000FF;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 14px;
                }
            """)
            self.detected = False
            self.done_motion = False
            self.write_his("Set at slot B")

    def set_slot_Y3(self):
        global pos_Y
        if self.detected:
            mang = pos_Y
            print(mang)
            ser.write(mang.encode())
            time.sleep(0.01)
            self.bt_Y1.setStyleSheet("""
                QPushButton {
                    background-color: #FFEB3B;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 14px;
                }
            """)
            self.detected = False
            self.bool_Y = False
            self.done_motion = False
            self.write_his("Set at slot Y")

    def return_style(self):
        self.bt_R1.setStyleSheet("")
        self.bt_B1.setStyleSheet("")
        self.bt_Y1.setStyleSheet("")
        self.write_his("Reset all slot")

    def done(self):
        if self.done_motion:
            print("doneeee")


# ==================== CHẠY CHƯƠNG TRÌNH ====================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())