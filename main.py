from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout,\
     QLineEdit, QPushButton,QMainWindow, QTableWidget, QTableWidgetItem,\
     QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import mysql.connector
class DatabaseConnection:
    def __init__(self,host = "localhost",user="root",password = "itqan123",database = "students"):
        self.host = host 
        self.user = user
        self.password = password
        self.database = database   
    def connect(self):
        return mysql.connector.connect(host= self.host, user= self.user, 
                                       password = self.password, database = self.database)
        

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800,500)


        # Menu items
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Add student menu item
        add_student_action = QAction(QIcon("icons/add.png"),"Add Student",self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # About menu item under the help item
        about_action = QAction("About",self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        # search menu item
        search_action = QAction(QIcon("icons/search.png"),"Search",self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        # Table as the central widget
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id","Name","Course","Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)
        
        

        # Toolbar 
        toolbar = QToolBar()
        toolbar.setMovable(True)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)
        self.addToolBar(toolbar)

        #Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button =  QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button =  QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)
    

    def edit(self):
        dialog = EditDialog()
        dialog.exec()
    
    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()
        
    def load_table(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT* FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number,column_number,QTableWidgetItem(str(data)))

        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()
    def search(self):
        dialog = SearchDialog()
        dialog.exec()
    
    def about(self):
        dialog = AboutDialog()
        dialog.exec()
        

class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        #Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        #Add course name widget
        self.course_name = QComboBox()
        courses = ["Biology", "Astronomy", "Math", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        #Add phone number widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)
    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name,course,mobile) values (%s,%s,%s)",(name,course,mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_table()

class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()

        cursor.execute("SELECT * from students where name = %s",(name,))
        result = cursor.fetchall()
        rows = list(result)

        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)

        for item in items:
            main_window.table.item(item.row(),1).setSelected(True)
        
        cursor.close()
        connection.close()

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        #Get student name from selected row
        index = main_window.table.currentRow()
        student_name = main_window.table.item(index,1).text()
        self.student_id = main_window.table.item(index,0).text()
        #Add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        #Add course name widget
        
        course_name = main_window.table.item(index,2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Astronomy", "Math", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        #Add phone number widget
        mobile = main_window.table.item(index,3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)
    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students set name = %s , course = %s , mobile = %s where id = %s ",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))

        connection.commit()
        cursor.close()
        connection.close()
        #Refresh the table
        main_window.load_table()
class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")
        

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("yes")
        no = QPushButton("no")
        layout.addWidget(confirmation,0,0,1,2)
        layout.addWidget(yes, 1,0)
        layout.addWidget(no, 1,1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)
    
    def delete_student(self):
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index,0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students where id = %s",(student_id,)) 
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_table()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully")
        confirmation_widget.exec()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("About")
        content = """
        This app was created during the Python 20 Apps Megacourse. Feel free to
        reuse it.
        """
        self.setText(content)


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.load_table()
main_window.show()
sys.exit(app.exec())