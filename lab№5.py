import tkinter as tk
from tkinter import messagebox, ttk, filedialog, Toplevel
import json
import os
import shutil
from PIL import Image, ImageTk
import csv
import pickle

# Папка для збереження файлів
SAVE_FOLDER = "Yusypiv"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Шляхи до файлів
TXT_FILE = os.path.join(SAVE_FOLDER, "artifacts.txt")
CSV_FILE = os.path.join(SAVE_FOLDER, "artifacts.csv")
BIN_FILE = os.path.join(SAVE_FOLDER, "artifacts.bin")

# Батьківський клас
class Artifact:
    def __init__(self, name, age, origin, material):
        self.name = name
        self.age = age
        self.origin = origin
        self.material = material

    def get_info(self):
        return f"Назва: {self.name}\nВік: {self.age} років\nПоходження: {self.origin}\nМатеріал: {self.material}"

# Клас-нащадок
class DetailedArtifact(Artifact):
    def __init__(self, name, age, origin, material, description, condition, category, discovery_day, status, image_path, original_image_name=""):
        super().__init__(name, age, origin, material)
        self.description = description
        self.condition = condition
        self.category = category
        self.discovery_day = discovery_day
        self.status = status
        self.image_path = image_path
        self.original_image_name = original_image_name

    def get_full_info(self):
        return (f"Назва: {self.name}\nВік: {self.age} років\nПоходження: {self.origin}\n"
                f"Матеріал: {self.material}\nОпис: {self.description}\n"
                f"Стан: {self.condition}\nКатегорія: {self.category}\n"
                f"День виявлення: {self.discovery_day}\nСтатус: {self.status}")

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "origin": self.origin,
            "material": self.material,
            "description": self.description,
            "condition": self.condition,
            "category": self.category,
            "discovery_day": self.discovery_day,
            "status": self.status,
            "image_path": self.image_path,
            "original_image_name": self.original_image_name
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"], data["age"], data["origin"], data["material"],
            data["description"], data["condition"], data["category"],
            data["discovery_day"], data["status"], data.get("image_path", ""),
            data.get("original_image_name", "")
        )

