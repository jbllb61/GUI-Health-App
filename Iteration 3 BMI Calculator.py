import os
import json
import datetime
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkcalendar import Calendar
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Constants
BMI_UNDERWEIGHT = 18.4
BMI_NORMAL = 29.4
BMI_OVERWEIGHT = 39.9
BMI_OBESE = 40.0
BMI_DECIMAL_PLACES = 1
DATA_DIR = "user_data"
USERS_FILE = "users.json"

# Class representing a user with username and password attributes
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.latest_weight = None
        self.latest_height = None

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
        # Load latest height and weight
        for username, user in self.users.items():
                    user.latest_weight = user_data[username].get('latest_weight')
                    user.latest_height = user_data[username].get('latest_height')
        else:
            self.save_users()

    # Save current user data into the JSON file
    def save_users(self):
        user_data = {
            username: {
                'password': user.password,
                'latest_weight': user.latest_weight,
                'latest_height': user.latest_height
            } for username, user in self.users.items()
        }
        with open(USERS_FILE, "w") as f:
            json.dump(user_data, f)

    # Register a new user; return False if username already exists
    def register_user(self, username, password):
        if username in self.users:
            return False
        self.users[username] = User(username, password)
        self.save_users()
        return True
    
    def update_user_data(self, username, weight, height):
        if username in self.users:
            self.users[username].latest_weight = weight
            self.users[username].latest_height = height
            self.save_users()
            
    def get_user_data(self, username):
        if username in self.users:
            return self.users[username].latest_weight, self.users[username].latest_height
        return None, None

    # Authenticate the user by checking the username and password
    def authenticate_user(self, username, password):
        if username not in self.users:
            return False
        return self.users[username].password == password

