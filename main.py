import json
import os
import random
import string
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

HISTORY_FILE = "password_history.json"
MIN_LENGTH = 4
MAX_LENGTH = 64


class RandomPasswordGeneratorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("920x620")

        self.history = []

        self.length_var = tk.IntVar(value=12)
        self.use_digits_var = tk.BooleanVar(value=True)
        self.use_letters_var = tk.BooleanVar(value=True)
        self.use_symbols_var = tk.BooleanVar(value=False)
        self.generated_password_var = tk.StringVar(value="Пароль: -")

        self._build_ui()
        self.load_history(show_message=False)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        options = ttk.LabelFrame(main, text="Параметры пароля", padding=10)
        options.pack(fill="x")

        ttk.Label(options, text=f"Длина пароля ({MIN_LENGTH}-{MAX_LENGTH}):").grid(
            row=0, column=0, sticky="w", padx=4, pady=4
        )
        self.length_scale = ttk.Scale(
            options,
            from_=MIN_LENGTH,
            to=MAX_LENGTH,
            orient="horizontal",
            command=self._on_scale_change,
            length=320,
        )
        self.length_scale.set(self.length_var.get())
        self.length_scale.grid(row=0, column=1, sticky="w", padx=4, pady=4)

        self.length_label = ttk.Label(options, text=str(self.length_var.get()))
        self.length_label.grid(row=0, column=2, sticky="w", padx=8, pady=4)

        ttk.Checkbutton(options, text="Цифры", variable=self.use_digits_var).grid(row=1, column=0, padx=4, pady=4, sticky="w")
        ttk.Checkbutton(options, text="Буквы", variable=self.use_letters_var).grid(row=1, column=1, padx=4, pady=4, sticky="w")
        ttk.Checkbutton(options, text="Спецсимволы", variable=self.use_symbols_var).grid(row=1, column=2, padx=4, pady=4, sticky="w")

        actions = ttk.Frame(options)
        actions.grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))
        ttk.Button(actions, text="Сгенерировать", command=self.generate_password).pack(side="left", padx=4)
        ttk.Button(actions, text="Скопировать", command=self.copy_password).pack(side="left", padx=4)
        ttk.Button(actions, text="Сохранить историю", command=self.save_history).pack(side="left", padx=4)
        ttk.Button(actions, text="Загрузить историю", command=self.load_history).pack(side="left", padx=4)
        ttk.Button(actions, text="Очистить историю", command=self.clear_history).pack(side="left", padx=4)

        ttk.Label(main, textvariable=self.generated_password_var, font=("Arial", 13, "bold")).pack(anchor="w", pady=(12, 8))

        table_wrap = ttk.LabelFrame(main, text="История генераций", padding=10)
        table_wrap.pack(fill="both", expand=True)

        columns = ("datetime", "length", "options", "password")
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings", height=16)
        self.tree.heading("datetime", text="Дата/время")
        self.tree.heading("length", text="Длина")
        self.tree.heading("options", text="Параметры")
        self.tree.heading("password", text="Пароль")

        self.tree.column("datetime", width=180)
        self.tree.column("length", width=80, anchor="center")
        self.tree.column("options", width=280)
        self.tree.column("password", width=300)

        scrollbar = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _on_scale_change(self, value):
        length = int(float(value))
        self.length_var.set(length)
        self.length_label.config(text=str(length))

    def _validate_inputs(self):
        length = self.length_var.get()
        if length < MIN_LENGTH or length > MAX_LENGTH:
            messagebox.showerror("Ошибка", f"Длина должна быть от {MIN_LENGTH} до {MAX_LENGTH}.")
            return None

        selected = []
        if self.use_digits_var.get():
            selected.append(("digits", string.digits))
        if self.use_letters_var.get():
            selected.append(("letters", string.ascii_letters))
        if self.use_symbols_var.get():
            selected.append(("symbols", string.punctuation))

        if not selected:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов.")
            return None

        return length, selected

    def generate_password(self):
        validated = self._validate_inputs()
        if not validated:
            return

        length, selected = validated
        alphabet = "".join(chars for _, chars in selected)
        password = "".join(random.choice(alphabet) for _ in range(length))

        self.generated_password_var.set(f"Пароль: {password}")

        options_label = ", ".join(label for label, _ in selected)
        self.history.insert(
            0,
            {
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "length": length,
                "options": options_label,
                "password": password,
            },
        )
        self._render_history()

    def copy_password(self):
        text = self.generated_password_var.get()
        prefix = "Пароль: "
        if not text.startswith(prefix) or text == "Пароль: -":
            messagebox.showwarning("Внимание", "Сначала сгенерируйте пароль.")
            return

        password = text[len(prefix):]
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        self.root.update()
        messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена.")

    def _render_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in self.history:
            self.tree.insert(
                "",
                "end",
                values=(row["datetime"], row["length"], row["options"], row["password"]),
            )

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", f"История сохранена в {os.path.abspath(HISTORY_FILE)}")
        except OSError as err:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {err}")

    def load_history(self, show_message=True):
        if not os.path.exists(HISTORY_FILE):
            self.history = []
            self._render_history()
            if show_message:
                messagebox.showwarning("Внимание", "Файл password_history.json не найден.")
            return

        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("Некорректный формат password_history.json")

            validated = []
            for row in data:
                if not isinstance(row, dict):
                    continue

                dt = str(row.get("datetime", "")).strip()
                length = row.get("length")
                options = str(row.get("options", "")).strip()
                password = str(row.get("password", "")).strip()

                if (
                    dt
                    and isinstance(length, int)
                    and MIN_LENGTH <= length <= MAX_LENGTH
                    and options
                    and password
                ):
                    validated.append(
                        {
                            "datetime": dt,
                            "length": length,
                            "options": options,
                            "password": password,
                        }
                    )

            self.history = validated
            self._render_history()
            if show_message:
                messagebox.showinfo("Успех", "История загружена.")
        except (OSError, json.JSONDecodeError, ValueError) as err:
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {err}")

    def clear_history(self):
        self.history = []
        self._render_history()


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomPasswordGeneratorApp(root)
    root.mainloop()
