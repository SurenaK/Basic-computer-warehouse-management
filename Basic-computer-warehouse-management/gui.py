import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import get_connection, init_db
import auth

# ─────────────────────────────────────────
#  پالت رنگ — تم تاریک مدرن
# ─────────────────────────────────────────
C = {
    "bg":           "#1e1e2e",   # پس‌زمینه اصلی
    "panel":        "#2a2a3e",   # پس‌زمینه پنل‌ها
    "card":         "#313145",   # کارت‌ها و فریم‌ها
    "accent":       "#7c6af7",   # بنفش اصلی
    "accent2":      "#5a9cf8",   # آبی ثانوی
    "success":      "#3dd68c",   # سبز موفقیت
    "danger":       "#f87171",   # قرمز خطر
    "warning":      "#facc15",   # زرد هشدار
    "text":         "#e2e8f0",   # متن اصلی
    "text_muted":   "#94a3b8",   # متن کم‌رنگ
    "border":       "#3d3d5c",   # خط جداکننده
    "entry_bg":     "#252538",   # پس‌زمینه ورودی
    "hover":        "#9d8bf5",   # هاور دکمه
    "row_odd":      "#2a2a3e",
    "row_even":     "#252538",
    "row_selected": "#4a3f7a",
}

FONT_MAIN  = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_LARGE = ("Segoe UI", 14, "bold")


# ─────────────────────────────────────────
#  دکمه سفارشی
# ─────────────────────────────────────────
class ModernButton(tk.Button):
    def __init__(self, parent, text, command=None, style="primary", **kwargs):
        colors = {
            "primary": (C["accent"],  C["hover"],   C["text"]),
            "success": (C["success"], "#2ebd7a",    "#0f2a1e"),
            "danger":  (C["danger"],  "#e55c5c",    "#2a0a0a"),
            "neutral": (C["card"],    C["border"],  C["text"]),
        }
        bg, hover_bg, fg = colors.get(style, colors["primary"])
        super().__init__(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=hover_bg, activeforeground=fg,
            relief="flat", bd=0, padx=14, pady=7,
            font=FONT_BOLD, cursor="hand2",
            **kwargs
        )
        self._bg = bg
        self._hover = hover_bg
        self.bind("<Enter>", lambda e: self.config(bg=self._hover))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))


# ─────────────────────────────────────────
#  فیلد ورودی سفارشی
# ─────────────────────────────────────────
class ModernEntry(tk.Entry):
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(
            parent,
            bg=C["entry_bg"], fg=C["text"],
            insertbackground=C["accent"],
            relief="flat", bd=0,
            font=FONT_MAIN,
            **kwargs
        )
        self._placeholder = placeholder
        self._has_focus = False
        if placeholder:
            self._show_placeholder()
            self.bind("<FocusIn>",  self._on_focus_in)
            self.bind("<FocusOut>", self._on_focus_out)

    def _show_placeholder(self):
        self.delete(0, tk.END)
        self.insert(0, self._placeholder)
        self.config(fg=C["text_muted"])

    def _on_focus_in(self, _):
        if self.get() == self._placeholder:
            self.delete(0, tk.END)
            self.config(fg=C["text"])
        self._has_focus = True

    def _on_focus_out(self, _):
        self._has_focus = False
        if not self.get():
            self._show_placeholder()

    def get_value(self):
        v = self.get()
        return "" if v == self._placeholder else v

    def clear(self):
        self.delete(0, tk.END)
        if self._placeholder:
            self._show_placeholder()


def _add_inner_border(widget, parent, pady=0, padx=0):
    """یک فریم با border شبیه‌سازی شده می‌سازد"""
    border = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
    widget_frame = tk.Frame(border, bg=C["entry_bg"])
    widget.pack(in_=widget_frame, fill="x", padx=4, pady=4)
    widget_frame.pack(fill="x")
    border.pack(fill="x", pady=pady, padx=padx)
    return border


