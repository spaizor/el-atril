# El Atril

*[Versión en español](README.md)*

A Markdown reader for Windows. Open a folder and El Atril (Spanish for *the lectern*) shows all
its `.md` pages, formatted, in a light or dark theme, with a side panel to jump between them, search,
and back / forward navigation, like a small documentation website.

It is meant for reading documentation: a project's docs, notes, a guide split into several
linked files. It is read-only; keep editing your `.md` files in your usual editor and El Atril
shows the changes as soon as you save.

## Features

- **Open any folder** with the *Open* button or Ctrl+O. Subfolders are included.
- **Recent folders**: on startup, the side panel lists the last folders you opened so you can
  go back to them with one click (the × removes them from the list). The *Close* button or Ctrl+W closes the open
  folder and goes back to that list.
- **Side panel** listing every page, grouped by folder and shown by its title (the first
  `# Title` in the file).
- **Page outline**: under the open page, the side panel lists its headings so you can jump to
  each section. The section you are reading is highlighted.
- **Starts on the front page**: if there is a `README.md`, `LEEME.md` or `index.md` at the root,
  it opens that one first.
- **Picks up where you left off**: when you go back to a folder, it opens the last page you read,
  scrolled to the same spot.
- **Adjustable font size** with the *A−* and *A+* buttons, Ctrl+mouse wheel or Ctrl+ +/−
  (Ctrl+0 resets it). It is remembered for next time.
- **Links between pages**: a link to another `.md` in the folder opens inside El Atril,
  including links to a section (`page.md#section`). Web links open in your browser.
- **Links to other files** in the folder (PDF, images, documents...) open with their Windows
  program, and links to a folder open in File Explorer. They are marked with a small ↗. For
  safety, programs and scripts (`.exe`, `.bat`, `.ps1`, `.py`...) are never opened and appear
  greyed out.
- **Light and dark theme**: by default it follows Windows (and switches on its own when you
  change it in Windows). The light bulb at the top right switches to light, to dark, or back to
  following Windows (shown with a small "A"). It is remembered for next time.
- **In English or Spanish**: by default, in the Windows language (Spanish if Windows is in
  Spanish, Catalan, Galician or Basque; English otherwise). The *ES* / *EN* button at the top
  right switches language or goes back to following Windows (shown with a small "A"). It is
  remembered for next time.
- **Help at hand**: click the version number at the top right (or on the start page) to open
  this README inside El Atril, in the window's language. Back takes you to what you were reading.
- **Images**: images from the folder used in your pages (`![text](photo.png)` or
  `<img src="photo.png">`) are shown, with paths relative to the page, like links. Images from
  the internet are not loaded: a small box with their text is shown instead, the same as when an
  image is missing or too large (over 15 MB).
- **Back and forward** like a browser (Alt+← and Alt+→).
- **Search** in the current page, highlighting matches regardless of case and accents, and
  **search across all pages** with a short snippet for each result.
- **Live reload**: if you edit the open page in another program and save it, El Atril updates it
  within a second without losing your place. New, renamed or deleted pages show up in the
  panel on their own too. It only checks file dates (it does not re-read anything until a file
  changes), so it does not slow the computer down.
- **Tables, task lists, strikethrough and code blocks**, on top of regular Markdown.
- **Syntax highlighting**: code blocks that name their language (` ```python `, ` ```powershell `,
  ` ```json `...) are coloured, in both themes. Blocks without a language stay plain.
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

When it opens, click **Open folder…** and choose the folder with your documents.
You can also pass the folder on start-up to open it straight away:

```powershell
.venv\Scripts\python main.py "C:\path\to\my docs"
```

Instead of a folder you can also pass a `.md` page: its folder opens, right on that page.

```powershell
.venv\Scripts\python main.py "C:\path\to\my docs\guide.md"
```

The same works with the `.exe`, and you can also **drag a folder or a `.md` file onto the
`.exe`**. To open `.md` files with a double click: right-click a `.md` file → *Open with* →
*Choose another app* → find `El Atril.exe` and tick *Always use this app*.

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
| F5 or Ctrl+R | Reload the folder and the current page by hand (it already happens on its own) |
| Ctrl+wheel or Ctrl+ +/− | Larger / smaller font |
| Ctrl+0 | Reset the font size |

## Privacy

El Atril does not connect to the internet and only reads the files in the folder you open. All
it stores, in `%APPDATA%\El Atril`, is:

- `recientes.json`: the list of recently opened folders (their paths, none of their content).
- `memoria.json`: the font size, the theme, the language and, for each folder, the name of the last page you read and how
  far down you were.

Delete those files and El Atril starts from scratch.

Web links inside your documents open in your browser only if you click them, and images from
the internet are not loaded.

## Known limitations

- It skips hidden folders (starting with `.`) and `node_modules`, `__pycache__`, `venv` and
  `site-packages`, which are usually full of third-party docs.
- In very large folders it lists at most the first 2000 pages, so it does not hang.
- Only tested on Windows 11.

## License

[MIT](LICENSE): you may use, copy, modify and distribute it freely, keeping the license notice.
