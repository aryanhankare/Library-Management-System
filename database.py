import mysql.connector
from config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def create_tables():
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )
    cursor = conn.cursor()

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`")
    cursor.execute(f"USE `{DB_CONFIG['database']}`")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `member` (
            `member_id` VARCHAR(20) NOT NULL,
            `member_name` VARCHAR(100) NOT NULL,
            `gender` INT(1) NOT NULL DEFAULT 0,
            `birth_date` DATE DEFAULT NULL,
            `member_type_id` INT(6) DEFAULT NULL,
            `member_address` VARCHAR(255) DEFAULT NULL,
            `member_email` VARCHAR(100) DEFAULT NULL,
            `member_phone` VARCHAR(50) DEFAULT NULL,
            `inst_name` VARCHAR(100) DEFAULT NULL,
            `register_date` DATE DEFAULT NULL,
            `expire_date` DATE NOT NULL,
            `input_date` DATE DEFAULT NULL,
            `last_update` DATE DEFAULT NULL,
            PRIMARY KEY (`member_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `biblio` (
            `biblio_id` INT(11) NOT NULL AUTO_INCREMENT,
            `title` TEXT NOT NULL,
            `isbn_issn` VARCHAR(20) DEFAULT NULL,
            `publisher_id` INT(11) DEFAULT NULL,
            `publish_year` VARCHAR(20) DEFAULT NULL,
            `input_date` DATETIME DEFAULT NULL,
            `last_update` DATETIME DEFAULT NULL,
            PRIMARY KEY (`biblio_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `item` (
            `item_id` INT(11) NOT NULL AUTO_INCREMENT,
            `biblio_id` INT(11) DEFAULT NULL,
            `item_code` VARCHAR(20) DEFAULT NULL,
            `call_number` VARCHAR(50) DEFAULT NULL,
            `coll_type_id` INT(3) DEFAULT NULL,
            `input_date` DATETIME NOT NULL,
            `last_update` DATETIME DEFAULT NULL,
            PRIMARY KEY (`item_id`),
            UNIQUE KEY `item_code` (`item_code`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `loan` (
            `loan_id` INT(11) NOT NULL AUTO_INCREMENT,
            `item_code` VARCHAR(20) DEFAULT NULL,
            `member_id` VARCHAR(20) DEFAULT NULL,
            `loan_date` DATE NOT NULL,
            `due_date` DATE NOT NULL,
            `renewed` INT(11) NOT NULL DEFAULT 0,
            `loan_rules_id` INT(11) NOT NULL DEFAULT 0,
            `is_lent` INT(11) NOT NULL DEFAULT 0,
            `is_return` INT(11) NOT NULL DEFAULT 0,
            `return_date` DATE DEFAULT NULL,
            PRIMARY KEY (`loan_id`),
            KEY `item_code` (`item_code`),
            KEY `member_id` (`member_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `reminder_log` (
            `log_id` INT(11) NOT NULL AUTO_INCREMENT,
            `member_id` VARCHAR(20) NOT NULL,
            `item_code` VARCHAR(20) NOT NULL,
            `due_date` DATE NOT NULL,
            `sent_at` DATETIME NOT NULL,
            `channel` VARCHAR(20) NOT NULL DEFAULT 'email',
            PRIMARY KEY (`log_id`),
            UNIQUE KEY `unique_reminder` (`member_id`, `item_code`, `due_date`, `channel`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("All tables created successfully.")


if __name__ == "__main__":
    create_tables()