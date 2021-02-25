import tkinter as tk
import webbrowser
class MainMenu(tk.Menu):

    def __init__(self, parent, *args, **kwargs):

        self.parent = parent

        self.menubar = tk.Menu(self.parent.parent)
        self.parent.config(menu=self.menubar)

        # File Menu
        self.file_menu = tk.Menu(
            self.menubar,
            tearoff=0
        )
        self.file_menu.add_command(label='Import Raw Data', command=self.load_raw_data_button)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Select export folder', command=self.browse_button)
        self.menubar.add_cascade(
            label="File",
            menu=self.file_menu
        )
        # Help Menu

        self.help_menu = tk.Menu(
            self.menubar,
            tearoff=0
        )
        self.menubar.add_cascade(
            label="Help",
            menu=self.help_menu
        )

        self.help_menu.add_command(label='GitHub page', command=lambda: webbrowser.open_new(
            'https://github.com/eilmi/HAMEG-HM1007-serial-interface'))
        return