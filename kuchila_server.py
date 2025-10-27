# --- KUCHILA SERVER (FINAL v2) ---
# ---------------------------------------------------------------------

import sys, os, subprocess, socket, warnings
from importlib.metadata import version
from typing import Dict, Any

warnings.filterwarnings("ignore", category=DeprecationWarning)
FLASK_COMPONENTS: Dict[str, Any] = {}

# --- Color constants ---
G = "\033[92m"   # Green
Y = "\033[93m"   # Yellow
R = "\033[91m"   # Red
B = "\033[94m"   # Blue
RESET = "\033[0m"

TERMINAL_BANNER = f"""
{G}
           __                       __   ___  __        ___  __  
|__/ |  | /  ` |__| | |     /\     /__` |__  |__) \  / |__  |__) 
|  \ \__/ \__, |  | | |___ /~~\    .__/ |___ |  \  \/  |___ |  \ 
                                                                 
{RESET}
"""

REQUIRED_PACKAGE = "Flask"

# ----------------------------------------------------------
def _print_header(title: str):
    print(f"\n{Y}{'-' * 70}{RESET}")
    print(f"{B}{title}{RESET}")
    print(f"{Y}{'-' * 70}{RESET}")


# ----------------------------------------------------------
# STEP 1: VIRTUAL ENVIRONMENT
# ----------------------------------------------------------
def check_and_relaunch_in_venv() -> None:
    _print_header("STEP 1/4 — Virtual Environment Check")

    if getattr(sys, "real_prefix", sys.base_prefix) != sys.prefix:
        print(f"{G}[✓]{RESET} Virtual environment detected.")
        return

    print(f"{Y}[i]{RESET} No virtual environment found. Creating one...")
    venv_path = os.path.join(os.getcwd(), "venv")
    venv_python = os.path.join(
        venv_path,
        "Scripts" if sys.platform == "win32" else "bin",
        "python",
    )

    if not os.path.exists(venv_python):
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True, text=True)
            print(f"{G}[✓]{RESET} Virtual environment created successfully.")
        except Exception as e:
            print(f"{R}[✗]{RESET} Failed to create virtual environment: {e}")
            sys.exit(1)

    print(f"{Y}[→]{RESET} Relaunching inside the virtual environment...")
    try:
        os.execv(venv_python, [venv_python] + sys.argv)
    except Exception as e:
        print(f"{R}[✗]{RESET} Relaunch failed: {e}")
        sys.exit(1)


# ----------------------------------------------------------
# STEP 2: DEPENDENCY CHECK
# ----------------------------------------------------------
def ensure_dependencies():
    _print_header("STEP 2/4 — Dependency Check")
    try:
        import flask  # noqa
        flask_version = version("flask")
        print(f"{G}[✓]{RESET} Flask dependency verified — version {flask_version}")
        return
    except ImportError:
        print(f"{Y}[i]{RESET} Flask not found. Installing automatically...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", REQUIRED_PACKAGE],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            flask_version = version("flask")
            print(f"{G}[✓]{RESET} Flask installed successfully — version {flask_version}")
        else:
            print(f"{R}[✗]{RESET} Flask installation failed:\n{result.stderr}")
            sys.exit(1)
    except Exception as e:
        print(f"{R}[✗]{RESET} Pip execution failed: {e}")
        sys.exit(1)


