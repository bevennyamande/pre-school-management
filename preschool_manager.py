import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect('preschool.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            guardian TEXT,
            contact TEXT,
            fees REAL
        )
    ''')
    conn.commit()
    conn.close()

# ---------- CORE APP ----------
class PreschoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Preschool Management System")
        self.root.geometry("800x500")

        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        # Inputs
        self.name_var = tk.StringVar()
        self.age_var = tk.IntVar()
        self.guardian_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.fees_var = tk.DoubleVar()

        frame = tk.LabelFrame(self.root, text="Student Info", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=10)

        tk.Label(frame, text="Name").grid(row=0, column=0)
        tk.Entry(frame, textvariable=self.name_var).grid(row=0, column=1)

        tk.Label(frame, text="Age").grid(row=0, column=2)
        tk.Entry(frame, textvariable=self.age_var).grid(row=0, column=3)

        tk.Label(frame, text="Guardian").grid(row=1, column=0)
        tk.Entry(frame, textvariable=self.guardian_var).grid(row=1, column=1)

        tk.Label(frame, text="Contact").grid(row=1, column=2)
        tk.Entry(frame, textvariable=self.contact_var).grid(row=1, column=3)

        tk.Label(frame, text="Fees Paid").grid(row=2, column=0)
        tk.Entry(frame, textvariable=self.fees_var).grid(row=2, column=1)

        tk.Button(frame, text="Add Student", command=self.add_student).grid(row=2, column=2)
        tk.Button(frame, text="Update Fee", command=self.update_fee).grid(row=2, column=3)

        # Table
        self.tree = ttk.Treeview(self.root, columns=('ID', 'Name', 'Age', 'Guardian', 'Contact', 'Fees'), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Bind row selection
        self.tree.bind('<ButtonRelease-1>', self.select_row)

    def add_student(self):
        conn = sqlite3.connect('preschool.db')
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO students (name, age, guardian, contact, fees)
                VALUES (?, ?, ?, ?, ?)''',
                (self.name_var.get(), self.age_var.get(), self.guardian_var.get(),
                 self.contact_var.get(), self.fees_var.get()))
            conn.commit()
            self.load_students()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def load_students(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect('preschool.db')
        c = conn.cursor()
        c.execute("SELECT * FROM students")
        for row in c.fetchall():
            self.tree.insert('', 'end', values=row)
        conn.close()

    def update_fee(self):
        selected = self.tree.focus()
        if not selected:
            return messagebox.showwarning("Selection", "No student selected.")
        data = self.tree.item(selected)['values']
        student_id = data[0]
        new_fee = self.fees_var.get()

        conn = sqlite3.connect('preschool.db')
        c = conn.cursor()
        c.execute("UPDATE students SET fees = ? WHERE id = ?", (new_fee, student_id))
        conn.commit()
        conn.close()
        self.load_students()

    def select_row(self, event):
        selected = self.tree.focus()
        if selected:
            data = self.tree.item(selected)['values']
            self.name_var.set(data[1])
            self.age_var.set(data[2])
            self.guardian_var.set(data[3])
            self.contact_var.set(data[4])
            self.fees_var.set(data[5])

    def clear_inputs(self):
        self.name_var.set('')
        self.age_var.set(0)
        self.guardian_var.set('')
        self.contact_var.set('')
        self.fees_var.set(0.0)


# ---------- MAIN ----------
if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    app = PreschoolApp(root)
    root.mainloop()
