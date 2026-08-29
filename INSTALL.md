# INSTALL.md · הוראות ל-Claude שמתקין/ה את Webinar-OS

הקובץ הזה מיועד ל-Claude Code של המשתמש/ת. המשתמש/ת הדביק/ה פרומפט שמפנה לכאן. בצע/י את הצעדים לפי הסדר, דווח/י בעברית, ואל תעשה/י שום דבר מעבר.

## מה מתקינים

תיקיית הסקיל `skills/webinar-os/` (מהחבילה הזו) לתוך `.claude/skills/webinar-os/` בפרויקט של המשתמש/ת. זה כל ההתקנה. אין תלויות, אין מפתחות, אין `pip install`.

## לפני הצעדים
- כתיבה לתוך `.claude/` מקפיצה פרומפט הרשאה של Claude Code. זה צפוי: אומרים למשתמש/ת בשורה אחת "תאשר/י את הבקשה לכתוב ל-.claude" וממשיכים. לא מנסים לעקוף.
- אם החבילה יושבת מחוץ לתיקיית הפרויקט (למשל "הורדות"), כלי הקריאה יחסמו אותה. מבקשים מהמשתמש/ת להעביר את תיקיית `webinar-os` לתוך תיקיית הפרויקט, ואז ממשיכים.
- **איזה מעטפת (shell) מריצה את הפקודות?** כלי ה-Bash של Claude Code מריץ bash: ב-Mac וב-Linux תמיד, וב-Windows דרך Git Bash (ברירת המחדל כשמותקן Git for Windows). לכן הפקודות בקובץ הזה כתובות ל-bash עם לוכסנים קדימה (`/`), וזה עובד בכל שלוש המערכות. ב-Windows מחליפים רק `python3` ב-`python`. את בלוק ה-PowerShell מריצים **רק** אם יש לך כלי PowerShell ולא כלי Bash. לא מערבבים: לוכסנים אחורה (`\`) בתוך bash נמחקים והפקודה נכשלת.

## צעדים

1. **אתר/י את החבילה.** הנתיב שהמשתמש/ת נתן/ה הוא תיקיית `webinar-os` (זו שמכילה `README.md`, `INSTALL.md`, `skills/`). קיבלת נתיב לזיפ? פתח/י אותו קודם, בתוך תיקיית הפרויקט. הנתיב הצפוי הוא בתוך הפרויקט: `./webinar-os` (כלומר `<פרויקט>/webinar-os`). ב-Windows זה נראה בסייר הקבצים כמו `C:\Users\<שם>\<פרויקט>\webinar-os`, ובפקודות bash מחליפים כל לוכסן אחורי (`\`) בלוכסן קדימה (`/`). התיקייה עדיין יושבת ב"הורדות" (`~/Downloads/webinar-os` או `C:\Users\<שם>\Downloads\webinar-os`)? זה בדיוק המקרה החסום שתואר למעלה: מבקשים מהמשתמש/ת להעביר אותה לתוך הפרויקט, ורק אז ממשיכים.

2. **אתר/י את הפרויקט.** ספריית העבודה הנוכחית של Claude Code היא הפרויקט. אם אין בה `.claude/`, צור/י. ההתקנה בבסיס היא לפרויקט הזה בלבד. רוצים את הסקיל בכל הפרויקטים? ראה/י "התקנה גלובלית" בסוף הקובץ, ואז כל הצעדים זהים עם היעד הגלובלי.

3. **העתק/י.** מריצים את הבלוק כולו, כולל שורת הגיבוי: אם כבר קיימת גרסה קודמת ב-`.claude/skills/webinar-os` (ריצה שנייה, או שדרוג), השורה מזיזה אותה ל-`webinar-os.bak-<תאריך>` לפני ההעתקה. בלי זה ההעתקה על יעד קיים מקננת (`webinar-os/webinar-os`) ומשאירה את הגרסה הישנה פעילה בלי שום שגיאה.
   כלי Bash (Mac / Linux / Windows עם Git Bash):
   ```bash
   mkdir -p .claude/skills
   if [ -d .claude/skills/webinar-os ]; then mv .claude/skills/webinar-os ".claude/skills/webinar-os.bak-$(date +%F-%H%M)"; fi
   cp -R "<חבילה>/skills/webinar-os" .claude/skills/webinar-os
   ```
   כלי PowerShell בלבד (Windows בלי Git Bash):
   ```powershell
   New-Item -ItemType Directory -Force .claude/skills | Out-Null
   if (Test-Path .claude/skills/webinar-os) { Move-Item .claude/skills/webinar-os ".claude/skills/webinar-os.bak-$(Get-Date -Format yyyy-MM-dd-HHmm)" }
   Copy-Item -Recurse -Force "<חבילה>/skills/webinar-os" ".claude/skills/webinar-os"
   ```
   בדיקה מיד אחרי ההעתקה: התיקייה `.claude/skills/webinar-os/webinar-os` אסור שתהיה קיימת. קיימת? זה קינון: מוחקים את `.claude/skills/webinar-os` כולה ומריצים את הבלוק שוב. הגיבוי `webinar-os.bak-<תאריך>` נשאר עד שבדיקת doctor בצעד 4 עוברת, ואז אפשר למחוק אותו.

4. **אמת/י.** מריצים את הבדיקה (ספרייה סטנדרטית בלבד):
   ```bash
   python3 .claude/skills/webinar-os/scripts/doctor.py
   ```
   ב-Windows (בכל מעטפת, Git Bash או PowerShell): `python .claude/skills/webinar-os/scripts/doctor.py`.
   בהתקנה גלובלית: `python3 ~/.claude/skills/webinar-os/scripts/doctor.py`.
   מציגים למשתמש/ת את הדוח כמו שהוא. שורות `!!` = לתקן לפי ההוראה בשורה. שורת `..` על דפדפן = מידע, לא חוסם.
   אין `python3`? נסה/י `python`. אין Python בכלל? אמור/י למשתמש/ת: python.org/downloads (ב-Windows לסמן "Add python.exe to PATH"), לפתוח טרמינל חדש, ולהריץ שוב. בלי Python אין רינדור של דפים ואין בדיקה: מתקינים Python ואז ממשיכים. עד אז אפשר להריץ רק את שלב 1 של הסקיל (מחקר). לא בונים HTML ביד במקום הרינדור.

5. **צור/י את תיקיית הפלט** אם אינה קיימת: `outputs/webinars/`.

6. **דווח/י** למשתמש/ת, בעברית, בדיוק ככה (בהתקנה גלובלית מחליפים את הנתיב ב-`~/.claude/skills/webinar-os/`):
   - "הסקיל webinar-os מותקן ב-`.claude/skills/webinar-os/`."
   - "הפעלה: `/webinar-os` בשיחה חדשה (כדי שהסקיל ייטען). זה מתחיל מיד בשאלה הראשונה מתוך 8."
   - "כדאי להכין: תאריך ושעה, מי מעביר/ה ומה ההוכחה, ולינק למדיניות הפרטיות שלך."
   - "נעצרת באמצע? `/webinar-os המשך`."

## התקנה גלובלית (אופציונלי, לכל הפרויקטים)

אותם צעדים בדיוק, רק שבכל מקום שכתוב `.claude/skills/webinar-os` היעד הוא `~/.claude/skills/webinar-os`. ב-bash (כולל Git Bash ב-Windows) `~` עובד כמו שהוא. ב-PowerShell כותבים `$env:USERPROFILE/.claude/skills/webinar-os` (לא `%USERPROFILE%`, זה תחביר של cmd). גם בדיקת doctor וגם הדיווח בצעד 6 מצביעים אז על הנתיב הגלובלי.

## מה לא לעשות

- לא להתקין חבילות, לא להריץ `pip install`, לא לשנות קבצים אחרים בפרויקט.
- לא לבקש מפתחות API. הבסיס לא צריך אף אחד.
- לא להריץ את הסקיל עצמו בתוך ההתקנה. ההפעלה הראשונה היא בשיחה חדשה.
