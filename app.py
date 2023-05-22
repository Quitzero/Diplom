import os, sys
from widgets.loginDialog import Ui_Dialog
from widgets.mainWindow import Ui_MainWindow
from src import database, crud
from PyQt5 import QtGui, QtWidgets, QtWebChannel, QtCore
from superqt import QDoubleRangeSlider
from sympy import Point, Polygon 
from fractions import Fraction
import re


class Backend(QtCore.QObject):
    @QtCore.pyqtSlot(list)
    def getRef(self, x):
        global getCoord
        getCoord = x[0]
        MainWindow.AreaWithCoordinatesSetText(window, getCoord)
        

class LoginWindow(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags( QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        self.login_btn.clicked.connect(lambda: self.Authorization(self.User.text(), self.Password.text()))
        self.close_btn.clicked.connect(lambda: self.close())
        self.collapse_btn.clicked.connect(self.minimization)
        self.header_2.mouseMoveEvent = self.moveWindow
        self.header_1.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=25, xOffset=3, yOffset=3, color=QtGui.QColor(0, 0, 0, 100)))
        self.login_btn.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=25, xOffset=3, yOffset=3, color=QtGui.QColor(0, 0, 0, 100)))
        self.authorized = False
        self.User.setText('root')
        self.Password.setText('89519821dD')


    #//////////////////////////////|Авторизация|//////////////////////////////
    def Authorization(self, Username, UserPassword):
        global engine
        status, engine = database.connect_tp_db(Username, UserPassword)
        if status == False:                            # Попытка авторизации
            print("База данных не существует или неверно введено имя пользователя/пароль")
        else:
            self.authorized = True                          # Отметить пользователя как авторизованного
            print("Подключение успешно")
            self.parent().setDisabled(False)
            self.close()                                    # Если авторизация удачна, то закрыть окно

#region Настройка кнопок у header
    #//////////////////////////////|Перемещение окна|//////////////////////////////
    def moveWindow(self, event):
        if self.isMaximized() == False:
            self.move(self.pos() + event.globalPos() - self.clickPosition)
            self.clickPosition = event.globalPos()
            event.accept()
            pass

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()
        pass
    
    #//////////////////////////////|Свернуть окно|//////////////////////////////
    def minimization(self):
        self.showMinimized()
        self.parent().showMinimized()
        print('Окна свернуты!')
#endregion

    #//////////////////////////////|Обработка события (закрыть окно LoginWindow)|//////////////////////////////
    def closeEvent(self, event):
        print(f'Состояние пользователя: {self.authorized}')
        if self.authorized == True:                                     # Проверка авторизации пользователя
            satellites =  crud.read_satellites(engine)
            for satellite in satellites:                                     # Перебор столбца Data_Collection в БД
                self.parent().satellite_comboBox.addItem(satellite[0])       # Добавление элемента в QComboBox
        else:
            self.parent().close()        # Если пользователь не авторизован, то закрыть так же родительское окно
            print('Работа завершена! (Login Window)')
            
        

class MainWindow(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Диплом")
        self.setDisabled(True)
        self.is_first_show = True
        self.coords_textArea.setFontPointSize(8)
        #self.showMaximized()
        self.close_btn.clicked.connect(lambda: self.close())
        self.collapse_btn.clicked.connect(self.minimization)
        

        # Откючение стандартноо header
        #########################################################################################
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.title_bar.mouseMoveEvent = self.moveWindow

        # Добавление скейлинга размера окна
        #########################################################################################
        self.gripSize = 8
        self.grips = []
        for Grip in range(2):
            grip = QtWidgets.QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            self.grips.append(grip)
        self.grips[0].hide()

        #Отображение карты leaflet
        #########################################################################################
        self.current_dir = os.path.dirname(os.path.realpath(__file__))          # Получение расположения текущей папки
        self.filename = os.path.join(self.current_dir, "./map/index.html")      # Создания пути до html файла
        self.url = QtCore.QUrl.fromLocalFile(self.filename)                     # Преобразования файла в QUrl
        self.map.load(self.url)                                                 # Загрузка файла
        self.map.setContextMenuPolicy(QtCore.Qt.NoContextMenu)                  # Отключить контекстное меню

        #Добавление QDoubleRangeSlider
        #########################################################################################
        self.slider = QDoubleRangeSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue((0, 100))
        self.clouds_text.setText(r"Облачность: 0% - 100%")
        self.slider.valueChanged.connect(self.display_cloud)
        self.verticalLayout_3.addWidget(self.slider)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)

        #Backend
        #########################################################################################
        self.backend = Backend()
        self.channel = QtWebChannel.QWebChannel()
        self.map.page().setWebChannel(self.channel)
        self.channel.registerObject("backend", self.backend)

        #Подключение функций к кнопкам
        #########################################################################################
        self.Search_Btn.clicked.connect(self.search)
        #self.logout_btn.clicked.connect(self.openLoginWindow)
        self.Display_Btn.clicked.connect(lambda: self.DisplayAreaWithCoordinates(self.coords_textArea.toPlainText()))


