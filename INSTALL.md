# INSTALL.md · הוראות ל-Claude שמתקין/ה את Webinar-OS

הקובץ הזה מיועד ל-Claude Code של המשתמש/ת. המשתמש/ת הדביק/ה פרומפט שמפנה לכאן. בצע/י את הצעדים לפי הסדר, דווח/י בעברית, ואל תעשה/י שום דבר מעבר.

## מה מתקינים

תיקיית הסקיל `skills/webinar-os/` (מהחבילה הזו) לתוך `.claude/skills/webinar-os/` בפרויקט של המשתמש/ת. זה כל ההתקנה. אין תלויות להתקין, אין מפתחות להגדיר.

## צעדים

1. **אתר/י את החבילה.** הנתיב שהמשתמש/ת נתן/ה הוא תיקיית `webinar-os` (זו שמכילה `README.md`, `INSTALL.md`, `skills/`). אם קיבלת נתיב לזיפ, פתח/י אותו קודם.

2. **אתר/י את הפרויקט.** ספריית העבודה הנוכחית של Claude Code היא הפרויקט. אם אין בה `.claude/`, צור/י. אם המשתמש/ת רוצה את הסקיל בכל הפרויקטים, היעד הוא `~/.claude/skills/webinar-os/` במקום (שאל/י רק אם לא ברור).

3. **העתק/י.**
   ```bash
   mkdir -p .claude/skills
   cp -R "<חבילה>/skills/webinar-os" .claude/skills/webinar-os
   ```
   ב-Windows (PowerShell): `Copy-Item -Recurse "<חבילה>\skills\webinar-os" ".claude\skills\webinar-os"`.
   אם כבר קיימת גרסה קודמת, גבה/י אותה ל-`.claude/skills/webinar-os.bak-<תאריך>` והחלף/י.

4. **אמת/י.** חייבים להתקיים:
   ```
   .claude/skills/webinar-os/SKILL.md
   .claude/skills/webinar-os/config.template.json
   .claude/skills/webinar-os/reference/   (7 קבצים)
   .claude/skills/webinar-os/templates/   (5 קבצים)
   .claude/skills/webinar-os/scripts/render_pages.py
   ```
   ובדיקת ריצה של הסקריפט (ספרייה סטנדרטית בלבד, Python 3.9+):
   ```bash
   python3 .claude/skills/webinar-os/scripts/render_pages.py --help
   ```
   אין `python3`? נסה/י `python`. אין Python בכלל? אמור/י למשתמש/ת שהדפים ייבנו על ידך ישירות מהתבניות (אפשרי, פשוט יותר איטי), והצע/י להתקין Python מ-python.org כשיהיה נוח.

5. **צור/י את תיקיית הפלט** אם אינה קיימת: `outputs/webinars/`.

6. **דווח/י** למשתמש/ת, בעברית:
   - "הסקיל webinar-os מותקן ב-`.claude/skills/webinar-os/`."
   - "הפעלה: `/webinar-os` (או 'תבנה לי וובינר'). בשיחה חדשה, כדי שהסקיל ייטען."
   - "מה כדאי להכין לפני: תאריך ושעה, מה מוכרים בקצה (או כלום), כתובת מדיניות הפרטיות שלך, לוגו וצבע אם יש."
   - "אופציונלי, לא חובה: אם יש לך מפתחות API (וואטסאפ, זום, מערכת דיוור, Bitly) שים/י אותם ב-`.env` בפרויקט והסקיל ישתמש בהם. בלי זה הכל עדיין עובד במסלול הידני."

## מה לא לעשות

- לא להתקין חבילות, לא להריץ `pip install`, לא לשנות קבצים אחרים בפרויקט.
- לא לבקש מפתחות API. ההתקנה לא צריכה אף אחד.
- לא להריץ את הסקיל עצמו בתוך ההתקנה. ההפעלה הראשונה היא בשיחה חדשה.