# ----------------------------------------------------------
# KUCHILA SERVER CLASS
# ----------------------------------------------------------
class KuchilaServer:
    FILE_MANAGER_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Kuchila File Manager</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <style>
        body { background:#f8fafc; font-family:'Inter',sans-serif; }
        .listing-card { max-width:1100px; margin:0 auto; overflow:hidden; }
        .item { border:1px solid #e5e7eb; border-radius:0.5rem; transition:background .15s; }
        .item:hover { background:#f1f5f9; }
        .thumb { width:80px; height:60px; object-fit:cover; border-radius:0.4rem; }
        .ico { width:1.1rem; height:1.1rem; }
        .download-btn:hover { background:#e2e8f0; }
      </style>
    </head>
    <body class="p-4 md:p-8">
      <div class="bg-gray-800 p-6 rounded-t-xl shadow-lg text-white listing-card mt-4 flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold">KUCHILA FILE MANAGER</h1>
          <p class="text-sm opacity-75">Serving: /{{ display_path }}</p>
        </div>
      </div>

      <div class="bg-white p-4 md:p-6 rounded-b-xl shadow-xl listing-card mb-10">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold text-gray-700">Contents</h2>
          <label class="flex items-center text-sm text-gray-600 cursor-pointer">
            <input type="checkbox" id="select-all" class="mr-2">Select All
          </label>
        </div>

        <button id="bulk-download-btn" disabled 
          class="bg-gray-500 text-white font-bold py-2 px-4 rounded-lg mb-4 opacity-50 cursor-not-allowed text-sm">
          ⬇️ Download Selected (0)
        </button>

        <ul class="space-y-2">
          {% for item in items %}
          <li class="item group flex items-center p-2">
            <div class="mr-3 w-5 h-5 flex items-center justify-center">
              {% if not item.is_dir %}
                <input type="checkbox" data-filename="{{ item.name }}" data-filepath="{{ item.link }}" class="select-file w-4 h-4">
              {% endif %}
            </div>

            <a href="{{ item.link }}" class="flex items-center text-gray-800 flex-grow">
              {% if item.thumbnail %}
                {% if item.is_video %}
                  <video class="thumb mr-3" src="{{ item.link }}" preload="metadata" muted></video>
                {% else %}
                  <img class="thumb mr-3" src="{{ item.link }}" loading="lazy" />
                {% endif %}
              {% endif %}
              {% if item.is_dir %}
                <svg class="ico mr-2 text-gray-600" viewBox="0 0 24 24" fill="currentColor">
                  <path fill-rule="evenodd" d="M1.75 8a.75.75 0 01.75-.75h3.8a.75.75 0 00.53-.22l.5-.5h6.9l.5.5h3.8a.75.75 0 01.75.75v8.5A2.75 2.75 0 0120.25 19H3.75A2.75 2.75 0 011 16.5V8z"/>
                </svg>
                <span class="font-semibold text-gray-900">{{ item.name }}/</span>
              {% else %}
                <svg class="ico mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M9 13H5m10 0H11M12 21H5a2 2 0 01-2-2V5a2 2 0 012-2h10l6 6v10a2 2 0 01-2 2h-7z"/>
                </svg>
                <span>{{ item.name }}</span>
              {% endif %}
            </a>

            <span class="text-xs text-gray-400 ml-auto mr-2">{{ item.size }}</span>

            {% if not item.is_dir %}
            <button onclick="handleSingleDownload('{{ item.link }}')" 
              title="Download" class="download-btn p-1 rounded-full text-gray-700 hover:text-black ml-1">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
              </svg>
            </button>
            {% endif %}
          </li>
          {% endfor %}
        </ul>
      </div>

      <p class="text-center text-xs text-gray-400 mt-4">Powered by Kuchila Server</p>

      <script>
        const selectAll = document.getElementById('select-all');
        const bulkDownloadBtn = document.getElementById('bulk-download-btn');
        const fileCheckboxes = () => document.querySelectorAll('.select-file');

        function updateDownloadButton() {
          const selected = document.querySelectorAll('.select-file:checked');
          const count = selected.length;
          bulkDownloadBtn.textContent = `⬇️ Download Selected (${count})`;
          bulkDownloadBtn.disabled = count === 0;
          bulkDownloadBtn.className = count > 0
            ? "bg-gray-800 text-white font-bold py-2 px-4 rounded-lg mb-4 hover:bg-gray-900 text-sm"
            : "bg-gray-500 text-white font-bold py-2 px-4 rounded-lg mb-4 opacity-50 cursor-not-allowed text-sm";
        }

        selectAll.addEventListener('change', () => {
          fileCheckboxes().forEach(cb => cb.checked = selectAll.checked);
          updateDownloadButton();
        });

        fileCheckboxes().forEach(cb => cb.addEventListener('change', updateDownloadButton));

        function handleSingleDownload(link) {
          const a = document.createElement('a');
          a.href = link;
          a.download = true;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }

        // ✅ Working Multiple Download Feature
        bulkDownloadBtn.addEventListener('click', () => {
          const selected = document.querySelectorAll('.select-file:checked');
          if (selected.length === 0) return;
          console.log(`Starting download for ${selected.length} files...`);
          selected.forEach((checkbox, index) => {
            const link = checkbox.getAttribute('data-filepath');
            setTimeout(() => handleSingleDownload(link), index * 500);
          });
          setTimeout(() => {
            selectAll.checked = false;
            fileCheckboxes().forEach(cb => cb.checked = false);
            updateDownloadButton();
          }, selected.length * 500 + 1000);
        });

        updateDownloadButton();
      </script>
    </body>
    </html>
    """

    CHOICE_PAGE_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Choose Action</title>
      <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="flex items-center justify-center min-h-screen bg-gray-50">
      <div class="max-w-md w-full bg-white rounded-xl shadow-xl overflow-hidden">
        <div class="bg-gray-800 p-6 text-white">
          <h1 class="text-2xl font-bold">Web App Detected</h1>
          <p class="text-sm opacity-75 mt-1">Folder: {{ path_segment }}</p>
        </div>
        <div class="p-6 space-y-4">
          <p class="text-gray-700">This folder contains an <b>index.html</b> file.</p>
          <a href="{{ webapp_run_link }}" class="block text-center bg-gray-800 hover:bg-black text-white font-bold py-3 rounded-lg">▶ Run Web App</a>
          <a href="{{ file_view_link }}" class="block text-center border border-gray-400 hover:bg-gray-100 text-gray-800 font-semibold py-3 rounded-lg">📁 View as Folder</a>
        </div>
      </div>
    </body>
    </html>
    """

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.app = FLASK_COMPONENTS["Flask"](__name__)
        self._configure_routes()

    @staticmethod
    def _fmt(size):
        if not size:
            return "0 B"
        units = ["B", "KB", "MB", "GB"]
        i = 0
        f = float(size)
        while f >= 1024 and i < len(units) - 1:
            f /= 1024
            i += 1
        return f"{f:.1f} {units[i]}"

    def _display_path(self, path: str) -> str:
        root_name = os.path.basename(self.root_dir.rstrip(os.sep)) or self.root_dir
        return root_name if not path else f"{root_name}/{path}"

    def _handle_dir(self, path, full):
        rts = FLASK_COMPONENTS["render_template_string"]
        request = FLASK_COMPONENTS["request"]

        index_files = ["index.html", "index.htm"]
        has_index = any(os.path.exists(os.path.join(full, f)) for f in index_files)
        index_name = next((f for f in index_files if os.path.exists(os.path.join(full, f))), None)

        if has_index and request.args.get("view") != "files":
            return rts(
                self.CHOICE_PAGE_TEMPLATE,
                path_segment=path or os.path.basename(full),
                webapp_run_link=f"/{path}/{index_name}" if path else f"/{index_name}",
                file_view_link=f"/{path}?view=files" if path else "?view=files",
            )

        items = []
        for n in sorted(os.listdir(full)):
            if n.startswith("."):
                continue
            p = os.path.join(full, n)
            is_dir = os.path.isdir(p)
            is_img = n.lower().endswith((".jpg", ".png", ".jpeg", ".gif", ".webp"))
            is_vid = n.lower().endswith((".mp4", ".webm", ".mov"))
            items.append(
                {
                    "name": n,
                    "is_dir": is_dir,
                    "link": f"/{path.rstrip('/')}/{n}" if path else f"/{n}",
                    "size": "Folder" if is_dir else self._fmt(os.path.getsize(p)),
                    "thumbnail": (is_img or is_vid),
                    "is_video": is_vid,
                }
            )
        return rts(self.FILE_MANAGER_TEMPLATE, items=items, display_path=self._display_path(path))

    def _serve(self, path=""):
        safe_join = FLASK_COMPONENTS["safe_join"]
        send_file = FLASK_COMPONENTS["send_file"]
        abort = FLASK_COMPONENTS["abort"]
        full = safe_join(self.root_dir, path)
        if os.path.isdir(full):
            return self._handle_dir(path, full)
        elif os.path.isfile(full):
            return send_file(full)
        else:
            return abort(404)

    def _configure_routes(self):
        self.app.add_url_rule("/", "root", self._serve, defaults={"path": ""})
        self.app.add_url_rule("/<path:path>", "path", self._serve)

    def run(self, host="0.0.0.0", port=8000):
        self.app.run(host=host, port=port)


# ----------------------------------------------------------
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def main():
    _print_header("STEP 3/4 — Importing Flask Components")
    try:
        from flask import Flask, render_template_string, send_file, abort, request
        from werkzeug.utils import safe_join
        FLASK_COMPONENTS.update(
            {
                "Flask": Flask,
                "render_template_string": render_template_string,
                "send_file": send_file,
                "abort": abort,
                "safe_join": safe_join,
                "request": request,
            }
        )
        print(f"{G}[✓]{RESET} Flask components imported successfully.")
    except Exception as e:
        print(f"{R}[✗]{RESET} Import failed: {e}")
        sys.exit(1)

    print(TERMINAL_BANNER)
    _print_header("STEP 4/4 — Setup Wizard")

    while True:
        root = input(f"{Y}Enter full path to the directory you want to share:{RESET} ").strip()
        if os.path.isdir(root):
            break
        print(f"{R}[✗]{RESET} Invalid path. Please try again.")

    port = 8000
    try:
        c = input(f"{Y}Use default port 8000? (y/n):{RESET} ").strip().lower()
        if c == "n":
            port = int(input(f"{Y}Enter custom port (1024–65535):{RESET} "))
    except:
        print(f"{Y}[i]{RESET} Using default port 8000.")

    server = KuchilaServer(root)
    ip = get_ip()

    print(f"\n{B}─────────────────────────── KUCHILA SERVER STATUS ───────────────────────────{RESET}")
    print(f"{G}📁 Directory:{RESET}  {root}")
    print(f"{B}🌐 Local URL:{RESET}   http://127.0.0.1:{port}")
    print(f"{B}🌍 Network URL:{RESET} http://{ip}:{port}")
    print(f"{Y}⚙️  Mode:{RESET}        File Manager / Web App (auto-detect)")
    print(f"{B}──────────────────────────────────────────────────────────────────────────────{RESET}\n")
    print(f"{G}Tip:{RESET} If a folder contains index.html, you’ll be asked whether to run it as a web app or view files.\n")
    print(f"{Y}Press CTRL+C to stop.{RESET}\n")

    try:
        server.run(host="0.0.0.0", port=port)
    except KeyboardInterrupt:
        print(f"\n{R}🛑 Server stopped by user.{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    check_and_relaunch_in_venv()
    ensure_dependencies()
    main()

