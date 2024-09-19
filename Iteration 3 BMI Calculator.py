import os
import json
import datetime
import customtkinter as ctk
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkcalendar import Calendar
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Constants
BMI_UNDERWEIGHT = 18.5
BMI_NORMAL = 25.0
BMI_OVERWEIGHT = 30.0
BMI_DECIMAL_PLACES = 1
DATA_DIR = "user_data"
USERS_FILE = "users.json"

# Set the color theme for customtkinter
ctk.set_appearance_mode("light")  # Light mode
ctk.set_default_color_theme("blue")  # Light blue theme

# Class representing a user with username and password attributes
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

# Class to manage users including registration, authentication, and file operations
class UserManager:
    def __init__(self):
        self.users = {}
        self.load_users()
        
    # Load user data from JSON file if it exists, otherwise create a new one
    def load_users(self):
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                user_data = json.load(f)
                # Convert JSON data into User objects
                self.users = {username: User(username, data['password']) for username, data in user_data.items()}
        else:
            self.save_users()

    # Save current user data into the JSON file
    def save_users(self):
        user_data = {username: {'password': user.password} for username, user in self.users.items()}
        with open(USERS_FILE, "w") as f:
            json.dump(user_data, f)

    # Register a new user; return False if username already exists
    def register_user(self, username, password):
        if username in self.users:
            return False
        self.users[username] = User(username, password)
        self.save_users()
        return True

    # Authenticate the user by checking the username and password
    def authenticate_user(self, username, password):
        if username not in self.users:
            return False
        return self.users[username].password == password

