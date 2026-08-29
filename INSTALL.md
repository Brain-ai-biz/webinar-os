# INSTALL.md · הוראות ל-Claude שמתקין/ה את Webinar-OS

הקובץ הזה מיועד ל-Claude Code של המשתמש/ת. המשתמש/ת הדביק/ה פרומפט שמפנה לכאן. בצע/י את הצעדים לפי הסדר, דווח/י בעברית, ואל תעשה/י שום דבר מעבר.

## מה מתקינים

תיקיית הסקיל `skills/webinar-os/` (מהחבילה הזו) לתוך `.claude/skills/webinar-os/` בפרויקט של המשתמש/ת. זה כל ההתקנה. אין תלויות, אין מפתחות, אין `pip install`.

## צעדים

1. **אתר/י את החבילה.** הנתיב שהמשתמש/ת נתן/ה הוא תיקיית `webinar-os` (זו שמכילה `README.md`, `INSTALL.md`, `skills/`). קיבלת נתיב לזיפ? פתח/י אותו קודם. ב-Windows הנתיב נראה כמו `C:\Users\<שם>\Downloads\webinar-os`; ב-Mac כמו `~/Downloads/webinar-os`.

2. **אתר/י את הפרויקט.** ספריית העבודה הנוכחית של Claude Code היא הפרויקט. אם אין בה `.claude/`, צור/י. רוצים את הסקיל בכל הפרויקטים? היעד הוא `~/.claude/skills/webinar-os/` (Windows: `%USERPROFILE%\.claude\skills\webinar-os`). שאל/י רק אם לא ברור.

3. **העתק/י.**
   Mac / Linux:
   ```bash
   mkdir -p .claude/skills
   cp -R "<חבילה>/skills/webinar-os" .claude/skills/webinar-os
   ```
   Windows (PowerShell):
   ```powershell
   New-Item -ItemType Directory -Force .claude\skills | Out-Null
   Copy-Item -Recurse -Force "<חבילה>\skills\webinar-os" ".claude\skills\webinar-os"
   ```
   כבר קיימת גרסה קודמת? גבה/י אותה ל-`.claude/skills/webinar-os.bak-<תאריך>` והחלף/י.

4. **אמת/י.** מריצים את הבדיקה (ספרייה סטנדרטית בלבד):
   ```bash
   python3 .claude/skills/webinar-os/scripts/doctor.py
   ```
   ב-Windows: `python .claude\skills\webinar-os\scripts\doctor.py`.
   מציגים למשתמש/ת את הדוח כמו שהוא. שורות `!!` = לתקן לפי ההוראה בשורה. שורת `..` על דפדפן = מידע, לא חוסם.
   אין `python3`? נסה/י `python`. אין Python בכלל? אמור/י למשתמש/ת: python.org/downloads (ב-Windows לסמן "Add python.exe to PATH"), לפתוח טרמינל חדש, ולהריץ שוב. בלי Python הדפים ייבנו על ידך ישירות מהתבניות (אפשרי, פשוט יותר איטי).

5. **צור/י את תיקיית הפלט** אם אינה קיימת: `outputs/webinars/`.

6. **דווח/י** למשתמש/ת, בעברית, בדיוק ככה:
   - "הסקיל webinar-os מותקן ב-`.claude/skills/webinar-os/`."
   - "הפעלה: `/webinar-os` בשיחה חדשה (כדי שהסקיל ייטען). זה מתחיל מיד בשאלה הראשונה מתוך 8."
   - "כדאי להכין: תאריך ושעה, מי מעביר/ה ומה ההוכחה, ולינק למדיניות הפרטיות שלך."
   - "נעצרת באמצע? `/webinar-os המשך`."

## מה לא לעשות

- לא להתקין חבילות, לא להריץ `pip install`, לא לשנות קבצים אחרים בפרויקט.
- לא לבקש מפתחות API. הבסיס לא צריך אף אחד.
- לא להריץ את הסקיל עצמו בתוך ההתקנה. ההפעלה הראשונה היא בשיחה חדשה.