# ─────────────────────────────────────────
#  پنجره لاگین
# ─────────────────────────────────────────
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("ورود به سیستم مدیریت انبار")
        self.root.geometry("420x480")
        self.root.resizable(False, False)
        self.root.configure(bg=C["bg"])
        self.root.eval('tk::PlaceWindow . center')

        self._build_ui()
        self.username_entry.focus()
        self.root.bind("<Return>", lambda e: self.do_login())

    def _build_ui(self):
        # ─── هدر ───
        header = tk.Frame(self.root, bg=C["panel"], pady=30)
        header.pack(fill="x")

        tk.Label(header, text="⬡", font=("Segoe UI", 32), bg=C["panel"],
                 fg=C["accent"]).pack()
        tk.Label(header, text="مدیریت انبار قطعات", font=FONT_LARGE,
                 bg=C["panel"], fg=C["text"]).pack(pady=(5, 2))
        tk.Label(header, text="کامپیوتر", font=FONT_TITLE,
                 bg=C["panel"], fg=C["accent"]).pack()

        # ─── فرم ───
        form = tk.Frame(self.root, bg=C["bg"], padx=40, pady=30)
        form.pack(fill="both", expand=True)

        self._field(form, "👤  نام کاربری")
        self.username_entry = tk.Entry(
            form, width=30,
            bg=C["entry_bg"], fg=C["text"],
            insertbackground=C["accent"],
            relief="flat", bd=0, font=FONT_MAIN
        )
        self.username_entry.pack(fill="x", ipady=8, pady=(0, 15))

        self._field(form, "🔒  رمز عبور")
        self.password_entry = tk.Entry(
            form, show="●", width=30,
            bg=C["entry_bg"], fg=C["text"],
            insertbackground=C["accent"],
            relief="flat", bd=0, font=FONT_MAIN
        )
        self.password_entry.pack(fill="x", ipady=8, pady=(0, 25))

        ModernButton(form, text="  ورود به سیستم  ", command=self.do_login,
                     style="primary").pack(fill="x", ipady=4)

        tk.Label(form, text="Warehouse Management System v2.0",
                 font=FONT_SMALL, bg=C["bg"], fg=C["text_muted"]).pack(pady=(20, 0))

    def _field(self, parent, label):
        tk.Label(parent, text=label, font=FONT_SMALL,
                 bg=C["bg"], fg=C["text_muted"], anchor="w").pack(fill="x", pady=(0, 4))

    def do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self._shake()
            return

        if auth.verify_login(username, password):
            self.root.destroy()
            open_main_app()
        else:
            self._shake()
            messagebox.showerror("خطای ورود", "نام کاربری یا رمز عبور اشتباه است.")
            self.password_entry.delete(0, tk.END)

    def _shake(self):
        x0, y0 = self.root.winfo_x(), self.root.winfo_y()
        for dx in [10, -10, 8, -8, 5, -5, 0]:
            self.root.geometry(f"+{x0+dx}+{y0}")
            self.root.update()
            self.root.after(30)


