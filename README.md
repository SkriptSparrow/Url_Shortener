# URL Cutter

A convenient desktop application for shortening long URLs in Python (GUI - Flet, shortener - TinyURL).

---

## 🔽 Loading

Windows: download the ready UrlCutter.exe from the Releases section:
➡️ [Latest release](https://github.com/SkriptSparrow/Url_Shortener/releases/latest).

The file is signed as UrlCutter.exe. If Windows SmartScreen asks, confirm the launch.

---

## ✨ Possibilities

- Enter long URL → get short link (TinyURL).
- Copy the result to the clipboard, clear the fields.
- Simple URL validation and error reporting.
- Small "protections": local rate-limit, internet check, careful timeouts.

---

## 🛠 Technologies

- Python 3.13 (compatible with 3.11+)
- Flet — cross-platform GUI
- pyshorteners (TinyURL provider)
- PyInstaller (for building .exe)

---

## ▶️ Run from source
```bash
git clone https://github.com/SkriptSparrow/Url_Shortener.git
cd Url_Shortener
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python lite_upgrade.py
```

---

## 🧪 Development
```bash
# тесты
pytest -q

# linters / formatters
ruff check --fix
black .
pre-commit run --all-files
```

---

## 🏗 Assembling .exe (PyInstaller)

OneDir (to check assets):

```powershell
pyinstaller lite_upgrade.py --name UrlCutter --windowed --onedir ^
  --icon "urlcutter/assets/img/app.ico" ^
  --collect-data urlcutter ^
  --add-data "urlcutter/assets;urlcutter/assets"
```


OneFile (one file):

```powershell
pyinstaller lite_upgrade.py --name UrlCutter --windowed --onefile ^
  --icon "urlcutter/assets/img/app.ico" ^
  --collect-data urlcutter ^
  --add-data "urlcutter/assets;urlcutter/assets"
```

Assets (window icon, images, fonts) are packed into a bundle at urlcutter/assets/....
The code uses safe path retrieval for both dev and .exe.

---

## 📸 Screenshots

![Вид приложения](https://i.ibb.co/xKK6HjHL/url-cutter.jpg)

---

## 📦 Version history

Look [Releases](https://github.com/SkriptSparrow/Url_Shortener/releases).

Download the latest version: [➡️ Latest release](https://github.com/SkriptSparrow/Url_Shortener/releases/latest)

---


## 📫 Contacts

* **Telegram:** [@Alex\_Gicheva](https://t.me/Alex_Gicheva)
* **Email:** [alexgicheva@gmail.com](mailto:alexgicheva@gmail.com)

✨ Thank you for your attention! I hope this application will make working with URLs more convenient and faster.
