# ===========================================================
# Author: sweet.Famine
# Project: Customer Management System
# Version: 1.0.0
# Date: 05.10.2025 22:30Uhr
#
# A smal and simple customer management system
# using customtkinter for GUI and sqlite3 for the database.
#
# All rights reserved.
# see LICENSE for details.
#
#    /\_/\
#   ( o.o )
#    > ^ <
# @sweetfamine 2025
# ===========================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import customtkinter as ctk
from Utils.config import Config
from Manager.customer_manager import CustomerManager
from Frontend.main_window import MainWindow

def main():
    config = Config()
    db_path = config.get("db_path", "data/customers.db")
    manager = CustomerManager(db_path=db_path)
    ctk.set_appearance_mode(config.get("appearance_mode", "light"))
    ctk.set_default_color_theme("dark-blue")
    app = MainWindow(manager, config)
    app.mainloop()
    manager.close()

if __name__ == "__main__":
    main()