# URL Cutter

Удобное десктоп-приложение для сокращения длинных URL на Python (GUI — Flet, шортнер — TinyURL).

---

## 🔽 Загрузка

Windows: скачай готовый UrlCutter.exe из раздела Releases:
➡️ [Latest release](https://github.com/SkriptSparrow/Url_Shortener/releases/latest).

Файл подписан как UrlCutter.exe. Если Windows SmartScreen спросит, подтвердите запуск.

---

## ✨ Возможности

- Ввод длинного URL → получение короткой ссылки (TinyURL).
- Копирование результата в буфер обмена, очистка полей.
- Простая валидация URL и сообщения об ошибках.
- Небольшие «защиты»: локальный rate-limit, проверка интернета, аккуратные таймауты.

---

## 🛠 Технологии

- Python 3.13 (совместимо с 3.11+)
- Flet — кроссплатформенный GUI
- pyshorteners (провайдер TinyURL)
- PyInstaller (для сборки .exe)

---

## ▶️ Запуск из исходников
```bash
git clone https://github.com/SkriptSparrow/Url_Shortener.git
cd Url_Shortener
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python lite_upgrade.py
```

---

## 🧪 Разработка
```bash
# тесты
pytest -q

# линтеры / форматтеры
ruff check --fix
black .
pre-commit run --all-files
```

---

## 🏗 Сборка .exe (PyInstaller)

OneDir (для проверки ассетов):

```powershell
pyinstaller lite_upgrade.py --name UrlCutter --windowed --onedir ^
  --icon "urlcutter/assets/img/app.ico" ^
  --collect-data urlcutter ^
  --add-data "urlcutter/assets;urlcutter/assets"
```


OneFile (одним файлом):

```powershell
pyinstaller lite_upgrade.py --name UrlCutter --windowed --onefile ^
  --icon "urlcutter/assets/img/app.ico" ^
  --collect-data urlcutter ^
  --add-data "urlcutter/assets;urlcutter/assets"
```

Ассеты (иконка окна, изображения, шрифты) упаковываются в бандл по пути urlcutter/assets/....
В коде используется безопасное получение путей как для dev, так и для .exe.

---

## 📸 Скриншоты

![Вид приложения](https://ibb.co/V00TmSm9/url-cutter.png)

---

## 📦 История версий

Смотри [Releases](https://github.com/SkriptSparrow/Url_Shortener/releases).

Скачать последнюю версию: [➡️ Latest release](https://github.com/SkriptSparrow/Url_Shortener/releases/latest)

---


## 📫 Контакты

* **Telegram:** [@Alex\_Gicheva](https://t.me/Alex_Gicheva)
* **Email:** [alexgicheva@gmail.com](mailto:alexgicheva@gmail.com)

✨ Спасибо за внимание! Надеюсь, это приложение сделает работу с URL удобнее и быстрее.
