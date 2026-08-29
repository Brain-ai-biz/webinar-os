# כשמשהו נתקע: 11 התקלות הצפויות

**מתי לטעון אותי:** בכל שגיאה, לפני שמנסים "עוד משהו". למשתתף/ת: "הדבק/י ל-Claude: קרא/י את reference/troubleshoot.md בסקיל webinar-os ותקן/י".

| # | סימפטום | סיבה | תיקון |
|---|---|---|---|
| 0 | `claude: command not found` (Mac) / `'claude' is not recognized` (Windows) | Claude Code לא מותקן, או שהטרמינל נפתח לפני ההתקנה ולא מכיר את הפקודה | מתקינים לפי claude.com/code, סוגרים את הטרמינל ופותחים חדש, מריצים `claude` פעם אחת ומתחברים לחשבון. רק אז חוזרים לצעד 3 ב-README |
| 1 | `python3: command not found` | ב-Windows הפקודה היא `python`; ב-Mac ישן אין Python | מנסים `python`. אין בכלל? python.org/downloads, ב-Windows לסמן "Add python.exe to PATH", לפתוח טרמינל חדש |
| 2 | `/webinar-os` לא מזוהה | הסקיל לא בתיקייה הנכונה, או שהשיחה נפתחה לפני ההתקנה | לוודא `.claude/skills/webinar-os/SKILL.md` בתיקייה שבה Claude Code פתוח. לפתוח שיחה חדשה |
| 3 | `/webinar-os המשך` מתחיל מההתחלה | אין `state.json` או שה-slug שונה | לפתוח `outputs/webinars/`, לוודא שיש תיקייה עם `state.json`; אם יש כמה, לומר ל-Claude איזו |
| 4 | `render_pages.py` מדפיס `x .../copy.json not found` (עם `--only pages`), או `(no copy.json yet -> pages skipped)` ומדלג על הדפים | עוד לא נכתב הקופי (שלב 3) | לרנדר עם `--only deck`, או להשלים את שלב 3 |
| 5 | `missing key` ברינדור | חסר סעיף ב-`copy.json` / `deck.json` | להשלים לפי `copy-blocks.md` §2 / `deck-structure.md` §2. הרינדור לא נכשל, הסעיף פשוט ריק |
| 6 | הדף מציג כפתור ולא טופס | אין `form_action` בקונפיג | רוצים גיליון? `manual-paths.md` §1, ואז `render_pages.py` שוב |
| 7 | הטופס "שולח" אבל אין שורה בגיליון | `form_action` עם `/viewform` במקום `/formResponse`, או מזהי `entry.` שגויים | לתקן לפי `manual-paths.md` §1, שלבים 3-4 |
| 8 | תיבת ההסכמה בלי לינק למדיניות | `privacy_url` ריק | להוסיף לקונפיג ולרנדר שוב. אין מדיניות? לא עולים לאוויר עם טופס |
| 9 | הפונט נראה אחר / ריבועים | Google Fonts לא נטען (אין אינטרנט / חומת אש) | הדפדפן משתמש בפונט המערכת. העימוד זהה, זה תקין. עם אינטרנט זה יתוקן לבד |
| 10 | הדף באוויר אבל `thank-you/` נותן 404 | הועלה `index.html` בלבד | להעלות את **תיקיית `landing` כולה** (`manual-paths.md` §4) |

## שלושה כללים כשמתקנים
1. תיקון אחד בכל פעם, ומריצים שוב את אותה פקודה.
2. כל שינוי נכנס ל-`config.json` / `copy.json` / `deck.json` ומרנדרים מחדש. לא עורכים את `landing/` או `deck.html` ביד.
3. לא ממציאים תוצאה. משהו לא עבד = אומרים מה, ומה הצעד הידני.