# ─────────────────────────────────────────
#  برنامه اصلی
# ─────────────────────────────────────────
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مدیریت انبار قطعات کامپیوتر")
        self.root.geometry("1050x620")
        self.root.configure(bg=C["bg"])
        self.root.eval('tk::PlaceWindow . center')

        self._build_sidebar()
        self._build_content()
        self._show_tab("parts")

    # ─────────────── سایدبار ───────────────
    def _build_sidebar(self):
        sidebar = tk.Frame(self.root, bg=C["panel"], width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # لوگو
        logo_frame = tk.Frame(sidebar, bg=C["accent"], pady=18)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="⬡ انبار", font=FONT_TITLE,
                 bg=C["accent"], fg="white").pack()

        # آمار سریع
        self.stat_frame = tk.Frame(sidebar, bg=C["card"], padx=15, pady=12)
        self.stat_frame.pack(fill="x", padx=10, pady=12)
        tk.Label(self.stat_frame, text="آمار سریع", font=FONT_SMALL,
                 bg=C["card"], fg=C["text_muted"]).pack(anchor="w")
        self.stat_parts = tk.Label(self.stat_frame, text="قطعات: —",
                                   font=FONT_BOLD, bg=C["card"], fg=C["accent"])
        self.stat_parts.pack(anchor="w", pady=2)
        self.stat_txn = tk.Label(self.stat_frame, text="تراکنش‌ها: —",
                                 font=FONT_BOLD, bg=C["card"], fg=C["accent2"])
        self.stat_txn.pack(anchor="w", pady=2)

        # منو
        self.nav_buttons = {}
        nav_items = [
            ("parts", "📦", "لیست قطعات"),
            ("buy",   "📥", "ثبت خرید"),
            ("sell",  "📤", "ثبت فروش"),
            ("log",   "📋", "لاگ تراکنش‌ها"),
        ]
        for key, icon, label in nav_items:
            btn = tk.Button(
                sidebar, text=f"  {icon}  {label}",
                font=FONT_MAIN, anchor="w",
                bg=C["panel"], fg=C["text"],
                activebackground=C["accent"], activeforeground="white",
                relief="flat", bd=0, pady=12, padx=10, cursor="hand2",
                command=lambda k=key: self._show_tab(k)
            )
            btn.pack(fill="x", padx=5, pady=2)
            self.nav_buttons[key] = btn

        # دکمه خروج پایین
        tk.Frame(sidebar, bg=C["border"], height=1).pack(fill="x", padx=10, pady=10)
        ModernButton(sidebar, text="🔓  خروج از حساب",
                     command=self.logout, style="neutral").pack(
            fill="x", padx=10, pady=5)

        self._update_stats()

    def _update_stats(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM parts")
        parts_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM transactions")
        txn_count = c.fetchone()[0]
        conn.close()
        self.stat_parts.config(text=f"قطعات: {parts_count}")
        self.stat_txn.config(text=f"تراکنش‌ها: {txn_count}")

    def _show_tab(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.config(bg=C["accent"], fg="white")
            else:
                btn.config(bg=C["panel"], fg=C["text"])

        for frame in self.tab_frames.values():
            frame.pack_forget()
        self.tab_frames[key].pack(fill="both", expand=True)

    # ─────────────── محتوا ───────────────
    def _build_content(self):
        self.content = tk.Frame(self.root, bg=C["bg"])
        self.content.pack(side="right", fill="both", expand=True)

        self.tab_frames = {}
        for key in ("parts", "buy", "sell", "log"):
            f = tk.Frame(self.content, bg=C["bg"])
            self.tab_frames[key] = f

        self.build_parts_tab(self.tab_frames["parts"])
        self.build_buy_tab(self.tab_frames["buy"])
        self.build_sell_tab(self.tab_frames["sell"])
        self.build_log_tab(self.tab_frames["log"])

    # ─────────────── هدر صفحه ───────────────
    def _page_header(self, parent, icon, title, subtitle=""):
        h = tk.Frame(parent, bg=C["panel"], padx=20, pady=14)
        h.pack(fill="x")
        tk.Label(h, text=f"{icon}  {title}", font=FONT_LARGE,
                 bg=C["panel"], fg=C["text"]).pack(side="left")
        if subtitle:
            tk.Label(h, text=subtitle, font=FONT_SMALL,
                     bg=C["panel"], fg=C["text_muted"]).pack(side="right", padx=10)

    # ─────────────── کمکی Treeview ───────────────
    def _styled_tree(self, parent, columns, headings, widths, height=12):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Modern.Treeview",
                        background=C["row_even"],
                        foreground=C["text"],
                        fieldbackground=C["row_even"],
                        borderwidth=0,
                        rowheight=30,
                        font=FONT_MAIN)
        style.configure("Modern.Treeview.Heading",
                        background=C["card"],
                        foreground=C["accent"],
                        font=FONT_BOLD,
                        relief="flat")
        style.map("Modern.Treeview",
                  background=[("selected", C["row_selected"])],
                  foreground=[("selected", "white")])

        container = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        container.pack(fill="both", expand=True, padx=15, pady=(10, 15))

        tree = ttk.Treeview(container, columns=columns, show="headings",
                            height=height, style="Modern.Treeview")
        for col, head, w in zip(columns, headings, widths):
            tree.heading(col, text=head)
            tree.column(col, width=w, anchor="center")

        tree.tag_configure("odd",  background=C["row_odd"])
        tree.tag_configure("even", background=C["row_even"])
        tree.tag_configure("low",  background="#3a2a2a", foreground=C["danger"])

        vsb = tk.Scrollbar(container, orient="vertical", command=tree.yview,
                           bg=C["card"], troughcolor=C["bg"], width=10)
        tree.configure(yscrollcommand=vsb.set)

        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.enable_copy(tree)
        return tree

    def enable_copy(self, tree):
        def copy_selection(event=None):
            selected = tree.selection()
            if not selected:
                return
            values = tree.item(selected[0], "values")
            text = "\t".join(str(v) for v in values)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)

        tree.bind("<Control-c>", copy_selection)
        tree.bind("<Control-C>", copy_selection)

        menu = tk.Menu(tree, tearoff=0, bg=C["card"], fg=C["text"],
                       activebackground=C["accent"], activeforeground="white",
                       relief="flat", bd=0)
        menu.add_command(label="📋 کپی ردیف", command=copy_selection)
        tree.bind("<Button-3>", lambda e: menu.post(e.x_root, e.y_root))

    # ─────────────── تب قطعات ───────────────
    def build_parts_tab(self, parent):
        self._page_header(parent, "📦", "لیست قطعات", "مدیریت و جستجوی قطعات انبار")

        # ─ فرم افزودن
        add_card = tk.Frame(parent, bg=C["card"], padx=18, pady=14)
        add_card.pack(fill="x", padx=15, pady=(12, 0))

        tk.Label(add_card, text="افزودن قطعه جدید", font=FONT_BOLD,
                 bg=C["card"], fg=C["accent"]).grid(row=0, column=0, columnspan=6,
                                                    sticky="w", pady=(0, 10))

        fields = [("نام قطعه", "part_name"), ("قیمت خرید (تومان)", "buy_price"),
                  ("قیمت فروش (تومان)", "sell_price")]
        self._entries = {}
        for i, (lbl, key) in enumerate(fields):
            tk.Label(add_card, text=lbl, font=FONT_SMALL,
                     bg=C["card"], fg=C["text_muted"]).grid(row=1, column=i*2,
                                                             sticky="e", padx=(10 if i else 0, 4))
            e = ModernEntry(add_card, width=18)
            e.grid(row=1, column=i*2+1, padx=(0, 12))
            self._entries[key] = e

        self.part_name_entry  = self._entries["part_name"]
        self.buy_price_entry  = self._entries["buy_price"]
        self.sell_price_entry = self._entries["sell_price"]

        ModernButton(add_card, text="➕ افزودن", command=self.add_part,
                     style="success").grid(row=1, column=6, padx=5)

        # ─ نوار جستجو + دکمه‌ها
        bar = tk.Frame(parent, bg=C["bg"], padx=15, pady=8)
        bar.pack(fill="x")

        tk.Label(bar, text="🔍", font=("Segoe UI", 12),
                 bg=C["bg"], fg=C["text_muted"]).pack(side="right")
        self.search_entry = ModernEntry(bar, placeholder="جستجو بر اساس نام یا شناسه…", width=28)
        self.search_entry.pack(side="right", padx=6)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_parts(self.search_entry.get_value()))

        ModernButton(bar, text="✕ پاک", command=self.clear_search,
                     style="neutral").pack(side="right", padx=2)

        ModernButton(bar, text="✏️ ویرایش", command=self.edit_selected_part,
                     style="primary").pack(side="left", padx=2)
        ModernButton(bar, text="🗑 حذف", command=self.delete_selected_part,
                     style="danger").pack(side="left", padx=2)

        # ─ جدول
        cols = ("id", "name", "buy_price", "sell_price", "profit", "quantity")
        heads = ("شناسه", "نام قطعه", "قیمت خرید", "قیمت فروش", "سود واحد", "موجودی")
        widths = (60, 200, 120, 120, 110, 90)
        self.parts_tree = self._styled_tree(parent, cols, heads, widths)
        self.parts_tree.bind("<Double-1>", lambda e: self.edit_selected_part())
        self.load_parts()

    def load_parts(self, search_term=None):
        for row in self.parts_tree.get_children():
            self.parts_tree.delete(row)

        conn = get_connection()
        c = conn.cursor()
        if search_term and search_term.strip():
            term = search_term.strip()
            if term.isdigit():
                c.execute("SELECT id, name, buy_price, sell_price, quantity FROM parts "
                          "WHERE id=? OR name LIKE ?", (int(term), f"%{term}%"))
            else:
                c.execute("SELECT id, name, buy_price, sell_price, quantity FROM parts "
                          "WHERE name LIKE ?", (f"%{term}%",))
        else:
            c.execute("SELECT id, name, buy_price, sell_price, quantity FROM parts")

        for i, row in enumerate(c.fetchall()):
            profit = row[3] - row[2]
            tag = "low" if row[4] == 0 else ("odd" if i % 2 else "even")
            self.parts_tree.insert("", "end", tags=(tag,),
                                   values=(row[0], row[1],
                                           f"{row[2]:,.0f}", f"{row[3]:,.0f}",
                                           f"{profit:,.0f}", row[4]))
        conn.close()
        self._update_stats()

    def on_search_keyrelease(self, event):
        self.load_parts(self.search_entry.get())

    def clear_search(self):
        self.search_entry.clear()
        self.load_parts()

    def add_part(self):
        name = self.part_name_entry.get_value().strip()
        try:
            buy_price  = float(self.buy_price_entry.get_value())
            sell_price = float(self.sell_price_entry.get_value())
        except ValueError:
            messagebox.showerror("خطا", "قیمت‌ها باید عدد باشند.")
            return
        if not name:
            messagebox.showerror("خطا", "نام قطعه نباید خالی باشد.")
            return

        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO parts (name, buy_price, sell_price) VALUES (?, ?, ?)",
                      (name, buy_price, sell_price))
            conn.commit()
            messagebox.showinfo("✅ موفق", f"قطعه «{name}» با موفقیت اضافه شد.")
            for e in (self.part_name_entry, self.buy_price_entry, self.sell_price_entry):
                e.clear()
            self.load_parts(self.search_entry.get_value())
        except sqlite3.IntegrityError:
            messagebox.showerror("خطا", "قطعه‌ای با این نام قبلاً وجود دارد.")
        finally:
            conn.close()

    def edit_selected_part(self):
        selected = self.parts_tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک قطعه را انتخاب کنید.")
            return

        vals = self.parts_tree.item(selected[0], "values")
        part_id, old_name = vals[0], vals[1]
        old_buy  = vals[2].replace(",", "")
        old_sell = vals[3].replace(",", "")

        win = tk.Toplevel(self.root)
        win.title(f"ویرایش قطعه — شناسه {part_id}")
        win.geometry("380x260")
        win.resizable(False, False)
        win.configure(bg=C["bg"])
        win.grab_set()

        tk.Label(win, text="✏️ ویرایش قطعه", font=FONT_TITLE,
                 bg=C["bg"], fg=C["accent"]).pack(pady=(18, 10))

        frm = tk.Frame(win, bg=C["bg"], padx=30)
        frm.pack(fill="x")

        entries = {}
        for i, (lbl, val) in enumerate([("نام قطعه", old_name),
                                         ("قیمت خرید", old_buy),
                                         ("قیمت فروش", old_sell)]):
            tk.Label(frm, text=lbl, font=FONT_SMALL, bg=C["bg"],
                     fg=C["text_muted"]).grid(row=i*2, column=0, sticky="w", pady=(8, 2))
            e = ModernEntry(frm, width=32)
            e.insert(0, val)
            e.grid(row=i*2+1, column=0, sticky="ew", ipady=5)
            entries[lbl] = e

        def save():
            new_name = entries["نام قطعه"].get().strip()
            try:
                new_buy  = float(entries["قیمت خرید"].get())
                new_sell = float(entries["قیمت فروش"].get())
            except ValueError:
                messagebox.showerror("خطا", "قیمت‌ها باید عدد باشند.", parent=win)
                return
            if not new_name:
                messagebox.showerror("خطا", "نام قطعه نمی‌تواند خالی باشد.", parent=win)
                return

            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute("UPDATE parts SET name=?, buy_price=?, sell_price=? WHERE id=?",
                          (new_name, new_buy, new_sell, part_id))
                conn.commit()
                win.destroy()
                self.load_parts(self.search_entry.get_value())
            except sqlite3.IntegrityError:
                messagebox.showerror("خطا", "قطعه‌ای با این نام وجود دارد.", parent=win)
            finally:
                conn.close()

        ModernButton(win, text="💾 ذخیره تغییرات", command=save,
                     style="success").pack(pady=18, ipadx=10, ipady=3)

    def delete_selected_part(self):
        selected = self.parts_tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک قطعه را انتخاب کنید.")
            return
        vals = self.parts_tree.item(selected[0], "values")
        part_id, part_name = vals[0], vals[1]

        if not messagebox.askyesno("⚠️ تأیید حذف",
                                   f"آیا از حذف قطعه «{part_name}» اطمینان دارید؟"):
            return

        conn = get_connection()
        conn.cursor().execute("DELETE FROM parts WHERE id=?", (part_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("✅ موفق", f"قطعه «{part_name}» حذف شد.")
        self.load_parts(self.search_entry.get_value())

    # ─────────────── تب خرید ───────────────
    def build_buy_tab(self, parent):
        self._page_header(parent, "📥", "ثبت خرید", "افزودن موجودی به انبار")
        self._transaction_form(parent, "buy")

    # ─────────────── تب فروش ───────────────
    def build_sell_tab(self, parent):
        self._page_header(parent, "📤", "ثبت فروش", "کاهش موجودی از انبار")
        self._transaction_form(parent, "sell")

    def _transaction_form(self, parent, mode):
        is_buy = mode == "buy"
        card = tk.Frame(parent, bg=C["card"], padx=30, pady=24)
        card.pack(padx=40, pady=30, fill="x")

        tk.Label(card, text="شناسه قطعه", font=FONT_SMALL,
                 bg=C["card"], fg=C["text_muted"]).pack(anchor="w", pady=(0, 4))
        id_entry = ModernEntry(card, placeholder="مثال: 1", width=30)
        id_entry.pack(fill="x", ipady=6, pady=(0, 16))

        tk.Label(card, text="تعداد", font=FONT_SMALL,
                 bg=C["card"], fg=C["text_muted"]).pack(anchor="w", pady=(0, 4))
        qty_entry = ModernEntry(card, placeholder="مثال: 10", width=30)
        qty_entry.pack(fill="x", ipady=6, pady=(0, 24))

        label = "📥 ثبت خرید" if is_buy else "📤 ثبت فروش"
        style = "success" if is_buy else "danger"
        ModernButton(card, text=label, style=style,
                     command=lambda: self._do_transaction(mode, id_entry, qty_entry)
                     ).pack(fill="x", ipady=5)

        tk.Label(card, text="💡 شناسه قطعه را از تب «لیست قطعات» ببینید.",
                 font=FONT_SMALL, bg=C["card"], fg=C["text_muted"]).pack(pady=(14, 0))

        if is_buy:
            self.buy_id_entry  = id_entry
            self.buy_qty_entry = qty_entry
        else:
            self.sell_id_entry  = id_entry
            self.sell_qty_entry = qty_entry

    def _do_transaction(self, mode, id_entry, qty_entry):
        try:
            part_id = int(id_entry.get_value())
            qty     = int(qty_entry.get_value())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("خطا", "شناسه و تعداد باید عدد صحیح مثبت باشند.")
            return

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT name, quantity FROM parts WHERE id=?", (part_id,))
        part = c.fetchone()
        if not part:
            messagebox.showerror("خطا", "قطعه‌ای با این شناسه یافت نشد.")
            conn.close()
            return

        if mode == "sell" and part[1] < qty:
            messagebox.showerror("خطا", f"موجودی کافی نیست. موجودی فعلی: {part[1]}")
            conn.close()
            return

        delta = qty if mode == "buy" else -qty
        c.execute("UPDATE parts SET quantity = quantity + ? WHERE id=?", (delta, part_id))
        c.execute("INSERT INTO transactions (part_id, transaction_type, quantity) VALUES (?, ?, ?)",
                  (part_id, mode, qty))
        conn.commit()
        conn.close()

        verb = "به انبار اضافه شد" if mode == "buy" else "فروخته شد"
        messagebox.showinfo("✅ موفق", f"{qty} عدد از قطعه «{part[0]}» {verb}.")
        id_entry.clear()
        qty_entry.clear()
        self.load_parts()

    # ─────────────── تب لاگ ───────────────
    def build_log_tab(self, parent):
        self._page_header(parent, "📋", "لاگ تراکنش‌ها", "تاریخچه کامل خریدها و فروش‌ها")

        bar = tk.Frame(parent, bg=C["bg"], padx=15, pady=8)
        bar.pack(fill="x")
        ModernButton(bar, text="🔄 به‌روزرسانی", command=self.refresh_log,
                     style="primary").pack(side="right")

        cols   = ("id", "part_name", "type", "qty", "date")
        heads  = ("شناسه", "قطعه", "نوع تراکنش", "تعداد", "تاریخ و ساعت")
        widths = (80, 220, 120, 80, 200)
        self.log_tree = self._styled_tree(parent, cols, heads, widths, height=14)
        self.log_tree.tag_configure("buy",  foreground=C["success"])
        self.log_tree.tag_configure("sell", foreground=C["danger"])
        self.refresh_log()

    def refresh_log(self):
        for row in self.log_tree.get_children():
            self.log_tree.delete(row)

        conn = get_connection()
        c = conn.cursor()
        c.execute("""SELECT t.id, p.name, t.transaction_type, t.quantity, t.date
                     FROM transactions t
                     JOIN parts p ON t.part_id = p.id
                     ORDER BY t.id DESC""")
        for row in c.fetchall():
            t_type = "📥 خرید" if row[2] == "buy" else "📤 فروش"
            tag    = "buy" if row[2] == "buy" else "sell"
            self.log_tree.insert("", "end", tags=(tag,),
                                 values=(row[0], row[1], t_type, row[3], row[4]))
        conn.close()
        self._update_stats()

    # ─────────────── خروج ───────────────
    def logout(self):
        self.root.destroy()
        open_login_window()


# ─────────────────────────────────────────
#  توابع راه‌انداز
# ─────────────────────────────────────────
def open_login_window():
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()

def open_main_app():
    root = tk.Tk()
    MainApp(root)
    root.mainloop()