# Клас для графічного інтерфейсу
class ArtifactApp:

    def clear_search_entry(self):
        self.search_entry.delete(0, tk.END)
        self.add_placeholder(None)

    def clear_filters(self):
        self.condition_var.set("Усі")
        self.category_var.set("Усі")
        self.day_var.set("Усі")
        self.status_var.set("Усі")
        self.search_info_label.config(text="")
        self.search_image_label.config(image="")

    def __init__(self, root):
        self.root = root
        self.root.title("Каталог артефактів")
        self.root.geometry("1209x804")

        # Список для хранения имен уже использованных фотографий
        self.used_image_names = []

        # Кеш для зображень
        self.image_cache = {}

        # Налаштування стилів
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", foreground="#333333")
        style.configure("TButton", background="#d0d0d0", foreground="#333333")
        style.map("TButton", background=[("active", "#b0b0b0")])
        self.root.configure(bg="#f0f0f0")

        # Завантаження даних
        self.load_data()

        self.current_artifact_index = 0
        self.current_image = None

        # Основний контейнер із вкладками
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладка "Пошук"
        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="Пошук")

        # Вкладка "Перегляд"
        self.browse_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.browse_tab, text="Перегляд")

        # Вкладка "Додавання артефактів"
        self.add_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_tab, text="Додавання артефактів")

        # Вкладка "Редагування артефактів"
        self.edit_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.edit_tab, text="Редагування артефактів")

        # --- Вкладка "Пошук" ---
        self.search_frame = tk.Frame(self.search_tab, bg="#f0f0f0", bd=2, relief="groove")
        self.search_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.search_frame, text="Введіть назву або вік:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(self.search_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.insert(0, "Введіть запит для пошуку")
        self.search_entry.config(fg="gray50")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)
        ttk.Button(self.search_frame, text="Пошук 🔍", command=self.search_artifact).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.search_frame, text="Очистити 🗑️", command=self.clear_search_entry).pack(side=tk.LEFT, padx=5)

        # Основной фрейм для содержимого вкладки "Пошук"
        self.main_search_frame = tk.Frame(self.search_tab, bg="#f0f0f0")
        self.main_search_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Список артефактов (слева)
        self.artifact_list_frame = tk.Frame(self.main_search_frame, bg="#f0f0f0", bd=2, relief="groove")
        self.artifact_list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        tk.Label(self.artifact_list_frame, text="Доступні артефакти:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.artifact_listbox = tk.Listbox(self.artifact_list_frame, height=15, width=30, bg="#ffffff", fg="#333333", font=("Arial", 10))
        self.artifact_listbox.pack(pady=5)
        self.update_artifact_listbox()


        # Фильтры (справа)
        self.filters_frame = tk.Frame(self.main_search_frame, bg="#f0f0f0", bd=2, relief="groove")
        self.filters_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        tk.Label(self.filters_frame, text="Стан:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.condition_var = tk.StringVar(value="Усі")
        self.condition_menu = ttk.OptionMenu(self.filters_frame, self.condition_var, "Усі", *self.conditions)
        self.condition_menu.pack(pady=5)

        tk.Label(self.filters_frame, text="Категорія:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.category_var = tk.StringVar(value="Усі")
        self.category_menu = ttk.OptionMenu(self.filters_frame, self.category_var, "Усі", *self.categories)
        self.category_menu.pack(pady=5)

        tk.Label(self.filters_frame, text="День виявлення:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.day_var = tk.StringVar(value="Усі")
        self.day_menu = ttk.OptionMenu(self.filters_frame, self.day_var, "Усі", *self.days_of_week)
        self.day_menu.pack(pady=5)

        tk.Label(self.filters_frame, text="Статус:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.status_var = tk.StringVar(value="Усі")
        self.status_menu = ttk.OptionMenu(self.filters_frame, self.status_var, "Усі", *self.statuses)
        self.status_menu.pack(pady=5)

        ttk.Button(self.filters_frame, text="Пошук 🔍", command=self.filter_search).pack(pady=10)
        ttk.Button(self.filters_frame, text="Очистити 🗑️", command=self.clear_filters).pack(pady=10)

        # Центральная часть: фото и описание артефакта
        self.search_info_frame = tk.Frame(self.main_search_frame, bg="#f0f0f0", bd=2, relief="groove")
        self.search_info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self.search_image_label = tk.Label(self.search_info_frame, bg="#f0f0f0")
        self.search_image_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.search_info_label = tk.Label(self.search_info_frame, text="", justify="left", bg="#f0f0f0", fg="#333333", font=("Arial", 12), wraplength=400)
        self.search_info_label.pack(side=tk.RIGHT, pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Нижняя часть: управление списками "Стан" и "Категория"
        self.manage_frame = tk.Frame(self.search_tab, bg="#f0f0f0", bd=2, relief="groove")
        self.manage_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(self.manage_frame, text="Нове значення:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.new_value_frame = tk.Frame(self.manage_frame, bg="#f0f0f0")
        self.new_value_frame.pack(pady=5)
        self.new_value_entry = tk.Entry(self.new_value_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.new_value_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.new_value_frame, text="Перевірити списки 📋", command=self.show_lists).pack(side=tk.LEFT, padx=5)

        self.manage_buttons_frame = tk.Frame(self.manage_frame, bg="#f0f0f0")
        self.manage_buttons_frame.pack(fill=tk.BOTH, expand=True)

        self.condition_manage_frame = tk.LabelFrame(self.manage_buttons_frame, text="СТАН", bg="#f0f0f0", fg="#333333", font=("Arial", 12, "bold"))
        self.condition_manage_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Button(self.condition_manage_frame, text="Додати ➕", command=self.add_to_conditions).pack(pady=2, padx=5, fill=tk.X)
        ttk.Button(self.condition_manage_frame, text="Редагувати ✏️", command=self.edit_condition).pack(pady=2, padx=5, fill=tk.X)
        ttk.Button(self.condition_manage_frame, text="Видалити 🗑️", command=self.delete_from_conditions).pack(pady=2, padx=5, fill=tk.X)
        ttk.Button(self.condition_manage_frame, text="Сортувати 🔢", command=self.sort_conditions).pack(pady=2, padx=5, fill=tk.X)
        ttk.Button(self.condition_manage_frame, text="Перевернути 🔄", command=self.reverse_conditions).pack(pady=2, padx=5, fill=tk.X)

        self.category_manage_frame = tk.LabelFrame(self.manage_buttons_frame, text="КАТЕГОРІЯ", bg="#f0f0f0", fg="#333333", font=("Arial", 12, "bold"))
        self.category_manage_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Button(self.category_manage_frame, text="Додати ➕", command=self.add_to_categories).pack(pady=2, padx=5, fill=tk.X)
        ttk.Button(self.category_manage_frame, text="Редагувати ✏️", command=self.edit_category).pack(pady=2, padx=5, fill=tk.X)
        ttk.Button(self.category_manage_frame, text="Видалити 🗑️", command=self.delete_from_categories).pack(pady=2, padx=5, fill=tk.X)
        ttk.Button(self.category_manage_frame, text="Сортувати 🔢", command=self.sort_categories).pack(pady=2, padx=5, fill=tk.X)
        ttk.Button(self.category_manage_frame, text="Перевернути 🔄", command=self.reverse_categories).pack(pady=2, padx=5, fill=tk.X)

        # --- Вкладка "Перегляд" ---
        self.browse_info_frame = tk.Frame(self.browse_tab, bg="#f0f0f0", bd=2, relief="groove")
        self.browse_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Індикатор поточного артефакту
        self.browse_index_label = tk.Label(self.browse_info_frame, text="", bg="#f0f0f0", fg="#333333", font=("Arial", 12))
        self.browse_index_label.pack(pady=5)

        self.browse_image_label = tk.Label(self.browse_info_frame, bg="#f0f0f0")
        self.browse_image_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.browse_info_label = tk.Label(self.browse_info_frame, text="", justify="left", bg="#f0f0f0", fg="#333333", font=("Arial", 12), wraplength=400)
        self.browse_info_label.pack(side=tk.RIGHT, pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.nav_frame = tk.Frame(self.browse_tab, bg="#f0f0f0")
        self.nav_frame.pack(pady=10)
        ttk.Button(self.nav_frame, text="До першого ⏮️", command=self.show_first_artifact).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.nav_frame, text="Попередній артефакт ⬅️", command=self.show_prev_artifact).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.nav_frame, text="Наступний артефакт ➡", command=self.show_next_artifact).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.nav_frame, text="До останнього ⏭️", command=self.show_last_artifact).pack(side=tk.LEFT, padx=5)

        # --- Вкладка "Додавання артефактів" ---
        self.add_main_frame = tk.Frame(self.add_tab, bg="#f0f0f0")
        self.add_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.add_left_frame = tk.Frame(self.add_main_frame, bg="#f0f0f0", bd=2, relief="groove")
        self.add_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(self.add_left_frame, text="Вибрана фото:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.add_image_display_label = tk.Label(self.add_left_frame, bg="#f0f0f0")
        self.add_image_display_label.pack(pady=5)

        self.add_image_path = tk.StringVar(value="")
        self.add_image_label = tk.Label(self.add_left_frame, text="Фото не вибрано", bg="#f0f0f0", fg="#333333", font=("Arial", 12))
        self.add_image_label.pack(pady=5)
        ttk.Button(self.add_left_frame, text="Вибрати фото 📷", command=self.select_image).pack(pady=5)

        self.add_right_frame = tk.Frame(self.add_main_frame, bg="#f0f0f0", bd=2, relief="groove")
        self.add_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(self.add_right_frame, text="Назва артефакту:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.add_name_entry = tk.Entry(self.add_right_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.add_name_entry.pack(pady=5)

        tk.Label(self.add_right_frame, text="Вік (років):", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.add_age_entry = tk.Entry(self.add_right_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.add_age_entry.pack(pady=5)

        tk.Label(self.add_right_frame, text="Походження:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.add_origin_entry = tk.Entry(self.add_right_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.add_origin_entry.pack(pady=5)

        tk.Label(self.add_right_frame, text="Матеріал:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.add_material_entry = tk.Entry(self.add_right_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.add_material_entry.pack(pady=5)

        tk.Label(self.add_right_frame, text="Опис:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.add_description_entry = tk.Entry(self.add_right_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.add_description_entry.pack(pady=5)

        tk.Label(self.add_right_frame, text="Стан:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.add_condition_var = tk.StringVar(value=self.conditions[0] if self.conditions else "")
        self.add_condition_menu = ttk.OptionMenu(self.add_right_frame, self.add_condition_var, self.add_condition_var.get(), *self.conditions)
        self.add_condition_menu.pack(pady=5)

        tk.Label(self.add_right_frame, text="Категорія:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.add_category_var = tk.StringVar(value=self.categories[0] if self.categories else "")
        self.add_category_menu = ttk.OptionMenu(self.add_right_frame, self.add_category_var, self.add_category_var.get(), *self.categories)
        self.add_category_menu.pack(pady=5)

        tk.Label(self.add_right_frame, text="День виявлення:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.add_day_var = tk.StringVar(value=self.days_of_week[0] if self.days_of_week else "")
        self.add_day_menu = ttk.OptionMenu(self.add_right_frame, self.add_day_var, self.add_day_var.get(), *self.days_of_week)
        self.add_day_menu.pack(pady=5)

        tk.Label(self.add_right_frame, text="Статус:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.add_status_var = tk.StringVar(value=self.statuses[0] if self.statuses else "")
        self.add_status_menu = ttk.OptionMenu(self.add_right_frame, self.add_status_var, self.add_status_var.get(), *self.statuses)
        self.add_status_menu.pack(pady=5)

        self.add_bottom_frame = tk.Frame(self.add_tab, bg="#f0f0f0")
        self.add_bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(self.add_bottom_frame, text="Додати артефакт ➕", command=self.add_artifact).pack(pady=10)

        # --- Вкладка "Редагування артефактів" ---
        self.edit_main_frame = tk.Frame(self.edit_tab, bg="#f0f0f0")
        self.edit_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.edit_left_frame = tk.Frame(self.edit_main_frame, bg="#f0f0f0", bd=2, relief="groove")
        self.edit_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(self.edit_left_frame, text="Вибраний артефакт:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.edit_artifact_listbox = tk.Listbox(self.edit_left_frame, height=15, width=30, bg="#ffffff", fg="#333333", font=("Arial", 10))
        self.edit_artifact_listbox.pack(pady=5)
        self.update_edit_artifact_listbox()
        self.edit_artifact_listbox.bind("<<ListboxSelect>>", self.on_edit_artifact_select)

        self.edit_image_display_label = tk.Label(self.edit_left_frame, bg="#f0f0f0")
        self.edit_image_display_label.pack(pady=5)

        self.edit_image_path = tk.StringVar(value="")
        self.edit_image_label = tk.Label(self.edit_left_frame, text="Фото не вибрано", bg="#f0f0f0", fg="#333333", font=("Arial", 12))
        self.edit_image_label.pack(pady=5)
        ttk.Button(self.edit_left_frame, text="Вибрати нове фото 📷", command=self.select_edit_image).pack(pady=5)

        self.edit_right_frame = tk.Frame(self.edit_main_frame, bg="#f0f0f0", bd=2, relief="groove")
        self.edit_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(self.edit_right_frame, text="Назва артефакту:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.edit_name_entry = tk.Entry(self.edit_right_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.edit_name_entry.pack(pady=5)

        tk.Label(self.edit_right_frame, text="Вік (років):", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.edit_age_entry = tk.Entry(self.edit_right_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.edit_age_entry.pack(pady=5)

        tk.Label(self.edit_right_frame, text="Походження:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.edit_origin_entry = tk.Entry(self.edit_right_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.edit_origin_entry.pack(pady=5)

        tk.Label(self.edit_right_frame, text="Матеріал:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.edit_material_entry = tk.Entry(self.edit_right_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.edit_material_entry.pack(pady=5)

        tk.Label(self.edit_right_frame, text="Опис:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.edit_description_entry = tk.Entry(self.edit_right_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.edit_description_entry.pack(pady=5)

        tk.Label(self.edit_right_frame, text="Стан:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.edit_condition_var = tk.StringVar(value=self.conditions[0] if self.conditions else "")
        self.edit_condition_menu = ttk.OptionMenu(self.edit_right_frame, self.edit_condition_var, self.edit_condition_var.get(), *self.conditions)
        self.edit_condition_menu.pack(pady=5)

        tk.Label(self.edit_right_frame, text="Категорія:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.edit_category_var = tk.StringVar(value=self.categories[0] if self.categories else "")
        self.edit_category_menu = ttk.OptionMenu(self.edit_right_frame, self.edit_category_var, self.edit_category_var.get(), *self.categories)
        self.edit_category_menu.pack(pady=5)

        tk.Label(self.edit_right_frame, text="День виявлення:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.edit_day_var = tk.StringVar(value=self.days_of_week[0] if self.days_of_week else "")
        self.edit_day_menu = ttk.OptionMenu(self.edit_right_frame, self.edit_day_var, self.edit_day_var.get(), *self.days_of_week)
        self.edit_day_menu.pack(pady=5)

        tk.Label(self.edit_right_frame, text="Статус:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.edit_status_var = tk.StringVar(value=self.statuses[0] if self.statuses else "")
        self.edit_status_menu = ttk.OptionMenu(self.edit_right_frame, self.edit_status_var, self.edit_status_var.get(), *self.statuses)
        self.edit_status_menu.pack(pady=5)

        self.edit_bottom_frame = tk.Frame(self.edit_tab, bg="#f0f0f0")
        self.edit_bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(self.edit_bottom_frame, text="Зберегти зміни 💾", command=self.save_artifact_changes).pack(pady=10)

        # Вкладка "Видалення артефактів"
        self.delete_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.delete_tab, text="Видалення артефактів")

        self.delete_main_frame = tk.Frame(self.delete_tab, bg="#f0f0f0")
        self.delete_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.delete_left_frame = tk.Frame(self.delete_main_frame, bg="#f0f0f0", bd=2, relief="groove")
        self.delete_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(self.delete_left_frame, text="Виберіть артефакт для видалення:", bg="#f0f0f0", fg="#333333",
                 font=("Arial", 12)).pack(pady=5)
        self.delete_artifact_listbox = tk.Listbox(self.delete_left_frame, height=15, width=30, bg="#ffffff",
                                                  fg="#333333", font=("Arial", 10))
        self.delete_artifact_listbox.pack(pady=5)
        self.update_delete_artifact_listbox()

        self.delete_image_display_label = tk.Label(self.delete_left_frame, bg="#f0f0f0")
        self.delete_image_display_label.pack(pady=5)

        self.delete_artifact_listbox.bind("<<ListboxSelect>>", self.on_delete_artifact_select)

        self.delete_right_frame = tk.Frame(self.delete_main_frame, bg="#f0f0f0", bd=2, relief="groove")
        self.delete_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.delete_info_label = tk.Label(self.delete_right_frame, text="Виберіть артефакт для перегляду деталей",
                                          justify="left", bg="#f0f0f0", fg="#333333", font=("Arial", 12),
                                          wraplength=400)
        self.delete_info_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.delete_bottom_frame = tk.Frame(self.delete_tab, bg="#f0f0f0")
        self.delete_bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(self.delete_bottom_frame, text="Видалити артефакт 🗑️", command=self.delete_artifact).pack(pady=10)

        self.current_artifact = None
        self.show_artifact()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


    def load_data(self):
        if os.path.exists(BIN_FILE):
            try:
                with open(BIN_FILE, "rb") as f:
                    data = pickle.load(f)
                    self.conditions = data.get("conditions", ["Відмінний", "Добрий", "Задовільний", "Поганий"])
                    self.categories = data.get("categories", ["Реліквія", "Скарб", "Документ", "Скульптура"])
                    self.days_of_week = tuple(data.get("days_of_week", ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]))
                    self.statuses = tuple(data.get("statuses", ["На виставці", "У сховищі", "На реставрації", "Втрачений"]))
                    self.max_list_size = data.get("max_list_size", 10)
                    self.artifacts = []
                    for artifact_data in data.get("artifacts", []):
                        try:
                            age = str(artifact_data["age"]).replace(" ", "")
                            artifact_data["age"] = age
                            self.artifacts.append(DetailedArtifact.from_dict(artifact_data))
                            if "original_image_name" in artifact_data:
                                self.used_image_names.append(artifact_data["original_image_name"])
                        except ValueError:
                            print(f"Помилка: Некоректний вік у артефакті {artifact_data['name']}, вік: {artifact_data['age']}")
                    return
            except Exception as e:
                print(f"Помилка завантаження з бінарного файлу: {e}")

        if os.path.exists(CSV_FILE):
            try:
                with open(CSV_FILE, newline='', encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    self.artifacts = []
                    for row in reader:
                        self.artifacts.append(DetailedArtifact(
                            row["name"], row["age"], row["origin"], row["material"],
                            row["description"], row["condition"], row["category"],
                            row["discovery_day"], row["status"], row["image_path"],
                            row.get("original_image_name", "")
                        ))
                        if row.get("original_image_name"):
                            self.used_image_names.append(row["original_image_name"])
                if os.path.exists("artifacts-lab5.json"):
                    with open("artifacts-lab5.json", "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.conditions = data.get("conditions", ["Відмінний", "Добрий", "Задовільний", "Поганий"])
                        self.categories = data.get("categories", ["Реліквія", "Скарб", "Документ", "Скульптура"])
                        self.days_of_week = tuple(data.get("days_of_week", ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]))
                        self.statuses = tuple(data.get("statuses", ["На виставці", "У сховищі", "На реставрації", "Втрачений"]))
                        self.max_list_size = data.get("max_list_size", 10)
                return
            except Exception as e:
                print(f"Помилка завантаження з CSV-файлу: {e}")

        if os.path.exists(TXT_FILE):
            try:
                with open(TXT_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    self.artifacts = []
                    artifact_data = {}
                    for line in lines:
                        line = line.strip()
                        if line == "-----------------------------------------------------":
                            if artifact_data:
                                self.artifacts.append(DetailedArtifact(
                                    artifact_data["name"], artifact_data["age"], artifact_data["origin"],
                                    artifact_data["material"], artifact_data["description"], artifact_data["condition"],
                                    artifact_data["category"], artifact_data["discovery_day"], artifact_data["status"],
                                    artifact_data["image_path"], artifact_data.get("original_image_name", "")
                                ))
                                if "original_image_name" in artifact_data:
                                    self.used_image_names.append(artifact_data["original_image_name"])
                            artifact_data = {}
                        else:
                            key, value = line.split(": ", 1)
                            artifact_data[key] = value
                if os.path.exists("artifacts-lab5.json"):
                    with open("artifacts-lab5.json", "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.conditions = data.get("conditions", ["Відмінний", "Добрий", "Задовільний", "Поганий"])
                        self.categories = data.get("categories", ["Реліквія", "Скарб", "Документ", "Скульптура"])
                        self.days_of_week = tuple(data.get("days_of_week", ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]))
                        self.statuses = tuple(data.get("statuses", ["На виставці", "У сховищі", "На реставрації", "Втрачений"]))
                        self.max_list_size = data.get("max_list_size", 10)
                return
            except Exception as e:
                print(f"Помилка завантаження з текстового файлу: {e}")

        self.conditions = ["Відмінний", "Добрий", "Задовільний", "Поганий"]
        self.categories = ["Реліквія", "Скарб", "Документ", "Скульптура"]
        self.days_of_week = ("Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя")
        self.statuses = ("На виставці", "У сховищі", "На реставрації", "Втрачений")
        self.max_list_size = 10
        self.artifacts = [
            DetailedArtifact("Маска Тутанхамона", "3300", "Стародавній Єгипет", "Золото, лазурит, бірюза",
                             "Золота похоронна маска фараона", "Відмінний", "Реліквія", "Понеділок", "На виставці", "images//artifact1.jpg"),
            DetailedArtifact("Камінь Розетти", "2250", "Стародавній Єгипет", "Граніт",
                             "Ключ до розшифровки єгипетських ієрогліфів", "Добрий", "Документ", "Середа", "На виставці", "images//artifact2.jpg"),
            DetailedArtifact("Теракотова армія", "2200", "Стародавній Китай", "Глина",
                             "Армія глиняних воїнів імператора", "Задовільний", "Скульптура", "П'ятниця", "У сховищі", "images//artifact3.jpg")
        ]

    def save_data(self):
        data = {
            "conditions": self.conditions,
            "categories": self.categories,
            "days_of_week": list(self.days_of_week),
            "statuses": list(self.statuses),
            "max_list_size": self.max_list_size,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts]
        }
        with open("artifacts-lab5.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        with open(TXT_FILE, "w", encoding="utf-8") as f:
            for artifact in self.artifacts:
                f.write(f"Назва: {artifact.name}\n")
                f.write(f"Вік: {artifact.age}\n")
                f.write(f"Походження: {artifact.origin}\n")
                f.write(f"Матеріал: {artifact.material}\n")
                f.write(f"Опис: {artifact.description}\n")
                f.write(f"Стан: {artifact.condition}\n")
                f.write(f"Категорія: {artifact.category}\n")
                f.write(f"День виявлення: {artifact.discovery_day}\n")
                f.write(f"Статус: {artifact.status}\n")
                f.write(f"Шлях до зображення: {artifact.image_path}\n")
                f.write(f"Оригінальна назва зображення: {artifact.original_image_name}\n")
                f.write("-----------------------------------------------------\n")

        with open(CSV_FILE, "w", newline='', encoding="utf-8") as f:
            fieldnames = ["name", "age", "origin", "material", "description", "condition", "category", "discovery_day", "status", "image_path", "original_image_name"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for artifact in self.artifacts:
                writer.writerow(artifact.to_dict())

        with open(BIN_FILE, "wb") as f:
            pickle.dump(data, f)

    def on_closing(self):
        self.save_data()
        self.root.destroy()

    def update_artifact_listbox(self):
        self.artifact_listbox.delete(0, tk.END)
        for artifact in self.artifacts:
            self.artifact_listbox.insert(tk.END, f"{artifact.name} ({artifact.age} років)")

    def update_edit_artifact_listbox(self):
        self.edit_artifact_listbox.delete(0, tk.END)
        for artifact in self.artifacts:
            self.edit_artifact_listbox.insert(tk.END, f"{artifact.name} ({artifact.age} років)")

    def load_image(self, image_path):
        if not image_path:
            return None
        # Перевірка, чи зображення вже є в кеші
        if image_path in self.image_cache:
            return self.image_cache[image_path]
        try:
            image = Image.open(image_path)
            image = image.resize((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            # Зберігаємо зображення в кеш
            self.image_cache[image_path] = photo
            return photo
        except Exception as e:
            print(f"Помилка завантаження зображення: {e}")
            return None

    def get_next_artifact_name(self):
        max_number = 3
        for artifact in self.artifacts:
            image_name = os.path.basename(artifact.image_path) if artifact.image_path else ""
            if image_name.startswith("artifact") and image_name.endswith(".jpg"):
                try:
                    number = int(image_name[len("artifact"):-len(".jpg")])
                    max_number = max(max_number, number)
                except ValueError:
                    continue
        return f"artifact{max_number + 1}"

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Виберіть фото артефакту",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if file_path:
            original_image_name = os.path.basename(file_path)
            if original_image_name in self.used_image_names:
                messagebox.showerror("Помилка", f"Фото з ім'ям {original_image_name} вже додано!")
                return

            self.add_image_path.set(file_path)
            self.add_image_label.config(text=f"Вибрано: {original_image_name}")
            photo = self.load_image(file_path)
            if photo:
                self.add_image_display_label.config(image=photo)
                self.add_image_display_label.image = photo
            else:
                self.add_image_display_label.config(image="")
        else:
            self.add_image_label.config(text="Фото не вибрано")
            self.add_image_display_label.config(image="")

    def select_edit_image(self):
        file_path = filedialog.askopenfilename(
            title="Виберіть нове фото артефакту",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if file_path:
            original_image_name = os.path.basename(file_path)
            if original_image_name in self.used_image_names and original_image_name != self.artifacts[self.edit_artifact_listbox.curselection()[0]].original_image_name:
                messagebox.showerror("Помилка", f"Фото з ім'ям {original_image_name} вже додано!")
                return

            self.edit_image_path.set(file_path)
            self.edit_image_label.config(text=f"Вибрано: {original_image_name}")
            photo = self.load_image(file_path)
            if photo:
                self.edit_image_display_label.config(image=photo)
                self.edit_image_display_label.image = photo
            else:
                self.edit_image_display_label.config(image="")
        else:
            self.edit_image_label.config(text="Фото не вибрано")
            self.edit_image_display_label.config(image="")

    def add_artifact(self):
        name = self.add_name_entry.get().strip()
        age = self.add_age_entry.get().strip()
        origin = self.add_origin_entry.get().strip()
        material = self.add_material_entry.get().strip()
        description = self.add_description_entry.get().strip()
        condition = self.add_condition_var.get()
        category = self.add_category_var.get()
        discovery_day = self.add_day_var.get()
        status = self.add_status_var.get()
        image_path = self.add_image_path.get()

        if not name or not age or not origin or not material or not description:
            messagebox.showerror("Помилка", "Заповніть усі текстові поля!")
            return
        if not image_path:
            messagebox.showerror("Помилка", "Виберіть фото артефакту!")
            return
        if not age.isdigit() or int(age) <= 0:
            messagebox.showerror("Помилка", "Вік має бути додатним числом!")
            return
        if len(name) > 100:
            messagebox.showerror("Помилка", "Назва артефакту занадто довга (макс. 100 символів)!")
            return

        for artifact in self.artifacts:
            if artifact.name.lower() == name.lower():
                messagebox.showerror("Помилка", "Артефакт з такою назвою вже існує!")
                return

        image_name = self.get_next_artifact_name()
        if not os.path.exists("images"):
            os.makedirs("images")
        new_image_path = os.path.join("images", f"{image_name}.jpg")
        try:
            shutil.copy(image_path, new_image_path)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося скопіювати зображення: {e}")
            return

        original_image_name = os.path.basename(image_path)
        self.used_image_names.append(original_image_name)

        new_artifact = DetailedArtifact(
            name, age, origin, material, description,
            condition, category, discovery_day, status, new_image_path,
            original_image_name
        )

        self.artifacts.append(new_artifact)
        self.update_artifact_listbox()
        self.update_edit_artifact_listbox()
        self.update_delete_artifact_listbox()
        self.save_data()

        self.add_name_entry.delete(0, tk.END)
        self.add_age_entry.delete(0, tk.END)
        self.add_origin_entry.delete(0, tk.END)
        self.add_material_entry.delete(0, tk.END)
        self.add_description_entry.delete(0, tk.END)
        self.add_condition_var.set(self.conditions[0] if self.conditions else "")
        self.add_category_var.set(self.categories[0] if self.categories else "")
        self.add_day_var.set(self.days_of_week[0] if self.days_of_week else "")
        self.add_status_var.set(self.statuses[0] if self.statuses else "")
        self.add_image_path.set("")
        self.add_image_label.config(text="Фото не вибрано")
        self.add_image_display_label.config(image="")

        messagebox.showinfo("Успіх", f"Артефакт {name} успішно додано!")

    def on_edit_artifact_select(self, event):
        if not self.edit_artifact_listbox.curselection():
            return
        index = self.edit_artifact_listbox.curselection()[0]
        artifact = self.artifacts[index]

        self.edit_name_entry.delete(0, tk.END)
        self.edit_name_entry.insert(0, artifact.name)
        self.edit_age_entry.delete(0, tk.END)
        self.edit_age_entry.insert(0, artifact.age)
        self.edit_origin_entry.delete(0, tk.END)
        self.edit_origin_entry.insert(0, artifact.origin)
        self.edit_material_entry.delete(0, tk.END)
        self.edit_material_entry.insert(0, artifact.material)
        self.edit_description_entry.delete(0, tk.END)
        self.edit_description_entry.insert(0, artifact.description)
        self.edit_condition_var.set(artifact.condition)
        self.edit_category_var.set(artifact.category)
        self.edit_day_var.set(artifact.discovery_day)
        self.edit_status_var.set(artifact.status)
        self.edit_image_path.set(artifact.image_path)
        self.edit_image_label.config(text=f"Вибрано: {artifact.original_image_name}")
        photo = self.load_image(artifact.image_path)
        if photo:
            self.edit_image_display_label.config(image=photo)
            self.edit_image_display_label.image = photo
        else:
            self.edit_image_display_label.config(image="")

    def save_artifact_changes(self):
        if not self.edit_artifact_listbox.curselection():
            messagebox.showerror("Помилка", "Виберіть артефакт для редагування!")
            return

        index = self.edit_artifact_listbox.curselection()[0]
        artifact = self.artifacts[index]

        name = self.edit_name_entry.get().strip()
        age = self.edit_age_entry.get().strip()
        origin = self.edit_origin_entry.get().strip()
        material = self.edit_material_entry.get().strip()
        description = self.edit_description_entry.get().strip()
        condition = self.edit_condition_var.get()
        category = self.edit_category_var.get()
        discovery_day = self.edit_day_var.get()
        status = self.edit_status_var.get()
        image_path = self.edit_image_path.get()

        if not name or not age or not origin or not material or not description:
            messagebox.showerror("Помилка", "Заповніть усі текстові поля!")
            return
        if not image_path:
            messagebox.showerror("Помилка", "Виберіть фото артефакту!")
            return
        if not age.isdigit() or int(age) <= 0:
            messagebox.showerror("Помилка", "Вік має бути додатним числом!")
            return
        if len(name) > 100:
            messagebox.showerror("Помилка", "Назва артефакту занадто довга (макс. 100 символів)!")
            return

        for i, art in enumerate(self.artifacts):
            if i != index and art.name.lower() == name.lower():
                messagebox.showerror("Помилка", "Артефакт з такою назвою вже існує!")
                return

        # Якщо вибрано нове зображення, оновлюємо його
        if image_path != artifact.image_path:
            image_name = self.get_next_artifact_name()
            new_image_path = os.path.join("images", f"{image_name}.jpg")
            try:
                shutil.copy(image_path, new_image_path)
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося скопіювати зображення: {e}")
                return
            # Видаляємо старе зображення з кешу
            if artifact.image_path in self.image_cache:
                del self.image_cache[artifact.image_path]
            # Оновлюємо шлях до зображення
            artifact.image_path = new_image_path
            artifact.original_image_name = os.path.basename(image_path)
            self.used_image_names.remove(artifact.original_image_name)
            self.used_image_names.append(artifact.original_image_name)

        artifact.name = name
        artifact.age = age
        artifact.origin = origin
        artifact.material = material
        artifact.description = description
        artifact.condition = condition
        artifact.category = category
        artifact.discovery_day = discovery_day
        artifact.status = status

        self.update_artifact_listbox()
        self.update_edit_artifact_listbox()
        self.save_data()
        messagebox.showinfo("Успіх", f"Артефакт {name} успішно відредаговано!")

    def add_to_conditions(self):
        new_value = self.new_value_entry.get().strip()
        if not new_value:
            messagebox.showerror("Помилка", "Введіть нове значення!")
            return
        if len(new_value) > 50:
            messagebox.showerror("Помилка", "Значення занадто довге (макс. 50 символів)!")
            return
        if len(self.conditions) >= self.max_list_size:
            messagebox.showerror("Помилка", f"Список станів перевищує ліміт ({self.max_list_size})!")
            return
        if new_value not in self.conditions:
            self.conditions.append(new_value)
            self.condition_menu["menu"].add_command(label=new_value, command=lambda v=new_value: self.condition_var.set(v))
            self.add_condition_menu["menu"].add_command(label=new_value, command=lambda v=new_value: self.add_condition_var.set(v))
            self.edit_condition_menu["menu"].add_command(label=new_value, command=lambda v=new_value: self.edit_condition_var.set(v))
            self.new_value_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Помилка", "Це значення вже є у списку!")

    def add_to_categories(self):
        new_value = self.new_value_entry.get().strip()
        if not new_value:
            messagebox.showerror("Помилка", "Введіть нове значення!")
            return
        if len(new_value) > 50:
            messagebox.showerror("Помилка", "Значення занадто довге (макс. 50 символів)!")
            return
        if len(self.categories) >= self.max_list_size:
            messagebox.showerror("Помилка", f"Список категорій перевищує ліміт ({self.max_list_size})!")
            return
        if new_value not in self.categories:
            self.categories.append(new_value)
            self.category_menu["menu"].add_command(label=new_value, command=lambda v=new_value: self.category_var.set(v))
            self.add_category_menu["menu"].add_command(label=new_value, command=lambda v=new_value: self.add_category_var.set(v))
            self.edit_category_menu["menu"].add_command(label=new_value, command=lambda v=new_value: self.edit_category_var.set(v))
            self.new_value_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Помилка", "Це значення вже є у списку!")

    def edit_condition(self):
        if self.condition_var.get() == "Усі":
            messagebox.showerror("Помилка", "Виберіть стан для редагування!")
            return
        new_value = self.new_value_entry.get().strip()
        if not new_value:
            messagebox.showerror("Помилка", "Введіть нове значення!")
            return
        if len(new_value) > 50:
            messagebox.showerror("Помилка", "Значення занадто довге (макс. 50 символів)!")
            return
        old_value = self.condition_var.get()
        index = self.conditions.index(old_value)
        self.conditions[index] = new_value
        self.condition_menu["menu"].delete(old_value)
        self.condition_menu["menu"].add_command(label=new_value, command=lambda v=new_value: self.condition_var.set(v))
        self.add_condition_menu["menu"].delete(old_value)
        self.add_condition_menu["menu"].add_command(label=new_value, command=lambda v=new_value: self.add_condition_var.set(v))
        self.edit_condition_menu["menu"].delete(old_value)
        self.edit_condition_menu["menu"].add_command(label=new_value, command=lambda v=new_value: self.edit_condition_var.set(v))
        self.condition_var.set(new_value)
        for artifact in self.artifacts:
            if artifact.condition == old_value:
                artifact.condition = new_value
        if self.current_artifact and self.current_artifact.condition == old_value:
            self.current_artifact.condition = new_value
            self.update_info_labels()

    def edit_category(self):
        if self.category_var.get() == "Усі":
            messagebox.showerror("Помилка", "Виберіть категорію для редагування!")
            return
        new_value = self.new_value_entry.get().strip()
        if not new_value:
            messagebox.showerror("Помилка", "Введіть нове значення!")
            return
        if len(new_value) > 50:
            messagebox.showerror("Помилка", "Значення занадто довге (макс. 50 символів)!")
            return
        old_value = self.category_var.get()
        index = self.categories.index(old_value)
        self.categories[index] = new_value
        self.category_menu["menu"].delete(old_value)
        self.category_menu["menu"].add_command(label=new_value, command=lambda v=new_value: self.category_var.set(v))
        self.add_category_menu["menu"].delete(old_value)
        self.add_category_menu["menu"].add_command(label=new_value, command=lambda v=new_value: self.add_category_var.set(v))
        self.edit_category_menu["menu"].delete(old_value)
        self.edit_category_menu["menu"].add_command(label=new_value, command=lambda v=new_value: self.edit_category_var.set(v))
        self.category_var.set(new_value)
        for artifact in self.artifacts:
            if artifact.category == old_value:
                artifact.category = new_value
        if self.current_artifact and self.current_artifact.category == old_value:
            self.current_artifact.category = new_value
            self.update_info_labels()

    def delete_from_conditions(self):
        if self.condition_var.get() == "Усі":
            messagebox.showerror("Помилка", "Виберіть стан для видалення!")
            return
        value = self.condition_var.get()
        for artifact in self.artifacts:
            if artifact.condition == value:
                messagebox.showerror("Помилка", "Цей стан використовується в артефактах!")
                return
        if not messagebox.askyesno("Підтвердження", f"Ви впевнені, що хочете видалити стан '{value}'?"):
            return
        self.conditions.remove(value)
        self.condition_menu["menu"].delete(value)
        self.add_condition_menu["menu"].delete(value)
        self.edit_condition_menu["menu"].delete(value)
        self.condition_var.set("Усі")
        self.add_condition_var.set(self.conditions[0] if self.conditions else "")

    def delete_from_categories(self):
        if self.category_var.get() == "Усі":
            messagebox.showerror("Помилка", "Виберіть категорію для видалення!")
            return
        value = self.category_var.get()
        for artifact in self.artifacts:
            if artifact.category == value:
                messagebox.showerror("Помилка", "Ця категорія використовується в артефактах!")
                return
        if not messagebox.askyesno("Підтвердження", f"Ви впевнені, що хочете видалити категорію '{value}'?"):
            return
        self.categories.remove(value)
        self.category_menu["menu"].delete(value)
        self.add_category_menu["menu"].delete(value)
        self.edit_category_menu["menu"].delete(value)
        self.category_var.set("Усі")
        self.add_category_var.set(self.categories[0] if self.categories else "")

    def sort_conditions(self):
        self.conditions.sort()
        self.condition_menu["menu"].delete(0, tk.END)
        self.condition_menu["menu"].add_command(label="Усі", command=lambda: self.condition_var.set("Усі"))
        for condition in self.conditions:
            self.condition_menu["menu"].add_command(label=condition, command=lambda v=condition: self.condition_var.set(v))
        self.add_condition_menu["menu"].delete(0, tk.END)
        for condition in self.conditions:
            self.add_condition_menu["menu"].add_command(label=condition, command=lambda v=condition: self.add_condition_var.set(v))
        self.edit_condition_menu["menu"].delete(0, tk.END)
        for condition in self.conditions:
            self.edit_condition_menu["menu"].add_command(label=condition, command=lambda v=condition: self.edit_condition_var.set(v))
        self.condition_var.set("Усі")
        self.add_condition_var.set(self.conditions[0] if self.conditions else "")

    def sort_categories(self):
        self.categories.sort()
        self.category_menu["menu"].delete(0, tk.END)
        self.category_menu["menu"].add_command(label="Усі", command=lambda: self.category_var.set("Усі"))
        for category in self.categories:
            self.category_menu["menu"].add_command(label=category, command=lambda v=category: self.category_var.set(v))
        self.add_category_menu["menu"].delete(0, tk.END)
        for category in self.categories:
            self.add_category_menu["menu"].add_command(label=category, command=lambda v=category: self.add_category_var.set(v))
        self.edit_category_menu["menu"].delete(0, tk.END)
        for category in self.categories:
            self.edit_category_menu["menu"].add_command(label=category, command=lambda v=category: self.edit_category_var.set(v))
        self.category_var.set("Усі")
        self.add_category_var.set(self.categories[0] if self.categories else "")

    def reverse_conditions(self):
        self.conditions.reverse()
        self.condition_menu["menu"].delete(0, tk.END)
        self.condition_menu["menu"].add_command(label="Усі", command=lambda: self.condition_var.set("Усі"))
        for condition in self.conditions:
            self.condition_menu["menu"].add_command(label=condition, command=lambda v=condition: self.condition_var.set(v))
        self.add_condition_menu["menu"].delete(0, tk.END)
        for condition in self.conditions:
            self.add_condition_menu["menu"].add_command(label=condition, command=lambda v=condition: self.add_condition_var.set(v))
        self.edit_condition_menu["menu"].delete(0, tk.END)
        for condition in self.conditions:
            self.edit_condition_menu["menu"].add_command(label=condition, command=lambda v=condition: self.edit_condition_var.set(v))
        self.condition_var.set("Усі")
        self.add_condition_var.set(self.conditions[0] if self.conditions else "")

    def reverse_categories(self):
        self.categories.reverse()
        self.category_menu["menu"].delete(0, tk.END)
        self.category_menu["menu"].add_command(label="Усі", command=lambda: self.category_var.set("Усі"))
        for category in self.categories:
            self.category_menu["menu"].add_command(label=category, command=lambda v=category: self.category_var.set(v))
        self.add_category_menu["menu"].delete(0, tk.END)
        for category in self.categories:
            self.add_category_menu["menu"].add_command(label=category, command=lambda v=category: self.add_category_var.set(v))
        self.edit_category_menu["menu"].delete(0, tk.END)
        for category in self.categories:
            self.edit_category_menu["menu"].add_command(label=category, command=lambda v=category: self.edit_category_var.set(v))
        self.category_var.set("Усі")
        self.add_category_var.set(self.categories[0] if self.categories else "")

    def clear_placeholder(self, event):
        if self.search_entry.get() == "Введіть запит для пошуку":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="#333333")

    def add_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Введіть запит для пошуку")
            self.search_entry.config(fg="gray50")

    def update_info_labels(self):
        if self.current_artifact:
            self.search_info_label.config(text=self.current_artifact.get_full_info())
            self.browse_info_label.config(text=self.current_artifact.get_full_info())
            self.current_image = self.load_image(self.current_artifact.image_path)
            if self.current_image:
                self.browse_image_label.config(image=self.current_image)
            else:
                self.browse_image_label.config(image="")

    def search_artifact(self):
        query = self.search_entry.get().strip().lower()
        if not query or query == "введіть запит для пошуку":
            messagebox.showerror("Помилка", "Введіть запит для пошуку!")
            return

        if query.isdigit():
            try:
                age = int(query)
                if age <= 0:
                    messagebox.showerror("Помилка", "Вік має бути додатним числом!")
                    return
            except ValueError:
                messagebox.showerror("Помилка", "Некоректне значення віку!")
                return
        else:
            if len(query) > 100:
                messagebox.showerror("Помилка", "Назва занадто довга (макс. 100 символів)!")
                return

        matching_artifacts = []
        for artifact in self.artifacts:
            matches_query = query == artifact.name.lower() or query == artifact.age
            if matches_query:
                matching_artifacts.append(artifact)

        if matching_artifacts:
            result_text = "Знайдені артефакти:\n\n"
            for artifact in matching_artifacts:
                result_text += artifact.get_full_info()
            self.search_info_label.config(text=result_text)

            self.current_image = self.load_image(matching_artifacts[0].image_path)
            if self.current_image:
                self.search_image_label.config(image=self.current_image)
            else:
                self.search_image_label.config(image="")
        else:
            self.search_info_label.config(text="Артефакт не знайдено")
            self.search_image_label.config(image="")

    def filter_search(self):
        selected_condition = self.condition_var.get()
        selected_category = self.category_var.get()
        selected_day = self.day_var.get()
        selected_status = self.status_var.get()

        filters_used = (
            selected_condition != "Усі" or
            selected_category != "Усі" or
            selected_day != "Усі" or
            selected_status != "Усі"
        )

        if not filters_used:
            messagebox.showerror("Помилка", "Виберіть хоча б один фільтр!")
            return

        matching_artifacts = []
        for artifact in self.artifacts:
            matches_condition = selected_condition == "Усі" or artifact.condition == selected_condition
            matches_category = selected_category == "Усі" or artifact.category == selected_category
            matches_day = selected_day == "Усі" or artifact.discovery_day == selected_day
            matches_status = selected_status == "Усі" or artifact.status == selected_status

            if matches_condition and matches_category and matches_day and matches_status:
                matching_artifacts.append(artifact)

        if matching_artifacts:
            result_text = "Знайдені артефакти:\n\n"
            for artifact in matching_artifacts:
                result_text += artifact.get_full_info() + "\n" + "-"*50 + "\n"
            self.search_info_label.config(text=result_text)

            self.current_image = self.load_image(matching_artifacts[0].image_path)
            if self.current_image:
                self.search_image_label.config(image=self.current_image)
            else:
                self.search_image_label.config(image="")
        else:
            self.search_info_label.config(text="Артефакт не знайдено")
            self.search_image_label.config(image="")

    def show_artifact(self):
        if not self.artifacts:
            self.browse_info_label.config(text="Немає артефактів для відображення")
            self.browse_image_label.config(image="")
            self.browse_index_label.config(text="")
            return
        self.current_artifact = self.artifacts[self.current_artifact_index]
        self.browse_info_label.config(text=self.current_artifact.get_full_info())
        self.current_image = self.load_image(self.current_artifact.image_path)
        if self.current_image:
            self.browse_image_label.config(image=self.current_image)
        else:
            self.browse_image_label.config(image="")
        self.browse_index_label.config(text=f"Артефакт {self.current_artifact_index + 1} з {len(self.artifacts)}")

    def show_next_artifact(self):
        if not self.artifacts:
            return
        if self.current_artifact_index >= len(self.artifacts) - 1:
            return
        self.current_artifact_index += 1
        self.show_artifact()

    def show_prev_artifact(self):
        if not self.artifacts:
            return
        if self.current_artifact_index <= 0:
            return
        self.current_artifact_index -= 1
        self.show_artifact()

    def show_first_artifact(self):
        if not self.artifacts:
            return
        self.current_artifact_index = 0
        self.show_artifact()

    def show_last_artifact(self):
        if not self.artifacts:
            return
        self.current_artifact_index = len(self.artifacts) - 1
        self.show_artifact()

    def show_lists(self):
        # Створюємо нове вікно для відображення списків
        lists_window = Toplevel(self.root)
        lists_window.title("Списки станів і категорій")

        # Розмір вікна
        window_width = 400
        window_height = 400

        # Отримуємо розміри екрану
        screen_width = lists_window.winfo_screenwidth()
        screen_height = lists_window.winfo_screenheight()

        # Обчислюємо координати для центру екрану
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Встановлюємо розмір і позицію вікна
        lists_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Фрейм для списків
        lists_frame = tk.Frame(lists_window, bg="#f0f0f0")
        lists_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Список станів
        conditions_frame = tk.LabelFrame(lists_frame, text="СТАНИ", bg="#f0f0f0", fg="#333333",
                                         font=("Arial", 12, "bold"))
        conditions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        conditions_listbox = tk.Listbox(conditions_frame, height=5, bg="#ffffff", fg="#333333", font=("Arial", 10))
        conditions_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        for condition in self.conditions:
            conditions_listbox.insert(tk.END, condition)

        # Список категорій
        categories_frame = tk.LabelFrame(lists_frame, text="КАТЕГОРІЇ", bg="#f0f0f0", fg="#333333",
                                         font=("Arial", 12, "bold"))
        categories_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        categories_listbox = tk.Listbox(categories_frame, height=5, bg="#ffffff", fg="#333333", font=("Arial", 10))
        categories_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        for category in self.categories:
            categories_listbox.insert(tk.END, category)

    def update_delete_artifact_listbox(self):
        self.delete_artifact_listbox.delete(0, tk.END)
        for artifact in self.artifacts:
            self.delete_artifact_listbox.insert(tk.END, f"{artifact.name} ({artifact.age} років)")

    def on_delete_artifact_select(self, event):
        if not self.delete_artifact_listbox.curselection():
            return
        index = self.delete_artifact_listbox.curselection()[0]
        artifact = self.artifacts[index]

        self.delete_info_label.config(text=artifact.get_full_info())
        photo = self.load_image(artifact.image_path)
        if photo:
            self.delete_image_display_label.config(image=photo)
            self.delete_image_display_label.image = photo
        else:
            self.delete_image_display_label.config(image="")

    def delete_artifact(self):
        if not self.delete_artifact_listbox.curselection():
            messagebox.showerror("Помилка", "Виберіть артефакт для видалення!")
            return

        index = self.delete_artifact_listbox.curselection()[0]
        artifact = self.artifacts[index]

        if not messagebox.askyesno("Підтвердження", f"Ви впевнені, що хочете видалити артефакт '{artifact.name}'?"):
            return

        # Видаляємо зображення з файлової системи
        if artifact.image_path and os.path.exists(artifact.image_path):
            try:
                os.remove(artifact.image_path)
            except Exception as e:
                messagebox.showwarning("Попередження", f"Не вдалося видалити зображення: {e}")

        # Видаляємо зображення з кешу
        if artifact.image_path in self.image_cache:
            del self.image_cache[artifact.image_path]

        # Видаляємо оригінальну назву зображення зі списку використаних
        if artifact.original_image_name in self.used_image_names:
            self.used_image_names.remove(artifact.original_image_name)

        # Видаляємо артефакт зі списку
        self.artifacts.pop(index)

        # Оновлюємо всі списки
        self.update_artifact_listbox()
        self.update_edit_artifact_listbox()
        self.update_delete_artifact_listbox()

        # Очищаємо відображення
        self.delete_info_label.config(text="Виберіть артефакт для перегляду деталей")
        self.delete_image_display_label.config(image="")

        # Оновлюємо індекс для перегляду, якщо потрібно
        if self.current_artifact_index >= len(self.artifacts) and self.artifacts:
            self.current_artifact_index = len(self.artifacts) - 1
        elif not self.artifacts:
            self.current_artifact_index = 0
        self.show_artifact()

        # Зберігаємо зміни у файли
        self.save_data()
        messagebox.showinfo("Успіх", f"Артефакт '{artifact.name}' успішно видалено!")

if __name__ == "__main__":
        root = tk.Tk()
        app = ArtifactApp(root)
        root.mainloop()