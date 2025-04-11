import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

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
    def __init__(self, name, age, origin, material, description, images, condition, category, discovery_day, status):
        super().__init__(name, age, origin, material)
        self.description = description
        self.images = images
        self.condition = condition
        self.category = category
        self.discovery_day = discovery_day
        self.status = status
        self.current_image = 0

    def get_full_info(self):
        return (f"{self.get_info()}\nОпис: {self.description}\n"
                f"Стан: {self.condition}\nКатегорія: {self.category}\n"
                f"День виявлення: {self.discovery_day}\nСтатус: {self.status}")

    def next_image(self):
        if self.current_image < len(self.images) - 1:
            self.current_image += 1
        return self.images[self.current_image]

    def prev_image(self):
        if self.current_image > 0:
            self.current_image -= 1
        return self.images[self.current_image]

# Клас для графічного інтерфейсу
class ArtifactApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Каталог артефактів")
        self.root.geometry("1000x700")

        # Списки та кортежі для нових атрибутів
        self.conditions = ["Відмінний", "Добрий", "Задовільний", "Поганий"]
        self.categories = ["Реліквія", "Скарб", "Документ", "Скульптура"]
        self.days_of_week = ("Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя")
        self.statuses = ("На виставці", "У сховищі", "На реставрації", "Втрачений")
        self.max_list_size = 10

        # Список артефактів
        self.artifacts = [
            DetailedArtifact("Маска Тутанхамона", "3300", "Стародавній Єгипет", "Золото, лазурит, бірюза",
                             "Золота похоронна маска фараона", ["artifact1.jpg"], "Відмінний", "Реліквія", "Понеділок", "На виставці"),
            DetailedArtifact("Камінь Розетти", "2250", "Стародавній Єгипет", "Граніт",
                             "Ключ до розшифровки єгипетських ієрогліфів", ["artifact2.jpg"], "Добрий", "Документ", "Середа", "На виставці"),
            DetailedArtifact("Теракотова армія", "2200", "Стародавній Китай", "Глина",
                             "Армія глиняних воїнів імператора", ["artifact3.jpg"], "Задовільний", "Скульптура", "П'ятниця", "У сховищі")
        ]

        self.current_artifact_index = 0

        # Основний контейнер із вкладками
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # Вкладка "Пошук"
        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="Пошук")

        # Вкладка "Перегляд"
        self.browse_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.browse_tab, text="Перегляд")

        # Вкладка "Управління списками"
        self.manage_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manage_tab, text="Управління списками")

        # --- Вкладка "Пошук" ---
        # Список артефактів (назва та вік)
        self.artifact_list_frame = tk.Frame(self.search_tab)
        self.artifact_list_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        tk.Label(self.artifact_list_frame, text="Доступні артефакти:").pack()
        self.artifact_listbox = tk.Listbox(self.artifact_list_frame, height=10, width=30)
        self.artifact_listbox.pack()
        for artifact in self.artifacts:
            self.artifact_listbox.insert(tk.END, f"{artifact.name} ({artifact.age} років)")

        # Поле пошуку
        self.search_frame = tk.Frame(self.search_tab)
        self.search_frame.pack(pady=5)
        tk.Label(self.search_frame, text="Введіть назву або вік:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(self.search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.insert(0, "Введіть запит для пошуку")
        self.search_entry.config(fg="gray50")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)
        tk.Button(self.search_frame, text="Пошук", command=self.search_artifact).pack(side=tk.LEFT, padx=5)

        # Фільтри
        self.filters_frame = tk.Frame(self.search_tab)
        self.filters_frame.pack(pady=5)

        # Стан
        tk.Label(self.filters_frame, text="Стан:").pack()
        self.condition_frame = tk.Frame(self.filters_frame)
        self.condition_frame.pack()
        self.condition_scrollbar = tk.Scrollbar(self.condition_frame, orient=tk.VERTICAL)
        self.condition_listbox = tk.Listbox(self.condition_frame, height=4, yscrollcommand=self.condition_scrollbar.set, exportselection=False)
        self.condition_scrollbar.config(command=self.condition_listbox.yview)
        self.condition_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.condition_listbox.pack(side=tk.LEFT)
        for condition in self.conditions:
            self.condition_listbox.insert(tk.END, condition)

        # Категорія
        tk.Label(self.filters_frame, text="Категорія:").pack()
        self.category_frame = tk.Frame(self.filters_frame)
        self.category_frame.pack()
        self.category_scrollbar = tk.Scrollbar(self.category_frame, orient=tk.VERTICAL)
        self.category_listbox = tk.Listbox(self.category_frame, height=4, yscrollcommand=self.category_scrollbar.set, exportselection=False)
        self.category_scrollbar.config(command=self.category_listbox.yview)
        self.category_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.category_listbox.pack(side=tk.LEFT)
        for category in self.categories:
            self.category_listbox.insert(tk.END, category)

        # День тижня
        tk.Label(self.filters_frame, text="День виявлення:").pack()
        self.day_frame = tk.Frame(self.filters_frame)
        self.day_frame.pack()
        self.day_scrollbar = tk.Scrollbar(self.day_frame, orient=tk.VERTICAL)
        self.day_listbox = tk.Listbox(self.day_frame, height=4, yscrollcommand=self.day_scrollbar.set, exportselection=False)
        self.day_scrollbar.config(command=self.day_listbox.yview)
        self.day_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.day_listbox.pack(side=tk.LEFT)
        for day in self.days_of_week:
            self.day_listbox.insert(tk.END, day)

        # Статус
        tk.Label(self.filters_frame, text="Статус:").pack()
        self.status_frame = tk.Frame(self.filters_frame)
        self.status_frame.pack()
        self.status_scrollbar = tk.Scrollbar(self.status_frame, orient=tk.VERTICAL)
        self.status_listbox = tk.Listbox(self.status_frame, height=4, yscrollcommand=self.status_scrollbar.set, exportselection=False)
        self.status_scrollbar.config(command=self.status_listbox.yview)
        self.status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_listbox.pack(side=tk.LEFT)
        for status in self.statuses:
            self.status_listbox.insert(tk.END, status)

        # Область для інформації
        self.search_info_label = tk.Label(self.search_tab, text="", justify="left")
        self.search_info_label.pack(pady=10)

        # Область для зображення
        self.search_image_label = tk.Label(self.search_tab)
        self.search_image_label.pack()

        # --- Вкладка "Перегляд" ---
        # Область для інформації
        self.browse_info_label = tk.Label(self.browse_tab, text="", justify="left")
        self.browse_info_label.pack(pady=10)

        # Область для зображення
        self.browse_image_label = tk.Label(self.browse_tab)
        self.browse_image_label.pack()

        # Кнопки навігації
        self.nav_frame = tk.Frame(self.browse_tab)
        self.nav_frame.pack(pady=5)
        self.prev_artifact_btn = tk.Button(self.nav_frame, text="Попередній артефакт", command=self.show_prev_artifact)
        self.prev_artifact_btn.pack(side=tk.LEFT, padx=5)
        self.next_artifact_btn = tk.Button(self.nav_frame, text="Наступний артефакт", command=self.show_next_artifact)
        self.next_artifact_btn.pack(side=tk.LEFT, padx=5)

        # --- Вкладка "Управління списками" ---
        self.manage_frame = tk.Frame(self.manage_tab)
        self.manage_frame.pack(pady=10)

        # Поле для введення нового значення
        tk.Label(self.manage_frame, text="Нове значення:").pack()
        self.new_value_entry = tk.Entry(self.manage_frame)
        self.new_value_entry.pack()

        # Кнопки для управління списками
        tk.Button(self.manage_frame, text="Додати до стану", command=self.add_to_conditions).pack(pady=2)
        tk.Button(self.manage_frame, text="Додати до категорії", command=self.add_to_categories).pack(pady=2)
        tk.Button(self.manage_frame, text="Редагувати стан", command=self.edit_condition).pack(pady=2)
        tk.Button(self.manage_frame, text="Редагувати категорію", command=self.edit_category).pack(pady=2)
        tk.Button(self.manage_frame, text="Видалити зі стану", command=self.delete_from_conditions).pack(pady=2)
        tk.Button(self.manage_frame, text="Видалити з категорії", command=self.delete_from_categories).pack(pady=2)
        tk.Button(self.manage_frame, text="Сортувати стан", command=self.sort_conditions).pack(pady=2)
        tk.Button(self.manage_frame, text="Сортувати категорію", command=self.sort_categories).pack(pady=2)
        tk.Button(self.manage_frame, text="Перевернути стан", command=self.reverse_conditions).pack(pady=2)
        tk.Button(self.manage_frame, text="Перевернути категорію", command=self.reverse_categories).pack(pady=2)
        tk.Button(self.manage_frame, text="Перевірити списки", command=self.check_lists).pack(pady=2)

        self.current_artifact = None
        self.photo = None
        self.show_artifact()  # Показати перший артефакт у режимі "Перегляд"

    def add_to_conditions(self):
        new_value = self.new_value_entry.get().strip()
        if not new_value:
            messagebox.showerror("Помилка", "Введіть нове значення!")
            return
        if len(self.conditions) >= self.max_list_size:
            messagebox.showerror("Помилка", f"Список станів перевищує ліміт ({self.max_list_size})!")
            return
        if new_value not in self.conditions:
            self.conditions.append(new_value)
            self.condition_listbox.insert(tk.END, new_value)
            self.new_value_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Помилка", "Це значення вже є у списку!")

    def add_to_categories(self):
        new_value = self.new_value_entry.get().strip()
        if not new_value:
            messagebox.showerror("Помилка", "Введіть нове значення!")
            return
        if len(self.categories) >= self.max_list_size:
            messagebox.showerror("Помилка", f"Список категорій перевищує ліміт ({self.max_list_size})!")
            return
        if new_value not in self.categories:
            self.categories.append(new_value)
            self.category_listbox.insert(tk.END, new_value)
            self.new_value_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Помилка", "Це значення вже є у списку!")

    def edit_condition(self):
        selected = self.condition_listbox.curselection()
        if not selected:
            messagebox.showerror("Помилка", "Виберіть стан для редагування!")
            return
        new_value = self.new_value_entry.get().strip()
        if not new_value:
            messagebox.showerror("Помилка", "Введіть нове значення!")
            return
        index = selected[0]
        old_value = self.conditions[index]
        self.conditions[index] = new_value
        self.condition_listbox.delete(index)
        self.condition_listbox.insert(index, new_value)
        for artifact in self.artifacts:
            if artifact.condition == old_value:
                artifact.condition = new_value
        if self.current_artifact and self.current_artifact.condition == old_value:
            self.current_artifact.condition = new_value
            self.update_info_labels()

    def edit_category(self):
        selected = self.category_listbox.curselection()
        if not selected:
            messagebox.showerror("Помилка", "Виберіть категорію для редагування!")
            return
        new_value = self.new_value_entry.get().strip()
        if not new_value:
            messagebox.showerror("Помилка", "Введіть нове значення!")
            return
        index = selected[0]
        old_value = self.categories[index]
        self.categories[index] = new_value
        self.category_listbox.delete(index)
        self.category_listbox.insert(index, new_value)
        for artifact in self.artifacts:
            if artifact.category == old_value:
                artifact.category = new_value
        if self.current_artifact and self.current_artifact.category == old_value:
            self.current_artifact.category = new_value
            self.update_info_labels()

    def delete_from_conditions(self):
        selected = self.condition_listbox.curselection()
        if not selected:
            messagebox.showerror("Помилка", "Виберіть стан для видалення!")
            return
        index = selected[0]
        value = self.conditions[index]
        for artifact in self.artifacts:
            if artifact.condition == value:
                messagebox.showerror("Помилка", "Цей стан використовується в артефактах!")
                return
        self.conditions.pop(index)
        self.condition_listbox.delete(index)

    def delete_from_categories(self):
        selected = self.category_listbox.curselection()
        if not selected:
            messagebox.showerror("Помилка", "Виберіть категорію для видалення!")
            return
        index = selected[0]
        value = self.categories[index]
        for artifact in self.artifacts:
            if artifact.category == value:
                messagebox.showerror("Помилка", "Ця категорія використовується в артефактах!")
                return
        self.categories.pop(index)
        self.category_listbox.delete(index)

    def sort_conditions(self):
        self.conditions.sort()
        self.condition_listbox.delete(0, tk.END)
        for condition in self.conditions:
            self.condition_listbox.insert(tk.END, condition)

    def sort_categories(self):
        self.categories.sort()
        self.category_listbox.delete(0, tk.END)
        for category in self.categories:
            self.category_listbox.insert(tk.END, category)

    def reverse_conditions(self):
        self.conditions.reverse()
        self.condition_listbox.delete(0, tk.END)
        for condition in self.conditions:
            self.condition_listbox.insert(tk.END, condition)

    def reverse_categories(self):
        self.categories.reverse()
        self.category_listbox.delete(0, tk.END)
        for category in self.categories:
            self.category_listbox.insert(tk.END, category)

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
            self.search_entry.config(fg="black")

    def add_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Введіть запит для пошуку")
            self.search_entry.config(fg="gray50")

    def update_info_labels(self):
        if self.current_artifact:
            self.search_info_label.config(text=self.current_artifact.get_full_info())
            self.browse_info_label.config(text=self.current_artifact.get_full_info())

    def search_artifact(self):
        query = self.search_entry.get().strip().lower()
        if query == "Введіть запит для пошуку" or not query:
            messagebox.showerror("Помилка", "Введіть запит для пошуку!")
            return

        selected_condition = self.condition_listbox.get(tk.ACTIVE) if self.condition_listbox.curselection() else None
        selected_category = self.category_listbox.get(tk.ACTIVE) if self.category_listbox.curselection() else None
        selected_day = self.day_listbox.get(tk.ACTIVE) if self.day_listbox.curselection() else None
        selected_status = self.status_listbox.get(tk.ACTIVE) if self.status_listbox.curselection() else None

        found = False
        for artifact in self.artifacts:
            matches_query = query == artifact.name.lower() or query == artifact.age
            matches_condition = not selected_condition or artifact.condition == selected_condition
            matches_category = not selected_category or artifact.category == selected_category
            matches_day = not selected_day or artifact.discovery_day == selected_day
            matches_status = not selected_status or artifact.status == selected_status

            if matches_query and matches_condition and matches_category and matches_day and matches_status:
                self.current_artifact = artifact
                self.current_artifact.current_image = 0
                self.search_info_label.config(text=self.current_artifact.get_full_info())
                self.load_image(self.current_artifact.images[0], self.search_image_label)
                found = True
                break

        if not found:
            self.search_info_label.config(text="Артефакт не знайдено")
            self.search_image_label.config(image="")
            self.current_artifact = None

    def show_artifact(self):
        self.current_artifact = self.artifacts[self.current_artifact_index]
        self.current_artifact.current_image = 0
        self.browse_info_label.config(text=self.current_artifact.get_full_info())
        self.load_image(self.current_artifact.images[0], self.browse_image_label)

    def show_next_artifact(self):
        if self.current_artifact_index >= len(self.artifacts) - 1:
            return
        self.current_artifact_index += 1
        self.show_artifact()

    def show_prev_artifact(self):
        if self.current_artifact_index <= 0:
            return
        self.current_artifact_index -= 1
        self.show_artifact()

    def load_image(self, image_path, label):
        try:
            image = Image.open(image_path)
            image = image.resize((300, 200), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)
            label.config(image=self.photo)
        except FileNotFoundError:
            label.config(text="Зображення не знайдено")
        except Exception as e:
            label.config(text=f"Помилка: {str(e)}")

# Запуск програми
if __name__ == "__main__":
    root = tk.Tk()
    app = ArtifactApp(root)
    root.mainloop()