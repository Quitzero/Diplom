import os, sys
from windows.loginDialog import Ui_Dialog
from windows.mainWindow import Ui_MainWindow
from src import database, crud
from PyQt5 import QtWidgets, QtCore
from superqt import QDoubleRangeSlider

class LoginWindow(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("App | Авторизация")
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.authorized = False
        self.login_btn.clicked.connect(self.login)
        
        self.User.setText('root')
        self.Password.setText('89519821dD')

    #//////////////////////////////|Авторизация|//////////////////////////////
    def login(self):
        global engine
        Username = self.User.text()                         # Получение содержимого инпута User
        UserPassword = self.Password.text()                 # Получение содержимого инпута Password
        status, engine = database.connect_tp_db(Username, UserPassword)
        if status == False:      # Попытка авторизации
            pass
        else:
            self.parent().setDisabled(False)
            self.authorized = True                          # Отметить пользователя как авторизованного
            self.close()                                    # Если авторизация удачна, то закрыть модальное окно



    #//////////////////////////////|Обработка события (закрыть окно LoginWindow)|//////////////////////////////
    def closeEvent(self, event):
        if self.authorized == True:                                     # Проверка авторизации пользователя
            satellites =  crud.read_satellites(engine)
            for satellite in satellites:                                     # Перебор столбца Data_Collection в БД
                self.parent().satellite_comboBox.addItem(satellite[0])       # Добавление элемента в QComboBox
        else:
            self.parent().close()        # Если пользователь не авторизован, то закрыть так же родительское окно
            
        

class MainWindow(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("App")
        #//////////////////////////////|QDoubleRangeSlider|//////////////////////////////
        self.slider = QDoubleRangeSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue((0, 100))
        self.clouds_text.setText("Облачность: 0% - 100%")
        self.slider.valueChanged.connect(self.display_cloud)
        self.verticalLayout_4.addWidget(self.slider)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.setDisabled(True)

        print(self.slider.value())


        #//////////////////////////////|Отображение карты leaflet|//////////////////////////////
        self.current_dir = os.path.dirname(os.path.realpath(__file__))          # Получение расположения текущей папки
        self.filename = os.path.join(self.current_dir, "./map/index.html")      # Создания пути до html файла
        self.url = QtCore.QUrl.fromLocalFile(self.filename)                     # Преобразования файла в QUrl
        self.map.load(self.url)                                                 # Загрузка файла
        self.map.setContextMenuPolicy(QtCore.Qt.NoContextMenu)                  # Отключить контекстное меню

    def display_cloud(self):
        min, max = self.slider.value()
        self.clouds_text.setText(f"Облачность: {round(min)}% - {round(max)}%")

    #//////////////////////////////|Обработка события (закрыть окно MainWindow)|//////////////////////////////
    def closeEvent(self, event):
        try:
            pass
            #connectClose()          # Отключение от базы данные
        except NameError:
            pass

    #//////////////////////////////|Обработка события (открыто окно MainWindow)|//////////////////////////////
    def showEvent(self, event):
        self.window_log = LoginWindow(self)
        self.window_log.setWindowModality(QtCore.Qt.WindowModal)    # Задать окно LoginWindow как модальное
        self.window_log.show()                                      # Отобразить окно LoginWindow

    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())