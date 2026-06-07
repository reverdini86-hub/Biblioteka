import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class LibrarySystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления библиотекой")
        self.root.geometry("1200x750")
        self.root.configure(bg="#E8E0F8")  # светло-фиолетовый фон
        self.root.minsize(1000, 650)
        
        # Подключение к БД
        self.db_name = "library.db"
        self.init_database()
        
        # Текущий пользователь
        self.current_user_id = None
        self.current_username = None
        self.current_role = None
        self.current_fullname = None
        self.current_frame = None
        
        self.show_login_screen()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def init_database(self):
        """Создание базы данных и таблиц"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Таблица книг
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER NOT NULL,
                genre TEXT,
                quantity INTEGER NOT NULL DEFAULT 1,
                available INTEGER NOT NULL DEFAULT 1
            )
        ''')
        
        # Таблица читателей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_name TEXT NOT NULL,
                first_name TEXT NOT NULL,
                middle_name TEXT,
                phone TEXT,
                email TEXT,
                reg_date TEXT NOT NULL
            )
        ''')
        
        # Таблица пользователей (администраторы и библиотекари)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                last_name TEXT NOT NULL,
                first_name TEXT NOT NULL,
                middle_name TEXT,
                role TEXT NOT NULL CHECK(role IN ('admin', 'librarian'))
            )
        ''')
        
        # Таблица выданных книг
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS issued_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                reader_id INTEGER NOT NULL,
                issue_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT NOT NULL DEFAULT 'issued',
                fine REAL DEFAULT 0,
                FOREIGN KEY (book_id) REFERENCES books (id),
                FOREIGN KEY (reader_id) REFERENCES readers (id)
            )
        ''')
        
        # Создание индексов для ускорения поиска
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_title ON books(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_author ON books(author)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_readers_last_name ON readers(last_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_issued_status ON issued_books(status)")
        
        # Создание тестового администратора, если нет пользователей
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO users (username, password, last_name, first_name, middle_name, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', 'admin123', 'Администратор', 'Главный', '', 'admin'))
        
        # Добавление тестовых книг, если таблица пуста
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] == 0:
            test_books = [
                ('Война и мир', 'Лев Толстой', 1869, 'Роман', 5, 5),
                ('Преступление и наказание', 'Фёдор Достоевский', 1866, 'Роман', 3, 3),
                ('Мастер и Маргарита', 'Михаил Булгаков', 1967, 'Роман', 4, 4),
                ('Евгений Онегин', 'Александр Пушкин', 1833, 'Роман в стихах', 2, 2),
                ('Мёртвые души', 'Николай Гоголь', 1842, 'Поэма', 3, 3)
            ]
            cursor.executemany('''
                INSERT INTO books (title, author, year, genre, quantity, available)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', test_books)
        
        # Добавление тестовых читателей, если таблица пуста
        cursor.execute("SELECT COUNT(*) FROM readers")
        if cursor.fetchone()[0] == 0:
            test_readers = [
                ('Иванов', 'Иван', 'Иванович', '+7(911)111-11-11', 'ivanov@mail.ru', datetime.now().strftime("%d.%m.%Y")),
                ('Петрова', 'Елена', 'Сергеевна', '+7(922)222-22-22', 'petrova@mail.ru', datetime.now().strftime("%d.%m.%Y")),
                ('Сидоров', 'Алексей', 'Владимирович', '+7(933)333-33-33', 'sidorov@mail.ru', datetime.now().strftime("%d.%m.%Y"))
            ]
            cursor.executemany('''
                INSERT INTO readers (last_name, first_name, middle_name, phone, email, reg_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', test_readers)
        
        conn.commit()
        conn.close()
    
    def on_closing(self):
        """Корректное закрытие приложения"""
        self.root.destroy()
    
    def clear_screen(self):
        """Очистка экрана"""
        if self.current_frame:
            self.current_frame.destroy()
    
    def show_login_screen(self):
        """Экран входа в систему"""
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg="#E8E0F8")
        main_frame.pack(fill="both", expand=True)
        self.current_frame = main_frame
        
        # Заголовок
        title = tk.Label(main_frame, text="📚 СИСТЕМА УПРАВЛЕНИЯ БИБЛИОТЕКОЙ\nАвтоматизация учёта книг и читателей",
                         font=("Arial", 20, "bold"), bg="#E8E0F8", fg="#4B0082", justify="center")
        title.pack(pady=40)
        
        # Форма входа
        form_frame = tk.Frame(main_frame, bg="white", relief="groove", bd=2)
        form_frame.pack(pady=30, padx=50)
        
        tk.Label(form_frame, text="Логин:", font=("Arial", 12), bg="white", fg="#4B0082").grid(row=0, column=0, padx=20, pady=15)
        self.login_username = tk.Entry(form_frame, font=("Arial", 12), width=20)
        self.login_username.grid(row=0, column=1, padx=20, pady=15)
        
        tk.Label(form_frame, text="Пароль:", font=("Arial", 12), bg="white", fg="#4B0082").grid(row=1, column=0, padx=20, pady=15)
        self.login_password = tk.Entry(form_frame, font=("Arial", 12), width=20, show="*")
        self.login_password.grid(row=1, column=1, padx=20, pady=15)
        
        btn_frame = tk.Frame(main_frame, bg="#E8E0F8")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="ВОЙТИ", command=self.login,
                 bg="#7B68EE", fg="white", font=("Arial", 12, "bold"), padx=30, pady=8).pack(side="left", padx=10)
        
        info_frame = tk.Frame(main_frame, bg="#E8E0F8")
        info_frame.pack(pady=30)
        tk.Label(info_frame, text="📌 Тестовые данные:\nАдминистратор: admin / admin123\nБиблиотекарь: (создайте через админа)",
                 font=("Arial", 10), bg="#E8E0F8", fg="#6A5ACD", justify="left").pack()
    
    def login(self):
        """Авторизация пользователя"""
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Ошибка", "Введите логин и пароль!")
            return
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, last_name, first_name, middle_name FROM users WHERE username=? AND password=?", 
                      (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            self.current_user_id = user[0]
            self.current_username = user[1]
            self.current_role = user[2]
            full_name = f"{user[3]} {user[4]} {user[5]}".strip()
            self.current_fullname = full_name
            
            if self.current_role == 'admin':
                self.show_admin_interface()
            else:
                self.show_librarian_interface()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")
    
    def create_header(self, parent, title, color):
        """Создание верхней панели"""
        header = tk.Frame(parent, bg=color, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=title, font=("Arial", 14, "bold"), bg=color, fg="white").pack(side="left", padx=20)
        tk.Button(header, text="🚪 ВЫХОД", command=self.show_login_screen,
                 bg="#9370DB", fg="white", font=("Arial", 10, "bold")).pack(side="right", padx=20)
        return header
    
    def show_admin_interface(self):
        """Интерфейс администратора"""
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg="#E8E0F8")
        main_frame.pack(fill="both", expand=True)
        self.current_frame = main_frame
        
        self.create_header(main_frame, f"👑 АДМИНИСТРАТОР: {self.current_fullname}", "#6A5ACD")
        
        # Кнопки меню
        buttons_frame = tk.Frame(main_frame, bg="#E8E0F8")
        buttons_frame.pack(pady=20)
        
        buttons = [
            ("📚 УПРАВЛЕНИЕ КНИГАМИ", "#7B68EE", self.show_books_management),
            ("👥 УПРАВЛЕНИЕ ЧИТАТЕЛЯМИ", "#8B78FF", self.show_readers_management),
            ("📖 ВЫДАЧА КНИГИ", "#9370DB", self.show_issue_book),
            ("🔄 ВОЗВРАТ КНИГИ", "#9B8AFF", self.show_return_book),
            ("📊 ОТЧЁТЫ", "#A39AFF", self.show_reports),
            ("👨‍💼 УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ", "#B0A8FF", self.show_users_management)
        ]
        
        for text, color, cmd in buttons:
            btn = tk.Button(buttons_frame, text=text, bg=color, fg="white",
                           font=("Arial", 11, "bold"), padx=15, pady=8, width=28, command=cmd)
            btn.pack(pady=6)
    
    def show_librarian_interface(self):
        """Интерфейс библиотекаря"""
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg="#E8E0F8")
        main_frame.pack(fill="both", expand=True)
        self.current_frame = main_frame
        
        self.create_header(main_frame, f"👩‍💼 БИБЛИОТЕКАРЬ: {self.current_fullname}", "#9370DB")
        
        buttons_frame = tk.Frame(main_frame, bg="#E8E0F8")
        buttons_frame.pack(pady=20)
        
        buttons = [
            ("📚 УПРАВЛЕНИЕ КНИГАМИ", "#7B68EE", self.show_books_management),
            ("👥 УПРАВЛЕНИЕ ЧИТАТЕЛЯМИ", "#8B78FF", self.show_readers_management),
            ("📖 ВЫДАЧА КНИГИ", "#9370DB", self.show_issue_book),
            ("🔄 ВОЗВРАТ КНИГИ", "#9B8AFF", self.show_return_book),
            ("📊 ОТЧЁТЫ", "#A39AFF", self.show_reports)
        ]
        
        for text, color, cmd in buttons:
            btn = tk.Button(buttons_frame, text=text, bg=color, fg="white",
                           font=("Arial", 11, "bold"), padx=15, pady=8, width=28, command=cmd)
            btn.pack(pady=6)
    
    def create_table(self, parent, columns, col_widths, data_func, on_select=None):
        """Универсальный метод создания таблицы"""
        table_frame = tk.Frame(parent, bg="#E8E0F8")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=col_widths.get(col, 100))
        
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        
        def refresh():
            for item in tree.get_children():
                tree.delete(item)
            for row in data_func():
                tree.insert("", "end", values=row)
        
        refresh()
        
        if on_select:
            tree.bind("<<TreeviewSelect>>", lambda e: on_select(tree))
        
        return tree, refresh
    
    # ==================== УПРАВЛЕНИЕ КНИГАМИ ====================
    
    def show_books_management(self):
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg="#E8E0F8")
        main_frame.pack(fill="both", expand=True)
        self.current_frame = main_frame
        
        self.create_header(main_frame, "📚 УПРАВЛЕНИЕ КНИГАМИ", "#7B68EE")
        
        # Поиск
        search_frame = tk.Frame(main_frame, bg="#E8E0F8")
        search_frame.pack(pady=10)
        
        tk.Label(search_frame, text="Поиск:", bg="#E8E0F8", font=("Arial", 11), fg="#4B0082").pack(side="left", padx=10)
        search_entry = tk.Entry(search_frame, width=30, font=("Arial", 11))
        search_entry.pack(side="left", padx=10)
        
        def get_books_data():
            search_text = search_entry.get().strip()
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            if search_text:
                cursor.execute('''
                    SELECT id, title, author, year, genre, quantity, available
                    FROM books WHERE title LIKE ? OR author LIKE ?
                    ORDER BY title
                ''', (f'%{search_text}%', f'%{search_text}%'))
            else:
                cursor.execute("SELECT id, title, author, year, genre, quantity, available FROM books ORDER BY title")
            books = cursor.fetchall()
            conn.close()
            return books
        
        columns = ("ID", "Название", "Автор", "Год", "Жанр", "Всего", "Доступно")
        col_widths = {"ID": 50, "Название": 250, "Автор": 180, "Год": 70, "Жанр": 120, "Всего": 70, "Доступно": 80}
        
        tree, refresh = self.create_table(main_frame, columns, col_widths, get_books_data)
        
        # Кнопки действий
        action_frame = tk.Frame(main_frame, bg="#E8E0F8")
        action_frame.pack(pady=10)
        
        def add_book():
            self.book_form("Добавление книги", None, refresh)
        
        def edit_book():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Ошибка", "Выберите книгу для редактирования!")
                return
            book_id = tree.item(selected[0])["values"][0]
            self.book_form("Редактирование книги", book_id, refresh)
        
        def delete_book():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Ошибка", "Выберите книгу для удаления!")
                return
            book_id = tree.item(selected[0])["values"][0]
            book_title = tree.item(selected[0])["values"][1]
            
            if messagebox.askyesno("Подтверждение", f"Удалить книгу '{book_title}'?"):
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM issued_books WHERE book_id=?", (book_id,))
                cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Успех", "Книга удалена!")
                refresh()
        
        tk.Button(action_frame, text="➕ ДОБАВИТЬ", command=add_book,
                 bg="#7B68EE", fg="white", font=("Arial", 11), padx=20, pady=5).pack(side="left", padx=10)
        tk.Button(action_frame, text="✏️ РЕДАКТИРОВАТЬ", command=edit_book,
                 bg="#9370DB", fg="white", font=("Arial", 11), padx=20, pady=5).pack(side="left", padx=10)
        tk.Button(action_frame, text="🗑️ УДАЛИТЬ", command=delete_book,
                 bg="#BA55D3", fg="white", font=("Arial", 11), padx=20, pady=5).pack(side="left", padx=10)
        
        tk.Button(search_frame, text="🔍 НАЙТИ", command=refresh,
                 bg="#9370DB", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(search_frame, text="СБРОСИТЬ", command=lambda: [search_entry.delete(0, tk.END), refresh()],
                 bg="#B0A8FF", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        back_btn = tk.Button(main_frame, text="← НАЗАД", command=self.show_admin_interface if self.current_role == 'admin' else self.show_librarian_interface,
                             bg="#6A5ACD", fg="white", font=("Arial", 11), padx=20, pady=8)
        back_btn.pack(pady=10)
    
    def book_form(self, title, book_id, refresh):
        """Форма добавления/редактирования книги"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x450")
        dialog.configure(bg="#E8E0F8")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=title, font=("Arial", 16, "bold"), bg="#E8E0F8", fg="#4B0082").pack(pady=15)
        
        form_frame = tk.Frame(dialog, bg="white", relief="groove", bd=2)
        form_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        fields = [
            ("Название:", "title"),
            ("Автор:", "author"),
            ("Год издания:", "year"),
            ("Жанр:", "genre"),
            ("Количество экземпляров:", "quantity")
        ]
        entries = {}
        
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, font=("Arial", 11), bg="white", fg="#4B0082").grid(row=i, column=0, padx=20, pady=10, sticky="e")
            entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
            entry.grid(row=i, column=1, padx=20, pady=10)
            entries[key] = entry
        
        if book_id:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT title, author, year, genre, quantity FROM books WHERE id=?", (book_id,))
            data = cursor.fetchone()
            conn.close()
            if data:
                entries['title'].insert(0, data[0])
                entries['author'].insert(0, data[1])
                entries['year'].insert(0, str(data[2]))
                entries['genre'].insert(0, data[3] or "")
                entries['quantity'].insert(0, str(data[4]))
        
        def save():
            title_val = entries['title'].get().strip()
            author_val = entries['author'].get().strip()
            year_val = entries['year'].get().strip()
            genre_val = entries['genre'].get().strip()
            quantity_val = entries['quantity'].get().strip()
            
            if not title_val or not author_val or not year_val:
                messagebox.showwarning("Ошибка", "Название, автор и год издания обязательны!")
                return
            
            try:
                year = int(year_val)
                quantity = int(quantity_val) if quantity_val else 1
                if quantity <= 0:
                    quantity = 1
            except ValueError:
                messagebox.showwarning("Ошибка", "Год и количество должны быть числами!")
                return
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if book_id:
                # Получаем текущее количество и доступное количество
                cursor.execute("SELECT quantity, available FROM books WHERE id=?", (book_id,))
                old_quantity, old_available = cursor.fetchone()
                delta = quantity - old_quantity
                new_available = old_available + delta
                if new_available < 0:
                    new_available = 0
                
                cursor.execute('''
                    UPDATE books SET title=?, author=?, year=?, genre=?, quantity=?, available=?
                    WHERE id=?
                ''', (title_val, author_val, year, genre_val, quantity, new_available, book_id))
                msg = "Книга обновлена!"
            else:
                cursor.execute('''
                    INSERT INTO books (title, author, year, genre, quantity, available)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (title_val, author_val, year, genre_val, quantity, quantity))
                msg = "Книга добавлена!"
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", msg)
            dialog.destroy()
            refresh()
        
        btn_frame = tk.Frame(dialog, bg="#E8E0F8")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="СОХРАНИТЬ", command=save,
                 bg="#7B68EE", fg="white", font=("Arial", 11, "bold"), padx=25, pady=5).pack(side="left", padx=10)
        tk.Button(btn_frame, text="ОТМЕНА", command=dialog.destroy,
                 bg="#BA55D3", fg="white", font=("Arial", 11), padx=25, pady=5).pack(side="left", padx=10)
    
    # ==================== УПРАВЛЕНИЕ ЧИТАТЕЛЯМИ ====================
    
    def show_readers_management(self):
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg="#E8E0F8")
        main_frame.pack(fill="both", expand=True)
        self.current_frame = main_frame
        
        self.create_header(main_frame, "👥 УПРАВЛЕНИЕ ЧИТАТЕЛЯМИ", "#8B78FF")
        
        search_frame = tk.Frame(main_frame, bg="#E8E0F8")
        search_frame.pack(pady=10)
        
        tk.Label(search_frame, text="Поиск по фамилии:", bg="#E8E0F8", font=("Arial", 11), fg="#4B0082").pack(side="left", padx=10)
        search_entry = tk.Entry(search_frame, width=25, font=("Arial", 11))
        search_entry.pack(side="left", padx=10)
        
        def get_readers_data():
            search_text = search_entry.get().strip()
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            if search_text:
                cursor.execute('''
                    SELECT id, last_name, first_name, middle_name, phone, email, reg_date
                    FROM readers WHERE last_name LIKE ?
                    ORDER BY last_name
                ''', (f'%{search_text}%',))
            else:
                cursor.execute("SELECT id, last_name, first_name, middle_name, phone, email, reg_date FROM readers ORDER BY last_name")
            readers = cursor.fetchall()
            conn.close()
            return readers
        
        columns = ("ID", "Фамилия", "Имя", "Отчество", "Телефон", "Email", "Дата регистрации")
        col_widths = {"ID": 50, "Фамилия": 120, "Имя": 100, "Отчество": 100, "Телефон": 120, "Email": 160, "Дата регистрации": 120}
        
        tree, refresh = self.create_table(main_frame, columns, col_widths, get_readers_data)
        
        action_frame = tk.Frame(main_frame, bg="#E8E0F8")
        action_frame.pack(pady=10)
        
        def add_reader():
            self.reader_form("Добавление читателя", None, refresh)
        
        def edit_reader():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Ошибка", "Выберите читателя для редактирования!")
                return
            reader_id = tree.item(selected[0])["values"][0]
            self.reader_form("Редактирование читателя", reader_id, refresh)
        
        def delete_reader():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Ошибка", "Выберите читателя для удаления!")
                return
            reader_id = tree.item(selected[0])["values"][0]
            reader_name = f"{tree.item(selected[0])['values'][1]} {tree.item(selected[0])['values'][2]}"
            
            if messagebox.askyesno("Подтверждение", f"Удалить читателя '{reader_name}'?"):
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM issued_books WHERE reader_id=?", (reader_id,))
                cursor.execute("DELETE FROM readers WHERE id=?", (reader_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Успех", "Читатель удалён!")
                refresh()
        
        tk.Button(action_frame, text="➕ ДОБАВИТЬ", command=add_reader,
                 bg="#7B68EE", fg="white", font=("Arial", 11), padx=20, pady=5).pack(side="left", padx=10)
        tk.Button(action_frame, text="✏️ РЕДАКТИРОВАТЬ", command=edit_reader,
                 bg="#9370DB", fg="white", font=("Arial", 11), padx=20, pady=5).pack(side="left", padx=10)
        tk.Button(action_frame, text="🗑️ УДАЛИТЬ", command=delete_reader,
                 bg="#BA55D3", fg="white", font=("Arial", 11), padx=20, pady=5).pack(side="left", padx=10)
        
        tk.Button(search_frame, text="🔍 НАЙТИ", command=refresh,
                 bg="#9370DB", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(search_frame, text="СБРОСИТЬ", command=lambda: [search_entry.delete(0, tk.END), refresh()],
                 bg="#B0A8FF", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        back_btn = tk.Button(main_frame, text="← НАЗАД", command=self.show_admin_interface if self.current_role == 'admin' else self.show_librarian_interface,
                             bg="#6A5ACD", fg="white", font=("Arial", 11), padx=20, pady=8)
        back_btn.pack(pady=10)
    
    def reader_form(self, title, reader_id, refresh):
        """Форма добавления/редактирования читателя"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x450")
        dialog.configure(bg="#E8E0F8")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=title, font=("Arial", 16, "bold"), bg="#E8E0F8", fg="#4B0082").pack(pady=15)
        
        form_frame = tk.Frame(dialog, bg="white", relief="groove", bd=2)
        form_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        fields = [
            ("Фамилия:", "last_name"),
            ("Имя:", "first_name"),
            ("Отчество:", "middle_name"),
            ("Телефон:", "phone"),
            ("Email:", "email")
        ]
        entries = {}
        
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, font=("Arial", 11), bg="white", fg="#4B0082").grid(row=i, column=0, padx=20, pady=10, sticky="e")
            entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
            entry.grid(row=i, column=1, padx=20, pady=10)
            entries[key] = entry
        
        if reader_id:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT last_name, first_name, middle_name, phone, email FROM readers WHERE id=?", (reader_id,))
            data = cursor.fetchone()
            conn.close()
            if data:
                entries['last_name'].insert(0, data[0])
                entries['first_name'].insert(0, data[1])
                entries['middle_name'].insert(0, data[2] or "")
                entries['phone'].insert(0, data[3] or "")
                entries['email'].insert(0, data[4] or "")
        
        def save():
            last_name = entries['last_name'].get().strip()
            first_name = entries['first_name'].get().strip()
            if not last_name or not first_name:
                messagebox.showwarning("Ошибка", "Фамилия и имя обязательны!")
                return
            
            middle_name = entries['middle_name'].get().strip()
            phone = entries['phone'].get().strip()
            email = entries['email'].get().strip()
            reg_date = datetime.now().strftime("%d.%m.%Y")
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if reader_id:
                cursor.execute('''
                    UPDATE readers SET last_name=?, first_name=?, middle_name=?, phone=?, email=?
                    WHERE id=?
                ''', (last_name, first_name, middle_name, phone, email, reader_id))
                msg = "Данные читателя обновлены!"
            else:
                cursor.execute('''
                    INSERT INTO readers (last_name, first_name, middle_name, phone, email, reg_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (last_name, first_name, middle_name, phone, email, reg_date))
                msg = "Читатель добавлен!"
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", msg)
            dialog.destroy()
            refresh()
        
        btn_frame = tk.Frame(dialog, bg="#E8E0F8")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="СОХРАНИТЬ", command=save,
                 bg="#7B68EE", fg="white", font=("Arial", 11, "bold"), padx=25, pady=5).pack(side="left", padx=10)
        tk.Button(btn_frame, text="ОТМЕНА", command=dialog.destroy,
                 bg="#BA55D3", fg="white", font=("Arial", 11), padx=25, pady=5).pack(side="left", padx=10)
    
    # ==================== ВЫДАЧА КНИГИ ====================
    
    def show_issue_book(self):
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg="#E8E0F8")
        main_frame.pack(fill="both", expand=True)
        self.current_frame = main_frame
        
        self.create_header(main_frame, "📖 ВЫДАЧА КНИГИ", "#9370DB")
        
        form_frame = tk.Frame(main_frame, bg="white", relief="groove", bd=2)
        form_frame.pack(pady=30, padx=50, fill="x")
        
        # Выбор читателя
        tk.Label(form_frame, text="Читатель:", font=("Arial", 12), bg="white", fg="#4B0082").grid(row=0, column=0, padx=20, pady=15, sticky="e")
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, last_name, first_name, middle_name FROM readers ORDER BY last_name")
        readers = cursor.fetchall()
        conn.close()
        
        reader_list = [f"{r[0]} - {r[1]} {r[2]} {r[3] or ''}".strip() for r in readers]
        reader_var = tk.StringVar()
        reader_combo = ttk.Combobox(form_frame, textvariable=reader_var, width=40, font=("Arial", 11))
        reader_combo["values"] = reader_list
        reader_combo.grid(row=0, column=1, padx=20, pady=15)
        
        # Выбор книги
        tk.Label(form_frame, text="Книга:", font=("Arial", 12), bg="white", fg="#4B0082").grid(row=1, column=0, padx=20, pady=15, sticky="e")
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author FROM books WHERE available > 0 ORDER BY title")
        books = cursor.fetchall()
        conn.close()
        
        book_list = [f"{b[0]} - {b[1]} ({b[2]})" for b in books]
        book_var = tk.StringVar()
        book_combo = ttk.Combobox(form_frame, textvariable=book_var, width=50, font=("Arial", 11))
        book_combo["values"] = book_list
        book_combo.grid(row=1, column=1, padx=20, pady=15)
        
        # Даты
        today = datetime.now().strftime("%d.%m.%Y")
        due_date = (datetime.now() + timedelta(days=14)).strftime("%d.%m.%Y")
        
        tk.Label(form_frame, text="Дата выдачи:", font=("Arial", 12), bg="white", fg="#4B0082").grid(row=2, column=0, padx=20, pady=15, sticky="e")
        tk.Label(form_frame, text=today, font=("Arial", 12, "bold"), bg="white", fg="#6A5ACD").grid(row=2, column=1, padx=20, pady=15, sticky="w")
        
        tk.Label(form_frame, text="Срок возврата:", font=("Arial", 12), bg="white", fg="#4B0082").grid(row=3, column=0, padx=20, pady=15, sticky="e")
        tk.Label(form_frame, text=due_date, font=("Arial", 12, "bold"), bg="white", fg="#6A5ACD").grid(row=3, column=1, padx=20, pady=15, sticky="w")
        
        def issue():
            reader_choice = reader_var.get()
            book_choice = book_var.get()
            
            if not reader_choice:
                messagebox.showwarning("Ошибка", "Выберите читателя!")
                return
            if not book_choice:
                messagebox.showwarning("Ошибка", "Выберите книгу!")
                return
            
            reader_id = int(reader_choice.split(" - ")[0])
            book_id = int(book_choice.split(" - ")[0])
            issue_date = today
            due_date_val = due_date
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Проверяем, есть ли доступные экземпляры
            cursor.execute("SELECT available FROM books WHERE id=?", (book_id,))
            available = cursor.fetchone()[0]
            
            if available <= 0:
                messagebox.showerror("Ошибка", "Нет доступных экземпляров этой книги!")
                conn.close()
                return
            
            # Добавляем запись о выдаче
            cursor.execute('''
                INSERT INTO issued_books (book_id, reader_id, issue_date, due_date, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (book_id, reader_id, issue_date, due_date_val, 'issued'))
            
            # Уменьшаем количество доступных экземпляров
            cursor.execute("UPDATE books SET available = available - 1 WHERE id=?", (book_id,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", f"Книга выдана!\nСрок возврата: {due_date_val}")
            
            # Очищаем выбор
            reader_var.set("")
            book_var.set("")
        
        btn_frame = tk.Frame(main_frame, bg="#E8E0F8")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="ВЫДАТЬ КНИГУ", command=issue,
                 bg="#7B68EE", fg="white", font=("Arial", 12, "bold"), padx=30, pady=8).pack(side="left", padx=10)
        
        back_btn = tk.Button(main_frame, text="← НАЗАД", command=self.show_admin_interface if self.current_role == 'admin' else self.show_librarian_interface,
                             bg="#6A5ACD", fg="white", font=("Arial", 11), padx=20, pady=8)
        back_btn.pack(pady=10)
    
    # ==================== ВОЗВРАТ КНИГИ ====================
    
    def show_return_book(self):
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg="#E8E0F8")
        main_frame.pack(fill="both", expand=True)
        self.current_frame = main_frame
        
        self.create_header(main_frame, "🔄 ВОЗВРАТ КНИГИ", "#9B8AFF")
        
        # Таблица выданных книг
        def get_issued_books_data():
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ib.id, r.last_name, r.first_name, r.middle_name, 
                       b.title, b.author, ib.issue_date, ib.due_date
                FROM issued_books ib
                JOIN readers r ON ib.reader_id = r.id
                JOIN books b ON ib.book_id = b.id
                WHERE ib.status = 'issued'
                ORDER BY ib.due_date
            ''')
            issued = cursor.fetchall()
            conn.close()
            
            result = []
            for i in issued:
                reader_name = f"{i[1]} {i[2]} {i[3] or ''}".strip()
                result.append((i[0], reader_name, i[4], i[5], i[6], i[7]))
            return result
        
        columns = ("ID", "Читатель", "Книга", "Автор", "Дата выдачи", "Срок возврата")
        col_widths = {"ID": 50, "Читатель": 180, "Книга": 200, "Автор": 150, "Дата выдачи": 110, "Срок возврата": 110}
        
        tree, refresh = self.create_table(main_frame, columns, col_widths, get_issued_books_data)
        
        def return_book():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Ошибка", "Выберите книгу для возврата!")
                return
            
            issued_id = tree.item(selected[0])["values"][0]
            book_title = tree.item(selected[0])["values"][2]
            due_date_str = tree.item(selected[0])["values"][5]
            issue_date_str = tree.item(selected[0])["values"][4]
            
            return_date = datetime.now()
            due_date = datetime.strptime(due_date_str, "%d.%m.%Y")
            issue_date = datetime.strptime(issue_date_str, "%d.%m.%Y")
            
            # Расчёт просрочки и штрафа
            fine = 0
            days_overdue = 0
            if return_date > due_date:
                days_overdue = (return_date - due_date).days
                fine = days_overdue * 10  # 10 рублей за день просрочки
                fine_message = f"Просрочка: {days_overdue} дней\nШтраф: {fine} руб."
            else:
                fine_message = "Просрочки нет."
            
            if messagebox.askyesno("Подтверждение", f"Вернуть книгу '{book_title}'?\n\n{fine_message}"):
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                
                # Обновляем запись о выдаче
                cursor.execute('''
                    UPDATE issued_books 
                    SET return_date=?, status='returned', fine=?
                    WHERE id=?
                ''', (return_date.strftime("%d.%m.%Y"), fine, issued_id))
                
                # Увеличиваем количество доступных экземпляров
                cursor.execute('''
                    UPDATE books SET available = available + 1 
                    WHERE id = (SELECT book_id FROM issued_books WHERE id=?)
                ''', (issued_id,))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Успех", f"Книга возвращена!\n{fine_message}")
                refresh()
        
        action_frame = tk.Frame(main_frame, bg="#E8E0F8")
        action_frame.pack(pady=10)
        tk.Button(action_frame, text="ВЕРНУТЬ ВЫБРАННУЮ КНИГУ", command=return_book,
                 bg="#7B68EE", fg="white", font=("Arial", 11, "bold"), padx=20, pady=5).pack()
        
        back_btn = tk.Button(main_frame, text="← НАЗАД", command=self.show_admin_interface if self.current_role == 'admin' else self.show_librarian_interface,
                             bg="#6A5ACD", fg="white", font=("Arial", 11), padx=20, pady=8)
        back_btn.pack(pady=10)
    
    # ==================== ОТЧЁТЫ ====================
    
    def show_reports(self):
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg="#E8E0F8")
        main_frame.pack(fill="both", expand=True)
        self.current_frame = main_frame
        
        self.create_header(main_frame, "📊 ОТЧЁТЫ", "#A39AFF")
        
        # Кнопки выбора отчёта
        btn_frame = tk.Frame(main_frame, bg="#E8E0F8")
        btn_frame.pack(pady=20)
        
        # Область для вывода результата
        result_frame = tk.Frame(main_frame, bg="#E8E0F8")
        result_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tree = None
        
        def show_debtors():
            nonlocal tree
            if tree:
                tree.destroy()
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.last_name, r.first_name, r.middle_name, 
                       b.title, b.author, ib.due_date,
                       (julianday('now') - julianday(ib.due_date)) as days_overdue
                FROM issued_books ib
                JOIN readers r ON ib.reader_id = r.id
                JOIN books b ON ib.book_id = b.id
                WHERE ib.status = 'issued' AND ib.due_date < date('now')
                ORDER BY days_overdue DESC
            ''')
            debtors = cursor.fetchall()
            conn.close()
            
            if not debtors:
                tk.Label(result_frame, text="Должников нет!", font=("Arial", 14), bg="#E8E0F8", fg="#4B0082").pack(pady=50)
                return
            
            # Создаём таблицу
            table_frame = tk.Frame(result_frame, bg="#E8E0F8")
            table_frame.pack(fill="both", expand=True)
            
            columns = ("Читатель", "Книга", "Автор", "Срок возврата", "Дней просрочки")
            tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            
            for debtor in debtors:
                reader_name = f"{debtor[0]} {debtor[1]} {debtor[2] or ''}".strip()
                days = int(debtor[6])
                tree.insert("", "end", values=(reader_name, debtor[3], debtor[4], debtor[5], days))
            
            scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scroll_y.set)
            tree.pack(side="left", fill="both", expand=True)
            scroll_y.pack(side="right", fill="y")
        
        def show_popular_books():
            nonlocal tree
            if tree:
                tree.destroy()
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT b.title, b.author, COUNT(ib.id) as issue_count
                FROM issued_books ib
                JOIN books b ON ib.book_id = b.id
                GROUP BY b.id
                ORDER BY issue_count DESC
                LIMIT 10
            ''')
            popular = cursor.fetchall()
            conn.close()
            
            if not popular:
                tk.Label(result_frame, text="Нет данных о выдачах!", font=("Arial", 14), bg="#E8E0F8", fg="#4B0082").pack(pady=50)
                return
            
            table_frame = tk.Frame(result_frame, bg="#E8E0F8")
            table_frame.pack(fill="both", expand=True)
            
            columns = ("Книга", "Автор", "Количество выдач")
            tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=200)
            
            for book in popular:
                tree.insert("", "end", values=(book[0], book[1], book[2]))
            
            scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scroll_y.set)
            tree.pack(side="left", fill="both", expand=True)
            scroll_y.pack(side="right", fill="y")
        
        def show_statistics():
            nonlocal tree
            if tree:
                tree.destroy()
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM books")
            total_books = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM readers")
            total_readers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM issued_books WHERE status='issued'")
            currently_issued = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(fine) FROM issued_books WHERE fine > 0")
            total_fines = cursor.fetchone()[0] or 0
            
            conn.close()
            
            stats_frame = tk.Frame(result_frame, bg="white", relief="groove", bd=2)
            stats_frame.pack(pady=50, padx=50)
            
            tk.Label(stats_frame, text="СТАТИСТИКА БИБЛИОТЕКИ", font=("Arial", 16, "bold"), bg="white", fg="#4B0082").pack(pady=15)
            tk.Label(stats_frame, text=f"Всего книг в библиотеке: {total_books}", font=("Arial", 12), bg="white").pack(anchor="w", padx=30, pady=5)
            tk.Label(stats_frame, text=f"Всего читателей: {total_readers}", font=("Arial", 12), bg="white").pack(anchor="w", padx=30, pady=5)
            tk.Label(stats_frame, text=f"Книг выдано в данный момент: {currently_issued}", font=("Arial", 12), bg="white").pack(anchor="w", padx=30, pady=5)
            tk.Label(stats_frame, text=f"Общая сумма штрафов: {total_fines:.2f} руб.", font=("Arial", 12), bg="white", fg="#BA55D3").pack(anchor="w", padx=30, pady=5)
        
        tk.Button(btn_frame, text="📋 ДОЛЖНИКИ", command=show_debtors,
                 bg="#7B68EE", fg="white", font=("Arial", 11, "bold"), padx=20, pady=8).pack(side="left", padx=10)
        tk.Button(btn_frame, text="⭐ ПОПУЛЯРНЫЕ КНИГИ", command=show_popular_books,
                 bg="#9370DB", fg="white", font=("Arial", 11, "bold"), padx=20, pady=8).pack(side="left", padx=10)
        tk.Button(btn_frame, text="📊 СТАТИСТИКА", command=show_statistics,
                 bg="#BA55D3", fg="white", font=("Arial", 11, "bold"), padx=20, pady=8).pack(side="left", padx=10)
        
        back_btn = tk.Button(main_frame, text="← НАЗАД", command=self.show_admin_interface if self.current_role == 'admin' else self.show_librarian_interface,
                             bg="#6A5ACD", fg="white", font=("Arial", 11), padx=20, pady=8)
        back_btn.pack(pady=10)
    
    # ==================== УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ (ТОЛЬКО АДМИН) ====================
    
    def show_users_management(self):
        if self.current_role != 'admin':
            messagebox.showerror("Ошибка", "Доступ запрещён! Только для администратора.")
            return
        
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg="#E8E0F8")
        main_frame.pack(fill="both", expand=True)
        self.current_frame = main_frame
        
        self.create_header(main_frame, "👨‍💼 УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ", "#B0A8FF")
        
        def get_users_data():
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, last_name, first_name, middle_name, role FROM users ORDER BY role, last_name")
            users = cursor.fetchall()
            conn.close()
            return users
        
        columns = ("ID", "Логин", "Фамилия", "Имя", "Отчество", "Роль")
        col_widths = {"ID": 50, "Логин": 120, "Фамилия": 120, "Имя": 100, "Отчество": 100, "Роль": 100}
        
        tree, refresh = self.create_table(main_frame, columns, col_widths, get_users_data)
        
        action_frame = tk.Frame(main_frame, bg="#E8E0F8")
        action_frame.pack(pady=10)
        
        def add_user():
            self.user_form("Добавление пользователя", None, refresh)
        
        def edit_user():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Ошибка", "Выберите пользователя для редактирования!")
                return
            user_id = tree.item(selected[0])["values"][0]
            self.user_form("Редактирование пользователя", user_id, refresh)
        
        def delete_user():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Ошибка", "Выберите пользователя для удаления!")
                return
            user_id = tree.item(selected[0])["values"][0]
            username = tree.item(selected[0])["values"][1]
            
            if username == 'admin':
                messagebox.showerror("Ошибка", "Нельзя удалить главного администратора!")
                return
            
            if messagebox.askyesno("Подтверждение", f"Удалить пользователя '{username}'?"):
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Успех", "Пользователь удалён!")
                refresh()
        
        tk.Button(action_frame, text="➕ ДОБАВИТЬ", command=add_user,
                 bg="#7B68EE", fg="white", font=("Arial", 11), padx=20, pady=5).pack(side="left", padx=10)
        tk.Button(action_frame, text="✏️ РЕДАКТИРОВАТЬ", command=edit_user,
                 bg="#9370DB", fg="white", font=("Arial", 11), padx=20, pady=5).pack(side="left", padx=10)
        tk.Button(action_frame, text="🗑️ УДАЛИТЬ", command=delete_user,
                 bg="#BA55D3", fg="white", font=("Arial", 11), padx=20, pady=5).pack(side="left", padx=10)
        
        back_btn = tk.Button(main_frame, text="← НАЗАД", command=self.show_admin_interface,
                             bg="#6A5ACD", fg="white", font=("Arial", 11), padx=20, pady=8)
        back_btn.pack(pady=10)
    
    def user_form(self, title, user_id, refresh):
        """Форма добавления/редактирования пользователя"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x500")
        dialog.configure(bg="#E8E0F8")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=title, font=("Arial", 16, "bold"), bg="#E8E0F8", fg="#4B0082").pack(pady=15)
        
        form_frame = tk.Frame(dialog, bg="white", relief="groove", bd=2)
        form_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        fields = [
            ("Логин:", "username"),
            ("Пароль:", "password"),
            ("Фамилия:", "last_name"),
            ("Имя:", "first_name"),
            ("Отчество:", "middle_name"),
            ("Роль:", "role")
        ]
        entries = {}
        
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, font=("Arial", 11), bg="white", fg="#4B0082").grid(row=i, column=0, padx=20, pady=10, sticky="e")
            
            if key == "role":
                entry = ttk.Combobox(form_frame, values=["admin", "librarian"], width=23, font=("Arial", 11))
                entry.set("librarian")
            else:
                entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
                if key == "password":
                    entry.config(show="*")
            entry.grid(row=i, column=1, padx=20, pady=10)
            entries[key] = entry
        
        if user_id:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT username, last_name, first_name, middle_name, role FROM users WHERE id=?", (user_id,))
            data = cursor.fetchone()
            conn.close()
            if data:
                entries['username'].insert(0, data[0])
                entries['last_name'].insert(0, data[1])
                entries['first_name'].insert(0, data[2])
                entries['middle_name'].insert(0, data[3] or "")
                entries['role'].set(data[4])
                entries['password'].insert(0, "********")
                entries['password'].config(state="disabled")
        
        def save():
            username = entries['username'].get().strip()
            password = entries['password'].get().strip()
            last_name = entries['last_name'].get().strip()
            first_name = entries['first_name'].get().strip()
            role = entries['role'].get()
            
            if not username or not last_name or not first_name:
                messagebox.showwarning("Ошибка", "Заполните все обязательные поля!")
                return
            
            if not user_id and not password:
                messagebox.showwarning("Ошибка", "Введите пароль!")
                return
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if user_id:
                if password and password != "********":
                    cursor.execute('''
                        UPDATE users SET username=?, password=?, last_name=?, first_name=?, middle_name=?, role=?
                        WHERE id=?
                    ''', (username, password, last_name, first_name, entries['middle_name'].get().strip(), role, user_id))
                else:
                    cursor.execute('''
                        UPDATE users SET username=?, last_name=?, first_name=?, middle_name=?, role=?
                        WHERE id=?
                    ''', (username, last_name, first_name, entries['middle_name'].get().strip(), role, user_id))
                msg = "Пользователь обновлён!"
            else:
                cursor.execute("SELECT COUNT(*) FROM users WHERE username=?", (username,))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует!")
                    conn.close()
                    return
                cursor.execute('''
                    INSERT INTO users (username, password, last_name, first_name, middle_name, role)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, password, last_name, first_name, entries['middle_name'].get().strip(), role))
                msg = "Пользователь добавлен!"
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", msg)
            dialog.destroy()
            refresh()
        
        btn_frame = tk.Frame(dialog, bg="#E8E0F8")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="СОХРАНИТЬ", command=save,
                 bg="#7B68EE", fg="white", font=("Arial", 11, "bold"), padx=25, pady=5).pack(side="left", padx=10)
        tk.Button(btn_frame, text="ОТМЕНА", command=dialog.destroy,
                 bg="#BA55D3", fg="white", font=("Arial", 11), padx=25, pady=5).pack(side="left", padx=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = LibrarySystem(root)
    root.mainloop()