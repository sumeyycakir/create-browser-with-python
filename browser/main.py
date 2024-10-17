import sys
import os
import json
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QTabWidget, QWidget, QVBoxLayout, QMessageBox, QListWidget, QDialog, QSizePolicy, QPushButton, QTabBar, QListWidgetItem
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon

class BrowserTab(QWidget):
    def __init__(self, main_window, close_callback):
        super(BrowserTab, self).__init__()
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('http://google.com'))

        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        self.setLayout(layout)

        self.close_callback = close_callback
        self.browser.titleChanged.connect(lambda title: self.update_title(title, main_window))

    def set_url(self, url):
        self.browser.setUrl(QUrl(url))

    def update_title(self, title, main_window):
        current_index = main_window.tabs.indexOf(self)
        if current_index != -1:
            main_window.tabs.setTabText(current_index, title)

class BookmarkDialog(QDialog):
    def __init__(self, bookmarks, parent=None):
        super(BookmarkDialog, self).__init__(parent)
        self.setWindowTitle("Yer İşaretleri")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        self.bookmark_list = QListWidget()

        self.bookmarks = bookmarks
        for index, bookmark in enumerate(bookmarks):
            item = QListWidgetItem(f"{bookmark['title']} ({bookmark['url']})")
            item.setData(Qt.UserRole, index)  # Yer işaretinin indeksini sakla
            self.bookmark_list.addItem(item)

        self.bookmark_list.itemDoubleClicked.connect(self.open_bookmark)
        layout.addWidget(self.bookmark_list)

        # Silme butonu
        delete_btn = QPushButton("Sil")
        delete_btn.clicked.connect(self.delete_bookmark)
        layout.addWidget(delete_btn)

        self.setLayout(layout)

    def open_bookmark(self, item):
        text = item.text()
        url = text.split('(')[-1].strip(')')
        main_window = self.parent()
        main_window.get_current_tab().set_url(url)
        self.close()

    def delete_bookmark(self):
        current_item = self.bookmark_list.currentItem()
        if current_item:
            index = current_item.data(Qt.UserRole)
            del self.bookmarks[index]  # Yer işaretini sil
            self.parent().save_bookmarks()  # Güncellemeyi kaydet
            self.close()  # Diyaloğu kapat
            QMessageBox.information(self, "Başarılı", "Yer işareti silindi.")
        else:
            QMessageBox.warning(self, "Hata", "Silmek için bir yer işareti seçin.")

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowIcon(QIcon("C:/Users/ssume/browser/icon/iconbrowser.jpg"))
        self.setWindowTitle("Chrome Killer")
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.add_new_tab()  # Varsayılan sekme

        # Araç çubuğu
        navbar = QToolBar()
        self.addToolBar(navbar)

        # Simge dosyalarının yolu
        icon_path = "C:/Users/ssume/browser/icon/"

        # Ana Sayfa butonu
        home_btn = QAction(QIcon(icon_path + 'ana sayfa.png'), 'Ana Sayfa', self)
        home_btn.triggered.connect(lambda: self.get_current_tab().set_url('http://google.com'))
        navbar.addAction(home_btn)

        # Geri butonu
        back_btn = QAction(QIcon(icon_path + 'geri.png'), 'Geri', self)
        back_btn.triggered.connect(lambda: self.get_current_tab().browser.back())
        navbar.addAction(back_btn)

        # İleri butonu
        forward_btn = QAction(QIcon(icon_path + 'ileri.png'), 'İleri', self)
        forward_btn.triggered.connect(lambda: self.get_current_tab().browser.forward())
        navbar.addAction(forward_btn)

        # Yenile butonu
        reload_btn = QAction(QIcon(icon_path + 'yenile.png'), 'Yenile', self)
        reload_btn.triggered.connect(lambda: self.get_current_tab().browser.reload())
        navbar.addAction(reload_btn)

        # Yeni sekme butonu
        new_tab_btn = QAction(QIcon(icon_path + 'yeni sekme.png'), 'Yeni Sekme', self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        navbar.addAction(new_tab_btn)

        # Sağ üst köşe için bir widget oluştur
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        navbar.addWidget(spacer)

        # Yer işareti ekle butonu
        bookmark_btn = QAction(QIcon(icon_path + 'yer işareti ekle.png'), 'Yer İşareti Ekle', self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        navbar.addAction(bookmark_btn)

        # Yer işaretlerini göster butonu
        show_bookmarks_btn = QAction(QIcon(icon_path + 'yer işaretleri.png'), 'Yer İşaretlerini Göster', self)
        show_bookmarks_btn.triggered.connect(self.show_bookmarks)
        navbar.addAction(show_bookmarks_btn)

        # Çeviri butonu
        translate_btn = QAction(QIcon(icon_path + 'çeviri.png'), 'Otomatik Çeviri', self)
        translate_btn.triggered.connect(self.translate_current_page)
        navbar.addAction(translate_btn)

        self.resize(900, 600)

        # Yer işaretlerini saklamak için
        self.bookmarks = self.load_bookmarks()

    def load_bookmarks(self):
        if os.path.exists('bookmarks.json'):
            with open('bookmarks.json', 'r') as file:
                return json.load(file)
        return []

    def save_bookmarks(self):
        with open('bookmarks.json', 'w') as file:
            json.dump(self.bookmarks, file)

    def add_bookmark(self):
        current_tab = self.get_current_tab()
        url = current_tab.browser.url().toString()
        title = current_tab.browser.title()

        if not url:
            QMessageBox.warning(self, "Hata", "Geçerli bir URL yok.")
            return

        bookmark = {"title": title, "url": url}
        self.bookmarks.append(bookmark)
        self.save_bookmarks()
        QMessageBox.information(self, "Yer İşareti Eklendi", f"{title} için yer işareti eklendi!")

    def show_bookmarks(self):
        dialog = BookmarkDialog(self.bookmarks, self)
        dialog.exec_()

    def translate_current_page(self):
        current_tab = self.get_current_tab()
        url = current_tab.browser.url().toString()
        translated_url = f"https://translate.google.com/translate?sl=auto&tl=tr&u={url}"
        current_tab.set_url(translated_url)

    def add_new_tab(self):
        new_tab = BrowserTab(main_window=self, close_callback=lambda: self.close_tab(self.tabs.indexOf(new_tab)))
        tab_index = self.tabs.addTab(new_tab, "")
        self.tabs.setCurrentWidget(new_tab)

        # Sekme kapatma butonu
        close_button = QPushButton("✖")
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet("border: none; background: transparent; color: gray;")
        close_button.clicked.connect(lambda: self.close_tab(tab_index))
        self.tabs.tabBar().setTabButton(tab_index, QTabBar.RightSide, close_button)

        new_tab.update_title("Yeni Sekme", self)

    def close_tab(self, index):
        if index >= 0:
            self.tabs.removeTab(index)

    def get_current_tab(self):
        return self.tabs.currentWidget()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
