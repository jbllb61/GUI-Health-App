import datetime
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

# Constants for BMI classification
BMI_UNDERWEIGHT = 18.5
BMI_NORMAL = 25.0
BMI_OVERWEIGHT = 30.0
BMI_DECIMAL_PLACES = 1

class BMICalculator:
    def __init__(self):
        self.bmi_data = []
        self.data_file = "bmi_data.json"
        self.load_data()

    def calculate_bmi(self, weight, height):
        """Calculate BMI given weight (kg) and height (cm)."""
        return weight / ((height / 100) ** 2)

    def interpret_bmi(self, bmi):
        """Interpret BMI value and return corresponding category."""
        if bmi < BMI_UNDERWEIGHT:
            return "Underweight"
        elif BMI_UNDERWEIGHT <= bmi < BMI_NORMAL:
            return "Normal weight"
        elif BMI_NORMAL <= bmi < BMI_OVERWEIGHT:
            return "Overweight"
        else:
            return "Obese"

    def add_bmi_entry(self, date, weight, height):
        """Add a new BMI entry to the data."""
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
        self.bmi_data.sort(key=lambda x: x["date"])  # Sort entries by date
        self.save_data()
        return entry

    def remove_bmi_entry(self, index):
        """Remove a BMI entry by index."""
        if 0 <= index < len(self.bmi_data):
            del self.bmi_data[index]
            self.save_data()
            return True
        return False

    def save_data(self):
        """Save BMI data to JSON file."""
        with open(self.data_file, "w") as f:
            json.dump(self.bmi_data, f)

    def load_data(self):
        """Load BMI data from JSON file if it exists, otherwise create an empty file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                self.bmi_data = json.load(f)
        else:
            self.save_data()

class BMICalculatorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("BMI Calculator")
        self.calculator = BMICalculator()

        self.create_widgets()

    def create_widgets(self):
        """Create and arrange GUI widgets."""
        # Input Frame
        input_frame = ttk.Frame(self.master, padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(input_frame, text="Date:").grid(row=0, column=0, sticky=tk.W)
        self.date_entry = DateEntry(input_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(input_frame, text="Weight (kg):").grid(row=1, column=0, sticky=tk.W)
        self.weight_entry = ttk.Entry(input_frame)
        self.weight_entry.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(input_frame, text="Height (cm):").grid(row=2, column=0, sticky=tk.W)
        self.height_entry = ttk.Entry(input_frame)
        self.height_entry.grid(row=2, column=1, sticky=tk.W)

        ttk.Button(input_frame, text="Calculate BMI", command=self.calculate_bmi).grid(row=3, column=0, columnspan=2)

        # Result Frame
        result_frame = ttk.Frame(self.master, padding="10")
        result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.result_label = ttk.Label(result_frame, text="")
        self.result_label.grid(row=0, column=0, sticky=tk.W)

        # History Frame
        history_frame = ttk.Frame(self.master, padding="10")
        history_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.history_tree = ttk.Treeview(history_frame, columns=("Date", "BMI", "Interpretation"), show="headings")
        self.history_tree.heading("Date", text="Date")
        self.history_tree.heading("BMI", text="BMI")
        self.history_tree.heading("Interpretation", text="Interpretation")
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Button(history_frame, text="Remove Selected", command=self.remove_entry).grid(row=1, column=0)

        self.update_history()

    def calculate_bmi(self):
        """Calculate BMI based on user input and update the result and history."""
        try:
            date = self.date_entry.get_date()
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())

            entry = self.calculator.add_bmi_entry(date, weight, height)
            self.result_label.config(text=f"BMI: {entry['bmi']} - {entry['interpretation']}")
            self.update_history()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid weight and height values.")

    def update_history(self):
        """Update the history treeview with the latest BMI data."""
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)
        for entry in self.calculator.bmi_data:
            self.history_tree.insert("", "end", values=(entry["date"], entry["bmi"], entry["interpretation"]))

    def remove_entry(self):
        """Remove the selected entry from the history."""
        selected_item = self.history_tree.selection()
        if selected_item:
            index = self.history_tree.index(selected_item)
            if self.calculator.remove_bmi_entry(index):
                self.update_history()
                messagebox.showinfo("Success", "Entry removed successfully.")
            else:
                messagebox.showerror("Error", "Failed to remove entry.")
        else:
            messagebox.showwarning("Warning", "Please select an entry to remove.")

def main():
    """Main function to run the BMI Calculator application."""
    root = tk.Tk()
    app = BMICalculatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()