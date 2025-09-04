import os, cryptocode, json
import tkinter as tk
from tkinter import messagebox


# ŞİFRE DOSYALARINI AYARLAMA
data_folder = os.path.join(os.path.expanduser("~"), "AppData", "Local", "MyPasswordApp")
os.makedirs(data_folder, exist_ok=True)
os.system(f'attrib +h "{data_folder}"')
passwords_path = os.path.join(data_folder, "passwords.json")
configPath = os.path.join(data_folder,"config.json")

if not os.path.exists(passwords_path):
    with open(passwords_path, "w") as f:
        json.dump({}, f)


# ANA UYGULAMA
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Password Protector")
        window_width, window_height = 400, 550

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x}+{y-50}")
        self.minsize(400, 550)
        self.maxsize(400, 550)

        container = tk.Frame(self, width=400, height=550)
        container.pack_propagate(False)  # container kendi boyutunu korusun
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (LoginPage, CreatePasswdPage, AddPasswordPage, ViewPasswordsPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.pack(fill="both", expand=True)
            frame.pack_forget()

    def show_frame(self, page_class):
        for f in self.frames.values():
            f.pack_forget()
        if page_class == ViewPasswordsPage:
            self.frames[page_class].refresh_list()  # listeyi güncelle
        self.frames[page_class].pack(fill="both", expand=True)


# ŞİFRE OLUŞTURMA SAYFASI
class CreatePasswdPage(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack_propagate(False)

        enter_passwd_label = tk.Label(
            self, 
            text="Şifreni seç. dikkatli ol, şifreni değiştiremezsin", 
            font=("Arial",10,"normal")
        )
        enter_passwd_label.place(relx=0.5, y=150, anchor="n")

        self.passwd_entry = tk.Entry(self, width=30)
        self.passwd_entry.place(relx=0.5, y=180, anchor="n")

        enter_sec_word = tk.Label(
            self, 
            text="Güvenlik kelimeni seç", 
            font=("Arial",10,"normal")
        )
        enter_sec_word.place(relx=0.5, y=220, anchor="n")

        self.sec_word_entry = tk.Entry(self, width=30)
        self.sec_word_entry.place(relx=0.5, y=250, anchor="n")

        submit_button = tk.Button(self, text="Onayla", width=15, command=self.create_user_button)
        submit_button.place(relx=0.5, y=310, anchor="n")

    def create_user_button(self):
        password = self.passwd_entry.get().strip()
        security_word = self.sec_word_entry.get().strip()

        try:
            if not password or not security_word:
                 messagebox.showerror("Hata","Değerler boş bırakılamaz")
            elif password==security_word:
                messagebox.showerror("Hata","Şifre ve güvenlik kelimesi aynı olamaz")
            else:
                encryptedPassword=cryptocode.encrypt(password,security_word)
                encryptedSecWord=cryptocode.encrypt(security_word,"snakecloudknifepillow")
                with open(configPath, "w") as f:
                    json.dump({"user_password":encryptedPassword,"user_sec_word":encryptedSecWord}, f)
                
                self.controller.show_frame(LoginPage)
        except:
            messagebox.showerror("Hata","Bir hata oluştu")


# LOGİN SAYFASI
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        enter_passwd = tk.Label(
            self, 
            text="Şifreni Gir", 
            font=("Arial",12,"normal")
        )
        enter_passwd.place(relx=0.5, y=190, anchor="n")

        self.passwd_entry = tk.Entry(self, width=30, show="*")
        self.passwd_entry.place(relx=0.5, y=230, anchor="n")

        submit_button = tk.Button(self, text="Giriş Yap",width=12,command=self.login_button_clicked)
        submit_button.place(relx=0.5, y=290, anchor="n")
    
    def login_button_clicked(self):
        passwd = self.passwd_entry.get().strip()
        try:
            if not passwd:
                messagebox.showerror("Hata","Şifre boş bırakılamaz")
            else:
                with open(configPath, "r") as f:
                    config = json.load(f)
                encrypted_passwd = config.get("user_password")
                encrypted_sec_word=config.get("user_sec_word")
                temp_sec_word=cryptocode.decrypt(encrypted_sec_word,"snakecloudknifepillow")
                temp_passwd=cryptocode.decrypt(encrypted_passwd,temp_sec_word)
                if temp_passwd==passwd:
                    messagebox.showinfo("Başarılı","Giriş başarılı")
                    self.controller.show_frame(ViewPasswordsPage)
                else:
                    messagebox.showerror("Hata","Şifre yanlış")
        except:
            messagebox.showerror("Hata","Bir hata oluştu")


# YENİ ŞİFRE EKLEME SAYFASI
class AddPasswordPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Başlık").pack(pady=5)
        self.title_entry = tk.Entry(self, width=30)
        self.title_entry.pack(pady=5)

        tk.Label(self, text="Şifre").pack(pady=5)
        self.pass_entry = tk.Entry(self, width=30, show="*")
        self.pass_entry.pack(pady=5)

        tk.Label(self, text="Güvenlik Kodu").pack(pady=5)
        self.sec_entry = tk.Entry(self, width=30)
        self.sec_entry.pack(pady=5)

        tk.Button(self, text="Kaydet", command=self.save_password).pack(pady=10)
        tk.Button(self, text="Geri", command=lambda:self.controller.show_frame(ViewPasswordsPage)).pack(pady=5)

    def save_password(self):
        title = self.title_entry.get().strip()
        passwd = self.pass_entry.get().strip()
        sec_word = self.sec_entry.get().strip()

        if not title or not passwd or not sec_word:
            messagebox.showerror("Hata","Alanlar boş bırakılamaz")
            return

        with open(passwords_path,"r") as f:
            data = json.load(f)

        if title in data:
            messagebox.showerror("Hata","Bu başlık zaten mevcut")
            return

        data[title] = {
            "password": cryptocode.encrypt(passwd, sec_word),
            "sec_word": cryptocode.encrypt(sec_word, "snakecloudknifepillow")
        }

        with open(passwords_path,"w") as f:
            json.dump(data, f, indent=4)

        messagebox.showinfo("Başarılı","Şifre kaydedildi")
        self.title_entry.delete(0,tk.END)
        self.pass_entry.delete(0,tk.END)
        self.sec_entry.delete(0,tk.END)


# ŞİFRELERİ GÖRÜNTÜLEME SAYFASI
class ViewPasswordsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Yeni Şifre Ekle butonu sağ üst köşede
        add_btn = tk.Button(self, text="Yeni Şifre Ekle", command=lambda: controller.show_frame(AddPasswordPage))
        add_btn.place(relx=1.0, x=-30, y=10, anchor="ne")

        # Scrollable frame oluştur
        self.canvas = tk.Canvas(self, borderwidth=0, width=380, height=480)
        self.scroll_frame = tk.Frame(self.canvas)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.place(relx=1.0, rely=0.06, relheight=0.88, anchor="ne")
        self.canvas.place(x=10, y=40)
        self.canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def ask_security_code(self, title):
        with open(passwords_path, "r") as f:
            data = json.load(f)
        info = data[title]

        popup = tk.Toplevel(self)
        popup.title("Güvenlik Kodu")
        popup.geometry("300x200+500+200")
        popup.transient(self.controller)
        popup.grab_set()

        tk.Label(popup, text="Güvenlik kodunu gir:").pack(pady=10)
        entry = tk.Entry(popup, show="*")
        entry.pack(pady=5)
        entry.focus_set()

        # Onayla butonu
        def check_code():
            sec_code = entry.get().strip()
            if not sec_code:
                messagebox.showerror("Hata", "Kod boş olamaz")
                return

            decrypted = cryptocode.decrypt(info["password"], sec_code)
            if decrypted:
                # Entry ve butonu devre dışı bırak
                entry.config(state="disabled")
                onayla_btn.config(state="disabled")

                # Şifreyi göster ve kopyala butonu ekle
                tk.Label(popup, text=f"Şifre: {decrypted}").pack(pady=10)
                tk.Button(popup, text="Kopyala", command=lambda: self.clipboard_clear() or self.clipboard_append(decrypted)).pack(pady=5)
            else:
                messagebox.showerror("Hata", "Kod yanlış")

        onayla_btn = tk.Button(popup, text="Onayla", command=check_code)
        onayla_btn.pack(pady=10)


    def delete_password(self, title):
        answer = messagebox.askyesno("Sil", f"{title} şifresini silmek istediğinizden emin misiniz?")
        if answer:
            with open(passwords_path, "r") as f:
                data = json.load(f)
            data.pop(title, None)
            with open(passwords_path, "w") as f:
                json.dump(data, f, indent=4)
            self.refresh_list()

    def refresh_list(self):
        # Önce scroll_frame içindeki widgetleri temizle
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        kayıtlı_sifreler_label = tk.Label(self, text="Kayıtlı Şifreler", font=("Arial",12,"bold"))
        kayıtlı_sifreler_label.place(x=10, y=10)



        with open(passwords_path, "r") as f:
            data = json.load(f)

        for title, info in data.items():
            frame = tk.Frame(self.scroll_frame)
            frame.pack(fill="x", pady=5, padx=5)

            tk.Label(frame, text=title, font=("Arial",10)).pack(side="left")
            tk.Button(frame, text="Göster", command=lambda t=title: self.ask_security_code(t)).pack(side="right", padx=5)
            tk.Button(frame, text="Sil", command=lambda t=title: self.delete_password(t)).pack(side="right", padx=5)




if __name__ == "__main__":
    app = App()

    if not os.path.exists(configPath):
        app.show_frame(CreatePasswdPage)
    else:
        app.show_frame(LoginPage)

    app.mainloop()
