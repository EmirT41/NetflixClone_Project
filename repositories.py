from typing import TYPE_CHECKING, Optional, List
from datetime import date

if TYPE_CHECKING:
    from database_connection import DatabaseConnection


# ──────────────────────────────────────────────────────────────────────────────
# UserRepository
# ──────────────────────────────────────────────────────────────────────────────

class UserRepository:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db

    def list_the_users(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT user_id, user_name, user_surname, mail,
                   gender, date_of_birth, country, user_role, is_active
            FROM users
            ORDER BY user_id
        """)
        return cursor.fetchall()

    def getUserById(self, user_id: int):
        cursor = self.db.getCursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone()

    def getUserByMail(self, mail: str):
        cursor = self.db.getCursor()
        cursor.execute("SELECT * FROM users WHERE mail = ?", (mail,))
        return cursor.fetchone()

    def mailExists(self, mail: str) -> bool:
        cursor = self.db.getCursor()
        cursor.execute("SELECT 1 FROM users WHERE mail = ?", (mail,))
        return cursor.fetchone() is not None

    def addUser(self, userName: str, userSurname: str, password: str, mail: str,
                gender: str, dateOfBirth: date, country: str, userRole: str) -> int:
        cursor = self.db.getCursor()
        cursor.execute("""
            INSERT INTO users
                (user_name, user_surname, password, mail, gender, date_of_birth, country, user_role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (userName, userSurname, password, mail, gender, dateOfBirth, country, userRole))
        self.db.commit()
        cursor.execute("SELECT user_id FROM users WHERE mail = ?", (mail,))
        return cursor.fetchone()[0]

    def updateUser(self, user_id: int, userName: str, userSurname: str,
                   mail: str, country: str, dateOfBirth: date):
        cursor = self.db.getCursor()
        cursor.execute("""
            UPDATE users
            SET user_name = ?, user_surname = ?, mail = ?, country = ?, date_of_birth = ?
            WHERE user_id = ?
        """, (userName, userSurname, mail, country, dateOfBirth, user_id))
        self.db.commit()

    def updatePassword(self, user_id: int, newPassword: str):
        cursor = self.db.getCursor()
        cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", (newPassword, user_id))
        self.db.commit()

    def setUserActive(self, user_id: int, is_active: bool):
        cursor = self.db.getCursor()
        cursor.execute("UPDATE users SET is_active = ? WHERE user_id = ?",
                       (1 if is_active else 0, user_id))
        self.db.commit()

    def getUserStats(self, user_id: int):
        """(total_duration, watched_count, avg_rating)"""
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT
                ISNULL((SELECT SUM(watched_duration) FROM watch_log WHERE user_id = ?), 0),
                ISNULL((SELECT COUNT(DISTINCT program_id) FROM user_programs WHERE user_id = ?), 0),
                ISNULL((SELECT AVG(CAST(rating AS FLOAT)) FROM user_programs
                        WHERE user_id = ? AND rating IS NOT NULL), 0)
        """, (user_id, user_id, user_id))
        return cursor.fetchone()

    def search_user_rating_time(self, user_id: int):
        cursor = self.db.getCursor()
        cursor.execute("SELECT SUM(rating) FROM user_programs WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()[0]
        return result if result is not None else 0


# ──────────────────────────────────────────────────────────────────────────────
# UserGenreRepository
# ──────────────────────────────────────────────────────────────────────────────

class UserGenreRepository:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db

    def addUserGenre(self, userId: int, genre: str):
        cursor = self.db.getCursor()
        cursor.execute("INSERT INTO user_genres (user_id, genre) VALUES (?, ?)", (userId, genre))
        self.db.commit()

    def getUserGenres(self, userId: int) -> List[str]:
        cursor = self.db.getCursor()
        cursor.execute("SELECT genre FROM user_genres WHERE user_id = ?", (userId,))
        return [row[0] for row in cursor.fetchall()]

    def deleteUserGenres(self, userId: int):
        cursor = self.db.getCursor()
        cursor.execute("DELETE FROM user_genres WHERE user_id = ?", (userId,))
        self.db.commit()


# ──────────────────────────────────────────────────────────────────────────────
# FavoriteRepository
# ──────────────────────────────────────────────────────────────────────────────

class FavoriteRepository:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db

    def addFavorite(self, userId: int, programId: int):
        cursor = self.db.getCursor()
        cursor.execute("INSERT INTO favorites (user_id, program_id) VALUES (?, ?)",
                       (userId, programId))
        self.db.commit()

    def isFavorite(self, userId: int, programId: int) -> bool:
        cursor = self.db.getCursor()
        cursor.execute("SELECT 1 FROM favorites WHERE user_id = ? AND program_id = ?",
                       (userId, programId))
        return cursor.fetchone() is not None

    def listFavorites(self, user_id: int):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT p.program_id, p.program_name, p.type,
                   ISNULL((SELECT STRING_AGG(pg.genre, ', ')
                           FROM program_genres pg WHERE pg.program_id = p.program_id), '') AS genres,
                   p.number_of_part, p.program_runtime, p.release_year,
                   ISNULL(AVG(CAST(up.rating AS FLOAT)), 0) AS avg_rating,
                   COUNT(DISTINCT wl.watch_log_id)          AS watch_count
            FROM favorites f
            INNER JOIN programs p ON p.program_id = f.program_id
            LEFT JOIN user_programs up ON up.program_id = p.program_id
            LEFT JOIN watch_log wl     ON wl.program_id = p.program_id AND wl.is_completed = 1
            WHERE f.user_id = ?
            GROUP BY p.program_id, p.program_name, p.type,
                     p.number_of_part, p.program_runtime, p.release_year
        """, (user_id,))
        return cursor.fetchall()

    def listFavoritesByGenre(self, user_id: int, genre: str):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT p.program_id, p.program_name, p.type,
                   ISNULL((SELECT STRING_AGG(pg2.genre, ', ')
                           FROM program_genres pg2 WHERE pg2.program_id = p.program_id), '') AS genres,
                   p.number_of_part, p.program_runtime, p.release_year,
                   ISNULL(AVG(CAST(up.rating AS FLOAT)), 0) AS avg_rating,
                   COUNT(DISTINCT wl.watch_log_id)          AS watch_count
            FROM favorites f
            INNER JOIN programs p ON p.program_id = f.program_id
            INNER JOIN program_genres pg ON pg.program_id = p.program_id AND pg.genre = ?
            LEFT JOIN user_programs up ON up.program_id = p.program_id
            LEFT JOIN watch_log wl     ON wl.program_id = p.program_id AND wl.is_completed = 1
            WHERE f.user_id = ?
            GROUP BY p.program_id, p.program_name, p.type,
                     p.number_of_part, p.program_runtime, p.release_year
        """, (genre, user_id))
        return cursor.fetchall()

    def deleteFavorite(self, userId: int, programId: int):
        cursor = self.db.getCursor()
        cursor.execute("DELETE FROM favorites WHERE user_id = ? AND program_id = ?",
                       (userId, programId))
        self.db.commit()


# ──────────────────────────────────────────────────────────────────────────────
# RoleRepository
# ──────────────────────────────────────────────────────────────────────────────

class RoleRepository:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db
        self.addRole()

    def addRole(self):
        cursor = self.db.getCursor()
        for role in ('Y', 'K'):
            cursor.execute("SELECT 1 FROM roles WHERE role = ?", (role,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO roles (role) VALUES (?)", (role,))
        self.db.commit()


# ──────────────────────────────────────────────────────────────────────────────
# UserProgramRepositories
# ──────────────────────────────────────────────────────────────────────────────

class UserProgramRepositories:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db

    def hasWatched(self, userId: int, programId: int) -> bool:
        cursor = self.db.getCursor()
        cursor.execute("SELECT 1 FROM user_programs WHERE user_id = ? AND program_id = ?",
                       (userId, programId))
        return cursor.fetchone() is not None

    def addUserProgram(self, userId: int, programId: int):
        if not self.hasWatched(userId, programId):
            cursor = self.db.getCursor()
            cursor.execute("INSERT INTO user_programs (user_id, program_id) VALUES (?, ?)",
                           (userId, programId))
            self.db.commit()

    def rateProgram(self, userId: int, programId: int, rating: int):
        """Sadece izlenmiş içeriğe puan verilebilir; tekrar verirse güncellenir."""
        if not self.hasWatched(userId, programId):
            raise ValueError("Bu içeriği henüz izlemediniz.")
        cursor = self.db.getCursor()
        cursor.execute("""
            UPDATE user_programs SET rating = ?
            WHERE user_id = ? AND program_id = ?
        """, (rating, userId, programId))
        self.db.commit()

    def getUserRating(self, userId: int, programId: int) -> Optional[int]:
        cursor = self.db.getCursor()
        cursor.execute("SELECT rating FROM user_programs WHERE user_id = ? AND program_id = ?",
                       (userId, programId))
        row = cursor.fetchone()
        return row[0] if row else None

    def updateProgress(self, userId: int, programId: int, lastEpisode: int, lastDuration: float):
        cursor = self.db.getCursor()
        cursor.execute("""
            UPDATE user_programs
            SET last_episode = ?, last_duration = ?, last_watched = GETDATE()
            WHERE user_id = ? AND program_id = ?
        """, (lastEpisode, lastDuration, userId, programId))
        self.db.commit()

    def getProgress(self, userId: int, programId: int):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT last_episode, last_duration
            FROM user_programs
            WHERE user_id = ? AND program_id = ?
        """, (userId, programId))
        return cursor.fetchone()

    def getWatchHistory(self, userId: int):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT p.program_name, p.type,
                   up.last_episode, up.last_duration, up.last_watched, up.rating
            FROM user_programs up
            INNER JOIN programs p ON up.program_id = p.program_id
            WHERE up.user_id = ?
            ORDER BY up.last_watched DESC
        """, (userId,))
        return cursor.fetchall()


# ──────────────────────────────────────────────────────────────────────────────
# ProgramRepository
# ──────────────────────────────────────────────────────────────────────────────

class ProgramRepository:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db

    # Yardımcı: tüm listeleme sorgularında aynı SELECT bloğu
    _BASE_SELECT = """
        SELECT p.program_id, p.program_name, p.type,
               ISNULL((SELECT STRING_AGG(pg.genre, ', ')
                       FROM program_genres pg WHERE pg.program_id = p.program_id), '') AS genres,
               p.number_of_part, p.program_runtime, p.release_year,
               ISNULL(AVG(CAST(up.rating AS FLOAT)), 0) AS avg_rating,
               COUNT(DISTINCT wl.watch_log_id)          AS watch_count
        FROM programs p
        LEFT JOIN user_programs up ON up.program_id = p.program_id
        LEFT JOIN watch_log wl     ON wl.program_id = p.program_id AND wl.is_completed = 1
    """
    _BASE_GROUP = """
        GROUP BY p.program_id, p.program_name, p.type,
                 p.number_of_part, p.program_runtime, p.release_year
    """

    def searchByProgramName(self, program_name: str):
        cursor = self.db.getCursor()
        cursor.execute(self._BASE_SELECT +
                       "WHERE p.program_name LIKE ? " + self._BASE_GROUP +
                       " ORDER BY p.program_name", (f"%{program_name}%",))
        return cursor.fetchall()

    def searchByProgramType(self, ptype: str):
        cursor = self.db.getCursor()
        cursor.execute(self._BASE_SELECT +
                       "WHERE p.type = ? " + self._BASE_GROUP, (ptype,))
        return cursor.fetchall()

    def searchByProgramGenre(self, genre: str):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT p.program_id, p.program_name, p.type,
                   ISNULL((SELECT STRING_AGG(pg2.genre, ', ')
                           FROM program_genres pg2 WHERE pg2.program_id = p.program_id), '') AS genres,
                   p.number_of_part, p.program_runtime, p.release_year,
                   ISNULL(AVG(CAST(up.rating AS FLOAT)), 0) AS avg_rating,
                   COUNT(DISTINCT wl.watch_log_id)          AS watch_count
            FROM programs p
            INNER JOIN program_genres pg ON pg.program_id = p.program_id AND pg.genre = ?
            LEFT JOIN user_programs up ON up.program_id = p.program_id
            LEFT JOIN watch_log wl     ON wl.program_id = p.program_id AND wl.is_completed = 1
            GROUP BY p.program_id, p.program_name, p.type,
                     p.number_of_part, p.program_runtime, p.release_year
        """, (genre,))
        return cursor.fetchall()

    def searchByReleaseYear(self, year: int):
        cursor = self.db.getCursor()
        cursor.execute(self._BASE_SELECT +
                       "WHERE YEAR(p.release_year) = ? " + self._BASE_GROUP, (year,))
        return cursor.fetchall()

    def searchByMinRating(self, minRating: float):
        cursor = self.db.getCursor()
        cursor.execute(self._BASE_SELECT + self._BASE_GROUP +
                       " HAVING ISNULL(AVG(CAST(up.rating AS FLOAT)), 0) >= ?", (minRating,))
        return cursor.fetchall()

    def listThePrograms(self):
        cursor = self.db.getCursor()
        cursor.execute(self._BASE_SELECT + self._BASE_GROUP + " ORDER BY p.program_id")
        return cursor.fetchall()

    def listTopRatedPrograms(self, limit: int = 10):
        cursor = self.db.getCursor()
        cursor.execute(f"SELECT TOP ({limit}) * FROM ({self._BASE_SELECT + self._BASE_GROUP}) t ORDER BY avg_rating DESC")
        return cursor.fetchall()

    def listMostWatchedPrograms(self, limit: int = 10):
        cursor = self.db.getCursor()
        cursor.execute(f"SELECT TOP ({limit}) * FROM ({self._BASE_SELECT + self._BASE_GROUP}) t ORDER BY watch_count DESC")
        return cursor.fetchall()

    def getProgramDetail(self, programId: int):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT p.program_id, p.program_name, p.plot, p.type,
                   ISNULL((SELECT STRING_AGG(pg.genre, ', ')
                           FROM program_genres pg WHERE pg.program_id = p.program_id), '') AS genres,
                   p.number_of_part, p.program_runtime, p.release_year, p.file_path,
                   ISNULL(AVG(CAST(up.rating AS FLOAT)), 0) AS avg_rating,
                   COUNT(DISTINCT wl.watch_log_id)          AS watch_count
            FROM programs p
            LEFT JOIN user_programs up ON up.program_id = p.program_id
            LEFT JOIN watch_log wl     ON wl.program_id = p.program_id AND wl.is_completed = 1
            WHERE p.program_id = ?
            GROUP BY p.program_id, p.program_name, p.plot, p.type,
                     p.number_of_part, p.program_runtime, p.release_year, p.file_path
        """, (programId,))
        return cursor.fetchone()

    def addToProgram(self, programName: str, plot: str, numberOfPart: int,
                     programRuntime: float, releaseYear: date, ptype: str, filePath: str) -> int:
        cursor = self.db.getCursor()
        cursor.execute("""
            INSERT INTO programs
                (program_name, plot, number_of_part, program_runtime, release_year, type, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (programName, plot, numberOfPart, programRuntime, releaseYear, ptype, filePath))
        self.db.commit()
        cursor.execute("SELECT program_id FROM programs WHERE program_name = ?", (programName,))
        return cursor.fetchone()[0]

    def updateProgram(self, programId: int, programName: str, plot: str,
                      numberOfPart: int, programRuntime: float,
                      releaseYear: date, ptype: str):
        cursor = self.db.getCursor()
        cursor.execute("""
            UPDATE programs
            SET program_name = ?, plot = ?, number_of_part = ?,
                program_runtime = ?, release_year = ?, type = ?
            WHERE program_id = ?
        """, (programName, plot, numberOfPart, programRuntime, releaseYear, ptype, programId))
        self.db.commit()

    def deleteProgram(self, programId: int):
        cursor = self.db.getCursor()
        cursor.execute("DELETE FROM favorites      WHERE program_id = ?", (programId,))
        cursor.execute("DELETE FROM watch_log       WHERE program_id = ?", (programId,))
        cursor.execute("DELETE FROM user_programs   WHERE program_id = ?", (programId,))
        cursor.execute("DELETE FROM program_genres  WHERE program_id = ?", (programId,))
        cursor.execute("DELETE FROM episodes        WHERE program_id = ?", (programId,))
        cursor.execute("DELETE FROM programs         WHERE program_id = ?", (programId,))
        self.db.commit()

    def getRecommendationsByGenres(self, genres: List[str],
                                   excludeIds: List[int], limit: int = 2):
        results = []
        seen_ids = set(excludeIds)
        cursor = self.db.getCursor()
        for genre in genres:
            excluded = list(seen_ids)
            excl_sql = ("AND p.program_id NOT IN (%s)" %
                        ",".join(["?"] * len(excluded))) if excluded else ""
            cursor.execute(f"""
                SELECT TOP (?) p.program_id, p.program_name, p.type,
                       ISNULL((SELECT STRING_AGG(pg2.genre, ', ')
                               FROM program_genres pg2 WHERE pg2.program_id = p.program_id), '') AS genres,
                       p.number_of_part, p.program_runtime, p.release_year,
                       ISNULL(AVG(CAST(up.rating AS FLOAT)), 0) AS avg_rating,
                       COUNT(DISTINCT wl.watch_log_id) AS watch_count
                FROM programs p
                INNER JOIN program_genres pg ON pg.program_id = p.program_id AND pg.genre = ?
                LEFT JOIN user_programs up ON up.program_id = p.program_id
                LEFT JOIN watch_log wl     ON wl.program_id = p.program_id AND wl.is_completed = 1
                {excl_sql}
                GROUP BY p.program_id, p.program_name, p.type,
                         p.number_of_part, p.program_runtime, p.release_year
                ORDER BY avg_rating DESC
            """, [limit, genre] + excluded)
            rows = cursor.fetchall()
            for r in rows:
                seen_ids.add(r[0])
                results.append(r)
        return results


