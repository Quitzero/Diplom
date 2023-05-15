from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.slider = QSlider(self)
        self.slider.setSingleStep(50)
        self.slider.valueChanged.connect(self.display_cloud)

    def display_cloud(self):
        print(self.slider.value())

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