class BMICalculator:
    def __init__(self, username):
        self.username = username
        self.bmi_data = []
        self.load_data()

    def calculate_bmi(self, weight, height):
        return weight / ((height / 100) ** 2)

    def interpret_bmi(self, bmi):
        if bmi < BMI_UNDERWEIGHT:
            return "Underweight"
        elif BMI_UNDERWEIGHT <= bmi < BMI_NORMAL:
            return "Normal weight"
        elif BMI_NORMAL <= bmi < BMI_OVERWEIGHT:
            return "Overweight"
        else:
            return "Obese"

    def add_bmi_entry(self, date, weight, height):
        bmi = self.calculate_bmi(weight, height)
        interpretation = self.interpret_bmi(bmi)
        entry = {
            "date": date.strftime("%Y-%m-%d"),
            "bmi": round(bmi, BMI_DECIMAL_PLACES),
            "weight": weight,
            "height": height,
            "interpretation": interpretation
        }
        self.bmi_data.append(entry)
        self.bmi_data.sort(key=lambda x: x["date"])
        self.save_data()
        return entry

    def remove_bmi_entry(self, index):
        if 0 <= index < len(self.bmi_data):
            del self.bmi_data[index]
            self.save_data()
            return True
        return False

    def save_data(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        with open(os.path.join(DATA_DIR, f"{self.username}_bmi_data.json"), "w") as f:
            json.dump(self.bmi_data, f)

    def load_data(self):
        file_path = os.path.join(DATA_DIR, f"{self.username}_bmi_data.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                self.bmi_data = json.load(f)
        else:
            self.save_data()

    def analyze_bmi_trend(self):
        if len(self.bmi_data) < 2:
            return "Not enough data to analyze trend."

        first_bmi = self.bmi_data[0]['bmi']
        last_bmi = self.bmi_data[-1]['bmi']
        bmi_change = last_bmi - first_bmi

        if bmi_change > 0:
            trend = "increasing"
        elif bmi_change < 0:
            trend = "decreasing"
        else:
            trend = "stable"

        return f"Your BMI has been {trend}. Total change: {bmi_change:.1f}"

# Class for handling the login window GUI
class LoginWindow:
    def __init__(self, master, user_manager, on_login_success):
        self.master = master
        self.user_manager = user_manager
        self.on_login_success = on_login_success

        self.master.title("Login")
        self.master.geometry("300x300")  # Increased height for spacing

        self.create_widgets()

    # Create login form fields for username, password, and buttons
    def create_widgets(self):
        self.username_label = ctk.CTkLabel(self.master, text="Username:")
        self.username_label.pack(pady=3)

        self.username_entry = ctk.CTkEntry(self.master, placeholder_text="Enter your username")
        self.username_entry.pack(pady=5)

        self.password_label = ctk.CTkLabel(self.master, text="Password:")
        self.password_label.pack(pady=3)

        self.password_entry = ctk.CTkEntry(self.master, show="*", placeholder_text="Enter your password")
        self.password_entry.pack(pady=5)

        self.login_button = ctk.CTkButton(self.master, text="Login", command=self.login)
        self.login_button.pack(pady=5)

        self.register_button = ctk.CTkButton(self.master, text="Register New Account", command=self.open_register_window)
        self.register_button.pack(pady=15)

    # Perform login when the user clicks the login button
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Call UserManager to authenticate the username and password
        if self.user_manager.authenticate_user(username, password):
            self.master.withdraw()  # Hide the login window after successful login
            self.on_login_success(username) # Call the callback to move forward in the app
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    # Open a new window for user registration
    def open_register_window(self):
        register_window = Toplevel(self.master)
        RegisterWindow(register_window, self.user_manager)

# Class for handling the user registration window GUI
class RegisterWindow:
    def __init__(self, master, user_manager):
        self.master = master
        self.user_manager = user_manager

        self.master.title("Register")
        self.master.geometry("300x300")

        self.create_widgets()
    
    # Create registration form fields for username, password, and buttons
    def create_widgets(self):
        self.username_label = ctk.CTkLabel(self.master, text="Username:")
        self.username_label.pack(pady=5)

        self.username_entry = ctk.CTkEntry(self.master, placeholder_text="Enter a username")
        self.username_entry.pack(pady=5)

        self.password_label = ctk.CTkLabel(self.master, text="Password:")
        self.password_label.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self.master, show="*", placeholder_text="Enter a password")
        self.password_entry.pack(pady=5)

        self.register_button = ctk.CTkButton(self.master, text="Register", command=self.register)
        self.register_button.pack(pady=10)

    # Register the user when the user clicks the register button
    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Call UserManager to register the new user
        if self.user_manager.register_user(username, password):
            messagebox.showinfo("Registration Successful", "You can now login with your new account")
            self.master.destroy() # Close the registration window after success
        else:
            messagebox.showerror("Registration Failed", "Username already exists")

class BMICalculatorGUI:
    def __init__(self, master, username):
        self.master = master
        self.master.title(f"BMI Calculator - {username}")
        self.calculator = BMICalculator(username)

        self.master.minsize(600, 400)
        self.master.geometry("600x400")

        self.create_widgets()

    def create_widgets(self):
        self.notebook = Notebook(self.master)
        self.notebook.pack(expand=True, fill=BOTH)

        self.create_input_tab()
        self.create_history_tab()
        self.create_chart_tab()

    def create_input_tab(self):
        input_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(input_frame, text="Input")

        # Create a frame to hold the input fields and calendar side by side
        content_frame = ctk.CTkFrame(input_frame)
        content_frame.pack(expand=True, fill=BOTH)
        
        # Left frame for input fields
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side=LEFT, padx=(0, 10), expand=True, fill=BOTH)

        # Add widgets to the left frame
        self.date_entry = self.create_labeled_entry(left_frame, "Date (YYYY-MM-DD):", Entry, 0)
        self.weight_entry = self.create_labeled_entry(left_frame, "Weight (kg):", Entry, 1)
        self.height_entry = self.create_labeled_entry(left_frame, "Height (cm):", Entry, 2)

        # Create a button frame to center buttons
        button_frame = ctk.CTkFrame(left_frame, corner_radius=10)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.create_button(button_frame, "Calculate BMI", self.calculate_bmi)
        self.result_label = Label(left_frame, text="")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)

        self.create_button(left_frame, "View Exercise Suggestions", self.show_exercise_suggestions, row=5)

        # Right frame for calendar
        right_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        right_frame.pack(side=RIGHT, padx=(10, 0), fill=BOTH)

        # Add calendar to the right frame
        self.calendar = Calendar(right_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack(fill=BOTH)

        # Bind the calendar selection to update the date entry
        self.calendar.bind("<<CalendarSelected>>", self.update_date_entry)

    def update_date_entry(self, event):
        selected_date = self.calendar.get_date()
        self.date_entry.delete(0, END)
        self.date_entry.insert(0, selected_date)

    def create_history_tab(self):
        history_frame = Frame(self.notebook, padding="10")
        self.notebook.add(history_frame, text="History")

        self.history_tree = Treeview(history_frame, columns=("Date", "BMI", "Interpretation"), show="headings")
        for col in ["Date", "BMI", "Interpretation"]:
            self.history_tree.heading(col, text=col)
        self.history_tree.pack(expand=True, fill=BOTH)

        self.create_button(history_frame, "Remove Selected", self.remove_entry, None, expand=True)

    def create_chart_tab(self):
        chart_frame = Frame(self.notebook, padding="10")
        self.notebook.add(chart_frame, text="BMI Chart")

        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=BOTH)

        self.update_history()
        self.update_chart()

    def create_labeled_entry(self, parent, text, widget_type, row):
        label = ctk.CTkLabel(parent, text=text)
        label.grid(row=row, column=0, sticky=W, padx=10, pady=5)
        entry = ctk.CTkEntry(parent, placeholder_text=text)
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        return entry

    def create_button(self, parent, text, command, row=None, expand=False):
        button = ctk.CTkButton(parent, text=text, command=command, corner_radius=10)
        if row is not None:
            button.grid(row=row, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
        else:
            button.pack(expand=expand, pady=5, padx=5)
        return button


    def calculate_bmi(self):
        try:
            date = datetime.datetime.strptime(self.date_entry.get(), "%Y-%m-%d").date()
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())

            entry = self.calculator.add_bmi_entry(date, weight, height)
            self.result_label.config(text=f"BMI: {entry['bmi']} - {entry['interpretation']}")
            self.update_history()
            self.update_chart()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid weight and height values.")

    def update_history(self):
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)
        for entry in self.calculator.bmi_data:
            self.history_tree.insert("", "end", values=(entry["date"], entry["bmi"], entry["interpretation"]))

    def remove_entry(self):
        selected_item = self.history_tree.selection()
        if selected_item:
            index = self.history_tree.index(selected_item)
            if self.calculator.remove_bmi_entry(index):
                self.update_history()
                self.update_chart()
                messagebox.showinfo("Success", "Entry removed successfully.")
            else:
                messagebox.showerror("Error", "Failed to remove entry.")
        else:
            messagebox.showwarning("Warning", "Please select an entry to remove.")

    # The following section shows the visual representation of BMI over time in the form of a graph
    def update_chart(self):
        self.ax.clear()
        # Convert the date strings from the BMI data entries into datetime objects for plotting
        dates = [datetime.datetime.strptime(entry['date'], "%Y-%m-%d") for entry in self.calculator.bmi_data]
        bmis = [entry['bmi'] for entry in self.calculator.bmi_data]

        # Check if there is any data to plot
        if not self.calculator.bmi_data:
            self.ax.set_title('BMI Trend')
            self.ax.set_xlabel('Date')
            self.ax.set_ylabel('BMI')
            self.ax.grid(True)
            self.ax.set_xticks([])  # Remove x-axis ticks if there's no data
            self.ax.set_yticks([])  # Remove y-axis ticks if there's no data
            self.canvas.draw()
            return

        self.ax.plot(dates, bmis, marker='o')
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('BMI')
        self.ax.set_title('BMI Trend')
        self.ax.grid(True)

        # Determine the range of dates to adjust tick frequency
        date_range = (max(dates) - min(dates)).days

        # Adjust tick frequency based on the date range
        if date_range <= 7:
            # Use daily ticks for a range of up to a week
            self.ax.xaxis.set_major_locator(mdates.DayLocator())
        elif date_range <= 31:
            # Use weekly ticks for a range of up to a month
            self.ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        else:
            # Use monthly ticks for longer ranges
            self.ax.xaxis.set_major_locator(mdates.MonthLocator())

        # Format dates to "day-month-year"
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))

        # Rotate date labels to prevent overlap
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right")

        # Adjust layout to accommodate rotated labels
        plt.tight_layout()

        self.canvas.draw()

    def show_exercise_suggestions(self):
        ExerciseSuggestionWindow(self.master)

