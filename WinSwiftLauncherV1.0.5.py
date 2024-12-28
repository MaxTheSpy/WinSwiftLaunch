import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import configparser
import threading

def delay_reset_button(button, original_text):
    def reset_text():
        button.config(text=original_text, state=tk.NORMAL)
    threading.Timer(5, reset_text).start()

class AppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("WinSwiftLaunch")
        self.root.minsize(300, 400)

        # Data storage for applications
        self.config_dir = os.path.join(os.path.expanduser("~"), "Documents", "WinSwiftLaunch")
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_file = os.path.join(self.config_dir, "config.ini")
        self.config = self.load_config()

        # Variables
        self.dark_mode = tk.BooleanVar(value=self.config.getboolean("Settings", "dark_mode", fallback=False))

        # Apply dark mode setting on startup
        self.apply_dark_mode()

        # Main frame setup
        self.main_frame = ttk.Frame(self.root)
        self.settings_frame = ttk.Frame(self.root)
        self.add_app_frame = None
        self.reorder_frame = None

        # Setup navigation buttons
        self.nav_frame = ttk.Frame(self.root)
        self.nav_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(self.nav_frame, text="Launcher", command=self.show_main).pack(side=tk.LEFT)
        ttk.Button(self.nav_frame, text="Settings", command=self.show_settings).pack(side=tk.LEFT)

        # Build the pages
        self.build_main_page()
        self.build_settings_page()

        # Show main page by default
        self.show_main()

    def load_config(self):
        """Load configuration from an INI file."""
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
        if "Applications" not in config:
            config["Applications"] = {}
        if "Settings" not in config:
            config["Settings"] = {"dark_mode": "False"}
        return config

    def save_config(self):
        """Save configuration to an INI file."""
        with open(self.config_file, "w") as file:
            self.config.write(file)

    def apply_dark_mode(self):
        """Apply dark mode setting on startup."""
        style = ttk.Style()
        if self.dark_mode.get():
            style.theme_use("clam")
            style.configure("TFrame", background="#2e2e2e")
            style.configure("TLabel", background="#2e2e2e", foreground="white")
            style.configure("TButton", background="#444", foreground="white")
            style.configure("TCheckbutton", background="#2e2e2e", foreground="white")
        else:
            style.theme_use("default")

    def build_main_page(self):
        """Build the main page where apps can be launched."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Display applications in order
        apps = eval(self.config["Applications"].get("app_list", "[]"))  # Convert string back to list of tuples
        for app_name, app_path in apps:
            button = ttk.Button(self.main_frame, text=app_name)
            button.config(command=lambda path=app_path, btn=button: self.launch_app_with_feedback(path, btn))
            button.pack(pady=5, padx=10, fill=tk.X)

        # Developer credit
        ttk.Label(self.main_frame, text="Developer: MTS2024", font=("Helvetica", 10)).pack(side=tk.BOTTOM, pady=10)

        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def build_settings_page(self):
        """Build the settings page."""
        for widget in self.settings_frame.winfo_children():
            widget.destroy()

        # Dark mode toggle
        ttk.Checkbutton(
            self.settings_frame, text="Dark Mode", variable=self.dark_mode, command=self.toggle_dark_mode
        ).pack(pady=10)

        # Add application and reorder applications side by side
        button_frame = ttk.Frame(self.settings_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Add Application", command=self.show_add_application).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reorder Applications", command=self.show_reorder_frame).pack(side=tk.LEFT, padx=5)

        # Developer credit
        ttk.Label(self.settings_frame, text="Developer: MTS2024", font=("Helvetica", 10)).pack(side=tk.BOTTOM, pady=10)

        self.settings_frame.pack(fill=tk.BOTH, expand=True)

    def show_add_application(self):
        """Show the add application form."""
        if self.add_app_frame:
            self.add_app_frame.destroy()

        self.add_app_frame = ttk.Frame(self.root)
        self.add_app_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.add_app_frame, text="Add New Application", font=("Helvetica", 16)).pack(pady=10)

        # Entry fields for app details
        ttk.Label(self.add_app_frame, text="Application Name:").pack(anchor=tk.W, padx=10)
        self.app_name_entry = ttk.Entry(self.add_app_frame)
        self.app_name_entry.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.add_app_frame, text="Executable Path:").pack(anchor=tk.W, padx=10)
        self.app_path_entry = ttk.Entry(self.add_app_frame)
        self.app_path_entry.pack(fill=tk.X, padx=10, pady=5)

        browse_add_back_frame = ttk.Frame(self.add_app_frame)
        browse_add_back_frame.pack(pady=10)
        ttk.Button(browse_add_back_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(browse_add_back_frame, text="Add", command=self.add_application).pack(side=tk.LEFT, padx=5)
        ttk.Button(browse_add_back_frame, text="Back", command=self.show_settings).pack(side=tk.LEFT, padx=5)

        # Developer credit
        ttk.Label(self.add_app_frame, text="Developer: MTS2024", font=("Helvetica", 10)).pack(side=tk.BOTTOM, pady=10)

    def show_reorder_frame(self):
        """Show the reorder applications frame."""
        if self.reorder_frame:
            self.reorder_frame.destroy()

        self.reorder_frame = ttk.Frame(self.root)
        self.reorder_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.reorder_frame, text="Reorder Applications", font=("Helvetica", 16)).pack(pady=10)

        apps = eval(self.config["Applications"].get("app_list", "[]"))  # Convert string back to list of tuples
        self.reorder_widgets = []

        for i, (app_name, app_path) in enumerate(apps):
            frame = ttk.Frame(self.reorder_frame)
            frame.pack(fill=tk.X, pady=5, padx=10)

            ttk.Label(frame, text=app_name).pack(side=tk.LEFT, padx=5)

            button_frame = ttk.Frame(frame)
            button_frame.pack(side=tk.RIGHT)

            up_button = ttk.Button(button_frame, text="Up", command=lambda idx=i: self.move_app(idx, -1))
            up_button.pack(side=tk.LEFT, padx=5)

            down_button = ttk.Button(button_frame, text="Down", command=lambda idx=i: self.move_app(idx, 1))
            down_button.pack(side=tk.LEFT, padx=5)

            self.reorder_widgets.append((frame, app_name, app_path))

        save_back_frame = ttk.Frame(self.reorder_frame)
        save_back_frame.pack(pady=10)
        ttk.Button(save_back_frame, text="Save", command=self.save_reorder).pack(side=tk.LEFT, padx=5)
        ttk.Button(save_back_frame, text="Back", command=self.show_settings).pack(side=tk.LEFT, padx=5)

        # Developer credit
        ttk.Label(self.reorder_frame, text="Developer: MTS2024", font=("Helvetica", 10)).pack(side=tk.BOTTOM, pady=10)

    def move_app(self, index, direction):
        """Move an application up or down in the list."""
        apps = eval(self.config["Applications"].get("app_list", "[]"))
        if 0 <= index + direction < len(apps):
            apps[index], apps[index + direction] = apps[index + direction], apps[index]
            self.config["Applications"]["app_list"] = str(apps)
            self.save_config()
            self.show_reorder_frame()

    def save_reorder(self):
        """Save the reordered application list."""
        apps = [(app_name, app_path) for _, app_name, app_path in self.reorder_widgets]
        self.config["Applications"]["app_list"] = str(apps)
        self.save_config()
        messagebox.showinfo("Success", "Application order updated.")
        self.show_main()

    def launch_app_with_feedback(self, app_path, button):
        """Launch the application and show feedback on the button."""
        original_text = button.cget("text")
        button.config(text="Launching...", state=tk.DISABLED)
        delay_reset_button(button, original_text)
        try:
            os.startfile(app_path) if os.name == "nt" else os.system(f"open \"{app_path}\" &")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch application: {e}")

    def show_main(self):
        """Show the main launcher page."""
        if self.add_app_frame:
            self.add_app_frame.pack_forget()
        if self.reorder_frame:
            self.reorder_frame.pack_forget()
        self.settings_frame.pack_forget()
        self.build_main_page()
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def show_settings(self):
        """Show the settings page."""
        if self.add_app_frame:
            self.add_app_frame.pack_forget()
        if self.reorder_frame:
            self.reorder_frame.pack_forget()
        self.main_frame.pack_forget()
        self.build_settings_page()
        self.settings_frame.pack(fill=tk.BOTH, expand=True)

    def browse_file(self):
        """Open a file dialog to select an executable."""
        file_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe" if os.name == "nt" else "*.*")])
        if file_path:
            self.app_path_entry.delete(0, tk.END)
            self.app_path_entry.insert(0, file_path)

    def add_application(self):
        """Add a new application to the launcher."""
        app_name = self.app_name_entry.get().strip()
        app_path = self.app_path_entry.get().strip()

        if not app_name or not app_path:
            messagebox.showerror("Error", "All fields must be filled out.")
            return

        if not os.path.exists(app_path):
            messagebox.showerror("Error", "Executable path does not exist.")
            return

        apps = eval(self.config["Applications"].get("app_list", "[]"))  # Convert string back to list
        apps.append((app_name, app_path))
        self.config["Applications"]["app_list"] = str(apps)  # Convert list back to string

        self.save_config()
        messagebox.showinfo("Success", "Application added successfully.")

        self.app_name_entry.delete(0, tk.END)
        self.app_path_entry.delete(0, tk.END)

    def toggle_dark_mode(self):
        """Toggle dark mode for the application."""
        style = ttk.Style()
        if self.dark_mode.get():
            style.theme_use("clam")
            style.configure("TFrame", background="#2e2e2e")
            style.configure("TLabel", background="#2e2e2e", foreground="white")
            style.configure("TButton", background="#444", foreground="white")
            style.configure("TCheckbutton", background="#2e2e2e", foreground="white")
            self.config["Settings"]["dark_mode"] = "True"
        else:
            style.theme_use("default")
            self.config["Settings"]["dark_mode"] = "False"
        self.save_config()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppLauncher(root)
    root.mainloop()
