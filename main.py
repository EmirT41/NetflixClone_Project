import sys
from datetime import date

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QStackedWidget, QComboBox,
    QCheckBox, QMessageBox, QScrollArea, QGridLayout, QFrame,
    QSpinBox, QDoubleSpinBox, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QTextEdit, QGroupBox,
    QFormLayout, QDialog, QDialogButtonBox, QTabWidget,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QCursor

# ──────────────────────────────────────────────────────────────────────────────
# Stil & Yardımcılar (Orijinal Tasarım Korundu)
# ──────────────────────────────────────────────────────────────────────────────

STYLE_SHEET = """
QWidget { background-color: #141414; color: #e5e5e5; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; }
QPushButton { background-color: #E50914; color: white; border: none; border-radius: 4px; padding: 8px 18px; font-weight: bold; }
QPushButton:hover   { background-color: #F40612; }
QPushButton:disabled{ background-color: #555; color: #aaa; }
QPushButton#secondaryBtn { background-color: transparent; border: 1px solid #777; color: #e5e5e5; }
QPushButton#secondaryBtn:hover { border: 1px solid white; }
QPushButton#dangerBtn  { background-color: #8B0000; }
QPushButton#dangerBtn:hover  { background-color: #A00000; }
QPushButton#successBtn { background-color: #1a7a1a; }
QPushButton#successBtn:hover { background-color: #228B22; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit { background-color: #2a2a2a; border: 1px solid #444; border-radius: 4px; padding: 7px; color: #e5e5e5; }
QLineEdit:focus, QComboBox:focus { border: 1px solid #E50914; }
QLabel#titleLabel  { font-size: 34px; font-weight: bold; color: #E50914; }
QLabel#headerLabel { font-size: 18px; font-weight: bold; }
QLabel#subLabel    { font-size: 12px; color: #aaa; }
QTableWidget { background-color: #1a1a1a; border: 1px solid #333; gridline-color: #2a2a2a; }
QTableWidget::item:selected { background-color: #E50914; color: white; }
QHeaderView::section { background-color: #222; color: #e5e5e5; padding: 6px; border: none; border-bottom: 1px solid #E50914; font-weight: bold; }
QScrollArea  { border: none; }
QGroupBox { border: 1px solid #333; border-radius: 6px; margin-top: 14px; padding: 10px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #E50914; }
QTabWidget::pane { border: 1px solid #333; }
QTabBar::tab { background: #222; color: #aaa; padding: 8px 18px; border-radius: 4px 4px 0 0; }
QTabBar::tab:selected { background: #E50914; color: white; }
QTextEdit { background-color: #2a2a2a; border: 1px solid #444; border-radius: 4px; color: #e5e5e5; }
"""

def lbl(text: str, style: str = "") -> QLabel:
    w = QLabel(text)
    if style: w.setObjectName(style)
    return w

def btn(text: str, obj: str = "") -> QPushButton:
    w = QPushButton(text)
    if obj: w.setObjectName(obj)
    w.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    return w

def info(parent, title, msg):  QMessageBox.information(parent, title, msg)
def warn(parent, title, msg):  QMessageBox.warning(parent, title, msg)

def confirm(parent, title, msg) -> bool:
    return QMessageBox.question(
        parent, title, msg,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    ) == QMessageBox.StandardButton.Yes

def fill_table(table: QTableWidget, rows):
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            if isinstance(val, float): val = f"{val:.1f}"
            item = QTableWidgetItem(str(val) if val is not None else "")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(r, c, item)

def make_table(cols) -> QTableWidget:
    t = QTableWidget()
    t.setColumnCount(len(cols))
    t.setHorizontalHeaderLabels(cols)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    return t

PROG_COLS = ["ID", "Ad", "Tip", "Türler", "Bölüm", "Süre(dk)", "Yıl", "Ort.Puan", "İzlenme"]
FAV_COLS  = PROG_COLS

# ──────────────────────────────────────────────────────────────────────────────
# Pencereler (Login, Register, UserHome, Detail, Watch, Profile, Favorites, History)
# ──────────────────────────────────────────────────────────────────────────────