#region Настройка кнопок у header
    #Перемещение окна
    #########################################################################################
    def moveWindow(self, event):
        if self.isMaximized() == False:
            self.move(self.pos() + event.globalPos() - self.clickPosition)
            self.clickPosition = event.globalPos()
            event.accept()
            pass

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()
        pass
    
    #Свернуть окно
    #########################################################################################
    def minimization(self):
        self.showMinimized()
        print('Окно свернуто! (Main Window)')
#endregion

    #Открытие окна авторизации
    #########################################################################################
    def openLoginWindow(self):
        crud.read_dd(engine)
        self.window_log = LoginWindow(self)
        self.window_log.setWindowModality(QtCore.Qt.WindowModal)    # Задать окно LoginWindow как модальное
        self.window_log.show()                                      # Отобразить окно LoginWindow


    #Добавление коорднат в coords_textArea
    #########################################################################################
    def AreaWithCoordinatesSetText(self, getCoord):
        global createdPolygon, peaks
        peaks = []
        vertex = 0
        while vertex < len(getCoord):
            res = Point(getCoord[vertex].get('lat'), getCoord[vertex].get('lng'))
            peaks.append(res)
            vertex+=1
                
        createdPolygon = Polygon(*tuple(peaks))

        area = ((Fraction(createdPolygon.area).numerator/Fraction(createdPolygon.area).denominator)*100000)
        self.Area_Square.setText(f'Выбранная область: {round(area, 3)} km^2')

        list = re.findall(r"[\d.]+", str(getCoord))
        len_list = len(list)
        my_list = []
        for j in range(len_list//2):
            i = j*2
            it =[item for item in list[i:i+2]]
            my_list.append(it)
        self.coords_textArea.setText(f'{my_list}')

    #Отображение на карте полигона с координатами полученными из coords_textArea
    #########################################################################################
    def DisplayAreaWithCoordinates(self, value):
        list = re.findall(r"[\d.]+", value)
        len_list = len(list)
        my_list = []
        for j in range(len_list//2):
            i = j*2
            it =[item for item in list[i:i+2]]
            my_list.append(it)
        self.map.page().runJavaScript(f"redraw({my_list})")

    #Отображение выбранноо значения облачности
    #########################################################################################
    def display_cloud(self):
        min, max = self.slider.value()
        self.clouds_text.setText(f"Облачность: {round(min)}% - {round(max)}%")

    #Изменение размера окна
    #########################################################################################
    def resizeEvent(self, event):
        QtWidgets.QMainWindow.resizeEvent(self, event)
        rect = self.rect()
        self.grips[1].move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)

    #Пермещение окна по экрану
    #########################################################################################
    def moveWindow(self, event):
        if self.isMaximized() == False:
            self.move(self.pos() + event.globalPos() - self.clickPosition)
            self.clickPosition = event.globalPos()
            event.accept()
            pass

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()
        pass
    

    #Обработка события (закрыть окно MainWindow)
    def closeEvent(self, event):
        print('Работа завершена! (Main Window)')
        try:
            pass
            #connectClose()          # Отключение от базы данные
        except NameError:
            pass

    #Обработка события (открыто окно MainWindow)
    #########################################################################################
    def showEvent(self, event):
        print('Открыто окно! (Main Window)')
        if self.is_first_show == True:
            self.window_log = LoginWindow(self)
            self.window_log.setWindowModality(QtCore.Qt.WindowModal)    # Задать окно LoginWindow как модальное
            self.window_log.show()                                      # Отобразить окно LoginWindow
            self.is_first_show = False
        else:
            pass
    
    #Поиск снимка
    #########################################################################################
    def search(self):
        index = 0
        self.map.page().runJavaScript(f"clear()")
        try:
            getCoord
        except NameError:
            print('Не выделена область поиска!')
        else:



            cloudiness_min , cloudiness_max = self.slider.value()
            dataset_satellite = self.satellite_comboBox.currentText()
            date_from = self.From_DateEdit.date().toPyDate()
            date_to = self.To_DateEdit.date().toPyDate()
            print('-'*5 + 'Параметры' + '-'*5)
            print(  f'Дата:\nОт: {date_from}\nДо: {date_to}')
            print(f'Спутник: {dataset_satellite}')
            print(f'Облачность: {round(cloudiness_min)}% - {round(cloudiness_max)}%')
            print('='*5 + 'Результат' + '='*5)

            if self.date_status_checkBox.isChecked():
                table_data =  crud.read_table(engine, dataset_satellite, cloudiness_min , cloudiness_max, None, None)
            else:
                table_data =  crud.read_table(engine, dataset_satellite, cloudiness_min , cloudiness_max, date_from, date_to)

            
            # ------------------------------------------------------------------------------------
            # ------------------------------------------------------------------------------------
            # ----------------------------------ПОФИКСИТЬ-----------------------------------------
            # ------------------------------------------------------------------------------------
            # ------------------------------------------------------------------------------------
            # ------------------------------------------------------------------------------------
            # ---------------Созданный квадрат не види что находится внутри!!!--------------------
            # ------------------------------------------------------------------------------------
            # ------------------------------------------------------------------------------------
            # ------------------------------------------------------------------------------------
            # ------------------------------------------------------------------------------------
            # ------------------------------------------------------------------------------------
            # ------------------------------------------------------------------------------------
            
            for data in table_data:
                a = [data.CORNER_UL_LAT_PRODUCT, data.CORNER_UL_LON_PRODUCT]
                b = [data.CORNER_LL_LAT_PRODUCT, data.CORNER_LL_LON_PRODUCT]
                c = [data.CORNER_LR_LAT_PRODUCT, data.CORNER_LR_LON_PRODUCT]
                d = [data.CORNER_UR_LAT_PRODUCT, data.CORNER_UR_LON_PRODUCT]
                
                db_poly1, db_poly2, db_poly3, db_poly4 = map(Point, 
                                                         [(data.CORNER_UL_LAT_PRODUCT, data.CORNER_UL_LON_PRODUCT),
                                                          (data.CORNER_LL_LAT_PRODUCT, data.CORNER_LL_LON_PRODUCT),
                                                          (data.CORNER_LR_LAT_PRODUCT, data.CORNER_LR_LON_PRODUCT),
                                                          (data.CORNER_UR_LAT_PRODUCT, data.CORNER_UR_LON_PRODUCT)])
                dbPoly = Polygon(db_poly1, db_poly2, db_poly3, db_poly4) 
            # ------------------------------------------------------------------------------------

                isIntersection = createdPolygon.intersection(dbPoly)
                isEnclosed = False
                for point in peaks:
                    if dbPoly.encloses_point(Point(point)) == True:
                        isEnclosed = True

                if isIntersection or isEnclosed:
                    print(index, data.Data_Collection, data.Time_Range)
                    self.map.page().runJavaScript(f"addPoly({a}, {b}, {c}, {d}, false)")
                    self.map.page().runJavaScript(f"renderPoly({index})")
                    index+=1
                else:
                    pass
 
        

    

if __name__ == "__main__":
    import widgets.resources.image.res_rc
    import widgets.resources.image.main_res_rc
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())