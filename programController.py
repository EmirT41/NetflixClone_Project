"""
programController.py
~~~~~~~~~~~~~~~~~~~~
Uygulamanın tüm iş mantığını barındıran denetleyici.
GUI katmanı yalnızca bu sınıf üzerinden veritabanıyla konuşur.
"""

import re
from datetime import date
from typing import Optional, List

from database_connection import DatabaseConnection
from table_creator import TableCreator
from repositories import (
    UserRepository, UserGenreRepository, FavoriteRepository,
    RoleRepository, UserProgramRepositories, ProgramRepository,
    GenreRepository, ProgramGenreRepository, ProgramTypeRepository,
    SessionLogRepository, WatchLogRepository, EpisodeRepository,
    ReportRepository,
)


class ProgramController:

    def __init__(self):
        self.db = DatabaseConnection()

        tc = TableCreator(self.db)
        tc.createTables()

        # Repository'ler
        self.roleRepo       = RoleRepository(self.db)
        self.userRepo       = UserRepository(self.db)
        self.userGenreRepo  = UserGenreRepository(self.db)
        self.favRepo        = FavoriteRepository(self.db)
        self.userProgRepo   = UserProgramRepositories(self.db)
        self.progRepo       = ProgramRepository(self.db)
        self.genreRepo      = GenreRepository(self.db)
        self.progGenreRepo  = ProgramGenreRepository(self.db)
        self.progTypeRepo   = ProgramTypeRepository(self.db)
        self.sessionLogRepo = SessionLogRepository(self.db)
        self.watchLogRepo   = WatchLogRepository(self.db)
        self.episodeRepo    = EpisodeRepository(self.db)
        self.reportRepo     = ReportRepository(self.db)

        # Varsayılan tipler
        for t in ("Film", "Dizi"):
            self.progTypeRepo.addProgramType(t)

        self.current_user = None  # tuple: users satırı

    # ──────────────────────────────────────────────────────────────
    # Oturum
    # ──────────────────────────────────────────────────────────────

    def login(self, mail: str, password: str) -> dict:
        mail = mail.strip()
        if not mail:
            return {"success": False, "message": "E-mail boş bırakılamaz."}
        if not password:
            return {"success": False, "message": "Şifre boş bırakılamaz."}
        if not self._valid_email(mail):
            return {"success": False, "message": "Geçersiz e-mail formatı."}

        user = self.userRepo.getUserByMail(mail)
        if user is None:
            self.sessionLogRepo.addSessionLog(mail, False)
            return {"success": False, "message": "Bu e-mail ile kayıtlı hesap bulunamadı."}

        # sütun sırası: user_id(0) name(1) surname(2) password(3) mail(4)
        #               gender(5) dob(6) country(7) role(8) is_active(9)
        if user[3] != password:
            self.sessionLogRepo.addSessionLog(mail, False)
            return {"success": False, "message": "Şifre hatalı."}

        if not user[9]:
            self.sessionLogRepo.addSessionLog(mail, False)
            return {"success": False, "message": "Hesabınız pasif duruma alınmıştır."}

        self.sessionLogRepo.addSessionLog(mail, True)
        self.current_user = user
        return {"success": True, "message": "Giriş başarılı.", "role": user[8]}

    def logout(self):
        self.current_user = None

    # ──────────────────────────────────────────────────────────────
    # Kayıt
    # ──────────────────────────────────────────────────────────────

    def register(self, userName: str, userSurname: str, password: str,
                 passwordConfirm: str, mail: str, gender: str,
                 dateOfBirth: date, country: str, genres: List[str]) -> dict:
        errors = []
        for field, name in [(userName, "Ad"), (userSurname, "Soyad"),
                             (mail, "E-mail"), (password, "Şifre"),
                             (gender, "Cinsiyet"), (country, "Ülke")]:
            if not str(field).strip():
                errors.append(f"{name} boş bırakılamaz.")

        if mail.strip() and not self._valid_email(mail):
            errors.append("Geçersiz e-mail formatı.")
        if len(password) < 6:
            errors.append("Şifre en az 6 karakter olmalıdır.")
        if password != passwordConfirm:
            errors.append("Şifre ve şifre tekrarı eşleşmiyor.")
        if dateOfBirth >= date.today():
            errors.append("Doğum tarihi bugünden büyük olamaz.")
        if len(genres) != 3:
            errors.append("Tam olarak 3 farklı favori tür seçilmelidir.")
        if mail.strip() and self.userRepo.mailExists(mail.strip()):
            errors.append("Bu e-mail adresi zaten kayıtlıdır.")

        if errors:
            return {"success": False, "message": "\n".join(errors)}

        # Türlerin veritabanında var olduğundan emin ol
        for g in genres:
            if not self.genreRepo.genreExists(g):
                self.genreRepo.addGenre(g)

        user_id = self.userRepo.addUser(
            userName.strip(), userSurname.strip(), password,
            mail.strip(), gender, dateOfBirth, country.strip(), "K"
        )
        for g in genres:
            self.userGenreRepo.addUserGenre(user_id, g)

        # Her türden en yüksek puanlı 2 içerik → 6 öneri
        recommendations = self.progRepo.getRecommendationsByGenres(genres, [], limit=2)
        return {"success": True, "message": "Kayıt başarılı!", "recommendations": recommendations}

    # ──────────────────────────────────────────────────────────────
    # Profil
    # ──────────────────────────────────────────────────────────────

    def getProfile(self) -> Optional[dict]:
        if not self.current_user:
            return None
        uid   = self.current_user[0]
        stats = self.userRepo.getUserStats(uid)
        u     = self.current_user
        return {
            "user_id":       u[0],
            "user_name":     u[1],
            "user_surname":  u[2],
            "mail":          u[4],
            "gender":        u[5],
            "date_of_birth": u[6],
            "country":       u[7],
            "user_role":     u[8],
            "total_duration":  float(stats[0]) if stats[0] else 0.0,
            "watched_count":   int(stats[1]) if stats[1] else 0,
            "avg_rating":      float(stats[2]) if stats[2] else 0.0,
            "favorite_genres": self.userGenreRepo.getUserGenres(uid),
        }

    def updateProfile(self, userName: str, userSurname: str, mail: str,
                      country: str, dateOfBirth: date,
                      newPassword: str = "", newGenres: Optional[List[str]] = None) -> dict:
        if not self.current_user:
            return {"success": False, "message": "Oturum açılmamış."}
        uid = self.current_user[0]
        errors = []
        if not self._valid_email(mail):
            errors.append("Geçersiz e-mail formatı.")
        if dateOfBirth >= date.today():
            errors.append("Doğum tarihi bugünden büyük olamaz.")
        if newPassword and len(newPassword) < 6:
            errors.append("Şifre en az 6 karakter olmalıdır.")
        if newGenres is not None and len(newGenres) != 3:
            errors.append("3 favori tür seçilmelidir.")
        if errors:
            return {"success": False, "message": "\n".join(errors)}

        self.userRepo.updateUser(uid, userName, userSurname, mail, country, dateOfBirth)
        if newPassword:
            self.userRepo.updatePassword(uid, newPassword)
        if newGenres is not None:
            for g in newGenres:
                if not self.genreRepo.genreExists(g):
                    self.genreRepo.addGenre(g)
            self.userGenreRepo.deleteUserGenres(uid)
            for g in newGenres:
                self.userGenreRepo.addUserGenre(uid, g)

        self.current_user = self.userRepo.getUserByMail(mail)
        return {"success": True, "message": "Profil güncellendi."}

    # ──────────────────────────────────────────────────────────────
    # İçerik Listeleme & Arama
    # ──────────────────────────────────────────────────────────────

    def listPrograms(self):
        return self.progRepo.listThePrograms()

    def listTopRated(self, limit: int = 10):
        return self.progRepo.listTopRatedPrograms(limit)

    def listMostWatched(self, limit: int = 10):
        return self.progRepo.listMostWatchedPrograms(limit)

    def searchByName(self, name: str):
        return self.progRepo.searchByProgramName(name)

    def searchByType(self, ptype: str):
        return self.progRepo.searchByProgramType(ptype)

    def searchByGenre(self, genre: str):
        return self.progRepo.searchByProgramGenre(genre)

    def searchByYear(self, year: int):
        return self.progRepo.searchByReleaseYear(year)

    def searchByMinRating(self, minRating: float):
        return self.progRepo.searchByMinRating(minRating)

    def getAvailableGenres(self) -> List[str]:
        return self.genreRepo.listAllGenres()

    def getAvailableTypes(self) -> List[str]:
        return self.progTypeRepo.listTypes()

    def getProgramDetail(self, programId: int) -> Optional[dict]:
        row = self.progRepo.getProgramDetail(programId)
        if not row:
            return None
        episodes = self.episodeRepo.getEpisodesByProgram(programId)
        result = {
            "program_id":     row[0],
            "program_name":   row[1],
            "plot":           row[2],
            "type":           row[3],
            "genres":         row[4],         # STRING_AGG sonucu
            "number_of_part": row[5],
            "program_runtime":row[6],
            "release_year":   row[7],
            "file_path":      row[8],
            "avg_rating":     float(row[9]) if row[9] else 0.0,
            "watch_count":    int(row[10]) if row[10] else 0,
            "episodes":       episodes,
        }
        if self.current_user:
            uid = self.current_user[0]
            result["is_watched"]  = self.userProgRepo.hasWatched(uid, programId)
            result["user_rating"] = self.userProgRepo.getUserRating(uid, programId)
            result["is_favorite"] = self.favRepo.isFavorite(uid, programId)
            result["progress"]    = self.userProgRepo.getProgress(uid, programId)
        return result

    # ──────────────────────────────────────────────────────────────
    # İzleme
    # ──────────────────────────────────────────────────────────────

    def watchContent(self, programId: int, episodeNumber: int,
                     watchedDuration: float, isCompleted: bool) -> dict:
        if not self.current_user:
            return {"success": False, "message": "Oturum açılmamış."}
        uid = self.current_user[0]
        self.userProgRepo.addUserProgram(uid, programId)
        self.watchLogRepo.addWatchLog(uid, episodeNumber, programId, watchedDuration, isCompleted)
        self.userProgRepo.updateProgress(uid, programId, episodeNumber, watchedDuration)
        return {"success": True, "message": "İzleme kaydedildi."}

    def getWatchHistory(self):
        if not self.current_user:
            return []
        return self.watchLogRepo.getUserWatchLog(self.current_user[0])

    def getProgress(self, programId: int):
        if not self.current_user:
            return None
        return self.userProgRepo.getProgress(self.current_user[0], programId)

    # ──────────────────────────────────────────────────────────────
    # Puanlama
    # ──────────────────────────────────────────────────────────────

    def rateProgram(self, programId: int, rating: int) -> dict:
        if not self.current_user:
            return {"success": False, "message": "Oturum açılmamış."}
        if not (1 <= rating <= 10):
            return {"success": False, "message": "Puan 1 ile 10 arasında olmalıdır."}
        try:
            self.userProgRepo.rateProgram(self.current_user[0], programId, rating)
            return {"success": True, "message": "Puan verildi / güncellendi."}
        except ValueError as e:
            return {"success": False, "message": str(e)}

    # ──────────────────────────────────────────────────────────────
    # Favoriler
    # ──────────────────────────────────────────────────────────────

    def addFavorite(self, programId: int) -> dict:
        if not self.current_user:
            return {"success": False, "message": "Oturum açılmamış."}
        uid = self.current_user[0]
        if self.favRepo.isFavorite(uid, programId):
            return {"success": False, "message": "Bu içerik zaten favorilerinizde."}
        self.favRepo.addFavorite(uid, programId)
        return {"success": True, "message": "Favoriye eklendi."}

    def removeFavorite(self, programId: int) -> dict:
        if not self.current_user:
            return {"success": False, "message": "Oturum açılmamış."}
        self.favRepo.deleteFavorite(self.current_user[0], programId)
        return {"success": True, "message": "Favoriden çıkarıldı."}

    def getFavorites(self, genreFilter: str = ""):
        if not self.current_user:
            return []
        uid = self.current_user[0]
        if genreFilter:
            return self.favRepo.listFavoritesByGenre(uid, genreFilter)
        return self.favRepo.listFavorites(uid)

    # ──────────────────────────────────────────────────────────────
    # Öneri Sistemi
    # ──────────────────────────────────────────────────────────────

    def getRecommendations(self) -> List:
        """
        Öneri kriterleri (öncelik sırasıyla):
        1. Kullanıcının favori türleri (kayıt sırasında seçilen)
        2. Daha önce izlediği içeriklerin türleri
        3. Yüksek puan verdiği içeriklerin türleri
        4. Hiçbiri yoksa en çok izlenenler
        """
        if not self.current_user:
            return []
        uid = self.current_user[0]

        # İzlenmiş program id'leri — hariç tut
        history = self.userProgRepo.getWatchHistory(uid)

        # Zaten izlenmiş id'leri bulmak için ayrı sorgu
        cursor = self.db.getCursor()
        cursor.execute("SELECT program_id FROM user_programs WHERE user_id = ?", (uid,))
        watched_ids = [r[0] for r in cursor.fetchall()]

        # 1. Favori türler
        fav_genres = self.userGenreRepo.getUserGenres(uid)

        # 2. İzlenen içeriklerin türleri
        watched_genres = []
        if watched_ids:
            placeholders = ",".join(["?"] * len(watched_ids))
            cursor.execute(
                f"SELECT DISTINCT genre FROM program_genres WHERE program_id IN ({placeholders})",
                watched_ids
            )
            watched_genres = [r[0] for r in cursor.fetchall()]

        # 3. Yüksek puan (>=7) verilen içeriklerin türleri
        cursor.execute("""
            SELECT DISTINCT pg.genre
            FROM user_programs up
            INNER JOIN program_genres pg ON pg.program_id = up.program_id
            WHERE up.user_id = ? AND up.rating >= 7
        """, (uid,))
        rated_genres = [r[0] for r in cursor.fetchall()]

        # Birleştir, tekrarları kaldır, sırayı koru
        all_genres = list(dict.fromkeys(fav_genres + watched_genres + rated_genres))

        if not all_genres:
            return self.progRepo.listMostWatchedPrograms(6)

        return self.progRepo.getRecommendationsByGenres(all_genres, watched_ids, limit=2)

    # ──────────────────────────────────────────────────────────────
    # Yönetici — İçerik Yönetimi
    # ──────────────────────────────────────────────────────────────

    def adminAddProgram(self, programName: str, plot: str, numberOfPart: int,
                        programRuntime: float, releaseYear: date, ptype: str,
                        filePath: str, genres: List[str]) -> dict:
        if not self._is_admin():
            return {"success": False, "message": "Yetkiniz yok."}
        if not programName.strip():
            return {"success": False, "message": "Program adı boş olamaz."}
        try:
            prog_id = self.progRepo.addToProgram(
                programName, plot, numberOfPart, programRuntime, releaseYear, ptype, filePath
            )
            for g in genres:
                if not self.genreRepo.genreExists(g):
                    self.genreRepo.addGenre(g)
                self.progGenreRepo.addProgramGenre(g, prog_id)
            return {"success": True, "message": "Program eklendi.", "program_id": prog_id}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def adminUpdateProgram(self, programId: int, programName: str, plot: str,
                           numberOfPart: int, programRuntime: float,
                           releaseYear: date, ptype: str, genres: List[str]) -> dict:
        if not self._is_admin():
            return {"success": False, "message": "Yetkiniz yok."}
        try:
            self.progRepo.updateProgram(
                programId, programName, plot, numberOfPart, programRuntime, releaseYear, ptype
            )
            self.progGenreRepo.deleteProgramGenres(programId)
            for g in genres:
                if not self.genreRepo.genreExists(g):
                    self.genreRepo.addGenre(g)
                self.progGenreRepo.addProgramGenre(g, programId)
            return {"success": True, "message": "Program güncellendi."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def adminDeleteProgram(self, programId: int) -> dict:
        if not self._is_admin():
            return {"success": False, "message": "Yetkiniz yok."}
        try:
            self.progRepo.deleteProgram(programId)
            return {"success": True, "message": "Program silindi."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def adminAddEpisode(self, programId: int, episodeNumber: int,
                        title: str, duration: float, filePath: str) -> dict:
        if not self._is_admin():
            return {"success": False, "message": "Yetkiniz yok."}
        try:
            self.episodeRepo.addEpisodes(programId, episodeNumber, title, duration, filePath)
            return {"success": True, "message": "Bölüm eklendi."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    # ──────────────────────────────────────────────────────────────
    # Yönetici — Tür Yönetimi
    # ──────────────────────────────────────────────────────────────

    def adminAddGenre(self, genre: str) -> dict:
        if not self._is_admin():
            return {"success": False, "message": "Yetkiniz yok."}
        genre = genre.strip()
        if not genre:
            return {"success": False, "message": "Tür adı boş olamaz."}
        try:
            self.genreRepo.addGenre(genre)
            return {"success": True, "message": f"'{genre}' türü eklendi."}
        except ValueError as e:
            return {"success": False, "message": str(e)}

    def adminUpdateGenre(self, oldGenre: str, newGenre: str) -> dict:
        if not self._is_admin():
            return {"success": False, "message": "Yetkiniz yok."}
        newGenre = newGenre.strip()
        if not newGenre:
            return {"success": False, "message": "Tür adı boş olamaz."}
        try:
            self.genreRepo.updateGenre(oldGenre, newGenre)
            return {"success": True, "message": "Tür güncellendi."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def adminDeleteGenre(self, genre: str) -> dict:
        if not self._is_admin():
            return {"success": False, "message": "Yetkiniz yok."}
        try:
            self.genreRepo.deleteGenre(genre)
            return {"success": True, "message": f"'{genre}' türü silindi."}
        except ValueError as e:
            return {"success": False, "message": str(e)}

    # ──────────────────────────────────────────────────────────────
    # Yönetici — Kullanıcı Yönetimi
    # ──────────────────────────────────────────────────────────────

    def adminListUsers(self):
        if not self._is_admin():
            return []
        return self.userRepo.list_the_users()

    def adminGetUserDetail(self, userId: int) -> Optional[dict]:
        if not self._is_admin():
            return None
        user = self.userRepo.getUserById(userId)
        if not user:
            return None
        stats   = self.userRepo.getUserStats(userId)
        history = self.watchLogRepo.getUserWatchLog(userId)
        return {
            "user":           user,
            "total_duration": float(stats[0]) if stats[0] else 0.0,
            "watched_count":  int(stats[1]) if stats[1] else 0,
            "avg_rating":     float(stats[2]) if stats[2] else 0.0,
            "watch_history":  history,
        }
    def adminSetUserActive(self, userId: int, active: bool) -> dict:
        if not self._is_admin():
            return {"success": False, "message": "Yetkiniz yok."}
        try:
            self.userRepo.setUserActive(userId, active)
            return {"success": True, "message": "Kullanıcı durumu güncellendi."}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
        

    # ──────────────────────────────────────────────────────────────
    # Yönetici — Raporlar
    # ──────────────────────────────────────────────────────────────

    def adminGetReports(self) -> dict:
        if not self._is_admin():
            return {}
        stats = self.reportRepo.getSummaryStats()
        return {
            "top10_most_watched":  self.reportRepo.getTop10MostWatched(),
            "top10_highest_rated": self.reportRepo.getTop10HighestRated(),
            "most_watched_genres": self.reportRepo.getMostWatchedGenres(),
            "most_active_users":   self.reportRepo.getMostActiveUsers(),
            "last7days":           self.reportRepo.getLast7DaysContent(),
            "user_count":          stats[0],
            "total_watches":       stats[1],
            "total_ratings":       stats[2],
        }

    # ──────────────────────────────────────────────────────────────
    # Yardımcı
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _valid_email(mail: str) -> bool:
        return bool(re.match(r"^[\w\.\+\-]+@[\w\-]+\.\w{2,}$", mail))

    def _is_admin(self) -> bool:
        return self.current_user is not None and self.current_user[8] == "Y"
