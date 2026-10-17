from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QPushButton, QMainWindow, QWidget

app = QApplication([])
window = QMainWindow()


label = QLabel(parent=window,text= 'Hello World')
label.move(50,0)
button = QPushButton(parent=window, text='click')
button.move(50,50)
window.show()
app.exec_()