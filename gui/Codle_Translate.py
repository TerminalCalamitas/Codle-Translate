# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Codle Translate.ui'
##
## Created by: Qt User Interface Compiler version 5.15.18
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(649, 514)
        font = QFont()
        font.setFamily(u"Sans Serif")
        font.setPointSize(12)
        MainWindow.setFont(font)
        self.GridLayout = QWidget(MainWindow)
        self.GridLayout.setObjectName(u"GridLayout")
        self.GridLayout.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.gridLayout = QGridLayout(self.GridLayout)
        self.gridLayout.setObjectName(u"gridLayout")
        self.InputLanguage = QComboBox(self.GridLayout)
        self.InputLanguage.addItem("")
        self.InputLanguage.addItem("")
        self.InputLanguage.addItem("")
        self.InputLanguage.addItem("")
        self.InputLanguage.setObjectName(u"InputLanguage")

        self.gridLayout.addWidget(self.InputLanguage, 0, 0, 1, 1)

        self.AboveButtonSpacing = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.AboveButtonSpacing, 1, 1, 1, 1)

        self.InputBox = QTextEdit(self.GridLayout)
        self.InputBox.setObjectName(u"InputBox")
        self.InputBox.viewport().setProperty("cursor", QCursor(Qt.IBeamCursor))
        self.InputBox.setAutoFillBackground(True)
        self.InputBox.setTabStopDistance(16.000000000000000)

        self.gridLayout.addWidget(self.InputBox, 1, 0, 3, 1)

        self.OutputLanguage = QComboBox(self.GridLayout)
        self.OutputLanguage.addItem("")
        self.OutputLanguage.addItem("")
        self.OutputLanguage.addItem("")
        self.OutputLanguage.addItem("")
        self.OutputLanguage.setObjectName(u"OutputLanguage")

        self.gridLayout.addWidget(self.OutputLanguage, 0, 2, 1, 1)

        self.RunTranslation = QPushButton(self.GridLayout)
        self.RunTranslation.setObjectName(u"RunTranslation")
        self.RunTranslation.setMaximumSize(QSize(149, 16777215))
        self.RunTranslation.setCheckable(False)

        self.gridLayout.addWidget(self.RunTranslation, 2, 1, 1, 1)

        self.OutputBox = QTextEdit(self.GridLayout)
        self.OutputBox.setObjectName(u"OutputBox")
        self.OutputBox.setEnabled(True)
        self.OutputBox.setAutoFillBackground(True)
        self.OutputBox.setReadOnly(True)

        self.gridLayout.addWidget(self.OutputBox, 1, 2, 3, 1)

        self.Belowbuttonspacing = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.Belowbuttonspacing, 3, 1, 1, 1)

        self.LoadExample = QPushButton(self.GridLayout)
        self.LoadExample.setObjectName(u"LoadExample")

        self.gridLayout.addWidget(self.LoadExample, 4, 0, 1, 1)

        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(2, 1)
        MainWindow.setCentralWidget(self.GridLayout)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 649, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QWidget.setTabOrder(self.InputLanguage, self.OutputLanguage)
        QWidget.setTabOrder(self.OutputLanguage, self.InputBox)
        QWidget.setTabOrder(self.InputBox, self.RunTranslation)
        QWidget.setTabOrder(self.RunTranslation, self.OutputBox)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Codle Translate", None))
        self.InputLanguage.setItemText(0, QCoreApplication.translate("MainWindow", u"Javascript", None))
        self.InputLanguage.setItemText(1, QCoreApplication.translate("MainWindow", u"Python", None))
        self.InputLanguage.setItemText(2, QCoreApplication.translate("MainWindow", u"Java", None))
        self.InputLanguage.setItemText(3, QCoreApplication.translate("MainWindow", u"C", None))

        self.InputBox.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Code to Translate", None))
        self.OutputLanguage.setItemText(0, QCoreApplication.translate("MainWindow", u"Javascript", None))
        self.OutputLanguage.setItemText(1, QCoreApplication.translate("MainWindow", u"Python", None))
        self.OutputLanguage.setItemText(2, QCoreApplication.translate("MainWindow", u"Java", None))
        self.OutputLanguage.setItemText(3, QCoreApplication.translate("MainWindow", u"C", None))

        self.RunTranslation.setText(QCoreApplication.translate("MainWindow", u"  Translate Input  ", None))
        self.OutputBox.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Translated Code", None))
        self.LoadExample.setText(QCoreApplication.translate("MainWindow", u"Load Example Code", None))
    # retranslateUi

