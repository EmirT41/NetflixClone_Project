import unittest
from unittest.mock import MagicMock, patch
from datetime import date
from programController import ProgramController

class TestProgramController(unittest.TestCase):

    @patch('programController.DatabaseConnection')
    @patch('programController.TableCreator')
    def setUp(self, mock_table_creator, mock_db_conn):
        """Her testten önce boş ve taklit edilmiş (mock) bir controller oluşturur."""
        self.mock_db = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_db.getCursor.return_value = self.mock_cursor
        mock_db_conn.return_value = self.mock_db
        
        # Controller'ı taklit veritabanıyla ayağa kaldır
        self.controller = ProgramController()

    def test_login_empty_fields(self):
        """Boş e-mail veya şifre ile giriş denemesi testi"""
        res = self.controller.login("   ", "123456")
        self.assertFalse(res["success"])
        self.assertEqual(res["message"], "E-mail boş bırakılamaz.")

        res = self.controller.login("test@mail.com", "")
        self.assertFalse(res["success"])
        self.assertEqual(res["message"], "Şifre boş bırakılamaz.")

    def test_login_invalid_email_format(self):
        """Hatalı e-mail formatı doğrulaması testi"""
        res = self.controller.login("emirhanmailcom", "123456")
        self.assertFalse(res["success"])
        self.assertIn("Geçersiz e-mail formatı", res["message"])

    def test_login_wrong_password(self):
        """Doğru e-mail fakat yanlış şifre uyarısı testi"""
        # Veritabanından dönecek örnek sahte kullanıcı satırı veri kümesi:
        # id(0), name(1), surname(2), password(3), mail(4), gender(5), dob(6), country(7), role(8), is_active(9)
        fake_user = (1, "Emirhan", "User", "dogrusifre123", "emirhan@mail.com", "E", "2004-01-01", "Türkiye", "K", 1)
        self.mock_cursor.fetchone.return_value = fake_user

        res = self.controller.login("emirhan@mail.com", "yanlissifre")
        self.assertFalse(res["success"])
        self.assertEqual(res["message"], "Şifre hatalı.")

    def test_login_passive_account(self):
        """Pasif durumdaki kullanıcının sisteme giriş engelinin testi"""
        # is_active sütunu 0 (Yani pasif kullanıcı)
        fake_user = (2, "Ahmet", "Clerk", "123456", "ahmet@mail.com", "E", "1000-01-01", "Türkiye", "K", 0)
        self.mock_cursor.fetchone.return_value = fake_user

        res = self.controller.login("ahmet@mail.com", "123456")
        self.assertFalse(res["success"])
        self.assertIn("Hesabınız pasif duruma alınmıştır", res["message"])

    def test_register_password_mismatch(self):
        """Kayıt esnasında şifrelerin birbiriyle uyuşmaması durumu testi"""
        res = self.controller.register(
            "Emirhan", "Dev", "sifre123", "sifre1234_farkli",
            "emirhan@kostu.edu.tr", "E", date(2004, 5, 20), "Türkiye", ["Aksiyon", "Dram", "Bilim Kurgu"]
        )
        self.assertFalse(res["success"])
        self.assertIn("Şifre ve şifre tekrarı eşleşmiyor.", res["message"])

    def test_register_insufficient_genres(self):
        """Eksik sayıda favori tür seçildiğinde hata fırlatma testi"""
        res = self.controller.register(
            "Emirhan", "Dev", "sifre123", "sifre123",
            "emirhan@kostu.edu.tr", "E", date(2004, 5, 20), "Türkiye", ["Aksiyon", "Dram"] # Sadece 2 adet
        )
        self.assertFalse(res["success"])
        self.assertIn("Tam olarak 3 farklı favori tür seçilmelidir.", res["message"])

    def test_rate_program_without_watching_yet(self):
        """Henüz izlenmemiş bir içeriğe puan verilmesini engelleme testi"""
        # Mevcut bir aktif kullanıcı oturumu simüle et
        self.controller.current_user = (1, "Emirhan", "User", "123456", "emirhan@mail.com", "E", "2004-01-01", "Türkiye", "K", 1)
        
        # userProgRepo.hasWatched taklidi False dönsün
        self.controller.userProgRepo.hasWatched = MagicMock(return_value=False)

        res = self.controller.rateProgram(programId=99, rating=8)
        self.assertFalse(res["success"])
        self.assertIn("Bu içeriği henüz izlemediniz", res["message"])

    def test_admin_authority_guard_on_add_program(self):
        """Yönetici rolü ('Y') olmayan kullanıcının içerik ekleme yetki bariyeri testi"""
        # Rolü 'K' (Normal Kullanıcı) olan bir oturum
        self.controller.current_user = (1, "Emirhan", "User", "123456", "emirhan@mail.com", "E", "2004-01-01", "Türkiye", "K", 1)

        res = self.controller.adminAddProgram(
            "Yeni Film", "Harika bir film konusu", 1, 120.0, date(2026, 1, 1), "Film", "C:/path", ["Dram"]
        )
        self.assertFalse(res["success"])
        self.assertEqual(res["message"], "Yetkiniz yok.")

if __name__ == '__main__':
    unittest.main()

    #Mock ile veritabanına zarar vermeden taklit ederek testleri yaptım. Önemli olan yerlerde try-except blokları kullanarak hata durumlarında sistemin çökmemesini ve kullanıcıya anlamlı bir mesaj göstermesini sağladım.