# ──────────────────────────────────────────────────────────────────────────────
# GenreRepository  (bağımsız tür tablosu)
# ──────────────────────────────────────────────────────────────────────────────

class GenreRepository:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db

    def listAllGenres(self) -> List[str]:
        cursor = self.db.getCursor()
        cursor.execute("SELECT genre FROM genres ORDER BY genre")
        return [row[0] for row in cursor.fetchall()]

    def addGenre(self, genre: str):
        cursor = self.db.getCursor()
        cursor.execute("SELECT 1 FROM genres WHERE genre = ?", (genre,))
        if cursor.fetchone():
            raise ValueError(f"'{genre}' türü zaten mevcut.")
        cursor.execute("INSERT INTO genres (genre) VALUES (?)", (genre,))
        self.db.commit()

    def updateGenre(self, oldGenre: str, newGenre: str):
        cursor = self.db.getCursor()
        # Bağlı kayıtları da güncelle (CASCADE olmadığı için manuel)
        cursor.execute("UPDATE program_genres SET genre = ? WHERE genre = ?", (newGenre, oldGenre))
        cursor.execute("UPDATE user_genres    SET genre = ? WHERE genre = ?", (newGenre, oldGenre))
        cursor.execute("UPDATE genres         SET genre = ? WHERE genre = ?", (newGenre, oldGenre))
        self.db.commit()

    def deleteGenre(self, genre: str):
        cursor = self.db.getCursor()
        cursor.execute("SELECT 1 FROM program_genres WHERE genre = ?", (genre,))
        if cursor.fetchone():
            raise ValueError(f"'{genre}' türüne bağlı içerik var, silinemez.")
        cursor.execute("DELETE FROM user_genres WHERE genre = ?", (genre,))
        cursor.execute("DELETE FROM genres      WHERE genre = ?", (genre,))
        self.db.commit()

    def genreExists(self, genre: str) -> bool:
        cursor = self.db.getCursor()
        cursor.execute("SELECT 1 FROM genres WHERE genre = ?", (genre,))
        return cursor.fetchone() is not None


