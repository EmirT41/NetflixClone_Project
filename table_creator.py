from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database_connection import DatabaseConnection


class TableCreator:
    def __init__(self, db: "DatabaseConnection"):
        self.db = db

    def createTables(self):
        cursor = self.db.getCursor()
        cursor.execute("SELECT name FROM sys.tables")
        tablesInDB = [row[0] for row in cursor.fetchall()]

        tables = {
            "roles":          self.__createRoleTable,
            "program_types":  self.__createProgramTypeTable,
            "genres":         self.__createGenreTable,
            "users":          self.__createUserTable,
            "programs":       self.__createProgramTable,
            "episodes":       self.__createEpisodeTable,
            "program_genres": self.__createProgramGenreTable,
            "user_genres":    self.__createUserGenreTable,
            "user_programs":  self.__createUserProgramTable,
            "favorites":      self.__createFavoriteTable,
            "session_log":    self.__createSessionLogTable,
            "watch_log":      self.__createWatchLogTable,
        }

        for tableName, createFunction in tables.items():
            if tableName not in tablesInDB:
                createFunction()

        self.__createIndexes()
        self.db.commit()

    def __createIndexes(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_session_log_mail')
            BEGIN
                CREATE INDEX idx_session_log_mail ON session_log(entered_mail)
            END
        """)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_watch_log_user_id')
            BEGIN
                CREATE INDEX idx_watch_log_user_id ON watch_log(user_id)
            END
        """)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_user_programs_user_id')
            BEGIN
                CREATE INDEX idx_user_programs_user_id ON user_programs(user_id)
            END
        """)

    def __createRoleTable(self):
        cursor = self.db.getCursor()
        cursor.execute("CREATE TABLE roles (role CHAR(1), CONSTRAINT pk_roles PRIMARY KEY (role))")

    def __createProgramTypeTable(self):
        cursor = self.db.getCursor()
        cursor.execute("CREATE TABLE program_types (type NVARCHAR(50), CONSTRAINT pk_types PRIMARY KEY (type))")

    def __createGenreTable(self):
        cursor = self.db.getCursor()
        cursor.execute("CREATE TABLE genres (genre NVARCHAR(100), CONSTRAINT pk_genres PRIMARY KEY (genre))")

    def __createUserTable(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            CREATE TABLE users (
                user_id    INT IDENTITY(1,1),
                user_name  NVARCHAR(50)  NOT NULL,
                user_surname NVARCHAR(50) NOT NULL,
                password   NVARCHAR(100) NOT NULL,
                mail       NVARCHAR(100) NOT NULL,
                gender     CHAR(1)       NOT NULL,
                date_of_birth DATE       NOT NULL,
                country    NVARCHAR(50)  NOT NULL,
                user_role  CHAR(1),
                is_active  BIT DEFAULT 1,
                CONSTRAINT pk_users         PRIMARY KEY (user_id),
                CONSTRAINT ch_password      CHECK (LEN(LTRIM(RTRIM(password))) BETWEEN 6 AND 100),
                CONSTRAINT uc_users_mail    UNIQUE (mail),
                CONSTRAINT fk_user_roles    FOREIGN KEY (user_role) REFERENCES roles(role)
            )
        """)

    def __createProgramTable(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            CREATE TABLE programs (
                program_id      INT IDENTITY(1,1),
                program_name    NVARCHAR(100) NOT NULL,
                plot            NVARCHAR(MAX) NOT NULL,
                number_of_part  INT,
                program_runtime DECIMAL(5,2)  NOT NULL,
                release_year    DATE          NOT NULL,
                type            NVARCHAR(50),
                file_path       NVARCHAR(500),
                CONSTRAINT pk_program_id   PRIMARY KEY (program_id),
                CONSTRAINT uc_program_name UNIQUE (program_name),
                CONSTRAINT fk_program_types FOREIGN KEY (type) REFERENCES program_types(type)
            )
        """)

    def __createEpisodeTable(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            CREATE TABLE episodes (
                episode_number INT,
                title          NVARCHAR(200),
                program_id     INT,
                duration       DECIMAL(5,2),
                file_path      NVARCHAR(500),
                CONSTRAINT pk_episodes          PRIMARY KEY (program_id, episode_number),
                CONSTRAINT fk_episode_program   FOREIGN KEY (program_id) REFERENCES programs(program_id)
            )
        """)

    def __createProgramGenreTable(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            CREATE TABLE program_genres (
                genre      NVARCHAR(100),
                program_id INT,
                CONSTRAINT pk_program_genres       PRIMARY KEY (program_id, genre),
                CONSTRAINT fk_pg_program_id        FOREIGN KEY (program_id) REFERENCES programs(program_id),
                CONSTRAINT fk_pg_genre             FOREIGN KEY (genre)      REFERENCES genres(genre)
            )
        """)

    def __createUserGenreTable(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            CREATE TABLE user_genres (
                user_id INT,
                genre   NVARCHAR(100),
                CONSTRAINT pk_user_genres      PRIMARY KEY (user_id, genre),
                CONSTRAINT fk_ug_user_id       FOREIGN KEY (user_id) REFERENCES users(user_id),
                CONSTRAINT fk_ug_genre         FOREIGN KEY (genre)   REFERENCES genres(genre)
            )
        """)

    def __createUserProgramTable(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            CREATE TABLE user_programs (
                user_id       INT,
                program_id    INT,
                rating        INT,
                last_episode  INT,
                last_duration DECIMAL(5,2),
                last_watched  DATETIME,
                CONSTRAINT ch_up_rating          CHECK (rating BETWEEN 1 AND 10),
                CONSTRAINT pk_user_programs      PRIMARY KEY (user_id, program_id),
                CONSTRAINT fk_up_user_id         FOREIGN KEY (user_id)    REFERENCES users(user_id),
                CONSTRAINT fk_up_program_id      FOREIGN KEY (program_id) REFERENCES programs(program_id)
            )
        """)

    def __createFavoriteTable(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            CREATE TABLE favorites (
                user_id    INT,
                program_id INT,
                CONSTRAINT pk_favorites        PRIMARY KEY (user_id, program_id),
                CONSTRAINT fk_fav_user_id      FOREIGN KEY (user_id)    REFERENCES users(user_id),
                CONSTRAINT fk_fav_program_id   FOREIGN KEY (program_id) REFERENCES programs(program_id)
            )
        """)

    def __createSessionLogTable(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            CREATE TABLE session_log (
                session_log_id INT IDENTITY(1,1),
                entered_mail   NVARCHAR(100),
                login_time     DATETIME DEFAULT GETDATE(),
                is_success     BIT NOT NULL,
                CONSTRAINT pk_session_log PRIMARY KEY (session_log_id)
            )
        """)

    def __createWatchLogTable(self):
        cursor = self.db.getCursor()
        cursor.execute("""
            CREATE TABLE watch_log (
                watch_log_id     INT IDENTITY(1,1),
                user_id          INT,
                episode_number   INT NOT NULL,
                program_id       INT,
                watched_duration DECIMAL(5,2) DEFAULT 0,
                is_completed     BIT DEFAULT 0,
                log_time         DATETIME DEFAULT GETDATE(),
                CONSTRAINT pk_watch_log        PRIMARY KEY (watch_log_id),
                CONSTRAINT uq_watch_log        UNIQUE (user_id, program_id, episode_number),
                CONSTRAINT fk_wl_user_id       FOREIGN KEY (user_id)    REFERENCES users(user_id),
                CONSTRAINT fk_wl_program_id    FOREIGN KEY (program_id) REFERENCES programs(program_id),
                CONSTRAINT fk_wl_episode       FOREIGN KEY (program_id, episode_number)
                                               REFERENCES episodes(program_id, episode_number)
            )
        """)