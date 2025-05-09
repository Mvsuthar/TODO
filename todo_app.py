import os
import json
import tkinter as tk
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
from PIL import Image, ImageTk
from tkcalendar import Calendar
import time

# Set appearance mode and default theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set window title and properties
        self.title("TODO App")
        self.geometry("1000x700")  # Increased width for calendar view
        self.minsize(850, 600)  # Increased minimum size
        
        # Override system date for testing if needed
        # This is specifically to fix issues with calendar functions
        # showing dates in 2025 instead of the current year
        self.current_time = datetime.now()
        
        # Initialize variables
        self.tasks = []
        self.selected_index = None
        self.data_file = "tasks.json"
        self.current_filter = "All"
        
        # Create assets folder if it doesn't exist
        if not os.path.exists("assets"):
            os.makedirs("assets")
        
        # Load tasks from file
        self.load_tasks()
        
        # Create layout
        self.create_ui()
        self.update_task_list()
        
        # Flag to track if calendar view is showing
        self.calendar_view_showing = False
        self.calendar_frame = None
        
    def create_ui(self):
        # Main grid configuration
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Main content
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)  # Updated to account for new button
        
        # App logo/title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="TODO", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Filter buttons in sidebar
        self.filter_all = ctk.CTkButton(
            self.sidebar_frame, 
            text="All Tasks",
            command=lambda: self.filter_tasks("All"),
            fg_color="transparent", 
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            height=40,
            anchor="w"
        )
        self.filter_all.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.filter_active = ctk.CTkButton(
            self.sidebar_frame, 
            text="Active Tasks",
            command=lambda: self.filter_tasks("Active"),
            fg_color="transparent", 
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            height=40,
            anchor="w"
        )
        self.filter_active.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.filter_completed = ctk.CTkButton(
            self.sidebar_frame, 
            text="Completed Tasks",
            command=lambda: self.filter_tasks("Completed"),
            fg_color="transparent", 
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            height=40,
            anchor="w"
        )
        self.filter_completed.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        # Calendar view button - Change to toggle
        self.calendar_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Calendar View",
            command=self.toggle_calendar_view,
            fg_color="transparent", 
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            height=40,
            anchor="w"
        )
        self.calendar_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        # Appearance mode settings at bottom of sidebar
        self.appearance_label = ctk.CTkLabel(
            self.sidebar_frame, text="Appearance:", anchor="w"
        )
        self.appearance_label.grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.appearance_option = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["System", "Light", "Dark"],
            command=self.change_appearance_mode
        )
        self.appearance_option.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Main content frame - container for both task view and calendar view
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Task view frame - this will be the default view
        self.task_view_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.task_view_frame.grid(row=0, column=0, sticky="nsew")
        self.task_view_frame.grid_columnconfigure(0, weight=1)
        self.task_view_frame.grid_rowconfigure(1, weight=1)
        
        # Header with filter label and task entry
        self.header_frame = ctk.CTkFrame(self.task_view_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=0)
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        self.filter_label = ctk.CTkLabel(
            self.header_frame, 
            text="All Tasks", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.filter_label.grid(row=0, column=0, sticky="w")
        
        # Task entry and add button
        self.entry_frame = ctk.CTkFrame(self.task_view_frame, fg_color="transparent") 
        self.entry_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="new")
        self.entry_frame.grid_columnconfigure(0, weight=1)
        
        self.task_entry = ctk.CTkEntry(
            self.entry_frame, 
            placeholder_text="Add new task...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.task_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.task_entry.bind("<Return>", lambda event: self.add_task())
        
        self.due_date_button = ctk.CTkButton(
            self.entry_frame,
            text="Set Due Date",
            width=100,
            command=self.select_due_date
        )
        self.due_date_button.grid(row=0, column=1, padx=5)
        
        self.add_button = ctk.CTkButton(
            self.entry_frame, 
            text="Add Task", 
            width=100,
            command=self.add_task
        )
        self.add_button.grid(row=0, column=2)
        
        # Selected due date label
        self.due_date_label = ctk.CTkLabel(
            self.entry_frame,
            text="No due date selected",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.due_date_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Store the selected due date
        self.selected_due_date = None
        
        # Task list frame
        self.task_frame = ctk.CTkScrollableFrame(
            self.task_view_frame, 
            fg_color="transparent", 
            corner_radius=0
        )
        self.task_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.task_frame.grid_columnconfigure(0, weight=1)
        
        # Footer with action buttons
        self.footer_frame = ctk.CTkFrame(self.task_view_frame, fg_color="transparent")
        self.footer_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.clear_completed_button = ctk.CTkButton(
            self.footer_frame, 
            text="Clear Completed", 
            command=self.clear_completed,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "gray90")
        )
        self.clear_completed_button.pack(side="right", padx=5)
        
        self.delete_button = ctk.CTkButton(
            self.footer_frame, 
            text="Delete Task", 
            command=self.delete_task,
            fg_color="#E53935",
            hover_color="#C62828"
        )
        self.delete_button.pack(side="right", padx=5)
        
        self.edit_button = ctk.CTkButton(
            self.footer_frame, 
            text="Edit Task", 
            command=self.edit_task
        )
        self.edit_button.pack(side="right", padx=5)
        
    def load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []
        else:
            self.tasks = []
    
    def save_tasks(self):
        with open(self.data_file, "w") as f:
            json.dump(self.tasks, f)
    
    def update_task_list(self):
        # Clear current tasks in the UI
        for widget in self.task_frame.winfo_children():
            widget.destroy()
        
        # Get filtered tasks
        filtered_tasks = self.get_filtered_tasks()
        
        # If there are no tasks, show a message
        if not filtered_tasks:
            no_tasks_label = ctk.CTkLabel(
                self.task_frame,
                text=f"No {self.current_filter.lower()} tasks to display",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_tasks_label.grid(row=0, column=0, pady=20)
            return
        
        # Add tasks to the UI
        for i, task in enumerate(filtered_tasks):
            task_id = task["id"]
            task_frame = ctk.CTkFrame(self.task_frame, corner_radius=6, fg_color=("gray90", "gray20"))
            task_frame.grid(row=i, column=0, sticky="ew", pady=5)
            task_frame.grid_columnconfigure(1, weight=1)
            
            # Store task ID directly in the frame for easier retrieval
            task_frame.task_id = task_id
            
            # Add click event to select task
            task_frame.bind("<Button-1>", self.on_task_click)
            
            # Checkbox for task completion
            check_var = tk.BooleanVar(value=task["completed"])
            checkbox = ctk.CTkCheckBox(
                task_frame, 
                text="",
                variable=check_var,
                command=lambda tid=task_id, var=check_var: self.toggle_task(tid, var.get()),
                width=20,
                checkbox_width=20,
                checkbox_height=20
            )
            checkbox.grid(row=0, column=0, padx=10, pady=10)
            
            # Task info frame (contains text and due date)
            task_info_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
            task_info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
            task_info_frame.grid_columnconfigure(0, weight=1)
            
            # Also bind the click event to the task info frame and store task ID
            task_info_frame.task_id = task_id
            task_info_frame.bind("<Button-1>", self.on_task_click)
            
            # Task text
            task_text = ctk.CTkLabel(
                task_info_frame, 
                text=task["text"],
                font=ctk.CTkFont(size=14),
                wraplength=400,
                justify="left",
                anchor="w"
            )
            if task["completed"]:
                task_text.configure(text_color="gray")
            task_text.grid(row=0, column=0, sticky="w")
            
            # Bind click event to the task text label as well and store task ID
            task_text.task_id = task_id
            task_text.bind("<Button-1>", self.on_task_click)
            
            # Due date (if present)
            if task.get("due_date"):
                due_date_str = self.format_date(task["due_date"])
                due_date_label = ctk.CTkLabel(
                    task_info_frame,
                    text=f"Due: {due_date_str}",
                    font=ctk.CTkFont(size=12),
                    text_color="#E67E22"  # Orange color for due dates
                )
                due_date_label.grid(row=1, column=0, sticky="w", pady=(2, 0))
            
            # Created date label
            date_text = self.format_date(task["date"])
            date_label = ctk.CTkLabel(
                task_frame, 
                text=date_text,
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            date_label.grid(row=0, column=2, padx=10, pady=10)
            
    def format_date(self, date_str):
        try:
            date = datetime.fromisoformat(date_str)
            return date.strftime("%b %d, %Y")
        except:
            return ""
            
    def add_task(self):
        text = self.task_entry.get().strip()
        if text:
            task = {
                "id": self.generate_id(),
                "text": text,
                "completed": False,
                "date": self.current_time.isoformat(),
                "due_date": self.selected_due_date
            }
            self.tasks.append(task)
            self.save_tasks()
            self.task_entry.delete(0, "end")
            
            # Reset due date
            self.selected_due_date = None
            self.due_date_label.configure(text="No due date selected")
            
            self.update_task_list()
            
            # Also refresh calendar view if it's showing
            if self.calendar_view_showing and hasattr(self, 'calendar_frame') and self.calendar_frame:
                # Use after to avoid refreshing in the middle of widget operations
                self.after(100, self.refresh_calendar_view)
    
    def generate_id(self):
        # Use our application's current_time to ensure consistency
        return self.current_time.strftime("%Y%m%d%H%M%S%f")
    
    def toggle_task(self, task_id, completed):
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = completed
                self.save_tasks()
                self.update_task_list()
                
                # Also refresh calendar view if it's showing
                if self.calendar_view_showing and hasattr(self, 'calendar_frame') and self.calendar_frame:
                    # Use after to avoid refreshing in the middle of widget operations
                    self.after(100, self.refresh_calendar_view)
                break
    
    def on_task_click(self, event):
        """Handle click on any part of a task"""
        # Get the widget that was clicked
        widget = event.widget
        
        # Get task ID from the widget or its parent
        task_id = getattr(widget, 'task_id', None)
        
        # If widget doesn't have task_id, try to get it from parent
        if task_id is None and hasattr(widget, 'master'):
            task_id = getattr(widget.master, 'task_id', None)
        
        # If we found a task ID, select the task
        if task_id:
            self.select_task(task_id)
    
    def select_task(self, task_id):
        """Select a task and highlight it"""
        self.selected_index = task_id
        
        # Reset all frames to default color
        for widget in self.task_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.configure(fg_color=("gray90", "gray20"))
                
                # If this is the selected task, highlight it
                if hasattr(widget, 'task_id') and widget.task_id == task_id:
                    widget.configure(fg_color=("gray75", "gray30"))
        
        print(f"Selected task with ID: {task_id}")  # Debug output
    
    def delete_task(self):
        if self.selected_index:
            for i, task in enumerate(self.tasks):
                if task["id"] == self.selected_index:
                    del self.tasks[i]
                    self.selected_index = None
                    self.save_tasks()
                    self.update_task_list()
                    
                    # Also refresh calendar view if it's showing
                    if self.calendar_view_showing and hasattr(self, 'calendar_frame') and self.calendar_frame:
                        # Use after to avoid refreshing in the middle of widget operations
                        self.after(100, self.refresh_calendar_view)
                    break
        else:
            messagebox.showinfo("Info", "Please select a task to delete")
    
    def edit_task(self):
        if not self.selected_index:
            messagebox.showinfo("Info", "Please select a task to edit")
            return
            
        # Find the selected task
        selected_task = None
        for task in self.tasks:
            if task["id"] == self.selected_index:
                selected_task = task
                break
                
        if not selected_task:
            messagebox.showinfo("Error", "Selected task not found")
            return
            
        # Create edit window
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Task")
        edit_window.geometry("400x300")  # Increased height to accommodate due date
        edit_window.resizable(False, False)
        edit_window.grab_set()  # Make the window modal
        
        edit_window.grid_columnconfigure(0, weight=1)
        
        # Task text entry
        task_label = ctk.CTkLabel(edit_window, text="Task:")
        task_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
        
        task_entry = ctk.CTkEntry(edit_window, width=360)
        task_entry.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
        task_entry.insert(0, selected_task["text"])
        
        # Due date section
        due_date_label = ctk.CTkLabel(edit_window, text="Due Date:")
        due_date_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        
        # Due date display and button frame
        due_date_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        due_date_frame.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="ew")
        due_date_frame.grid_columnconfigure(0, weight=1)
        
        # Format and display current due date
        if selected_task.get("due_date"):
            try:
                due_date = datetime.fromisoformat(selected_task["due_date"])
                due_date_text = due_date.strftime("%B %d, %Y")
                text_color = "#E67E22"  # Orange for due dates
            except:
                due_date_text = "No due date"
                text_color = ("gray10", "gray90")
        else:
            due_date_text = "No due date"
            text_color = ("gray10", "gray90")
        
        # Due date display
        self.edit_due_date_value = selected_task.get("due_date")  # Store the current value
        self.edit_due_date_display = ctk.CTkLabel(
            due_date_frame, 
            text=due_date_text,
            font=ctk.CTkFont(size=14),
            text_color=text_color
        )
        self.edit_due_date_display.grid(row=0, column=0, sticky="w")
        
        # Change due date button
        change_date_button = ctk.CTkButton(
            due_date_frame,
            text="Change Due Date",
            command=lambda: self.change_due_date(edit_window)
        )
        change_date_button.grid(row=0, column=1, padx=(10, 0))
        
        # Clear due date button
        clear_date_button = ctk.CTkButton(
            due_date_frame,
            text="Clear",
            width=60,
            command=lambda: self.clear_edit_due_date(edit_window),
            fg_color="#E74C3C",  # Red
            hover_color="#C0392B"
        )
        clear_date_button.grid(row=0, column=2, padx=(10, 0))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        buttons_frame.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            buttons_frame, 
            text="Cancel", 
            command=edit_window.destroy,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "gray90")
        )
        cancel_button.pack(side="left", padx=5)
        
        # Save button
        def save_edit():
            new_text = task_entry.get().strip()
            if new_text:
                selected_task["text"] = new_text
                selected_task["due_date"] = self.edit_due_date_value  # Update due date
                self.save_tasks()
                self.update_task_list()
                
                # Also refresh calendar view if it's showing
                if self.calendar_view_showing and hasattr(self, 'calendar_frame') and self.calendar_frame:
                    # Use after to avoid refreshing in the middle of widget operations
                    self.after(100, self.refresh_calendar_view)
                    
                edit_window.destroy()
        
        save_button = ctk.CTkButton(
            buttons_frame, 
            text="Save", 
            command=save_edit
        )
        save_button.pack(side="right", padx=5)
        
        task_entry.focus_set()
        
        # Center the window
        edit_window.update_idletasks()
        width = edit_window.winfo_width()
        height = edit_window.winfo_height()
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_window.winfo_screenheight() // 2) - (height // 2)
        edit_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def change_due_date(self, parent_window):
        """Open calendar to change due date in edit window"""
        due_date_window = ctk.CTkToplevel(parent_window)
        due_date_window.title("Change Due Date")
        due_date_window.geometry("350x450")  # Increased height for buttons
        due_date_window.resizable(False, False)
        due_date_window.grab_set()  # Make the window modal
        
        # Center the window
        due_date_window.update_idletasks()
        x = (due_date_window.winfo_screenwidth() // 2) - (350 // 2)
        y = (due_date_window.winfo_screenheight() // 2) - (450 // 2)
        due_date_window.geometry(f"350x450+{x}+{y}")
        
        # Title header
        header_frame = ctk.CTkFrame(due_date_window, fg_color="#3498db", corner_radius=0)
        header_frame.pack(fill="x", pady=(0, 15))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="CHANGE DUE DATE",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        header_label.pack(pady=15)
        
        # Instructions
        instructions_label = ctk.CTkLabel(
            due_date_window,
            text="Choose a new due date for this task:",
            font=ctk.CTkFont(size=14)
        )
        instructions_label.pack(pady=(0, 10))
        
        # Calendar widget with default date if exists
        current_date = datetime.now()
        cal = Calendar(
            due_date_window, 
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            year=current_date.year,
            month=current_date.month,
            day=current_date.day,
            font=("Helvetica", 10),
            showweeknumbers=False,
            borderwidth=0,
            headersbackground="#3498db",
            headersforeground="white",
            selectbackground="#9b59b6",
            selectforeground="white"
        )
        
        # If there's an existing due date, select it in the calendar
        current_date_text = "None"
        if self.edit_due_date_value:
            try:
                due_date = datetime.fromisoformat(self.edit_due_date_value)
                cal.selection_set(due_date)
                current_date_text = due_date.strftime("%B %d, %Y")
            except:
                pass
                
        cal.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Selected date display
        selected_date_frame = ctk.CTkFrame(due_date_window, fg_color="transparent")
        selected_date_frame.pack(fill="x", padx=20, pady=10)
        
        selected_date_label = ctk.CTkLabel(
            selected_date_frame,
            text="Selected Date:",
            font=ctk.CTkFont(size=14)
        )
        selected_date_label.pack(side="left")
        
        # Display current selected date
        selected_date_value = ctk.CTkLabel(
            selected_date_frame,
            text=current_date_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#E67E22"
        )
        selected_date_value.pack(side="left", padx=10)
        
        # Update selected date label when user clicks a date
        def update_selected_date(event=None):
            try:
                selected_date = cal.selection_get()
                selected_date_value.configure(
                    text=selected_date.strftime("%B %d, %Y"),
                    text_color="#E67E22"
                )
            except:
                selected_date_value.configure(text="None")
        
        cal.bind("<<CalendarSelected>>", update_selected_date)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(due_date_window, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=20, padx=20)
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=due_date_window.destroy,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "gray90"),
            width=80
        )
        cancel_button.pack(side="left", padx=5)
        
        # Confirm button - larger and more prominent
        def confirm_date():
            try:
                selected_date = cal.selection_get()
                self.edit_due_date_value = datetime(
                    selected_date.year,
                    selected_date.month,
                    selected_date.day
                ).isoformat()
                
                # Update the displayed date
                self.edit_due_date_display.configure(
                    text=selected_date.strftime("%B %d, %Y"),
                    text_color="#E67E22"  # Orange color
                )
                due_date_window.destroy()
            except:
                messagebox.showwarning("Warning", "Please select a date first")
        
        confirm_button = ctk.CTkButton(
            buttons_frame,
            text="Confirm Selection",
            command=confirm_date,
            fg_color="blue",  # Green
            hover_color="green",
            width=150
        )
        confirm_button.pack(side="right", padx=5)
    
    def clear_edit_due_date(self, parent_window):
        """Clear the due date in edit window"""
        self.edit_due_date_value = None
        self.edit_due_date_display.configure(
            text="No due date",
            text_color=("gray10", "gray90")
        )
    
    def clear_completed(self):
        self.tasks = [task for task in self.tasks if not task["completed"]]
        self.save_tasks()
        self.update_task_list()
    
    def filter_tasks(self, filter_type):
        self.current_filter = filter_type
        self.filter_label.configure(text=f"{filter_type} Tasks")
        self.update_task_list()
        
        # Update sidebar button styling
        self.filter_all.configure(fg_color="transparent")
        self.filter_active.configure(fg_color="transparent")
        self.filter_completed.configure(fg_color="transparent")
        
        if filter_type == "All":
            self.filter_all.configure(fg_color=("gray75", "gray25"))
        elif filter_type == "Active":
            self.filter_active.configure(fg_color=("gray75", "gray25"))
        elif filter_type == "Completed":
            self.filter_completed.configure(fg_color=("gray75", "gray25"))
    
    def get_filtered_tasks(self):
        if self.current_filter == "All":
            return self.tasks
        elif self.current_filter == "Active":
            return [task for task in self.tasks if not task["completed"]]
        elif self.current_filter == "Completed":
            return [task for task in self.tasks if task["completed"]]
        return self.tasks
        
    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def select_due_date(self):
        """Open a calendar dialog to select a due date"""
        due_date_window = ctk.CTkToplevel(self)
        due_date_window.title("Select Due Date")
        due_date_window.geometry("350x450")  # Increased height for buttons
        due_date_window.resizable(False, False)
        due_date_window.grab_set()  # Make the window modal
        
        # Center the window
        due_date_window.update_idletasks()
        x = (due_date_window.winfo_screenwidth() // 2) - (350 // 2)
        y = (due_date_window.winfo_screenheight() // 2) - (450 // 2)
        due_date_window.geometry(f"350x450+{x}+{y}")
        
        # Title header
        header_frame = ctk.CTkFrame(due_date_window, fg_color="#3498db", corner_radius=0)
        header_frame.pack(fill="x", pady=(0, 15))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="SELECT DUE DATE",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        header_label.pack(pady=15)
        
        # Instructions
        instructions_label = ctk.CTkLabel(
            due_date_window,
            text="Choose a date for your task:",
            font=ctk.CTkFont(size=14)
        )
        instructions_label.pack(pady=(0, 10))
        
        # Calendar widget
        current_date = datetime.now()
        cal = Calendar(
            due_date_window, 
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            year=current_date.year,
            month=current_date.month,
            day=current_date.day,
            font=("Helvetica", 10),
            showweeknumbers=False,
            borderwidth=0,
            headersbackground="#3498db",
            headersforeground="white",
            selectbackground="#9b59b6",
            selectforeground="white"
        )
        cal.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Selected date display
        selected_date_frame = ctk.CTkFrame(due_date_window, fg_color="transparent")
        selected_date_frame.pack(fill="x", padx=20, pady=10)
        
        selected_date_label = ctk.CTkLabel(
            selected_date_frame,
            text="Selected Date:",
            font=ctk.CTkFont(size=14)
        )
        selected_date_label.pack(side="left")
        
        # Display current selected date
        selected_date_value = ctk.CTkLabel(
            selected_date_frame,
            text="None",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#E67E22"
        )
        selected_date_value.pack(side="left", padx=10)
        
        # Update selected date label when user clicks a date
        def update_selected_date(event=None):
            try:
                selected_date = cal.selection_get()
                selected_date_value.configure(
                    text=selected_date.strftime("%B %d, %Y"),
                    text_color="#E67E22"
                )
            except:
                selected_date_value.configure(text="None")
        
        cal.bind("<<CalendarSelected>>", update_selected_date)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(due_date_window, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=20, padx=20)
        
        # Clear button
        def clear_date():
            self.selected_due_date = None
            self.due_date_label.configure(text="No due date selected")
            due_date_window.destroy()
        
        clear_button = ctk.CTkButton(
            buttons_frame,
            text="Clear",
            command=clear_date,
            fg_color="#E74C3C",  # Red
            hover_color="red",
            width=80
        )
        clear_button.pack(side="left", padx=5)
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=due_date_window.destroy,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "gray90"),
            width=80
        )
        cancel_button.pack(side="left", padx=5)
        
        # Confirm button - larger and more prominent
        def confirm_date():
            try:
                selected_date = cal.selection_get()
                self.selected_due_date = datetime(
                    selected_date.year,
                    selected_date.month,
                    selected_date.day
                ).isoformat()
                self.due_date_label.configure(
                    text=f"Due date: {selected_date.strftime('%b %d, %Y')}",
                    text_color="#E67E22"  # Orange color
                )
                due_date_window.destroy()
            except:
                messagebox.showwarning("Warning", "Please select a date first")
        
        confirm_button = ctk.CTkButton(
            buttons_frame,
            text="Confirm Selection",
            command=confirm_date,
            fg_color="blue",  # Green
            hover_color="green",
            width=150
        )
        confirm_button.pack(side="right", padx=5)
    
    def toggle_calendar_view(self):
        """Toggle between task view and calendar view"""
        if self.calendar_view_showing:
            # Hide calendar frame first
            if self.calendar_frame:
                self.calendar_frame.grid_forget()
            
            # Show task view
            self.task_view_frame.grid(row=0, column=0, sticky="nsew")
            self.calendar_button.configure(text="Calendar View")
            self.calendar_view_showing = False
        else:
            # Hide task view first
            self.task_view_frame.grid_forget()
            
            # Show or create calendar view
            self.open_calendar_view()
            self.calendar_button.configure(text="Task View")
            self.calendar_view_showing = True

    def open_calendar_view(self):
        """Create or show the calendar view in the main window"""
        try:
            # If the calendar frame already exists, just show it
            if self.calendar_frame:
                self.calendar_frame.grid(row=0, column=0, sticky="nsew")
                return
            
            # Create a new calendar frame in the main window
            self.calendar_frame = ctk.CTkFrame(self.main_frame)
            self.calendar_frame.grid(row=0, column=0, sticky="nsew")
            
            # Header with title
            header_frame = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=(20, 10))
            
            calendar_title = ctk.CTkLabel(
                header_frame,
                text="CALENDAR VIEW",
                font=ctk.CTkFont(size=26, weight="bold"),
            )
            calendar_title.pack(side="left", padx=20)
            
            today_str = self.current_time.strftime("%A, %B %d, %Y")
            today_label = ctk.CTkLabel(
                header_frame,
                text=f"Today: {today_str}",
                font=ctk.CTkFont(size=14),
                text_color=("gray50", "gray70")
            )
            today_label.pack(side="right", padx=20)
            
            # Main content with calendar and sidebar
            content_frame = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=20, pady=10)
            content_frame.grid_columnconfigure(0, weight=0, minsize=250)
            content_frame.grid_columnconfigure(1, weight=1)
            content_frame.grid_rowconfigure(0, weight=1)
            
            # Calendar navigation sidebar
            sidebar = ctk.CTkFrame(content_frame, corner_radius=10)
            sidebar.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
            
            # Month display in blue box
            month_box = ctk.CTkFrame(sidebar, fg_color="#3498db", corner_radius=8)
            month_box.pack(fill="x", padx=10, pady=10)
            
            # Current month/year
            current_month = self.current_time.strftime("%B %Y")
            self.month_label = ctk.CTkLabel(
                month_box,
                text=current_month,
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="white"
            )
            self.month_label.pack(pady=15)
            
            # Navigation buttons
            nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
            nav_frame.pack(fill="x", padx=10, pady=10)
            
            prev_month_btn = ctk.CTkButton(
                nav_frame, 
                text="← Previous Month", 
                command=lambda: self.calendar_change_month(-1),
                fg_color="#2ecc71",
                hover_color="#27ae60",
                text_color="white",
                corner_radius=8,
                height=36
            )
            prev_month_btn.pack(fill="x", pady=(0, 5))
            
            next_month_btn = ctk.CTkButton(
                nav_frame, 
                text="Next Month →", 
                command=lambda: self.calendar_change_month(1),
                fg_color="#2ecc71",
                hover_color="#27ae60",
                text_color="white",
                corner_radius=8,
                height=36
            )
            next_month_btn.pack(fill="x", pady=(5, 0))
            
            # Today button
            today_btn = ctk.CTkButton(
                sidebar, 
                text="Jump to Today", 
                command=self.calendar_go_to_today,
                fg_color="#9b59b6",
                hover_color="#8e44ad",
                text_color="white",
                corner_radius=8,
                height=40
            )
            today_btn.pack(fill="x", padx=10, pady=10)
            
            # Refresh button
            refresh_btn = ctk.CTkButton(
                sidebar, 
                text="↻ Refresh Tasks", 
                command=self.refresh_calendar_view,
                fg_color="#e67e22",  # Orange
                hover_color="#d35400",
                text_color="white",
                corner_radius=8,
                height=40
            )
            refresh_btn.pack(fill="x", padx=10, pady=10)
            
            # Create the calendar widget
            cal_frame = ctk.CTkFrame(content_frame, corner_radius=10)
            cal_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
            
            # Custom styling for calendar
            cal_style = {
                'headersbackground': "#3498db",
                'headersforeground': "white",
                'weekendbackground': '#f5f5f5',
                'weekendforeground': "#2c3e50",
                'othermonthbackground': '#f0f0f0',
                'othermonthforeground': "gray70",
                'background': 'white',
                'foreground': "#2c3e50",
                'bordercolor': "#3498db",
                'selectbackground': "#9b59b6",
                'selectforeground': "white",
            }
            
            # Force year to be 2025 to match system date
            system_year = self.current_time.year
            system_month = self.current_time.month
            system_day = self.current_time.day  # Explicitly set to 5th
            
            # Store current calendar date
            self.calendar_year = system_year
            self.calendar_month = system_month
            self.calendar_day = system_day
            
            # Set month display correctly
            current_month = datetime(system_year, system_month, 1).strftime("%B %Y")
            self.month_label.configure(text=current_month)
            
            # Create Calendar widget - ensure the month matches our stored month
            self.calendar_widget = Calendar(
                cal_frame, 
                selectmode='day',
                year=system_year,
                month=system_month,
                day=system_day,
                showweeknumbers=False,
                firstweekday='sunday',
                font=('Helvetica', 11),
                **cal_style
            )
            self.calendar_widget.pack(fill="both", expand=True, padx=15, pady=15)
            
            # Bind date selection event
            self.calendar_widget.bind("<<CalendarSelected>>", self.on_calendar_date_selected)
            
            # Tasks for selected date
            tasks_frame = ctk.CTkFrame(self.calendar_frame, corner_radius=10)
            tasks_frame.pack(fill="x", padx=20, pady=10)
            
            # Selected date header
            date_str = datetime(system_year, system_month, system_day).strftime("%A, %B %d, %Y")
            tasks_header = ctk.CTkFrame(tasks_frame, fg_color="#3498db", corner_radius=8)
            tasks_header.pack(fill="x", padx=10, pady=10)
            
            self.selected_date_label = ctk.CTkLabel(
                tasks_header, 
                text=f"Tasks for {date_str}",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            self.selected_date_label.pack(pady=12)
            
            # Tasks list for selected date
            self.calendar_tasks_frame = ctk.CTkScrollableFrame(
                tasks_frame, 
                fg_color="transparent",
                height=150
            )
            self.calendar_tasks_frame.pack(fill="x", padx=10, pady=10, expand=False)
            
            # Show tasks for the current date
            self.show_calendar_tasks(datetime(system_year, system_month, system_day))
            
            print("Calendar view created in main window")
        except Exception as e:
            print(f"Error creating calendar view: {e}")
            messagebox.showerror("Error", "Could not create calendar view. Please check console for details.")

    def calendar_change_month(self, delta):
        """Change the displayed month in the calendar by delta months"""
        try:
            # Calculate new month and year
            new_month = self.calendar_month + delta
            new_year = self.calendar_year
            
            # Handle year changes
            if new_month > 12:
                new_month = 1
                new_year += 1
            elif new_month < 1:
                new_month = 12
                new_year -= 1
            
            # Update internal tracking
            self.calendar_month = new_month
            self.calendar_year = new_year
            
            # Create a date object for the 1st of the new month
            first_day = datetime(new_year, new_month, 1)
            
            # Update the month label in the sidebar
            month_name = first_day.strftime("%B %Y")
            self.month_label.configure(text=month_name)
            
            # Set a date in the new month to force calendar to update
            self.calendar_widget.selection_set(first_day)
            
            # Simplest approach - remove and recreate the calendar
            try:
                # Store the parent frame
                parent_frame = self.calendar_widget.master
                
                # Save style settings
                style_settings = {
                    'selectbackground': self.calendar_widget.cget('selectbackground'),
                    'selectforeground': self.calendar_widget.cget('selectforeground'),
                    'headersbackground': self.calendar_widget.cget('headersbackground'),
                    'headersforeground': self.calendar_widget.cget('headersforeground')
                }
                
                # Remove the old calendar
                self.calendar_widget.destroy()
                
                # Create a new calendar with the new month/year
                self.calendar_widget = Calendar(
                    parent_frame, 
                    selectmode='day',
                    year=new_year,
                    month=new_month,
                    day=1,
                    showweeknumbers=False,
                    firstweekday='sunday',
                    font=('Helvetica', 11),
                    **style_settings
                )
                self.calendar_widget.pack(fill="both", expand=True, padx=15, pady=15)
                
                # Rebind the date selection event
                self.calendar_widget.bind("<<CalendarSelected>>", self.on_calendar_date_selected)
                
                # Update task display
                self.show_calendar_tasks(first_day)
            except Exception as e:
                print(f"Error recreating calendar: {e}")
            
            print(f"Calendar navigated to {month_name}")
        except Exception as e:
            print(f"Error changing calendar month: {e}")
    
    def calendar_go_to_today(self):
        """Set the calendar to today's date"""
        try:
            # Force today to be May 5, 2025
            system_year = self.current_time.year
            system_month = self.current_time.month  # Use Month 5 (May) for today
            system_day = self.current_time.day  # Explicitly set to 5th
            
            today = datetime(system_year, system_month, system_day)
            
            # Update internal tracking
            self.calendar_year = system_year
            self.calendar_month = system_month
            self.calendar_day = system_day
            
            # Update the month label
            month_name = today.strftime("%B %Y")
            self.month_label.configure(text=month_name)
            
            # Store the parent frame
            parent_frame = self.calendar_widget.master
            
            # Save style settings
            style_settings = {
                'selectbackground': self.calendar_widget.cget('selectbackground'),
                'selectforeground': self.calendar_widget.cget('selectforeground'),
                'headersbackground': self.calendar_widget.cget('headersbackground'),
                'headersforeground': self.calendar_widget.cget('headersforeground')
            }
            
            # Remove the old calendar
            self.calendar_widget.destroy()
            
            # Create a new calendar with today's date
            self.calendar_widget = Calendar(
                parent_frame, 
                selectmode='day',
                year=system_year,
                month=system_month,
                day=system_day,
                showweeknumbers=False,
                firstweekday='sunday',
                font=('Helvetica', 11),
                **style_settings
            )
            self.calendar_widget.pack(fill="both", expand=True, padx=15, pady=15)
            
            # Rebind the date selection event
            self.calendar_widget.bind("<<CalendarSelected>>", self.on_calendar_date_selected)
            
            # Set the selection to today
            self.calendar_widget.selection_set(today)
            
            # Update task display
            self.show_calendar_tasks(today)
            
            print(f"Calendar set to today: {today.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"Error setting calendar to today: {e}")
            # Print detailed traceback for debugging
            import traceback
            traceback.print_exc()
    
    def on_calendar_date_selected(self, event=None):
        """Handle date selection in the calendar"""
        try:
            # Get the selected date
            selected_date = self.calendar_widget.selection_get()
            
            # Update the task display for this date
            self.show_calendar_tasks(selected_date)
            
            print(f"Calendar date selected: {selected_date.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"Error handling calendar date selection: {e}")
    
    def show_calendar_tasks(self, date):
        """Show tasks for the selected date in the calendar view"""
        try:
            # Clear current tasks
            for widget in self.calendar_tasks_frame.winfo_children():
                widget.destroy()
            
            # Update the header
            date_str = date.strftime("%A, %B %d, %Y")
            self.selected_date_label.configure(text=f"Tasks for {date_str}")
            
            # Get tasks for this date
            date_str_iso = date.strftime("%Y-%m-%d")
            date_tasks = []
            
            for task in self.tasks:
                if "due_date" in task and task["due_date"]:
                    # Extract date part (YYYY-MM-DD)
                    task_date = task["due_date"].split("T")[0] if "T" in task["due_date"] else task["due_date"][:10]
                    if task_date == date_str_iso:
                        date_tasks.append(task)
            
            # If no tasks, show a message
            if not date_tasks:
                no_tasks_label = ctk.CTkLabel(
                    self.calendar_tasks_frame, 
                    text="No tasks for this date",
                    font=ctk.CTkFont(size=14),
                    text_color="gray"
                )
                no_tasks_label.pack(pady=20)
                return
            
            # Display tasks
            for task in date_tasks:
                task_frame = ctk.CTkFrame(
                    self.calendar_tasks_frame, 
                    corner_radius=8
                )
                task_frame.pack(fill="x", pady=5, padx=5)
                
                # Create horizontal layout
                task_inner_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
                task_inner_frame.pack(fill="x", padx=10, pady=10)
                
                # Task completion indicator
                status_color = "#2ecc71" if task["completed"] else "#e74c3c"
                status_text = "✓ Completed" if task["completed"] else "◯ Pending"
                status_frame = ctk.CTkFrame(
                    task_inner_frame, 
                    width=120,
                    corner_radius=4, 
                    fg_color=status_color
                )
                status_frame.pack(side="left", padx=(0, 10))
                
                status_label = ctk.CTkLabel(
                    status_frame,
                    text=status_text,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="white"
                )
                status_label.pack(padx=8, pady=4)
                
                # Task text
                text_container = ctk.CTkFrame(task_inner_frame, fg_color="transparent")
                text_container.pack(side="left", fill="both", expand=True)
                
                task_text = ctk.CTkLabel(
                    text_container, 
                    text=task["text"],
                    font=ctk.CTkFont(size=14),
                    wraplength=500,
                    justify="left",
                    anchor="w"
                )
                if task["completed"]:
                    task_text.configure(text_color="gray")
                task_text.pack(anchor="w")
                
                # Creation date in small text below
                if "date" in task:
                    try:
                        creation_date = datetime.fromisoformat(task["date"])
                        creation_text = f"Created: {creation_date.strftime('%b %d, %Y')}"
                        
                        date_label = ctk.CTkLabel(
                            text_container,
                            text=creation_text,
                            font=ctk.CTkFont(size=10),
                            text_color="gray"
                        )
                        date_label.pack(anchor="w")
                    except:
                        pass
                        
            print(f"Showing {len(date_tasks)} tasks for {date_str}")
        except Exception as e:
            print(f"Error showing calendar tasks: {e}")

    def refresh_calendar_view(self):
        """Refresh the calendar view to show updated task status"""
        try:
            # Only refresh if calendar view exists
            if not self.calendar_frame or not self.calendar_widget:
                return
                
            # Get currently selected date
            try:
                selected_date = self.calendar_widget.selection_get()
            except:
                # If no date is selected, use the current calendar date
                selected_date = datetime(self.calendar_year, self.calendar_month, self.calendar_day)
                
            # Reload tasks from file to ensure we have latest data
            self.load_tasks()
                
            # Update the tasks display for the selected date
            self.show_calendar_tasks(selected_date)
            
            # Show a brief confirmation
            self.flash_status_message("Tasks refreshed")
            
            print(f"Calendar view refreshed for {selected_date.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"Error refreshing calendar view: {e}")
            import traceback
            traceback.print_exc()
            
    def flash_status_message(self, message, duration=2000):
        """Show a temporary status message at the bottom of the window"""
        try:
            # Create message frame if it doesn't exist
            if not hasattr(self, 'status_frame'):
                self.status_frame = ctk.CTkFrame(self, height=30, fg_color="#3498db")
                self.status_frame.place(relx=0.5, rely=0.95, anchor="center", relwidth=0.5)
                
                self.status_label = ctk.CTkLabel(
                    self.status_frame,
                    text="",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="white"
                )
                self.status_label.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Update and show the message
            self.status_label.configure(text=message)
            self.status_frame.lift()  # Bring to front
            self.status_frame.place(relx=0.5, rely=0.95, anchor="center", relwidth=0.3)
            
            # Schedule removal
            self.after(duration, self.hide_status_message)
        except Exception as e:
            print(f"Error displaying status message: {e}")
    
    def hide_status_message(self):
        """Hide the status message"""
        if hasattr(self, 'status_frame'):
            self.status_frame.place_forget()

if __name__ == "__main__":
    print("Starting Stunning TODO application...")
    app = TodoApp()
    print("Application initialized, starting main loop...")
    app.mainloop()
    print("Application closed.") 