# ──────────────────────────────────────────────────────────────────────────────
# ProgramGenreRepository
# ──────────────────────────────────────────────────────────────────────────────

class ProgramGenreRepository:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db

    def addProgramGenre(self, genre: str, programId: int):
        cursor = self.db.getCursor()
        cursor.execute("INSERT INTO program_genres (genre, program_id) VALUES (?, ?)",
                       (genre, programId))
        self.db.commit()

    def deleteProgramGenres(self, programId: int):
        cursor = self.db.getCursor()
        cursor.execute("DELETE FROM program_genres WHERE program_id = ?", (programId,))
        self.db.commit()

    def getByProgram(self, programId: int) -> List[str]:
        cursor = self.db.getCursor()
        cursor.execute("SELECT genre FROM program_genres WHERE program_id = ?", (programId,))
        return [row[0] for row in cursor.fetchall()]


# ──────────────────────────────────────────────────────────────────────────────
# ProgramTypeRepository
# ──────────────────────────────────────────────────────────────────────────────

class ProgramTypeRepository:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db

    def addProgramType(self, ptype: str):
        cursor = self.db.getCursor()
        cursor.execute("SELECT 1 FROM program_types WHERE type = ?", (ptype,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO program_types (type) VALUES (?)", (ptype,))
            self.db.commit()

    def listTypes(self) -> List[str]:
        cursor = self.db.getCursor()
        cursor.execute("SELECT type FROM program_types ORDER BY type")
        return [row[0] for row in cursor.fetchall()]


# ──────────────────────────────────────────────────────────────────────────────
# SessionLogRepository
# ──────────────────────────────────────────────────────────────────────────────

class SessionLogRepository:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db

    def addSessionLog(self, enteredMail: str, isSuccess: bool):
        cursor = self.db.getCursor()
        cursor.execute("INSERT INTO session_log (entered_mail, is_success) VALUES (?, ?)",
                       (enteredMail, isSuccess))
        self.db.commit()

    def getUserSessionLog(self, user_id: int):
        cursor = self.db.getCursor()
        cursor.execute("SELECT * FROM session_log WHERE entered_mail = "
                       "(SELECT mail FROM users WHERE user_id = ?)", (user_id,))
        return cursor.fetchall()


# ──────────────────────────────────────────────────────────────────────────────
# WatchLogRepository
# ──────────────────────────────────────────────────────────────────────────────

class WatchLogRepository:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db

    def addWatchLog(self, userId: int, episodeNumber: int, programId: int,
                    watchedDuration: float, isCompleted: bool):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT 1 FROM watch_log
            WHERE user_id = ? AND program_id = ? AND episode_number = ?
        """, (userId, programId, episodeNumber))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE watch_log
                SET watched_duration = ?, is_completed = ?, log_time = GETDATE()
                WHERE user_id = ? AND program_id = ? AND episode_number = ?
            """, (watchedDuration, isCompleted, userId, programId, episodeNumber))
        else:
            cursor.execute("""
                INSERT INTO watch_log
                    (user_id, episode_number, program_id, watched_duration, is_completed)
                VALUES (?, ?, ?, ?, ?)
            """, (userId, episodeNumber, programId, watchedDuration, isCompleted))
        self.db.commit()

    def getUserWatchLog(self, user_id: int):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT p.program_name, wl.episode_number, wl.watched_duration,
                   wl.is_completed, wl.log_time,
                   ISNULL(up.rating, 0) AS rating
            FROM watch_log wl
            INNER JOIN programs p ON wl.program_id = p.program_id
            LEFT JOIN user_programs up
                   ON up.user_id = wl.user_id AND up.program_id = wl.program_id
            WHERE wl.user_id = ?
            ORDER BY wl.log_time DESC
        """, (user_id,))
        return cursor.fetchall()


# ──────────────────────────────────────────────────────────────────────────────
# EpisodeRepository
# ──────────────────────────────────────────────────────────────────────────────

class EpisodeRepository:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db

    def getFilePath(self, programId: int, episodeNumber: int):
        cursor = self.db.getCursor()
        cursor.execute("SELECT file_path FROM episodes WHERE program_id = ? AND episode_number = ?",
                       (programId, episodeNumber))
        return cursor.fetchone()

    def getEpisodesByProgram(self, programId: int):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT episode_number, title, duration
            FROM episodes WHERE program_id = ? ORDER BY episode_number
        """, (programId,))
        return cursor.fetchall()

    def addEpisodes(self, programId: int, episodeNumber: int,
                    title: str, duration: float, filePath: str):
        cursor = self.db.getCursor()
        cursor.execute("""
            INSERT INTO episodes (program_id, episode_number, title, duration, file_path)
            VALUES (?, ?, ?, ?, ?)
        """, (programId, episodeNumber, title, duration, filePath))
        self.db.commit()


