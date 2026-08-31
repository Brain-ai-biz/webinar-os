# קריאייטיבים וקופי למודעות (שלב 10)

המסמך הזה הוא המפרט של שלב 10. קוראים אותו כשמגיעים לשלב, לא לפני.
המטרה: אחרי שהדף באוויר, לצאת עם חבילה אחת שאפשר להדביק בכל ערוץ, וכל טקסט כבר כתוב במלואו.

## תוכן עניינים

- סעיף 0: סדר העבודה
- סעיף 1: המפתח
- סעיף 2: כיווני מסר (עצירת אישור)
- סעיף 3: מפרט הערוצים
- סעיף 4: חוקי הקריאייטיב, שני התפקידים של התמונה, ומה אסור
- סעיף 5: ספריית הכיוונים (עשרה כיוונים עם ניסוח מלא)
- סעיף 6: מודעה ממומנת: מה משתנה
- סעיף 7: רף האיכות ולולאת הבחירה
- סעיף 8: הסקריפט
- סעיף 9: הלבשת השורה העברית

---

## 0. סדר העבודה (לא משנים)

1. שואלים אילו ערוצים. אפשר לבחור כמה: אינסטגרם סטורי · פוסט לפייסבוק · הודעה לוואטסאפ · דיוור במייל · מודעה ממומנת.
   ברירת המחדל: הכל חוץ מהמודעה הממומנת.
2. שואלים פעם אחת על מפתח של OpenAI (סעיף 1). אין מפתח? ממשיכים, והטקסטים נכתבים במלואם.
3. **מסרים קודם, תמונות אחר כך.** כותבים 4 עד 6 כיווני מסר קצרים, המשתמש/ת בוחר/ת 2 עד 3. זו עצירת אישור.
4. מהכיוונים שאושרו כותבים את הפוסטים המלאים לכל ערוץ שנבחר, ומייצרים את הקריאייטיבים התואמים.
5. מוסרים `ads.md` (כל הטקסטים, כל אחד בבלוק העתקה), תיקיית `creatives/` עם התמונות, וטבלה של מה הולך לאן.

---

## 1. המפתח (שואלים פעם אחת, ולא חוסמים)

מנסחים בשורה אחת: כדי לייצר את התמונות צריך מפתח של OpenAI, מנפיקים אותו ב-platform.openai.com בעמוד API keys.
שומרים אותו ל-`.env` (`env_set.py OPENAI_API_KEY "<המפתח>"`) ואומרים שורה אחת יבשה: "נשמר ל-.env, לא צריך להדביק שוב". בלי אזהרות אבטחה, בלי "זה מסוכן", בלי להציע להחליף מפתח.

אין מפתח? אומרים בפשטות: הטקסטים נכתבים במלואם, רק התמונות מדולגות, ואפשר לייצר אותן בכל רגע אחר עם אותה פקודה.
לא מפצירים, לא חוזרים על השאלה, ולא עוצרים את השלב.

---

## 2. כיווני מסר (עצירת אישור)

