import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OrdinalEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QBrush, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os

# Get the directory where the executable is located
base_path = os.path.dirname(os.path.abspath(__file__))

# Use relative paths for your files
model_path = os.path.join(base_path, 'random_forest_model.pkl')
csv_path_train = os.path.join(base_path, 'train.csv')
csv_path_scale = os.path.join(base_path, 'data_for_scaler.csv')
background_image_path = os.path.join(base_path, 'diamond_background.jpg')
window_icon_path = os.path.join(base_path, 'window_icon.png')
result_window_icon_path = os.path.join(base_path, 'result_window_icon.png')

# Global variables for model, scaler, and encoder
model = None
scaler = None
category_encoder = None
train_set = None

class LoaderThread(QThread):
    finished = pyqtSignal()

    def run(self):
        global model, scaler, category_encoder, train_set
        model = joblib.load(model_path)
        scaler = self.get_scaler()
        category_encoder = self.get_encoder()
        train_set = pd.read_csv(csv_path_train)
        self.finished.emit()

    def get_scaler(self):
        data_for_scaler = pd.read_csv(csv_path_scale)
        scaler = StandardScaler()
        scaler.fit(data_for_scaler)
        return scaler

    def get_encoder(self):
        cut_category_encoding = [['Fair','Good','Very Good','Premium','Ideal']]
        color_category_encoding = [['J','I','H','G','F','E','D']]
        clarity_category_encoding = [['I1','SI2','SI1','VS2','VS1','VVS2','VVS1','IF']]

        cut_pipeling = Pipeline([('cut_encoder',OrdinalEncoder(categories=cut_category_encoding))])
        color_pipeling = Pipeline([('color_encoder',OrdinalEncoder(categories=color_category_encoding))])
        clarity_pipeling = Pipeline([('clarity_encoder',OrdinalEncoder(categories=clarity_category_encoding))])

        categories_encoding = ColumnTransformer([
            ('cut_pip',cut_pipeling, ['cut']),
            ('color_pip',color_pipeling, ['color']),
            ('clarity_pip',clarity_pipeling, ['clarity'])
        ])
        train_set = pd.read_csv(csv_path_train)
        categories_encoding.fit(train_set)
        return categories_encoding


def reassign_outliers_iqr(df, data, columns):

    for column in columns:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - (1.5 * IQR)
        upper_bound = Q3 + (1.5 * IQR)
        data.loc[((data[column] > upper_bound), column)] = upper_bound
        data.loc[((data[column] < lower_bound), column)] = lower_bound
    return data


# ... (rest of the code remains the same)

class DiamondPriceGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.result_window = None
        self.label_color = QColor(255, 255, 255)
        self.initUI()
        self.load_data()

    def load_data(self):
        self.loader_thread = LoaderThread()
        self.loader_thread.finished.connect(self.on_load_finished)
        self.loader_thread.start()

    def on_load_finished(self):
        print("\nModel and data loading completed\n")

    # ... (rest of the methods remain the same)

    
    def initUI(self):
        self.setWindowTitle('Diamond Price Predictor')
        self.setGeometry(100, 100, 400, 500)
        
        # Set the window icon
        self.setWindowIcon(QIcon(window_icon_path))  # You can use .png here
        self.setStyleSheet("""
            QLineEdit {
                border-radius: 6px;
                padding: 1px;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton {
                background-color: rgb(255, 255, 255);
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
                min-height: 30px;
            }
        """)
        # Set background image
        background = QPixmap(background_image_path)  # Replace with your image path
        if not background.isNull():
            scaled_background = background.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            palette = self.palette()
            palette.setBrush(QPalette.Window, QBrush(scaled_background))
            self.setPalette(palette)
            self.setAutoFillBackground(True)
        else:
            print("Failed to load background image. Using default background.")

        layout = QVBoxLayout()
        
        # Create input fields
        self.carat = self.create_input("Carat (number):")
        self.cut = self.create_combo("Cut:", ["Fair", "Good", "Very Good", "Premium", "Ideal"])
        self.color = self.create_combo("Color:", ["D", "E", "F", "G", "H", "I", "J"])
        self.clarity = self.create_combo("Clarity:", ["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"])
        self.depth = self.create_input("Depth (number):")
        self.table = self.create_input("Table (number):")
        self.x = self.create_input("X (number):")
        self.y = self.create_input("Y (number):")
        self.z = self.create_input("Z (number):")
        
        # Add input fields to layout
        for field in [self.carat, self.cut, self.color, self.clarity, self.depth, self.table, self.x, self.y, self.z]:
            layout.addLayout(field)
        
        # Create and add predict button
        predict_btn = QPushButton('Predict Price')
        predict_btn.clicked.connect(self.predict_price)
        
        # # Create a QFont object
        # button_font = QFont()
        # button_font.setBold(True)
        # button_font.setPointSize(15)
        
        # # Set the font for the button
        # predict_btn.setFont(button_font)
        # predict_btn.setFixedSize(200, 40)  
        layout.addWidget(predict_btn)
        
        self.setLayout(layout)
    
    def create_input(self, label):
        layout = QHBoxLayout()
        label_widget = QLabel(label)
        label_widget.setFont(QFont('Arial', 15, QFont.Bold))
        label_widget.setStyleSheet(f"color: {self.label_color.name()};")
        layout.addWidget(label_widget)
        line_edit = QLineEdit()
        layout.addWidget(line_edit)
        return layout
    
    def create_combo(self, label, options):
        layout = QHBoxLayout()
        label_widget = QLabel(label)
        label_widget.setFont(QFont('Arial', 15, QFont.Bold))
        label_widget.setStyleSheet(f"color: {self.label_color.name()}")
        layout.addWidget(label_widget)
        combo = QComboBox()
        combo.addItems(options)
        layout.addWidget(combo)
        return layout
    
    def predict_price(self):
        try:
            carat = float(self.carat.itemAt(1).widget().text())
            cut = self.cut.itemAt(1).widget().currentText()
            color = self.color.itemAt(1).widget().currentText()
            clarity = self.clarity.itemAt(1).widget().currentText()
            depth = float(self.depth.itemAt(1).widget().text())
            table = float(self.table.itemAt(1).widget().text())
            x = float(self.x.itemAt(1).widget().text())
            y = float(self.y.itemAt(1).widget().text())
            z = float(self.z.itemAt(1).widget().text())
            
            price = predict_price(scaler, category_encoder, model, train_set, carat, cut, color, clarity, depth, table, x, y, z)
            
            self.show_result(price)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please ensure all numeric inputs are valid numbers.")
    
    def show_result(self, price):
        if self.result_window is None:
            self.result_window = ResultWindow(price)
        else:
            self.result_window.close()
            self.result_window = ResultWindow(price)
        self.result_window.show()

# Placeholder for the AI model
def predict_price(scaler, categories_encoding, model, train_set, carat, cut, color, clarity, depth, table, x, y, z):
    # Form dictionary
    input_data = {
        'carat': [carat],
        'cut': [cut],
        'color': [color],
        'clarity':[clarity],
        'depth':[depth],
        'table':[table],
        'x':[x],
        'y':[y],
        'z':[z]
    }
    
    # Form a dataframe 
    data = pd.DataFrame(input_data)

    # Take the log for some data
    data[['carat','depth','table','x','y','z']] = np.log(data[['carat','depth','table','x','y','z']])
    
    # Columns to with some outliers
    columns_with_outliers = ['carat','x','y','z']
    data = reassign_outliers_iqr(train_set, data, columns_with_outliers)
    
    # Feature Engineering
    data['average_dimensions'] = (data['x'] + data['y'] + data['z']) / 3
    data['depth_percentage'] = (data['depth'] / data['average_dimensions']) * 100
    data['table_percentage'] = (data['table'] / data['average_dimensions']) * 100
    data.drop(['depth', 'table', 'average_dimensions'], axis=1, inplace=True)
    
    # Encode the categorical data
    cat = ['cut','color','clarity']
    data[cat] = categories_encoding.transform(data)
    
    # Scaling the data
    x_scaled = scaler.transform(data)
    data = pd.DataFrame(x_scaled, columns=data.columns,index=data.index)
    
    # Make Prediction 
    prediction = model.predict(data)
    
    return prediction 


class ResultWindow(QWidget):
    def __init__(self, price):
        super().__init__()
        self.label_color = QColor(0, 0, 0)  # Blue color for labels

        self.initUI(price)
        
    def initUI(self, price):
        self.setWindowTitle('Predicted Price')
        self.setGeometry(150, 150, 350, 100)
        
        # Set the window icon
        self.setWindowIcon(QIcon(result_window_icon_path))  # You can use .png here
        
        layout = QVBoxLayout()
        label_widget = QLabel(f"The predicted price is: ${price[0]:.2f}")
        label_widget.setFont(QFont('Arial', 15, QFont.Bold))
        label_widget.setStyleSheet(f"color: {self.label_color.name()}")
        layout.addWidget(label_widget)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DiamondPriceGUI()
    ex.show()
    sys.exit(app.exec_())