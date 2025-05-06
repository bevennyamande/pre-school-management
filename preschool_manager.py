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
            fees_paid REAL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value REAL
        )
    ''')
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('tuition_fee', 300.0)")
    conn.commit()
    conn.close()


def get_tuition_fee():
    conn = sqlite3.connect('preschool.db')
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key='tuition_fee'")
    result = c.fetchone()
    conn.close()
    return float(result[0]) if result else 300.0


def set_tuition_fee(new_fee):
    conn = sqlite3.connect('preschool.db')
    c = conn.cursor()
    c.execute("UPDATE settings SET value=? WHERE key='tuition_fee'", (new_fee,))
    conn.commit()
    conn.close()


# ---------- APPLICATION ----------
class PreschoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Preschool Management System")
        self.root.geometry("900x600")
        self.selected_id = None

        self.setup_ui()

    def setup_ui(self):
        # Tabs
        self.tabs = ttk.Notebook(self.root)
        self.tab_students = ttk.Frame(self.tabs)
        self.tab_admin = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_students, text='👧 Students')
        self.tabs.add(self.tab_admin, text='🛠 Admin')
        self.tabs.pack(fill="both", expand=True)

        self.setup_students_tab()
        self.setup_admin_tab()

    def setup_students_tab(self):
        # Variables
        self.name_var = tk.StringVar()
        self.age_var = tk.IntVar()
        self.guardian_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.fees_var = tk.DoubleVar()

        # Form Frame
        form = tk.LabelFrame(self.tab_students, text="Student Information", padx=10, pady=10)
        form.pack(fill="x", padx=10, pady=10)

        tk.Label(form, text="Name").grid(row=0, column=0)
        tk.Entry(form, textvariable=self.name_var).grid(row=0, column=1)

        tk.Label(form, text="Age").grid(row=0, column=2)
        tk.Entry(form, textvariable=self.age_var).grid(row=0, column=3)

        tk.Label(form, text="Guardian").grid(row=1, column=0)
        tk.Entry(form, textvariable=self.guardian_var).grid(row=1, column=1)

        tk.Label(form, text="Contact").grid(row=1, column=2)
        tk.Entry(form, textvariable=self.contact_var).grid(row=1, column=3)

        tk.Label(form, text="Fees Paid").grid(row=2, column=0)
        tk.Entry(form, textvariable=self.fees_var).grid(row=2, column=1)

        tk.Button(form, text="➕ Add", command=self.add_student).grid(row=2, column=2)
        tk.Button(form, text="✏️ Update", command=self.update_student).grid(row=2, column=3)
        tk.Button(form, text="🗑️ Delete", command=self.delete_student).grid(row=2, column=4)

        # Table
        columns = ('ID', 'Name', 'Age', 'Guardian', 'Contact', 'Fees Paid', 'Balance')
        self.tree = ttk.Treeview(self.tab_students, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind('<ButtonRelease-1>', self.select_row)

        self.load_students()

    def setup_admin_tab(self):
        self.tuition_fee_var = tk.DoubleVar(value=get_tuition_fee())
        admin_frame = tk.LabelFrame(self.tab_admin, text="Admin Settings", padx=10, pady=10)
        admin_frame.pack(fill="x", padx=20, pady=20)

        tk.Label(admin_frame, text="Default Tuition Fee ($):").grid(row=0, column=0)
        tk.Entry(admin_frame, textvariable=self.tuition_fee_var).grid(row=0, column=1)
        tk.Button(admin_frame, text="💾 Save", command=self.save_tuition_fee).grid(row=0, column=2)

    def save_tuition_fee(self):
        try:
            new_fee = float(self.tuition_fee_var.get())
            set_tuition_fee(new_fee)
            self.load_students()
            messagebox.showinfo("Success", "Tuition fee updated.")
        except ValueError:
            messagebox.showerror("Error", "Invalid tuition fee value.")

    def clear_inputs(self):
        self.name_var.set('')
        self.age_var.set(0)
        self.guardian_var.set('')
        self.contact_var.set('')
        self.fees_var.set(0.0)

    def add_student(self):
        try:
            conn = sqlite3.connect('preschool.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO students (name, age, guardian, contact, fees_paid)
                VALUES (?, ?, ?, ?, ?)''',
                (self.name_var.get(), self.age_var.get(), self.guardian_var.get(),
                 self.contact_var.get(), self.fees_var.get()))
            conn.commit()
            conn.close()
            self.load_students()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_students(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        tuition_fee = get_tuition_fee()

        conn = sqlite3.connect('preschool.db')
        c = conn.cursor()
        c.execute("SELECT * FROM students")
        for row in c.fetchall():
            balance = round(tuition_fee - row[5], 2)
            self.tree.insert('', 'end', values=(*row, balance))
        conn.close()

    def select_row(self, event):
        selected = self.tree.focus()
        if selected:
            data = self.tree.item(selected)['values']
            self.selected_id = data[0]
            self.name_var.set(data[1])
            self.age_var.set(data[2])
            self.guardian_var.set(data[3])
            self.contact_var.set(data[4])
            self.fees_var.set(data[5])

    def update_student(self):
        try:
            conn = sqlite3.connect('preschool.db')
            c = conn.cursor()
            c.execute('''
                UPDATE students SET name=?, age=?, guardian=?, contact=?, fees_paid=?
                WHERE id=?''',
                (self.name_var.get(), self.age_var.get(), self.guardian_var.get(),
                 self.contact_var.get(), self.fees_var.get(), self.selected_id))
            conn.commit()
            conn.close()
            self.load_students()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_student(self):
        if not self.selected_id:
            messagebox.showwarning("Select", "Please select a student to delete.")
            return
        try:
            conn = sqlite3.connect('preschool.db')
            c = conn.cursor()
            c.execute("DELETE FROM students WHERE id=?", (self.selected_id,))
            conn.commit()
            conn.close()
            self.load_students()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ---------- RUN ----------
if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    app = PreschoolApp(root)
    root.mainloop()