כיוון מסר = שורה אחת של זווית, ואחריה שורת המכה (הפאנץ') שהיא תישא.
כותבים 4 עד 6 כאלה, מבוססים על `research.md`, `copy.json` והקול של המשתמש/ת, ומציגים אותם ממוספרים.
מבקשים לבחור 2 עד 3. אפשר לבקש שינוי בניסוח, מתקנים ומראים שוב.

דוגמה למבנה: "הזווית: מה שהם כבר ניסו ולא עבד. הפאנץ': ניסית הכל, חוץ מהדבר אחד שבאמת משנה."

---

## 3. מפרט הערוצים (הכללים, לא המלצות)

| ערוץ | אורך | קריאייטיב | מקצב |
|------|------|-----------|------|
| אינסטגרם סטורי | כיתוב קצר | 9:16 | 3 עד 4 מקטעים זעירים, כל אחד בשורה משלו |
| פייסבוק | כ-800 עד 900 תווים | 1:1 | סיפור קטן: וו, כאב, תפנית, מה מקבלים, תאריך, לינק |
| וואטסאפ | כ-800 עד 900 תווים | 1:1 | אישי וצפוף יותר מפייסבוק, שורת רווח כל משפט או שניים, לינק אחד בסוף |
| דיוור | כ-800 עד 1200 תווים | 1:1 (לא חובה) | אוויר, כותרות משנה, שורה קצרה שעומדת לבד, שורה שחוזרת למקצב |
| מודעה ממומנת | עד כ-125 תווים לפני הקיפול | 1:1 | כותרת אחת עד 40 תווים, קריאה לפעולה אחת |

פירוט:

- **אינסטגרם סטורי:** על התמונה שורה אחת בלבד. הכיתוב מפורק ל-3 עד 4 מקטעים זעירים, כל מקטע בשורה נפרדת, כדי שייקרא מהר בנייד.
- **פייסבוק:** יש מקום לספר. שורת וו ראשונה, שתיים או שלוש שורות של הכאב, התפנית, מה מקבלים, התאריך והשעה, ואז הלינק.
- **וואטסאפ:** אותו אורך בערך, אבל אישי וישיר יותר, כאילו נכתב לאדם אחד. שורת רווח כל משפט או שניים. לינק אחד, בסוף.
- **דיוור:** שורת נושא עד 50 תווים, ואחריה שורת תצוגה מקדימה. בגוף המייל משחקים עם הטקסט עצמו: פסקה ארוכה ואחריה שורה קצרה שעומדת לבד, שורה שחוזרת פעמיים למקצב, כותרות משנה, ולפעמים מילה אחת בשורה משלה כהדגשה.
- **מודעה ממומנת:** הטקסט הראשי עד כ-125 תווים לפני הקיפול, כותרת אחת עד 40 תווים, קריאייטיב 1:1, קריאה לפעולה אחת וברורה.

**כללי הכתיבה של הערכה חלים על כל שורה:** עברית, פנייה דו-מגדרית ביחיד/ה קודם ("תוכל/י", "בעל/ת עסק"),
בלי קו מפריד ארוך ובלי קו באורך בינוני, בלי מילה לועזית בתחילת שורה, מספר רק עם מקור מ-`research.md`,
וניסוח אחד ויחיד לקריאה לפעולה בכל הערוצים.

---

## 4. חוקי הקריאייטיב

התמונה נושאת את המסר של הוובינר, ועליה **שורת טקסט אחת לכל היותר**, גדולה ובועטת.

### 4.1 שני תפקידים לתמונה, ולכל אחד מסגור אחר

זו הטעות שהכי מפילה את השלב, ולכן היא ראשונה. לאותה תמונה יש שני שימושים שונים לגמרי:

| תפקיד | מה זה | איך התמונה נראית בסוף | איך ממסגרים אותה |
|---|---|---|---|
| **גיבור** (`hero`) | התמונה עצמה היא המודעה: פוסט אורגני, מודעה ממומנת, כרטיס לינק | רואים אותה במלואה, בצבע מלא | משאירים **חצי פריים עליון שקט וריק** לכותרת. הנושא יושב בשליש התחתון |
| **כרטיס** (`card`) | הרקע בתוך `templates/creative.html`: תזכורות לנרשמים, ספירה לאחור, "עולים לאוויר" | התמונה מעומעמת ל-28 אחוז ונמסכת כך שהיא **דוהה כלפי מטה**: נראית למעלה, נעלמת למטה | בדיוק הפוך: התוכן חי ב**שני השלישים העליונים**, התחתון נשאר ריק, והתמונה צריכה להיות **בהירה ובעלת ניגודיות גבוהה**, אחרת היא נעלמת לגמרי מאחורי הטקסט |

מה שיוצא לנרשמים (הכרטיסים) כבר עובד יפה, ולא נוגעים בו. מה שנשבר בסבב הקודם היה הגיבורים:
תמונות שנוצרו בניסוח דליל, בלי בימוי, ולכן יצאו כלליות. הסעיפים הבאים מטפלים בזה.

תמונה כהה מאוד (חדר חשוך, לילה) היא כמעט תמיד **גיבור בלבד**. בתוך הכרטיס היא נעלמת.

### 4.2 מה אסור, בלי יוצא מן הכלל

מוחות · רשתות נוירונים · לוחות מעגלים · גרדיאנטים סגולים או כחולים זוהרים · הולוגרמות ·
רובוטים אנושיים · "עולם עתידני" גנרי כטפט · לחיצות ידיים מתמונות סטוק · פאנלים של ממשק מרחפים באוויר ·
קווי אור ניאון · כדור הארץ עם נקודות מחוברות · אנשים בחליפה שמצביעים על מסך שקוף.
כל אלה מורידים את המודעה לרמה של כולם, ומסמנים לצופה בשנייה שזו תמונה שיוצרה בבינה מלאכותית.

עוד שני איסורים שנוגעים לפלט עצמו: **אין אותיות בתוך התמונה** (המודל משבש עברית, וגם אנגלית יוצאת מעוותת),
ואין לוגו, חתימה או סימן מים.

### 4.3 מה כן

רגע אנושי קונקרטי · חפץ יומיומי שהופך למוזר · מטאפורה גרפית בנויה מחומר אמיתי · טיפוגרפיה כפיסול ·
טבע דומם עריכתי · לפני ואחרי בפריים אחד · פער קנה מידה · פריים תיעודי גנוב.
אור אמיתי, טקסטורה אמיתית, נושא אחד ברור, ופלטה מצומצמת של שני צבעים ועוד מבטא אחד.

### 4.4 מתוך מה בנוי ניסוח טוב

ניסוח בשורה אחת ("שולחן עם מחשב, סגנון עתידני") מייצר בדיוק את התמונה הגנרית שאיש לא עוצר בשבילה.
ניסוח שמייצר תמונה ברמת קמפיין ממומן נכתב באנגלית ומכיל **שמונה רכיבים, בסדר הזה**:

1. **נושא ופעולה** מה נמצא בפריים ומה בדיוק קורה ברגע הזה. פועל, לא תיאור סטטי.
2. **קומפוזיציה ומסגור** איפה הנושא יושב (שליש תחתון ימני, מרכז, פינה), ומה ריק.
3. **עדשה ועומק שדה** מספר מ"מ ומספר צמצם: 24mm f/8 לרוחב ולעומק, 35mm f/2.8 לתיעודי, 50mm f/2 לרגע אנושי, 90mm macro f/8 לטבע דומם.
4. **תאורה** מאיפה האור מגיע, אם הוא קשה או רך, ובאיזו שעה. מקור מפתח אחד ועוד מקור השלמה, לא "מואר יפה".
5. **צבע וגרייד** שני צבעים ומבטא אחד, עם שם לגוון (ענבר חם, כחול-דיו, טורקיז עמוק, לבן-עצם).
6. **טקסטורה וחומר** נייר, בטון, גבס, פליז, עץ, גרעיניות פילם, אבק באוויר.
7. **מצב רוח** מילה או שתיים על התחושה, לא על הרעיון.
8. **המקום השמור לטקסט** משפט מפורש שאומר איזה חלק בפריים נשאר שקט וריק (לפי הטבלה ב-4.1).

ה"אסור" לא נכתב בניסוח: `gen_creatives.py` מוסיף אותו לבד לכל בקשה.

---

## 5. ספריית הכיוונים

עשרה כיוונים. מציגים למשתמש/ת את **השמות ואת שורת "מתי"** בלבד, לא את הניסוחים.
הניסוח נכנס ל-`creatives.json` בשדה `prompt`, באנגלית, כך המודל מדייק.

בכל תבנית, מה שבסוגריים מסולסלים הוא החריץ שממלאים מנושא הוובינר, מ-`research.md` ומהקהל שב-`config.json`.
שאר המשפט נשאר מילה במילה: הוא זה שמייצר את האיכות.

**1. הרגע האנושי** · כשהמסר הוא הכאב או ההקלה של אדם אחד. הכיוון הכי בטוח, ובדרך כלל הכי ממיר.
```
Documentary photograph of {a person from the audience, in their real place of work, at the exact
moment the problem happens}. {One concrete telling detail in the foreground}. Shot on a 50mm lens
at f/2, eye level, the subject low in the right third of the frame, the plain wall above them empty.
Lighting: one warm practical light as key, cool daylight or streetlight as rim, deep unlit background.
Colour grade: muted amber highlights against desaturated teal shadows, fine film grain, real skin
texture, no retouching. Mood: {the feeling in one or two words}.
```

**2. הפריים התיעודי** · כשרוצים "זה קורה עכשיו, אצל מישהו אמיתי". טוב לקהל שלא מזדהה עם סטודיו.
```
Documentary photograph of {a real workplace at its busiest moment}, {the subject} mid-motion and
slightly motion-blurred at 1/30s while {the one object that matters} stays razor sharp. Shot on a
35mm lens at f/2.8, chest height, slightly off-centre, the action in the lower left third, a bright
plain wall filling the upper half. Lighting: large soft daylight from a window camera left, warm
tungsten spill from inside. Colour grade: honest contrast, clean neutral whites, fine grain.
Mood: real work happening, nobody posing.
```

**3. הטבע הדומם העריכתי** · כשהמסר הוא "כל העסק שלך על שולחן אחד". נקי, זול לייצר, קל להבנה.
```
Editorial still life photographed from directly overhead on a {colour} paper surface.
{The messy side: a spill, fan or pile of the objects that represent the problem} across the lower
left of the frame, and {the one calm object that represents the answer} alone on the clean empty
right side, glowing warm white and throwing real light onto the paper. Shot on a 90mm macro lens at
f/8. Lighting: one hard studio light from the top left for crisp shadows, plus that practical glow.
Colour grade: two colours only, {colour A} and {colour B}, plus one warm pool of light.
The top third of the frame is empty paper. Mood: the mess on one side, one calm thing handling it.
```

**4. החפץ המוזר** · כשרוצים לעצור גלילה. חפץ יומיומי שעושה משהו שחפץ לא עושה.
```
{An ordinary everyday object} on {a plain surface} in a bare room, and {the impossible thing it is
doing: its shadow is the silhouette of a standing person / a column of light rises from it / it is
casting a shadow of something else entirely}. Wide shot on a 28mm lens at f/8, camera low, the object
small in the lower centre, the effect stretching away toward the top of the frame. Lighting: one hard
low sun raking in from a doorway out of frame, dust in the air, hard shadow edges. Colour grade: warm
grey concrete with one deep orange accent in the light pool. The upper half of the frame is empty wall.
Mood: something ordinary is quietly doing the work of a person.
```

**5. המטאפורה הגרפית** · כשהמסר הוא מספר או תהליך ("הרבה נכנס, אחד מטפל"). הכי קריא בתצוגה זעירה.
```
A graphic metaphor built from real cut paper and photographed in a studio, not illustrated:
{about forty small paper units representing the many} arranged in a wide converging fan across the
top of the frame, clearly narrowing downward and funnelling into {one single object representing the
answer} standing at the bottom centre. Real paper, real hard shadows, on a flat {colour} paper
backdrop. Shot on a 50mm lens at f/5.6, straight on, symmetrical. Lighting: one hard studio light
from the upper left, crisp parallel shadows. Colour grade: exactly two colours, {colour} and bone
white. Mood: {many something, one place they land}.
```

**6. הטיפוגרפיה כפיסול** · כשאין דימוי טוב, ורוצים שהצורה עצמה תגיד את הנושא. יוקרתי, ריק, מותגי.
```
{One or two oversized symbolic forms: a speech bubble, a question mark, an arrow, a key} sculpted
from solid matte plaster, standing on a polished concrete floor in a large empty room, no text on
them, surface slightly rough with visible tool marks, taller than a person. Wide shot on a 35mm lens
at f/8, the sculpture in the lower right quarter, a vast plain deep ink-blue wall filling the upper
left. Lighting: one hard directional light from the upper right, long geometric shadows stretching
across the floor. Colour grade: warm bone plaster against deep ink blue, one burnt orange accent.
Mood: an everyday thing, made monumental.
```

**7. לפני ואחרי בפריים אחד** · כשהמסר הוא התוצאה. הכי מסביר את ההבטחה בלי מילה.
```
{One continuous surface: a desk, a counter, a workbench} photographed straight on so a single frame
reads as two halves with no border and no split-screen device. The left half is {the chaos before},
lit by flat cold fluorescent light. The right half of the same surface is bare and calm, {the one
thing that replaced it}, lit by warm golden hour light from a window. Shot on a 40mm lens at f/8,
eye level, a plain painted wall filling the entire upper half of the frame. Colour grade: cold
desaturated grey-green on the left flowing into warm amber on the right, one photograph.
Mood: same place, two different lives.
```

**8. פער קנה המידה** · כשהמסר הוא גודל הבעיה, או כמה קטן הצעד הראשון.
```
A very small human figure seen from behind, standing on a wide empty dark floor, facing an enormous
monolithic mass built from {the material of the problem: stacked paper, crates, folders} that fills
only the lower right of the frame. Above and to the left, two thirds of the image is a plain dark
empty wall with nothing in it. Shot on a 24mm lens at f/8, deep focus, the figure occupying the
bottom left eighth. Lighting: one shaft of warm light hitting the base of the mass where the figure
stands, everything above falling into darkness. Colour grade: near black navy, bone white, one warm
amber pool. Mood: the size of it, and one person deciding to start.
```

**9. האור בחדר החשוך** · כשהמסר הוא "זה עובד גם כשאת/ה לא שם". לילה, מקור אור אחד.
```
Documentary photograph taken from the doorway of a dark room at 2am: {the person} asleep or absent,
only an edge of them lit. In the foreground {the working object} with its screen or lamp on, the
single light source in the room, throwing a soft pool of light across the surface and up onto the
wall. Shot on a 35mm lens at f/1.8, focus on the object, the figure soft behind it, the object in the
lower left third, the wall above almost black and empty. Lighting: that screen as the only key, faint
cool moonlight through a slatted blind on the far wall. Colour grade: deep blue-black shadows, one
warm-white pool, heavy natural grain. Mood: {they are asleep and the work is still happening}.
```

**10. הפוסטר מנייר גזור** · כשצריך **רקע לכרטיס** (`card`) ולא גיבור: בהיר, גרפי, שורד עמעום ל-28 אחוז.
```
A bold editorial poster composition made of real cut paper shapes photographed in a studio:
{three or four simple geometric shapes representing the idea} overlapping in the upper two thirds of
the frame, casting real hard shadows, the bottom third left almost empty. Shot on a 50mm lens at
f/5.6, straight on. Lighting: one hard studio light from the upper left. Colour grade: two flat
saturated colours only, {colour A} and {colour B}, high contrast, visible paper fibre texture.
Mood: graphic, confident, quiet at the bottom.
```

**איך בוחרים כיוון:** כיוון אחד לכל מסר שאושר בסעיף 2, ולא אותו כיוון לשני מסרים.
חבילה טובה מחזיקה שלושה עולמות שונים: אחד אנושי (1, 2 או 9), אחד גרפי (5, 6 או 10), ואחד רעיוני (4, 7 או 8).

---

## 6. מודעה ממומנת: מה משתנה

מודעה ממומנת נראית לאדם שלא מכיר אותנו, בגלילה, בגודל אגודל, ליד תוכן של חברים.
לכן היא לא "פוסט יפה יותר", אלא סט חוקים אחר:

1. **מוקד אחד.** אובייקט אחד או אדם אחד. שתי נקודות עניין = אף נקודת עניין בגודל אגודל.
2. **קריאות בתצוגה זעירה.** מכווצים את התמונה לרוחב 150 פיקסלים ומסתכלים. אם הנושא לא מזוהה, הניסוח חוזר לתנור.
3. **ניגודיות מול הפיד.** הפיד בהיר וצפוף. תמונה כהה ונקייה או תמונה עם שטח צבע שטוח אחד בולטת. תמונה אפורה בינונית נבלעת.
4. **טקסט גדול בלבד.** שורה אחת, לא יותר מכשש מילים. אין שורת משנה קטנה, אין רשימת נקודות, אין מחיר באותיות קטנות.
5. **שני החיתוכים עובדים.** מייצרים 1:1, ובודקים שגם חיתוך 9:16 מהמרכז לא חותך את הנושא ולא את הכותרת. אם כן, מייצרים גרסה נפרדת ב-9:16 במקום למתוח.
6. **בלי פנים של אנשים אמיתיים ומוכרים, בלי לוגו של חברה אחרת, בלי מספרים בלי מקור.** אלה גם כללי הפלטפורמה וגם כללי הערכה.
7. **שלוש גרסאות, לא אחת.** למודעה ממומנת מייצרים שלוש תמונות לאותו מסר ומעלים את שתי החזקות כשתי מודעות באותו סט. ההבדל בין תמונה טובה לחלשה בעלות לליד גדול מכל ניסוח קופי.

---

## 7. רף האיכות ולולאת הבחירה

**לא בוחרים מתמונה אחת.** לכל מסר שאושר מייצרים 2 עד 3 וריאציות, פותחים אותן, ומשאירים את החזקה.
זו הפקודה:

```
python3 <skill-dir>/scripts/gen_creatives.py --config outputs/webinars/<slug>/config.json --key <המפתח> --variations 3
```

הקבצים יוצאים `creatives/bg-<id>-1.png`, `-2.png`, `-3.png`. פותחים את כולם, בוחרים אחד,
ומוחקים את השאר או משאירים אותם בתיקייה בלי להשתמש בהם.

**רף האיכות. שבע שאלות, על כל תמונה, בעיניים פקוחות. תשובה שלילית אחת פוסלת:**

1. **עוצרת גלילה בגודל אגודל?** מכווצים ל-150 פיקסלים. יש צורה אחת שמזוהה מיד?
2. **נקראת בשנייה אחת?** אפשר להגיד מה רואים בלי לחשוב?
3. **הקומפוזיציה נקייה לכותרת?** יש שטח שקט אחד ורציף במקום הנכון (לפי הטבלה ב-4.1), בלי פרטים שיתחרו באותיות?
4. **נראית כמו צילום אמיתי או כמו עיצוב מכוון?** לא כמו "תמונה שיוצרה בבינה מלאכותית": בלי אור פלסטי, בלי סימטריה מושלמת מדי, בלי אצבעות עודפות, בלי ריכוך דיגיטלי על הכל.
5. **נושאת את המסר של הוובינר?** לא סתם יפה. אם מחליפים את הכותרת למסר של וובינר אחר והתמונה עדיין מתאימה, היא כללית מדי.
6. **נקייה מהרשימה האסורה** (סעיף 4.2)?
7. **אין בה אותיות מעוותות?** לא בשלט ברקע, לא על מסך, לא על נייר. אם יש, מייצרים שוב.

נכשלה? **לא מייצרים שוב את אותו ניסוח.** מתקנים את הרכיב שנכשל לפי סעיף 4.4 (בדרך כלל התאורה, המסגור,
או שהנושא לא היה מספיק קונקרטי), ומריצים `--only <id>` שוב. לא מוסרים תמונה שלא נפתחה ולא נבדקה.

---

## 8. הסקריפט

```
python3 <skill-dir>/scripts/gen_creatives.py --config outputs/webinars/<slug>/config.json --dry-run
python3 <skill-dir>/scripts/gen_creatives.py --config outputs/webinars/<slug>/config.json --key <המפתח>
python3 <skill-dir>/scripts/gen_creatives.py --config ... --key <המפתח> --variations 3 --only post-a
```

קורא `config.json` ו-`creatives.json` שלידו, ומייצר `creatives/bg-<id>.png` לכל פריט
(או `bg-<id>-N.png` כשמבקשים כמה וריאציות). מבנה פריט ב-`creatives.json`:

```json
[{"id":"post-a","direction":"פער קנה המידה","use":"hero","prompt":"A very small human figure ...",
  "size":"1:1","punch":"שורה אחת","subline":"שורת משנה"}]
```

- `size` הוא `1:1` (1024x1024) או `9:16` (1024x1536).
- `use` הוא `hero` (ברירת מחדל, התמונה היא המודעה) או `card` (רקע לתבנית, סעיף 4.1). השדה קובע איזה
  משפט של מקום-שמור-לטקסט נוסף לניסוח מאחורי הקלעים.
- דגלים: `--config`, `--key`, `--only`, `--variations`, `--dry-run`.
- `--dry-run` עובד בלי מפתח ומדפיס בדיוק מה היה נשלח, כולל רשימת האסור.

---

## 9. הלבשת השורה העברית

**הטקסט העברי לא נכנס לתוך התמונה.** מודלים של תמונות משבשים עברית. לכן מייצרים את הרקע **בלי טקסט**,
ומלבישים מעליו את השורה העברית עם `templates/creative.html` והרינדור.
הטוקנים של כיוון העיצוב שנבחר בשלב 8 נשארים כמו שהם, כדי שהקריאייטיבים ייראו כמו שאר המשפך.

מעתיקים את שם קובץ הרקע לשדה `creative_photo` ב-`copy.json`, כותבים את `copy.creatives`
(מזהה, `punch`, `subline`), ומריצים:

```
python3 <skill-dir>/scripts/render_pages.py --config outputs/webinars/<slug>/config.json --creatives
python3 <skill-dir>/scripts/screenshot.py --dir outputs/webinars/<slug>/landing/creatives
```

לפני הרינדור מוודאים ש-`date_he` ו-`time` מלאים ב-`config.json`, אחרת כרטיס התאריך בקריאייטיב יוצא ריק.
רוצים רקע שונה לכל קריאייטיב? מריצים את שני הצעדים האלה פעם אחת לכל רקע, ומחליפים ביניהם את `creative_photo`.

שתי אזהרות שנבדקו בפועל על התבנית:

- הרקע מעומעם ל-28 אחוז ונמסך כלפי מטה. רקע כהה נעלם בו לחלוטין. לכרטיס בוחרים רקע **בהיר וגרפי**
  (כיוונים 3, 5, 10), ולא צילום לילה.
- שורת ה-`punch` מעל 14 תווים יורדת אוטומטית לגודל קטן יותר. שורה של עד כשש מילים נשארת ענקית, וזו המטרה.

**מודעה ממומנת היא לרוב `hero`, לא כרטיס:** מעלים את התמונה עצמה, והכותרת נכתבת בשדה הכותרת של הפלטפורמה
או מולבשת בתבנית רק אם רוצים את הזהות הוויזואלית של הוובינר על התמונה.
