import os
import sys
import time
import asyncio
import sqlite3
import random
import logging
import threading
from datetime import datetime, timezone, timedelta

import aiohttp

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter, MessageEntityType
from pyrogram.errors import UserNotParticipant, RPCError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("ModerationBot")

API_ID = int(os.environ.get("API_ID", "33235659"))
API_HASH = os.environ.get("API_HASH", "6b546489b46e68555f915a8f8022e757")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8105530067:AAFYa7Sv4kPA7lCBPbJQb290j07dK1-SXbA")
WHISPER_BOT_TOKEN = "8918822588:AAEtuIdlnkh2IcRTugToJt2gMz-bLQ4YS8Y"
_whisper_bot_username = "r8bbbot"
OWNER_ID = int(os.environ.get("OWNER_ID", "930185623"))

START_TIME = time.time()

AI_KEYS = [
    "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",
]




ROLE_LEVELS = {
    "member": 0, "member_perfect": 0, "vip": 1, "admin": 2, "manager": 3, "creator": 4,
    "supervisor": 4, "supervisor_perfect": 4, "creator_basic": 5, "developer": 6,
    "developer_secondary": 7, "developer_basic": 8, "asaasi": 8,
    "owner_basic": 8, "owner": 9, "bot_owner": 10, "supreme": 10
}
ROLE_ARABIC = {
    "member": "عضو", "vip": "مميز", "admin": "ادمن", "manager": "مدير",
    "creator": "منشئ", "creator_basic": "منشئ اساسي", "developer": "مطور",
    "developer_secondary": "مطور ثانوي", "developer_basic": "مطور اساسي",
    "owner": "مالك الكروب", "bot_owner": "مالك البوت", "supreme": "المطور الاساسي للبوت",
    "asaasi": "اساسي", "owner_basic": "مالك اساسي",
    "supervisor": "مشرف", "supervisor_perfect": "مشرف مثالي",
    "member_perfect": "عضو مثالي"
}
WELCOME_BOT_PHRASES = [
    "اقرا اسمي",
    "شكو خير",
    "اسمي روز",
    "؟؟",
    "ها يمعود",
    "خيير",
    "تفضل",
    "شتريد"
]
GAMES_DATA = {
    "sentences": [
        "اللهم اني اسالك ان تبسط لساني بشكر النعمة منك",
        "العلم يرفع بيوتا لا عماد لها والجهل يهدم بيت العز والشرف",
        "من جد وجد ومن زرع حصد ومن سار على الدرب وصل",
        "لا تحسبن العلم ينفع وحده ما لم يتوج ربه بخلاق",
        "لسان الفتى نصف ونصف فؤاده فلم يبق إلا صورة اللحم والدم",
        "إنما الأمم الأخلاق ما بقيت فإن هم ذهبت أخلاقهم ذهبوا"
    ],
    "questions": [
        "أشياء تغيرت نظرتك لها مؤخراً؟", "شيء كل ما تذكرته تبتسم؟",
        "صفة في شخصيتك تتمنى التخلص منها؟", "ما هي العادة التي تود التخلي عنها؟",
        "من هو الشخص الذي تعتبره قدوة لك في الحياة؟",
        "تجربة مررت بها وعلمتك درساً لن تنساه؟"
    ],
    "flags": [
        {"emoji": "🇮🇶", "ans": ["العراق", "عراق"]},
        {"emoji": "🇸🇦", "ans": ["السعودية", "السعوديه", "المملكة العربية السعودية"]},
        {"emoji": "🇪🇬", "ans": ["مصر", "جمهورية مصر العربية"]},
        {"emoji": "🇵🇸", "ans": ["فلسطين", "فلسطين الحرة"]},
        {"emoji": "🇸🇾", "ans": ["سوريا", "سوريه"]},
        {"emoji": "🇯🇴", "ans": ["الأردن", "الاردن"]},
        {"emoji": "🇱🇧", "ans": ["لبنان"]},
        {"emoji": "🇾🇪", "ans": ["اليمن"]},
        {"emoji": "🇦🇪", "ans": ["الإمارات", "الامارات", "الامارات العربية المتحدة"]},
        {"emoji": "🇶🇦", "ans": ["قطر"]},
        {"emoji": "🇰🇼", "ans": ["الكويت"]},
        {"emoji": "🇴🇲", "ans": ["عمان", "سلطنة عمان"]},
        {"emoji": "🇧🇭", "ans": ["البحرين"]},
        {"emoji": "🇩🇿", "ans": ["الجزائر", "الجزائر"]},
        {"emoji": "🇲🇦", "ans": ["المغرب"]},
        {"emoji": "🇹🇳", "ans": ["تونس"]},
        {"emoji": "🇱🇾", "ans": ["ليبيا"]},
        {"emoji": "🇸🇩", "ans": ["السودان"]},
        {"emoji": "🇸🇴", "ans": ["الصومال"]},
        {"emoji": "🇲🇷", "ans": ["موريتانيا", "موريتاني"]},
        {"emoji": "🇹🇷", "ans": ["تركيا", "تركيه"]},
        {"emoji": "🇮🇷", "ans": ["إيران", "ايران"]},
        {"emoji": "🇺🇸", "ans": ["أمريكا", "امريكا", "الولايات المتحدة"]},
        {"emoji": "🇬🇧", "ans": ["بريطانيا", "المملكة المتحدة"]},
        {"emoji": "🇫🇷", "ans": ["فرنسا", "فرنسه"]},
        {"emoji": "🇩🇪", "ans": ["ألمانيا", "المانيا"]},
        {"emoji": "🇮🇹", "ans": ["إيطاليا", "ايطاليا"]},
        {"emoji": "🇪🇸", "ans": ["إسبانيا", "اسبانيا"]},
        {"emoji": "🇯🇵", "ans": ["اليابان"]},
        {"emoji": "🇨🇳", "ans": ["الصين"]},
        {"emoji": "🇷🇺", "ans": ["روسيا"]}
    ],
    "scramble_words": [
        "مدرسة", "تفاح", "برمجيات", "أمان", "بغداد", "العراق",
        "كمبيوتر", "هاتف", "صديق", "عائلة", "طاولة", "كرسي",
        "شمس", "قمر", "نجوم", "كتاب", "قلم", "دفتر", "مفتاح"
    ],
    "disassemble": [
        {"word": "انتهى", "decomp": "ا ن ت ه ى"},
        {"word": "مدرسة", "decomp": "م د ر س ة"},
        {"word": "أمان", "decomp": "أ م ا ن"},
        {"word": "الوطن", "decomp": "ا ل و ط ن"},
        {"word": "بغداد", "decomp": "ب غ د ا د"}
    ],
    "capitals": [
        {"country": "العراق", "capital": "بغداد"},
        {"country": "السعودية", "capital": "الرياض"},
        {"country": "مصر", "capital": "القاهرة"},
        {"country": "سوريا", "capital": "دمشق"},
        {"country": "فلسطين", "capital": "القدس"},
        {"country": "الأردن", "capital": "عمان"},
        {"country": "اليمن", "capital": "صنعاء"},
        {"country": "لبنان", "capital": "بيروت"}
    ],
    "riddles": [
        {"q": "ما هو الشيء الذي يكتب ولا يقرأ؟", "a": ["القلم", "قلم"]},
        {"q": "ما هو الشيء الذي كلما كثر لدينا غلا وكلما قل رخص؟", "a": ["العقل", "عقل"]},
        {"q": "ما هو الشيء الذي يتحدث جميع اللغات؟", "a": ["الصدى", "صدى"]},
        {"q": "ما هو الشيء الذي يحترق لكي يضيء للآخرين؟", "a": ["الشمعة", "شمعة", "الشمع"]},
        {"q": "ابن أمك وابن أبيك، وليس بأختك ولا بأخيك، فمن يكون؟", "a": ["أنت", "انت", "انا", "أنا"]},
        {"q": "ما هو الشيء الذي تراه في الليل ثلاث مرات وفي النهار مرة واحدة؟", "a": ["حرف اللام", "اللام"]}
    ]
}
POETRY_DATA = [
    "وما كنت ممن يدخل العشق قلبه \n ولكن من يبصر جفونك يعشقِ",
    "عيناك نازلتا القلوب فكلها \n إما جريح أو قتيل الهوى",
    "أحبك حباً لو يفيض يسيره \n على الخلق مات الخلق من شدة الحب",
    "قالت جننت بمن تهوى فقلت لها \n العشق أعظم مما بالمجانين",
    "أراك فتحلو لدي الحياة \n ويملأ نفسي صباح الأمل",
    "يا ليت من نتمنى عند خلوتنا \n يرى جميل الذي نلقاه من وجدِ",
    "لو كان قلبي معي ما اخترت غيركم \n ولا رضيت بسواكم في الهوى بدلا",
    "وإني لأهوى النوم في غير حينه \n لعل لقاء في المنام يكون",
    "أحبك كالبدر الذي فاض نوره \n على الأرض حتى أصبح الكون زاهيا",
    "أنت النعيم لقلبي والعذاب له \n فما أمرّك في قلبي وأحلاكِ",
    "لقد دب الهوى لك في فؤادي \n دبيب دم الحياة إلى عروقي",
    "خَليلَيّ غُضّا عن مَلامي وأَقْصِرا \n فما في فؤادي مَوْضِعٌ لِلعَواذِلِ",
    "أقلّي اللوم عاذل والعتّابا \n وقولي إن أصبت لقد أصابا",
    "أغركِ مني أن حبك قاتلي \n وأنكِ مهما تأمري القلب يفعلِ",
    "فوالله لا أختار غيركِ في الهوى \n ولو ملئت أرض الحجاز حِسانا",
    "سأبقى أحبك حتى تفارق \n روحي جسدي وتصعد للسماء"
]
LOCK_COLUMNS = {
    "الفويسات": "lock_voice", "الفيديو": "lock_video", "الصور": "lock_photo",
    "الملصقات": "lock_sticker", "الدخول": "lock_join", "الملفات": "lock_file",
    "المتحركات": "lock_gif", "الدردشه": "lock_chat", "الهشتاق": "lock_mention",
    "الروابط": "lock_link", "الكلايش": "lock_long_text", "التكرار": "lock_spam",
    "التوجيه": "lock_forward",     "تعديل الميديا": "lock_media_edit",
    "السب": "lock_swear",
    "التشويش": "lock_spoiler"
}
SWEAR_WORDS = [
    "حيوان", "حيوانات", "حيوانة", "حيوانه",
    "عار", "عارات", "قحبة", "قحبه", "كحبة", "كحبه", "كحاب", "كحبجية", "كحبجيه",
    "زبالة", "زباله", "قندرة", "قندره",
    "كس", "عير", "كس اختك", "كسي", "كسج", "كسمي", "كسختي", "كسختك", "كساختك",
    "كسك", "كسمك", "كس امك", "كسامك",
    "طيز", "طيزي", "طيزك", "طيزج",
    "ديس", "ديوس", "عنابة", "عنابه",
    "نغل", "نغولة", "نغوله", "نغلة", "نغله", "نغلات",
    "تناحه", "تناحة", "خصية", "خصيه", "خصيان", "خصاوي",
    "العير", "الجبة", "الجبه", "الچبة", "الچبه",
    "مطيزة", "مطيزه", "ستيان",
    "نيج", "انيجك", "انيجج", "انيجكم", "انيجها", "كسخواتكم", "نيجني", "نيجوني",
    "عيري", "مكوم", "فاجر", "عاهر", "زاني", "فاجرة", "عاهرة", "زانية", "زانيه",
    "طوبز", "طوبزي", "عرضك", "دحسه", "دحسة", "ادحس", "ادحسه", "ادحسة",
    "نجت", "دودة", "دودكي", "نكاح"
]
ROLE_MAPPING = {
    "مميز": "vip", "ادمن": "admin", "مدير": "manager",
    "منشئ اساسي": "creator_basic", "منشئ أساسي": "creator_basic",
    "منشئ": "creator", "مطور ثانوي": "developer_secondary",
    "مطور اساسي": "developer_basic", "مطور أساسي": "developer_basic",
    "مطور": "developer",     "مالك": "owner",
    "مالك البوت": "bot_owner",
    "اساسي": "asaasi", "أساسي": "asaasi",
    "مالك اساسي": "owner_basic", "مالك أساسي": "owner_basic",
    "مشرف": "supervisor", "مشرف مثالي": "supervisor_perfect",
    "عضو مثالي": "member_perfect"
}

DB_PATH = "bot_database.db"


