# Подключаем нужные модули:
import threading                                                    # чтобы получать сообщения в фоне, пока работает интерфейс
from socket import *                                                        # чтобы подключаться к серверу (как телефонный звонок)
from customtkinter import *                                         # это красивая версия обычного tkinter — для создания окна и кнопок

# Это наш главный класс — окно чата
class MainWindow(CTk):
    def __init__(self):
        super().__init__()  # запускаем "родительский" код окна
        
        # Задаем размер окна
        self.geometry('400x300')

        self.label = None  # Пока у нас нет подписи в меню

        # === МЕНЮ СБОКУ ===
        # Создаем панель сбоку (но узкую, шириной 30)
        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)  # запрет изменять размер по содержимому
        self.menu_frame.place(x=0, y=0)  # размещаем в левом верхнем углу

        self.is_show_menu = False         # по умолчанию меню скрыто
        self.speed_animate_menu = -5      # шаг анимации меню (слева направо или наоборот)
        
        # Кнопка, чтобы открыть/закрыть меню (▶️ или ◀️)
        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)

        # === ОСНОВНАЯ ЧАСТЬ: чат ===
        # Окно, где будут появляться все сообщения
        self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disable')
        self.chat_field.place(x=0, y=0)

        # Поле, куда пишем новое сообщение
        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
        self.message_entry.place(x=0, y=0)

        # Кнопка "отправить"
        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
        self.send_button.place(x=0, y=0)

        # Имя пользователя (можно изменить в будущем)
        self.username = 'Artem'

        # === СОЕДИНЯЕМСЯ С СЕРВЕРОМ ===
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)  # создаем "телефон"
            self.sock.connect(('localhost', 8080))     # звоним на сервер
            
            # Отправляем серверу приветствие
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))

            # Запускаем параллельно прослушку сообщений (как радио)
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

        # Адаптируем интерфейс под размер окна
        self.adaptive_ui()

    # === Показываем или скрываем боковое меню ===
    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1  # меняем направление анимации
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()

            # Показываем элементы в меню (метка и поле для имени)
            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack()

    # === Анимированное открытие/закрытие меню ===
    def show_menu(self):
        # Меняем ширину меню на шаг анимации
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)

        # Если меню еще не полностью открыто — продолжаем анимацию
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)

        # Если меню еще не полностью закрылось — продолжаем закрытие
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)

            # Удаляем виджеты меню, если они были
            if self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()

    # === Автоматическая настройка интерфейса под размер окна ===
    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())

        # Поле чата не должно залезать под меню
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width(), height=self.winfo_height() - 40)

        # Кнопка отправки и поле ввода снизу
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())

        # Каждые 50 миллисекунд повторяем (вдруг окно поменяло размер)
        self.after(50, self.adaptive_ui)

    # === Добавить сообщение в чат (на экран) ===
    def add_message(self, text):
        self.chat_field.configure(state='normal')  # делаем поле редактируемым
        self.chat_field.insert(END, 'Я: ' + text + '\n')  # вставляем текст
        self.chat_field.configure(state='disable')  # снова блокируем

    # === Отправка сообщения на сервер ===
    def send_message(self):
        message = self.message_entry.get()  # берем текст из поля
        if message:
            self.add_message(f"{self.username}: {message}")  # показываем в окне
            data = f"TEXT@{self.username}@{message}\n"  # подготавливаем текст для отправки
            try:
                self.sock.sendall(data.encode())  # отправляем серверу
            except:
                pass
        self.message_entry.delete(0, END)  # очищаем поле

    # === Получение сообщений от других ===
    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)  # слушаем сервер
                if not chunk:
                    break
                buffer += chunk.decode()  # добавляем к уже полученному

                # Пока есть строки с концом строки (\n) — разбираем
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())  # обрабатываем каждую строку
            except:
                break
        self.sock.close()  # закрываем соединение

    # === Обработка полученной строки (разбор) ===
    def handle_line(self, line):
        if not line:
            return

        parts = line.split("@", 3)  # разбиваем строку на части
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")

        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                self.add_message(f"{author} надіслав(ла) зображення: {filename}")

        else:
            self.add_message(line)

# Запускаем наше окно
win = MainWindow()
win.mainloop()
