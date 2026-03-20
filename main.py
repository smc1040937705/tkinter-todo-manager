import tkinter as tk
from models import DataManager
from views import MainWindow


def main():
    data_manager = DataManager()
    app = MainWindow(data_manager)
    app.run()


if __name__ == "__main__":
    main()