class LoginPage(QWidget):
    def __init__(self, switch, ctrl):
        super().__init__()
        self.switch, self.ctrl = switch, ctrl
        self._build()

    def _build(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        title = lbl("NETFLIX KLONU", "titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mail_inp = QLineEdit(); self.mail_inp.setPlaceholderText("E-mail"); self.mail_inp.setFixedWidth(320)
        self.pass_inp = QLineEdit(); self.pass_inp.setPlaceholderText("Şifre"); self.pass_inp.setEchoMode(QLineEdit.EchoMode.Password); self.pass_inp.setFixedWidth(320)
        self.pass_inp.returnPressed.connect(self._login)
        login_btn = btn("Giriş Yap"); login_btn.setFixedWidth(320); login_btn.clicked.connect(self._login)
        reg_btn = btn("Kayıt Ol", "secondaryBtn"); reg_btn.setFixedWidth(320); reg_btn.clicked.connect(lambda: self.switch("register"))
        for w in [title, self.mail_inp, self.pass_inp, login_btn, reg_btn]: layout.addWidget(w, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

    def _login(self):
        res = self.ctrl.login(self.mail_inp.text(), self.pass_inp.text())
        if not res["success"]: warn(self, "Giriş Hatası", res["message"]); return
        self.mail_inp.clear(); self.pass_inp.clear()
        self.switch("admin" if res["role"] == "Y" else "home")


class RegisterPage(QWidget):
    def __init__(self, switch, ctrl):
        super().__init__()
        self.switch, self.ctrl = switch, ctrl
        self._build()

    def _build(self):
        form = QFormLayout(); form.setSpacing(10)
        self.name, self.surname, self.mail, self.pw, self.pw2, self.country = QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()
        self.pw.setEchoMode(QLineEdit.EchoMode.Password); self.pw2.setEchoMode(QLineEdit.EchoMode.Password)
        self.dob = QDateEdit(); self.dob.setCalendarPopup(True); self.dob.setDate(QDate(2000, 1, 1)); self.dob.setMaximumDate(QDate.currentDate().addDays(-1))
        self.gender = QComboBox(); self.gender.addItems(["E", "K"])
        for label, w in [("Ad *", self.name), ("Soyad *", self.surname), ("E-mail *", self.mail), ("Şifre *", self.pw), ("Şifre Tekrar *", self.pw2), ("Doğum Tarihi *", self.dob), ("Cinsiyet *", self.gender), ("Ülke *", self.country)]: form.addRow(label, w)
        self.genre_group = QGroupBox("Favori 3 Türünüzü Seçin *")
        self.genre_layout = QGridLayout(); self.genre_group.setLayout(self.genre_layout)
        self.checkboxes = []
        reg_btn = btn("Kayıt İşlemini Tamamla"); reg_btn.clicked.connect(self._register)
        back_btn = btn("Geri Dön", "secondaryBtn"); back_btn.clicked.connect(lambda: self.switch("login"))
        cl = QVBoxLayout()
        cl.addWidget(lbl("Yeni Hesap Oluştur", "headerLabel")); cl.addSpacing(8); cl.addLayout(form); cl.addWidget(self.genre_group); cl.addSpacing(8); cl.addWidget(reg_btn); cl.addWidget(back_btn)
        container = QWidget(); container.setLayout(cl); container.setFixedWidth(480)
        scroll = QScrollArea(); scroll.setWidget(container); scroll.setWidgetResizable(True)
        main = QVBoxLayout(); main.setAlignment(Qt.AlignmentFlag.AlignCenter); main.addWidget(scroll)
        self.setLayout(main)

    def reload_genres(self):
        for cb in self.checkboxes: self.genre_layout.removeWidget(cb); cb.deleteLater()
        self.checkboxes.clear()
        for i, g in enumerate(self.ctrl.getAvailableGenres()):
            cb = QCheckBox(g); self.checkboxes.append(cb); self.genre_layout.addWidget(cb, i // 3, i % 3)

    def _register(self):
        genres = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        d = self.dob.date()
        res = self.ctrl.register(self.name.text(), self.surname.text(), self.pw.text(), self.pw2.text(), self.mail.text(), self.gender.currentText(), date(d.year(), d.month(), d.day()), self.country.text(), genres)
        if not res["success"]: warn(self, "Kayıt Hatası", res["message"]); return
        recs = res.get("recommendations", [])
        msg = "Kayıt başarılı!\n\nSizin İçin Önerilen İçerikler:\n"
        if recs:
            for r in recs: msg += f"  • {r[1]} ({r[2]})  —  Tür: {r[3]}  —  Puan: {r[7]:.1f}\n"
        else: msg += "  Henüz öneri oluşturulamadı."
        info(self, "Başarılı", msg); self._clear(); self.switch("login")

    def _clear(self):
        for w in [self.name, self.surname, self.mail, self.pw, self.pw2, self.country]: w.clear()
        for cb in self.checkboxes: cb.setChecked(False)


class UserHomePage(QWidget):
    def __init__(self, switch, ctrl):
        super().__init__()
        self.switch, self.ctrl = switch, ctrl
        self._build()

    def _build(self):
        top = QHBoxLayout()
        self.search_inp, self.year_inp, self.minrating_inp = QLineEdit(), QLineEdit(), QLineEdit()
        self.search_inp.setPlaceholderText("İçerik adı ile ara…"); self.year_inp.setPlaceholderText("Yıl"); self.year_inp.setFixedWidth(70); self.minrating_inp.setPlaceholderText("Min puan"); self.minrating_inp.setFixedWidth(80)
        self.type_combo, self.genre_combo, self.sort_combo = QComboBox(), QComboBox(), QComboBox()
        self.type_combo.addItems(["Tüm Tipler", "Film", "Dizi"]); self.genre_combo.addItem("Tüm Türler")
        self.sort_combo.addItems(["Tüm İçerikler", "En Yüksek Puanlı", "En Çok İzlenen"])
        search_btn = btn("Ara"); search_btn.clicked.connect(self._search)
        listall_btn = btn("Tümünü Listele", "secondaryBtn"); listall_btn.clicked.connect(self._list_all)
        for w in [self.search_inp, self.type_combo, self.genre_combo, self.sort_combo, self.year_inp, self.minrating_inp, search_btn, listall_btn]: top.addWidget(w)
        
        self.rec_scroll = QScrollArea(); self.rec_scroll.setFixedHeight(60); self.rec_scroll.setWidgetResizable(True)
        self.rec_inner = QWidget(); self.rec_hlay = QHBoxLayout(self.rec_inner); self.rec_scroll.setWidget(self.rec_inner)
        self.table = make_table(PROG_COLS); self.table.doubleClicked.connect(self._open_detail)
        
        bot = QHBoxLayout()
        actions = [("Detay / İzle", self._open_detail, ""), ("Favoriye Ekle", self._add_fav, ""), ("İzleme Geçmişim", lambda: self.switch("history"), "secondaryBtn"), ("Favorilerim", lambda: self.switch("favorites"), "secondaryBtn"), ("Profil", lambda: self.switch("profile"), "secondaryBtn"), ("Çıkış Yap", self._logout, "dangerBtn")]
        for text, slot, style in actions: b = btn(text, style); b.clicked.connect(slot); bot.addWidget(b)
        
        main = QVBoxLayout()
        main.addLayout(top); main.addSpacing(4); main.addWidget(lbl("Sizin İçin Önerilenler", "headerLabel")); main.addWidget(self.rec_scroll); main.addSpacing(4); main.addWidget(lbl("İçerikler", "headerLabel")); main.addWidget(self.table); main.addLayout(bot)
        self.setLayout(main)

    def on_show(self): self._load_genre_combo(); self._load_recs(); self._list_all()
    def _load_genre_combo(self):
        self.genre_combo.clear(); self.genre_combo.addItem("Tüm Türler")
        for g in self.ctrl.getAvailableGenres(): self.genre_combo.addItem(g)
    def _load_recs(self):
        while self.rec_hlay.count():
            item = self.rec_hlay.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for r in self.ctrl.getRecommendations():
            b = btn(f"{r[1][:22]}"); b.clicked.connect(lambda _, p=r[0]: self.switch("detail", program_id=p))
            self.rec_hlay.addWidget(b)
        self.rec_hlay.addStretch()
    def _list_all(self): fill_table(self.table, self.ctrl.listPrograms())
    def _search(self):
        name, genre, ptype, sort, year, minr = self.search_inp.text().strip(), self.genre_combo.currentText(), self.type_combo.currentText(), self.sort_combo.currentText(), self.year_inp.text().strip(), self.minrating_inp.text().strip()
        if sort == "En Yüksek Puanlı": rows = self.ctrl.listTopRated()
        elif sort == "En Çok İzlenen": rows = self.ctrl.listMostWatched()
        elif name: rows = self.ctrl.searchByName(name)
        elif genre != "Tüm Türler": rows = self.ctrl.searchByGenre(genre)
        elif ptype != "Tüm Tipler": rows = self.ctrl.searchByType(ptype)
        elif year:
            try: rows = self.ctrl.searchByYear(int(year))
            except ValueError: warn(self, "Hata", "Geçerli bir yıl girin."); return
        elif minr:
            try: rows = self.ctrl.searchByMinRating(float(minr))
            except ValueError: warn(self, "Hata", "Geçerli bir puan girin."); return
        else: rows = self.ctrl.listPrograms()
        fill_table(self.table, rows)
    def _selected_id(self):
        row = self.table.currentRow()
        if row < 0: warn(self, "Uyarı", "Lütfen bir içerik seçin."); return None
        return int(self.table.item(row, 0).text())
    def _open_detail(self):
        pid = self._selected_id()
        if pid: self.switch("detail", program_id=pid)
    def _add_fav(self):
        pid = self._selected_id()
        if pid: res = self.ctrl.addFavorite(pid); (info if res["success"] else warn)(self, "Favoriler", res["message"])
    def _logout(self): self.ctrl.logout(); self.switch("login")


class DetailPage(QWidget):
    def __init__(self, switch, ctrl):
        super().__init__()
        self.switch, self.ctrl, self.pid = switch, ctrl, None
        self._build()

    def _build(self):
        self.title_lbl = lbl("", "titleLabel"); self.info_lbl = QLabel(); self.info_lbl.setWordWrap(True)
        self.plot_lbl = QLabel(); self.plot_lbl.setWordWrap(True); self.plot_lbl.setObjectName("subLabel")
        self.ep_label, self.ep_combo, self.cont_btn = lbl("Bölüm seç:"), QComboBox(), btn("Kaldığım Yerden Devam Et", "successBtn")
        self.ep_label.setVisible(False); self.ep_combo.setVisible(False); self.cont_btn.setVisible(False); self.cont_btn.clicked.connect(self._continue)
        self.fav_btn, self.watch_btn, self.rate_spin = btn("Favoriye Ekle"), btn("İzle", "successBtn"), QSpinBox()
        self.rate_spin.setRange(1, 10); self.rate_spin.setPrefix("Puan: ")
        rate_btn = btn("Puan Ver"); rate_btn.clicked.connect(self._rate)
        back_btn = btn("Geri", "secondaryBtn"); back_btn.clicked.connect(lambda: self.switch("home"))
        self.fav_btn.clicked.connect(self._toggle_fav); self.watch_btn.clicked.connect(self._watch)
        
        ep_row = QHBoxLayout(); ep_row.addWidget(self.ep_label); ep_row.addWidget(self.ep_combo); ep_row.addWidget(self.cont_btn); ep_row.addStretch()
        act_row = QHBoxLayout(); act_row.addWidget(self.watch_btn); act_row.addWidget(self.fav_btn); act_row.addWidget(self.rate_spin); act_row.addWidget(rate_btn); act_row.addStretch()
        
        layout = QVBoxLayout(); layout.addWidget(self.title_lbl); layout.addWidget(self.info_lbl); layout.addWidget(self.plot_lbl); layout.addSpacing(10); layout.addLayout(ep_row); layout.addLayout(act_row); layout.addWidget(back_btn); layout.addStretch()
        self.setLayout(layout)

    def load(self, pid: int):
        self.pid = pid
        d = self.ctrl.getProgramDetail(pid)
        if not d: warn(self, "Hata", "İçerik bulunamadı."); return
        self.title_lbl.setText(d["program_name"]); self.plot_lbl.setText(d["plot"])
        self.info_lbl.setText(f"Tip: {d['type']} | Türler: {d['genres']} | Bölüm Sayısı: {d['number_of_part']} | Süre: {d['program_runtime']} dk | Yayın Yılı: {d['release_year']} | Ort. Puan: {d['avg_rating']:.1f} | İzlenme: {d['watch_count']} | İzlediniz mi: {'Evet' if d.get('is_watched') else 'Hayır'} | Puanınız: {d.get('user_rating') or '—'}")
        self.fav_btn.setText("Favoriden Çıkar" if d.get("is_favorite") else "Favoriye Ekle")
        is_series = str(d["type"]).lower() == "dizi"
        self.ep_label.setVisible(is_series); self.ep_combo.setVisible(is_series)
        if is_series:
            self.ep_combo.clear()
            for ep in d["episodes"]: self.ep_combo.addItem(f"Bölüm {ep[0]}: {ep[1]}", ep[0])
            prog = d.get("progress")
            self.cont_btn.setVisible(bool(prog and prog[0]))
            if prog and prog[0]: self.cont_btn.setText(f"{prog[0]}. Bölüm — {float(prog[1]):.0f}. dakikadan Devam Et")
        else: self.cont_btn.setVisible(False)

    def _toggle_fav(self):
        d = self.ctrl.getProgramDetail(self.pid)
        res = (self.ctrl.removeFavorite if d and d.get("is_favorite") else self.ctrl.addFavorite)(self.pid)
        if res["success"]: self.load(self.pid)
        else: warn(self, "Favoriler", res["message"])
    def _watch(self): self.switch("watch", program_id=self.pid, episode=self.ep_combo.currentData() if self.ep_combo.isVisible() else 1)
    def _continue(self):
        p = self.ctrl.getProgress(self.pid)
        if p: self.switch("watch", program_id=self.pid, episode=p[0])
    def _rate(self):
        res = self.ctrl.rateProgram(self.pid, self.rate_spin.value())
        (info if res["success"] else warn)(self, "Puan", res["message"])
        if res["success"]: self.load(self.pid)


class WatchPage(QWidget):
    def __init__(self, switch, ctrl):
        super().__init__()
        self.switch, self.ctrl, self.pid, self.episode = switch, ctrl, None, 1
        self._build()

    def _build(self):
        self.title_lbl, self.ep_lbl, self.dur_spin = lbl("", "headerLabel"), lbl(""), QDoubleSpinBox()
        self.dur_spin.setRange(0, 9999)
        dur_row = QHBoxLayout(); dur_row.addWidget(lbl("İzleme süresi (dakika):")); dur_row.addWidget(self.dur_spin); dur_row.addStretch()
        complete_btn = btn("İzlemeyi Tamamla", "successBtn"); complete_btn.clicked.connect(self._complete)
        save_btn = btn("Kaldığım Yere Kaydet", "secondaryBtn"); save_btn.clicked.connect(self._save)
        self.rate_spin = QSpinBox(); self.rate_spin.setRange(1, 10)
        rate_btn = btn("Puan Ver"); rate_btn.clicked.connect(self._rate)
        rate_row = QHBoxLayout(); rate_row.addWidget(lbl("Puan ver (1-10):")); rate_row.addWidget(self.rate_spin); rate_row.addWidget(rate_btn); rate_row.addStretch()
        back_btn = btn("Geri", "secondaryBtn"); back_btn.clicked.connect(lambda: self.switch("detail", program_id=self.pid))
        layout = QVBoxLayout(); layout.addWidget(self.title_lbl); layout.addWidget(self.ep_lbl); layout.addSpacing(20); layout.addLayout(dur_row); layout.addWidget(complete_btn); layout.addWidget(save_btn); layout.addSpacing(20); layout.addLayout(rate_row); layout.addStretch(); layout.addWidget(back_btn)
        self.setLayout(layout)

    def load(self, pid: int, episode: int):
        self.pid, self.episode = pid, episode
        d = self.ctrl.getProgramDetail(pid)
        self.title_lbl.setText(f"▶  {d['program_name'] if d else str(pid)}"); self.ep_lbl.setText(f"Bölüm {episode} / {d['number_of_part'] if d else '?'}")
        self.dur_spin.setValue(0)
        prog = self.ctrl.getProgress(pid)
        if prog and prog[0] == episode and float(prog[1]) > 0:
            if confirm(self, "Devam Et", f"{episode}. bölüm {float(prog[1]):.0f}. dakikadan devam etmek ister misiniz?"): self.dur_spin.setValue(float(prog[1]))

    def _complete(self):
        if self.ctrl.watchContent(self.pid, self.episode, self.dur_spin.value(), True)["success"]: info(self, "Tamamlandı", "İzleme kaydedildi."); self.switch("detail", program_id=self.pid)
    def _save(self): res = self.ctrl.watchContent(self.pid, self.episode, self.dur_spin.value(), False); (info if res["success"] else warn)(self, "Kaydet", res["message"])
    def _rate(self): res = self.ctrl.rateProgram(self.pid, self.rate_spin.value()); (info if res["success"] else warn)(self, "Puan", res["message"])


class ProfilePage(QWidget):
    def __init__(self, switch, ctrl):
        super().__init__()
        self.switch, self.ctrl, self.checkboxes = switch, ctrl, []
        self._build()

    def _build(self):
        self.stats_lbl = lbl("", "subLabel"); form = QFormLayout(); form.setSpacing(10)
        self.name, self.surname, self.mail, self.country, self.pw_new = QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()
        self.pw_new.setPlaceholderText("Yeni şifre (boş = değişmez)"); self.pw_new.setEchoMode(QLineEdit.EchoMode.Password)
        self.dob = QDateEdit(); self.dob.setCalendarPopup(True); self.dob.setMaximumDate(QDate.currentDate().addDays(-1))
        for label, w in [("Ad:", self.name), ("Soyad:", self.surname), ("E-mail:", self.mail), ("Ülke:", self.country), ("Doğum Tarihi:", self.dob), ("Yeni Şifre:", self.pw_new)]: form.addRow(label, w)
        self.genre_group = QGroupBox("Favori Türlerim (3 seç)"); self.genre_glayout = QGridLayout(); self.genre_group.setLayout(self.genre_glayout)
        save_btn = btn("Güncelle", "successBtn"); save_btn.clicked.connect(self._save)
        back_btn = btn("Geri", "secondaryBtn"); back_btn.clicked.connect(lambda: self.switch("home"))
        inner = QVBoxLayout(); inner.addWidget(lbl("Profil", "headerLabel")); inner.addWidget(self.stats_lbl); inner.addLayout(form); inner.addWidget(self.genre_group); inner.addWidget(save_btn); inner.addWidget(back_btn)
        container = QWidget(); container.setLayout(inner)
        scroll = QScrollArea(); scroll.setWidget(container); scroll.setWidgetResizable(True)
        main = QVBoxLayout(); main.addWidget(scroll); self.setLayout(main)

    def on_show(self):
        profile = self.ctrl.getProfile()
        if not profile: return
        self.name.setText(profile["user_name"]); self.surname.setText(profile["user_surname"]); self.mail.setText(profile["mail"]); self.country.setText(profile["country"])
        if profile["date_of_birth"]: self.dob.setDate(QDate(profile["date_of_birth"].year, profile["date_of_birth"].month, profile["date_of_birth"].day))
        self.stats_lbl.setText(f"Toplam İzleme: {profile['total_duration']:.0f} dk  |  İzlenen: {profile['watched_count']}  |  Ort. Puan: {profile['avg_rating']:.1f}")
        for cb in self.checkboxes: self.genre_glayout.removeWidget(cb); cb.deleteLater()
        self.checkboxes.clear()
        saved = set(profile["favorite_genres"])
        for i, g in enumerate(self.ctrl.getAvailableGenres()):
            cb = QCheckBox(g); cb.setChecked(g in saved); self.checkboxes.append(cb); self.genre_glayout.addWidget(cb, i // 3, i % 3)

    def _save(self):
        genres = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        d = self.dob.date()
        res = self.ctrl.updateProfile(self.name.text(), self.surname.text(), self.mail.text(), self.country.text(), date(d.year(), d.month(), d.day()), self.pw_new.text(), genres if genres else None)
        (info if res["success"] else warn)(self, "Profil", res["message"])


class FavoritesPage(QWidget):
    def __init__(self, switch, ctrl):
        super().__init__()
        self.switch, self.ctrl = switch, ctrl
        self._build()

    def _build(self):
        filter_row = QHBoxLayout(); self.genre_combo = QComboBox(); self.genre_combo.addItem("Tüm Türler")
        filter_btn = btn("Filtrele"); filter_btn.clicked.connect(self._load)
        filter_row.addWidget(lbl("Türe Göre Filtrele:")); filter_row.addWidget(self.genre_combo); filter_row.addWidget(filter_btn); filter_row.addStretch()
        self.table = make_table(FAV_COLS)
        remove_btn = btn("Favoriden Çıkar", "dangerBtn"); remove_btn.clicked.connect(self._remove)
        back_btn = btn("Geri", "secondaryBtn"); back_btn.clicked.connect(lambda: self.switch("home"))
        layout = QVBoxLayout(); layout.addWidget(lbl("Favorilerim", "headerLabel")); layout.addLayout(filter_row); layout.addWidget(self.table)
        bot = QHBoxLayout(); bot.addWidget(remove_btn); bot.addWidget(back_btn); bot.addStretch(); layout.addLayout(bot); self.setLayout(layout)

    def on_show(self):
        self.genre_combo.clear(); self.genre_combo.addItem("Tüm Türler")
        for g in self.ctrl.getAvailableGenres(): self.genre_combo.addItem(g)
        self._load()
    def _load(self): fill_table(self.table, self.ctrl.getFavorites("" if self.genre_combo.currentText() == "Tüm Türler" else self.genre_combo.currentText()))
    def _remove(self):
        row = self.table.currentRow()
        if row >= 0 and self.ctrl.removeFavorite(int(self.table.item(row, 0).text()))["success"]: self._load()


class HistoryPage(QWidget):
    def __init__(self, switch, ctrl):
        super().__init__()
        self.switch, self.ctrl = switch, ctrl
        self._build()

    def _build(self):
        self.table = make_table(["Program", "Bölüm", "Süre (dk)", "Tamamlandı?", "İzleme Tarihi", "Puan"])
        back_btn = btn("Geri", "secondaryBtn"); back_btn.clicked.connect(lambda: self.switch("home"))
        layout = QVBoxLayout(); layout.addWidget(lbl("İzleme Geçmişim", "headerLabel")); layout.addWidget(self.table); layout.addWidget(back_btn); self.setLayout(layout)

    def on_show(self):
        rows = self.ctrl.getWatchHistory(); self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            vals = [row[0], row[1], f"{float(row[2]):.1f}" if row[2] is not None else "0", "Evet" if row[3] else "Hayır", str(row[4]) if row[4] else "", str(row[5]) if row[5] else "—"]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(str(v)); item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable); self.table.setItem(r, c, item)

# ──────────────────────────────────────────────────────────────────────────────
# Sayfa 8 — Yönetici Paneli (Geliştirildi)
# ──────────────────────────────────────────────────────────────────────────────

class AdminPage(QWidget):
    def __init__(self, switch, ctrl):
        super().__init__()
        self.switch, self.ctrl = switch, ctrl
        self._build()

    def _build(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_content_tab(), "İçerik Yönetimi")
        self.tabs.addTab(self._build_genre_tab(),   "Tür Yönetimi")
        self.tabs.addTab(self._build_user_tab(),    "Kullanıcı Yönetimi")
        self.tabs.addTab(self._build_report_tab(),  "Raporlar")
        logout_btn = btn("Çıkış Yap", "dangerBtn"); logout_btn.clicked.connect(self._logout)
        layout = QVBoxLayout(); layout.addWidget(lbl("Yönetici Paneli", "headerLabel")); layout.addWidget(self.tabs); layout.addWidget(logout_btn); self.setLayout(layout)

    def _build_content_tab(self):
        w = QWidget(); self.prog_table = make_table(PROG_COLS)
        refresh_btn = btn("Yenile", "secondaryBtn"); refresh_btn.clicked.connect(self._load_programs)
        add_btn = btn("Yeni Program Ekle", "successBtn"); add_btn.clicked.connect(self._add_prog)
        edit_btn = btn("Düzenle"); edit_btn.clicked.connect(self._edit_prog)
        del_btn = btn("Sil", "dangerBtn"); del_btn.clicked.connect(self._del_prog)
        top = QHBoxLayout()
        for b in [refresh_btn, add_btn, edit_btn, del_btn]: top.addWidget(b)
        top.addStretch()
        layout = QVBoxLayout(); layout.addLayout(top); layout.addWidget(self.prog_table); w.setLayout(layout)
        return w

    def _load_programs(self): fill_table(self.prog_table, self.ctrl.listPrograms())
    def _add_prog(self):
        dlg = ProgramDialog(self, self.ctrl)
        if dlg.exec():
            res = self.ctrl.adminAddProgram(**dlg.get_data())
            (info if res["success"] else warn)(self, "Program", res["message"])
            if res["success"]: self._load_programs()
    def _edit_prog(self):
        row = self.prog_table.currentRow()
        if row < 0: warn(self, "Uyarı", "Bir program seçin."); return
        pid = int(self.prog_table.item(row, 0).text())
        detail = self.ctrl.getProgramDetail(pid)
        if detail:
            dlg = ProgramDialog(self, self.ctrl, detail)
            if dlg.exec():
                data = dlg.get_data(); data.pop("filePath", None)
                res = self.ctrl.adminUpdateProgram(programId=pid, **data)
                (info if res["success"] else warn)(self, "Program", res["message"])
                if res["success"]: self._load_programs()
    def _del_prog(self):
        row = self.prog_table.currentRow()
        if row >= 0 and confirm(self, "Sil", f"'{self.prog_table.item(row,1).text()}' silinsin mi?"):
            if self.ctrl.adminDeleteProgram(int(self.prog_table.item(row,0).text()))["success"]: self._load_programs()

    def _build_genre_tab(self):
        w = QWidget(); self.genre_table = make_table(["Tür Adı"])
        ag, ug = QGroupBox("Yeni Tür Ekle"), QGroupBox("Seçili Türü Güncelle")
        self.new_genre_inp, self.upd_genre_inp = QLineEdit(), QLineEdit()
        ab, ub = btn("Ekle", "successBtn"), btn("Güncelle")
        ab.clicked.connect(self._add_genre); ub.clicked.connect(self._update_genre)
        r1, r2 = QHBoxLayout(), QHBoxLayout()
        r1.addWidget(self.new_genre_inp); r1.addWidget(ab); ag.setLayout(r1)
        r2.addWidget(self.upd_genre_inp); r2.addWidget(ub); ug.setLayout(r2)
        db, rb = btn("Seçili Türü Sil", "dangerBtn"), btn("Yenile", "secondaryBtn")
        db.clicked.connect(self._del_genre); rb.clicked.connect(self._load_genres)
        top = QHBoxLayout(); top.addWidget(rb); top.addWidget(db); top.addStretch()
        layout = QVBoxLayout(); layout.addLayout(top); layout.addWidget(self.genre_table); layout.addWidget(ag); layout.addWidget(ug); w.setLayout(layout)
        return w

    def _load_genres(self):
        genres = self.ctrl.getAvailableGenres(); self.genre_table.setRowCount(len(genres))
        for i, g in enumerate(genres):
            item = QTableWidgetItem(g); item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable); self.genre_table.setItem(i, 0, item)
    def _add_genre(self):
        if self.new_genre_inp.text().strip():
            res = self.ctrl.adminAddGenre(self.new_genre_inp.text().strip()); (info if res["success"] else warn)(self, "Tür", res["message"]); self.new_genre_inp.clear(); self._load_genres()
    def _update_genre(self):
        row = self.genre_table.currentRow()
        if row >= 0 and self.upd_genre_inp.text().strip():
            res = self.ctrl.adminUpdateGenre(self.genre_table.item(row,0).text(), self.upd_genre_inp.text().strip()); (info if res["success"] else warn)(self, "Tür", res["message"]); self.upd_genre_inp.clear(); self._load_genres()
    def _del_genre(self):
        row = self.genre_table.currentRow()
        if row >= 0 and confirm(self, "Sil", f"'{self.genre_table.item(row,0).text()}' silinsin mi?"):
            res = self.ctrl.adminDeleteGenre(self.genre_table.item(row,0).text()); (info if res["success"] else warn)(self, "Tür", res["message"]); self._load_genres()

    def _build_user_tab(self):
        w = QWidget(); self.user_table = make_table(["ID", "Ad", "Soyad", "E-mail", "Cinsiyet", "Ülke", "Rol", "Aktif?"])
        refresh_btn = btn("Yenile", "secondaryBtn"); refresh_btn.clicked.connect(self._load_users)
        detail_btn = btn("Detay Göster"); detail_btn.clicked.connect(self._user_detail)
        deactivate_btn = btn("Pasif Yap", "dangerBtn"); deactivate_btn.clicked.connect(lambda: self._set_active(False))
        activate_btn = btn("Aktif Yap", "successBtn"); activate_btn.clicked.connect(lambda: self._set_active(True))
        top = QHBoxLayout()
        for b in [refresh_btn, detail_btn, deactivate_btn, activate_btn]: top.addWidget(b)
        top.addStretch()
        layout = QVBoxLayout(); layout.addLayout(top); layout.addWidget(self.user_table); w.setLayout(layout)
        return w

    def _load_users(self):
        rows = self.ctrl.adminListUsers(); self.user_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            vals = [row[0], row[1], row[2], row[3], row[4], row[6], row[7], "Evet" if row[8] else "Hayır"]
            for c, v in enumerate(vals): item = QTableWidgetItem(str(v) if v is not None else ""); item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable); self.user_table.setItem(r, c, item)

    def _user_detail(self):
        row = self.user_table.currentRow()
        if row < 0: warn(self, "Uyarı", "Bir kullanıcı seçin."); return
        uid = int(self.user_table.item(row, 0).text())
        d = self.ctrl.adminGetUserDetail(uid)
        if not d: return
        
        # Komple Geçmiş İçin Scroll Modalı (Düzeltildi) 
        dlg = QDialog(self); dlg.setWindowTitle("Kullanıcı İzleme Detayı"); dlg.setMinimumSize(500, 400)
        vlay = QVBoxLayout(dlg)
        u = d["user"]
        summary = lbl(f"Kullanıcı: {u[1]} {u[2]} ({u[4]})\nToplam İzleme: {d['total_duration']:.0f} dk | İzlenen: {d['watched_count']} içerik | Ort. Puan: {d['avg_rating']:.1f}", "headerLabel")
        vlay.addWidget(summary)
        
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll_inner = QWidget(); scroll_lay = QVBoxLayout(scroll_inner)
        scroll_lay.addWidget(lbl("Tüm İzleme Geçmişi:", "headerLabel"))
        
        for h in d["watch_history"]:
            scroll_lay.addWidget(lbl(f"  • {h[0]} - Bölüm {h[1]} ({float(h[2]):.0f} dk) - Tarih: {h[4]} - Puan: {h[5] if h[5] else '—'}"))
        
        scroll_inner.setLayout(scroll_lay); scroll.setWidget(scroll_inner); vlay.addWidget(scroll)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok); bb.accepted.connect(dlg.accept); vlay.addWidget(bb)
        dlg.exec()

    def _set_active(self, active: bool):
        row = self.user_table.currentRow()
        if row >= 0: self.ctrl.setUserActive(int(self.user_table.item(row,0).text()), active); self._load_users()
    def _build_report_tab(self):
        w = QWidget(); self.report_text = QTextEdit(); self.report_text.setReadOnly(True)
        load_btn = btn("Raporları Yükle"); load_btn.clicked.connect(self._load_reports)
        layout = QVBoxLayout(); layout.addWidget(load_btn); layout.addWidget(self.report_text); w.setLayout(layout)
        return w

    def _load_reports(self):
        r = self.ctrl.adminGetReports()
        if not r: self.report_text.setPlainText("Yetki hatası."); return
        lines = ["═══════════════════════ ÖZET ════════════════════════", f"  Kullanıcı Sayısı : {r['user_count']}", f"  Toplam İzlenme   : {r['total_watches']}", f"  Toplam Puan      : {r['total_ratings']}", "", "═══════════════ EN ÇOK İZLENEN 10 İÇERİK ════════════"]
        for x in r["top10_most_watched"]: lines.append(f"  {x[0]:<40} {x[1]} izlenme")
        lines += ["", "═══════════════ EN YÜKSEK PUANLI 10 İÇERİK ══════════"]
        for x in r["top10_highest_rated"]: lines.append(f"  {x[0]:<40} {x[1]:.2f} puan")
        lines += ["", "═══════════════════ EN ÇOK İZLENEN TÜRLER ════════════"]
        for x in r["most_watched_genres"]: lines.append(f"  {x[0]:<30} {x[1]} izlenme")
        lines += ["", "════════════════════ EN AKTİF KULLANICILAR ═══════════"]
        for x in r["most_active_users"]: lines.append(f"  {x[0]:<35} {x[1]} izlenme")
        lines += ["", "═══════════════ SON 7 GÜNDE İZLENENLER ══════════════"]
        for x in r["last7days"]: lines.append(f"  {x[0]:<40} {x[1]} izlenme")
        self.report_text.setPlainText("\n".join(lines))

    def on_show(self): self._load_programs(); self._load_users(); self._load_genres()
    def _logout(self): self.ctrl.logout(); self.switch("login")

# ──────────────────────────────────────────────────────────────────────────────
# Program Ekle / Düzenle Diyaloğu (Bölüm Ekleme İsteri Entegre Edildi)
# ──────────────────────────────────────────────────────────────────────────────

class ProgramDialog(QDialog):
    def __init__(self, parent, ctrl, prefill: dict = None):
        super().__init__(parent)
        self.ctrl, self.prefill = ctrl, prefill
        self.setWindowTitle("Program Ekle / Düzenle")
        self.setMinimumWidth(550)
        self._build(prefill)

    def _build(self, p):
        form = QFormLayout()
        self.name_inp = QLineEdit(p["program_name"] if p else "")
        self.plot_inp = QTextEdit(p["plot"] if p else ""); self.plot_inp.setFixedHeight(80)
        self.parts_spin = QSpinBox(); self.parts_spin.setRange(1, 9999)
        self.rt_spin = QDoubleSpinBox(); self.rt_spin.setRange(1, 9999)
        self.year_inp = QDateEdit(); self.year_inp.setCalendarPopup(True); self.year_inp.setDate(QDate.currentDate())
        self.type_combo = QComboBox()
        for t in self.ctrl.getAvailableTypes(): self.type_combo.addItem(t)
        self.fp_inp = QLineEdit(p.get("file_path", "") if p else "")

        if p:
            self.parts_spin.setValue(p.get("number_of_part") or 1)
            self.rt_spin.setValue(float(p.get("program_runtime") or 90))
            if p.get("release_year"): self.year_inp.setDate(QDate(p["release_year"].year, p["release_year"].month, p["release_year"].day))
            idx = self.type_combo.findText(p.get("type", ""))
            if idx >= 0: self.type_combo.setCurrentIndex(idx)

        form.addRow("Program Adı *:",  self.name_inp)
        form.addRow("Açıklama *:",     self.plot_inp)
        form.addRow("Bölüm Sayısı:",   self.parts_spin)
        form.addRow("Süre (dk):",      self.rt_spin)
        form.addRow("Yayın Yılı:",     self.year_inp)
        form.addRow("Tip:",            self.type_combo)
        form.addRow("Dosya Yolu:",     self.fp_inp)

        genre_group = QGroupBox("Türler"); gl = QGridLayout(); self.genre_cbs = []
        saved = set(p["genres"].split(", ")) if p and p.get("genres") else set()
        for i, g in enumerate(self.ctrl.getAvailableGenres()):
            cb = QCheckBox(g); cb.setChecked(g in saved); self.genre_cbs.append(cb); gl.addWidget(cb, i // 3, i % 3)
        genre_group.setLayout(gl)

        # Dizi İçin Bölüm Ekleme Aksiyon Satırı (Yeni İster Çözümü) 
        self.ep_manage_btn = btn("Bu Diziye Yeni Bölüm Tanımla", "successBtn")
        self.ep_manage_btn.clicked.connect(self._add_episode_clicked)
        self.type_combo.currentTextChanged.connect(self._toggle_ep_btn)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form); layout.addWidget(genre_group); layout.addWidget(self.ep_manage_btn); layout.addWidget(btns)
        self.setLayout(layout)
        self._toggle_ep_btn(self.type_combo.currentText())

    def _toggle_ep_btn(self, current_text):
        # Sadece mevcut bir dizi düzenlenirken veya tipi "Dizi" seçildiğinde bölüm eklenebilir
        self.ep_manage_btn.setVisible(current_text == "Dizi" and self.prefill is not None)

    def _add_episode_clicked(self):
        if not self.prefill: return
        pid = self.prefill["program_id"]
        
        # Bölüm Bilgileri İçin Hızlı Bir QDialog Pop-up'ı
        dlg = QDialog(self); dlg.setWindowTitle("Yeni Bölüm Ekle"); form = QFormLayout(dlg)
        num_spin = QSpinBox(); num_spin.setRange(1, 1000)
        title_inp = QLineEdit(); dur_spin = QDoubleSpinBox(); dur_spin.setRange(1, 180)
        fp_inp = QLineEdit()
        form.addRow("Bölüm No:", num_spin); form.addRow("Bölüm Başlığı:", title_inp); form.addRow("Süre (dk):", dur_spin); form.addRow("Dosya Yolu:", fp_inp)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject); form.addWidget(bb)
        
        if dlg.exec() == QDialog.DialogCode.Accepted:
            res = self.ctrl.adminAddEpisode(pid, num_spin.value(), title_inp.text(), dur_spin.value(), fp_inp.text())
            (info if res["success"] else warn)(self, "Bölüm", res["message"])

    def get_data(self) -> dict:
        d = self.year_inp.date()
        return {
            "programName":    self.name_inp.text(),
            "plot":           self.plot_inp.toPlainText(),
            "numberOfPart":   self.parts_spin.value(),
            "programRuntime": self.rt_spin.value(),
            "releaseYear":    date(d.year(), d.month(), d.day()),
            "ptype":          self.type_combo.currentText(),
            "filePath":       self.fp_inp.text(),
            "genres":         [cb.text() for cb in self.genre_cbs if cb.isChecked()],
        }