class ExerciseSuggestionWindow:
    def __init__(self, parent):
        self.window = Toplevel(parent)
        self.window.title("Exercise Suggestions")
        self.window.geometry("500x400")

        self.exercises = self.load_exercise_data()
        self.current_exercise = 0

        self.create_widgets()

    def create_widgets(self):
        self.image_label = Label(self.window)
        self.image_label.pack(pady=10)

        self.description_label = Label(self.window, wraplength=450, justify="center")
        self.description_label.pack(pady=10)

        button_frame = Frame(self.window)
        button_frame.pack(pady=10)

        self.create_button(button_frame, "Previous", self.previous_exercise)
        self.create_button(button_frame, "Next", self.next_exercise)

        self.display_exercise()

    def create_button(self, parent, text, command):
        Button(parent, text=text, command=command).pack(side=LEFT, padx=5)

    def load_exercise_data(self):
        return [
            {"name": "Walking", "description": "Walking is a low-impact exercise that can be done anywhere. It improves cardiovascular health, strengthens muscles, and boosts mood. Recommended: 150 minutes per week."},
            {"name": "Running", "description": "Running is an excellent cardio workout that burns a lot of calories and improves cardiovascular fitness. It can be done outdoors or on a treadmill. Recommended: 3-4 times per week, 20-30 minutes per session."},
            {"name": "Cycling", "description": "Cycling, whether on a bike or stationary, is great for cardiovascular health and leg strength. It’s low-impact and can be adjusted for different fitness levels. Recommended: 2-3 times per week, 30-45 minutes per session."},
            {"name": "Rowing", "description": "Rowing provides a full-body workout, focusing on both upper and lower body strength as well as cardio endurance. It’s effective and low-impact. Recommended: 2-3 times per week, 20-30 minutes per session."},
            {"name": "Jump Rope", "description": "Jumping rope is an effective way to boost cardiovascular health and coordination. It’s a high-intensity workout that can be done in a short time. Recommended: 3 times per week, 10-15 minutes per session."},
            {"name": "Swimming", "description": "Swimming is a low-impact exercise that improves cardiovascular fitness and tones muscles. It’s ideal for full-body conditioning. Recommended: 2-3 times per week, 30 minutes per session."},
            {"name": "High-Intensity Interval Training (HIIT)", "description": "HIIT involves short bursts of intense exercise followed by rest periods. It’s highly effective for burning calories and improving cardiovascular health. Recommended: 2-3 times per week, 20-30 minutes per session."}
        ]

    def display_exercise(self):
        exercise = self.exercises[self.current_exercise]
        self.description_label.config(text=f"{exercise['name']}\n\n{exercise['description']}")

    def next_exercise(self):
        self.current_exercise = (self.current_exercise + 1) % len(self.exercises)
        self.display_exercise()

    def previous_exercise(self):
        self.current_exercise = (self.current_exercise - 1) % len(self.exercises)
        self.display_exercise()

def main():
    root = Tk()
    user_manager = UserManager()

    def on_login_success(username):
        login_window.master.destroy()
        new_root = Tk()
        app = BMICalculatorGUI(new_root, username)
        new_root.mainloop()

    login_window = LoginWindow(root, user_manager, on_login_success)
    root.mainloop()

if __name__ == "__main__":
    main()