# ──────────────────────────────────────────────────────────────────────────────
# ReportRepository
# ──────────────────────────────────────────────────────────────────────────────

class ReportRepository:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db

    def getTop10MostWatched(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT TOP 10 p.program_name,
                   COUNT(DISTINCT wl.watch_log_id) AS watch_count
            FROM watch_log wl
            INNER JOIN programs p ON p.program_id = wl.program_id
            WHERE wl.is_completed = 1
            GROUP BY p.program_id, p.program_name
            ORDER BY watch_count DESC
        """)
        return cursor.fetchall()

    def getTop10HighestRated(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT TOP 10 p.program_name,
                   ISNULL(AVG(CAST(up.rating AS FLOAT)), 0) AS avg_rating
            FROM programs p
            LEFT JOIN user_programs up ON up.program_id = p.program_id
            GROUP BY p.program_id, p.program_name
            HAVING COUNT(up.rating) > 0
            ORDER BY avg_rating DESC
        """)
        return cursor.fetchall()

    def getMostWatchedGenres(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT pg.genre, COUNT(DISTINCT wl.watch_log_id) AS watch_count
            FROM watch_log wl
            INNER JOIN program_genres pg ON pg.program_id = wl.program_id
            WHERE wl.is_completed = 1
            GROUP BY pg.genre
            ORDER BY watch_count DESC
        """)
        return cursor.fetchall()

    def getMostActiveUsers(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT TOP 10
                   u.user_name + ' ' + u.user_surname AS full_name,
                   COUNT(DISTINCT wl.watch_log_id)    AS total_watches
            FROM watch_log wl
            INNER JOIN users u ON u.user_id = wl.user_id
            GROUP BY u.user_id, u.user_name, u.user_surname
            ORDER BY total_watches DESC
        """)
        return cursor.fetchall()

    def getLast7DaysContent(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT p.program_name,
                   COUNT(DISTINCT wl.watch_log_id) AS watch_count
            FROM watch_log wl
            INNER JOIN programs p ON p.program_id = wl.program_id
            WHERE wl.log_time >= DATEADD(DAY, -7, GETDATE())
            GROUP BY p.program_id, p.program_name
            ORDER BY watch_count DESC
        """)
        return cursor.fetchall()

    def getSummaryStats(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM users)                         AS user_count,
                (SELECT COUNT(*) FROM watch_log WHERE is_completed=1) AS total_watches,
                (SELECT COUNT(*) FROM user_programs WHERE rating IS NOT NULL) AS total_ratings
        """)
        return cursor.fetchone()
