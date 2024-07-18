import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import psycopg2
from tkinter import messagebox

class Table:
    def __init__(self, root):
        self.root = root
        self.add_button = None

        # Load and resize images
        self.edit_icon = self.load_and_resize_image('editt.png', 25, 15)
        self.delete_icon = self.load_and_resize_image('delete.png', 20, 15)
        self.add_icon = self.load_and_resize_image('addd.png', 30, 30)
        self.addd_icon = self.load_and_resize_image('add.png', 30, 30)

        self.Insurance_icon = self.load_and_resize_image('Insurance.png', 30, 30)  # Using the add icon as a placeholder for Insurance icon

        # Connect to the database
        self.conn = psycopg2.connect(database="", user="", password="", host="", port="5432")
        self.cursor = self.conn.cursor()
        
        # Retrieve data from the "persons" table
        self.cursor.execute("SELECT * FROM Personal_Info")
        rows = self.cursor.fetchall()
        self.lst = [row for row in rows]

        # Create a Canvas widget
        self.canvas = tk.Canvas(root)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar
        self.scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        # Create a frame inside the canvas
        self.frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

        # Create table headers
        headers = ['National ID', 'First Name', 'Last Name', 'Father name', 'Postal code', 'Phone', 'Email', 'Birth_date', 'Actions', 'Insurance List']
        for j, header in enumerate(headers):
            label = ttk.Label(self.frame, text=header, style='My.TLabel')
            label.grid(row=0, column=j, sticky='we')
            label.configure(background='#c7b8e6', font=('Arial', 12, 'bold'), padding=10)
            label.configure(borderwidth=1, relief='solid')

        # Create table rows
        self.table_rows = []
        for i, row in enumerate(self.lst):
            self.create_table_row(i, row)

        # Create Add button
        self.add_button = ttk.Button(self.frame, image=self.add_icon, text='Add', command=self.add_record, padding='25 10')
        # Places the button in the new row below the last row of the table and in the last column.
        self.add_button.grid(row=len(self.lst) + 1, column=len(headers) - 1, pady=20)

        # Create info frame for displaying total and average age
        self.info_frame = ttk.Frame(self.frame)
        self.info_frame.grid(row=len(self.lst) + 2, column=0, columnspan=len(headers), pady=10)
        
        # Display total and average age
        self.display_age_info()

    def load_and_resize_image(self, path, width, height):
        """Load an image and resize it."""
        image = Image.open(path)
        image = image.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def display_age_info(self):
        """Display total and average age information at the bottom of the table."""
        query = """
        SELECT 
            SUM(EXTRACT(YEAR FROM AGE(CURRENT_DATE, Birth_Date))) AS TotalAge,
            AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, Birth_Date))) AS AverageAge
        FROM 
            Personal_Info;
        """
        self.cursor.execute(query)
        total_age, average_age = self.cursor.fetchone()

        # Clear previous age information
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        total_age_label = ttk.Label(self.info_frame, text=f'Total Age: {total_age}', style='My.TLabel')
        total_age_label.grid(row=0, column=0, padx=5, pady=5)

        average_age_label = ttk.Label(self.info_frame, text=f'Average Age: {average_age:.2f}', style='My.TLabel')
        average_age_label.grid(row=0, column=1, padx=5, pady=5)

    def create_table_row(self, i, row):
        row_widgets = []
        # Creating table cells with labels:
        for j, value in enumerate(row):
            label = ttk.Label(self.frame, text=value, style='My.TLabel')
            label.grid(row=i + 1, column=j, sticky='we')
            label.configure(font=('Arial', 10), padding=10)
            label.configure(borderwidth=1, relief='solid')
            label.configure(background='#da70d6' if j == 0 else '#e6e6fa')  # ID is in the first column
            row_widgets.append(label)

        # Create Edit and Delete buttons
        frame = ttk.Frame(self.frame)
        frame.grid(row=i + 1, column=len(row))
        edit_button = ttk.Button(frame, image=self.edit_icon, command=lambda i=i: self.edit_record(i), padding='20 0')
        edit_button.grid(row=0, column=0)
        delete_button = ttk.Button(frame, image=self.delete_icon, command=lambda i=i: self.delete_record(i), padding='20 0')
        delete_button.grid(row=1, column=0)
        row_widgets.append(frame)

        # Create Insurance List button
        frame = ttk.Frame(self.frame)
        frame.grid(row=i + 1, column=len(row) + 1)
        Insurance_list_button = ttk.Button(frame, image=self.Insurance_icon, text='Insurance List', command=lambda i=i: self.open_Insurance_list(i), padding='40 5')
        Insurance_list_button.grid(row=2, column=0)
        row_widgets.append(frame)

        self.table_rows.append(row_widgets)

    def add_record(self):
        # Create a new window
        add_window = tk.Toplevel()
        add_window.title('Add Record')

        headers = ['National ID', 'First Name', 'Last Name', 'Father name', 'Postal code', 'Phone', 'Email', 'Birth_date']
        self.entries = []

        for i, header in enumerate(headers):
            label = ttk.Label(add_window, text=header, style='My.TLabel')
            label.grid(row=i, column=0, padx=10, pady=10, sticky='w')
            entry = ttk.Entry(add_window, style='My.TEntry')
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.entries.append(entry)

        add_button = ttk.Button(add_window, text='Add', command=self.save_record)
        add_button.grid(row=len(headers), column=0, columnspan=2, pady=10)

        self.add_window = add_window

    def save_record(self):
        data = [e.get() for e in self.entries]
        data[0] = int(data[0])

        query = "INSERT INTO Personal_Info (national_id, first_name, last_name, father_name, postal_code, mobile, email, birth_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        
        try:
            self.cursor.execute(query, data)
            self.conn.commit()
            self.add_window.destroy()
            self.refresh_table()
            self.display_age_info()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror('Error', f'An error occurred while saving the record: {e}')

    def edit_record(self, index):
        edit_window = tk.Toplevel()
        edit_window.title('Edit Record')

        headers = ['National ID', 'First Name', 'Last Name', 'Father name', 'Postal code', 'Phone', 'Email', 'Birth_date']
        self.entries = []

        for i, header in enumerate(headers):
            label = ttk.Label(edit_window, text=header, style='My.TLabel')
            label.grid(row=i, column=0, padx=10, pady=10, sticky='w')
            entry = ttk.Entry(edit_window, style='My.TEntry')
            entry.grid(row=i, column=1, padx=10, pady=10)
            entry.insert(0, self.lst[index][i])
            self.entries.append(entry)

        save_button = ttk.Button(edit_window, text='Save', command=lambda: self.save_edit_record(index, edit_window))
        save_button.grid(row=len(headers), column=0, columnspan=2, pady=10)

    def save_edit_record(self, index, window=None):
        data = [e.get() for e in self.entries]
        query = "UPDATE Personal_Info SET national_id = %s, first_name = %s, last_name = %s, father_name = %s, postal_code = %s, mobile = %s, email = %s, birth_date = %s WHERE national_id = %s"
        
        try:
            self.cursor.execute(query, data + [self.lst[index][0]])
            self.conn.commit()
            if window:
                window.destroy()
            self.refresh_table()
            self.display_age_info()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror('Error', f'An error occurred while editing the record: {e}')

    def delete_record(self, index):
        query = "DELETE FROM Personal_Info WHERE national_id = %s"
        
        try:
            self.cursor.execute(query, [self.lst[index][0]])
            self.conn.commit()
            del self.lst[index]
            self.refresh_table()
            self.display_age_info()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror('Error', f'An error occurred while deleting the record: {e}')



    ####################################################################################################
    def open_Insurance_list(self, index):
        person_id = self.lst[index][0]
        Insurance_window = tk.Toplevel()
        Insurance_window.title('Insurance List')

        query = """
            SELECT 
                iai.Insurance_ID,
                pi.first_Name,
                pi.last_name,
                iai.Insurance_Type,
                iai.Account_Number,
                iai.Bank_Name,
                iai.Branch_Name,
                iai.Branch_Code
            FROM 
                Personal_Info pi
            JOIN 
                Insurance_Account_Info iai 
            ON 
                pi.National_ID = iai.National_ID
            WHERE 
                pi.National_ID = %s
            """
        
        try:
            self.cursor.execute(query, (person_id,))
            Insurance_rows = self.cursor.fetchall()
            self.Insurance_rows = [row for row in Insurance_rows]

            Insurance_headers = ['Insurance ID','First Name', 'Last Name ', 'Insurance Type', 'Account_Number','Bank_Name','Branch_Name','Branch_Code', 'Actions']
            for j, header in enumerate(Insurance_headers):
                label = ttk.Label(Insurance_window, text=header, style='My.TLabel')
                label.grid(row=0, column=j, sticky='we')
                label.configure(background='#86c5e4', font=('Arial', 12, 'bold'), padding=10)
                label.configure(borderwidth=1, relief='solid')

            for i, row in enumerate(self.Insurance_rows):
                for j, value in enumerate(row):
                    label = ttk.Label(Insurance_window, text=value, style='My.TLabel')
                    label.grid(row=i + 1, column=j, sticky='we')
                    label.configure(font=('Arial', 10), padding=10)
                    label.configure(borderwidth=1, relief='solid')
                    label.configure(background='#7a90e0' if j == 0 else '#e0eaff')

                frame = ttk.Frame(Insurance_window)
                frame.grid(row=i + 1, column=len(Insurance_headers) - 1)
                edit_button = ttk.Button(frame, image=self.edit_icon, text='Edit', command=lambda i=i: self.edit_Insurance(i, person_id, Insurance_window), padding='30 0')
                edit_button.grid(row=0, column=0)
                delete_button = ttk.Button(frame, image=self.delete_icon, text='Delete', command=lambda i=i: self.delete_Insurance(i, person_id, Insurance_window), padding='30 0')
                delete_button.grid(row=1, column=0)

            add_button = ttk.Button(Insurance_window, image=self.addd_icon, text='Add', command=lambda: self.add_Insurance(person_id, Insurance_window), padding='10 5')
            add_button.grid(row=len(Insurance_rows) + 1, column=len(Insurance_headers) - 1, pady=20)
        except Exception as e:
            self.conn.rollback()


    def add_Insurance(self, person_id, window):
        add_Insurance_window = tk.Toplevel()
        add_Insurance_window.title('Add Insurance')

        headers = ['Insurance Type', 'Account_Number','Bank_Name','Branch_Name','Branch_Code']
        self.Insurance_entries = []

        for i, header in enumerate(headers):
            label = ttk.Label(add_Insurance_window, text=header, style='My.TLabel')
            label.grid(row=i, column=0, padx=10, pady=10, sticky='w')
            entry = ttk.Entry(add_Insurance_window, style='My.TEntry')
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.Insurance_entries.append(entry)

        add_Insurance_button = ttk.Button(add_Insurance_window, text='Add Insurance', command=lambda: self.save_Insurance(person_id))
        add_Insurance_button.grid(row=len(headers), column=0, columnspan=2, pady=10)

        self.add_Insurance_window = add_Insurance_window
        window.destroy()

    def save_Insurance(self, person_id):
        data = [e.get() for e in self.Insurance_entries]
        query = "INSERT INTO Insurance_Account_Info (Insurance_Type, Account_Number, Bank_Name,Branch_Name,Branch_Code, National_ID) VALUES ( %s, %s, %s,%s, %s, %s)"
        
        try:
            self.cursor.execute(query, data + [person_id])
            self.conn.commit()
            self.add_Insurance_window.destroy()
            self.open_Insurance_list_after_change(person_id)
        except Exception as e:
            self.conn.rollback()

    def edit_Insurance(self, index, person_id, window):
        edit_Insurance_window = tk.Toplevel()
        edit_Insurance_window.title('Edit Insurance')

        headers = ['Insurance Type', 'Account_Number','Bank_Name','Branch_Name','Branch_Code']
        self.edit_Insurance_entries = []

        for i, header in enumerate(headers):
            label = ttk.Label(edit_Insurance_window, text=header, style='My.TLabel')
            label.grid(row=i, column=0, padx=10, pady=10, sticky='w')
            entry = ttk.Entry(edit_Insurance_window, style='My.TEntry')
            entry.grid(row=i, column=1, padx=10, pady=10)
            entry.insert(0, self.Insurance_rows[index][i + 3])  # Adjusted index to match the correct data
            self.edit_Insurance_entries.append(entry)

        save_Insurance_button = ttk.Button(edit_Insurance_window, text='Save', command=lambda: self.save_edit_Insurance(index, person_id, edit_Insurance_window))
        save_Insurance_button.grid(row=len(headers), column=0, columnspan=2, pady=10)

        window.destroy()

    def save_edit_Insurance(self, index, person_id, window):
        data = [e.get() for e in self.edit_Insurance_entries]
        query = "UPDATE Insurance_Account_Info SET  Insurance_Type= %s, Account_Number = %s, Bank_Name = %s,Branch_Name= %s,Branch_Code= %s WHERE Insurance_ID = %s"
        
        try:
            self.cursor.execute(query, data + [self.Insurance_rows[index][0]])  # Adjusted index to match the correct data
            self.conn.commit()
            window.destroy()
            self.open_Insurance_list_after_change(person_id)
        except Exception as e:
            self.conn.rollback()

    def delete_Insurance(self, index, person_id, window):
        query = "DELETE FROM Insurance_Account_Info WHERE Insurance_ID = %s"
        
        try:
            self.cursor.execute(query, [self.Insurance_rows[index][0]])  # Adjusted index to match the correct data
            self.conn.commit()
            del self.Insurance_rows[index]
            window.destroy()
            self.open_Insurance_list_after_change(person_id)
        except Exception as e:
            self.conn.rollback()


    def open_Insurance_list_after_change(self, person_id):
        self.open_Insurance_list(person_id)

    def refresh_table(self):
        for widgets in self.table_rows:
            for widget in widgets:
                widget.destroy()
        self.table_rows.clear()


        # Retrieve data from the "persons" table
        self.cursor.execute("SELECT * FROM Personal_Info")
        rows = self.cursor.fetchall()
        self.lst = [row for row in rows]

        for i, row in enumerate(self.lst):
            self.create_table_row(i, row)

        # Update add button position
        self.add_button.grid(row=len(self.lst) + 1, column=len(self.lst[0]) + 1, pady=10)

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

# Create a Tkinter window
root = tk.Tk()
root.title('Insurance Registration Table')
root.configure(background='#abf0df')

# Create style objects for the labels and entries
style = ttk.Style()
style.configure('My.TLabel', background='#fffddb', font=('Arial', 12, 'bold'), padding=10)
style.configure('My.TEntry', background='white', font=('Arial', 10), padding=5)

# Set a fixed initial size for the window (standard laptop resolution)
root.geometry("1125x500")


# Create a Table object to display the data
table = Table(root)

# Run the Tkinter event loop
root.mainloop()
