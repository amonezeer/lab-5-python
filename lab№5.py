import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
import os
import shutil
from PIL import Image, ImageTk
import csv
import pickle

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
    def __init__(self, name, age, origin, material, description, condition, category, discovery_day, status, image_path):
        super().__init__(name, age, origin, material)
        self.description = description
        self.condition = condition
        self.category = category
        self.discovery_day = discovery_day
        self.status = status
        self.image_path = image_path

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
            "image_path": self.image_path
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"], data["age"], data["origin"], data["material"],
            data["description"], data["condition"], data["category"],
            data["discovery_day"], data["status"], data.get("image_path", "")
        )

# Клас для графічного інтерфейсу
class ArtifactApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Каталог артефактів")
        self.root.geometry("1209x804")

        # Налаштування стилів
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", foreground="#333333")
        style.configure("TButton", background="#d0d0d0", foreground="#333333")
        style.map("TButton", background=[("active", "#b0b0b0")])
        self.root.configure(bg="#f0f0f0")

        # Шлях до папки для збереження файлів
        self.storage_path = r"C:\Users\Александр\PycharmProjects\University\Yusypiv"
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

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

        # Вкладка "Управління списками"
        self.manage_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manage_tab, text="Управління списками")

        # Вкладка "Додавання артефактів"
        self.add_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_tab, text="Додавання артефактів")

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
        ttk.Button(self.search_frame, text="Пошук", command=self.search_artifact).pack(side=tk.LEFT, padx=5)

        self.main_search_frame = tk.Frame(self.search_tab, bg="#f0f0f0")
        self.main_search_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.artifact_list_frame = tk.Frame(self.main_search_frame, bg="#f0f0f0", bd=2, relief="groove")
        self.artifact_list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        tk.Label(self.artifact_list_frame, text="Доступні артефакти:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.artifact_listbox = tk.Listbox(self.artifact_list_frame, height=15, width=30, bg="#ffffff", fg="#333333", font=("Arial", 10))
        self.artifact_listbox.pack(pady=5)
        self.update_artifact_listbox()

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

        self.search_info_frame = tk.Frame(self.search_tab, bg="#f0f0f0", bd=2, relief="groove")
        self.search_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.search_image_label = tk.Label(self.search_info_frame, bg="#f0f0f0")
        self.search_image_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.search_info_label = tk.Label(self.search_info_frame, text="", justify="left", bg="#f0f0f0", fg="#333333", font=("Arial", 12), wraplength=400)
        self.search_info_label.pack(side=tk.RIGHT, pady=10, padx=10, fill=tk.BOTH, expand=True)

        # --- Вкладка "Перегляд" ---
        self.browse_info_frame = tk.Frame(self.browse_tab, bg="#f0f0f0", bd=2, relief="groove")
        self.browse_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.browse_image_label = tk.Label(self.browse_info_frame, bg="#f0f0f0")
        self.browse_image_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.browse_info_label = tk.Label(self.browse_info_frame, text="", justify="left", bg="#f0f0f0", fg="#333333", font=("Arial", 12), wraplength=400)
        self.browse_info_label.pack(side=tk.RIGHT, pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.nav_frame = tk.Frame(self.browse_tab, bg="#f0f0f0")
        self.nav_frame.pack(pady=10)
        ttk.Button(self.nav_frame, text="Попередній артефакт", command=self.show_prev_artifact).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.nav_frame, text="Наступний артефакт", command=self.show_next_artifact).pack(side=tk.LEFT, padx=5)

        # --- Вкладка "Управління списками" ---
        self.manage_input_frame = tk.Frame(self.manage_tab, bg="#f0f0f0", bd=2, relief="groove")
        self.manage_input_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(self.manage_input_frame, text="Нове значення:", bg="#f0f0f0", fg="#333333", font=("Arial", 12)).pack(pady=5)
        self.new_value_entry = tk.Entry(self.manage_input_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#333333")
        self.new_value_entry.pack(pady=5)

        self.manage_buttons_frame = tk.Frame(self.manage_tab, bg="#f0f0f0")
        self.manage_buttons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.condition_frame = tk.LabelFrame(self.manage_buttons_frame, text="Управління списком 'Стан'", bg="#f0f0f0", fg="#333333", font=("Arial", 12, "bold"))
        self.condition_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Button(self.condition_frame, text="Додати до стану", command=self.add_to_conditions).pack(pady=5, padx=10, fill=tk.X)
        ttk.Button(self.condition_frame, text="Редагувати стан", command=self.edit_condition).pack(pady=5, padx=10, fill=tk.X)
        ttk.Button(self.condition_frame, text="Видалити зі стану", command=self.delete_from_conditions).pack(pady=5, padx=10, fill=tk.X)
        ttk.Button(self.condition_frame, text="Сортувати стан", command=self.sort_conditions).pack(pady=5, padx=10, fill=tk.X)
        ttk.Button(self.condition_frame, text="Перевернути стан", command=self.reverse_conditions).pack(pady=5, padx=10, fill=tk.X)

        self.category_frame = tk.LabelFrame(self.manage_buttons_frame, text="Управління списком 'Категорія'", bg="#f0f0f0", fg="#333333", font=("Arial", 12, "bold"))
        self.category_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Button(self.category_frame, text="Додати до категорії", command=self.add_to_categories).pack(pady=5, padx=10, fill=tk.X)
        ttk.Button(self.category_frame, text="Редагувати категорію", command=self.edit_category).pack(pady=5, padx=10, fill=tk.X)
        ttk.Button(self.category_frame, text="Видалити з категорії", command=self.delete_from_categories).pack(pady=5, padx=10, fill=tk.X)
        ttk.Button(self.category_frame, text="Сортувати категорію", command=self.sort_categories).pack(pady=5, padx=10, fill=tk.X)
        ttk.Button(self.category_frame, text="Перевернути категорію", command=self.reverse_categories).pack(pady=5, padx=10, fill=tk.X)

        self.check_frame = tk.Frame(self.manage_tab, bg="#f0f0f0", bd=2, relief="groove")
        self.check_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(self.check_frame, text="Перевірити списки", command=self.check_lists).pack(pady=5)

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
        ttk.Button(self.add_left_frame, text="Вибрати фото", command=self.select_image).pack(pady=5)

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
        ttk.Button(self.add_bottom_frame, text="Додати артефакт", command=self.add_artifact).pack(pady=10)

        self.current_artifact = None
        self.show_artifact()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_data(self):
        # Спочатку перевіряємо наявність файлів у папці Yusypiv
        txt_path = os.path.join(self.storage_path, "artifacts.txt")
        csv_path = os.path.join(self.storage_path, "artifacts.csv")
        bin_path = os.path.join(self.storage_path, "artifacts.bin")

        self.artifacts = []
        self.conditions = ["Відмінний", "Добрий", "Задовільний", "Поганий"]
        self.categories = ["Реліквія", "Скарб", "Документ", "Скульптура"]
        self.days_of_week = ("Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя")
        self.statuses = ("На виставці", "У сховищі", "На реставрації", "Втрачений")
        self.max_list_size = 10

        # Спробуємо завантажити дані з файлів
        if os.path.exists(txt_path):
            self.load_from_txt(txt_path)
        elif os.path.exists(csv_path):
            self.load_from_csv(csv_path)
        elif os.path.exists(bin_path):
            self.load_from_bin(bin_path)
        else:
            # Якщо файлів немає, ініціалізуємо стандартні дані
            self.artifacts = [
                DetailedArtifact("Маска Тутанхамона", "3300", "Стародавній Єгипет", "Золото, лазурит, бірюза",
                                 "Золота похоронна маска фараона", "Відмінний", "Реліквія", "Понеділок", "На виставці", "images//artifact1.jpg"),
                DetailedArtifact("Камінь Розетти", "2250", "Стародавній Єгипет", "Граніт",
                                 "Ключ до розшифровки єгипетських ієрогліфів", "Добрий", "Документ", "Середа", "На виставці", "images//artifact2.jpg"),
                DetailedArtifact("Теракотова армія", "2200", "Стародавній Китай", "Глина",
                                 "Армія глиняних воїнів імператора", "Задовільний", "Скульптура", "П'ятниця", "У сховищі", "images/artifact3.jpg")
            ]

    def save_data(self):
        # Зберігаємо дані у всіх трьох форматах
        self.save_to_txt(os.path.join(self.storage_path, "artifacts.txt"))
        self.save_to_csv(os.path.join(self.storage_path, "artifacts.csv"))
        self.save_to_bin(os.path.join(self.storage_path, "artifacts.bin"))

    def save_to_txt(self, file_path):
        with open(file_path, "w", encoding="utf-8") as f:
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
                f.write("-" * 50 + "\n")

    def save_to_csv(self, file_path):
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            # Заголовки
            writer.writerow(["name", "age", "origin", "material", "description", "condition", "category", "discovery_day", "status", "image_path"])
            # Дані
            for artifact in self.artifacts:
                writer.writerow([
                    artifact.name, artifact.age, artifact.origin, artifact.material,
                    artifact.description, artifact.condition, artifact.category,
                    artifact.discovery_day, artifact.status, artifact.image_path
                ])

    def save_to_bin(self, file_path):
        with open(file_path, "wb") as f:
            pickle.dump([artifact.to_dict() for artifact in self.artifacts], f)

    def load_from_txt(self, file_path):
        self.artifacts = []
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            i = 0
            while i < len(lines):
                if lines[i].startswith("Назва:"):
                    name = lines[i].split("Назва: ")[1].strip()
                    age = lines[i+1].split("Вік: ")[1].strip()
                    origin = lines[i+2].split("Походження: ")[1].strip()
                    material = lines[i+3].split("Матеріал: ")[1].strip()
                    description = lines[i+4].split("Опис: ")[1].strip()
                    condition = lines[i+5].split("Стан: ")[1].strip()
                    category = lines[i+6].split("Категорія: ")[1].strip()
                    discovery_day = lines[i+7].split("День виявлення: ")[1].strip()
                    status = lines[i+8].split("Статус: ")[1].strip()
                    image_path = lines[i+9].split("Шлях до зображення: ")[1].strip()
                    self.artifacts.append(DetailedArtifact(
                        name, age, origin, material, description,
                        condition, category, discovery_day, status, image_path
                    ))
                    i += 11  # Переходимо до наступного артефакту
                else:
                    i += 1

    def load_from_csv(self, file_path):
        self.artifacts = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.artifacts.append(DetailedArtifact(
                    row["name"], row["age"], row["origin"], row["material"],
                    row["description"], row["condition"], row["category"],
                    row["discovery_day"], row["status"], row["image_path"]
                ))

    def load_from_bin(self, file_path):
        self.artifacts = []
        with open(file_path, "rb") as f:
            artifacts_data = pickle.load(f)
            for data in artifacts_data:
                self.artifacts.append(DetailedArtifact.from_dict(data))

    def on_closing(self):
        self.save_data()
        self.root.destroy()

    def update_artifact_listbox(self):
        self.artifact_listbox.delete(0, tk.END)
        for artifact in self.artifacts:
            self.artifact_listbox.insert(tk.END, f"{artifact.name} ({artifact.age} років)")

    def load_image(self, image_path):
        try:
            if image_path and os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                return photo
            return None
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
            self.add_image_path.set(file_path)
            self.add_image_label.config(text=f"Вибрано: {os.path.basename(file_path)}")
            photo = self.load_image(file_path)
            if photo:
                self.add_image_display_label.config(image=photo)
                self.add_image_display_label.image = photo
            else:
                self.add_image_display_label.config(image="")
        else:
            self.add_image_label.config(text="Фото не вибрано")
            self.add_image_display_label.config(image="")

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

        new_artifact = DetailedArtifact(
            name, age, origin, material, description,
            condition, category, discovery_day, status, new_image_path
        )

        self.artifacts.append(new_artifact)
        self.update_artifact_listbox()
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
        self.conditions.remove(value)
        self.condition_menu["menu"].delete(value)
        self.add_condition_menu["menu"].delete(value)
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
        self.categories.remove(value)
        self.category_menu["menu"].delete(value)
        self.add_category_menu["menu"].delete(value)
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
        self.category_var.set("Усі")
        self.add_category_var.set(self.categories[0] if self.categories else "")

    def check_lists(self):
        messages = []
        if not self.conditions:
            messages.append("Список станів порожній!")
        else:
            messages.append(f"Список станів: {len(self.conditions)} елементів")
        if len(self.conditions) > self.max_list_size:
            messages.append(f"Список станів перевищує ліміт ({self.max_list_size})!")
        if not self.categories:
            messages.append("Список категорій порожній!")
        else:
            messages.append(f"Список категорій: {len(self.categories)} елементів")
        if len(self.categories) > self.max_list_size:
            messages.append(f"Список категорій перевищує ліміт ({self.max_list_size})!")
        messagebox.showinfo("Перевірка списків", "\n".join(messages))

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
        use_query = query and query != "Введіть запит для пошуку"

        if use_query:
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

        if not use_query and not filters_used:
            messagebox.showerror("Помилка", "Введіть запит або виберіть хоча б один фільтр!")
            return

        matching_artifacts = []
        for artifact in self.artifacts:
            matches_query = True
            if use_query:
                matches_query = query == artifact.name.lower() or query == artifact.age

            matches_condition = selected_condition == "Усі" or artifact.condition == selected_condition
            matches_category = selected_category == "Усі" or artifact.category == selected_category
            matches_day = selected_day == "Усі" or artifact.discovery_day == selected_day
            matches_status = selected_status == "Усі" or artifact.status == selected_status

            if matches_query and matches_condition and matches_category and matches_day and matches_status:
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
            return
        self.current_artifact = self.artifacts[self.current_artifact_index]
        self.browse_info_label.config(text=self.current_artifact.get_full_info())
        self.current_image = self.load_image(self.current_artifact.image_path)
        if self.current_image:
            self.browse_image_label.config(image=self.current_image)
        else:
            self.browse_image_label.config(image="")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = ArtifactApp(root)
    root.mainloop()