class BMICalculator:
    def __init__(self, username, user_manager):
        self.username = username
        self.user_manager = user_manager
        self.bmi_data = {}  # Initialize as an empty dictionary
        self.load_data()

    def calculate_bmi(self, weight, height):
        return weight / ((height / 100) ** 2)

    def interpret_bmi(self, bmi):
        if bmi <= BMI_UNDERWEIGHT:
            return "Underweight"
        elif BMI_UNDERWEIGHT < bmi <= BMI_NORMAL:
            return "Normal weight"
        elif BMI_NORMAL < bmi <= BMI_OVERWEIGHT:
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
        
        # Store the entry using the formatted date as the key
        self.bmi_data[date.strftime("%Y-%m-%d")] = entry

        self.save_data()
        self.user_manager.update_user_data(self.username, weight, height)
        
        return entry

    def remove_bmi_entry(self, date_str):
        if date_str in self.bmi_data:
            del self.bmi_data[date_str]
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
            try:
                with open(file_path, "r") as f:
                    file_content = f.read()
                    if not file_content.strip():  # Check if the file is empty
                        self.bmi_data = {}  # Initialize with empty dictionary
                    else:
                        loaded_data = json.loads(file_content)
                        if isinstance(loaded_data, list):
                            # Convert list to dictionary if old format is encountered
                            self.bmi_data = {entry['date']: entry for entry in loaded_data}
                        elif isinstance(loaded_data, dict):
                            self.bmi_data = loaded_data
                        else:
                            print(f"Unexpected data type in file: {type(loaded_data)}")
                            self.bmi_data = {}
            except json.JSONDecodeError:
                print("Error decoding JSON, initializing with empty data")
                self.bmi_data = {}
        else:
            self.bmi_data = {}
        self.save_data()  # Save to ensure consistent format

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
        self.master.geometry("300x220")  # Increased height for spacing

        self.create_widgets()
        self.load_saved_details()  # Load saved login details if available

    # Create login form fields for username, password, and buttons
    def create_widgets(self):
        self.username_label = Label(self.master, text="Username:")
        self.username_label.pack(pady=5)

        self.username_entry = Entry(self.master)
        self.username_entry.pack()

        self.password_label = Label(self.master, text="Password:")
        self.password_label.pack(pady=5)

        self.password_entry = Entry(self.master, show="*")
        self.password_entry.pack()

        # Remember Me checkbox
        self.remember_var = BooleanVar()
        self.remember_check = Checkbutton(self.master, text="Remember My Details", variable=self.remember_var)
        self.remember_check.pack(pady=5)

        self.login_button = Button(self.master, text="Login", command=self.login)
        self.login_button.pack(pady=3)

        self.register_button = Button(self.master, text="Register New Account", command=self.open_register_window)
        self.register_button.pack(pady=15)

    # Perform login when the user clicks the login button
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.user_manager.authenticate_user(username, password):
            # Save login details if "Remember Me" is checked
            if self.remember_var.get():
                self.save_login_details(username, password)
            else:
                self.clear_login_details()
                
            self.master.withdraw()
            self.on_login_success(username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    # Open a new window for user registration
    def open_register_window(self):
        register_window = Toplevel(self.master)
        RegisterWindow(register_window, self.user_manager)

    def load_saved_details(self):
        if os.path.exists("remember_details.json"):
            with open("remember_details.json", "r") as f:
                data = json.load(f)
                self.username_entry.insert(0, data.get("username", ""))
                self.password_entry.insert(0, data.get("password", ""))
                self.remember_var.set(True)

    def save_login_details(self, username, password):
        with open("remember_details.json", "w") as f:
            json.dump({"username": username, "password": password}, f)

    def clear_login_details(self):
        if os.path.exists("remember_details.json"):
            os.remove("remember_details.json")
            
# Class for handling the user registration window GUI
class RegisterWindow:
    def __init__(self, master, user_manager):
        self.master = master
        self.user_manager = user_manager

        self.master.title("Register")
        self.master.geometry("300x150")

        self.create_widgets()
    
    # Create registration form fields for username, password, and buttons
    def create_widgets(self):
        self.username_label = Label(self.master, text="Username:")
        self.username_label.pack()
        self.username_entry = Entry(self.master)
        self.username_entry.pack()

        self.password_label = Label(self.master, text="Password:")
        self.password_label.pack()
        self.password_entry = Entry(self.master, show="*") # Hide password characters
        self.password_entry.pack()

        # Button to register the new user
        self.register_button = Button(self.master, text="Register", command=self.register)
        self.register_button.pack()

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
    def __init__(self, master, username, user_manager):
        self.master = master
        self.master.title(f"BMI Calculator - {username}")
        self.user_manager = user_manager
        self.calculator = BMICalculator(username, user_manager)

        self.master.minsize(600, 400)
        self.master.geometry("600x400")

        self.create_widgets()
        self.load_user_data()
        
    def create_widgets(self):
        self.notebook = Notebook(self.master)
        self.notebook.pack(expand=True, fill=BOTH)

        self.create_input_tab()
        self.create_history_tab()
        self.create_chart_tab()
        
    def load_user_data(self):
        weight, height = self.user_manager.get_user_data(self.calculator.username)
        if weight:
            self.weight_entry.delete(0, END)
            self.weight_entry.insert(0, str(weight))
        if height:
            self.height_entry.delete(0, END)
            self.height_entry.insert(0, str(height))

    def create_input_tab(self):
        input_frame = Frame(self.notebook, padding="10")
        self.notebook.add(input_frame, text="Input")

        # Create a frame to hold the input fields and calendar side by side
        content_frame = Frame(input_frame)
        content_frame.pack(expand=True, fill=BOTH)

        # Left frame for input fields
        left_frame = Frame(content_frame)
        left_frame.pack(side=LEFT, padx=(0, 10), expand=True, fill=BOTH)

        # Add widgets to the left frame
        self.date_entry = self.create_labeled_entry(left_frame, "Date (YYYY-MM-DD):", Entry, 0)
        self.weight_entry = self.create_labeled_entry(left_frame, "Weight (kg):", Entry, 1)
        self.height_entry = self.create_labeled_entry(left_frame, "Height (cm):", Entry, 2)

        # Set today's date as default value
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)

        # Create a button frame to center buttons
        button_frame = Frame(left_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.create_button(button_frame, "Calculate BMI", self.calculate_bmi)
        self.result_label = Label(left_frame, text="")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)

        self.create_button(left_frame, "View Exercise Suggestions", self.show_exercise_suggestions, row=5)

        # Add BMI ranges section
        ranges_frame = Frame(left_frame)
        ranges_frame.grid(row=6, column=0, columnspan=2, pady=10)

        Label(ranges_frame, text="BMI Ranges:", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, pady=5)

        Label(ranges_frame, text="Underweight", background="white").grid(row=1, column=0, sticky=W, padx=5)
        Label(ranges_frame, text=f"Up to {BMI_UNDERWEIGHT}", background="white").grid(row=1, column=1, sticky=W, padx=5)

        Label(ranges_frame, text="Normal weight", background="lightgreen").grid(row=2, column=0, sticky=W, padx=5)
        Label(ranges_frame, text=f"From {BMI_UNDERWEIGHT+0.1} to {BMI_NORMAL}", background="lightgreen").grid(row=2, column=1, sticky=W, padx=5)

        Label(ranges_frame, text="Overweight", background="orange").grid(row=3, column=0, sticky=W, padx=5)
        Label(ranges_frame, text=f"From {BMI_NORMAL+0.1} to {BMI_OVERWEIGHT}", background="orange").grid(row=3, column=1, sticky=W, padx=5)

        Label(ranges_frame, text="Obese", background="brown1").grid(row=4, column=0, sticky=W, padx=5)
        Label(ranges_frame, text=f"From {BMI_OVERWEIGHT+0.1}+", background="brown1").grid(row=4, column=1, sticky=W, padx=5)

        # Right frame for calendar
        right_frame = Frame(content_frame)
        right_frame.pack(side=RIGHT, padx=(10, 0), fill=BOTH)

        # Add calendar to the right frame
        self.calendar = Calendar(right_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack(fill=BOTH)

        # Set the calendar to today's date
        self.calendar.selection_set(datetime.date.today())

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

        # Dropdown for date range selection
        self.date_range_var = StringVar()
        self.date_range_var.set("Last 7 Days")  # Set the default value

        # Options list
        options = ["Last 7 Days", "Last 7 Days", "Last 2 Weeks", "Last 3 Weeks", "Last Month", "Last 3 Months", "Last 6 Months", "Last Year"]

        # Create OptionMenu
        self.date_range_menu = OptionMenu(chart_frame, self.date_range_var, *options)
        self.date_range_menu.pack(pady=10)

        # Radio buttons for graph type
        self.graph_type_var = StringVar()
        self.graph_type_var.set("Line")  # Default graph type

        line_radio = Radiobutton(chart_frame, text="Line Graph", variable=self.graph_type_var, value="Line", command=self.update_chart)
        line_radio.pack(anchor=W)

        bar_radio = Radiobutton(chart_frame, text="Bar Graph", variable=self.graph_type_var, value="Bar", command=self.update_chart)
        bar_radio.pack(anchor=W)

        # Create figure and canvas for plotting
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=BOTH)

        # Bind the dropdown selection to update the chart
        self.date_range_var.trace("w", self.update_chart)

        self.update_history()
        self.update_chart()  # Initial chart update


    def create_labeled_entry(self, parent, text, widget_type, row):
        Label(parent, text=text).grid(row=row, column=0, sticky=W)
        entry = widget_type(parent)
        entry.grid(row=row, column=1, sticky=W)
        return entry

    def create_button(self, parent, text, command, row=None, expand=False):
        button = Button(parent, text=text, command=command)
        if row is not None:
            button.grid(row=row, column=0, columnspan=2)
        else:
            button.pack(expand=expand)
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

    def set_item_color(self, item, interpretation):
        color_map = {
            "Underweight": "white",
            "Normal weight": "lightgreen",
            "Overweight": "orange",
            "Obese": "brown1"
        }
        color = color_map.get(interpretation, "white")  # Default to white if interpretation is unknown
        self.history_tree.item(item, tags=(color,))
        self.history_tree.tag_configure(color, background=color)
    
    def update_history(self):
        # Clear existing entries in the history tree
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)

        # Iterate over the sorted BMI data entries
        for date, entry in sorted(self.calculator.bmi_data.items(), key=lambda x: x[0]):
            item = self.history_tree.insert("", "end", values=(date, entry["bmi"], entry["interpretation"]))
            self.set_item_color(item, entry["interpretation"])

    def remove_entry(self):
        selected_item = self.history_tree.selection()
        if selected_item:
            date_str = self.history_tree.item(selected_item)['values'][0]
            if self.calculator.remove_bmi_entry(date_str):
                self.update_history()
                self.update_chart()
                messagebox.showinfo("Success", "Entry removed successfully.")
            else:
                messagebox.showerror("Error", "Failed to remove entry.")
        else:
            messagebox.showwarning("Warning", "Please select an entry to remove.")
            
    # The following section shows the visual representation of BMI over time in the form of a graph
    def update_chart(self, *args):
        self.ax.clear()  # Clear previous chart

        # Define the colors for different BMI ranges
        underweight_color = "white"
        normal_color = "lightgreen"
        overweight_color = "orange"
        obese_color = "#FF6347"

        # Draw color backgrounds for BMI ranges
        self.ax.axhspan(0, BMI_UNDERWEIGHT, facecolor=underweight_color, alpha=0.3, label='Underweight')
        self.ax.axhspan(BMI_UNDERWEIGHT, BMI_NORMAL, facecolor=normal_color, alpha=0.3, label='Normal weight')
        self.ax.axhspan(BMI_NORMAL, BMI_OVERWEIGHT, facecolor=overweight_color, alpha=0.3, label='Overweight')
        self.ax.axhspan(BMI_OVERWEIGHT, max(50, max(self.calculator.bmi_data.values(), key=lambda x: x["bmi"])["bmi"] + 1), 
                        facecolor=obese_color, alpha=0.3, label='Obese')

        # Convert the date strings from the BMI data entries into datetime objects for plotting
        dates = []
        bmis = []

        # Iterate over the sorted BMI data entries and fill dates and bmis lists
        for date, entry in sorted(self.calculator.bmi_data.items()):
            dates.append(datetime.datetime.strptime(date, "%Y-%m-%d"))
            bmis.append(entry['bmi'])

        # Check if there is any data to plot
        if not dates:
            self.ax.set_title('BMI Trend')
            self.ax.set_xlabel('Date')
            self.ax.set_ylabel('BMI')
            self.ax.grid(True)
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.canvas.draw()
            return

        # Filter data based on selected date range
        selected_range = self.date_range_var.get()
        end_date = max(dates)
        start_date = None

        if selected_range == "Last 7 Days":
            start_date = end_date - datetime.timedelta(days=7)
        elif selected_range == "Last 2 Weeks":
            start_date = end_date - datetime.timedelta(days=14)
        elif selected_range == "Last 3 Weeks":
            start_date = end_date - datetime.timedelta(days=21)
        elif selected_range == "Last Month":
            start_date = end_date - datetime.timedelta(days=30)
        elif selected_range == "Last 3 Months":
            start_date = end_date - datetime.timedelta(days=90)
        elif selected_range == "Last 6 Months":
            start_date = end_date - datetime.timedelta(days=180)
        elif selected_range == "Last Year":
            start_date = end_date - datetime.timedelta(days=365)

        # Filter data to include only entries within the selected range
        filtered_dates = [date for date in dates if start_date <= date <= end_date]
        filtered_bmis = [bmis[dates.index(date)] for date in filtered_dates]

        if not filtered_dates:
            self.ax.set_title('BMI Trend')
            self.ax.set_xlabel('Date')
            self.ax.set_ylabel('BMI')
            self.ax.grid(True)
            self.ax.set_xticks([])  # Remove x-axis ticks if there's no filtered data
            self.ax.set_yticks([])  # Remove y-axis ticks if there's no filtered data
            self.canvas.draw()
            return

        # Determine the type of graph to plot
        plot_type = self.graph_type_var.get()  # Assume plot_type_var is a StringVar holding the plot type

        # Plotting
        if plot_type == "Line":
            self.ax.plot(filtered_dates, filtered_bmis, marker='o')
        elif plot_type == "Bar":
            self.ax.bar(filtered_dates, filtered_bmis, width=0.5, color='skyblue')

        # Set labels and title
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('BMI')
        self.ax.set_title('BMI Trend')
        self.ax.grid(True)

        # Determine the range of dates to adjust tick frequency
        date_range = (max(filtered_dates) - min(filtered_dates)).days

        if date_range <= 7:
            self.ax.xaxis.set_major_locator(mdates.DayLocator())
        elif date_range <= 30:
            self.ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        elif date_range <= 90:
            self.ax.xaxis.set_major_locator(mdates.MonthLocator())
        else:
            self.ax.xaxis.set_major_locator(mdates.YearLocator())

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
        app = BMICalculatorGUI(new_root, username, user_manager)
        new_root.mainloop()

    login_window = LoginWindow(root, user_manager, on_login_success)
    root.mainloop()

if __name__ == "__main__":
    main()  