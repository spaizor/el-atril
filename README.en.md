# El Atril

*[Versión en español](README.md)*

A Markdown reader for Windows. Open a folder and El Atril (Spanish for *the lectern*) shows all
its `.md` pages, formatted and in a dark theme, with a side panel to jump between them, search,
and back / forward navigation, like a small documentation website.

It is meant for reading documentation: a project's docs, notes, a guide split into several
linked files. It is read-only; keep editing your `.md` files in your usual editor and press F5
in El Atril to see the changes.

> The user interface is currently in Spanish only.

## Features

- **Open any folder** with the *Abrir* (Open) button or Ctrl+O. Subfolders are included.
- **Recent folders**: on startup, the side panel lists the last folders you opened so you can
  go back to them with one click (the × removes them from the list). The *Cerrar* (Close) button or Ctrl+W closes the open
  folder and goes back to that list.
- **Side panel** listing every page, grouped by folder and shown by its title (the first
  `# Title` in the file).
- **Starts on the front page**: if there is a `README.md`, `LEEME.md` or `index.md` at the root,
  it opens that one first.
- **Links between pages**: a link to another `.md` in the folder opens inside El Atril,
  including links to a section (`page.md#section`). Web links open in your browser.
- **Back and forward** like a browser (Alt+← and Alt+→).
- **Search** in the current page, highlighting matches regardless of case and accents, and
  **search across all pages** with a short snippet for each result.
- **Reload** (F5) to see changes while you edit the `.md` files.
- **Tables, task lists, strikethrough and code blocks**, on top of regular Markdown.
- **Excel files in the folder** get their own section in the panel; they open in Excel.

## Requirements

- Windows 10 or 11.
- **Microsoft Edge WebView2 Runtime**, which draws the window. It ships with Windows 11 and with
  an up-to-date Windows 10; if it is missing, it is a free download from Microsoft.
- To run from source: **Python 3.13**.

## Installation

There is no published `.exe` yet, so for now it runs from source.

```powershell
git clone https://github.com/spaizor/el-atril.git
cd el-atril
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

### Building the .exe

```powershell
.venv\Scripts\pyinstaller build.spec
```

This creates `dist\El Atril.exe`, a single file that runs without Python installed.

## Usage

When it opens, click **Abrir carpeta…** (Open folder) and choose the folder with your documents.
You can also pass the folder on start-up to open it straight away:

```powershell
.venv\Scripts\python main.py "C:\path\to\my docs"
```

The same works with the `.exe`, and you can also **drag a folder onto the `.exe`**.

### Keyboard shortcuts

| Key | Action |
|---|---|
| Ctrl+O | Open another folder |
| Ctrl+W | Close the folder and go back to the recent list |
| Ctrl+F | Go to the search box |
| Enter / Shift+Enter | Next / previous match (also F3 / Shift+F3) |
| Ctrl+Enter | Search all pages |
| Esc | Clear the search |
| Alt+← / Alt+→ | Back / forward |
| F5 or Ctrl+R | Reload the folder and the current page |

## Privacy

El Atril does not connect to the internet and only reads the files in the folder you open. The
only thing it stores is the list of recently opened folders (their paths, none of their
content), in `%APPDATA%\El Atril\recientes.json`; delete that file to clear the list.

Web links inside your documents open in your browser only if you click them.

## Known limitations

- **Images in `.md` files are not shown yet.**
- Links to files that are not `.md` (PDF, images...) do not open from El Atril; they appear greyed
  out.
- It skips hidden folders (starting with `.`) and `node_modules`, `__pycache__`, `venv` and
  `site-packages`, which are usually full of third-party docs.
- In very large folders it lists at most the first 2000 pages, so it does not hang.
- The interface is in Spanish only.
- Only tested on Windows 11.

## License

[MIT](LICENSE): you may use, copy, modify and distribute it freely, keeping the license notice.