# ──────────────────────────────────────────────────────────────────────────────
# Ana Uygulama Nesnesi (NetflixApp)
# ──────────────────────────────────────────────────────────────────────────────

class NetflixApp(QMainWindow):
    PAGE = { "login": 0, "register": 1, "home": 2, "detail": 3, "watch": 4, "profile": 5, "favorites": 6, "history": 7, "admin": 8 }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("İçerik Yönetim Platformu"); self.setGeometry(100, 100, 1280, 800); self.setStyleSheet(STYLE_SHEET)
        try:
            from programController import ProgramController
            self.ctrl = ProgramController()
        except Exception as e:
            QMessageBox.critical(self, "Veritabanı Hatası", f"Veritabanına bağlanılamadı:\n{e}"); sys.exit(1)

        self.stack = QStackedWidget(); self.setCentralWidget(self.stack)
        self.login_page = LoginPage(self.switch_page, self.ctrl)
        self.register_page = RegisterPage(self.switch_page, self.ctrl)
        self.home_page = UserHomePage(self.switch_page, self.ctrl)
        self.detail_page = DetailPage(self.switch_page, self.ctrl)
        self.watch_page = WatchPage(self.switch_page, self.ctrl)
        self.profile_page = ProfilePage(self.switch_page, self.ctrl)
        self.favorites_page = FavoritesPage(self.switch_page, self.ctrl)
        self.history_page = HistoryPage(self.switch_page, self.ctrl)
        self.admin_page = AdminPage(self.switch_page, self.ctrl)

        for page in [self.login_page, self.register_page, self.home_page, self.detail_page, self.watch_page, self.profile_page, self.favorites_page, self.history_page, self.admin_page]: self.stack.addWidget(page)

    def switch_page(self, name: str, **kwargs):
        self.stack.setCurrentIndex(self.PAGE.get(name, 0))
        if name == "register": self.register_page.reload_genres()
        elif name == "home": self.home_page.on_show()
        elif name == "detail": self.detail_page.load(kwargs["program_id"])
        elif name == "watch": self.watch_page.load(kwargs["program_id"], kwargs.get("episode", 1))
        elif name == "profile": self.profile_page.on_show()
        elif name == "favorites": self.favorites_page.on_show()
        elif name == "history": self.history_page.on_show()
        elif name == "admin": self.admin_page.on_show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NetflixApp()
    window.show()
    sys.exit(app.exec())