class DB:
    _conn: sqlite3.Connection | None = None
    _lock = threading.Lock()

    @classmethod
    def _get_conn(cls) -> sqlite3.Connection:
        if cls._conn is None:
            cls._conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
            cls._conn.execute("PRAGMA busy_timeout=30000")
            cls._conn.execute("PRAGMA journal_mode=WAL")
        return cls._conn

    @classmethod
    def init_db(cls):
        conn = cls._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY, is_active INTEGER DEFAULT 0,
                welcome_msg TEXT, rules TEXT, lock_edit INTEGER DEFAULT 0,
                lock_voice INTEGER DEFAULT 0, lock_video INTEGER DEFAULT 0,
                lock_photo INTEGER DEFAULT 0, lock_sticker INTEGER DEFAULT 0,
                lock_join INTEGER DEFAULT 0, lock_file INTEGER DEFAULT 0,
                lock_gif INTEGER DEFAULT 0, lock_chat INTEGER DEFAULT 0,
                lock_mention INTEGER DEFAULT 0, lock_link INTEGER DEFAULT 0,
                lock_long_text INTEGER DEFAULT 0, lock_spam INTEGER DEFAULT 0,
                lock_forward INTEGER DEFAULT 0, welcome_active INTEGER DEFAULT 1,
                replies_active INTEGER DEFAULT 1, id_active INTEGER DEFAULT 1,
                link_active INTEGER DEFAULT 1, warnings_active INTEGER DEFAULT 1,
                id_style INTEGER DEFAULT 1, lock_premium_sticker INTEGER DEFAULT 0,
                tag_all_active INTEGER DEFAULT 1, tag_random_active INTEGER DEFAULT 1,
                lock_notifications INTEGER DEFAULT 0, id_photo_active INTEGER DEFAULT 1,
                lock_audio INTEGER DEFAULT 0,
                lock_media_edit INTEGER DEFAULT 0,
                games_active INTEGER DEFAULT 1,
                bio_active INTEGER DEFAULT 1,
                delete_active INTEGER DEFAULT 1,
                auto_clean_active INTEGER DEFAULT 0,
                auto_clean_count INTEGER DEFAULT 20,
                aliases_active INTEGER DEFAULT 0,
                marry_active INTEGER DEFAULT 1,
                ask_active INTEGER DEFAULT 1,
                warn_active INTEGER DEFAULT 1,
                kickme_active INTEGER DEFAULT 1,
                unrankme_active INTEGER DEFAULT 1,
                ban_active INTEGER DEFAULT 1,
                kick_active INTEGER DEFAULT 1,
                promote_active INTEGER DEFAULT 1,
                demote_active INTEGER DEFAULT 1,
                reveal_active INTEGER DEFAULT 1,
                lock_swear INTEGER DEFAULT 0,
                lock_spoiler INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS ranks (
                chat_id INTEGER, user_id INTEGER, role TEXT,
                PRIMARY KEY (chat_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS messages_count (
                chat_id INTEGER, user_id INTEGER, count INTEGER DEFAULT 0,
                PRIMARY KEY (chat_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS user_points (
                chat_id INTEGER, user_id INTEGER, points INTEGER DEFAULT 0,
                PRIMARY KEY (chat_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS muted_users (
                chat_id INTEGER, user_id INTEGER,
                PRIMARY KEY (chat_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS custom_ranks (
                chat_id INTEGER, user_id INTEGER, rank_title TEXT,
                PRIMARY KEY (chat_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS banned_words (
                chat_id INTEGER, word TEXT,
                PRIMARY KEY (chat_id, word)
            );
            CREATE TABLE IF NOT EXISTS nicknames (
                chat_id INTEGER, user_id INTEGER, nickname TEXT,
                PRIMARY KEY (chat_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS aliases (
                chat_id INTEGER, original_cmd TEXT, custom_cmd TEXT,
                PRIMARY KEY (chat_id, custom_cmd)
            );
            CREATE TABLE IF NOT EXISTS bot_owners (
                user_id INTEGER PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS warnings (
                chat_id INTEGER, user_id INTEGER, count INTEGER DEFAULT 0,
                PRIMARY KEY (chat_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS media_history (
                chat_id INTEGER, message_id INTEGER,
                PRIMARY KEY (chat_id, message_id)
            );
            CREATE TABLE IF NOT EXISTS edited_history (
                chat_id INTEGER, message_id INTEGER,
                PRIMARY KEY (chat_id, message_id)
            );
            CREATE TABLE IF NOT EXISTS marriages (
                chat_id INTEGER, user_id INTEGER, partner_id INTEGER,
                PRIMARY KEY (chat_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS custom_replies (
                chat_id INTEGER, keyword TEXT, reply_type TEXT, reply_data TEXT,
                PRIMARY KEY (chat_id, keyword)
            );
            CREATE TABLE IF NOT EXISTS user_messages (
                chat_id INTEGER, user_id INTEGER, message_id INTEGER,
                PRIMARY KEY (chat_id, message_id)
            );
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS owner_female (
                chat_id INTEGER PRIMARY KEY,
                user_id INTEGER
            );
            CREATE TABLE IF NOT EXISTS banned_user_messages (
                chat_id INTEGER,
                user_id INTEGER,
                message_text TEXT,
                PRIMARY KEY (chat_id, user_id, message_text)
            );
            CREATE TABLE IF NOT EXISTS bot_users (
                user_id INTEGER PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS whispers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                target_name TEXT DEFAULT '',
                sender_name TEXT DEFAULT '',
                message_text TEXT DEFAULT '',
                status TEXT DEFAULT 'pending'
            );
        """)
        conn.commit()
        existing = {r[1] for r in conn.execute("PRAGMA table_info(groups)").fetchall()}
        all_cols = {
            "lock_audio": 0, "lock_media_edit": 0, "games_active": 1, "bio_active": 1,
            "delete_active": 1, "auto_clean_active": 0, "auto_clean_count": 20, "aliases_active": 0,
            "marry_active": 1, "ask_active": 1, "warn_active": 1, "kickme_active": 1,
            "unrankme_active": 1, "ban_active": 1, "kick_active": 1, "promote_active": 1,
            "demote_active": 1, "reveal_active": 1, "lock_swear": 0, "trend_active": 1,
            "whisper_active": 1, "lock_spoiler": 0
        }
        for col, default in all_cols.items():
            if col not in existing:
                try:
                    conn.execute(f"ALTER TABLE groups ADD COLUMN {col} INTEGER DEFAULT {default}")
                    conn.commit()
                    log.info("Added column %s to groups table", col)
                except Exception as e:
                    log.warning("Failed to add column %s: %s", col, e)

    @classmethod
    async def execute(cls, query: str, params: tuple = (), fetchall=False, fetchone=False, commit=False):
        with cls._lock:
            try:
                conn = cls._get_conn()
                cur = conn.execute(query, params)
                if commit:
                    conn.commit()
                if fetchall:
                    return cur.fetchall()
                if fetchone:
                    return cur.fetchone()
                return cur
            except Exception as e:
                log.error("DB error: %s | query: %s", e, query[:80])
                raise


DB.init_db()

conv_states: dict = {}
spam_cache: dict = {}
active_games: dict = {}
active_xo_games: dict = {}
emoji_games: dict = {}


def estimate_creation_year(uid: int) -> str:
    if uid < 0: return "حساب آلي أو قناة"
    if uid < 50000000: return "2013-2014"
    if uid < 150000000: return "2015"
    if uid < 300000000: return "2016"
    if uid < 500000000: return "2017"
    if uid < 800000000: return "2018"
    if uid < 1100000000: return "2019"
    if uid < 1600000000: return "2020"
    if uid < 2100000000: return "2021"
    if uid < 5000000000: return "2022-2023"
    return "2024-2025"


async def check_force_sub(client: Client, uid: int) -> bool:
    if uid == OWNER_ID:
        return True
    row_en = await DB.execute("SELECT value FROM bot_settings WHERE key='force_sub_enabled'", fetchone=True)
    if not row_en or row_en[0] != "1":
        return True
    row_link = await DB.execute("SELECT value FROM bot_settings WHERE key='force_sub_link'", fetchone=True)
    if not row_link or not row_link[0]:
        return True
    ch = row_link[0].rstrip("/").split("/")[-1]
    if ch.startswith("@"):
        ch = ch[1:]
    if not ch:
        return True
    try:
        m = await client.get_chat_member(ch, uid)
        return m.status not in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED)
    except UserNotParticipant:
        return False
    except Exception as e:
        log.warning("Force sub check for %d in %s: %s", uid, ch, e)
        return True


async def is_bot_cmd(chat_id: int, text: str) -> bool:
    if not text:
        return False
    t = text.strip()
    if t == "بوت":
        return True
    commands = [
        "تفعيل", "تعطيل", "الاوامر", "طرد", "كتم", "الغاء الكتم", "تقييد",
        "الغاء التقييد", "الغاء الحظر", "رفع القيود", "تحذير", "طرد بوت",
        "منع", "الغاء منع", "اضف رد", "أضف رد", "حذف الرد",
        "حذف رد", "حذف قائمة الردود", "قفل", "فتح",
        "السورس", "الرابط", "رتبتي", "الترحيب", "القوانين", "المطور",
        "لقبني", "لقبي", "الساعه", "الساعة", "التاريخ", "المجموعة", "المجموعه",
        "ايدي", "صلاحياتي", "صلاحياته", "تعيين الترحيب", "تعيين القوانين",
        "اضافة امر", "مسح امر", "كشف", "تغيير الايدي",
        "جمل", "كت", "اعلام", "أعلام", "ترتيب", "تفكيك", "عواصم",
        "الالالعاب", "الالعاب", "الألعاب",
        "لغز", "اسئلني", "محيبس", "ايموجي",
        "تاك", "زوجني", "طلقني", "مسح القوانين", "المالك", "ترتيب الاوامر", "تعطيل ترتيب الاوامر",
        "قفل الملصق المميز", "فتح الملصق المميز", "اكس او",
        "تاك عام", "@all", "تفعيل تاك عام", "تعطيل تاك عام", "تفعيل تاك", "تعطيل تاك",
        "قفل التفليش", "فتح التفليش", "قفل تعديل الميديا", "فتح تعديل الميديا",
        "حزورة", "نقاطي", "رفع ادمن", "تنزيل ادمن", "قفل الاشعارات", "فتح الاشعارات",
        "تعطيل الايدي", "تفعيل الايدي", "تعطيل الايدي بالصورة", "تفعيل الايدي بالصورة", "نداء", "عرض الردود",
        "مسح رسائلي", "رسائلي", "شعر", "تثبيت",
        "انذار", "انذاراته", "مسح انذاراته",
        "حظر", "الغاء حظر",
        "كشف القيود",
        "منعه", "الغاء منعه", "مسح ممنوعاته",
        "طرد المحذوفين",
        "مسح المالكين", "مسح المنشئين", "مسح المدراء", "مسح الادمنيه",
        "قائمه المنع", "قائمة المنع", "مسح الاوامر المضافه",
        "مسح جميع الممنوعات", "امسح",
        "مسح الترحيب", "مسح الرابط",
        "مسح وسائط البوت",
        "روز غادري",
        "تفعيل الالعاب", "تعطيل الالعاب",
        "تفعيل البايو", "تعطيل البايو",
        "تفعيل امسح", "تعطيل امسح",
        "تفعيل التنظيف التلقائي", "تعطيل التنظيف التلقائي",
        "تنظيف تلقائي",
        "تفعيل زوجني", "تعطيل زوجني",
        "تفعيل كت", "تعطيل كت",
        "الردود",
        "تفعيل الردود", "تعطيل الردود",
        "تفعيل الانذار", "تعطيل الانذار",
        "تفعيل التحذير", "تعطيل التحذير",
        "اطردني", "تفعيل اطردني", "تعطيل اطردني",
        "نزلني", "تفعيل نزلني", "تعطيل نزلني",
        "تفعيل الحظر", "تعطيل الحظر",
        "تفعيل الطرد", "تعطيل الطرد",
        "تفعيل الرفع", "تعطيل الرفع",
        "تفعيل التنزيل", "تعطيل التنزيل",
        "تفعيل الكشف", "تعطيل الكشف",
        "ترند", "تصفير الترند",
        "تفعيل ترند", "تعطيل ترند",
        "تفعيل همسه", "تعطيل همسه",
        "رفع اساسي", "تنزيل اساسي", "رفع مالك اساسي", "تنزيل مالك اساسي",
        "رفع مشرف", "تنزيل مشرف", "رفع مشرف مثالي", "تنزيل مشرف مثالي",
        "رفع عضو مثالي", "تنزيل عضو مثالي",
        "مسح الكل", "مسح المطرودين",
        "عدد الرتب", "الاساسي", "المالكين الاساسين", "المالكين",
        "المشرفين", "المنشئين", "الادمنيه", "المحظورين", "المقيدين",
        "المكتومين", "اعدادات القروب", "معلوماتي", "معلومات المجموعه",
        "المشرف المثالي", "العضو المثالي", "اضف المالكه", "المالكه",
        "ضع صوره", "ضع اسم", "وضع وصف"
    ]
    if any(t == cmd or t.startswith(cmd + " ") for cmd in commands):
        return True
    if await DB.execute("SELECT 1 FROM custom_replies WHERE chat_id=? AND keyword=?", (chat_id, t), fetchone=True):
        return True
    if await DB.execute("SELECT 1 FROM aliases WHERE chat_id=? AND custom_cmd=?", (chat_id, t), fetchone=True):
        return True
    return False


async def get_role(chat_id: int, uid: int, client: Client) -> tuple[str, int]:
    if uid == OWNER_ID:
        return "supreme", 10
    if chat_id == uid:
        return "member", 0
    try:
        m = await client.get_chat_member(chat_id, uid)
        if m.status == ChatMemberStatus.OWNER:
            await DB.execute("INSERT INTO ranks (chat_id,user_id,role) VALUES (?,?,?) ON CONFLICT DO UPDATE SET role=?",
                             (chat_id, uid, "owner", "owner"), commit=True)
            return "owner", 9
    except Exception:
        pass
    row = await DB.execute("SELECT role FROM ranks WHERE chat_id=? AND user_id=?", (chat_id, uid), fetchone=True)
    if row:
        return row[0], ROLE_LEVELS.get(row[0], 0)
    try:
        m = await client.get_chat_member(chat_id, uid)
        if m.status == ChatMemberStatus.ADMINISTRATOR:
            return "manager", 3
    except Exception:
        pass
    return "member", 0


async def extract_target(message) -> any:
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    if not message.text:
        return None
    for part in message.text.split()[1:]:
        p = part.strip()
        if p.startswith("@"):
            try:
                return await message._client.get_users(p)
            except Exception:
                pass
        elif p.isdigit():
            try:
                return await message._client.get_users(int(p))
            except Exception:
                pass
    return None


async def change_rank(message, target_id: int, target_role: str | None, promotion: bool = True):
    sender = message.from_user.id
    chat = message.chat.id
    cl = message._client
    _, sl = await get_role(chat, sender, cl)
    _, tl = await get_role(chat, target_id, cl)
    if sl <= tl and sl < 10:
        await message.reply_text("❌ لا تملك صلاحية التحكم بمستخدم يملك رتبة مساوية أو أعلى منك.")
        return
    try:
        tu = await cl.get_users(target_id)
    except Exception:
        await message.reply_text("❌ لم يتم العثور على المستخدم المستهدف.")
        return
    if promotion:
        trl = ROLE_LEVELS.get(target_role or "", 0)
        if trl >= sl and sl < 10:
            await message.reply_text(f"❌ لا يمكنك الترقية إلى رتبة مساوية أو أعلى من رتبتك الحالية.")
            return
        await DB.execute("INSERT INTO ranks (chat_id,user_id,role) VALUES (?,?,?) ON CONFLICT DO UPDATE SET role=?",
                         (chat, target_id, target_role, target_role), commit=True)
        role_ar = ROLE_ARABIC.get(target_role or '', '')
        await message.reply_text(f"• تم رفعه {role_ar}\n• المستخدم ↤︎ {tu.mention}")
    else:
        await DB.execute("DELETE FROM ranks WHERE chat_id=? AND user_id=?", (chat, target_id), commit=True)
        role_ar = ROLE_ARABIC.get(target_role, '') if target_role else 'الرتب'
        await message.reply_text(f"• تم تنزيله {role_ar}\n• المستخدم ↤︎ {tu.mention}")


def xo_winner(board):
    wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] != " ":
            return board[a]
    return None


def xo_grid(game, cid):
    b = game["board"]
    kb = [[InlineKeyboardButton("➖" if b[i+j] == " " else b[i+j], callback_data=f"xo_{cid}_{i+j}") for j in range(3)] for i in range(0,9,3)]
    kb.append([InlineKeyboardButton("🏳️ إنهاء اللعبة", callback_data=f"xoc_{cid}")])
    return InlineKeyboardMarkup(kb)


def xo_grid_end(game):
    b = game["board"]
    kb = [[InlineKeyboardButton(b[i+j] if b[i+j] != " " else "➖", callback_data="xox") for j in range(3)] for i in range(0,9,3)]
    return InlineKeyboardMarkup(kb)


async def stats_ui(client, uid):
    ag = (await DB.execute("SELECT COUNT(*) FROM groups WHERE is_active=1", fetchone=True) or [0])[0]
    tm = (await DB.execute("SELECT SUM(count) FROM messages_count", fetchone=True) or [0])[0] or 0
    cr = (await DB.execute("SELECT COUNT(*) FROM custom_ranks", fetchone=True) or [0])[0]
    mu = (await DB.execute("SELECT COUNT(*) FROM muted_users", fetchone=True) or [0])[0]
    al = (await DB.execute("SELECT COUNT(*) FROM aliases", fetchone=True) or [0])[0]
    nn = (await DB.execute("SELECT COUNT(*) FROM nicknames", fetchone=True) or [0])[0]
    up = int(time.time() - START_TIME)
    h, r = divmod(up, 3600)
    m, s = divmod(r, 60)
    msg = (
        f"📊 **لوحة إحصائيات البوت الفنية الخاصة بالمالك المبرمج:**\n\n"
        f"⏱️ مدة تشغيل النظام: `{h} ساعة، {m} دقيقة`\n"
        f"👥 المجموعات النشطة والمحمية: `{ag}`\n"
        f"💬 إجمالي الرسائل المحللة: `{tm}`\n"
        f"🏷️ الرتب المخصصة الممنوحة: `{cr}`\n"
        f"🔇 إجمالي المكتومين: `{mu}`\n"
        f"🔄 اختصارات الأوامر المفعلة: `{al}`\n"
        f"👤 الألقاب المحفوظة للأعضاء: `{nn}`\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📋 **روابط الانتقال والانضمام للمجموعات المضافة:**"
    )
    rows = await DB.execute("SELECT chat_id FROM groups", fetchall=True) or []
    btns = [
        [InlineKeyboardButton("📢 الاشتراك الاجباري", callback_data=f"fs_{uid}")],
        [InlineKeyboardButton("📡 الاذاعة", callback_data=f"bc_{uid}")]
    ]
    for r in rows:
        gid = r[0]
        try:
            ci = await client.get_chat(gid)
            lnk = ci.invite_link or (f"https://t.me/{ci.username}" if ci.username else None)
            btns.append([
                InlineKeyboardButton(f"👥 {ci.title}", url=lnk) if lnk else InlineKeyboardButton(f"🚫 {gid}", callback_data=f"nolink_{gid}"),
                InlineKeyboardButton("❌ إخراج البوت", callback_data=f"leave_{gid}")
            ])
        except Exception:
            btns.append([
                InlineKeyboardButton(f"🚫 {gid}", callback_data=f"nolink_{gid}"),
                InlineKeyboardButton("❌ إخراج البوت", callback_data=f"leave_{gid}")
            ])
    return msg, InlineKeyboardMarkup(btns) if btns else None


async def force_sub_ui(uid: int):
    fs_en = await DB.execute("SELECT value FROM bot_settings WHERE key='force_sub_enabled'", fetchone=True)
    enabled = fs_en and fs_en[0] == "1"
    status_text = "✅ مفعل" if enabled else "❌ معطل"
    row_link = await DB.execute("SELECT value FROM bot_settings WHERE key='force_sub_link'", fetchone=True)
    link = row_link[0] if row_link and row_link[0] else "غير محدد"
    row_msg = await DB.execute("SELECT value FROM bot_settings WHERE key='force_sub_msg'", fetchone=True)
    has_msg = bool(row_msg and row_msg[0])
    msg = f"📢 **إعدادات الاشتراك الإجباري**\n\n"
    msg += f"الحالة: {status_text}\n📎 رابط القناة: `{link}`\n📝 رسالة الاشتراك: {'✅ موجودة' if has_msg else '❌ غير محددة'}"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ مفعل" if enabled else "❌ معطل", callback_data=f"fs_toggle_{uid}")],
        [InlineKeyboardButton("📝 رسالة الاشتراك", callback_data=f"fs_show_msg_{uid}"),
         InlineKeyboardButton("✏️ تغيير", callback_data=f"fs_set_msg_{uid}"),
         InlineKeyboardButton("🗑️", callback_data=f"fs_del_msg_{uid}")],
        [InlineKeyboardButton("➕ إضافة رابط قناة", callback_data=f"fs_set_link_{uid}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data=f"fs_back_{uid}")]
    ])
    return msg, kb


async def broadcast_ui(uid: int):
    msg = "📡 **اهلا بك في قسم الاذاعة**\n\nاختر نوع الاذاعة المناسب من الاسفل"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 اذاعة خاص الى مستخدمين البوت", callback_data=f"bc_users_{uid}")],
        [InlineKeyboardButton("👥 اذاعة الى مجموعات البوت", callback_data=f"bc_groups_{uid}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data=f"bc_back_{uid}")]
    ])
    return msg, kb


async def add_points(cid: int, uid: int, pts: int = 5):
    await DB.execute("INSERT INTO user_points (chat_id,user_id,points) VALUES (?,?,?) ON CONFLICT DO UPDATE SET points=points+?",
                     (cid, uid, pts, pts), commit=True)


def _mh_kb(cid: int, game: dict):
    rows = []
    for i in range(6):
        text = f"🫴 ({i+1})" if i in game.get("opened", set()) else f"👊 ({i+1})"
        rows.append([InlineKeyboardButton(text, callback_data=f"mh_{cid}_{i}")])
    return InlineKeyboardMarkup(rows)


def _emj_kb(cid: int, game: dict):
    rows = []
    for i in range(4):
        p = game["players"][i]
        if p:
            rows.append([InlineKeyboardButton(f"👤 {p['name']}", callback_data="emj_noop")])
        else:
            rows.append([InlineKeyboardButton(f"⬜ تسجيل لاعب {i+1}", callback_data=f"emjr_{cid}_{i}")])
    if game["phase"] == "registering":
        rows.append([InlineKeyboardButton("❌ إلغاء اللعبة", callback_data=f"emjc_{cid}")])
    return InlineKeyboardMarkup(rows)


FALLBACK_WORDS = ["التيتانيك", "ميسي", "أبو ظبي", "شيرلوك هولمز", "الأهرامات", "نابليون", "فورت نايت", "سبونج بوب", "القط الأسود", "المريخ", "البرازيل", "القاهرة", "توم وجيري", "علاء الدين", "هارى بوتر", "سوبر مان", "بات مان", "الأسد الملك", "فروزن", "أفاتار"]


app = Client("moderation_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)
whisper_app = Client("whisper_bot", api_id=API_ID, api_hash=API_HASH, bot_token=WHISPER_BOT_TOKEN, in_memory=True)

# ── Whisper bot handlers ──────────────────────────────────────────
_pending_whispers: dict[int, int] = {}  # user_id -> whisper_id

@whisper_app.on_message(filters.private & filters.command("start"))
async def whisper_start(client, message):
    uid = message.from_user.id
    txt = message.text or ""
    parts = txt.split()
    if len(parts) < 2 or not parts[1].startswith("whisper_"):
        await message.reply_text("👋 أهلاً بك في بوت الهمسة!\nاستخدم الأمر من المجموعة.")
        return
    try:
        _, wid, chat_id, sender_id, target_id = parts[1].split("_")
        wid, chat_id, sender_id, target_id = int(wid), int(chat_id), int(sender_id), int(target_id)
    except (ValueError, IndexError):
        await message.reply_text("❌ رابط غير صالح.")
        return
    if uid != sender_id:
        await message.reply_text("❌ هذه الهمسة ليست لك.")
        return
    _pending_whispers[uid] = wid
    await message.reply_text("- حسناً, ارسل الهمسة الان")

@whisper_app.on_message(filters.private & filters.text)
async def whisper_text(client, message):
    uid = message.from_user.id
    wid = _pending_whispers.pop(uid, None)
    if wid is None:
        return
    txt = message.text.strip()
    await DB.execute("UPDATE whispers SET message_text=?, status='collected' WHERE id=?", (txt, wid), commit=True)
    row = await DB.execute("SELECT chat_id, sender_id, target_id, target_name, sender_name FROM whispers WHERE id=?", (wid,), fetchone=True)
    if not row:
        await message.reply_text("❌ حدث خطأ.")
        return
    chat_id, sender_id, target_id, target_name, sender_name = row
    await message.reply_text("- تم ارسالها بنجاح بالمجموعة")
    try:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("• عرض الهمسه•", callback_data=f"ws_{wid}")]
        ])
        coro = app.send_message(
            chat_id,
            f"• عزيزي [{target_name}](tg://user?id={target_id})، لديك همسة سرية من المستخدم [{sender_name}](tg://user?id={sender_id}) •",
            reply_markup=kb
        )
        asyncio.run_coroutine_threadsafe(coro, app.loop)
    except Exception as e:
        log.warning(f"Whisper delivery failed: {e}")

# ── End whisper bot handlers ──────────────────────────────────────


@app.on_message(filters.private & filters.text)
async def private_handler(client, message):
    uid = message.from_user.id
    txt = message.text
    await DB.execute("INSERT OR IGNORE INTO bot_users (user_id) VALUES (?)", (uid,), commit=True)
    if uid == OWNER_ID:
        await DB.execute("INSERT OR IGNORE INTO bot_owners (user_id) VALUES (?)", (uid,), commit=True)
    if txt in ("/start", "بدأ", "بدء"):
        if uid == OWNER_ID:
            msg, mk = await stats_ui(client, uid)
            await message.reply_text(msg, reply_markup=mk)
            return
        me = await client.get_me()
        wt = "مرحبا في بوت الحماية\n\nقم بأضافة البوت الى مجموعتك وقم برفعه مشرف ثم ارسل (تفعيل) ليعمل البوت معك"
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ أضف البوت إلى مجموعتك", url=f"https://t.me/{me.username}?startgroup=true")]
        ])
        if me.photo:
            try:
                await message.reply_photo(me.photo.big_file_id, caption=wt, reply_markup=btns)
                return
            except Exception:
                pass
        await message.reply_text(wt, reply_markup=btns)
        return

    # --- Private chat conversation states (owner only) ---
    if uid == OWNER_ID and uid in conv_states:
        st = conv_states[uid]
        if st["user_id"] == uid and txt:
            if txt == "الغاء":
                conv_states.pop(uid, None)
                await message.reply_text("❌ تم الإلغاء.")
                return
            s = st["state"]
            if s == "waiting_force_sub_msg":
                await DB.execute("INSERT OR REPLACE INTO bot_settings (key,value) VALUES ('force_sub_msg',?)", (txt,), commit=True)
                conv_states.pop(uid, None)
                log.info("Force sub message set by %d", uid)
                msg, mk = await force_sub_ui(uid)
                await message.reply_text("✅ تم حفظ رسالة الاشتراك.", reply_markup=mk)
                return
            if s == "waiting_force_sub_link":
                await DB.execute("INSERT OR REPLACE INTO bot_settings (key,value) VALUES ('force_sub_link',?)", (txt,), commit=True)
                conv_states.pop(uid, None)
                log.info("Force sub link set by %d: %s", uid, txt)
                msg, mk = await force_sub_ui(uid)
                await message.reply_text("✅ تم حفظ رابط قناة الاشتراك الإجباري.", reply_markup=mk)
                return
            if s in ("waiting_broadcast_users", "waiting_broadcast_groups"):
                conv_states.pop(uid, None)
                target = "المستخدمين" if s == "waiting_broadcast_users" else "المجموعات"
                sm = await message.reply_text(f"📡 جاري الاذاعة الى {target}...")
                success = 0
                failed = 0
                if s == "waiting_broadcast_users":
                    rows = await DB.execute("SELECT user_id FROM bot_users", fetchall=True) or []
                    user_ids = [r[0] for r in rows if r[0] != uid]
                    for user_id in user_ids:
                        try:
                            await client.send_message(user_id, txt)
                            success += 1
                            await asyncio.sleep(0.05)
                        except Exception:
                            failed += 1
                else:
                    rows = await DB.execute("SELECT chat_id FROM groups", fetchall=True) or []
                    for (gid,) in rows:
                        try:
                            await client.send_message(gid, txt)
                            success += 1
                            await asyncio.sleep(0.05)
                        except Exception:
                            failed += 1
                try:
                    await sm.edit_text(f"✅ تم الانتهاء من الاذاعة.\n• نجح: {success}\n• فشل: {failed}")
                except Exception:
                    pass
                msg, mk = await broadcast_ui(uid)
                await message.reply_text("📡 عدنا الى قائمة الاذاعة.", reply_markup=mk)
                return


@app.on_message(filters.new_chat_members & filters.group)
async def welcome_handler(client, message):
    cid = message.chat.id
    await DB.execute("INSERT INTO groups (chat_id,is_active) VALUES (?,0) ON CONFLICT DO NOTHING", (cid,), commit=True)
    try:
        me = await client.get_me()
        if any(m.id == me.id for m in message.new_chat_members):
            async for m in client.get_chat_members(cid, filter=ChatMembersFilter.ADMINISTRATORS):
                if m.status == ChatMemberStatus.OWNER:
                    await DB.execute("INSERT INTO ranks (chat_id,user_id,role) VALUES (?,?,?) ON CONFLICT DO UPDATE SET role=?",
                                     (cid, m.user.id, "owner", "owner"), commit=True)
                    break
    except Exception as e:
        log.error("Welcome owner detect: %s", e)
    lj = await DB.execute("SELECT lock_join FROM groups WHERE chat_id=?", (cid,), fetchone=True)
    if lj and lj[0]:
        try:
            await message.delete()
        except Exception:
            pass
        return
    wa = await DB.execute("SELECT welcome_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
    if wa and not wa[0]:
        return
    row = await DB.execute("SELECT welcome_msg FROM groups WHERE chat_id=?", (cid,), fetchone=True)
    w = row[0] if row and row[0] else "👋 أهلاً بك في المجموعة! يسعدنا انضمامك إلينا."
    try:
        await message.reply_text(w, reply_to_message_id=message.id)
    except Exception:
        pass


COMMAND_1 = """
-اهلا بك في قائمة اوامر الادمنيه:
_
اوامر الرفع والتنزيل:
رفع - تنزيل اساسي
رفع - تنزيل مالك اساسي
رفع - تنزيل مالك
رفع - تنزيل مشرف
رفع - تنزيل منشئ
رفع - تنزيل مدير
رفع - تنزيل ادمن
رفع - تنزيل مميز
رفع - تنزيل مشرف مثالي
رفع - تنزيل عضو مثالي
مسح الكل
تنزيل الكل - بالرد على الشخص
━━━━━━━━━━━━━━━━
- اوامر المسح:
مسح المالكين الاساسين
مسح المالكين
مسح المنشئين
مسح المدراء
مسح الادمنيه
مسح المميزين
مسح المحظورين
مسح المطرودين
مسح المقيدين
مسح المكتومين
مسح قائمة المنع
مسح الردود
مسح الاوامر المضافه
مسح + عدد
امسح
مسح جميع الممنوعات
مسح بالرد
مسح انذاراته - بالرد
مسح الترحيب
مسح الرابط
مسح القوانين
مسح وسائط البوت
━━━━━━━━━━━━━━━━
- اوامر الكتم والحظر:
كتم
الغاء الكتم
مسح المكتومين
رفع القيود
حظر
الغاء حظر
مسح المحظورين
طرد
رفع القيود
تقييد + الوقت
تقييد
الغاء التقييد
مسح المقيدين
━━━━━━━━━━━━━━━━
- اوامر الانذارات:
انذار
انذاراته
مسح انذاراته
━━━━━━━━━━━━━━━━
- اوامر الكشف والمنع:
معلومات المجموعه
كشف
كشف القيود
منع بالرد
الغاء منع
طرد المحذوفين
منعه
الغاء منعه
مسح ممنوعاته
━━━━━━━━━━━━━━━━
"""


COMMAND_2 = """
- اهـلًا بـك فـي
- قائمة اوامر الاعدادات :
━━━━━━━━━━━━━━━━
- اوامر رؤية الاعدادات :

• عدد الرتب
• الاساسي
• المالكين الاساسين
• المالكين
• المشرفين
• المنشئين
• الادمنيه
• المدراء
• المميزين
• المحظورين
• المقيدين
• المكتومين
• اعدادات القروب
- القوانين
- الترحيب
- الرابط
• معلوماتي
• المشرف المثالي
• العضو المثالي
━━━━━━━━━━━━━━━━
- اوامر وضع الاعدادات :

اضف المالكه
ضع صوره
ضع اسم + الاسم
وضع وصف
"""

COMMAND_3 = """
-اهلا بك في قائمة اوامر القفل والحماية:
_
اوامر الاقفال:
قفل / فتح الفويسات
قفل / فتح الفيديو
قفل / فتح الصور
قفل / فتح الملصقات
قفل / فتح الملصق المميز
قفل / فتح الدخول
قفل / فتح الملفات
قفل / فتح المتحركات
قفل / فتح الدردشه
قفل / فتح الهشتاق
قفل / فتح الروابط
قفل / فتح الكلايش
قفل / فتح التكرار
قفل / فتح التوجيه
قفل / فتح الاشعارات
قفل / فتح الكل
قفل / فتح التفليش
قفل / فتح تعديل الميديا
━━━━━━━━━━━━━━━━
اوامر الردود:
اضف رد / أضف رد
حذف رد / مسح رد
عرض الردود
━━━━━━━━━━━━━━━━
اوامر اخرى:
السورس
بوت
"""

COMMAND_4 = """
-اهلا بك في قائمة اوامر التفعيل والتثبيت والمنشن:
_
اوامر التفعيل والتعطيل:
تفعيل / تعطيل البوت
تفعيل / تعطيل الترحيب
تفعيل / تعطيل الايدي
تفعيل / تعطيل الايدي بالصورة
تفعيل / تعطيل الرابط
تفعيل / تعطيل تاك عام
تفعيل / تعطيل تاك
تفعيل / تعطيل الالعاب
تفعيل / تعطيل البايو
تفعيل / تعطيل امسح
تنظيف تلقائي + العدد
تفعيل / تعطيل التنظيف التلقائي
تفعيل / تعطيل زوجني
تفعيل / تعطيل كت
تفعيل / تعطيل الردود
تفعيل / تعطيل الانذار
تفعيل / تعطيل التحذير
تفعيل / تعطيل اطردني
تفعيل / تعطيل نزلني
تفعيل / تعطيل الحظر
تفعيل / تعطيل الطرد
تفعيل / تعطيل الرفع
تفعيل / تعطيل التنزيل
تفعيل / تعطيل الكشف
تفعيل / تعطيل ترند
تفعيل / تعطيل همسه
قفل / فتح الاشعارات
ترتيب الاوامر / تعطيل ترتيب الاوامر
━━━━━━━━━━━━━━━━
اوامر التثبيت:
تثبيت - بالرد على الرسالة
━━━━━━━━━━━━━━━━
اوامر المنشن (التاك):
تاك عام / @all
تاك
نداء
"""

COMMAND_5 = """
-اهلا بك في قائمة اوامر التسليه:
_
اوامر الزواج:
زوجني
طلقني
━━━━━━━━━━━━━━━━
اوامر التنظيف:
مسح رسائلي
مسح + عدد
امسح - بالرد على الرسالة
━━━━━━━━━━━━━━━━
الالعاب:
جمل / جملة - لعبة الجمل المشوشة
كت / سؤال - سؤال عشوائي
اعلام / أعلام - لعبة الأعلام
ترتيب - لعبة ترتيب الحروف
تفكيك - لعبة تفكيك الكلمة
عواصم - لعبة تخمين العواصم
حزورة - لعبة الحزورة
اكس او / XO - لعبة اكس او
━━━━━━━━━━━━━━━━
اخرى:
شعر - عرض بيت شعري
نقاطي - عرض نقاطك
لقبي - عرض لقبك
لقبني - تعيين لقب
"""

COMMAND_6 = """
-اهلا بك في قائمة اوامر الخدميه:
_
الخدمات العامة:
ايدي - عرض بطاقة المعلومات
رتبتي - عرض رتبتك
صلاحياتي - عرض صلاحياتك
كشف - كشف معلومات العضو
البايو - عرض البايو
الردود - عرض الردود المخصصة
المجموعة - معلومات المجموعة
الرابط - رابط المجموعة
المطور - معلومات المطور
المالك - معلومات المالك
الساعه / الساعة - الوقت والتاريخ
التاريخ - التاريخ اليوم
السورس - قناة السورس
بوت - كلمة ترحيبية
    اطردني - طرد نفسك من المجموعة
    نزلني - تنزيل جميع رتبك
    ترند - عرض الترند
    ━━━━━━━━━━━━━━━━
    الاشتراك الاجباري:
(اعدادات الاشتراك الاجباري للمالك الاساسي فقط)
"""

PREDEFINED_ALIASES = {
    "ح": "حزورة", "رد": "اضف رد", "تك": "تنزيل الكل", "تغ": "تغيير الايدي",
    "اد": "رفع ادمن", "حذ": "حذف رد", "تعط": "تعطيل الايدي بالصورة",
    "م": "رفع مميز", "م ر": "مسح الرتب", "امر": "اضف امر",
    "تفع": "تفعيل الايدي بالصورة", "ام": "امسح", "ند": "نداء",
    "ك": "كشف", "رر": "عرض الردود", "ر": "الرابط",
    "تكك": "تاك عام", "من": "رفع منشئ", "اس": "رفع منشئ اساسي",
    "رف": "رفع القيود", "رس": "مسح رسائلي", "الغ": "الغاء حظر",
    "ش": "شعر", "ت": "تثبيت", "ق ك": "قفل الكل",
    "ا": "ايدي", "،،": "مسح المكتومين", "ثانوي": "رفع مطور ثانوي",
    "مد": "رفع مدير", "مط": "رفع مطور",
}

GAMES_LIST = """
🎮 **قائمة الألعاب:**

1️⃣ `جمل` - إعادة كتابة جملة مشوشة
2️⃣ `كت` - سؤال عشوائي
3️⃣ `اعلام` - تخمين اسم الدولة من العلم
4️⃣ `ترتيب` - ترتيب الحروف
5️⃣ `تفكيك` - تفكيك الكلمة
6️⃣ `عواصم` - تخمين العاصمة
7️⃣ `حزورة` - الغاز وفوازير
8️⃣ `اكس او / XO` - لعبة اكس او
9️⃣ `لغز` - لغز مع خيارات
🔟 `اسئلني` - سؤال ثقافي
1️⃣1️⃣ `محيبس` - لعبة المحيبس
1️⃣2️⃣ `ايموجي` - لعبة الإيموجي الجماعية
"""
 


@app.on_message(filters.group, group=1)
async def group_handler(client, message):
    cid = message.chat.id
    uid = message.from_user.id if message.from_user else None
    if not uid:
        return

    media_types = (message.photo, message.video, message.audio, message.voice,
                   message.sticker, message.animation, message.document, message.video_note)
    if any(media_types):
        await DB.execute("INSERT OR IGNORE INTO media_history (chat_id,message_id) VALUES (?,?)", (cid, message.id), commit=True)

        # Auto-clean: if enabled, delete all tracked media when count reaches threshold
        ac = await DB.execute("SELECT auto_clean_active, auto_clean_count FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ac and ac[0]:
            threshold = ac[1] or 20
            mh = await DB.execute("SELECT message_id FROM media_history WHERE chat_id=?", (cid,), fetchall=True)
            if len(mh) >= threshold:
                mids = [r[0] for r in mh]
                for i in range(0, len(mids), 100):
                    try:
                        await client.delete_messages(cid, mids[i:i+100])
                    except Exception:
                        for mid in mids[i:i+100]:
                            try:
                                await client.delete_messages(cid, [mid])
                            except Exception:
                                pass
                await DB.execute("DELETE FROM media_history WHERE chat_id=?", (cid,), commit=True)
                try:
                    await client.send_message(cid, f"✅ تم حذف {len(mh)} وسائط بواسطة التنظيف التلقائي.")
                except Exception:
                    pass

        # Media-specific lock check (instant delete, before NSFW to avoid scanning locked types)
        media_locks = await DB.execute(
            "SELECT lock_audio,lock_voice,lock_file,lock_video,lock_photo,lock_sticker,lock_gif "
            "FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if media_locks:
            la, lv, lf, lvd, lp, ls, lg = media_locks
            if (la and message.audio) or (lv and message.voice) or (lf and message.document) or \
               (lvd and (message.video or message.video_note)) or (lp and message.photo) or \
               (ls and message.sticker) or (lg and message.animation):
                try:
                    await message.delete()
                except Exception:
                    pass
                return
        if cid in conv_states and conv_states[cid].get("user_id") == uid and conv_states[cid].get("state") == "waiting_group_photo":
            if message.photo:
                try:
                    photo_path = await client.download_media(message.photo.file_id, file_name=f"group_photo_{cid}.jpg")
                    if not photo_path:
                        await message.reply_text("❌ تعذر تحميل الصورة.")
                        return
                    await client.set_chat_photo(chat_id=cid, photo=photo_path)
                    conv_states.pop(cid, None)
                    await message.reply_text("✅ تم تعيين الصورة كصورة للمجموعة بنجاح.")
                except Exception as e:
                    await message.reply_text(f"❌ تعذر تعيين الصورة: {e}")
                return

    if uid == OWNER_ID:
        await DB.execute("INSERT OR IGNORE INTO bot_owners (user_id) VALUES (?)", (uid,), commit=True)

    await DB.execute("INSERT INTO groups (chat_id,is_active) VALUES (?,0) ON CONFLICT DO NOTHING", (cid,), commit=True)

    muted = await DB.execute("SELECT 1 FROM muted_users WHERE chat_id=? AND user_id=?", (cid, uid), fetchone=True)
    if muted:
        try:
            await message.delete()
        except Exception:
            pass
        return

    await DB.execute("INSERT OR IGNORE INTO user_messages (chat_id,user_id,message_id) VALUES (?,?,?)",
                     (cid, uid, message.id), commit=True)

    text = message.text
    if text and cid in emoji_games:
        game = emoji_games[cid]
        if game["phase"] == "playing":
            if uid == game["players"][game["sender_idx"]]["id"]:
                has_letter = any(c.isalpha() for c in text)
                if has_letter:
                    try:
                        await message.delete()
                    except Exception:
                        pass
                    return
            if text.strip().lower() == game["secret_word"].strip().lower():
                for p in game["players"]:
                    if p and p["id"] == uid:
                        await add_points(cid, uid, 1)
                        await add_points(cid, game["players"][game["sender_idx"]]["id"], 1)
                        await message.reply_text(f"🎉 **إجابة صحيحة!**\n\n{message.from_user.mention} ربح نقطة!\n{game['players'][game['sender_idx']]['name']} ربح نقطة كمرسل!\nالكلمة كانت: **{game['secret_word']}**")
                        emoji_games.pop(cid, None)
                        return
    if text:
        first_word = text.split()[0]
        # 1) Exact DB alias match
        alias = await DB.execute("SELECT original_cmd FROM aliases WHERE chat_id=? AND custom_cmd=?", (cid, text), fetchone=True)
        if alias:
            in_conv_state = cid in conv_states and conv_states[cid].get("user_id") == uid
            if not in_conv_state:
                text = alias[0]
        # 2) Exact PREDEFINED_ALIASES match (handles multi-word like "م ر")
        if not alias and text in PREDEFINED_ALIASES:
            aa = await DB.execute("SELECT aliases_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
            if aa and aa[0]:
                in_conv_state = cid in conv_states and conv_states[cid].get("user_id") == uid
                if not in_conv_state:
                    text = PREDEFINED_ALIASES[text]
        def _is_valid_target(word):
            return word.startswith("@") or word.isdigit()
        # 3) First-word DB alias match (shortcut + arguments like "م @user")
        if not alias and first_word != text:
            rest = text[len(first_word):].strip()
            if rest and _is_valid_target(rest.split()[0]):
                alias = await DB.execute("SELECT original_cmd FROM aliases WHERE chat_id=? AND custom_cmd=?", (cid, first_word), fetchone=True)
                if alias:
                    in_conv_state = cid in conv_states and conv_states[cid].get("user_id") == uid
                    if not in_conv_state:
                        text = alias[0] + text[len(first_word):]
        # 4) First-word PREDEFINED_ALIASES match (shortcut + arguments like "م @user")
        if not alias and first_word in PREDEFINED_ALIASES:
            rest = text[len(first_word):].strip()
            if rest and _is_valid_target(rest.split()[0]):
                aa = await DB.execute("SELECT aliases_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
                if aa and aa[0]:
                    in_conv_state = cid in conv_states and conv_states[cid].get("user_id") == uid
                    if not in_conv_state:
                        text = PREDEFINED_ALIASES[first_word] + text[len(first_word):]

    if text:
        if await is_bot_cmd(cid, text):
            if not await check_force_sub(client, uid):
                try:
                    row_msg = await DB.execute("SELECT value FROM bot_settings WHERE key='force_sub_msg'", fetchone=True)
                    row_link = await DB.execute("SELECT value FROM bot_settings WHERE key='force_sub_link'", fetchone=True)
                    sub_msg = row_msg[0] if row_msg and row_msg[0] else "⚠️ عذرا {mention} لا يمكنك استخدام البوت قبل الاشتراك بقناة البوت."
                    sub_link = row_link[0] if row_link and row_link[0] else ""
                    sub_text = sub_msg.replace("{mention}", message.from_user.mention).replace("{link}", sub_link)
                    kb = None
                    if sub_link:
                        kb = InlineKeyboardMarkup([[InlineKeyboardButton("📢 اشترك في القناة", url=sub_link)]])
                    await message.reply_text(sub_text, reply_markup=kb)
                except Exception:
                    pass
                return

    role_key, sender_level = await get_role(cid, uid, client)

    if text and sender_level < 1:
        bw = await DB.execute("SELECT word FROM banned_words WHERE chat_id=?", (cid,), fetchall=True)
        if bw:
            tlow = text.lower()
            for (bw,) in bw:
                if bw.lower() in tlow:
                    try:
                        await message.delete()
                    except Exception:
                        pass
                    break

    if sender_level < 1:
        locks = await DB.execute(
            "SELECT lock_voice,lock_video,lock_photo,lock_sticker,lock_file,lock_gif,"
            "lock_chat,lock_mention,lock_link,lock_long_text,lock_spam,lock_forward,lock_premium_sticker,lock_audio,lock_spoiler "
            "FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if locks:
            lv, lvd, lp, ls, lf, lg, lc, lm, ll, llt, lsp, lfw, lps, la, lspo = locks
            if lc:
                try: await message.delete()
                except Exception: pass
                return
            if lspo and text:
                if message.entities and any(e.type == MessageEntityType.SPOILER for e in message.entities):
                    try: await message.delete()
                    except Exception: pass
                    return
            if lfw and (message.forward_date or message.forward_from or message.forward_from_chat):
                try: await message.delete()
                except Exception: pass
                return
            if lps and message.sticker and message.sticker.is_premium:
                try: await message.delete()
                except Exception: pass
                return
            if lm:
                content = (text or "") + " " + (message.caption or "")
                if "@" in content or "#" in content:
                    try: await message.delete()
                    except Exception: pass
                    return
            if ll:
                content = (text or "") + " " + (message.caption or "")
                if any(x in content for x in ("http://", "https://", "t.me/", "telegram.me/")):
                    try: await message.delete()
                    except Exception: pass
                    return
            if llt and text and (len(text.split('\n')) >= 4 or len(text) >= 200):
                try: await message.delete()
                except Exception: pass
                return
            if lsp and text:
                now = time.time()
                sc = spam_cache.setdefault(cid, {}).get(uid)
                if sc and sc["t"] == text and (now - sc["ts"]) <= 2:
                    try:
                        await message.delete()
                        ref = f"@{message.from_user.username}" if message.from_user.username else message.from_user.mention
                        await client.send_message(cid, f"⚠️ تنبيه ممنوع التكرار {ref}")
                    except Exception:
                        pass
                    return
                spam_cache.setdefault(cid, {})[uid] = {"t": text, "ts": now}

    if text:
        bm = await DB.execute("SELECT 1 FROM banned_user_messages WHERE chat_id=? AND user_id=? AND message_text=?", (cid, uid, text), fetchone=True)
        if bm:
            try:
                await message.delete()
            except Exception:
                pass
            return

    if text and sender_level < 2:
        lsw = await DB.execute("SELECT lock_swear FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if lsw and lsw[0]:
            tlow = text.lower()
            if any(w in tlow for w in SWEAR_WORDS):
                try:
                    await message.delete()
                except Exception:
                    pass
                ref = f"@{message.from_user.username}" if message.from_user.username else message.from_user.mention
                await DB.execute("INSERT INTO warnings (chat_id,user_id,count) VALUES (?,?,1) ON CONFLICT DO UPDATE SET count=count+1", (cid, uid), commit=True)
                c = (await DB.execute("SELECT count FROM warnings WHERE chat_id=? AND user_id=?", (cid, uid), fetchone=True) or [1])[0]
                if c >= 3:
                    try:
                        await client.restrict_chat_member(cid, uid, ChatPermissions(can_send_messages=False))
                    except Exception:
                        pass
                    await DB.execute("INSERT OR IGNORE INTO muted_users (chat_id,user_id) VALUES (?,?)", (cid, uid), commit=True)
                    await DB.execute("DELETE FROM warnings WHERE chat_id=? AND user_id=?", (cid, uid), commit=True)
                    await client.send_message(cid, f"🔇 {ref}\nتم كتمه بسبب تخطي عدد التحذيرات المسموح بها (3/3).")
                else:
                    await client.send_message(cid, f"⚠️ {ref}\nممنوع السب❗\nتحذير {c}/3")
                return

    if text and cid in active_games:
        game = active_games[cid]
        if "answer" not in game:
            pass
        else:
            correct = game["answer"]
            ans = text.strip()
            ok = ans.lower() in [a.lower() for a in correct] if isinstance(correct, list) else ans.lower() == correct.lower()
            if ok:
                active_games.pop(cid, None)
                await add_points(cid, uid, 5)
                await message.reply_text(f"🎉 صحيح! لقد فاز البطل {message.from_user.mention} بالإجابة الصحيحة السريعة وحصل على 5 نقاط 🏆")
                return

    # --- Conversation states ---
    if cid in conv_states:
        st = conv_states[cid]
        if st["user_id"] == uid and (text or st["state"] == "waiting_reply_response"):
            if text in ("الغاء", "إلغاء"):
                conv_states.pop(cid, None)
                await message.reply_text("❌ تم إلغاء العملية الإدارية الحالية بنجاح.")
                return
            s = st["state"]
            if s == "waiting_welcome":
                await DB.execute("UPDATE groups SET welcome_msg=? WHERE chat_id=?", (text, cid), commit=True)
                conv_states.pop(cid, None)
                await message.reply_text("✅ تم تعيين رسالة الترحيب بنجاح!")
                return
            elif s == "waiting_rules":
                await DB.execute("UPDATE groups SET rules=? WHERE chat_id=?", (text, cid), commit=True)
                conv_states.pop(cid, None)
                await message.reply_text("✅ تم حفظ قوانين المجموعة بنجاح!")
                return
            elif s == "waiting_alias_old":
                st["tmp"] = text
                st["state"] = "waiting_alias_new"
                await message.reply_text("💬 ارسل الآن الكلمة الجديدة كبديل مختصر للأمر:")
                return
            elif s == "waiting_alias_new":
                old, new = st["tmp"], text
                await DB.execute("INSERT OR REPLACE INTO aliases (chat_id,original_cmd,custom_cmd) VALUES (?,?,?)", (cid, old, new), commit=True)
                conv_states.pop(cid, None)
                await message.reply_text(f"✅ تم إضافة اختصار الأمر بنجاح:\n`{new}` ➡️ `{old}`")
                return
            elif s == "waiting_alias_delete":
                exists = await DB.execute("SELECT 1 FROM aliases WHERE chat_id=? AND custom_cmd=?", (cid, text), fetchone=True)
                if exists:
                    await DB.execute("DELETE FROM aliases WHERE chat_id=? AND custom_cmd=?", (cid, text), commit=True)
                    await message.reply_text(f"✅ تم حذف الأمر المخصص `{text}` بنجاح.")
                else:
                    await message.reply_text(f"❌ لم يتم العثور على الأمر المخصص `{text}`.")
                conv_states.pop(cid, None)
                return
            elif s == "waiting_reply_keyword":
                st["tmp"] = {"kw": text.strip()}
                st["state"] = "waiting_reply_response"
                await message.reply_text("• حسناً يمكنك اضافة \n( نص,صوره,فيديو,متحركه,بصمه,اغنيه,ملف,ملصق )")
                return
            elif s == "waiting_reply_response":
                kw = st["tmp"]["kw"]
                rtype, rdata = None, None
                if text:
                    rtype, rdata = "text", text
                elif message.photo: rtype, rdata = "photo", message.photo.file_id
                elif message.video: rtype, rdata = "video", message.video.file_id
                elif message.animation: rtype, rdata = "animation", message.animation.file_id
                elif message.voice: rtype, rdata = "voice", message.voice.file_id
                elif message.audio: rtype, rdata = "audio", message.audio.file_id
                elif message.document: rtype, rdata = "document", message.document.file_id
                elif message.sticker: rtype, rdata = "sticker", message.sticker.file_id
                if not rtype:
                    await message.reply_text("⚠️ نوع جواب الرد غير مدعوم، يرجى إرسال (نص، صورة، فيديو، متحركة، بصمة، أغنية، ملف، ملصق) أو أرسل 'الغاء':")
                    return
                await DB.execute("INSERT OR REPLACE INTO custom_replies (chat_id,keyword,reply_type,reply_data) VALUES (?,?,?,?)",
                                 (cid, kw, rtype, rdata), commit=True)
                conv_states.pop(cid, None)
                await message.reply_text("✅ تم حفظ الرد بنجاح!")
                return
            elif s == "waiting_reply_delete":
                exists = await DB.execute("SELECT 1 FROM custom_replies WHERE chat_id=? AND keyword=?", (cid, text.strip()), fetchone=True)
                if exists:
                    await DB.execute("DELETE FROM custom_replies WHERE chat_id=? AND keyword=?", (cid, text.strip()), commit=True)
                    conv_states.pop(cid, None)
                    await message.reply_text("تم حذف الرد")
                else:
                    conv_states.pop(cid, None)
                    await message.reply_text(f"❌ لم يتم العثور على رد مخصص مسجل للكلمة **'{text}'**.")
                return

    row = await DB.execute("SELECT is_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
    is_active = row[0] if row else 0

    if not is_active:
        if text and text.strip() == "تفعيل":
            if sender_level < 2:
                await message.reply_text("❌ تفعيل البوت متاح فقط للمشرفين ومالك الكروب.")
                return
            await DB.execute("UPDATE groups SET is_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "البوت")
        return

    await DB.execute("INSERT INTO messages_count (chat_id,user_id,count) VALUES (?,?,1) ON CONFLICT DO UPDATE SET count=count+1",
                     (cid, uid), commit=True)

    if not text:
        return

    if text.startswith("مسح ") and text[4:].strip().isdigit():
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        cnt = int(text[4:].strip())
        cnt = max(1, min(cnt, 300))
        sm = await message.reply_text(f"🧹 جاري مسح آخر {cnt} رسالة من المجموعة...")
        rows = await DB.execute(
            "SELECT message_id FROM user_messages WHERE chat_id=? ORDER BY message_id DESC LIMIT ?",
            (cid, cnt), fetchall=True)
        if not rows:
            try:
                await sm.edit_text("📭 لم يتم العثور على رسائل لمسحها.")
                await asyncio.sleep(2)
                await sm.delete()
            except Exception:
                pass
            return
        mids = [r[0] for r in rows if r[0] != sm.id]
        mids.append(sm.id)
        dc = 0
        for i in range(0, len(mids), 100):
            try:
                await client.delete_messages(cid, mids[i:i+100])
                dc += len(mids[i:i+100])
                await DB.execute(
                    "DELETE FROM user_messages WHERE chat_id=? AND message_id IN ({})".format(
                        ",".join("?" for _ in mids[i:i+100])),
                    (cid,) + tuple(mids[i:i+100]), commit=True)
            except Exception:
                for mid in mids[i:i+100]:
                    try:
                        await client.delete_messages(cid, [mid])
                        dc += 1
                        await DB.execute("DELETE FROM user_messages WHERE chat_id=? AND message_id=?", (cid, mid), commit=True)
                    except Exception:
                        pass
        await DB.execute("DELETE FROM user_messages WHERE chat_id=? AND message_id=?", (cid, sm.id), commit=True)
        try:
            await message.reply_text(f"• تم مسح - {dc} رساله")
        except Exception:
            pass
        return

    if text.strip() in ("تعطيل", "تعطيل البوت"):
        if role_key in ("owner", "supreme"):
            await DB.execute("UPDATE groups SET is_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "البوت")
        else:
            await message.reply_text("❌ عذراً، تعطيل البوت متاح فقط للمشرفين والمالكين.")
        return

    if sender_level >= 2:
        if text == "تعطيل تاك عام":
            await DB.execute("UPDATE groups SET tag_all_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "تاك عام")
            return
        if text == "تفعيل تاك عام":
            await DB.execute("UPDATE groups SET tag_all_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "تاك عام")
            return
        if text == "تعطيل تاك":
            await DB.execute("UPDATE groups SET tag_random_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "تاك")
            return
        if text == "تفعيل تاك":
            await DB.execute("UPDATE groups SET tag_random_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "تاك")
            return
        if text == "تعطيل الايدي":
            await DB.execute("UPDATE groups SET id_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "الايدي")
            return
        if text == "تفعيل الايدي":
            await DB.execute("UPDATE groups SET id_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "الايدي")
            return
        if text == "تعطيل الايدي بالصورة":
            await DB.execute("UPDATE groups SET id_photo_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "الايدي بالصورة")
            return
        if text == "تفعيل الايدي بالصورة":
            await DB.execute("UPDATE groups SET id_photo_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "الايدي بالصورة")
            return
        if text == "تفعيل الترحيب":
            log.info("Welcome enabled in chat %d by user %d", cid, uid)
            await DB.execute("UPDATE groups SET welcome_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "الترحيب")
            return
        if text == "تعطيل الترحيب":
            log.info("Welcome disabled in chat %d by user %d", cid, uid)
            await DB.execute("UPDATE groups SET welcome_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "الترحيب")
            return
        if text == "قفل الملصق المميز":
            await DB.execute("UPDATE groups SET lock_premium_sticker=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "قفل", "الملصق المميز")
            return
        if text == "فتح الملصق المميز":
            await DB.execute("UPDATE groups SET lock_premium_sticker=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "فتح", "الملصق المميز")
            return
        if text == "قفل الاشعارات":
            await DB.execute("UPDATE groups SET lock_notifications=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "قفل", "الاشعارات")
            return
        if text == "فتح الاشعارات":
            await DB.execute("UPDATE groups SET lock_notifications=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "فتح", "الاشعارات")
            return
        if text == "تفعيل الالعاب":
            await DB.execute("UPDATE groups SET games_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "الألعاب")
            return
        if text == "تعطيل الالعاب":
            await DB.execute("UPDATE groups SET games_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "الألعاب")
            return
        if text == "تفعيل البايو":
            await DB.execute("UPDATE groups SET bio_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "البايو")
            return
        if text == "تعطيل البايو":
            await DB.execute("UPDATE groups SET bio_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "البايو")
            return
        if text == "تفعيل امسح":
            await DB.execute("UPDATE groups SET delete_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "امسح")
            return
        if text == "تعطيل امسح":
            await DB.execute("UPDATE groups SET delete_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "امسح")
            return
        if text == "تفعيل التنظيف التلقائي":
            await DB.execute("UPDATE groups SET auto_clean_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "التنظيف التلقائي")
            return
        if text == "تعطيل التنظيف التلقائي":
            await DB.execute("UPDATE groups SET auto_clean_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "التنظيف التلقائي")
            return
        if text.startswith("تنظيف تلقائي "):
            ac = await DB.execute("SELECT auto_clean_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
            if ac and not ac[0]:
                await message.reply_text("❌ أمر التنظيف التلقائي معطل في هذه المجموعة.")
                return
            num_str = text[len("تنظيف تلقائي "):].strip()
            if num_str.isdigit():
                cnt = int(num_str)
                cnt = max(5, min(cnt, 500))
                await DB.execute("UPDATE groups SET auto_clean_count=? WHERE chat_id=?", (cnt, cid), commit=True)
                await message.reply_text(f"✅ تم ضبط التنظيف التلقائي على {cnt} وسائط.")
            else:
                await message.reply_text("❌ الاستخدام: `تنظيف تلقائي + العدد` (مثال: `تنظيف تلقائي 50`).")
            return
        if text == "تفعيل زوجني":
            await DB.execute("UPDATE groups SET marry_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "زوجني")
            return
        if text == "تعطيل زوجني":
            await DB.execute("UPDATE groups SET marry_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "زوجني")
            return
        if text == "تفعيل طلقني":
            await DB.execute("UPDATE groups SET marry_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "طلقني")
            return
        if text == "تعطيل طلقني":
            await DB.execute("UPDATE groups SET marry_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "طلقني")
            return
        if text == "تفعيل كت":
            await DB.execute("UPDATE groups SET ask_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "كت")
            return
        if text == "تعطيل كت":
            await DB.execute("UPDATE groups SET ask_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "كت")
            return
        if text == "تفعيل الردود":
            await DB.execute("UPDATE groups SET replies_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "الردود")
            return
        if text == "تعطيل الردود":
            await DB.execute("UPDATE groups SET replies_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "الردود")
            return
        if text == "تفعيل الانذار":
            await DB.execute("UPDATE groups SET warn_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "الانذار")
            return
        if text == "تعطيل الانذار":
            await DB.execute("UPDATE groups SET warn_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "الانذار")
            return
        if text == "تفعيل التحذير":
            await DB.execute("UPDATE groups SET warn_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "التحذير")
            return
        if text == "تعطيل التحذير":
            await DB.execute("UPDATE groups SET warn_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "التحذير")
            return
        if text == "تفعيل اطردني":
            await DB.execute("UPDATE groups SET kickme_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "اطردني")
            return
        if text == "تعطيل اطردني":
            await DB.execute("UPDATE groups SET kickme_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "اطردني")
            return
        if text == "تفعيل نزلني":
            await DB.execute("UPDATE groups SET unrankme_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "نزلني")
            return
        if text == "تعطيل نزلني":
            await DB.execute("UPDATE groups SET unrankme_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "نزلني")
            return
        if text == "تفعيل الحظر":
            if sender_level < 3:
                await message.reply_text("❌ يتطلب هذا الأمر صلاحية مدير فما فوق.")
                return
            await DB.execute("UPDATE groups SET ban_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "الحظر")
            return
        if text == "تعطيل الحظر":
            if sender_level < 3:
                await message.reply_text("❌ يتطلب هذا الأمر صلاحية مدير فما فوق.")
                return
            await DB.execute("UPDATE groups SET ban_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "الحظر")
            return
        if text == "تفعيل الطرد":
            if sender_level < 3:
                await message.reply_text("❌ يتطلب هذا الأمر صلاحية مدير فما فوق.")
                return
            await DB.execute("UPDATE groups SET kick_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "الطرد")
            return
        if text == "تعطيل الطرد":
            if sender_level < 3:
                await message.reply_text("❌ يتطلب هذا الأمر صلاحية مدير فما فوق.")
                return
            await DB.execute("UPDATE groups SET kick_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "الطرد")
            return
        if text == "تفعيل الرفع":
            if role_key not in ("bot_owner", "supreme"):
                await message.reply_text("❌ هذا الأمر متاح لمالك البوت فقط.")
                return
            await DB.execute("UPDATE groups SET promote_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "الرفع")
            return
        if text == "تعطيل الرفع":
            if role_key not in ("bot_owner", "supreme"):
                await message.reply_text("❌ هذا الأمر متاح لمالك البوت فقط.")
                return
            await DB.execute("UPDATE groups SET promote_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "الرفع")
            return
        if text == "تفعيل التنزيل":
            if role_key not in ("bot_owner", "supreme"):
                await message.reply_text("❌ هذا الأمر متاح لمالك البوت فقط.")
                return
            await DB.execute("UPDATE groups SET demote_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "التنزيل")
            return
        if text == "تعطيل التنزيل":
            if role_key not in ("bot_owner", "supreme"):
                await message.reply_text("❌ هذا الأمر متاح لمالك البوت فقط.")
                return
            await DB.execute("UPDATE groups SET demote_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "التنزيل")
            return
        if text == "تفعيل الكشف":
            if sender_level < 4:
                await message.reply_text("❌ يتطلب هذا الأمر صلاحية منشئ فما فوق.")
                return
            await DB.execute("UPDATE groups SET reveal_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "الكشف")
            return
        if text == "تعطيل الكشف":
            if sender_level < 4:
                await message.reply_text("❌ يتطلب هذا الأمر صلاحية منشئ فما فوق.")
                return
            await DB.execute("UPDATE groups SET reveal_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "الكشف")
            return
        if text == "تفعيل ترند":
            await DB.execute("UPDATE groups SET trend_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "الترند")
            return
        if text == "تعطيل ترند":
            await DB.execute("UPDATE groups SET trend_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "الترند")
            return
        if text == "تفعيل همسه":
            await DB.execute("UPDATE groups SET whisper_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "الهمسات")
            return
        if text == "تعطيل همسه":
            await DB.execute("UPDATE groups SET whisper_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "الهمسات")
            return
        if text.startswith("قفل ") or text.startswith("فتح "):
            parts = text.split(" ", 1)
            if len(parts) == 2:
                act, tgt = parts
                is_lock = act == "قفل"
                if tgt in LOCK_COLUMNS:
                    col = LOCK_COLUMNS[tgt]
                    await DB.execute(f"UPDATE groups SET {col}=? WHERE chat_id=?", (1 if is_lock else 0, cid), commit=True)
                    await _reply_toggle(message, "قفل" if is_lock else "فتح", tgt)
                    return
                if tgt == "الكل":
                    val = 1 if is_lock else 0
                    cols = ["lock_voice","lock_video","lock_photo","lock_sticker","lock_join","lock_file",
                    "lock_gif","lock_chat","lock_mention","lock_link","lock_long_text","lock_spam","lock_forward","lock_edit","lock_audio","lock_media_edit"]
                    sets = ", ".join(f"{c}=?" for c in cols)
                    await DB.execute(f"UPDATE groups SET {sets} WHERE chat_id=?", (val,)*len(cols) + (cid,), commit=True)
                    await _reply_toggle(message, "قفل" if is_lock else "فتح", "الكل")
                    return
        if text in ("قفل التفليش", "فتح التفليش"):
            is_lock = text == "قفل التفليش"
            val = 1 if is_lock else 0
            cols = ["lock_voice","lock_video","lock_photo","lock_sticker","lock_join","lock_file",
                    "lock_gif","lock_chat","lock_mention","lock_link","lock_long_text","lock_spam","lock_forward","lock_edit","lock_audio","lock_media_edit"]
            sets = ", ".join(f"{c}=?" for c in cols)
            await DB.execute(f"UPDATE groups SET {sets} WHERE chat_id=?", (val,)*len(cols) + (cid,), commit=True)
            await _reply_toggle(message, "قفل" if is_lock else "فتح", "التفليش")
            return
        if text == "تعطيل الرابط":
            await DB.execute("UPDATE groups SET link_active=0 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تعطيل", "الرابط")
            return
        if text == "تفعيل الرابط":
            await DB.execute("UPDATE groups SET link_active=1 WHERE chat_id=?", (cid,), commit=True)
            await _reply_toggle(message, "تفعيل", "الرابط")
            return
        if text in ("المكتومين", "قائمة المكتومين"):
            rows = await DB.execute("SELECT user_id FROM muted_users WHERE chat_id=?", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("📭 لا يوجد مكتومين في هذه المجموعة.")
                return
            users = []
            for (uid,) in rows:
                try:
                    u = await client.get_users(uid)
                    users.append(u.mention)
                except Exception:
                    users.append(f"`{uid}`")
            await message.reply_text("🔇 **قائمة المكتومين:**\n" + "\n".join(f"• {u}" for u in users))
            return
        if text in ("المقيدين", "قائمة المقيدين"):
            restricted = []
            try:
                async for m in client.get_chat_members(cid, filter=ChatMembersFilter.RESTRICTED):
                    restricted.append(m.user.mention if m.user else f"`{m.user.id}`")
            except Exception:
                pass
            if not restricted:
                await message.reply_text("📭 لا يوجد مقيدين في هذه المجموعة.")
                return
            await message.reply_text("🚫 **قائمة المقيدين:**\n" + "\n".join(f"• {u}" for u in restricted))
            return
        if text in ("المحظورين", "قائمة المحظورين"):
            banned = []
            try:
                async for m in client.get_chat_members(cid, filter=ChatMembersFilter.BANNED):
                    banned.append(m.user.mention if m.user else f"`{m.user.id}`")
            except Exception:
                pass
            if not banned:
                await message.reply_text("📭 لا يوجد محظورين في هذه المجموعة.")
                return
            await message.reply_text("⛔ **قائمة المحظورين:**\n" + "\n".join(f"• {u}" for u in banned))
            return
        if text == "المميزين":
            if sender_level <= 1:
                await message.reply_text("❌ لا تملك صلاحية عرض هذه الرتبة.")
                return
            rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='vip'", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("📭 لا يوجد مميزين في هذه المجموعة.")
                return
            users = []
            for (uid,) in rows:
                try:
                    u = await client.get_users(uid)
                    users.append(u.mention)
                except Exception:
                    users.append(f"`{uid}`")
            await message.reply_text("⭐ **قائمة المميزين:**\n" + "\n".join(f"• {u}" for u in users))
            return
        if text in ("الادمنية", "الادمنيه"):
            if sender_level <= 2:
                await message.reply_text("❌ لا تملك صلاحية عرض هذه الرتبة.")
                return
            rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='admin'", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("📭 لا يوجد ادمنية في هذه المجموعة.")
                return
            users = []
            for (uid,) in rows:
                try:
                    u = await client.get_users(uid)
                    users.append(u.mention)
                except Exception:
                    users.append(f"`{uid}`")
            await message.reply_text("🛡️ **قائمة الادمنية:**\n" + "\n".join(f"• {u}" for u in users))
            return
        if text == "المدراء":
            if sender_level <= 3:
                await message.reply_text("❌ لا تملك صلاحية عرض هذه الرتبة.")
                return
            rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='manager'", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("📭 لا يوجد مدراء في هذه المجموعة.")
                return
            users = []
            for (uid,) in rows:
                try:
                    u = await client.get_users(uid)
                    users.append(u.mention)
                except Exception:
                    users.append(f"`{uid}`")
            await message.reply_text("👔 **قائمة المدراء:**\n" + "\n".join(f"• {u}" for u in users))
            return
        if text == "مسح المحظورين":
            cnt = 0
            try:
                async for m in client.get_chat_members(cid, filter=ChatMembersFilter.BANNED):
                    try:
                        await client.unban_chat_member(cid, m.user.id)
                        cnt += 1
                    except Exception:
                        pass
            except Exception:
                pass
            if cnt:
                await message.reply_text(f"• تم مسح {cnt} من المحظورين")
            else:
                await message.reply_text("لا يوجد محظورين لمسحهم")
            return
        if text == "مسح المطرودين":
            cnt = 0
            try:
                async for m in client.get_chat_members(cid, filter=ChatMembersFilter.BANNED):
                    try:
                        await client.unban_chat_member(cid, m.user.id)
                        cnt += 1
                    except Exception:
                        pass
            except Exception:
                pass
            if cnt:
                await message.reply_text(f"• تم مسح {cnt} من المحظورين")
            else:
                await message.reply_text("لا يوجد محظورين لمسحهم")
            return
        if text == "مسح المكتومين":
            rows = await DB.execute("SELECT user_id FROM muted_users WHERE chat_id=?", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("• لا يوجد مكتومين حاليا")
                return
            await DB.execute("DELETE FROM muted_users WHERE chat_id=?", (cid,), commit=True)
            await message.reply_text(f"• تم مسح {len(rows)} من المكتومين")
            return
        if text == "مسح المميزين":
            if sender_level <= 1:
                await message.reply_text("❌ لا تملك صلاحية مسح هذه الرتبة.")
                return
            rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='vip'", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("• لا يوجد مميزين حاليا")
                return
            await DB.execute("DELETE FROM ranks WHERE chat_id=? AND role='vip'", (cid,), commit=True)
            await message.reply_text(f"• تم مسح {len(rows)} من المميزين")
            return
        if text == "مسح المقيدين":
            cnt = 0
            try:
                async for m in client.get_chat_members(cid, filter=ChatMembersFilter.RESTRICTED):
                    try:
                        await client.restrict_chat_member(cid, m.user.id, ChatPermissions(
                            can_send_messages=True, can_send_media_messages=True,
                            can_send_other_messages=True, can_add_web_page_previews=True))
                        cnt += 1
                    except Exception:
                        pass
            except Exception:
                pass
            if cnt:
                await message.reply_text(f"• تم مسح {cnt} من المقيديين")
            else:
                await message.reply_text("• لا يوجد مقيدين حاليا")
            return

        if text == "مسح الادمنيه":
            if sender_level <= 2:
                await message.reply_text("❌ لا تملك صلاحية مسح هذه الرتبة.")
                return
            rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='admin'", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("• لا يوجد ادمنيه حاليا")
                return
            await DB.execute("DELETE FROM ranks WHERE chat_id=? AND role='admin'", (cid,), commit=True)
            await message.reply_text(f"• تم مسح {len(rows)} من الادمنيه")
            return
        if text == "مسح المدراء":
            if sender_level <= 3:
                await message.reply_text("❌ لا تملك صلاحية مسح هذه الرتبة.")
                return
            rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='manager'", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("• لا يوجد مدراء حاليا")
                return
            await DB.execute("DELETE FROM ranks WHERE chat_id=? AND role='manager'", (cid,), commit=True)
            await message.reply_text(f"• تم مسح {len(rows)} من المدراء")
            return
        if text == "مسح المنشئين":
            if sender_level <= 4:
                await message.reply_text("❌ لا تملك صلاحية مسح هذه الرتبة.")
                return
            rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='creator'", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("• لا يوجد منشئين حاليا")
                return
            await DB.execute("DELETE FROM ranks WHERE chat_id=? AND role='creator'", (cid,), commit=True)
            await message.reply_text(f"• تم مسح {len(rows)} من المنشئين")
            return
        if text == "مسح المالكين":
            if sender_level <= 9:
                await message.reply_text("❌ لا تملك صلاحية مسح هذه الرتبة.")
                return
            rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='owner'", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("• لا يوجد مالكين حاليا")
                return
            await DB.execute("DELETE FROM ranks WHERE chat_id=? AND role='owner'", (cid,), commit=True)
            await message.reply_text(f"• تم مسح {len(rows)} من المالكين")
            return
        if text == "مسح المالكين الاساسين":
            if sender_level <= 8:
                await message.reply_text("❌ لا تملك صلاحية مسح هذه الرتبة.")
                return
            rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='owner_basic'", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("• لا يوجد مالكين اساسين حاليا")
                return
            await DB.execute("DELETE FROM ranks WHERE chat_id=? AND role='owner_basic'", (cid,), commit=True)
            await message.reply_text(f"• تم مسح {len(rows)} من المالكين الاساسين")
            return
        if text == "قائمة المنع":
            rows = await DB.execute("SELECT word FROM banned_words WHERE chat_id=?", (cid,), fetchall=True)
            if rows:
                words = "\n".join(f"• `{r[0]}`" for r in rows)
                await message.reply_text(f"🚫 **قائمة الكلمات الممنوعة:**\n\n{words}")
            else:
                await message.reply_text("📭 قائمة المنع فارغة.")
            return
        if text in ("قائمه المنع", "مسح قائمة المنع"):
            rows = await DB.execute("SELECT word FROM banned_words WHERE chat_id=?", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("• عذراً لا توجد كلمات ممنوعه ليتم حذفها")
                return
            await DB.execute("DELETE FROM banned_words WHERE chat_id=?", (cid,), commit=True)
            await message.reply_text(f"• بواسطة ↤︎ {message.from_user.mention}\n• تم مسح 〖{len(rows)}〗 كلمات من المنع")
            return
        if text == "منع":
            t = await extract_target(message)
            if not t or not message.reply_to_message or not message.reply_to_message.text:
                await message.reply_text("❌ يرجى الرد على رسالة تحتوي على كلمة لإضافتها إلى قائمة المنع.")
                return
            word = message.reply_to_message.text.strip().split("\n")[0][:100]
            await DB.execute("INSERT OR IGNORE INTO banned_words (chat_id,word) VALUES (?,?)", (cid, word), commit=True)
            await message.reply_text(f"✅ تمت إضافة `{word}` إلى قائمة المنع.")
            return
        if text == "الغاء منع":
            t = await extract_target(message)
            if not t or not message.reply_to_message or not message.reply_to_message.text:
                await message.reply_text("❌ يرجى الرد على رسالة تحتوي على الكلمة المراد إزالتها من قائمة المنع.")
                return
            word = message.reply_to_message.text.strip().split("\n")[0][:100]
            await DB.execute("DELETE FROM banned_words WHERE chat_id=? AND word=?", (cid, word), commit=True)
            await message.reply_text(f"✅ تمت إزالة `{word}` من قائمة المنع.")
            return
        if text == "منعه":
            ba = await DB.execute("SELECT ban_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
            if ba and not ba[0]:
                await message.reply_text("❌ أمر الحظر معطل في هذه المجموعة.")
                return
            if not message.reply_to_message or not message.reply_to_message.from_user or not message.reply_to_message.text:
                await message.reply_text("❌ يرجى الرد على رسالة نصية لحظرها من المرسل.")
                return
            target = message.reply_to_message.from_user
            msg_text = message.reply_to_message.text.strip()[:200]
            await DB.execute("INSERT OR IGNORE INTO banned_user_messages (chat_id,user_id,message_text) VALUES (?,?,?)",
                             (cid, target.id, msg_text), commit=True)
            await message.reply_text(f"✅ تم حظر هذه الرسالة من {target.mention}.")
            return
        if text == "الغاء منعه":
            if not message.reply_to_message or not message.reply_to_message.from_user or not message.reply_to_message.text:
                await message.reply_text("❌ يرجى الرد على الرسالة لإلغاء حظرها.")
                return
            target = message.reply_to_message.from_user
            msg_text = message.reply_to_message.text.strip()[:200]
            await DB.execute("DELETE FROM banned_user_messages WHERE chat_id=? AND user_id=? AND message_text=?",
                             (cid, target.id, msg_text), commit=True)
            await message.reply_text(f"✅ تم إلغاء حظر هذه الرسالة من {target.mention}.")
            return
        if text == "مسح ممنوعاته" or text.startswith("مسح ممنوعاته "):
            tu = await extract_target(message)
            if tu:
                await DB.execute("DELETE FROM banned_user_messages WHERE chat_id=? AND user_id=?", (cid, tu.id), commit=True)
                await message.reply_text(f"✅ تم مسح الرسائل المحظورة للمستخدم {tu.mention}.")
            else:
                await DB.execute("DELETE FROM banned_user_messages WHERE chat_id=?", (cid,), commit=True)
                await message.reply_text("✅ تم مسح جميع الرسائل المحظورة في المجموعة.")
            return
        if text == "مسح جميع الممنوعات":
            bw = await DB.execute("SELECT COUNT(*) FROM banned_words WHERE chat_id=?", (cid,), fetchone=True) or [0]
            bm = await DB.execute("SELECT COUNT(*) FROM banned_user_messages WHERE chat_id=?", (cid,), fetchone=True) or [0]
            if (bw and bw[0]) or (bm and bm[0]):
                await DB.execute("DELETE FROM banned_words WHERE chat_id=?", (cid,), commit=True)
                await DB.execute("DELETE FROM banned_user_messages WHERE chat_id=?", (cid,), commit=True)
                await message.reply_text("تم حذف جميع الممنوعات")
            else:
                await message.reply_text("لا توجد ممنوعات لحذفها")
            return
        if text == "مسح الردود":
            rows = await DB.execute("SELECT 1 FROM custom_replies WHERE chat_id=?", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("• لا يوجد ردود ليتم مسحها")
                return
            await DB.execute("DELETE FROM custom_replies WHERE chat_id=?", (cid,), commit=True)
            await message.reply_text("تم مسح كل الردود")
            return
        if text == "مسح الاوامر المضافه":
            rows = await DB.execute("SELECT original_cmd FROM aliases WHERE chat_id=?", (cid,), fetchall=True)
            if not rows:
                await message.reply_text("لا توجد اوامر مضافه ليتم مسحها")
                return
            await DB.execute("DELETE FROM aliases WHERE chat_id=?", (cid,), commit=True)
            await message.reply_text(f"تم مسح {len(rows)} بنجاح")
            return

    if text == "طرد المحذوفين":
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        cnt = 0
        try:
            async for m in client.get_chat_members(cid):
                if m.user and m.user.is_deleted:
                    try:
                        await client.ban_chat_member(cid, m.user.id)
                        await client.unban_chat_member(cid, m.user.id)
                        cnt += 1
                    except Exception:
                        pass
        except Exception:
            pass
        await message.reply_text(f"• تم طرد ( {cnt} ) حساب محذوف")
        return

    # --- Ban / mute / restrict commands ---
    if text == "طرد" or text.startswith("طرد "):
        kc = await DB.execute("SELECT kick_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if kc and not kc[0]:
            await message.reply_text("❌ أمر الطرد معطل في هذه المجموعة.")
            return
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم عبر الرد أو المعرف/الآيدي الرقمي.")
            return
        if await _check_target_rank(message, t.id, client):
            return
        _, tl = await get_role(cid, t.id, client)
        if sender_level <= tl and sender_level < 10:
            await message.reply_text("❌ لا تملك صلاحية طرد مستخدم مساوٍ أو أعلى منك رتبة.")
            return
        try:
            await client.ban_chat_member(cid, t.id)
            await client.unban_chat_member(cid, t.id)
            await message.reply_text(f"• تم طرده من المجموعه\n• المستخدم ↤︎ {t.mention}")
        except Exception as e:
            await message.reply_text(f"❌ تعذر إتمام عملية الطرد: {e}")
        return

    if text == "حظر" or text.startswith("حظر "):
        ba = await DB.execute("SELECT ban_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ba and not ba[0]:
            await message.reply_text("❌ أمر الحظر معطل في هذه المجموعة.")
            return
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم عبر الرد أو المعرف/الآيدي الرقمي.")
            return
        if await _check_target_rank(message, t.id, client):
            return
        _, tl = await get_role(cid, t.id, client)
        if sender_level <= tl and sender_level < 10:
            await message.reply_text("❌ لا تملك صلاحية حظر مستخدم مساوٍ أو أعلى منك رتبة.")
            return
        try:
            await client.ban_chat_member(cid, t.id)
            await message.reply_text(f"• تم حظره من المجموعه\n• المستخدم ↤︎ {t.mention}")
        except Exception as e:
            await message.reply_text(f"❌ تعذر إتمام عملية الحظر: {e}")
        return

    if text == "كتم" or text.startswith("كتم "):
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم عبر الرد أو المعرف/الآيدي الرقمي.")
            return
        if await _check_target_rank(message, t.id, client):
            return
        _, tl = await get_role(cid, t.id, client)
        if sender_level <= tl and sender_level < 10:
            await message.reply_text("❌ لا تملك صلاحية كتم مستخدم مساوٍ أو أعلى منك رتبة.")
            return
        await DB.execute("INSERT OR IGNORE INTO muted_users (chat_id,user_id) VALUES (?,?)", (cid, t.id), commit=True)
        await message.reply_text(f"• تم كتمه في المجموعه\n• المستخدم ↤︎ {t.mention}")
        return

    if text == "الغاء الكتم" or text.startswith("الغاء الكتم "):
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم عبر الرد أو المعرف/الآيدي الرقمي.")
            return
        await DB.execute("DELETE FROM muted_users WHERE chat_id=? AND user_id=?", (cid, t.id), commit=True)
        await message.reply_text(f"• تم الغاء كتمه من المجموعه\n• المستخدم ↤︎ {t.mention}")
        return

    if text == "تقييد" or text.startswith("تقييد "):
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم عبر الرد أو المعرف/الآيدي الرقمي.")
            return
        if await _check_target_rank(message, t.id, client):
            return
        _, tl = await get_role(cid, t.id, client)
        parts = text.split()
        dur = None
        for i in range(len(parts)-1):
            if parts[i].isdigit() and parts[i+1] in ("دقيقة","دقائق","ساعة","ساعات"):
                dur = int(parts[i]) * (60 if "دقيق" in parts[i+1] else 3600)
                break
        try:
            await client.restrict_chat_member(cid, t.id, ChatPermissions(can_send_messages=False))
            if dur:
                dur_str = f"{parts[parts.index(next(p for p in parts if p.isdigit()))]} {parts[parts.index(next(p for p in parts if p.isdigit()))+1]}"
                await message.reply_text(f"• تم تقييده في المجموعه\n• لرفع التقييد☜  الغاء التقييد\n• لمدة : {dur_str}\n• المستخدم ↤︎ {t.mention}")
                asyncio.create_task(_auto_unrestrict(client, cid, t.id, dur))
            else:
                await message.reply_text(f"• تم تقييده في المجموعه\n• لرفع التقييد☜  الغاء التقييد\n• المستخدم ↤︎ {t.mention}")
        except Exception as e:
            await message.reply_text(f"❌ تعذر التقييد: {e}")
        return

    if text == "الغاء التقييد" or text.startswith("الغاء التقييد "):
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم المقيّد عبر الرد أو المعرف/الآيدي الرقمي.")
            return
        try:
            await client.restrict_chat_member(cid, t.id, ChatPermissions(
                can_send_messages=True, can_send_media_messages=True,
                can_send_other_messages=True, can_add_web_page_previews=True))
            await message.reply_text(f"• تم الغاء تقييده من المجموعه\n• المستخدم ↤︎ {t.mention}")
        except Exception as e:
            await message.reply_text(f"❌ تعذر فك التقييد: {e}")
        return

    if text in ("الغاء الحظر", "رفع القيود") or text.startswith("الغاء الحظر ") or text.startswith("رفع القيود "):
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم عبر الرد أو المعرف/الآيدي.")
            return
        try:
            await client.unban_chat_member(cid, t.id)
            await DB.execute("DELETE FROM muted_users WHERE chat_id=? AND user_id=?", (cid, t.id), commit=True)
            await message.reply_text(f"• تم رفع القيود عن {t.mention}")
        except Exception as e:
            await message.reply_text(f"❌ تعذر إلغاء الحظر: {e}")
        return

    if text == "امسح":
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        de = await DB.execute("SELECT delete_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if de and not de[0]:
            await message.reply_text("❌ أمر امسح معطل في هذه المجموعة.")
            return
        sm = await message.reply_text("🧹 جاري مسح جميع الوسائط في المجموعة...")
        mh = await DB.execute("SELECT message_id FROM media_history WHERE chat_id=?", (cid,), fetchall=True)
        mids = [r[0] for r in mh]
        if not mids:
            try:
                await sm.edit_text("📭 لا توجد وسائط لمسحها.")
            except Exception:
                pass
            return
        dc = 0
        for i in range(0, len(mids), 100):
            try:
                await client.delete_messages(cid, mids[i:i+100])
                dc += len(mids[i:i+100])
            except Exception:
                for mid in mids[i:i+100]:
                    try:
                        await client.delete_messages(cid, [mid])
                        dc += 1
                    except Exception:
                        pass
        await DB.execute("DELETE FROM media_history WHERE chat_id=?", (cid,), commit=True)
        try:
            await sm.edit_text(f"✅ تم مسح {dc} وسائط بنجاح.")
        except Exception:
            pass
        return

    if text == "مسح":
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        if not message.reply_to_message:
            await message.reply_text("❌ يرجى الرد على الرسالة المراد مسحها.")
            return
        try:
            await client.delete_messages(cid, [message.reply_to_message.id, message.id])
        except Exception:
            try:
                await client.delete_messages(cid, [message.reply_to_message.id])
                await message.reply_text("✅ تم مسح الرسالة بنجاح.")
            except Exception as e:
                await message.reply_text(f"❌ تعذر مسح الرسالة: {e}")
        return

    if text == "اطردني":
        km = await DB.execute("SELECT kickme_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if km and not km[0]:
            await message.reply_text("❌ أمر اطردني معطل في هذه المجموعة.")
            return
        try:
            await client.ban_chat_member(cid, uid)
            await client.unban_chat_member(cid, uid)
            await message.reply_text("✅ تم طردك من المجموعة.")
        except Exception as e:
            await message.reply_text(f"❌ تعذر طردك: {e}")
        return

    if text == "نزلني":
        ur = await DB.execute("SELECT unrankme_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ur and not ur[0]:
            await message.reply_text("❌ أمر نزلني معطل في هذه المجموعة.")
            return
        rk, _ = await get_role(cid, uid, client)
        if rk in ("member",):
            await message.reply_text("❌ أنت عضو بالفعل وليس لديك رتبة لتنزيلها.")
            return
        await DB.execute("DELETE FROM ranks WHERE chat_id=? AND user_id=?", (cid, uid), commit=True)
        await message.reply_text("✅ تم تنزيل جميع رتبك بنجاح.")
        return

    if text in ("تحذير", "انذار") or text.startswith("تحذير ") or text.startswith("انذار "):
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        wa = await DB.execute("SELECT warn_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if wa and not wa[0]:
            await message.reply_text("❌ نظام التحذيرات معطل في هذه المجموعة حالياً.")
            return
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم المستهدف بالرد أو المنشن/الآيدي.")
            return
        _, tl = await get_role(cid, t.id, client)
        if tl >= 1:
            await message.reply_text("❌ هذا الأمر ينطبق على الأعضاء فقط، ولا يمكن تحذير من يملك رتبة مميز فما فوق.")
            return
        await DB.execute("INSERT INTO warnings (chat_id,user_id,count) VALUES (?,?,1) ON CONFLICT DO UPDATE SET count=count+1", (cid, t.id), commit=True)
        c = (await DB.execute("SELECT count FROM warnings WHERE chat_id=? AND user_id=?", (cid, t.id), fetchone=True) or [1])[0]
        if c >= 3:
            await DB.execute("DELETE FROM warnings WHERE chat_id=? AND user_id=?", (cid, t.id), commit=True)
            await DB.execute("INSERT OR IGNORE INTO muted_users (chat_id,user_id) VALUES (?,?)", (cid, t.id), commit=True)
            await message.reply_text(f"🚫 تلقى {t.mention} ثلاثة تحذيرات وتم كتمه تلقائياً.")
        else:
            await message.reply_text(f"⚠️ تم تحذير {t.mention} (التحذير {c}/3).")
        return

    if text == "انذاراته" and sender_level >= 2:
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم بالرد أو المعرف/الآيدي.")
            return
        wc = (await DB.execute("SELECT count FROM warnings WHERE chat_id=? AND user_id=?", (cid, t.id), fetchone=True) or [0])[0]
        await message.reply_text(f"⚠️ عدد إنذارات {t.mention}: {wc}/3.")
        return

    if text == "مسح انذاراته" and sender_level >= 2:
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم بالرد أو المعرف/الآيدي.")
            return
        wc = await DB.execute("SELECT count FROM warnings WHERE chat_id=? AND user_id=?", (cid, t.id), fetchone=True)
        if not wc or not wc[0]:
            await message.reply_text(f"لا توجد انذارت على {t.mention}")
            return
        await DB.execute("DELETE FROM warnings WHERE chat_id=? AND user_id=?", (cid, t.id), commit=True)
        await message.reply_text(f"تم مسح جميع انذارات {t.mention}")
        return

    if text == "تثبيت":
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        if not message.reply_to_message:
            await message.reply_text("❌ يرجى استخدام هذا الأمر بالرد على الرسالة المراد تثبيتها.")
            return
        try:
            chat = await client.get_chat(cid)
            if chat.permissions and not chat.permissions.can_pin_messages:
                await message.reply_text("❌ تثبيت الرسائل معطل في المجموعة حالياً.")
                return
        except Exception:
            pass
        nr = await DB.execute("SELECT lock_notifications FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        silent = nr and nr[0] == 1
        try:
            await client.pin_chat_message(cid, message.reply_to_message.id, disable_notification=silent)
            await message.reply_text("✅ تم تثبيت الرسالة بنجاح داخل الكروب.")
        except Exception as e:
            await message.reply_text(f"❌ تعذر تثبيت الرسالة: {e}")
        return

    # --- Role management ---
    if text.startswith("رفع ") and sender_level >= 3:
        pr = await DB.execute("SELECT promote_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if pr and not pr[0]:
            await message.reply_text("❌ أمر الرفع معطل في هذه المجموعة.")
            return
        after = text[4:].strip()
        matched = None
        for key in sorted(ROLE_MAPPING, key=len, reverse=True):
            if after.startswith(key):
                matched = ROLE_MAPPING[key]
                break
        if matched:
            t = await extract_target(message)
            if not t:
                await message.reply_text("❌ يرجى تحديد المستخدم عبر الرد أو المعرف/الآيدي الرقمي.")
                return
            await change_rank(message, t.id, matched, True)
            return

    if text.startswith("تنزيل ") and any(k in text for k in ("مميز","ادمن","مدير","منشئ","مطور","مالك")) and sender_level >= 3:
        dm = await DB.execute("SELECT demote_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if dm and not dm[0]:
            await message.reply_text("❌ أمر التنزيل معطل في هذه المجموعة.")
            return
        after = text[6:].strip()
        matched = None
        for key in sorted(ROLE_MAPPING, key=len, reverse=True):
            if after.startswith(key):
                matched = ROLE_MAPPING[key]
                break
        if matched:
            t = await extract_target(message)
            if not t:
                await message.reply_text("❌ يرجى تحديد المستخدم عبر الرد أو المعرف/الآيدي الرقمي.")
                return
            await change_rank(message, t.id, matched, False)
            return

    if text == "تنزيل الكل" and sender_level >= 9:
        await DB.execute("DELETE FROM ranks WHERE chat_id=?", (cid,), commit=True)
        await message.reply_text("✅ تم تنزيل جميع الأعضاء وإلغاء كافة رتبهم المخزنة بالمجموعة بنجاح.")
        return

    if (text == "تنزيل" or text.startswith("تنزيل ")) and sender_level >= 3:
        dm = await DB.execute("SELECT demote_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if dm and not dm[0]:
            await message.reply_text("❌ أمر التنزيل معطل في هذه المجموعة.")
            return
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم بالرد أو بالتاك/المعرف للقيام بعملية تنزيل رتبته.")
            return
        await change_rank(message, t.id, None, False)
        return

    if text == "رسائلي":
        mc = (await DB.execute("SELECT count FROM messages_count WHERE chat_id=? AND user_id=?", (cid, uid), fetchone=True) or [0])[0]
        await message.reply_text(f"💬 عدد رسائلك في هذه المجموعة: **{mc}** رسالة.")
        return

    # --- Points ---
    if text == "نقاطي":
        pr = (await DB.execute("SELECT points FROM user_points WHERE chat_id=? AND user_id=?", (cid, uid), fetchone=True) or [0])[0]
        await message.reply_text(f"🎯 رصيد نقاطك الحالي في هذه المجموعة هو: **{pr}** نقطة.")
        return

    # --- Nida ---
    if text == "نداء" and sender_level >= 2:
        members = []
        try:
            async for m in client.get_chat_members(cid):
                if m.user and not m.user.is_bot and not m.user.is_deleted and m.user.id != uid:
                    members.append(m.user)
        except Exception:
            pass
        if not members:
            await message.reply_text("🔍 لم يتم العثور على أعضاء للنداء.")
            return
        r = random.choice(members)
        ph = random.choice([
            "وين طامس يحلو", "تعال نورنا وسولف معنا يا غالي",
            "اشتقنا لطلتك الحلوة هنا", "الكروب مظلم بدونك يا قمرنا",
            "وينك غايب يا عسل؟ طمنا عنك", "طلتك علينا تسوى الدنيا وما فيها",
            "يا حلو شاركنا الكلام ولا تضل غايب", "أجمل كيمياء بالكروب تبدأ بحضورك البهي",
            "وين هالغيبة يا وردة الكروب؟", "سولف معنا يالجميل وخلي اليوم يسعد بقربك",
            "مكانك فارغ بالكروب يا غالي لا تطول الغيبة", "منور الكروب بحروفك دائماً لا تحرمنا من هالنور",
            "تعال سولف وخلي الضحكة تملأ المكان يا عسل", "يا ضحكة الكروب وبسمته وين طامس اليوم؟",
            "حضورك يسعدنا وغيابك يتعبنا يا بطل"
        ])
        await message.reply_text(f"{ph} {r.mention}")
        return

    # --- Delete my messages ---
    if text == "مسح رسائلي":
        sm = await message.reply_text("🧹 جاري فحص ومسح رسائلك السابقة بالكامل من المجموعة...")
        rows = await DB.execute(
            "SELECT message_id FROM user_messages WHERE chat_id=? AND user_id=? ORDER BY message_id DESC LIMIT 300",
            (cid, uid), fetchall=True)
        if not rows:
            try:
                await sm.edit_text("✅ لم يتم العثور على رسائل سابقة لك في المجموعة.")
                await asyncio.sleep(3)
                await sm.delete()
            except Exception:
                pass
            return
        mids = [r[0] for r in rows if r[0] != sm.id]
        cnt = 0
        for i in range(0, len(mids), 100):
            chunk = mids[i:i+100]
            try:
                await client.delete_messages(cid, chunk)
                cnt += len(chunk)
                await DB.execute(
                    "DELETE FROM user_messages WHERE chat_id=? AND message_id IN ({})".format(
                        ",".join("?" for _ in chunk)),
                    (cid,) + tuple(chunk), commit=True)
                await DB.execute(
                    "DELETE FROM media_history WHERE chat_id=? AND message_id IN ({})".format(
                        ",".join("?" for _ in chunk)),
                    (cid,) + tuple(chunk), commit=True)
            except Exception:
                for mid in chunk:
                    try:
                        await client.delete_messages(cid, [mid])
                        cnt += 1
                        await DB.execute("DELETE FROM user_messages WHERE chat_id=? AND message_id=?", (cid, mid), commit=True)
                        await DB.execute("DELETE FROM media_history WHERE chat_id=? AND message_id=?", (cid, mid), commit=True)
                    except Exception:
                        pass
        try:
            await sm.edit_text(f"✅ تم مسح {cnt} من رسائلك بنجاح.")
            await asyncio.sleep(3)
            await sm.delete()
        except Exception:
            pass
        return

    # --- Poetry ---
    if text == "شعر":
        await message.reply_text(f"📜 **من عيون الشعر العربي:**\n\n{random.choice(POETRY_DATA)}")
        return

    # --- Games ---
    if text in ("كت", "سؤال"):
        ga = await DB.execute("SELECT games_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ga and not ga[0]:
            await message.reply_text("❌ الألعاب معطلة في هذه المجموعة.")
            return
        ar = await DB.execute("SELECT ask_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ar and not ar[0]:
            await message.reply_text("❌ أمر كت معطل في هذه المجموعة.")
            return
        await message.reply_text(f"💬 **سؤال عشوائي للتفكير:**\n\n⇜ {random.choice(GAMES_DATA['questions'])}\nشاركنا إجابتك في المجموعة!")
        return
    if text in ("جمل", "جملة"):
        ga = await DB.execute("SELECT games_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ga and not ga[0]:
            await message.reply_text("❌ الألعاب معطلة في هذه المجموعة.")
            return
        s = random.choice(GAMES_DATA["sentences"])
        active_games[cid] = {"type": "جمل", "answer": s}
        await message.reply_text(f"📝 **لعبة الجمل المشوشة:**\n\n⇜ أعد كتابة هذه الجملة كاملة:\n`{s.replace(' ','')}`\n\nاكتب الجواب الصحيح لتفوز بـ 5 نقاط!")
        return
    if text in ("اعلام", "أعلام", "علم"):
        ga = await DB.execute("SELECT games_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ga and not ga[0]:
            await message.reply_text("❌ الألعاب معطلة في هذه المجموعة.")
            return
        f = random.choice(GAMES_DATA["flags"])
        active_games[cid] = {"type": "اعلام", "answer": f["ans"]}
        await message.reply_text(f"🌍 **لعبة الأعلام:**\n\n⇜ ما اسم الدولة لهذا العلم؟ {f['emoji']}\nاكتب اسم الدولة لتفوز بـ 5 نقاط!")
        return
    if text == "ترتيب":
        ga = await DB.execute("SELECT games_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ga and not ga[0]:
            await message.reply_text("❌ الألعاب معطلة في هذه المجموعة.")
            return
        w = random.choice(GAMES_DATA["scramble_words"])
        s = list(w)
        random.shuffle(s)
        active_games[cid] = {"type": "ترتيب", "answer": w}
        await message.reply_text(f"🔤 **لعبة ترتيب الحروف:**\n\n⇜ رتب الحروف التالية لتكوين كلمة صحيحة:\n`{' '.join(s)}`\n\nاكتب الكلمة الصحيحة لتفوز بـ 5 نقاط!")
        return
    if text == "تفكيك":
        ga = await DB.execute("SELECT games_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ga and not ga[0]:
            await message.reply_text("❌ الألعاب معطلة في هذه المجموعة.")
            return
        i = random.choice(GAMES_DATA["disassemble"])
        active_games[cid] = {"type": "تفكيك", "answer": i["decomp"]}
        await message.reply_text(f"🧩 **لعبة تفكيك الكلمة:**\n\n⇜ قم بتفكيك الكلمة التالية بوضع مسافة بين كل حرف:\n`{i['word']}`\nمثال: `ا ن ت ه ى`\nاكتب الحروف المفككة لتفوز بـ 5 نقاط!")
        return
    if text == "عواصم":
        ga = await DB.execute("SELECT games_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ga and not ga[0]:
            await message.reply_text("❌ الألعاب معطلة في هذه المجموعة.")
            return
        i = random.choice(GAMES_DATA["capitals"])
        active_games[cid] = {"type": "عواصم", "answer": i["capital"]}
        await message.reply_text(f"🏛️ **لعبة العواصم:**\n\n⇜ ما هي عاصمة دولة **{i['country']}**؟\nاكتب اسم العاصمة لتفوز بـ 5 نقاط!")
        return
    if text == "حزورة":
        ga = await DB.execute("SELECT games_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ga and not ga[0]:
            await message.reply_text("❌ الألعاب معطلة في هذه المجموعة.")
            return
        r = random.choice(GAMES_DATA["riddles"])
        active_games[cid] = {"type": "حزورة", "answer": r["a"]}
        await message.reply_text(f"🧩 **لعبة الحزورة:**\n\n⇜ {r['q']}\nاكتب الجواب الصحيح لتفوز بـ 5 نقاط!")
        return

    if text == "لغز":
        ga = await DB.execute("SELECT games_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ga and not ga[0]:
            await message.reply_text("❌ الألعاب معطلة في هذه المجموعة.")
            return
        msg = await message.reply_text("🤔 جاري تحضير اللغز...")
        ai_resp = await _ask_ai("أنشئ لغزاً عربياً قصيراً (سطرين) مع 2-4 خيارات. أعد النتيجة بهذا التنسيق بالضبط:\nسؤال: <نص اللغز>\nخيارات: <خيار1> | <خيار2> | <خيار3> | <خيار4>\nجواب: <رقم الخيار الصحيح من 1>")
        if not ai_resp:
            await msg.edit_text("❌ تعذر تحضير اللغز حالياً، حاول مرة أخرى.")
            return
        lines = ai_resp.split("\n")
        question = ""
        options = []
        correct = 0
        for line in lines:
            if line.startswith("سؤال:") or line.startswith("سؤال:"):
                question = line.split(":", 1)[1].strip()
            elif line.startswith("خيارات:") or line.startswith("خيارات:"):
                opts_str = line.split(":", 1)[1].strip()
                options = [o.strip() for o in opts_str.split("|") if o.strip()]
            elif line.startswith("جواب:") or line.startswith("جواب:"):
                try:
                    correct = int(line.split(":", 1)[1].strip()) - 1
                except ValueError:
                    correct = 0
        if not question or len(options) < 2:
            await msg.edit_text("❌ فشل في فهم اللغز، حاول مرة أخرى.")
            return
        if correct >= len(options):
            correct = 0
        active_games[cid] = {"type": "لغز", "correct": correct}
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(o, callback_data=f"lz_{cid}_{i}")] for i, o in enumerate(options)])
        await msg.edit_text(f"🧩 **لغز:**\n\n{question}", reply_markup=kb)
        return

    if text == "اسئلني":
        ga = await DB.execute("SELECT games_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ga and not ga[0]:
            await message.reply_text("❌ الألعاب معطلة في هذه المجموعة.")
            return
        msg = await message.reply_text("🤔 جاري تحضير السؤال...")
        ai_resp = await _ask_ai("أنشئ سؤالاً ثقافياً أو تاريخياً أو علمياً بالعربية مع 3-4 خيارات. أعد النتيجة بهذا التنسيق بالضبط:\nسؤال: <نص السؤال>\nخيارات: <خيار1> | <خيار2> | <خيار3> | <خيار4>\nجواب: <رقم الخيار الصحيح من 1>")
        if not ai_resp:
            await msg.edit_text("❌ تعذر تحضير السؤال حالياً، حاول مرة أخرى.")
            return
        lines = ai_resp.split("\n")
        question = ""
        options = []
        correct = 0
        for line in lines:
            if line.startswith("سؤال:") or line.startswith("سؤال:"):
                question = line.split(":", 1)[1].strip()
            elif line.startswith("خيارات:") or line.startswith("خيارات:"):
                opts_str = line.split(":", 1)[1].strip()
                options = [o.strip() for o in opts_str.split("|") if o.strip()]
            elif line.startswith("جواب:") or line.startswith("جواب:"):
                try:
                    correct = int(line.split(":", 1)[1].strip()) - 1
                except ValueError:
                    correct = 0
        if not question or len(options) < 2:
            await msg.edit_text("❌ فشل في فهم السؤال، حاول مرة أخرى.")
            return
        if correct >= len(options):
            correct = 0
        active_games[cid] = {"type": "اسئلني", "correct": correct}
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(o, callback_data=f"sq_{cid}_{i}")] for i, o in enumerate(options)])
        await msg.edit_text(f"❓ **سؤال:**\n\n{question}", reply_markup=kb)
        return

    if text == "محيبس":
        ga = await DB.execute("SELECT games_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ga and not ga[0]:
            await message.reply_text("❌ الألعاب معطلة في هذه المجموعة.")
            return
        correct_hand = random.randint(0, 5)
        active_games[cid] = {"type": "محيبس", "correct": correct_hand, "opened": set()}
        kb = _mh_kb(cid, active_games[cid])
        await message.reply_text("🎲 **أهلاً بك في لعبة المحيبس!**\n\nعليك تخمين المحيبس في أي يد للفوز بـ 5 نقاط 👊", reply_markup=kb)
        return

    if text == "ايموجي":
        ga = await DB.execute("SELECT games_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ga and not ga[0]:
            await message.reply_text("❌ الألعاب معطلة في هذه المجموعة.")
            return
        if cid in emoji_games:
            await message.reply_text("⚠️ توجد لعبة إيموجي نشطة بالفعل في هذه المجموعة!")
            return
        emoji_games[cid] = {
            "players": [{"id": uid, "name": message.from_user.first_name or "لاعب"}, None, None, None],
            "phase": "registering",
            "msg_id": None
        }
        kb = _emj_kb(cid, emoji_games[cid])
        msg = await message.reply_text("🎮 **لعبة الإيموجي!**\n\nاضغط على الأزرار للتسجيل (مطلوب 4 لاعبين):", reply_markup=kb)
        emoji_games[cid]["msg_id"] = msg.id
        return

    if text in ("الالعاب", "الألعاب", "الالالعاب"):
        await message.reply_text(GAMES_LIST.strip())
        return

    # --- Rank ---
    if text == "رتبتي":
        rk, _ = await get_role(cid, uid, client)
        rn = ROLE_ARABIC.get(rk, "عضو")
        cr = await DB.execute("SELECT rank_title FROM custom_ranks WHERE chat_id=? AND user_id=?", (cid, uid), fetchone=True)
        if cr:
            await message.reply_text(f"🏷️ رتبتك الأمنية: **{rn}**\n🎖️ لقبك الخاص الممنوح: **{cr[0]}**")
        else:
            await message.reply_text(f"🏷️ رتبتك الأمنية: **{rn}**")
        return

    # --- ID card ---
    if text in ("ايدي", "الايدي") or text.startswith("ايدي ") or text.startswith("الايدي "):
        ida = await DB.execute("SELECT id_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ida and not ida[0]:
            await message.reply_text("❌ عذراً، أمر الايدي معطل في هذه المجموعة حالياً.")
            return
        tu = await extract_target(message) or message.from_user
        mc = (await DB.execute("SELECT count FROM messages_count WHERE chat_id=? AND user_id=?", (cid, tu.id), fetchone=True) or [0])[0]
        pf = None
        try:
            async for p in client.get_chat_photos(tu.id, limit=1):
                pf = p.file_id
        except Exception:
            pass
        cy = estimate_creation_year(tu.id)
        us = await _get_usernames(client, tu.id, tu)
        sr = (await DB.execute("SELECT id_style FROM groups WHERE chat_id=?", (cid,), fetchone=True) or [1])[0]
        pr = (await DB.execute("SELECT id_photo_active FROM groups WHERE chat_id=?", (cid,), fetchone=True) or [1])[0]
        sp = pr != 0

        if sr == 1:
            card = f"👤 **بطاقة البيانات الشخصية للمستخدم:**\n\n🏷️ الاسم: {tu.mention}\n🆔 رقم الحساب (ID): `{tu.id}`\n🌐 المعرفات: {us}\n💬 عدد الرسائل المرسلة: `{mc}`\n📅 التقدير التقريبي لإنشاء الحساب: `{cy}`"
        elif sr == 2:
            card = f"🌐 **[ ACCOUNT SECURITY CARD ]** 🌐\n━━━━━━━━━━━━━━━━━━━\n👤 الاسم ⇽ {tu.mention}\n🆔 الآيدي ⇽ `{tu.id}`\n💎 اليوزرات ⇽ {us}\n💬 التفاعل ⇽ `{mc}` رسالة\n📆 تاريخ الإنشاء ⇽ `{cy}`\n━━━━━━━━━━━━━━━━━━━"
        elif sr == 3:
            card = f"⚜️ **بطاقة العضو** ⚜️\n\n✨ الـنـقـي: {tu.mention}\n📎 الـمـعـرّف الـرقـمـي: `{tu.id}`\n🌍 الـرّابـط الـعـلـمـي: {us}\n📈 نـسـبـة الـحـضـور: `{mc}` رسالة\n🕰️ الـتـأسـيـس: `{cy}`"
        elif sr == 4:
            card = f"▫️ **ID CARD** ▫️\n\n▪️ User: {tu.mention}\n▪️ ID: `{tu.id}`\n▪️ Handles: {us}\n▪️ Messages: `{mc}`\n▪️ Year: `{cy}`"
        elif sr == 5:
            card = f"▫️ **USER CARD** ▫️\n━━━━━━━━━━━━━━━━━━━\n👤 User     : {tu.mention}\n🆔 ID       : `{tu.id}`\n🌐 Handles  : {us}\n💬 Messages : `{mc}`\n📅 Created  : {cy}\n━━━━━━━━━━━━━━━━━━━"
        elif sr == 6:
            card = f"▫️ **بطاقة المستخدم** ▫️\n━━━━━━━━━━━━━━━━━━━\n👤 الاسم    : {tu.mention}\n🆔 الايدي   : `{tu.id}`\n🌐 المعرفات : {us}\n💬 الرسائل  : `{mc}`\n📅 السنة    : {cy}\n━━━━━━━━━━━━━━━━━━━"
        elif sr == 7:
            card = f"╔══════ PROFILE ══════╗\n👤 User     : {tu.mention}\n🆔 ID       : `{tu.id}`\n🌐 Handles  : {us}\n💬 Messages : `{mc}`\n📅 Created  : {cy}\n╚══════════════════════╝"
        else:
            card = f"📇 {tu.mention}\n🆔 `{tu.id}` • 💬 `{mc}`\n🌐 {us}\n📅 {cy}"

        if pf and sp:
            try:
                sm = await message.reply_photo(pf, caption=card)
                await DB.execute("INSERT OR IGNORE INTO media_history (chat_id,message_id) VALUES (?,?)", (cid, sm.id), commit=True)
            except Exception:
                await message.reply_text(card)
        else:
            await message.reply_text(card)
        return

    # --- Welcome / Rules / Aliases ---
    if text == "تعيين الترحيب" and sender_level >= 4:
        conv_states[cid] = {"user_id": uid, "state": "waiting_welcome"}
        await message.reply_text("💬 حسناً، أرسل الآن رسالة الترحيب التي ترغب بظهورها عند انضمام الأعضاء:")
        return

    if text == "الترحيب" and sender_level >= 2:
        wa = await DB.execute("SELECT welcome_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if wa and not wa[0]:
            await message.reply_text("❌ أمر الترحيب معطل في هذه المجموعة حالياً.")
            return
        row = await DB.execute("SELECT welcome_msg FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        w = row[0] if row and row[0] else "👋 أهلاً بك في المجموعة! يسعدنا انضمامك إلينا."
        await message.reply_text(w)
        return

    if text == "تعيين القوانين" and sender_level >= 4:
        conv_states[cid] = {"user_id": uid, "state": "waiting_rules"}
        await message.reply_text("📜 حسناً، أرسل القوانين والتعليمات العامة التي ترغب بتثبيتها:")
        return

    if text == "القوانين":
        row = await DB.execute("SELECT rules FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        await message.reply_text(row[0] if row and row[0] else "📜 لا توجد قوانين رسمية مسجلة لهذه المجموعة بعد.")
        return

    if text in ("اضافة امر", "اضف امر") and sender_level >= 4:
        conv_states[cid] = {"user_id": uid, "state": "waiting_alias_old"}
        await message.reply_text("💬 ارسل الآن الأمر القديم (الأساسي) المراد استبداله:")
        return

    if text in ("مسح امر", "حذف امر") and sender_level >= 4:
        conv_states[cid] = {"user_id": uid, "state": "waiting_alias_delete"}
        await message.reply_text("🗑️ أرسل الآن الكلمة البديلة التي ترغب بإزالتها من قاعدة بيانات الاختصارات:")
        return

    if text == "الاوامر" and sender_level >= 2:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("1 ◂", callback_data=f"c1_{uid}"), InlineKeyboardButton("2 ◂", callback_data=f"c2_{uid}"), InlineKeyboardButton("3 ◂", callback_data=f"c3_{uid}")],
            [InlineKeyboardButton("4 ◂", callback_data=f"c4_{uid}"), InlineKeyboardButton("5 ◂", callback_data=f"c5_{uid}"), InlineKeyboardButton("6 ◂", callback_data=f"c6_{uid}")]
        ])
        await message.reply_text(
            "‌‌‏أهلاً بك عزيزي في قائمة الاوامر :\n"
            "━━━━━━━━━━━━━━━━\n"
            " ◂ 1 : اوامر الادمنيه ، الرفع ، المسح\n"
            " ◂ 2 : اوامر رؤية الاعدادات ، وضع الاعدادات\n"
            " ◂ 3 : اوامر القفل ، الحماية ، الردود\n"
            " ◂ 4 : اوامر التفعيل ، التثبيت ، المنشن\n"
            " ◂ 5 : اوامر التسليه ، الزواج ، التنظيف\n"
            " ◂ 6 :اوامر الخدميه ، الاشتراك الاجباري\n"
            "• لـرؤيـة قائمة الالعاب اكتب : الالعاب\n"
            "━━━━━━━━━━━━━━━━",
            reply_markup=kb
        )
        return

    if text == "ترتيب الاوامر" and sender_level >= 3:
        await DB.execute("UPDATE groups SET aliases_active=1 WHERE chat_id=?", (cid,), commit=True)
        lines = ["- تم ترتيب الاوامر بالشكل التالي ."]
        for shortcut, target in sorted(PREDEFINED_ALIASES.items(), key=lambda x: x[1]):
            lines.append(f"- {target} - {shortcut} .")
        await message.reply_text("\n".join(lines))
        return

    if text == "تعطيل ترتيب الاوامر" and sender_level >= 3:
        await DB.execute("UPDATE groups SET aliases_active=0 WHERE chat_id=?", (cid,), commit=True)
        await _reply_toggle(message, "تعطيل", "ترتيب الاوامر")
        return

    if text in ("اضف رد", "أضف رد") and sender_level >= 2:
        ra = await DB.execute("SELECT replies_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ra and not ra[0]:
            await message.reply_text("❌ الردود معطلة في هذه المجموعة.")
            return
        conv_states[cid] = {"user_id": uid, "state": "waiting_reply_keyword"}
        await message.reply_text("• حسناً , الان ارسل كلمه الرد \n• لألغاء الأمر ارسل ☜ الغاء")
        return

    if text in ("حذف رد", "مسح رد") and sender_level >= 2:
        conv_states[cid] = {"user_id": uid, "state": "waiting_reply_delete"}
        await message.reply_text("🗑️ أرسل الكلمة التي تريد حذف ردها المخصص:")
        return

    if text in ("الردود", "عرض الردود") and sender_level >= 2:
        rows = await DB.execute("SELECT keyword, reply_type FROM custom_replies WHERE chat_id=?", (cid,), fetchall=True) or []
        if not rows:
            await message.reply_text("📭 لا توجد ردود مخصصة مسجلة في هذه المجموعة حالياً.")
            return
        icons = {"text": "📝", "photo": "🖼️", "video": "🎬", "animation": "🎞️", "voice": "🎤", "audio": "🎵", "document": "📄", "sticker": "🏷️"}
        await message.reply_text("📋 **قائمة الردود المخصصة في المجموعة:**\n\n" + "\n".join(f"{icons.get(r, '📄')} `{k}`" for k, r in rows))
        return

    if text == "مسح الرتب" and uid == OWNER_ID:
        cnt = (await DB.execute("SELECT COUNT(*) FROM ranks WHERE chat_id=?", (cid,), fetchone=True) or [0])[0]
        if cnt:
            await DB.execute("DELETE FROM ranks WHERE chat_id=?", (cid,), commit=True)
            await message.reply_text(f"✅ تم مسح وتصفير كافة سجلات الرتب المخزنة للمجموعة ({cnt} رتبة).")
        else:
            await message.reply_text("❌ لا يوجد رتب مسجلة في قاعدة بيانات هذه المجموعة لحذفها.")
        return

    if text in ("بوت", "روز"):
        await message.reply_text(random.choice(WELCOME_BOT_PHRASES))
        return

    if text == "ترند":
        tr = await DB.execute("SELECT trend_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if tr and not tr[0]:
            await message.reply_text("❌ أمر الترند معطل في هذه المجموعة.")
            return
        rows = await DB.execute(
            "SELECT user_id, count FROM messages_count WHERE chat_id=? ORDER BY count DESC LIMIT 10",
            (cid,), fetchall=True)
        if not rows:
            await message.reply_text("📭 لا توجد بيانات ترند بعد.")
            return
        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for i, (uid, cnt) in enumerate(rows):
            medal = medals[i] if i < 3 else f"{i+1}."
            try:
                u = await client.get_users(uid)
                uname = f"@{u.username}" if u.username else u.mention
            except Exception:
                uname = f"`{uid}`"
            lines.append(f"{medal} {uname} ({cnt} رسالة)")
        await message.reply_text("📊 **الترند:**\n" + "\n".join(lines))
        return

    if text == "تصفير الترند":
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        await DB.execute("DELETE FROM messages_count WHERE chat_id=?", (cid,), commit=True)
        await message.reply_text("✅ تم تصفير الترند في المجموعة.")
        return

    if text == "همسه":
        wa = await DB.execute("SELECT whisper_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if wa and not wa[0]:
            await message.reply_text("❌ الهمسات معطلة في هذه المجموعة.")
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("❌ يرجى الرد على رسالة الشخص الذي تريد إرسال الهمسة له.")
            return
        target = message.reply_to_message.from_user
        if target.id == uid:
            await message.reply_text("❌ لا يمكنك إرسال همسة لنفسك.")
            return
        if target.is_bot:
            await message.reply_text("❌ لا يمكنك إرسال همسة لبوت.")
            return
        sender_name = message.from_user.first_name or "المستخدم"
        target_name = target.first_name or "المستخدم"
        tid = target.id
        cur = await DB.execute(
            "INSERT INTO whispers (chat_id, sender_id, target_id, target_name, sender_name) VALUES (?,?,?,?,?)",
            (cid, uid, tid, target_name, sender_name), commit=True
        )
        wid = cur.lastrowid
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("• اضغط هنا لأكمال الهمسه•", url=f"https://t.me/{_whisper_bot_username}?start=whisper_{wid}_{cid}_{uid}_{tid}")]
        ])
        await message.reply_text("• اضغط اسفل لاكمال الهمسة", reply_markup=kb)
        return

    if text.startswith("شات "):
        q = text[4:].strip()
        if not q:
            await message.reply_text("❌ يرجى كتابة سؤال بعد الأمر.\nمثال: شات الموناليزا")
            return
        msg = await message.reply_text("🤔 جاري البحث عن الإجابة...")
        answer = await _ask_ai(q)
        if answer:
            await msg.edit_text(f"🤖 {answer}")
        else:
            await msg.edit_text("❌ تعذر الحصول على إجابة، حاول لاحقاً")
        return

    if text == "روز غادري":
        if uid != OWNER_ID and sender_level < 9:
            return
        await message.reply_text("✅ وداعاً!")
        await client.leave_chat(cid)
        return

    if (text == "كشف القيود" or text.startswith("كشف القيود ")) and sender_level >= 2:
        rv = await DB.execute("SELECT reveal_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if rv and not rv[0]:
            await message.reply_text("❌ أمر الكشف معطل في هذه المجموعة.")
            return
        tu = await extract_target(message)
        if not tu:
            await message.reply_text("❌ يرجى تحديد المستخدم بالرد أو المعرف/الآيدي.")
            return
        muted = await DB.execute("SELECT user_id FROM muted_users WHERE chat_id=? AND user_id=?", (cid, tu.id), fetchone=True)
        wrn = (await DB.execute("SELECT count FROM warnings WHERE chat_id=? AND user_id=?", (cid, tu.id), fetchone=True) or [0])[0]
        msg_bans = await DB.execute("SELECT COUNT(*) FROM banned_user_messages WHERE chat_id=? AND user_id=?", (cid, tu.id), fetchone=True)
        ban_count = msg_bans[0] if msg_bans else 0
        is_restricted = False
        is_banned = False
        try:
            mem = await client.get_chat_member(cid, tu.id)
            if mem.status == ChatMemberStatus.RESTRICTED:
                is_restricted = True
            elif mem.status == ChatMemberStatus.BANNED:
                is_banned = True
        except Exception:
            pass
        lines = [
            f"🔍 **كشف القيود:** {tu.mention}\n",
            f"{'🔇' if muted else '✅'} المكتوم: {'مكتوم' if muted else 'غير مكتوم'}",
            f"{'⛔' if is_restricted else '✅'} المقيد: {'مقيد' if is_restricted else 'غير مقيد'}",
            f"{'🚫' if is_banned else '✅'} المحظور: {'محظور' if is_banned else 'غير محظور'}",
            f"⚠️ الانذارات: {wrn}",
            f"📝 الرسائل الممنوعة: {ban_count}"
        ]
        await message.reply_text("\n".join(lines))
        return

    if text in ("كشف",) or text.startswith("كشف "):
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم بالرد أو المعرف/الآيدي.")
            return
        us = await _get_usernames(client, t.id, t)
        rk, _ = await get_role(cid, t.id, client)
        rn = ROLE_ARABIC.get(rk, "عضو")
        pt = (await DB.execute("SELECT points FROM user_points WHERE chat_id=? AND user_id=?", (cid, t.id), fetchone=True) or [0])[0]
        ms = (await DB.execute("SELECT count FROM messages_count WHERE chat_id=? AND user_id=?", (cid, t.id), fetchone=True) or [0])[0]
        await message.reply_text(f"🔍 **كشف بيانات العضو:**\n\n👤 الاسم: {t.mention}\n🆔 الآيدي: `{t.id}`\n🌐 المعرفات: {us}\n🏷️ الرتبة: {rn}\n💬 الرسائل: {ms}\n⭐ النقاط: {pt}")
        return

    if text == "انشاء رابط" and sender_level >= 3:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 رابط انضمام مباشر", callback_data="cdl")],
            [InlineKeyboardButton("📩 رابط طلبات انضمام", callback_data="crl")]
        ])
        await message.reply_text("🔗 **إنشاء رابط للمجموعة:**\nاختر نوع الرابط الذي تريد إنشاءه:", reply_markup=kb)
        return

    if text == "الرابط":
        la = await DB.execute("SELECT link_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if la and not la[0]:
            await message.reply_text("❌ أمر الرابط معطل في هذه المجموعة حالياً.")
            return
        try:
            ci = await client.get_chat(cid)
            lnk = ci.invite_link or (f"https://t.me/{ci.username}" if ci.username else None)
            if lnk:
                await message.reply_text(f"🔗 **رابط المجموعة:**\n{lnk}")
            else:
                kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 رابط مباشر", callback_data="cdl")],
                    [InlineKeyboardButton("📩 رابط طلبات", callback_data="crl")]
                ])
                await message.reply_text("📎 **لا يوجد رابط للمجموعة حالياً، يمكنك إنشاء واحد:**", reply_markup=kb)
        except Exception as e:
            await message.reply_text(f"❌ تعذر جلب الرابط: {e}")
        return

    if text == "المطور":
        try:
            ou = await client.get_users(OWNER_ID)
        except Exception:
            await message.reply_text(f"👨‍💻 **مطور البوت:** `{OWNER_ID}`")
            return
        bio = ""
        try:
            fc = await client.get_chat(OWNER_ID)
            if fc.bio:
                bio = fc.bio
        except Exception:
            pass
        uname = f"@{ou.username}" if ou.username else ""
        msg = f"👨‍💻 **مطور البوت:** {ou.mention}\n"
        if uname:
            msg += f"🌐 {uname}\n"
        msg += f"🆔 `{OWNER_ID}`\n"
        if bio:
            msg += f"📝 {bio}"
        btn_label = "\U0001d477\U0001d493\U0001d490\U0001d487\U0001d48a\U0001d48d\U0001d486"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(btn_label, url=f"tg://user?id={OWNER_ID}")]])
        pf = None
        try:
            async for p in client.get_chat_photos(OWNER_ID, limit=1):
                pf = p.file_id
        except Exception:
            pass
        if pf:
            try:
                await message.reply_photo(pf, caption=msg, reply_markup=kb)
            except Exception:
                await message.reply_text(msg, reply_markup=kb)
        else:
            await message.reply_text(msg, reply_markup=kb)
        return

    if text in ("الساعه", "الساعة"):
        n = datetime.now(timezone(timedelta(hours=3)))
        await message.reply_text(f"🕐 **التاريخ والوقت:**\n📅 {n.strftime('%Y-%m-%d')}\n⏰ {n.strftime('%I:%M:%S %p')}")
        return

    if text == "التاريخ":
        await message.reply_text(f"📅 **التاريخ اليوم:** {datetime.now(timezone(timedelta(hours=3))).strftime('%Y-%m-%d')}")
        return

    if text == "مسح القوانين" and sender_level >= 2:
        row = await DB.execute("SELECT rules FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if not row or not row[0]:
            await message.reply_text("لا توجد قوانين لازالتها")
            return
        await DB.execute("UPDATE groups SET rules=NULL WHERE chat_id=?", (cid,), commit=True)
        await message.reply_text("• تم ازالة قوانين المجموعه")
        return

    if text == "مسح الترحيب" and sender_level >= 2:
        await DB.execute("UPDATE groups SET welcome_msg=NULL WHERE chat_id=?", (cid,), commit=True)
        await message.reply_text("• تم ازالة ترحيب المجموعه")
        return

    if text == "مسح الرابط":
        if role_key not in ("owner", "supreme"):
            await message.reply_text("❌ هذا الأمر متاح لمالك الكروب ومالك البوت فقط.")
            return
        try:
            await client.export_chat_invite_link(cid)
            await message.reply_text("• تم مسح الرابط")
        except Exception as e:
            await message.reply_text(f"❌ تعذر مسح الرابط: {e}")
        return

    if text == "مسح وسائط البوت" and sender_level >= 2:
        sm = await message.reply_text("🧹 جاري مسح وسائط البوت...")
        rows = await DB.execute("SELECT message_id FROM media_history WHERE chat_id=?", (cid,), fetchall=True)
        if rows:
            mids = [r[0] for r in rows]
            dc = 0
            for i in range(0, len(mids), 100):
                try:
                    await client.delete_messages(cid, mids[i:i+100])
                    dc += len(mids[i:i+100])
                except Exception:
                    pass
            await DB.execute("DELETE FROM media_history WHERE chat_id=?", (cid,), commit=True)
            try:
                await sm.edit_text(f"✅ تم مسح {dc} وسائط بوت بنجاح.")
            except Exception:
                pass
        else:
            try:
                await sm.edit_text("📭 لا توجد وسائط بوت لمسحها.")
            except Exception:
                pass
        return

    if text == "تغيير الايدي" and sender_level >= 4:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("الشكل 1", callback_data=f"sv1_{uid}"), InlineKeyboardButton("الشكل 2", callback_data=f"sv2_{uid}")],
            [InlineKeyboardButton("الشكل 3", callback_data=f"sv3_{uid}"), InlineKeyboardButton("الشكل 4", callback_data=f"sv4_{uid}")],
            [InlineKeyboardButton("الشكل 5", callback_data=f"sv5_{uid}"), InlineKeyboardButton("الشكل 6", callback_data=f"sv6_{uid}")],
            [InlineKeyboardButton("الشكل 7", callback_data=f"sv7_{uid}"), InlineKeyboardButton("الشكل 8", callback_data=f"sv8_{uid}")]
        ])
        await message.reply_text("🎨 **لوحة اختيار كليشة الـ ID للمجموعة:**\n\nيرجى الضغط على الأشكال التالية لمعاينتها واختيار الأنسب لمجموعتك:", reply_markup=kb)
        return

    if text in ("اكس او", "XO", "xo"):
        ga = await DB.execute("SELECT games_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ga and not ga[0]:
            await message.reply_text("❌ الألعاب معطلة في هذه المجموعة.")
            return
        if cid in active_xo_games:
            await message.reply_text("⚠️ توجد لعبة إكس أو نشطة بالفعل في هذه المجموعة!")
            return
        g = {"board": [" "]*9, "p1": uid, "p1_name": message.from_user.first_name or "لاعب", "p2": None, "p2_name": None, "p1_symbol": "O", "p2_symbol": "X", "turn": uid}
        active_xo_games[cid] = g
        await message.reply_text(f"🎮 **تم إنشاء لعبة إكس أو (XO)!**\n\n👤 اللاعب الأول: [{g['p1_name']}] (O)\n\n⏳ ينتظر منافساً للانضمام...",
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚔️ انضم كلاعب ثاني", callback_data=f"xoj_{cid}")]]))
        return

    if text == "المالك":
        owner_id = None
        owner_name = ""
        try:
            async for m in client.get_chat_members(cid, filter=ChatMembersFilter.ADMINISTRATORS):
                if m.status == ChatMemberStatus.OWNER:
                    owner_id = m.user.id
                    owner_name = m.user.first_name or "المالك"
                    break
        except Exception:
            pass
        if not owner_id:
            await message.reply_text("❌ لم يتم العثور على مالك المجموعة.")
            return
        try:
            ou = await client.get_users(owner_id)
        except Exception:
            await message.reply_text("❌ تعذر جلب معلومات المالك.")
            return
        bio = ""
        try:
            fc = await client.get_chat(owner_id)
            if fc.bio:
                bio = fc.bio
        except Exception:
            pass
        uname = f"@{ou.username}" if ou.username else ""
        msg = f"👑 **مالك المجموعة:** {ou.mention}\n"
        if uname:
            msg += f"🌐 {uname}\n"
        msg += f"🆔 `{owner_id}`\n"
        if bio:
            msg += f"📝 {bio}"
        btn_label = "\U0001d477\U0001d493\U0001d490\U0001d487\U0001d48a\U0001d48d\U0001d486"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(btn_label, url=f"tg://user?id={owner_id}")]])
        pf = None
        try:
            async for p in client.get_chat_photos(owner_id, limit=1):
                pf = p.file_id
        except Exception:
            pass
        if pf:
            try:
                await message.reply_photo(pf, caption=msg, reply_markup=kb)
            except Exception:
                await message.reply_text(msg, reply_markup=kb)
        else:
            await message.reply_text(msg, reply_markup=kb)
        return

    if text.startswith("لقبني "):
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم بالرد.")
            return
        nick = text[6:].strip()
        if not nick:
            await message.reply_text("❌ يرجى إرسال اللقب المطلوب.")
            return
        await DB.execute("INSERT INTO custom_ranks (chat_id,user_id,rank_title) VALUES (?,?,?) ON CONFLICT DO UPDATE SET rank_title=?",
                         (cid, t.id, nick, nick), commit=True)
        await message.reply_text(f"✅ تم تعيين لقب **{nick}** لـ {t.mention}.")
        return

    if text == "لقبي":
        cr = await DB.execute("SELECT rank_title FROM custom_ranks WHERE chat_id=? AND user_id=?", (cid, uid), fetchone=True)
        await message.reply_text(f"🎖️ لقبك الحالي: **{cr[0]}**" if cr else "❌ لا يوجد لقب مسجل لك.")
        return

    if text in ("صلاحياتي", "صلاحياته"):
        tu = await extract_target(message) or message.from_user
        rk, lv = await get_role(cid, tu.id, client)
        rn = ROLE_ARABIC.get(rk, "عضو")
        await message.reply_text(f"🔰 **صلاحيات {tu.mention}:**\n🏷️ الرتبة: {rn}\n📊 المستوى: {lv}")
        return

    if text == "زوجني":
        mr = await DB.execute("SELECT marry_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if mr and not mr[0]:
            await message.reply_text("❌ أمر الزواج معطل في هذه المجموعة.")
            return
        m = await DB.execute("SELECT partner_id FROM marriages WHERE chat_id=? AND user_id=?", (cid, uid), fetchone=True)
        if m:
            try:
                pu = await client.get_users(m[0])
                await message.reply_text(f"💔 أنت متزوج بالفعل من {pu.mention}! أرسل `طلقني` للطلاق.")
            except Exception:
                await message.reply_text("💔 أنت متزوج بالفعل! أرسل `طلقني` للطلاق.")
            return
        members = []
        try:
            async for mb in client.get_chat_members(cid):
                if mb.user and not mb.user.is_bot and not mb.user.is_deleted and mb.user.id != uid:
                    members.append(mb.user)
        except Exception:
            await message.reply_text("❌ تعذر جلب قائمة الأعضاء.")
            return
        if not members:
            await message.reply_text("❌ لا يوجد أعضاء للزواج.")
            return
        p = random.choice(members)
        await DB.execute("INSERT INTO marriages (chat_id,user_id,partner_id) VALUES (?,?,?) ON CONFLICT DO UPDATE SET partner_id=?", (cid, uid, p.id, p.id), commit=True)
        await DB.execute("INSERT INTO marriages (chat_id,user_id,partner_id) VALUES (?,?,?) ON CONFLICT DO UPDATE SET partner_id=?", (cid, p.id, uid, uid), commit=True)
        await message.reply_text(f"💍 مبروك! تم زواج {message.from_user.mention} بـ {p.mention} ❤️")
        return

    if text == "طلقني":
        mr = await DB.execute("SELECT marry_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if mr and not mr[0]:
            await message.reply_text("❌ أمر الزواج معطل في هذه المجموعة.")
            return
        m = await DB.execute("SELECT partner_id FROM marriages WHERE chat_id=? AND user_id=?", (cid, uid), fetchone=True)
        if not m:
            await message.reply_text("❌ أنت لست متزوجاً في هذه المجموعة.")
            return
        await DB.execute("DELETE FROM marriages WHERE chat_id=? AND (user_id=? OR user_id=?)", (cid, uid, m[0]), commit=True)
        await message.reply_text("💔 تم الطلاق بنجاح!")
        return

    if text == "السورس":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Official Channel", url="https://t.me/SourceRozaya"),
             InlineKeyboardButton("Call Us", url="https://t.me/EasyTI")]
        ])
        wt = "Welcome To Source Rozaya\n• قناة سورس روز الرسمية\n• يمكنك معرفة كل شي عن السورس من خلال القناة"
        try:
            await message.reply_photo("https://t.me/SourceRozaya", caption=wt, reply_markup=kb)
        except Exception:
            await message.reply_text(wt, reply_markup=kb)
        return

    if text in ("المجموعة", "المجموعه"):
        try:
            c = await client.get_chat(cid)
            mc = await client.get_chat_members_count(cid)
            await message.reply_text(f"ℹ️ **معلومات المجموعة:**\n\n👥 الاسم: {c.title}\n🆔 الآيدي: `{cid}`\n👤 الأعضاء: {mc}\n📌 الرابط: {c.invite_link or 'لا يوجد'}")
        except Exception as e:
            await message.reply_text(f"❌ تعذر جلب معلومات المجموعة: {e}")
        return

    if text == "معلومات المجموعه":
        try:
            c = await client.get_chat(cid)
            mc = await client.get_chat_members_count(cid)
            total_msgs = (await DB.execute("SELECT SUM(count) FROM messages_count WHERE chat_id=?", (cid,), fetchone=True) or [0])[0] or 0
            owner_name = ""
            try:
                async for m in client.get_chat_members(cid, filter=ChatMembersFilter.ADMINISTRATORS):
                    if m.status == ChatMemberStatus.OWNER:
                        owner_name = m.user.mention if m.user else f"`{m.user.id}`"
                        break
            except Exception:
                owner_name = "غير معروف"
            ranks_list = []
            role_order = [
                ("asaasi", "اساسي"), ("owner_basic", "مالك اساسي"), ("owner", "مالك"),
                ("supervisor", "مشرف"), ("creator", "منشئ"), ("manager", "مدير"),
                ("admin", "ادمن"), ("vip", "مميز")
            ]
            for role_key, role_ar in role_order:
                rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role=?", (cid, role_key), fetchall=True)
                for (ruid,) in rows:
                    try:
                        ru = await client.get_users(ruid)
                        ranks_list.append(f"• {ru.mention} ← {role_ar}")
                    except Exception:
                        ranks_list.append(f"• `{ruid}` ← {role_ar}")
            msg = (
                f"• معرف المجموعة : `{cid}`\n"
                f"• عدد الاعضاء : `{mc}`\n"
                f"• عدد الرسائل : `{total_msgs}`\n"
                f"• حساب المالك : {owner_name}\n\n"
            )
            if ranks_list:
                msg += "• قائمة الرتب :\n" + "\n".join(ranks_list)
            else:
                msg += "• لا يوجد رتب مسجلة."
            await message.reply_text(msg)
        except Exception as e:
            await message.reply_text(f"❌ تعذر جلب معلومات المجموعة: {e}")
        return

    # --- Tag all / random ---
    if text in ("تاك عام", "@all") or text.startswith("تاك عام ") or text.startswith("@all "):
        if sender_level < 2:
            await message.reply_text("❌ يتطلب هذا الأمر صلاحية ادمن فما فوق.")
            return
        sr = await DB.execute("SELECT tag_all_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if sr and not sr[0]:
            await message.reply_text("❌ أمر تاك عام معطل في هذه المجموعة حالياً.")
            return
        sm = await message.reply_text("📣 جاري جلب طاقم وأعضاء المجموعة والمناداة عليهم حركياً...")
        members = []
        try:
            async for mb in client.get_chat_members(cid):
                if mb.user and not mb.user.is_bot and not mb.user.is_deleted:
                    members.append(mb.user)
        except Exception as e:
            await sm.edit_text(f"❌ تعذر استخراج قائمة الأعضاء: `{e}`")
            return
        if not members:
            await sm.edit_text("🔍 لم يتم العثور على أعضاء حقيقيين للمناداة.")
            return
        for i in range(0, len(members), 5):
            chunk = members[i:i+5]
            await client.send_message(cid, "📣 **مناداة جماعية نشطة للأعضاء (تاك عام):**\n\n" + " | ".join(m.mention for m in chunk))
            await asyncio.sleep(1.5)
        try:
            await sm.delete()
        except Exception:
            pass
        return

    if text == "تاك" and sender_level >= 2:
        sr = await DB.execute("SELECT tag_random_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if sr and not sr[0]:
            await message.reply_text("❌ أمر تاك العشوائي معطل في هذه المجموعة حالياً.")
            return
        members = []
        try:
            async for mb in client.get_chat_members(cid):
                if mb.user and not mb.user.is_bot and not mb.user.is_deleted and mb.user.id != uid:
                    members.append(mb.user)
        except Exception as e:
            await message.reply_text(f"❌ تعذر جلب قائمة الأعضاء: `{e}`")
            return
        if not members:
            await message.reply_text("🔍 لم يتم العثور على أعضاء عشوائيين للمناداة.")
            return
        await message.reply_text(f"🎯 العضو المستهدف بالتاك العشوائي: {random.choice(members).mention}")
        return

    # --- Custom replies ---
    cr = await DB.execute("SELECT reply_type, reply_data FROM custom_replies WHERE chat_id=? AND keyword=?", (cid, text), fetchone=True)
    if cr:
        rt, rd = cr
        sm = None
        try:
            if rt == "text": await message.reply_text(rd)
            elif rt == "photo": sm = await message.reply_photo(rd)
            elif rt == "video": sm = await message.reply_video(rd)
            elif rt == "animation": sm = await message.reply_animation(rd)
            elif rt == "voice": sm = await message.reply_voice(rd)
            elif rt == "audio": sm = await message.reply_audio(rd)
            elif rt == "document": sm = await message.reply_document(rd)
            elif rt == "sticker": sm = await message.reply_sticker(rd)
            if sm:
                await DB.execute("INSERT OR IGNORE INTO media_history (chat_id,message_id) VALUES (?,?)", (cid, sm.id), commit=True)
        except Exception as e:
            log.error("Custom reply: %s", e)
        return

    # --- Second menu commands (creator+) ---
    if text == "عدد الرتب" and role_key in ("owner", "bot_owner", "supreme"):
        rc = {}
        for rk in ["asaasi", "owner_basic", "owner", "supervisor", "creator", "manager", "admin", "vip"]:
            cnt = (await DB.execute("SELECT COUNT(*) FROM ranks WHERE chat_id=? AND role=?", (cid, rk), fetchone=True) or [0])[0]
            rc[rk] = cnt
        msg = "أهلاً بك عزيزي في عدد رتب المجموعة \n\n"
        msg += f"المالكين الاساسين ↤ {rc.get('owner_basic', 0)}\n"
        msg += f"المالكين ↤ {rc.get('owner', 0)}\n"
        msg += f"المنشئين ↤ {rc.get('creator', 0)}\n"
        msg += f"المدراء ↤ {rc.get('manager', 0)}\n"
        msg += f"الادمنيه ↤ {rc.get('admin', 0)}\n"
        msg += f"المميزين ↤ {rc.get('vip', 0)}"
        await message.reply_text(msg)
        return

    if text == "الاساسي" and sender_level > 8:
        rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='asaasi'", (cid,), fetchall=True)
        if not rows:
            await message.reply_text("📭 لا يوجد اساسين في هذه المجموعة.")
            return
        users = []
        for (uid,) in rows:
            try:
                u = await client.get_users(uid)
                users.append(u.mention)
            except Exception:
                users.append(f"`{uid}`")
        await message.reply_text("**قائمة الاساسين:**\n" + "\n".join(f"• {u}" for u in users))
        return

    if text == "المالكين الاساسين" and sender_level > 8:
        rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='owner_basic'", (cid,), fetchall=True)
        if not rows:
            await message.reply_text("📭 لا يوجد مالكين اساسيين في هذه المجموعة.")
            return
        users = []
        for (uid,) in rows:
            try:
                u = await client.get_users(uid)
                users.append(u.mention)
            except Exception:
                users.append(f"`{uid}`")
        await message.reply_text("**قائمة المالكين الاساسين:**\n" + "\n".join(f"• {u}" for u in users))
        return

    if text == "المالكين" and sender_level > 9:
        rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='owner'", (cid,), fetchall=True)
        if not rows:
            await message.reply_text("📭 لا يوجد مالكين في هذه المجموعة.")
            return
        users = []
        for (uid,) in rows:
            try:
                u = await client.get_users(uid)
                users.append(u.mention)
            except Exception:
                users.append(f"`{uid}`")
        await message.reply_text("**قائمة المالكين:**\n" + "\n".join(f"• {u}" for u in users))
        return

    if text == "المشرفين" and sender_level > 4:
        rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='supervisor'", (cid,), fetchall=True)
        if not rows:
            await message.reply_text("📭 لا يوجد مشرفين في هذه المجموعة.")
            return
        users = []
        for (uid,) in rows:
            try:
                u = await client.get_users(uid)
                users.append(u.mention)
            except Exception:
                users.append(f"`{uid}`")
        await message.reply_text("**قائمة المشرفين:**\n" + "\n".join(f"• {u}" for u in users))
        return

    if text == "المنشئين" and sender_level > 4:
        rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='creator'", (cid,), fetchall=True)
        if not rows:
            await message.reply_text("📭 لا يوجد منشئين في هذه المجموعة.")
            return
        users = []
        for (uid,) in rows:
            try:
                u = await client.get_users(uid)
                users.append(u.mention)
            except Exception:
                users.append(f"`{uid}`")
        await message.reply_text("**قائمة المنشئين:**\n" + "\n".join(f"• {u}" for u in users))
        return

    if text == "المشرف المثالي":
        rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='supervisor_perfect'", (cid,), fetchall=True)
        if not rows:
            await message.reply_text("📭 لا يوجد مشرفين مثاليين في هذه المجموعة.")
            return
        users = []
        for (uid,) in rows:
            try:
                u = await client.get_users(uid)
                users.append(u.mention)
            except Exception:
                users.append(f"`{uid}`")
        await message.reply_text("**قائمة المشرفين المثاليين:**\n" + "\n".join(f"• {u}" for u in users))
        return

    if text == "العضو المثالي":
        rows = await DB.execute("SELECT user_id FROM ranks WHERE chat_id=? AND role='member_perfect'", (cid,), fetchall=True)
        if not rows:
            await message.reply_text("📭 لا يوجد اعضاء مثاليين في هذه المجموعة.")
            return
        users = []
        for (uid,) in rows:
            try:
                u = await client.get_users(uid)
                users.append(u.mention)
            except Exception:
                users.append(f"`{uid}`")
        await message.reply_text("**قائمة الاعضاء المثاليين:**\n" + "\n".join(f"• {u}" for u in users))
        return

    if text == "البايو" or text.startswith("البايو "):
        ba = await DB.execute("SELECT bio_active FROM groups WHERE chat_id=?", (cid,), fetchone=True)
        if ba and not ba[0]:
            await message.reply_text("❌ أمر البايو معطل في هذه المجموعة.")
            return
        tu = await extract_target(message) or message.from_user
        try:
            fc = await client.get_chat(tu.id)
            bio = fc.bio or "لا يوجد بايو"
            await message.reply_text(f"ℹ️ بايو {tu.mention}:\n\n{bio}")
        except Exception as e:
            await message.reply_text(f"❌ تعذر جلب البايو: {e}")
        return

    if text == "معلوماتي":
        mc = (await DB.execute("SELECT count FROM messages_count WHERE chat_id=? AND user_id=?", (cid, uid), fetchone=True) or [0])[0]
        rk, _ = await get_role(cid, uid, client)
        rn = ROLE_ARABIC.get(rk, "عضو")
        us = await _get_usernames(client, uid, message.from_user)
        if mc < 50:
            interaction = "غير متفاعل"
        elif mc < 200:
            interaction = "تفاعل ضعيف"
        elif mc < 500:
            interaction = "متوسط"
        else:
            interaction = "متفاعل"
        msg = (
            f"• ايديك : `{uid}`\n"
            f"• معرفك : {us}\n"
            f"• رتبته المجموعه : {rn}\n"
            f"• رسائلك : `{mc}`\n"
            f"• تفاعلك : {interaction}"
        )
        await message.reply_text(msg)
        return

    if text == "اعدادات القروب" and role_key in ("owner", "supreme"):
        try:
            cm = await client.get_chat_member(cid, uid)
            is_owner = cm.status == ChatMemberStatus.OWNER
        except Exception:
            is_owner = False
        if not is_owner:
            await message.reply_text("❌ هذا الامر متاح لمالك الكروب فقط.")
            return
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("الصلاحيات العامة", callback_data=f"gs_gen_{uid}")],
            [InlineKeyboardButton("صلاحيات الوسائط", callback_data=f"gs_med_{uid}")]
        ])
        await message.reply_text("• أختار نوع الصلاحيات التي تريد تعديلها للمجموعة", reply_markup=kb)
        return

    if text == "اضف المالكه" and role_key in ("owner", "supreme"):
        t = await extract_target(message)
        if not t:
            await message.reply_text("❌ يرجى تحديد المستخدم عبر الرد او المعرف.")
            return
        await DB.execute("INSERT OR REPLACE INTO owner_female (chat_id,user_id) VALUES (?,?)", (cid, t.id), commit=True)
        await message.reply_text(f"✅ تم رفع {t.mention} بلقب مالكه بنجاح.")
        return

    if text == "المالكه":
        row = await DB.execute("SELECT user_id FROM owner_female WHERE chat_id=?", (cid,), fetchone=True)
        if not row:
            return
        tuid = row[0]
        try:
            tu = await client.get_users(tuid)
        except Exception:
            return
        bio = ""
        try:
            fc = await client.get_chat(tuid)
            if fc.bio:
                bio = fc.bio
        except Exception:
            pass
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("حسابه", url=f"tg://user?id={tuid}")]
        ])
        uname = f"@{tu.username}" if tu.username else f"`{tuid}`"
        msg = f"• مالكة المجموعه ↤︎ {uname}\n• البايو ↤︎ {bio}"
        pf = None
        try:
            async for p in client.get_chat_photos(tuid, limit=1):
                pf = p.file_id
        except Exception:
            pass
        if pf:
            try:
                await message.reply_photo(pf, caption=msg, reply_markup=kb)
            except Exception:
                await message.reply_text(msg, reply_markup=kb)
        else:
            await message.reply_text(msg, reply_markup=kb)
        return

    if text == "ضع صوره" and role_key in ("owner", "supreme"):
        conv_states[cid] = {"user_id": uid, "state": "waiting_group_photo"}
        await message.reply_text("📸 أرسل الصورة التي تريد تعيينها كصورة للمجموعة.")
        return

    if text.startswith("ضع اسم") and role_key in ("owner", "supreme"):
        new_name = text[6:].strip()
        if not new_name:
            await message.reply_text("❌ يرجى كتابة الاسم الجديد. مثال: `ضع اسم علي`")
            return
        try:
            await client.set_chat_title(cid, new_name)
            await message.reply_text(f"✅ تم تعيين اسم المجموعة الى : {new_name}")
        except Exception as e:
            await message.reply_text(f"❌ تعذر تغيير الاسم: {e}")
        return

    if text.startswith("وضع وصف") and role_key in ("owner", "supreme"):
        new_desc = text[8:].strip()
        if not new_desc:
            await message.reply_text("❌ يرجى كتابة الوصف. مثال: `وضع وصف كروب شباب وبنات`")
            return
        try:
            await client.set_chat_description(cid, new_desc)
            await message.reply_text(f"✅ تم تعيين وصف المجموعة بنجاح.")
        except Exception as e:
            await message.reply_text(f"❌ تعذر تغيير الوصف: {e}")
        return


async def _ask_ai(question: str) -> str | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {AI_KEYS[0]}"},
                json={"model": "openai/gpt-oss-20b", "messages": [{"role": "user", "content": question}], "max_tokens": 2048},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    answer = data["choices"][0]["message"]["content"]
                    if answer:
                        return answer.strip()
                else:
                    text = await resp.text()
                    log.warning(f"Groq/DeepSeek ({resp.status}): {text[:200]}")
    except asyncio.TimeoutError:
        log.warning("Groq/DeepSeek timed out after 30s")
    except Exception as e:
        log.warning(f"Groq/DeepSeek failed: {e}")
    return None



async def _get_usernames(client, uid, fallback=None) -> str:
    us = []
    if fallback and fallback.username:
        us.append(f"@{fallback.username}")
    try:
        fc = await client.get_chat(uid)
        if fc:
            if fc.username and f"@{fc.username}" not in us:
                us.append(f"@{fc.username}")
            if hasattr(fc, "usernames"):
                for u in fc.usernames or []:
                    if u.active and f"@{u.username}" not in us:
                        us.append(f"@{u.username}")
    except Exception:
        pass
    if not us and fallback and hasattr(fallback, "usernames"):
        for u in fallback.usernames or []:
            if u.active and f"@{u.username}" not in us:
                us.append(f"@{u.username}")
    return ", ".join(us) if us else "لا يوجد"


async def _reply_toggle(message, action: str, feature: str):
    ref = f"@{message.from_user.username}" if message.from_user.username else message.from_user.mention
    await message.reply_text(f"- بواسطه : {ref}\n- تم {action} {feature} بنجاح .")


async def _check_target_rank(message, target_id: int, client) -> bool:
    _, tl = await get_role(message.chat.id, target_id, client)
    if tl >= 1:
        role_name = ROLE_ARABIC.get(_, "مجهولة")
        await message.reply_text(f"❌ هذا العضو يمتلك رتبة \"{role_name}\" يجب تنزيله اولا")
        return True
    return False


async def _auto_unrestrict(client, cid, uid, delay):
    await asyncio.sleep(delay)
    try:
        await client.restrict_chat_member(cid, uid, ChatPermissions(
            can_send_messages=True, can_send_media_messages=True,
            can_send_other_messages=True, can_add_web_page_previews=True))
    except Exception:
        pass


@app.on_edited_message(filters.group)
async def edit_handler(client, message):
    if not message.from_user:
        return
    cid, uid = message.chat.id, message.from_user.id
    try:
        await DB.execute("INSERT OR IGNORE INTO edited_history (chat_id,message_id) VALUES (?,?)", (cid, message.id), commit=True)
    except Exception:
        pass
    gi = await DB.execute("SELECT lock_edit,lock_media_edit FROM groups WHERE chat_id=?", (cid,), fetchone=True)
    if gi:
        le, lme = gi
    else:
        le = lme = 0
    if le:
        _, lv = await get_role(cid, uid, client)
        if lv < 1:
            try:
                await message.delete()
                ref = f"@{message.from_user.username}" if message.from_user.username else message.from_user.mention
                await client.send_message(cid, f"⚠️ ممنوع تعديل الرسائل {ref}")
            except Exception:
                pass
    if lme and (message.photo or message.video or message.audio or message.voice or message.document or message.animation or message.video_note):
        try:
            await message.delete()
            ref = f"@{message.from_user.username}" if message.from_user.username else message.from_user.mention
            await client.send_message(cid, f"⚠️ ممنوع تعديل الميديا {ref}")
        except Exception:
            pass


@app.on_callback_query()
async def cb_handler(client, cb):
    data = cb.data
    cid = cb.message.chat.id
    uid = cb.from_user.id

    # --- Force sub management ---
    if data.startswith("fs_"):
        parts = data.split("_")
        creator_id = int(parts[-1])
        if uid != creator_id:
            await cb.answer("❌ هذه اللوحة ليست لك.", show_alert=True)
            return
        if len(parts) == 2:
            # Main panel
            msg, mk = await force_sub_ui(uid)
            await cb.message.edit_text(msg, reply_markup=mk)
            await cb.answer()
            return
        action = "_".join(parts[1:-1])
        if action == "back":
            msg, mk = await stats_ui(client, uid)
            await cb.message.edit_text(msg, reply_markup=mk)
            await cb.answer()
            return
        if action == "toggle":
            row = await DB.execute("SELECT value FROM bot_settings WHERE key='force_sub_enabled'", fetchone=True)
            cur = row[0] if row else "0"
            new_val = "0" if cur == "1" else "1"
            await DB.execute("INSERT OR REPLACE INTO bot_settings (key,value) VALUES ('force_sub_enabled',?)", (new_val,), commit=True)
            log.info("Force sub toggled to %s by %d", new_val, uid)
            msg, mk = await force_sub_ui(uid)
            await cb.message.edit_text(msg, reply_markup=mk)
            await cb.answer(f"✅ تم {'تفعيل' if new_val == '1' else 'تعطيل'} الاشتراك الإجباري.")
            return
        if action == "show_msg":
            row = await DB.execute("SELECT value FROM bot_settings WHERE key='force_sub_msg'", fetchone=True)
            txt = row[0] if row and row[0] else "⚠️ لا توجد رسالة مخصصة. سيتم استخدام الرسالة الافتراضية."
            await cb.answer(txt, show_alert=True)
            return
        if action == "set_msg":
            conv_states[uid] = {"user_id": uid, "state": "waiting_force_sub_msg"}
            await cb.message.edit_text("✏️ أرسل الآن رسالة الاشتراك الجديدة.\nيمكنك استخدام `{mention}` و `{link}` كمتغيرات.\nأرسل 'الغاء' للإلغاء.")
            await cb.answer()
            return
        if action == "del_msg":
            await DB.execute("DELETE FROM bot_settings WHERE key='force_sub_msg'", commit=True)
            log.info("Force sub message deleted by %d", uid)
            msg, mk = await force_sub_ui(uid)
            await cb.message.edit_text(msg, reply_markup=mk)
            await cb.answer("✅ تم حذف رسالة الاشتراك.", show_alert=True)
            return
        if action == "set_link":
            conv_states[uid] = {"user_id": uid, "state": "waiting_force_sub_link"}
            await cb.message.edit_text("➕ أرسل الآن رابط قناة الاشتراك الإجباري (مثال: https://t.me/MyChannel).\nأرسل 'الغاء' للإلغاء.")
            await cb.answer()
            return
        return

    if data.startswith("bc_"):
        parts = data.split("_")
        creator_id = int(parts[-1])
        if uid != creator_id:
            await cb.answer("❌ هذه اللوحة ليست لك.", show_alert=True)
            return
        if len(parts) == 2:
            msg, mk = await broadcast_ui(uid)
            await cb.message.edit_text(msg, reply_markup=mk)
            await cb.answer()
            return
        action = "_".join(parts[1:-1])
        if action == "back":
            msg, mk = await stats_ui(client, uid)
            await cb.message.edit_text(msg, reply_markup=mk)
            await cb.answer()
            return
        if action == "users":
            conv_states[uid] = {"user_id": uid, "state": "waiting_broadcast_users"}
            await cb.message.edit_text("📡 أرسل المنشور الان\n\nأرسل 'الغاء' للإلغاء.",
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("الغاء الامر", callback_data=f"bc_cancel_{uid}")]]))
            await cb.answer()
            return
        if action == "groups":
            conv_states[uid] = {"user_id": uid, "state": "waiting_broadcast_groups"}
            await cb.message.edit_text("📡 أرسل المنشور الان\n\nأرسل 'الغاء' للإلغاء.",
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("الغاء الامر", callback_data=f"bc_cancel_{uid}")]]))
            await cb.answer()
            return
        if action == "cancel":
            conv_states.pop(uid, None)
            msg, mk = await broadcast_ui(uid)
            await cb.message.edit_text(msg, reply_markup=mk)
            await cb.answer("❌ تم إلغاء الاذاعة.", show_alert=True)
            return
        return

    if data.startswith("leave_"):
        gid = int(data.split("_", 1)[1])
        owners = await DB.execute("SELECT user_id FROM bot_owners", fetchall=True) or []
        oids = [r[0] for r in owners] + [OWNER_ID]
        if uid in oids:
            try:
                await client.leave_chat(gid)
                await DB.execute("DELETE FROM groups WHERE chat_id=?", (gid,), commit=True)
                await cb.answer("✅ تم مغادرة وإزالة الكروب من البوت بنجاح!", show_alert=True)
                msg, mk = await stats_ui(client, uid)
                await cb.message.edit_text(msg, reply_markup=mk)
            except Exception as e:
                await cb.answer(f"❌ تعذر الخروج: {e}", show_alert=True)
        else:
            await cb.answer("❌ عذراً، هذا الإجراء مخصص لمطور البوت فقط.", show_alert=True)
        return

    if data.startswith("xoj_"):
        gid = int(data.split("_", 1)[1])
        game = active_xo_games.get(gid)
        if not game:
            await cb.answer("⚠️ اللعبة غير موجودة أو انتهت بالفعل.", show_alert=True)
            return
        if game["p1"] == uid:
            await cb.answer("❌ لا يمكنك اللعب ضد نفسك!", show_alert=True)
            return
        if game["p2"] is not None:
            await cb.answer("❌ هذه اللعبة ممتلئة بالفعل باللاعبين!", show_alert=True)
            return
        p2n = cb.from_user.first_name or "منافس"
        game["p2"] = uid
        game["p2_name"] = p2n
        grid = xo_grid(game, gid)
        await cb.message.edit_text(
            f"🎮 **بدأت معركة إكس أو (XO) الكبرى!**\n\n"
            f"👤 اللاعب الأول: [{game['p1_name']}] (O)\n👤 اللاعب الثاني: [{p2n}] (X)\n\n"
            f"⚡ الدور الآن عند: **[{game['p1_name']}]** (O)",
            reply_markup=grid)
        await cb.answer("⚔️ تم الانضمام كمنافس بنجاح، بالتوفيق!", show_alert=True)
        return

    if data.startswith("xo_"):
        if data.startswith("xoc_"):
            gid = int(data.split("_", 1)[1])
            game = active_xo_games.get(gid)
            if game and uid in (game["p1"], game["p2"]):
                active_xo_games.pop(gid, None)
                await cb.message.edit_text("🏳️ **تم إنهاء المباراة وإلغاء جولة إكس أو بناءً على رغبة أحد الطرفين.**")
                await cb.answer("تم إلغاء الجولة بنجاح", show_alert=True)
            else:
                await cb.answer("❌ هذا الإجراء متاح فقط للاعبي المباراة الجارية!", show_alert=True)
            return
        if data == "xox":
            await cb.answer("🏆 هذه اللعبة منتهية بالفعل، جرب بدء جولة جديدة!", show_alert=True)
            return
        parts = data.split("_")
        if len(parts) == 3:
            gid, idx = int(parts[1]), int(parts[2])
            game = active_xo_games.get(gid)
            if not game:
                await cb.answer("⚠️ اللعبة غير موجودة أو انتهت بالفعل.", show_alert=True)
                return
            if uid != game["turn"]:
                await cb.answer("❌ ليس دورك الآن! انتظر دور خصمك.", show_alert=True)
                return
            if game["board"][idx] != " ":
                await cb.answer("❌ هذا المربع محجوز بالفعل، اختر مكاناً آخر!", show_alert=True)
                return
            cur = "p1" if uid == game["p1"] else "p2"
            sym = game["p1_symbol"] if cur == "p1" else game["p2_symbol"]
            game["board"][idx] = sym
            winner = xo_winner(game["board"])
            if winner:
                wid = game["p1"] if winner == "O" else game["p2"]
                wn = game["p1_name"] if winner == "O" else game["p2_name"]
                await add_points(gid, wid, 5)
                grid = xo_grid_end(game)
                await cb.message.edit_text(
                    f"🎉 **مبروك! انتهى التحدي بفوز ساحق وحصولك على 5 نقاط!** 🎉\n\n"
                    f"🏆 الفائز البطل: **[{wn}]** ({winner})\n💀 الخاسر: حظاً أوفر في المرة القادمة!",
                    reply_markup=grid)
                active_xo_games.pop(gid, None)
                await cb.answer()
                return
            if " " not in game["board"]:
                grid = xo_grid_end(game)
                await cb.message.edit_text("🤝 **انتهت المباراة بالتعادل العادل!**\n\nلقد قاتل كلا الطرفين ببسالة كبيرة دون حسم، أداء مميز!", reply_markup=grid)
                active_xo_games.pop(gid, None)
                await cb.answer()
                return
            nt = game["p2"] if cur == "p1" else game["p1"]
            nn = game["p2_name"] if cur == "p1" else game["p1_name"]
            ns = game["p2_symbol"] if cur == "p1" else game["p1_symbol"]
            game["turn"] = nt
            grid = xo_grid(game, gid)
            await cb.message.edit_text(
                f"🎮 **مباراة إكس أو (XO) جارية...**\n\n"
                f"👤 [{game['p1_name']}] (O) 🆚 [{game['p2_name']}] (X)\n\n"
                f"⚡ الدور الآن عند: **[{nn}]** ({ns})",
                reply_markup=grid)
            await cb.answer()
            return

    # --- Game callbacks: لغز ---
    if data.startswith("lz_"):
        parts = data.split("_")
        if len(parts) == 3:
            try:
                gid = int(parts[1])
            except ValueError:
                await cb.answer("❌ بيانات غير صالحة.", show_alert=True)
                return
            if gid != cid:
                await cb.answer("❌ هذه اللعبة غير متاحة هنا.", show_alert=True)
                return
            selected = int(parts[2])
            game = active_games.get(cid)
            if not game or game.get("type") != "لغز":
                await cb.answer("⚠️ اللعبة غير موجودة أو انتهت بالفعل.", show_alert=True)
                return
            if selected == game["correct"]:
                active_games.pop(cid, None)
                await add_points(cid, uid, 5)
                await cb.message.edit_text(f"🎉 **إجابة صحيحة!**\n\n{cb.from_user.mention} فاز بـ 5 نقاط 🏆")
                await cb.answer("🎉 إجابة صحيحة! ربحت 5 نقاط!", show_alert=True)
            else:
                active_games.pop(cid, None)
                await cb.message.edit_text(f"❌ **الجواب خطأ، حظ اوفر في المرة المقبلة.**\n\n{cb.from_user.mention} أخطأ في الإجابة.")
                await cb.answer("❌ الجواب خطأ، حظ اوفر في المرة المقبلة.", show_alert=True)
        return

    # --- Game callbacks: اسئلني ---
    if data.startswith("sq_"):
        parts = data.split("_")
        if len(parts) == 3:
            try:
                gid = int(parts[1])
            except ValueError:
                await cb.answer("❌ بيانات غير صالحة.", show_alert=True)
                return
            if gid != cid:
                await cb.answer("❌ هذه اللعبة غير متاحة هنا.", show_alert=True)
                return
            selected = int(parts[2])
            game = active_games.get(cid)
            if not game or game.get("type") != "اسئلني":
                await cb.answer("⚠️ اللعبة غير موجودة أو انتهت بالفعل.", show_alert=True)
                return
            if selected == game["correct"]:
                active_games.pop(cid, None)
                await add_points(cid, uid, 5)
                await cb.message.edit_text(f"🎉 **إجابة صحيحة!**\n\n{cb.from_user.mention} فاز بـ 5 نقاط 🏆")
                await cb.answer("🎉 إجابة صحيحة! ربحت 5 نقاط!", show_alert=True)
            else:
                active_games.pop(cid, None)
                await cb.message.edit_text(f"❌ **الجواب خطأ، حظ اوفر في المرة المقبلة.**\n\n{cb.from_user.mention} أخطأ في الإجابة.")
                await cb.answer("❌ الجواب خطأ، حظ اوفر في المرة المقبلة.", show_alert=True)
        return

    # --- Game callbacks: محيبس ---
    if data.startswith("mh_"):
        parts = data.split("_")
        if len(parts) == 3:
            try:
                gid = int(parts[1])
            except ValueError:
                await cb.answer("❌ بيانات غير صالحة.", show_alert=True)
                return
            if gid != cid:
                await cb.answer("❌ هذه اللعبة غير متاحة هنا.", show_alert=True)
                return
            selected = int(parts[2])
            game = active_games.get(cid)
            if not game or game.get("type") != "محيبس":
                await cb.answer("⚠️ اللعبة غير موجودة أو انتهت بالفعل.", show_alert=True)
                return
            if selected == game["correct"]:
                active_games.pop(cid, None)
                await add_points(cid, uid, 5)
                await cb.message.edit_text(f"🎉 **أصبت! المحيبس كان في هذه اليد!** 🎉\n\n{cb.from_user.mention} فاز بـ 5 نقاط 🏆")
                await cb.answer("🎉 أصبت! ربحت 5 نقاط!", show_alert=True)
                return
            opened = game["opened"]
            if selected in opened:
                await cb.answer("🫴 هذه اليد مفتوحة بالفعل!", show_alert=True)
                return
            opened.add(selected)
            if len(opened) >= 5:
                active_games.pop(cid, None)
                await cb.message.edit_text(f"💀 **خسرت! المحيبس كان في اليد ({game['correct']+1})**\n\n{cb.from_user.mention} لم يتمكن من العثور على المحيبس!")
                await cb.answer("💀 خسرت! المرة القادمة قد تكون أفضل!", show_alert=True)
            else:
                kb = _mh_kb(cid, game)
                remain = 6 - len(opened) - 1
                await cb.message.edit_text(
                    f"🎲 **لعبة المحيبس**\n\nتم فتح اليد ({selected+1}) 👊➜🫴\n"
                    f"المتبقي {remain} أيدي، واحد منها فيه المحيبس!",
                    reply_markup=kb)
                await cb.answer()
        return

    # --- Game callbacks: ايموجي registration ---
    if data.startswith("emjr_"):
        parts = data.split("_")
        if len(parts) == 3:
            try:
                gid = int(parts[1])
            except ValueError:
                await cb.answer("❌ بيانات غير صالحة.", show_alert=True)
                return
            if gid != cid:
                await cb.answer("❌ هذه اللعبة غير متاحة هنا.", show_alert=True)
                return
            slot = int(parts[2])
            game = emoji_games.get(cid)
            if not game or game["phase"] != "registering":
                await cb.answer("⚠️ اللعبة غير موجودة أو انتهى التسجيل.", show_alert=True)
                return
            for p in game["players"]:
                if p and p["id"] == uid:
                    await cb.answer("✅ أنت مسجل بالفعل!", show_alert=True)
                    return
            if game["players"][slot] is not None:
                await cb.answer("⚠️ هذا المقعد محجوز بالفعل!", show_alert=True)
                return
            game["players"][slot] = {"id": uid, "name": cb.from_user.first_name or "لاعب"}
            kb = _emj_kb(cid, game)
            try:
                await cb.message.edit_text("🎮 **لعبة الإيموجي!**\n\nاضغط على الأزرار للتسجيل (مطلوب 4 لاعبين):", reply_markup=kb)
            except Exception:
                pass
            await cb.answer("✅ تم تسجيلك!", show_alert=True)
            if all(p is not None for p in game["players"]):
                game["phase"] = "playing"
                sender_idx = random.randint(0, 3)
                game["sender_idx"] = sender_idx
                sender = game["players"][sender_idx]
                ai_resp = await _ask_ai("اختر كلمة واحدة عشوائية (اسم فيلم مشهور، دولة، أو شخصية مشهورة) بالعربية. أعد الكلمة فقط بدون أي شرح أو علامات ترقيم.")
                word = ai_resp.strip() if ai_resp else random.choice(FALLBACK_WORDS)
                game["secret_word"] = word
                others = [p for i, p in enumerate(game["players"]) if i != sender_idx]
                others_names = "، ".join(p["name"] for p in others)
                try:
                    await client.send_message(sender["id"], f"🕵️ **أنت المرسل في لعبة الإيموجي!**\n\nالكلمة هي: **{word}**\n\nقم بتوصيلها لزملائك باستخدام الإيموجيات فقط في المجموعة!")
                except Exception:
                    pass
                try:
                    await cb.message.edit_text(
                        f"🎮 **بدأت لعبة الإيموجي!**\n\n"
                        f"🕵️ **المرسل:** {sender['name']}\n"
                        f"👥 **المتسابقون:** {others_names}\n\n"
                        f"المرسل يستخدم الإيموجيات فقط للتلميح، والبقية يكتبون الإجابة!\n"
                        f"🚫 **{sender['name']} ممنوع من كتابة النصوص!** استخدم الإيموجي فقط."
                    )
                except Exception:
                    pass
        return

    # --- Game callbacks: ايموجي cancel ---
    if data.startswith("emjc_"):
        parts = data.split("_")
        if len(parts) == 2:
            try:
                gid = int(parts[1])
            except ValueError:
                await cb.answer("❌ بيانات غير صالحة.", show_alert=True)
                return
            if gid != cid:
                await cb.answer("❌ هذه اللعبة غير متاحة هنا.", show_alert=True)
                return
            game = emoji_games.get(cid)
            if not game or game["phase"] != "registering":
                await cb.answer("⚠️ اللعبة غير موجودة أو انتهت بالفعل.", show_alert=True)
                return
            if not game["players"][0] or game["players"][0]["id"] != uid:
                await cb.answer("❌ فقط منشئ اللعبة يمكنه إلغاؤها.", show_alert=True)
                return
            emoji_games.pop(cid, None)
            try:
                await cb.message.edit_text("❌ تم إلغاء اللعبة.")
            except Exception:
                pass
            await cb.answer("✅ تم إلغاء اللعبة.", show_alert=True)
        return

    if data == "emj_noop":
        await cb.answer()
        return

    # --- Style previews ---
    if data.startswith("sv") or data.startswith("ss") or data.startswith("sb"):
        parts = data.split("_")
        creator_id = int(parts[-1])
        if uid != creator_id:
            await cb.answer("❌ عذراً، هذه اللوحة ليست لك ولا يمكنك التحكم بها.", show_alert=True)
            return
        action = parts[0]
        if action.startswith("sv"):
            sn = int(action[2])
            u = await client.get_users(uid)
            up = await _get_usernames(client, uid, u)
            cy = estimate_creation_year(uid)
            if sn == 1:
                txt = f"👤 **بطاقة البيانات الشخصية للمستخدم (الشكل 1):**\n\n🏷️ الاسم: {u.mention}\n🆔 رقم الحساب (ID): `{uid}`\n🌐 المعرفات: {up}\n💬 عدد الرسائل المرسلة: `147`\n📅 التقدير التقريبي لإنشاء الحساب: `{cy}`"
            elif sn == 2:
                txt = f"🌐 **[ ACCOUNT SECURITY CARD ] (الشكل 2)** 🌐\n━━━━━━━━━━━━━━━━━━━\n👤 الاسم ⇽ {u.mention}\n🆔 الآيدي ⇽ `{uid}`\n💎 اليوزرات ⇽ {up}\n💬 التفاعل ⇽ `147` رسالة\n📆 تاريخ الإنشاء ⇽ `{cy}`\n━━━━━━━━━━━━━━━━━━━"
            elif sn == 3:
                txt = f"⚜️ **بطاقة العضو (الشكل 3)** ⚜️\n\n✨ الـنـقـي: {u.mention}\n📎 الـمـعـرّف الـرقـمـي: `{uid}`\n🌍 الـرّابـط الـعـلـمـي: {up}\n📈 نـسـبـة الـحـضـور: `147` رسالة\n🕰️ الـتـأسـيـس: `{cy}`"
            elif sn == 4:
                txt = f"▫️ **ID CARD (الشكل 4)** ▫️\n\n▪️ User: {u.mention}\n▪️ ID: `{uid}`\n▪️ Handles: {up}\n▪️ Messages: `147`\n▪️ Year: `{cy}`"
            elif sn == 5:
                txt = f"▫️ **USER CARD (الشكل 5)** ▫️\n━━━━━━━━━━━━━━━━━━━\n👤 User     : {u.mention}\n🆔 ID       : `{uid}`\n🌐 Handles  : {up}\n💬 Messages : `147`\n📅 Created  : {cy}\n━━━━━━━━━━━━━━━━━━━"
            elif sn == 6:
                txt = f"▫️ **بطاقة المستخدم (الشكل 6)** ▫️\n━━━━━━━━━━━━━━━━━━━\n👤 الاسم    : {u.mention}\n🆔 الايدي   : `{uid}`\n🌐 المعرفات : {up}\n💬 الرسائل  : `147`\n📅 السنة    : {cy}\n━━━━━━━━━━━━━━━━━━━"
            elif sn == 7:
                txt = f"╔══════ PROFILE ══════╗\n👤 User     : {u.mention}\n🆔 ID       : `{uid}`\n🌐 Handles  : {up}\n💬 Messages : `147`\n📅 Created  : {cy}\n╚══════════════════════╝"
            else:
                txt = f"📇 {u.mention}\n🆔 `{uid}` • 💬 `147`\n🌐 {up}\n📅 {cy}"
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("حفظ هذا الشكل ✅", callback_data=f"ss{sn}_{creator_id}")],
                [InlineKeyboardButton("🔙 رجوع", callback_data=f"sb_{creator_id}")]
            ])
            await cb.message.edit_text(f"👀 **معاينة الشكل {sn}:**\n\n{txt}", reply_markup=kb)
            await cb.answer()
            return
        if action.startswith("ss"):
            sn = int(action[2])
            await DB.execute("UPDATE groups SET id_style=? WHERE chat_id=?", (sn, cid), commit=True)
            await cb.message.edit_text(f"✅ **تم حفظ وتطبيق الشكل {sn} لبطاقة الايدي في هذه المجموعة بنجاح!**")
            await cb.answer("تم حفظ التنسيق بنجاح", show_alert=True)
            return
        if action.startswith("sb"):
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("الشكل 1", callback_data=f"sv1_{creator_id}"), InlineKeyboardButton("الشكل 2", callback_data=f"sv2_{creator_id}")],
                [InlineKeyboardButton("الشكل 3", callback_data=f"sv3_{creator_id}"), InlineKeyboardButton("الشكل 4", callback_data=f"sv4_{creator_id}")],
                [InlineKeyboardButton("الشكل 5", callback_data=f"sv5_{creator_id}"), InlineKeyboardButton("الشكل 6", callback_data=f"sv6_{creator_id}")],
                [InlineKeyboardButton("الشكل 7", callback_data=f"sv7_{creator_id}"), InlineKeyboardButton("الشكل 8", callback_data=f"sv8_{creator_id}")]
            ])
            await cb.message.edit_text("🎨 **لوحة اختيار كليشة الـ ID للمجموعة:**\n\nيرجى الضغط على الأشكال التالية لمعاينتها واختيار الأنسب لمجموعتك:", reply_markup=kb)
            await cb.answer()
            return

    # --- Group settings (اعدادات القروب) ---
    if data.startswith("gs_"):
        parts = data.split("_")
        creator_id = int(parts[-1])
        if uid != creator_id:
            await cb.answer("❌ هذه اللوحة ليست لك.", show_alert=True)
            return
        action = "_".join(parts[1:-1])
        try:
            chat = await client.get_chat(cid)
            perms = chat.permissions
        except Exception:
            await cb.answer("❌ تعذر جلب الصلاحيات.", show_alert=True)
            return

        if action == "gen":
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{'✅' if perms.can_pin_messages else '❌'} تثبيت الرسائل", callback_data=f"gs_set_pin_{creator_id}")],
                [InlineKeyboardButton(f"{'✅' if perms.can_invite_users else '❌'} اضافة الاعضاء", callback_data=f"gs_set_invite_{creator_id}")],
                [InlineKeyboardButton(f"{'✅' if perms.can_change_info else '❌'} تغيير المعلومات", callback_data=f"gs_set_info_{creator_id}")],
                [InlineKeyboardButton(f"{'✅' if perms.can_send_messages else '❌'} الرسائل النصية", callback_data=f"gs_set_sendmsg_{creator_id}")],
                [InlineKeyboardButton("🔙 رجوع", callback_data=f"gs_back_{creator_id}")]
            ])
            await cb.message.edit_text("• أختار نوع الصلاحيات التي تريد تعديلها للمجموعة", reply_markup=kb)
            await cb.answer()
            return

        if action == "med":
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{'✅' if perms.can_send_other_messages else '❌'} الملصقات والمتحركات", callback_data=f"gs_set_other_{creator_id}")],
                [InlineKeyboardButton(f"{'✅' if perms.can_send_media_messages else '❌'} الملفات الصوتية", callback_data=f"gs_set_audio_{creator_id}")],
                [InlineKeyboardButton(f"{'✅' if perms.can_send_media_messages else '❌'} الرسائل الصوتية", callback_data=f"gs_set_voice_{creator_id}")],
                [InlineKeyboardButton(f"{'✅' if perms.can_send_media_messages else '❌'} الملفات", callback_data=f"gs_set_file_{creator_id}")],
                [InlineKeyboardButton(f"{'✅' if perms.can_send_media_messages else '❌'} الفيديو", callback_data=f"gs_set_video_{creator_id}")],
                [InlineKeyboardButton(f"{'✅' if perms.can_send_polls else '❌'} الاستفتاءات", callback_data=f"gs_set_polls_{creator_id}")],
                [InlineKeyboardButton(f"{'✅' if perms.can_send_media_messages else '❌'} الصور", callback_data=f"gs_set_photo_{creator_id}")],
                [InlineKeyboardButton("🔙 رجوع", callback_data=f"gs_back_{creator_id}")]
            ])
            await cb.message.edit_text("• صلاحيات الوسائط", reply_markup=kb)
            await cb.answer()
            return

        if action == "back":
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("الصلاحيات العامة", callback_data=f"gs_gen_{creator_id}")],
                [InlineKeyboardButton("صلاحيات الوسائط", callback_data=f"gs_med_{creator_id}")]
            ])
            await cb.message.edit_text("• أختار نوع الصلاحيات التي تريد تعديلها للمجموعة", reply_markup=kb)
            await cb.answer()
            return

        if action.startswith("set_"):
            field = action[4:]

            # Telegram-permission fields (audio/voice/file/video/photo map to can_send_media_messages)
            toggles = {}
            if field == "pin":
                toggles["can_pin_messages"] = not perms.can_pin_messages
            elif field == "invite":
                toggles["can_invite_users"] = not perms.can_invite_users
            elif field == "info":
                toggles["can_change_info"] = not perms.can_change_info
            elif field == "sendmsg":
                toggles["can_send_messages"] = not perms.can_send_messages
            elif field == "other":
                toggles["can_send_other_messages"] = not perms.can_send_other_messages
            elif field in ("audio", "voice", "file", "video", "photo"):
                toggles["can_send_media_messages"] = not perms.can_send_media_messages
            elif field == "polls":
                toggles["can_send_polls"] = not perms.can_send_polls
            try:
                new_perms = ChatPermissions(
                    can_send_messages=toggles.get("can_send_messages", perms.can_send_messages),
                    can_send_media_messages=toggles.get("can_send_media_messages", perms.can_send_media_messages),
                    can_send_polls=toggles.get("can_send_polls", perms.can_send_polls),
                    can_send_other_messages=toggles.get("can_send_other_messages", perms.can_send_other_messages),
                    can_add_web_page_previews=perms.can_add_web_page_previews,
                    can_change_info=toggles.get("can_change_info", perms.can_change_info),
                    can_invite_users=toggles.get("can_invite_users", perms.can_invite_users),
                    can_pin_messages=toggles.get("can_pin_messages", perms.can_pin_messages),
                )
                await client.set_chat_permissions(cid, new_perms)
                await cb.answer("✅ تم تغيير الصلاحية بنجاح!")
                chat = await client.get_chat(cid)
                perms = chat.permissions
                if field in ("pin", "invite", "info", "sendmsg"):
                    kb = InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"{'✅' if perms.can_pin_messages else '❌'} تثبيت الرسائل", callback_data=f"gs_set_pin_{creator_id}")],
                        [InlineKeyboardButton(f"{'✅' if perms.can_invite_users else '❌'} اضافة الاعضاء", callback_data=f"gs_set_invite_{creator_id}")],
                        [InlineKeyboardButton(f"{'✅' if perms.can_change_info else '❌'} تغيير المعلومات", callback_data=f"gs_set_info_{creator_id}")],
                        [InlineKeyboardButton(f"{'✅' if perms.can_send_messages else '❌'} الرسائل النصية", callback_data=f"gs_set_sendmsg_{creator_id}")],
                        [InlineKeyboardButton("🔙 رجوع", callback_data=f"gs_back_{creator_id}")]
                    ])
                    await cb.message.edit_text("• أختار نوع الصلاحيات التي تريد تعديلها للمجموعة", reply_markup=kb)
                else:
                    kb = InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"{'✅' if perms.can_send_other_messages else '❌'} الملصقات والمتحركات", callback_data=f"gs_set_other_{creator_id}")],
                        [InlineKeyboardButton(f"{'✅' if perms.can_send_media_messages else '❌'} الملفات الصوتية", callback_data=f"gs_set_audio_{creator_id}")],
                        [InlineKeyboardButton(f"{'✅' if perms.can_send_media_messages else '❌'} الرسائل الصوتية", callback_data=f"gs_set_voice_{creator_id}")],
                        [InlineKeyboardButton(f"{'✅' if perms.can_send_media_messages else '❌'} الملفات", callback_data=f"gs_set_file_{creator_id}")],
                        [InlineKeyboardButton(f"{'✅' if perms.can_send_media_messages else '❌'} الفيديو", callback_data=f"gs_set_video_{creator_id}")],
                        [InlineKeyboardButton(f"{'✅' if perms.can_send_polls else '❌'} الاستفتاءات", callback_data=f"gs_set_polls_{creator_id}")],
                        [InlineKeyboardButton(f"{'✅' if perms.can_send_media_messages else '❌'} الصور", callback_data=f"gs_set_photo_{creator_id}")],
                        [InlineKeyboardButton("🔙 رجوع", callback_data=f"gs_back_{creator_id}")]
                    ])
                    await cb.message.edit_text("• صلاحيات الوسائط", reply_markup=kb)
            except Exception as e:
                await cb.answer(f"❌ تعذر تغيير الصلاحية: {e}", show_alert=True)
            return
        return

    # --- Command lists ---
    if data.startswith("c") and "_" in data and len(data) > 2:
        parts = data.split("_")
        creator_id = int(parts[-1])
        if uid != creator_id:
            await cb.answer("❌ عذراً، هذه القائمة ليست لك ولا يمكنك التحكم بها.", show_alert=True)
            return
        action = parts[0]

        if action == "cb":
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("1 ◂", callback_data=f"c1_{creator_id}"), InlineKeyboardButton("2 ◂", callback_data=f"c2_{creator_id}"), InlineKeyboardButton("3 ◂", callback_data=f"c3_{creator_id}")],
                [InlineKeyboardButton("4 ◂", callback_data=f"c4_{creator_id}"), InlineKeyboardButton("5 ◂", callback_data=f"c5_{creator_id}"), InlineKeyboardButton("6 ◂", callback_data=f"c6_{creator_id}")]
            ])
            await cb.message.edit_text(
                "‌‌‏أهلاً بك عزيزي في قائمة الاوامر :\n"
                "━━━━━━━━━━━━━━━━\n"
                " ◂ 1 : اوامر الادمنيه ، الرفع ، المسح\n"
                " ◂ 2 : اوامر رؤية الاعدادات ، وضع الاعدادات\n"
                " ◂ 3 : اوامر القفل ، الحماية ، الردود\n"
                " ◂ 4 : اوامر التفعيل ، التثبيت ، المنشن\n"
                " ◂ 5 : اوامر التسليه ، الزواج ، التنظيف\n"
                " ◂ 6 :اوامر الخدميه ، الاشتراك الاجباري\n"
                "• لـرؤيـة قائمة الالعاب اكتب : الالعاب\n"
                "━━━━━━━━━━━━━━━━",
                reply_markup=kb
            )
            await cb.answer()
            return

        txts = {"c1": COMMAND_1, "c2": COMMAND_2, "c3": COMMAND_3, "c4": COMMAND_4, "c5": COMMAND_5, "c6": COMMAND_6, "cg": GAMES_LIST}
        if action in txts:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 الرجوع", callback_data=f"cb_{creator_id}")]])
            await cb.message.edit_text(txts[action].strip(), reply_markup=kb)
            await cb.answer()
            return

    # --- Whisper show ---
    if data.startswith("ws_"):
        wid = int(data[3:])
        row = await DB.execute("SELECT chat_id, sender_id, target_id, message_text FROM whispers WHERE id=?", (wid,), fetchone=True)
        if not row:
            await cb.answer("❌ هذه الهمسة غير موجودة.", show_alert=True)
            return
        chat_id, sender_id, target_id, msg_text = row
        if uid not in (sender_id, target_id):
            await cb.answer("❌ هذه الهمسة ليست لك.", show_alert=True)
            return
        if not msg_text:
            await cb.answer("❌ لم يتم إرسال الهمسة بعد.", show_alert=True)
            return
        await DB.execute("UPDATE whispers SET status='delivered' WHERE id=?", (wid,), commit=True)
        from_user = await client.get_users(sender_id)
        sender_name = from_user.first_name or "المستخدم"
        await cb.answer(f"• الهمسة من {sender_name}:\n\n{msg_text}", show_alert=True)
        return

    # --- Link buttons ---
    _, lv = await get_role(cid, uid, client)
    if lv < 3:
        await cb.answer("❌ عذراً، هذا الإجراء مخصص للمشرفين فقط في هذه المجموعة.", show_alert=True)
        return

    if data == "cdl":
        try:
            link = await client.create_chat_invite_link(cid, creates_join_request=False)
            await cb.message.edit_text(f"🔗 **تم إنشاء رابط انضمام مباشر بنجاح:**\n{link.invite_link}")
        except Exception as e:
            await cb.message.edit_text(f"❌ تعذر إنشاء الرابط: `{e}`")
    elif data == "crl":
        try:
            link = await client.create_chat_invite_link(cid, creates_join_request=True)
            await cb.message.edit_text(f"📩 **تم إنشاء رابط طلبات انضمام بنجاح:**\n{link.invite_link}")
        except Exception as e:
            await cb.message.edit_text(f"❌ تعذر إنشاء الرابط: `{e}`")
    elif data.startswith("nolink_"):
        await cb.answer("هذه المجموعة لا تملك رابط دعوة علني حالياً.", show_alert=True)


if __name__ == "__main__":
    log.info("نظام الحماية والرقابة الإدارية قيد التشغيل والعمل الآن")

    def _run_whisper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        whisper_app.run()

    t = threading.Thread(target=_run_whisper, daemon=True)
    t.start()
    app.run()
