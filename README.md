# hebi-pygame demo project (no sound, just a fun snake on transparent layer on desktop)

hebi-pygame = game of Snake in pygame. Has exe variant (thanks, pyinstaller)

pygame pywin32 screeninfo test

Learned:
1. collect monitor data (screeninfo)
2. how to create a desktop mascot in a no_frame floating mode on the desktop screen transparent layer (pywin32)
3. how to create snake game (pygame)

made during university algorithms&alg.languages

## ru:

### дисциплина Алгоритмы и Алгоритмические языки (Pygame)

### Hebi (по-японски "змейка"): стрелки, P=pause пауза, Q=quit выход

* базовая змейка + pywin32/screeninfo + gfx для чуть красоты
* минимализм как в дизайне, так и в механике
* можно использовать как код для маскота (скопировать часть кода с pywin32/screeninfo и сделать своего персонажа, анимировать спрайты)
* клавишное управление
* выход в любое время Q
* таблица рекордов подгружается с json
* условно 4 экрана: статичный старт-экран, активная игра парит над десктопом, статичный конец игры, ввод-inputbox в экран вечной славы
* помощь пользователю, есть инструкции какие клавишы использовать (стрелки, P=pause, Q=quit)

### планы

* планируется добавить автопилот, чтобы змейка бежала по экрану и играла сама
* планируется отдельно сделать маскота (визуально приятного, спрайт готов, осталось доделать бег по кругу стола, анимации), 
* планируется добавить-анимировать спрайты
* планируется рефакторинг под ООП подход, замаксить читабельность
* must-do: создать отдельный репозиторий с инструкцией как создать и заспрайтить своего маскота (например, аниме или игрового персонажа, и тд)
