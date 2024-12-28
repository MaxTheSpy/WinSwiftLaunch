import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import configparser

class AppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Application Launcher")
        self.root.minsize(300, 400)

        # Data storage for applications
        self.config_file = "config.ini"
        self.config = self.load_config()

        # Variables
        self.dark_mode = tk.BooleanVar(value=self.config.getboolean("Settings", "dark_mode", fallback=False))

        # Apply dark mode setting on startup
        self.apply_dark_mode()

        # Main frame setup
        self.main_frame = ttk.Frame(self.root)
        self.settings_frame = ttk.Frame(self.root)
        self.add_app_frame = None

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

        ttk.Label(self.main_frame, text="Application Launcher", font=("Helvetica", 16)).pack(pady=10)

        # Show categorized apps with dropdowns
        for category in self.config["Applications"]:
            apps = eval(self.config["Applications"][category])  # Convert string back to list of tuples
            frame = ttk.LabelFrame(self.main_frame, text=f"Category: {category}", padding=(10, 5))
            frame.pack(fill=tk.X, padx=10, pady=5)

            toggle_button = ttk.Button(
                frame, text="Show/Hide", command=lambda f=frame: self.toggle_visibility(f)
            )
            toggle_button.pack(side=tk.RIGHT, padx=5)

            for app_name, app_path in apps:
                button = ttk.Button(
                    frame, text=app_name, command=lambda path=app_path: self.launch_app(path)
                )
                button.pack(pady=2, padx=20, fill=tk.X)

        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def build_settings_page(self):
        """Build the settings page."""
        for widget in self.settings_frame.winfo_children():
            widget.destroy()

        # Dark mode toggle
        ttk.Checkbutton(
            self.settings_frame, text="Dark Mode", variable=self.dark_mode, command=self.toggle_dark_mode
        ).pack(pady=10)

        # Add application button
        ttk.Button(self.settings_frame, text="Add Application", command=self.show_add_application).pack(pady=10)

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
        ttk.Button(self.add_app_frame, text="Browse", command=self.browse_file).pack(pady=5)

        ttk.Label(self.add_app_frame, text="Category:").pack(anchor=tk.W, padx=10)
        self.category_entry = ttk.Entry(self.add_app_frame)
        self.category_entry.pack(fill=tk.X, padx=10, pady=5)

        # Add button
        ttk.Button(self.add_app_frame, text="Add", command=self.add_application).pack(pady=10)
        ttk.Button(self.add_app_frame, text="Back", command=self.show_settings).pack(pady=5)

    def show_main(self):
        """Show the main launcher page."""
        if self.add_app_frame:
            self.add_app_frame.pack_forget()
        self.settings_frame.pack_forget()
        self.build_main_page()
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def show_settings(self):
        """Show the settings page."""
        if self.add_app_frame:
            self.add_app_frame.pack_forget()
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
        category = self.category_entry.get().strip()

        if not app_name or not app_path or not category:
            messagebox.showerror("Error", "All fields must be filled out.")
            return

        if not os.path.exists(app_path):
            messagebox.showerror("Error", "Executable path does not exist.")
            return

        if category not in self.config["Applications"]:
            self.config["Applications"][category] = str([])

        apps = eval(self.config["Applications"][category])  # Convert string back to list
        apps.append((app_name, app_path))
        self.config["Applications"][category] = str(apps)  # Convert list back to string

        self.save_config()
        messagebox.showinfo("Success", "Application added successfully.")

        self.app_name_entry.delete(0, tk.END)
        self.app_path_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)

    def launch_app(self, app_path):
        """Launch the selected application."""
        try:
            os.startfile(app_path) if os.name == "nt" else os.system(f"open {app_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch application: {e}")

    def toggle_visibility(self, frame):
        """Toggle the visibility of a frame's children."""
        for child in frame.winfo_children():
            if not isinstance(child, ttk.Button):  # Keep the toggle button visible
                child.pack_forget() if child.winfo_manager() else child.pack(pady=2, padx=20, fill=tk.X)

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
