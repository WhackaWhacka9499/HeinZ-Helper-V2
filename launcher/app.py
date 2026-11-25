import importlib.util
import os
import re
import sys
import time
import subprocess
import threading
import webbrowser
import json
import traceback
import psutil
import customtkinter as ctk

CRASH_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash.log")

def log_crash(err):
    try:
        with open(CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] CRASH: {err}\n")
            f.write(traceback.format_exc() + "\n\n")
    except Exception:
        pass

sys.excepthook = lambda t, v, tb: log_crash(v)

# Set appearance mode and color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _resolve_repo_root():
    candidates = [
        os.environ.get("LASTZ_REPO_ROOT", "").strip(),
        os.path.abspath(os.path.join(BASE_DIR, "..")),
        BASE_DIR,
        r".",
        os.path.join(os.path.expanduser("~"), "Desktop", "LastZ-PC-Master-Overhaul"),
        os.getcwd(),
    ]
    for cand in candidates:
        if not cand:
            continue
        tools_cand = os.path.join(cand, "tools")
        if os.path.isdir(tools_cand) and os.path.exists(os.path.join(tools_cand, "client discovery.py")):
            return os.path.abspath(cand)
    return os.path.abspath(os.path.join(BASE_DIR, ".."))


def _resolve_python_cli():
    exe = sys.executable or "python"
    if os.path.basename(exe).lower() == "pythonw.exe":
        console_exe = os.path.join(os.path.dirname(exe), "python.exe")
        if os.path.exists(console_exe):
            return console_exe
    return exe


REPO_ROOT = _resolve_repo_root()
PYTHON_CLI_EXE = _resolve_python_cli()
NO_WINDOW_FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)


def _hidden_startupinfo():
    si_cls = getattr(subprocess, "STARTUPINFO", None)
    if si_cls is None:
        return None
    si = si_cls()
    si.dwFlags |= getattr(subprocess, "STARTF_USESHOWWINDOW", 1)
    si.wShowWindow = 0
    return si
TOOLS_DIR = os.path.join(REPO_ROOT, "tools")
API_DIR = os.path.join(REPO_ROOT, "api")
DAEMON_DIR = os.path.join(REPO_ROOT, "daemon")
DATA_DIR = os.path.join(REPO_ROOT, "data")
BRACKET_DIR = os.path.join(DATA_DIR, "bracket states")

SCRATCH_DIR = r"data/cache"
if not os.path.exists(BRACKET_DIR):
    BRACKET_DIR = os.path.join(SCRATCH_DIR, "bracket_xlsx_perfect")

for p in [TOOLS_DIR, API_DIR, DAEMON_DIR, SCRATCH_DIR]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

# Authoritative Google Apps Script endpoints from project rules
ROSTER_SHEET_URL = "https://script.google.com/macros/s/AKfycbwMVcm76RExNGoxHzWR4afOhHDIVyz--A4m4cG8IJ6PVrYofuPl5cbdS4ADFvXyoqYDdg/exec"
GAMEMASTER_DB_URL = "https://script.google.com/macros/s/AKfycbyXojj8Br_cvFVPpdp5CZpUQfvN_YBMWOQPIutG_1FeeoghayTGizhyg40boiPAE2Y7OQ/exec"


def _load_tool_module(mod_name, rel_path):
    full_path = os.path.join(REPO_ROOT, rel_path)
    if not os.path.exists(full_path):
        return None
    spec = importlib.util.spec_from_file_location(mod_name, full_path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


try:
    _env_mod = _load_tool_module("auto_detect_environment", os.path.join("tools", "auto detect environment.py"))
    if _env_mod is None:
        from auto_detect_environment import detect_environment
    else:
        detect_environment = _env_mod.detect_environment
except Exception:
    def detect_environment(pid=None):
        return {"isLive": False, "serverId": 702, "bracketId": 16, "bracketServers": list(range(689, 705))}

try:
    client_discovery = _load_tool_module("client_discovery", os.path.join("tools", "client discovery.py"))
except Exception:
    client_discovery = None

try:
    sync_farm_clients = _load_tool_module("sync_farm_clients", os.path.join("tools", "sync farm clients.py"))
except Exception:
    sync_farm_clients = None

try:
    multi_client_bot = _load_tool_module("multi_client_bot", os.path.join("tools", "multi client bot.py"))
except Exception:
    multi_client_bot = None

try:
    bot_actions = _load_tool_module("bot_actions", os.path.join("tools", "bot actions.py"))
except Exception:
    bot_actions = None

TASK_LABELS = [
    ("war_safety", "War Safety (Auto-Shield + Recall)"),
    ("hospital_heal", "Hospital Auto-Heal (Help Batches)"),
    ("alliance_daily", "Alliance Red Packets & Tasks"),
    ("research_queue", "Research Queue (Tech + Free Speed)"),
    ("radar_events", "Radar Events (Scan + All Types)"),
    ("daily_tasks_complete", "Daily Tasks (Complete All)"),
    ("daily_claims", "Daily Tasks & Passes"),
    ("free_recruits", "Free Recruits + Safe Bag Chests"),
    ("garage_upgrades", "Garage Upgrades (Monday Refit/Merge)"),
    ("alliance_boss_mine", "Alliance Boss (Bear + Mine)"),
    ("auto_help", "Auto-Help Alliance & Both Gift Tabs"),
    ("rf_hq_under_attack", "RF Attacked HQs"),
    ("vip_store_rewards", "VIP + Store 2nd Tab Rewards"),
    ("hero_battlefield", "Hero Battlefield (Quick Deploy + Auto-Skip)"),
    ("arena", "Arena (Standard x5 Battles)"),
    ("treasure_helicopter", "Treasure Helicopter (March + Click)"),
    ("furylord", "Furylord (03:00 F1 x4)"),
    ("full_preparedness", "Full Preparedness (Tasks + Boxes)"),
    ("speedups", "Smart Speedups (Main: Free Only)"),
    ("troop_training", "Train Troops (Event Speed-Zoom)"),
    ("building_upgrades", "Upgrade HQ / Buildings"),
    ("tyrant_event", "Tyrant Rally (F1 Host + Join)"),
    ("bounties", "Gold Bounties (Lock Orange + Ally Help + Plunder)"),
    ("trucks", "Trade Trucks (Claim + Send Gold)"),
    ("mining_event", "Mining Event (Mon/Tue Lv7 XP)"),
    ("boomer_runs", "Boomer Rallies"),
    ("area_exploration", "Area Exploration (Auto-Skip)"),
]

class HeinZ(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HeinZ")
        self.geometry("1040x980")
        self.minsize(920, 760)
        self.resizable(True, True)
        self.configure(fg_color="#101012")
        self._last_layout_h = 0
        self._last_layout_w = 0

        self.target_pid = None
        self.selected_client_pid = None
        self.selected_client_label = None
        self.discovered_clients = []
        self.running_clients = []
        self._live_info_by_pid = {}
        self._uid_name_cache = {}
        try:
            status_cache = os.path.join(DATA_DIR, "bot status.json")
            if os.path.exists(status_cache):
                with open(status_cache, "r", encoding="utf-8") as sf:
                    sdata = json.load(sf)
                cached_clients = sdata.get("clients") or (sdata.get("last_cycle", {}) or {}).get("clients", [])
                for lc_item in cached_clients:
                    snap = lc_item.get("snapshot") or {}
                    suid = str(snap.get("uid") or "").strip()
                    sname = str(snap.get("name") or "").strip()
                    if suid and sname:
                        self._uid_name_cache[suid] = sname
            for cname in ("client profiles.json", "clients.json"):
                cache_clients = os.path.join(DATA_DIR, cname)
                if os.path.exists(cache_clients):
                    with open(cache_clients, "r", encoding="utf-8") as cf:
                        cdata = json.load(cf)
                    self.discovered_clients = cdata if isinstance(cdata, list) else (cdata.get("clients", []) if isinstance(cdata, dict) else [])
                    if self.discovered_clients:
                        break
            self.running_clients = self._discover_running_clients(query_lua=False)
        except Exception:
            pass
        self._last_dropdown_values = []
        self._last_env_pid = None
        self._last_env_ts = 0.0
        self.task_vars = {}
        self.auto_launch_var = None
        self.main_enabled_var = None
        self.is_monitoring = True
        self.env = {
            "isLive": False,
            "serverId": 702,
            "playerName": "Heinzy",
            "allianceTag": "WARG",
            "bracketId": 16,
            "bracketServers": list(range(689, 705))
        }

        self.create_widgets()

        # Initial environment check
        self.refresh_environment_once()

        # Start background game monitor
        self.monitor_thread = threading.Thread(target=self.poll_game_status, daemon=True)
        self.monitor_thread.start()

        # Ensure background engine daemon is running
        self.ensure_daemon_running()

    def create_widgets(self):
        # Centered responsive dashboard shell (prevents ultrawide/maximized stretching)
        self.main_shell = ctk.CTkFrame(self, fg_color="transparent")
        self.main_shell.pack(fill="both", expand=True, padx=0, pady=0)

# - Header Frame & Metrics
        header = ctk.CTkFrame(self.main_shell, fg_color="#18181B", corner_radius=10)
        header.pack(side="top", fill="x", padx=14, pady=(10, 4))

        top_row = ctk.CTkFrame(header, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(10, 2))

        title_lbl = ctk.CTkLabel(
            top_row,
            text="HeinZ",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#F4F4F5"
        )
        title_lbl.pack(side="left")

        sub_lbl = ctk.CTkLabel(
            top_row,
            text="PC Control Center & Strategic Intelligence",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#71717A"
        )
        sub_lbl.pack(side="left", padx=(10, 0), pady=(3, 0))

        # Status indicators and target client selector on top right
        status_box = ctk.CTkFrame(top_row, fg_color="transparent")
        status_box.pack(side="right")

        target_box = ctk.CTkFrame(top_row, fg_color="transparent")
        target_box.pack(side="right", padx=(0, 12))

        ctk.CTkLabel(
            target_box,
            text="Target:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#A1A1AA"
        ).pack(side="left", padx=(0, 6))

        self.combo_target_client = ctk.CTkComboBox(
            target_box,
            values=["Auto"],
            width=205,
            height=26,
            state="readonly",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            command=self.on_select_target_client
        )
        self.combo_target_client.set("Auto")
        self.combo_target_client.pack(side="left")

        self.fps_badge = ctk.CTkLabel(
            status_box,
            text="180 FPS",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#10B981",
            fg_color="#064E3B",
            corner_radius=4,
            padx=6,
            pady=2
        )
        self.fps_badge.pack(side="right", padx=(8, 0))

        self.status_dot = ctk.CTkLabel(
            status_box,
            text="●",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#10B981"
        )
        self.status_dot.pack(side="left")

        self.status_text = ctk.CTkLabel(
            status_box,
            text="Engine Active",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#F4F4F5"
        )
        self.status_text.pack(side="left", padx=(4, 0))

        # Metric Pills Bar
        pill_bar = ctk.CTkFrame(header, fg_color="#27272A", corner_radius=6)
        pill_bar.pack(fill="x", padx=12, pady=(6, 10))

        # Pill 1: Active State & Server
        p1 = ctk.CTkFrame(pill_bar, fg_color="transparent")
        p1.pack(side="left", expand=True, padx=4, pady=4)
        ctk.CTkLabel(p1, text="Active State", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color="#A1A1AA").pack(anchor="center")
        self.val_state = ctk.CTkLabel(p1, text="State #702", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#F4F4F5")
        self.val_state.pack(anchor="center")

        # Pill 2: VS Duel Matchup
        p2 = ctk.CTkFrame(pill_bar, fg_color="transparent")
        p2.pack(side="left", expand=True, padx=4, pady=4)
        ctk.CTkLabel(p2, text="VS Duel", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color="#A1A1AA").pack(anchor="center")
        self.val_duel = ctk.CTkLabel(p2, text="702 vs 700", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#F4F4F5")
        self.val_duel.pack(anchor="center")

        # Pill 3: Alliance
        p3 = ctk.CTkFrame(pill_bar, fg_color="transparent")
        p3.pack(side="left", expand=True, padx=4, pady=4)
        ctk.CTkLabel(p3, text="Alliance", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color="#A1A1AA").pack(anchor="center")
        self.val_alliance = ctk.CTkLabel(p3, text="[WARG] WARGODS", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#F4F4F5")
        self.val_alliance.pack(anchor="center")

        # Pill 4: Bracket Range
        p4 = ctk.CTkFrame(pill_bar, fg_color="transparent")
        p4.pack(side="left", expand=True, padx=4, pady=4)
        ctk.CTkLabel(p4, text="Bracket", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color="#A1A1AA").pack(anchor="center")
        self.val_bracket = ctk.CTkLabel(p4, text="Bracket #16 (16 States)", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#F4F4F5")
        self.val_bracket.pack(anchor="center")

        # Pill 5: Map Status
        p5 = ctk.CTkFrame(pill_bar, fg_color="transparent")
        p5.pack(side="left", expand=True, padx=4, pady=4)
        ctk.CTkLabel(p5, text="Map Intel", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color="#A1A1AA").pack(anchor="center")
        self.val_map = ctk.CTkLabel(p5, text="2,180 Bases (1,545 Open)", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#F4F4F5")
        self.val_map.pack(anchor="center")

        # 2. Bottom Console Log Box (locked to bottom ~20% so tabs show all controls)
        self.log_frame = ctk.CTkFrame(self.main_shell, fg_color="#18181B", corner_radius=10, height=175)
        self.log_frame.pack(side="bottom", fill="x", expand=False, padx=14, pady=(4, 8))
        self.log_frame.pack_propagate(False)

        log_hdr = ctk.CTkFrame(self.log_frame, fg_color="transparent")
        log_hdr.pack(fill="x", padx=12, pady=(5, 2))

        ctk.CTkLabel(
            log_hdr,
            text="EXECUTION LOG",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#71717A"
        ).pack(side="left")

        btn_clear = ctk.CTkButton(
            log_hdr,
            text="Clear",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#27272A",
            hover_color="#3F3F46",
            width=50,
            height=20,
            command=self.clear_log
        )
        btn_clear.pack(side="right")

        self.log_box = ctk.CTkTextbox(
            self.log_frame,
            fg_color="#0F0F11",
            text_color="#E4E4E7",
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=6
        )
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(2, 8))

        # 3. Category Tab View (Game | Alliances | Map | Farms / Bot)
        self.tabs = ctk.CTkTabview(
            self.main_shell,
            fg_color="#141416",
            segmented_button_fg_color="#27272A",
            segmented_button_selected_color="#2563EB",
            segmented_button_selected_hover_color="#1D4ED8",
            segmented_button_unselected_hover_color="#3F3F46",
            text_color="#F4F4F5",
            corner_radius=8
        )
        self.tabs.pack(side="top", fill="both", expand=True, padx=14, pady=(2, 4))
        self.bind("<Configure>", self._on_window_resize)

        tab_game = self.tabs.add("  GAME  ")
        tab_alliances = self.tabs.add("  ALLIANCES  ")
        tab_map = self.tabs.add("  MAP  ")
        tab_bots = self.tabs.add("  FARMS / BOT  ")

        # TAB 1: GAME
        body_game = self._create_tab_body(tab_game)
        # Card 1A: Engine Hardware & Performance
        c_perf = self.create_card(body_game, "HARDWARE ACCELERATION & ENGINE", expand=False)
        grid_perf = ctk.CTkFrame(c_perf, fg_color="transparent")
        grid_perf.pack(fill="x", padx=10, pady=(4, 8))
        grid_perf.grid_columnconfigure((0, 1), weight=1, uniform="perf_cols")

        self.add_btn(grid_perf, 0, 0, "Apply 180 FPS & Wide Preloader", "#D97706", "#B45309", self.on_apply_engine, width=None)
        self.add_btn(grid_perf, 0, 1, "Flush RAM & Garbage Collect", "#475569", "#334155", self.on_flush_ram, width=None)
        self.add_btn(grid_perf, 1, 0, "Instant Heli Help All (Silent)", "#059669", "#047857", self.on_trigger_heli, width=None)
        self.add_btn(grid_perf, 1, 1, "Restart Background Daemon", "#2563EB", "#1D4ED8", self.on_restart_daemon, width=None)

        # Card 1B: Account Reserves & Bag Audit
        c_acc = self.create_card(body_game, "ACCOUNT RESERVES & BAG INVENTORY", expand=False)
        grid_acc = ctk.CTkFrame(c_acc, fg_color="transparent")
        grid_acc.pack(fill="x", padx=10, pady=(4, 8))
        grid_acc.grid_columnconfigure((0, 1), weight=1, uniform="acc_cols")

        self.add_btn(grid_acc, 0, 0, "Export Inventory", "#2563EB", "#1D4ED8", self.on_export_inventory, width=None)
        self.add_btn(grid_acc, 0, 1, "Export Tech Tree Progress (Excel)", "#2563EB", "#1D4ED8", self.on_export_tech, width=None)
        self.add_btn(grid_acc, 1, 0, "Open Data Master Workspace", "#475569", "#334155", self.on_open_data_folder, width=None)
        self.add_btn(grid_acc, 1, 1, "Open Working Scratch Folder", "#475569", "#334155", lambda: os.startfile(SCRATCH_DIR), width=None)

        # TAB 2: ALLIANCES
        body_alliances = self._create_tab_body(tab_alliances)
        # Card 2A: VS Duel War Intelligence
        c_vs = self.create_card(body_alliances, "VS DUEL WAR INTELLIGENCE (AUTO-DETECTED)", expand=False)
        grid_vs = ctk.CTkFrame(c_vs, fg_color="transparent")
        grid_vs.pack(fill="x", padx=10, pady=(4, 8))
        grid_vs.grid_columnconfigure((0, 1), weight=1, uniform="vs_cols")

        self.btn_export_vs = self.add_btn(grid_vs, 0, 0, "Export VS Duel: #702 vs #700 (Excel)", "#2563EB", "#1D4ED8", self.on_export_vs, width=None)
        self.add_btn(grid_vs, 0, 1, "Open VS Duel Excel Workbook", "#059669", "#047857", lambda: self.open_file("vs_duel_rankings.xlsx"), width=None)

        # Card 2B: Alliance Roster & Bracket Migration Intel
        c_al = self.create_card(body_alliances, "ALLIANCE ROSTER & BRACKET MIGRATION INTEL", expand=False)
        grid_al = ctk.CTkFrame(c_al, fg_color="transparent")
        grid_al.pack(fill="x", padx=10, pady=(4, 8))
        grid_al.grid_columnconfigure((0, 1), weight=1, uniform="al_cols")

        self.btn_export_roster = self.add_btn(grid_al, 0, 0, "Export Alliance Roster (Excel)", "#2563EB", "#1D4ED8", self.on_export_roster, width=None)
        self.add_btn(grid_al, 0, 1, "Export Alliance Members (Excel)", "#2563EB", "#1D4ED8", self.on_export_alliance_members, width=None)
        self.btn_active_mig = self.add_btn(grid_al, 1, 0, "Open State 702 Migration Excel", "#059669", "#047857", self.on_open_active_migration, width=None)
        self.add_btn(grid_al, 1, 1, "Export Top 10 Alliances Master", "#2563EB", "#1D4ED8", self.on_export_top10, width=None)
        self.add_btn(grid_al, 2, 0, "Open Main Google Sheet Roster", "#475569", "#334155", lambda: webbrowser.open(ROSTER_SHEET_URL), colspan=2, width=None)

        # Card 2C: Interactive Bracket State Selector (All 16 States)
        c_bracket = self.create_card(body_alliances, "BRACKET STATE EXPLORER (CHOOSE STATE TO INSPECT)", expand=False)
        bracket_row = ctk.CTkFrame(c_bracket, fg_color="transparent")
        bracket_row.pack(fill="x", padx=10, pady=(4, 8))

        ctk.CTkLabel(bracket_row, text="State:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#A1A1AA").pack(side="left", padx=(4, 6))

        bracket_vals = [f"State {s}" for s in range(689, 705)]
        self.combo_bracket = ctk.CTkComboBox(
            bracket_row, 
            values=bracket_vals,
            width=130,
            height=28,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        )
        self.combo_bracket.set(f"State {self.env.get('serverId', 702)}")
        self.combo_bracket.pack(side="left", padx=4)

        btn_open_selected_state = ctk.CTkButton(
            bracket_row,
            text="Open State Migration Workbook",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            height=28,
            command=self.on_open_selected_bracket_state
        )
        btn_open_selected_state.pack(side="left", padx=6)

        btn_open_bracket_folder = ctk.CTkButton(
            bracket_row,
            text="All 16 Workbooks",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#475569",
            hover_color="#334155",
            height=28,
            command=self.on_open_bracket_folder
        )
        btn_open_bracket_folder.pack(side="left", padx=4)

        # TAB 3: MAP
        body_map = self._create_tab_body(tab_map)
        # Card 3A: Map Scanner
        c_map = self.create_card(body_map, "FULL MAP SCANNER & INTEL", expand=False)
        grid_map = ctk.CTkFrame(c_map, fg_color="transparent")
        grid_map.pack(fill="x", padx=10, pady=(4, 8))
        grid_map.grid_columnconfigure((0, 1), weight=1, uniform="map_cols")

        self.add_btn(grid_map, 0, 0, "Export Full Map Data", "#2563EB", "#1D4ED8", self.on_export_map, width=None)
        self.add_btn(grid_map, 0, 1, "Open All Bases (Excel)", "#059669", "#047857", lambda: self.open_file("map_all_bases.xlsx"), width=None)
        self.add_btn(grid_map, 1, 0, "Open All Resources (CSV)", "#475569", "#334155", lambda: self.open_file("map_all_resources.csv"), width=None)
        self.add_btn(grid_map, 1, 1, "Open Map Summary (Excel)", "#059669", "#047857", self.on_open_map_summary_excel, width=None)

        # Card 3B: Resource Locator & In-Game Direct Navigator (NEW!)
        c_finder = self.create_card(body_map, "RESOURCE LOCATOR & DIRECT IN-GAME NAVIGATOR", expand=False)
        finder_box = ctk.CTkFrame(c_finder, fg_color="transparent")
        finder_box.pack(fill="x", padx=10, pady=(4, 8))

        f_row = ctk.CTkFrame(finder_box, fg_color="transparent")
        f_row.pack(fill="x", pady=2)

        ctk.CTkLabel(f_row, text="Resource:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#A1A1AA").pack(side="left", padx=(4, 6))
        self.combo_res_type = ctk.CTkComboBox(
            f_row,
            values=["Mine", "Lumberyard", "Farm", "Diamonds", "Windmill (electricity)"],
            width=180,
            height=28,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        )
        self.combo_res_type.set("Mine")
        self.combo_res_type.pack(side="left", padx=4)

        ctk.CTkLabel(f_row, text="Level:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#A1A1AA").pack(side="left", padx=(10, 6))
        self.combo_res_lvl = ctk.CTkComboBox(
            f_row,
            values=["Level 8", "Level 7", "Level 6", "Level 5", "Level 4", "Level 3", "Any Level"],
            width=110,
            height=28,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        )
        self.combo_res_lvl.set("Level 6")
        self.combo_res_lvl.pack(side="left", padx=4)

        btn_go = ctk.CTkButton(
            f_row,
            text="GO (Navigate In-Game)",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            width=165,
            height=28,
            command=self.on_navigate_resource
        )
        btn_go.pack(side="left", padx=(10, 4))

        btn_dispatch = ctk.CTkButton(
            f_row,
            text="DISPATCH SQUAD (Auto-March)",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            width=185,
            height=28,
            command=self.on_dispatch_resource
        )
        btn_dispatch.pack(side="left", padx=4)

        self.lbl_finder_status = ctk.CTkLabel(
            finder_box,
            text="Ready: Select resource type and level, then click GO to jump in-game or DISPATCH SQUAD to auto-march.",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#A1A1AA"
        )
        self.lbl_finder_status.pack(anchor="w", padx=6, pady=(4, 2))

        # Card 3C: Target Reconnaissance & Scout Radar (Reworded)
        c_radar = self.create_card(body_map, "TARGET RECONNAISSANCE & SCOUT RADAR", expand=False)
        grid_radar = ctk.CTkFrame(c_radar, fg_color="transparent")
        grid_radar.pack(fill="x", padx=10, pady=(4, 8))
        grid_radar.grid_columnconfigure((0, 1), weight=1, uniform="radar_cols")

        self.add_btn(grid_radar, 0, 0, "Export Unshielded Targets", "#DC2626", "#B91C1C", self.on_export_radar, width=None)
        self.add_btn(grid_radar, 0, 1, "Export Elite Targets", "#DC2626", "#B91C1C", self.on_export_elite_radar, width=None)
        self.add_btn(grid_radar, 1, 0, "Export High-Tier Mines", "#059669", "#047857", self.on_export_mines, width=None)
        self.add_btn(grid_radar, 1, 1, "Open Unshielded Targets (Excel)", "#475569", "#334155", lambda: self.open_file("unshielded_targets.xlsx"), width=None)

        # TAB 4: FARMS / BOT
        self._build_farms_bot_tab(tab_bots)

        self.log("HeinZ Control Hub initialized.")
        self.log(f"Active Workspace: {REPO_ROOT}")
        self._load_bot_config_into_ui()
        self._refresh_fleet_ui()
        self._update_target_dropdown_ui(self.running_clients, None)

    # Helpers: UI Card & Button Builders
    def create_card(self, parent, title, expand=True, pack_card=True):
        card = ctk.CTkFrame(parent, fg_color="#18181B", corner_radius=8)
        if pack_card:
            card.pack(fill="both" if expand else "x", expand=expand, padx=10, pady=4)

        lbl = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#71717A"
        )
        lbl.pack(anchor="w", padx=10, pady=(5, 2))
        return card

    def add_btn(self, parent, row, col, text, fg, hover, cmd, colspan=1, height=30, width=215):
        btn_kwargs = dict(
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=fg,
            hover_color=hover,
            height=height,
            corner_radius=6,
            command=cmd,
        )
        if width is not None:
            btn_kwargs["width"] = width
        btn = ctk.CTkButton(parent, **btn_kwargs)
        grid_kwargs = dict(row=row, column=col, columnspan=colspan, padx=8, pady=3)
        if width is None:
            grid_kwargs["sticky"] = "ew"
        btn.grid(**grid_kwargs)
        for c in range(col, col + colspan):
            parent.grid_columnconfigure(c, weight=1)
        return btn

    def _create_tab_body(self, tab):
        body = ctk.CTkScrollableFrame(
            tab,
            fg_color="#141416",
            scrollbar_button_color="#27272A",
            scrollbar_button_hover_color="#3F3F46",
        )
        body.pack(fill="both", expand=True, padx=2, pady=2)
        return body

    def _on_window_resize(self, event=None):
        if event is None or event.widget is not self or not hasattr(self, "log_frame"):
            return
        win_h = int(getattr(event, "height", 0) or 0)
        win_w = int(getattr(event, "width", 0) or 0)
        try:
            scaling = max(0.5, float(self._get_window_scaling()))
        except Exception:
            scaling = 1.0

        if win_h > 100 and abs(win_h - self._last_layout_h) >= 12:
            self._last_layout_h = win_h
            logical_h = int(win_h / scaling)
            target_h = max(125, min(210, int(logical_h * 0.20)))
            try:
                self.log_frame.configure(height=target_h)
            except Exception:
                pass

        if win_w > 200 and abs(win_w - self._last_layout_w) >= 12 and hasattr(self, "main_shell"):
            self._last_layout_w = win_w
            logical_w = int(win_w / scaling)
            side_pad = max(0, (logical_w - 1240) // 2) if logical_w > 1260 else 0
            try:
                self.main_shell.pack_configure(padx=side_pad)
            except Exception:
                pass

    def log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{timestamp}] {msg}\n")
        self.log_box.see("end")

    def clear_log(self):
        self.log_box.delete("1.0", "end")

    def run_worker(self, target_func):
        threading.Thread(target=target_func, daemon=True).start()

    def _subprocess_env(self):
        env = os.environ.copy()
        if self.target_pid:
            env["LASTZ_TARGET_PID"] = str(self.target_pid)
        else:
            env.pop("LASTZ_TARGET_PID", None)
        return env

    def _pid_args(self):
        return ["--pid", str(self.target_pid)] if self.target_pid else []

    def _begin_action(self, key):
        active = getattr(self, "_active_actions", None)
        if active is None:
            active = set()
            self._active_actions = active
        if key in active:
            return False
        active.add(key)
        return True

    def _end_action(self, key):
        active = getattr(self, "_active_actions", None)
        if active is not None:
            active.discard(key)

    def _subproc_run(self, args, timeout=15, env=None):
        return subprocess.run(
            args,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=REPO_ROOT,
            env=env,
            creationflags=NO_WINDOW_FLAGS,
            startupinfo=_hidden_startupinfo(),
        )

    def _subproc_popen(self, args, creationflags=NO_WINDOW_FLAGS, env=None):
        flags = (creationflags or 0) | NO_WINDOW_FLAGS
        return subprocess.Popen(
            args,
            cwd=REPO_ROOT,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
            startupinfo=_hidden_startupinfo(),
        )

    def _run_tool(self, script_name, extra_args=None, timeout=30, env=None, utf8=True):
        script = self.find_script(script_name)
        if not script or not os.path.exists(script):
            raise FileNotFoundError(f"Script not found in {REPO_ROOT}: {script_name}")
        cmd = [PYTHON_CLI_EXE]
        if utf8:
            cmd.extend(["-X", "utf8"])
        cmd.append(script)
        if extra_args:
            cmd.extend(extra_args)
        return self._subproc_run(cmd, timeout=timeout, env=env)

    def _build_farms_bot_tab(self, tab_bots):
        layout = self._create_tab_body(tab_bots)

        # Card 4A: Client Fleet & Multi-Account Launcher
        c_fleet = self.create_card(layout, "CLIENT FLEET & MULTI-ACCOUNT LAUNCHER", expand=False)
        ctrl_row = ctk.CTkFrame(c_fleet, fg_color="transparent")
        ctrl_row.pack(fill="x", padx=12, pady=(2, 4))

        ctk.CTkLabel(
            ctrl_row,
            text="Launch Mode:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#A1A1AA"
        ).pack(side="left", padx=(0, 6))

        self.combo_launch_mode = ctk.CTkComboBox(
            ctrl_row,
            values=["Eco", "Windowed", "Hidden"],
            width=115,
            height=26,
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        self.combo_launch_mode.set("Eco")
        self.combo_launch_mode.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(
            ctrl_row,
            text="Cycle Scope:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#A1A1AA"
        ).pack(side="left", padx=(0, 6))

        self.combo_cycle_scope = ctk.CTkComboBox(
            ctrl_row,
            values=["All Running", "Selected Client", "Main Only", "Farms Only"],
            width=145,
            height=26,
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        self.combo_cycle_scope.set("All Running")
        self.combo_cycle_scope.pack(side="left", padx=(0, 12))

        self.lbl_fleet_summary = ctk.CTkLabel(
            ctrl_row,
            text="Fleet: Initializing...",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#A1A1AA"
        )
        self.lbl_fleet_summary.pack(side="right", padx=(8, 0))

        grid_fleet = ctk.CTkFrame(c_fleet, fg_color="transparent")
        grid_fleet.pack(fill="x", padx=10, pady=(2, 8))
        for c in range(6):
            grid_fleet.grid_columnconfigure(c, weight=1, uniform="fleet_cols")
        self.add_btn(grid_fleet, 0, 0, "Scan For Survival.exe", "#2563EB", "#1D4ED8", self.on_scan_fleet, colspan=2, height=28, width=None)
        self.add_btn(grid_fleet, 0, 2, "Sync Farm Game Builds", "#475569", "#334155", self.on_sync_farm_builds, colspan=2, height=28, width=None)
        self.add_btn(grid_fleet, 0, 4, "+ Provision Farm Clone", "#7C3AED", "#6D28D9", self.on_provision_farm_client, colspan=2, height=28, width=None)
        self.add_btn(grid_fleet, 1, 1, "Launch All Farm Clients", "#059669", "#047857", self.on_launch_all_farms, colspan=2, height=28, width=None)
        self.add_btn(grid_fleet, 1, 3, "Stop All Farm Clients", "#DC2626", "#B91C1C", self.on_stop_all_farms, colspan=2, height=28, width=None)

        # Card 4B: Automation Modules & Schedule Config
        c_cfg = self.create_card(layout, "MULTI-CLIENT AUTOMATION MODULES (28 TASKS)", expand=False)
        grid_tasks = ctk.CTkFrame(c_cfg, fg_color="transparent")
        grid_tasks.pack(fill="x", padx=12, pady=(2, 4))
        for c in range(3):
            grid_tasks.grid_columnconfigure(c, weight=1, uniform="task_cols")

        for idx, (task_key, task_label) in enumerate(TASK_LABELS):
            var = ctk.BooleanVar(value=True)
            self.task_vars[task_key] = var
            chk = ctk.CTkCheckBox(
                grid_tasks,
                text=task_label,
                variable=var,
                checkbox_width=18,
                checkbox_height=18,
                height=22,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="#E4E4E7",
                command=lambda: self.on_save_bot_config(quiet=True)
            )
            chk.grid(row=idx // 3, column=idx % 3, padx=8, pady=2, sticky="w")

        sched_row = ctk.CTkFrame(c_cfg, fg_color="transparent")
        sched_row.pack(fill="x", padx=12, pady=(3, 6))

        self.auto_launch_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            sched_row,
            text="Auto-launch stopped clients",
            variable=self.auto_launch_var,
            checkbox_width=18,
            checkbox_height=18,
            height=22,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#E4E4E7",
            command=lambda: self.on_save_bot_config(quiet=True)
        ).pack(side="left", padx=(0, 12))

        self.main_enabled_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            sched_row,
            text="Automate Main",
            variable=self.main_enabled_var,
            checkbox_width=18,
            checkbox_height=18,
            height=22,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#E4E4E7",
            command=lambda: self.on_save_bot_config(quiet=True)
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            sched_row,
            text="Cycle (s):",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#A1A1AA"
        ).pack(side="left", padx=(0, 4))
        self.entry_cycle_sec = ctk.CTkEntry(sched_row, width=56, height=24, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_cycle_sec.insert(0, "180")
        self.entry_cycle_sec.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            sched_row,
            text="Task (min):",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#A1A1AA"
        ).pack(side="left", padx=(0, 4))
        self.entry_task_min = ctk.CTkEntry(sched_row, width=50, height=24, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_task_min.insert(0, "15")
        self.entry_task_min.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            sched_row,
            text="Save Config",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            width=98,
            height=26,
            command=lambda: self.on_save_bot_config(quiet=False)
        ).pack(side="right")

        ctk.CTkButton(
            sched_row,
            text="Trucks & Event Rules...",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#4F46E5",
            hover_color="#4338CA",
            width=150,
            height=26,
            command=self.open_event_rules_modal
        ).pack(side="right", padx=(0, 8))

        # Card 4C: Bot Orchestrator, Schedule & Google Bracket Sync
        c_orch = self.create_card(layout, "BOT ORCHESTRATOR, WINDOWS SCHEDULE & GOOGLE DRIVE BRACKET SYNC", expand=False)
        self.lbl_bot_status = ctk.CTkLabel(
            c_orch,
            text="Daemon: Checking... | Windows Task: Checking...",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#A1A1AA"
        )
        self.lbl_bot_status.pack(anchor="w", padx=12, pady=(1, 4))

        grid_orch = ctk.CTkFrame(c_orch, fg_color="transparent")
        grid_orch.pack(fill="x", padx=10, pady=(2, 8))
        for c in range(4):
            grid_orch.grid_columnconfigure(c, weight=1, uniform="orch_cols")
        self.add_btn(grid_orch, 0, 0, "Run Bot Cycle Now (Live)", "#D97706", "#B45309", lambda: self.on_run_bot_cycle(False), height=28, width=None)
        self.add_btn(grid_orch, 0, 1, "Dry-Run Audit (Safe)", "#2563EB", "#1D4ED8", lambda: self.on_run_bot_cycle(True), height=28, width=None)
        self.add_btn(grid_orch, 0, 2, "Start Bot Daemon", "#059669", "#047857", self.on_start_bot_daemon, height=28, width=None)
        self.add_btn(grid_orch, 0, 3, "Stop Bot Daemon", "#DC2626", "#B91C1C", self.on_stop_bot_daemon, height=28, width=None)
        self.add_btn(grid_orch, 1, 0, "Register Win Schedule", "#475569", "#334155", self.on_install_bot_task, height=28, width=None)
        self.add_btn(grid_orch, 1, 1, "Remove Win Schedule", "#475569", "#334155", self.on_uninstall_bot_task, height=28, width=None)
        self.add_btn(grid_orch, 1, 2, "Sync 16 Bracket Sheets to Drive", "#059669", "#047857", self.on_sync_google_bracket, colspan=2, height=28, width=None)

    def find_script(self, name):
        candidates = [
            os.path.join(TOOLS_DIR, name),
            os.path.join(TOOLS_DIR, name.replace("_", " ")),
            os.path.join(TOOLS_DIR, name.replace(" ", "_")),
            os.path.join(REPO_ROOT, "daemon", name),
            os.path.join(REPO_ROOT, "daemon", name.replace("_", " ")),
            os.path.join(REPO_ROOT, "daemon", name.replace(" ", "_")),
            os.path.join(REPO_ROOT, "api", name),
            os.path.join(REPO_ROOT, "api", name.replace("_", " ")),
            os.path.join(REPO_ROOT, "api", name.replace(" ", "_")),
            os.path.join(SCRATCH_DIR, name),
            os.path.join(SCRATCH_DIR, name.replace("_", " ")),
            os.path.join(SCRATCH_DIR, name.replace(" ", "_")),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return os.path.join(TOOLS_DIR if os.path.isdir(TOOLS_DIR) else SCRATCH_DIR, name)

    def find_file(self, name):
        candidates = [
            os.path.join(DATA_DIR, name),
            os.path.join(DATA_DIR, name.replace("_", " ")),
            os.path.join(DATA_DIR, name.replace(" ", "_")),
            os.path.join(SCRATCH_DIR, name),
            os.path.join(SCRATCH_DIR, name.replace("_", " ")),
            os.path.join(SCRATCH_DIR, name.replace(" ", "_")),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return os.path.join(SCRATCH_DIR, name)

    def open_file(self, rel_name):
        path = self.find_file(rel_name)
        if os.path.exists(path):
            self.log(f"Opening: {os.path.basename(path)}")
            os.startfile(path)
        else:
            self.log(f"File not found: {rel_name}")
    def refresh_environment_once(self):
        try:
            cache_path = os.path.join(SCRATCH_DIR, "detected_environment.json")
            if os.path.exists(cache_path):
                with open(cache_path, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                    if cached:
                        self.apply_environment(cached)
        except Exception:
            pass

    def _client_display_name(self, proc):
        if not proc:
            return "Client"
        pid = int(proc["pid"]) if proc.get("pid") is not None else None
        live = self._live_info_by_pid.get(pid, {}) if pid is not None else {}
        name = str(proc.get("name") or live.get("name") or "").strip()
        if name:
            return name
        reg_uid = str(proc.get("uid") or proc.get("reg_uid") or "").strip()
        if reg_uid and reg_uid in self._uid_name_cache:
            return self._uid_name_cache[reg_uid]
        return str(proc.get("label") or proc.get("unity_profile") or "Client")

    def on_select_target_client(self, choice):
        c = str(choice or "Auto").strip()
        if c == "Auto":
            self.selected_client_pid = None
            self.selected_client_label = None
            self.log("Target client set to Auto (prefers Main).")
            return
        m = re.search(r"\(PID\s+(\d+)\)\s*$", c)
        picked_pid = int(m.group(1)) if m else None
        proc = next((p for p in self.running_clients if int(p["pid"]) == picked_pid), None) if picked_pid is not None else None
        if proc is None:
            prefix = c.split(" (PID ", 1)[0].strip()
            proc = next((p for p in self.running_clients if prefix in (self._client_display_name(p), str(p.get("label") or ""))), None)
        if proc is not None:
            self.selected_client_pid = int(proc["pid"])
            self.selected_client_label = str(proc.get("label") or "") or None
            self.target_pid = self.selected_client_pid
            os.environ["LASTZ_TARGET_PID"] = str(self.target_pid)
        else:
            self.selected_client_pid = picked_pid
            self.selected_client_label = c.split(" (PID ", 1)[0].strip() or None
            if picked_pid is not None:
                self.target_pid = picked_pid
                os.environ["LASTZ_TARGET_PID"] = str(picked_pid)
        self._last_env_ts = 0.0
        self.log(f"Target client switched to {choice}.")

    def _discover_running_clients(self, query_lua=False, force_pids=None):
        if client_discovery is not None:
            running = client_discovery.find_running_processes()
        else:
            running = []
            exe_roles = {"survival.exe": ("Main", "main"), "farmgame.exe": ("Farm", "farm"), "alt3game.exe": ("Third", "farm")}
            for proc in psutil.process_iter(["pid", "name"]):
                nm = str(proc.info.get("name") or "")
                if nm.lower() in exe_roles:
                    lbl, role = exe_roles[nm.lower()]
                    running.append({"pid": int(proc.info["pid"]), "exe_name": nm, "label": lbl, "role": role})

        active_pids = {int(c["pid"]) for c in running}
        for dead_pid in list(self._live_info_by_pid.keys()):
            if dead_pid not in active_pids:
                self._live_info_by_pid.pop(dead_pid, None)

        force_set = set(force_pids or [])
        for item in running:
            pid = int(item["pid"])
            cached_live = self._live_info_by_pid.get(pid)
            need_query = query_lua and (cached_live is None or not cached_live.get("loggedIn") or pid in force_set)
            if need_query and client_discovery is not None:
                try:
                    if client_discovery._xlua_loaded(pid):
                        ok, out = client_discovery.frida_eval_lua(pid, client_discovery.LUA_QUICK_STATUS)
                        if ok:
                            data = json.loads(out)
                            if isinstance(data, dict):
                                self._live_info_by_pid[pid] = data
                                uid_str = str(data.get("uid") or "").strip()
                                nm_str = str(data.get("name") or "").strip()
                                if uid_str and nm_str:
                                    self._uid_name_cache[uid_str] = nm_str
                except Exception:
                    pass
            live = self._live_info_by_pid.get(pid)
            if live:
                for lk in ("loggedIn", "name", "uid", "serverId", "selfServerId", "allianceTag", "hqLv"):
                    if live.get(lk) not in (None, ""):
                        item[lk] = live[lk]
        return running

    def _update_target_dropdown_ui(self, running, active_proc):
        values = ["Auto"] + [f"{self._client_display_name(c)} (PID {c['pid']})" for c in running]
        if values != self._last_dropdown_values:
            self._last_dropdown_values = list(values)
            self.combo_target_client.configure(values=values)
        matched = None
        if self.selected_client_pid is not None:
            matched = next((v for v in values if v.endswith(f"(PID {self.selected_client_pid})")), None)
        if matched is None and self.selected_client_label:
            lbl_proc = next((c for c in running if str(c.get("label") or "") == self.selected_client_label), None)
            if lbl_proc is not None:
                self.selected_client_pid = int(lbl_proc["pid"])
                matched = next((v for v in values if v.endswith(f"(PID {self.selected_client_pid})")), None)
        if matched:
            if self.combo_target_client.get() != matched:
                self.combo_target_client.set(matched)
        elif self.selected_client_pid is None and self.selected_client_label is None:
            if self.combo_target_client.get() != "Auto":
                self.combo_target_client.set("Auto")

    def poll_game_status(self):
        loop_idx = 0
        while self.is_monitoring:
            try:
                refresh_all_pids = [int(c["pid"]) for c in self.running_clients] if (loop_idx % 5 == 0) else None
                running = self._discover_running_clients(query_lua=True, force_pids=refresh_all_pids)
                self.running_clients = running

                if client_discovery is not None and (loop_idx % 5 == 0 or not self.discovered_clients):
                    disc = client_discovery.discover_clients(save_cache=False)
                    self.discovered_clients = disc if isinstance(disc, list) else (disc.get("clients", []) if isinstance(disc, dict) else [])

                active_proc = None
                if running:
                    if self.selected_client_pid is not None:
                        active_proc = next((c for c in running if int(c["pid"]) == self.selected_client_pid), None)
                    if active_proc is None and self.selected_client_label:
                        active_proc = next((c for c in running if str(c.get("label")) == self.selected_client_label), None)
                    if active_proc is None:
                        mains = [c for c in running if str(c.get("role", "")).lower() == "main"]
                        active_proc = mains[0] if mains else running[0]

                self.after(0, lambda r=running, a=active_proc: self._update_target_dropdown_ui(r, a))

                if active_proc is not None:
                    pid = int(active_proc["pid"])
                    self.target_pid = pid
                    os.environ["LASTZ_TARGET_PID"] = str(pid)
                    disp_name = self._client_display_name(active_proc)
                    status_lbl = f"{len(running)} Online | {disp_name} (PID {pid})"
                    self.after(0, lambda t=status_lbl: self.set_status(True, t))
                    now = time.time()
                    if pid != self._last_env_pid or (now - self._last_env_ts) >= 25.0:
                        try:
                            env = detect_environment(pid)
                            self._last_env_pid = pid
                            self._last_env_ts = now
                            pname = str((env or {}).get("playerName") or "").strip()
                            puid = str((env or {}).get("playerUid") or "").strip()
                            if pname:
                                self._live_info_by_pid.setdefault(pid, {}).update({"loggedIn": True, "name": pname, "uid": puid})
                                if puid:
                                    self._uid_name_cache[puid] = pname
                                self.after(0, lambda r=self.running_clients, a=active_proc: self._update_target_dropdown_ui(r, a))
                            self.after(0, lambda e=env: self.apply_environment(e))
                        except Exception:
                            pass
                else:
                    self.target_pid = None
                    os.environ.pop("LASTZ_TARGET_PID", None)
                    self.after(0, lambda: self.set_status(False, "No Client Running"))

                if loop_idx % 3 == 0:
                    bot_status = {}
                    if multi_client_bot is not None:
                        try:
                            bot_status = multi_client_bot.get_status(skip_discovery=True)
                        except Exception:
                            bot_status = {}
                    self.after(0, lambda bs=bot_status: self._refresh_fleet_ui(status_data=bs))
            except Exception:
                pass

            loop_idx += 1
            time.sleep(3.0)

    def set_status(self, is_online, text):
        if is_online:
            self.status_dot.configure(text_color="#10B981")
            self.status_text.configure(text=text, text_color="#F4F4F5")
            self.fps_badge.configure(text_color="#10B981", text="180 FPS: Locked")
        else:
            self.status_dot.configure(text_color="#EF4444")
            self.status_text.configure(text=text, text_color="#A1A1AA")
            self.fps_badge.configure(text_color="#EF4444", text="Offline")

    def apply_environment(self, env):
        if not env:
            return
        self.env = env
        server_id = env.get("serverId", 702)
        fight_server_id = env.get("fightServerId", 700)
        al_tag = env.get("allianceTag", "WARG")
        al_name = env.get("allianceName", "WARGODS")
        al_members = env.get("allianceMembers", 96)
        bracket_id = env.get("bracketId", 16)
        player_name = env.get("playerName", "Heinzy")

        # Update Metric Pills
        self.val_state.configure(text=f"State #{server_id}")
        self.val_duel.configure(text=f"{server_id} vs {fight_server_id}")
        self.val_alliance.configure(text=f"[{al_tag}] {al_name or ''} ({al_members} Mbrs)".strip())
        self.val_bracket.configure(text=f"Bracket #{bracket_id} (16 States)")

        # Update Dynamic Buttons
        if hasattr(self, 'btn_export_roster'):
            if al_tag:
                self.btn_export_roster.configure(text=f"Export [{al_tag}] Alliance Roster (Excel)")
            else:
                self.btn_export_roster.configure(text="Export Alliance Roster (Excel)")

        if hasattr(self, 'btn_export_vs'):
            if fight_server_id:
                self.btn_export_vs.configure(text=f"Export VS Duel: #{server_id} vs #{fight_server_id} (Excel)")
            else:
                self.btn_export_vs.configure(text="Export VS Duel Rankings (Excel)")

        if hasattr(self, 'btn_active_mig'):
            self.btn_active_mig.configure(text=f"Open State {server_id} Migration Excel")

        # Keep bracket combo synced
        if hasattr(self, 'combo_bracket'):
            current_pick = self.combo_bracket.get()
            if not current_pick or current_pick == "State 694":
                self.combo_bracket.set(f"State {server_id}")

    # Action Handlers: Game Tab
    def on_apply_engine(self):
        self.log("Applying 180 FPS hardware acceleration & preloader...")
        def worker():
            script = self.find_script("apply widescreen smooth map.py")
            try:
                args = [PYTHON_CLI_EXE, script] + self._pid_args()
                res = self._subproc_run(args, timeout=15, env=self._subprocess_env())
                out = res.stdout.strip() or res.stderr.strip()
                self.after(0, lambda o=out: self.log(f"Engine: {o}"))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Engine Exception: {e}"))
        self.run_worker(worker)

    def on_flush_ram(self):
        self.log("Flushing RAM and collecting garbage...")
        def worker():
            script = self.find_script("flush game memory.py")
            if not os.path.exists(script):
                script = self.find_script("manual_instant_gc.py")
            try:
                args = [PYTHON_CLI_EXE, script] + self._pid_args()
                res = self._subproc_run(args, timeout=15, env=self._subprocess_env())
                out = res.stdout.strip() or res.stderr.strip()
                self.after(0, lambda o=out: self.log(f"RAM Flush: {o}"))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"RAM Flush Exception: {e}"))
        self.run_worker(worker)

    def on_trigger_heli(self):
        self.log("Triggering silent Heli Help All...")
        def worker():
            script = self.find_script("trigger helicopter help.py")
            if not os.path.exists(script):
                script = self.find_script("trigger_heli_help.py")
            try:
                args = [PYTHON_CLI_EXE, script] + self._pid_args()
                res = self._subproc_run(args, timeout=15, env=self._subprocess_env())
                out = res.stdout.strip() or res.stderr.strip()
                self.after(0, lambda o=out: self.log(f"Heli Help: {o}"))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Heli Help Exception: {e}"))
        self.run_worker(worker)

    def open_event_rules_modal(self):
        """Open configuration dialog for Trucks (per-slot tier + formation), Furylord 03:00, Bounties, and Mining Event."""
        if multi_client_bot is None:
            self.log("Multi-client bot module unavailable.")
            return
        cfg = multi_client_bot.load_config()
        base = cfg.get("client_defaults", {}).get("main", {})
        tr = base.get("trucks") or {}
        fl = base.get("furylord") or {}
        bo = base.get("bounties") or {}
        bs = base.get("bounty_steal") or {}
        mn = base.get("mining_event") or {}
        vp = base.get("vip_store_rewards") or {}
        ae = base.get("area_exploration") or {}
        hb = base.get("hero_battlefield") or {}
        ar = base.get("arena") or {}
        ws = base.get("war_safety") or {}
        hh = base.get("hospital_heal") or {}
        ad = base.get("alliance_daily") or {}
        rq = base.get("research_queue") or {}
        rd = base.get("radar_events") or {}
        fr = base.get("free_recruits") or {}
        gu = base.get("garage_upgrades") or {}
        ab = base.get("alliance_boss_mine") or {}

        win = ctk.CTkToplevel(self)
        win.title("Bot Rules: VIP, Explore, Battlefield, Arena & Events")
        win.geometry("580x690")
        win.configure(fg_color="#09090B")
        win.transient(self)
        win.grab_set()

        q_labels = {5: "Gold (5)", 4: "Purple (4)", 3: "Blue (3)", 2: "Green (2)", 1: "Any (1)"}
        q_values = {v: k for k, v in q_labels.items()}
        f_labels = {1: "F1", 2: "F2", 3: "F3", 4: "F4", 0: "Auto"}
        f_values = {v: k for k, v in f_labels.items()}

        body = ctk.CTkScrollableFrame(win, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=10)

        # Trucks card
        c_tr = self.create_card(body, "TRUCKS (4 SLOTS: CHOOSE TIER + FORMATION)", expand=False)
        slots_raw = tr.get("slots") or []
        slot_vars = []
        for idx in range(4):
            s = slots_raw[idx] if idx < len(slots_raw) and isinstance(slots_raw[idx], dict) else {}
            q_init = q_labels.get(int(s.get("quality", 5)), "Gold (5)")
            f_init = f_labels.get(int(s.get("formation", idx + 1)), f"F{idx + 1}")
            row = ctk.CTkFrame(c_tr, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=f"Truck {idx + 1}:", width=70, anchor="w").pack(side="left")
            qv = ctk.StringVar(value=q_init)
            fv = ctk.StringVar(value=f_init)
            ctk.CTkOptionMenu(row, values=list(q_labels.values()), variable=qv, width=130, height=26).pack(side="left", padx=6)
            ctk.CTkOptionMenu(row, values=list(f_labels.values()), variable=fv, width=90, height=26).pack(side="left", padx=6)
            slot_vars.append((qv, fv))

        tr_row2 = ctk.CTkFrame(c_tr, fg_color="transparent")
        tr_row2.pack(fill="x", padx=10, pady=(4, 6))
        ctk.CTkLabel(tr_row2, text="Attack Margin Below F1 (M):").pack(side="left")
        margin_entry = ctk.CTkEntry(tr_row2, width=54, height=24)
        margin_entry.insert(0, str(max(0, int(int(tr.get("attack_power_margin_below_f1", 20_000_000)) // 1_000_000))))
        margin_entry.pack(side="left", padx=(4, 12))
        tr_cross_var = ctk.BooleanVar(value=bool(tr.get("attack_cross_state_only", True)))
        ctk.CTkCheckBox(tr_row2, text="Cross-State Attack Only", variable=tr_cross_var, height=22).pack(side="left", padx=4)
        tr_dia_var = ctk.BooleanVar(value=bool(tr.get("reroll_with_diamonds", False)))
        ctk.CTkCheckBox(c_tr, text="Use Diamonds on Truck Reroll (otherwise Contracts/Free only)", variable=tr_dia_var, height=22).pack(anchor="w", padx=10, pady=(0, 6))

        # Furylord card
        c_fl = self.create_card(body, "FURYLORD (EXACT 03:00 F1 x4 SCHEDULE)", expand=False)
        fl_row = ctk.CTkFrame(c_fl, fg_color="transparent")
        fl_row.pack(fill="x", padx=10, pady=(4, 8))
        ctk.CTkLabel(fl_row, text="Hour:").pack(side="left")
        fl_hour_e = ctk.CTkEntry(fl_row, width=42, height=24)
        fl_hour_e.insert(0, str(int(fl.get("exact_hour", 3))))
        fl_hour_e.pack(side="left", padx=(4, 10))
        ctk.CTkLabel(fl_row, text="Min:").pack(side="left")
        fl_min_e = ctk.CTkEntry(fl_row, width=42, height=24)
        fl_min_e.insert(0, str(int(fl.get("exact_minute", 0))))
        fl_min_e.pack(side="left", padx=(4, 10))
        ctk.CTkLabel(fl_row, text="Max/Day:").pack(side="left")
        fl_cnt_e = ctk.CTkEntry(fl_row, width=42, height=24)
        fl_cnt_e.insert(0, str(int(fl.get("max_attacks", 4))))
        fl_cnt_e.pack(side="left", padx=(4, 10))
        fl_form_var = ctk.StringVar(value=f_labels.get(int(fl.get("formation_index", 1)), "F1"))
        ctk.CTkOptionMenu(fl_row, values=["F1", "F2", "F3", "F4"], variable=fl_form_var, width=76, height=24).pack(side="left", padx=4)

        # Bounties & Steal card
        c_bo = self.create_card(body, "BOUNTIES & CROSS-STATE STEAL", expand=False)
        bo_dia_var = ctk.BooleanVar(value=bool(bo.get("use_diamonds", False)))
        ctk.CTkCheckBox(c_bo, text="Bounties: Use Diamonds when Free/Tickets exhausted", variable=bo_dia_var, height=22).pack(anchor="w", padx=10, pady=2)
        bs_row = ctk.CTkFrame(c_bo, fg_color="transparent")
        bs_row.pack(fill="x", padx=10, pady=(2, 6))
        ctk.CTkLabel(bs_row, text="Steal Min Lv:").pack(side="left")
        bs_lv_e = ctk.CTkEntry(bs_row, width=44, height=24)
        bs_lv_e.insert(0, str(int(bs.get("min_level", 5))))
        bs_lv_e.pack(side="left", padx=(4, 12))
        bs_cross_var = ctk.BooleanVar(value=bool(bs.get("cross_state_only", True)))
        ctk.CTkCheckBox(bs_row, text="Cross-State Steal Only (Golden)", variable=bs_cross_var, height=22).pack(side="left")

        # Mining Event card
        c_mn = self.create_card(body, "MINING EVENT (MON / TUE EVENT CALENDAR)", expand=False)
        mn_row = ctk.CTkFrame(c_mn, fg_color="transparent")
        mn_row.pack(fill="x", padx=10, pady=(2, 6))
        ctk.CTkLabel(mn_row, text="Mine Type:").pack(side="left")
        mn_type_var = ctk.StringVar(value="XP / Crystal (2)" if int(mn.get("mine_type", 2)) == 2 else "Gold (1)")
        ctk.CTkOptionMenu(mn_row, values=["XP / Crystal (2)", "Gold (1)"], variable=mn_type_var, width=140, height=24).pack(side="left", padx=(4, 10))
        ctk.CTkLabel(mn_row, text="Level:").pack(side="left")
        mn_lv_e = ctk.CTkEntry(mn_row, width=40, height=24)
        mn_lv_e.insert(0, str(int(mn.get("mine_level", 7))))
        mn_lv_e.pack(side="left", padx=(4, 10))
        mn_skip_var = ctk.BooleanVar(value=bool(mn.get("skip_occupied_players", True)))
        ctk.CTkCheckBox(c_mn, text="Never attack mines occupied by players", variable=mn_skip_var, height=22).pack(anchor="w", padx=10, pady=(0, 6))

        # VIP & Store 2nd Tab Rewards card
        c_vp = self.create_card(body, "VIP & STORE 2ND TAB DAILY REWARDS", expand=False)
        vp_pts_var = ctk.BooleanVar(value=bool(vp.get("claim_vip_points", True)))
        vp_daily_var = ctk.BooleanVar(value=bool(vp.get("claim_vip_daily_freebie", True)))
        vp_store_var = ctk.BooleanVar(value=bool(vp.get("claim_store_vip_tab_free", True)))
        vp_week_var = ctk.BooleanVar(value=bool(vp.get("claim_weekly_gift_freebie", True)))
        ctk.CTkCheckBox(c_vp, text="Claim VIP Daily Points chest (red dot)", variable=vp_pts_var, height=22).pack(anchor="w", padx=10, pady=2)
        ctk.CTkCheckBox(c_vp, text="Claim VIP Daily Freebies chest", variable=vp_daily_var, height=22).pack(anchor="w", padx=10, pady=2)
        ctk.CTkCheckBox(c_vp, text="Claim Store 2nd Tab (VIP Shop) free daily reward", variable=vp_store_var, height=22).pack(anchor="w", padx=10, pady=2)
        ctk.CTkCheckBox(c_vp, text="Claim free daily/weekly Gift Pack item", variable=vp_week_var, height=22).pack(anchor="w", padx=10, pady=(2, 6))

        # Area Exploration card
        c_ae = self.create_card(body, "AREA EXPLORATION (HQ -> EXPLORE SOLO STAGES)", expand=False)
        ae_row = ctk.CTkFrame(c_ae, fg_color="transparent")
        ae_row.pack(fill="x", padx=10, pady=(2, 4))
        ctk.CTkLabel(ae_row, text="Max Stages/Cycle:").pack(side="left")
        ae_max_e = ctk.CTkEntry(ae_row, width=44, height=24)
        ae_max_e.insert(0, str(int(ae.get("max_battles_per_cycle", 5))))
        ae_max_e.pack(side="left", padx=(4, 10))
        ae_hang_var = ctk.BooleanVar(value=bool(ae.get("claim_hangup_rewards", True)))
        ae_jump_var = ctk.BooleanVar(value=bool(ae.get("auto_jump", True)))
        ae_battle_var = ctk.BooleanVar(value=bool(ae.get("auto_battle", True)))
        ae_stop_var = ctk.BooleanVar(value=bool(ae.get("stop_on_fail", True)))
        ae_cache_var = ctk.BooleanVar(value=bool(ae.get("skip_already_failed_same_power", True)))
        ctk.CTkCheckBox(ae_row, text="Claim Idle Chest", variable=ae_hang_var, height=22).pack(side="left", padx=4)
        ctk.CTkCheckBox(ae_row, text="Auto Batch-Jump", variable=ae_jump_var, height=22).pack(side="left", padx=4)
        ctk.CTkCheckBox(c_ae, text="Run solo Explore battles until defeat detected, then move on", variable=ae_battle_var, height=22).pack(anchor="w", padx=10, pady=2)
        ae_row2 = ctk.CTkFrame(c_ae, fg_color="transparent")
        ae_row2.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkCheckBox(ae_row2, text="Stop cycle loop on first defeat", variable=ae_stop_var, height=22).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(ae_row2, text="Skip failed stage until power rises", variable=ae_cache_var, height=22).pack(side="left")

        # Hero Battlefield card
        c_hb = self.create_card(body, "CAMPERVAN HERO BATTLEFIELD (3 FACTIONS -> GLORY POINTS)", expand=False)
        hb_row = ctk.CTkFrame(c_hb, fg_color="transparent")
        hb_row.pack(fill="x", padx=10, pady=(2, 4))
        ctk.CTkLabel(hb_row, text="Max Stages/Faction:").pack(side="left")
        hb_max_e = ctk.CTkEntry(hb_row, width=44, height=24)
        hb_max_e.insert(0, str(int(hb.get("max_battles_per_faction", 5))))
        hb_max_e.pack(side="left", padx=(4, 10))
        hb_prefill_var = ctk.BooleanVar(value=bool(hb.get("auto_prefill_strongest_faction", True)))
        hb_stop_var = ctk.BooleanVar(value=bool(hb.get("stop_on_fail", True)))
        hb_skip_var = ctk.BooleanVar(value=bool(hb.get("skip_if_failed_this_period", True)))
        ctk.CTkCheckBox(hb_row, text="Pre-fill strongest heroes of matching faction only", variable=hb_prefill_var, height=22).pack(side="left")
        hb_row2 = ctk.CTkFrame(c_hb, fg_color="transparent")
        hb_row2.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkCheckBox(hb_row2, text="Stop faction on defeat", variable=hb_stop_var, height=22).pack(side="left", padx=(0, 12))
        ctk.CTkCheckBox(hb_row2, text="Skip factions already failed this period", variable=hb_skip_var, height=22).pack(side="left")

        # Arena card
        c_ar = self.create_card(body, "ARENA (1v1 / 3v3 AUTO, FACTION TOP-5, >70% WIN ODDS)", expand=False)
        ar_row = ctk.CTkFrame(c_ar, fg_color="transparent")
        ar_row.pack(fill="x", padx=10, pady=(2, 4))
        ctk.CTkLabel(ar_row, text="Battles/Cycle:").pack(side="left")
        ar_max_e = ctk.CTkEntry(ar_row, width=40, height=24)
        ar_max_e.insert(0, str(int(ar.get("max_battles_per_cycle", 5))))
        ar_max_e.pack(side="left", padx=(4, 10))
        ctk.CTkLabel(ar_row, text="Min Win Odds (%):").pack(side="left")
        ar_odds_e = ctk.CTkEntry(ar_row, width=44, height=24)
        ar_odds_e.insert(0, str(int(ar.get("min_win_odds_pct", 70))))
        ar_odds_e.pack(side="left", padx=(4, 10))
        ctk.CTkLabel(ar_row, text="Min Ratio:").pack(side="left")
        ar_ratio_e = ctk.CTkEntry(ar_row, width=44, height=24)
        ar_ratio_e.insert(0, str(float(ar.get("min_power_advantage_ratio", 1.0))))
        ar_ratio_e.pack(side="left", padx=(4, 8))
        ar_ref_var = ctk.BooleanVar(value=bool(ar.get("refresh_opponents", True)))
        ar_freeref_var = ctk.BooleanVar(value=bool(ar.get("auto_free_refresh", True)))
        ar_pure_var = ctk.BooleanVar(value=bool(ar.get("pure_faction_teams", True)))
        ar_weak_var = ctk.BooleanVar(value=bool(ar.get("pick_weakest", True)))
        ar_row2 = ctk.CTkFrame(c_ar, fg_color="transparent")
        ar_row2.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkCheckBox(ar_row2, text="Pure faction top-5 teams", variable=ar_pure_var, height=22).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(ar_row2, text="Free refresh if < odds", variable=ar_freeref_var, height=22).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(ar_row2, text="Pick weakest", variable=ar_weak_var, height=22).pack(side="left")

        # Hospital Auto-Heal & Alliance Daily
        c_hh = self.create_card(body, "HOSPITAL AUTO-HEAL & ALLIANCE DAILY", expand=False)
        hh_row = ctk.CTkFrame(c_hh, fg_color="transparent")
        hh_row.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(hh_row, text="Heal Batch (min):").pack(side="left")
        hh_batch_e = ctk.CTkEntry(hh_row, width=44, height=24)
        hh_batch_e.insert(0, str(int(hh.get("batch_minutes", 30))))
        hh_batch_e.pack(side="left", padx=(4, 12))
        hh_help_var = ctk.BooleanVar(value=bool(hh.get("call_alliance_help", True)))
        ctk.CTkCheckBox(hh_row, text="Auto Alliance Help", variable=hh_help_var, height=22).pack(side="left", padx=(0, 12))
        ad_tech_var = ctk.BooleanVar(value=bool(ad.get("donate_tech", True)))
        ctk.CTkCheckBox(hh_row, text="Donate Tech", variable=ad_tech_var, height=22).pack(side="left")

        ad_row2 = ctk.CTkFrame(c_hh, fg_color="transparent")
        ad_row2.pack(fill="x", padx=10, pady=(0, 6))
        ad_gifts_var = ctk.BooleanVar(value=bool(ad.get("claim_gifts", True)))
        ad_red_var = ctk.BooleanVar(value=bool(ad.get("claim_red_packets", True)))
        ad_tasks_var = ctk.BooleanVar(value=bool(ad.get("claim_tasks", True)))
        ctk.CTkCheckBox(ad_row2, text="Claim Alliance Gifts", variable=ad_gifts_var, height=22).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(ad_row2, text="Claim Red Packets", variable=ad_red_var, height=22).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(ad_row2, text="Claim Alliance Tasks", variable=ad_tasks_var, height=22).pack(side="left")

        # Research, Radar & Free Recruits / Safe Chests
        c_rq = self.create_card(body, "RESEARCH, RADAR & FREE RECRUITS / SAFE CHESTS", expand=False)
        rq_row = ctk.CTkFrame(c_rq, fg_color="transparent")
        rq_row.pack(fill="x", padx=10, pady=4)
        rq_rec_var = ctk.BooleanVar(value=bool(rq.get("prefer_recommended", True)))
        rq_free_var = ctk.BooleanVar(value=bool(rq.get("use_free_speed", True)))
        rd_disp_var = ctk.BooleanVar(value=bool(rd.get("auto_dispatch", True)))
        ctk.CTkCheckBox(rq_row, text="Research Recommended", variable=rq_rec_var, height=22).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(rq_row, text="Free Speedup", variable=rq_free_var, height=22).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(rq_row, text="Radar Dispatch", variable=rd_disp_var, height=22).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(rq_row, text="Max:").pack(side="left")
        rd_max_e = ctk.CTkEntry(rq_row, width=36, height=24)
        rd_max_e.insert(0, str(int(rd.get("max_dispatches_per_cycle", 3))))
        rd_max_e.pack(side="left", padx=(4, 0))

        fr_row = ctk.CTkFrame(c_rq, fg_color="transparent")
        fr_row.pack(fill="x", padx=10, pady=(0, 6))
        fr_hero_var = ctk.BooleanVar(value=bool(fr.get("claim_hero_recruits", True)))
        fr_chest_var = ctk.BooleanVar(value=bool(fr.get("open_safe_chests", True)))
        ctk.CTkCheckBox(fr_row, text="Free Hero Recruits", variable=fr_hero_var, height=22).pack(side="left", padx=(0, 12))
        ctk.CTkCheckBox(fr_row, text="Open Non-Choice Safe Bag Chests", variable=fr_chest_var, height=22).pack(side="left")

        # War Safety, Monday Garage & Alliance Boss / Mine
        c_ws = self.create_card(body, "WAR SAFETY, MONDAY GARAGE & BEAR / ALLIANCE MINE", expand=False)
        ws_row = ctk.CTkFrame(c_ws, fg_color="transparent")
        ws_row.pack(fill="x", padx=10, pady=4)
        ws_shield_var = ctk.BooleanVar(value=bool(ws.get("auto_shield_on_attack", True)))
        ws_fever_var = ctk.BooleanVar(value=bool(ws.get("respect_war_fever", True)))
        ws_recall_var = ctk.BooleanVar(value=bool(ws.get("recall_gatherers_on_attack", True)))
        ctk.CTkCheckBox(ws_row, text="Auto-Shield Under Attack", variable=ws_shield_var, height=22).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(ws_row, text="Respect War Fever", variable=ws_fever_var, height=22).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(ws_row, text="Recall Gatherers", variable=ws_recall_var, height=22).pack(side="left")

        gu_row = ctk.CTkFrame(c_ws, fg_color="transparent")
        gu_row.pack(fill="x", padx=10, pady=2)
        gu_mon_var = ctk.BooleanVar(value=bool(gu.get("only_monday", True)))
        gu_free_var = ctk.BooleanVar(value=bool(gu.get("use_refit_free_only", True)))
        ctk.CTkCheckBox(gu_row, text="Garage Monday-Only", variable=gu_mon_var, height=22).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(gu_row, text="Free Refit Only", variable=gu_free_var, height=22).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(gu_row, text="Refit Steps:").pack(side="left")
        gu_steps_e = ctk.CTkEntry(gu_row, width=36, height=24)
        gu_steps_e.insert(0, str(int(gu.get("max_refit_steps_per_cycle", 5))))
        gu_steps_e.pack(side="left", padx=(4, 0))

        ab_row = ctk.CTkFrame(c_ws, fg_color="transparent")
        ab_row.pack(fill="x", padx=10, pady=(2, 6))
        ab_rew_var = ctk.BooleanVar(value=bool(ab.get("bear_claim_rewards", True)))
        ab_join_var = ctk.BooleanVar(value=bool(ab.get("bear_join_or_rally", True)))
        ab_mine_var = ctk.BooleanVar(value=bool(ab.get("alliance_mine_dispatch", True)))
        ctk.CTkCheckBox(ab_row, text="Bear Rewards", variable=ab_rew_var, height=22).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(ab_row, text="Bear Join/Rally", variable=ab_join_var, height=22).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(ab_row, text="Alliance Mine Gather", variable=ab_mine_var, height=22).pack(side="left")

        def _save_modal():
            cur = multi_client_bot.load_config()
            defs = cur.setdefault("client_defaults", {})
            new_slots = [{"quality": q_values.get(qv.get(), 5), "formation": f_values.get(fv.get(), i + 1)} for i, (qv, fv) in enumerate(slot_vars)]
            try:
                margin_m = max(0, int(margin_entry.get().strip())) * 1_000_000
            except Exception:
                margin_m = 20_000_000
            try:
                fh = max(0, min(23, int(fl_hour_e.get().strip())))
            except Exception:
                fh = 3
            try:
                fm = max(0, min(59, int(fl_min_e.get().strip())))
            except Exception:
                fm = 0
            try:
                fc = max(1, int(fl_cnt_e.get().strip()))
            except Exception:
                fc = 4
            try:
                bs_lv = max(1, int(bs_lv_e.get().strip()))
            except Exception:
                bs_lv = 5
            try:
                mn_lv = max(1, int(mn_lv_e.get().strip()))
            except Exception:
                mn_lv = 7
            mn_t = 2 if "2" in mn_type_var.get() else 1
            try:
                ae_max = max(1, min(20, int(ae_max_e.get().strip())))
            except Exception:
                ae_max = 5
            try:
                hb_max = max(1, min(15, int(hb_max_e.get().strip())))
            except Exception:
                hb_max = 5
            try:
                ar_max = max(1, min(10, int(ar_max_e.get().strip())))
            except Exception:
                ar_max = 5
            try:
                ar_odds = max(50, min(99, int(ar_odds_e.get().strip())))
            except Exception:
                ar_odds = 70
            try:
                ar_ratio = max(0.5, float(ar_ratio_e.get().strip()))
            except Exception:
                ar_ratio = 1.0
            try:
                hh_batch = max(5, min(240, int(hh_batch_e.get().strip())))
            except Exception:
                hh_batch = 30
            try:
                rd_max = max(1, min(20, int(rd_max_e.get().strip())))
            except Exception:
                rd_max = 3
            try:
                gu_steps = max(1, min(20, int(gu_steps_e.get().strip())))
            except Exception:
                gu_steps = 5

            for role_key in ("main", "farm"):
                rc = defs.setdefault(role_key, {})
                rc.setdefault("trucks", {}).update({
                    "slots": new_slots,
                    "reroll_with_diamonds": bool(tr_dia_var.get()),
                    "attack_cross_state_only": bool(tr_cross_var.get()),
                    "attack_power_margin_below_f1": margin_m,
                })
                rc.setdefault("furylord", {}).update({
                    "exact_hour": fh,
                    "exact_minute": fm,
                    "max_attacks": fc,
                    "formation_index": f_values.get(fl_form_var.get(), 1),
                })
                rc.setdefault("bounties", {})["use_diamonds"] = bool(bo_dia_var.get())
                rc.setdefault("bounty_steal", {}).update({
                    "min_level": bs_lv,
                    "cross_state_only": bool(bs_cross_var.get()),
                })
                rc.setdefault("mining_event", {}).update({
                    "mine_type": mn_t,
                    "mine_reward": "xp" if mn_t == 2 else "gold",
                    "mine_level": mn_lv,
                    "skip_occupied_players": bool(mn_skip_var.get()),
                })
                rc.setdefault("vip_store_rewards", {}).update({
                    "claim_vip_points": bool(vp_pts_var.get()),
                    "claim_vip_daily_freebie": bool(vp_daily_var.get()),
                    "claim_store_vip_tab_free": bool(vp_store_var.get()),
                    "claim_weekly_gift_freebie": bool(vp_week_var.get()),
                })
                rc.setdefault("area_exploration", {}).update({
                    "claim_hangup_rewards": bool(ae_hang_var.get()),
                    "auto_jump": bool(ae_jump_var.get()),
                    "auto_battle": bool(ae_battle_var.get()),
                    "max_battles_per_cycle": ae_max,
                    "stop_on_fail": bool(ae_stop_var.get()),
                    "skip_already_failed_same_power": bool(ae_cache_var.get()),
                })
                rc.setdefault("hero_battlefield", {}).update({
                    "auto_prefill_strongest_faction": bool(hb_prefill_var.get()),
                    "max_battles_per_faction": hb_max,
                    "stop_on_fail": bool(hb_stop_var.get()),
                    "skip_if_failed_this_period": bool(hb_skip_var.get()),
                })
                rc.setdefault("arena", {}).update({
                    "max_battles_per_cycle": ar_max,
                    "refresh_opponents": bool(ar_ref_var.get()),
                    "auto_free_refresh": bool(ar_freeref_var.get()),
                    "pure_faction_teams": bool(ar_pure_var.get()),
                    "pick_weakest": bool(ar_weak_var.get()),
                    "min_win_odds_pct": ar_odds,
                    "min_power_advantage_ratio": ar_ratio,
                })
                rc.setdefault("war_safety", {}).update({
                    "auto_shield_on_attack": bool(ws_shield_var.get()),
                    "respect_war_fever": bool(ws_fever_var.get()),
                    "recall_gatherers_on_attack": bool(ws_recall_var.get()),
                })
                rc.setdefault("hospital_heal", {}).update({
                    "batch_minutes": hh_batch,
                    "call_alliance_help": bool(hh_help_var.get()),
                })
                rc.setdefault("alliance_daily", {}).update({
                    "donate_tech": bool(ad_tech_var.get()),
                    "claim_gifts": bool(ad_gifts_var.get()),
                    "claim_red_packets": bool(ad_red_var.get()),
                    "claim_tasks": bool(ad_tasks_var.get()),
                })
                rc.setdefault("research_queue", {}).update({
                    "prefer_recommended": bool(rq_rec_var.get()),
                    "use_free_speed": bool(rq_free_var.get()),
                })
                rc.setdefault("radar_events", {}).update({
                    "auto_dispatch": bool(rd_disp_var.get()),
                    "max_dispatches_per_cycle": rd_max,
                })
                rc.setdefault("free_recruits", {}).update({
                    "claim_hero_recruits": bool(fr_hero_var.get()),
                    "open_safe_chests": bool(fr_chest_var.get()),
                })
                rc.setdefault("garage_upgrades", {}).update({
                    "only_monday": bool(gu_mon_var.get()),
                    "use_refit_free_only": bool(gu_free_var.get()),
                    "max_refit_steps_per_cycle": gu_steps,
                })
                rc.setdefault("alliance_boss_mine", {}).update({
                    "bear_claim_rewards": bool(ab_rew_var.get()),
                    "bear_join_or_rally": bool(ab_join_var.get()),
                    "alliance_mine_dispatch": bool(ab_mine_var.get()),
                })
            multi_client_bot.save_config(cur)
            self.log(f"Saved Event & Bot Rules (Heal {hh_batch}m, Radar max {rd_max}, Furylord {fh:02d}:{fm:02d} x{fc}, Arena x{ar_max} >={ar_odds}%, Mine Lv{mn_lv}).")
            win.destroy()

        btn_bar = ctk.CTkFrame(win, fg_color="transparent")
        btn_bar.pack(fill="x", padx=14, pady=(0, 10))
        ctk.CTkButton(btn_bar, text="Save & Close", fg_color="#059669", hover_color="#047857", height=30, command=_save_modal).pack(side="right", padx=4)
        ctk.CTkButton(btn_bar, text="Cancel", fg_color="#3F3F46", hover_color="#27272A", height=30, command=win.destroy).pack(side="right", padx=4)

    def _load_bot_config_into_ui(self):
        if multi_client_bot is None:
            return
        try:
            cfg = multi_client_bot.load_config()
            enabled_map = cfg.get("enabled_tasks", {})
            farm_tasks = cfg.get("client_defaults", {}).get("farm", {}).get("tasks", {})
            for key, var in self.task_vars.items():
                var.set(bool(enabled_map.get(key, farm_tasks.get(key, True))))
            if self.auto_launch_var is not None:
                self.auto_launch_var.set(bool(cfg.get("auto_launch_stopped_clients", False)))
            if self.main_enabled_var is not None:
                self.main_enabled_var.set(bool(cfg.get("client_defaults", {}).get("main", {}).get("enabled", True)))
            self.entry_cycle_sec.delete(0, "end")
            self.entry_cycle_sec.insert(0, str(int(cfg.get("cycle_interval_seconds", 180))))
            self.entry_task_min.delete(0, "end")
            self.entry_task_min.insert(0, str(int(cfg.get("schedule", {}).get("interval_minutes", 15))))
            mode_val = str(cfg.get("auto_launch_mode", "eco")).capitalize()
            if mode_val in ("Eco", "Windowed", "Hidden"):
                self.combo_launch_mode.set(mode_val)
        except Exception as e:
            self.log(f"Bot config load notice: {e}")

    def on_save_bot_config(self, quiet=False):
        if multi_client_bot is None:
            return
        try:
            cfg = multi_client_bot.load_config()
            cfg.setdefault("enabled_tasks", {})
            defaults = cfg.setdefault("client_defaults", {})
            farm_prev = dict(defaults.get("farm", {}).get("tasks", {})) if isinstance(defaults.get("farm"), dict) else {}
            for key, var in self.task_vars.items():
                val = bool(var.get())
                cfg["enabled_tasks"][key] = val
                if isinstance(defaults.get("farm"), dict):
                    defaults["farm"].setdefault("tasks", {})[key] = val
                if isinstance(defaults.get("main"), dict):
                    # Preserve Main-only disabled overrides unless the user explicitly toggled this key in the UI
                    if (not val) or (val != bool(farm_prev.get(key, True))):
                        defaults["main"].setdefault("tasks", {})[key] = val
            if self.auto_launch_var is not None:
                cfg["auto_launch_stopped_clients"] = bool(self.auto_launch_var.get())
            if self.main_enabled_var is not None:
                defaults.setdefault("main", {})["enabled"] = bool(self.main_enabled_var.get())
            try:
                cfg["cycle_interval_seconds"] = max(30, int(self.entry_cycle_sec.get().strip()))
            except ValueError:
                pass
            try:
                cfg.setdefault("schedule", {})["interval_minutes"] = max(1, int(self.entry_task_min.get().strip()))
            except ValueError:
                pass
            cfg["auto_launch_mode"] = self.combo_launch_mode.get().strip().lower()
            multi_client_bot.save_config(cfg)
            if not quiet:
                self.log("Saved multi-client bot configuration.")
        except Exception as e:
            self.log(f"Save Bot Config Error: {e}")

    def _refresh_fleet_ui(self, live_snapshots=None, status_data=None):
        if status_data is None:
            try:
                status_data = multi_client_bot.get_status(skip_discovery=True) if multi_client_bot is not None else {}
            except Exception:
                status_data = {}

        last_by_label = {}
        last_cycle = status_data.get("last_cycle") or {}
        for c in last_cycle.get("clients", []):
            last_by_label[str(c.get("label") or "")] = c

        running_by_label = {str(r.get("label") or ""): r for r in self.running_clients}
        snap_by_label = live_snapshots or {}

        discovered = list(self.discovered_clients)
        if not discovered:
            discovered = list(self.running_clients)

        lines = []
        summary_parts = []
        for client in discovered:
            lbl = str(client.get("label") or client.get("unity_profile") or "Client")
            role = str(client.get("role") or "farm")
            run_info = running_by_label.get(lbl)
            pid_txt = f"PID {run_info['pid']}" if run_info else "Stopped"
            summary_parts.append(f"{lbl}: {pid_txt}")
            snap = snap_by_label.get(lbl) or (last_by_label.get(lbl, {}).get("snapshot") or {})
            if snap and snap.get("ok"):
                hq = snap.get("hqLv", "?")
                srv = snap.get("serverId", "?")
                pwr = f"{int(snap.get('power', 0)) / 1_000_000:.1f}M"
                stam = snap.get("stamina", "?")
                sq = f"{snap.get('freeFormations', '?')}/{snap.get('unlockFormations', '?')}"
                shd = "Shield" if snap.get("shielded") else "NoShield"
                lines.append(f"{lbl:<7} [{role:<4}] {pid_txt:<10} | #{srv} HQ{hq} | {pwr} | Stam {stam} | Squads {sq} | {shd}")
            else:
                exe = client.get("exe_name") or ""
                lines.append(f"{lbl:<7} [{role:<4}] {pid_txt:<10} | {exe} (run scan or cycle for live stats)")

        self._last_fleet_lines = lines
        summary_txt = "Fleet: " + (" | ".join(summary_parts) if summary_parts else "No clients discovered")
        if hasattr(self, "lbl_fleet_summary"):
            self.lbl_fleet_summary.configure(text=summary_txt)

        daemon_txt = "Running" if status_data.get("daemon_running") else "Stopped"
        sched_root = status_data.get("schedule") or {}
        primary = sched_root.get("primary") or {}
        if primary.get("exists"):
            next_run = "Scheduled"
            for line in str(primary.get("raw") or "").splitlines():
                if line.startswith("Next Run Time:"):
                    next_run = line.split(":", 1)[1].strip()
                    break
            sched_txt = f"Installed ({next_run})"
        else:
            sched_txt = "Not Registered"
        fin_txt = last_cycle.get("finished_at", "Never")
        if isinstance(fin_txt, str) and len(fin_txt) > 19:
            fin_txt = fin_txt[:19].replace("T", " ")
        self.lbl_bot_status.configure(text=f"Daemon: {daemon_txt} | Win Task: {sched_txt} | Last Cycle: {fin_txt}")

    def _resolve_cycle_target_arg(self):
        scope = self.combo_cycle_scope.get()
        if scope == "Selected Client":
            return self.selected_client_label or (str(self.target_pid) if self.target_pid else "all")
        if scope == "Main Only":
            return "Main"
        if scope == "Farms Only":
            return "farms"
        return "all"

    def on_scan_fleet(self):
        self.log("Scanning all configured and running Last Z clients...")
        def worker():
            try:
                if client_discovery is None:
                    self.after(0, lambda: self.log("client discovery.py not found."))
                    return
                disc = client_discovery.discover_clients(save_cache=True)
                self.discovered_clients = disc if isinstance(disc, list) else (disc.get("clients", []) if isinstance(disc, dict) else [])
                running = self._discover_running_clients(query_lua=True, force_pids=[int(c["pid"]) for c in self.running_clients])
                self.after(0, lambda r=running: self._update_target_dropdown_ui(r, None))
                self.running_clients = running
                live_snaps = {}
                if bot_actions is not None:
                    for proc in running:
                        snap = bot_actions.snapshot_client(client_discovery, int(proc["pid"]))
                        live_snaps[str(proc.get("label") or "")] = snap
                def _finish_scan():
                    self._refresh_fleet_ui(live_snapshots=live_snaps)
                    self.log(f"Fleet scan complete: {len(self.discovered_clients)} discovered, {len(running)} running.")
                    for fl in getattr(self, "_last_fleet_lines", []):
                        self.log(f"  {fl}")
                self.after(0, _finish_scan)
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Fleet Scan Error: {e}"))
        self.run_worker(worker)

    def on_sync_farm_builds(self):
        if not self._begin_action("sync_farm_builds"):
            self.log("Farm binary sync already in progress...")
            return
        self.log("Syncing client binaries across Farm installs...")
        def worker():
            try:
                res = self._run_tool("sync farm clients.py", ["sync"], timeout=45)
                out = res.stdout.strip() or res.stderr.strip() or f"exit={res.returncode}"
                summary = out
                if out.startswith("["):
                    try:
                        items = json.loads(out)
                        summary = " | ".join(
                            f"{it.get('label', '?')}: {it.get('message', 'OK' if it.get('ok') else 'Failed')}"
                            for it in items
                        )
                    except Exception:
                        pass
                self.after(0, lambda o=summary: self.log(f"Farm Sync: {o}"))
                self.after(300, self._refresh_fleet_ui)
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Farm Sync Error: {e}"))
            finally:
                self.after(0, lambda: self._end_action("sync_farm_builds"))
        self.run_worker(worker)

    def on_launch_all_farms(self):
        if not self._begin_action("launch_farms"):
            self.log("Farm launch already in progress...")
            return
        mode = self.combo_launch_mode.get().strip().lower()
        self.log(f"Launching farm clients in {mode} mode...")
        def worker():
            try:
                labels = []
                if client_discovery is not None:
                    try:
                        labels = [
                            c["label"]
                            for c in client_discovery.discover_clients(save_cache=False)
                            if c.get("role") != "main" and c.get("label")
                        ]
                    except Exception:
                        labels = []
                if not labels:
                    labels = ["Farm", "Third"]
                msgs = []
                for lbl in labels:
                    res = self._run_tool("sync farm clients.py", ["launch", lbl, mode, "--wait"], timeout=60)
                    msgs.append(f"{lbl}: {(res.stdout.strip() or res.stderr.strip())}")
                self.after(0, lambda m=" | ".join(msgs): self.log(f"Launch Farms: {m}"))
                self.after(1500, self.on_scan_fleet)
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Launch Farms Error: {e}"))
            finally:
                self.after(0, lambda: self._end_action("launch_farms"))
        self.run_worker(worker)

    def on_stop_all_farms(self):
        if not self._begin_action("stop_farms"):
            self.log("Farm stop already in progress...")
            return
        self.log("Stopping all secondary farm clients (keeping Main intact)...")
        def worker():
            try:
                res = self._run_tool("sync farm clients.py", ["stop", "farms"], timeout=20)
                out = res.stdout.strip() or res.stderr.strip() or f"exit={res.returncode}"
                self.after(0, lambda o=out: self.log(f"Stop Farms: {o}"))
                self.after(800, self._refresh_fleet_ui)
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Stop Farms Error: {e}"))
            finally:
                self.after(0, lambda: self._end_action("stop_farms"))
        self.run_worker(worker)

    def _open_output_file(self, path):
        if path and os.path.exists(path) and not os.environ.get("HEINZ_NO_STARTFILE"):
            os.startfile(path)

    def on_provision_farm_client(self):
        existing = getattr(self, "_provision_dialog", None)
        if existing is not None and existing.winfo_exists():
            existing.focus()
            return

        dlg = ctk.CTkToplevel(self)
        dlg.title("Provision New Isolated Farm Clone")
        dlg.geometry("460x340")
        dlg.resizable(False, False)
        dlg.configure(fg_color="#0F172A")
        dlg.transient(self)
        dlg.grab_set()
        self._provision_dialog = dlg

        def _close():
            self._provision_dialog = None
            dlg.destroy()

        dlg.protocol("WM_DELETE_WINDOW", _close)

        hdr = ctk.CTkLabel(
            dlg,
            text="Provision Isolated Farm Client Clone",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#F8FAFC",
        )
        hdr.pack(anchor="w", padx=18, pady=(14, 2))
        sub = ctk.CTkLabel(
            dlg,
            text="Creates an isolated Unity PlayerPrefs clone folder linked to Main GameData.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8",
        )
        sub.pack(anchor="w", padx=18, pady=(0, 10))

        form = ctk.CTkFrame(dlg, fg_color="#111827", corner_radius=8)
        form.pack(fill="x", padx=16, pady=4)
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="Client Label:", text_color="#CBD5E1", font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=10, pady=6, sticky="w")
        ent_label = ctk.CTkEntry(form, placeholder_text="Fourth")
        ent_label.insert(0, "Fourth")
        ent_label.grid(row=0, column=1, columnspan=2, padx=10, pady=6, sticky="ew")

        ctk.CTkLabel(form, text="Unity Profile (5 chars):", text_color="#CBD5E1", font=ctk.CTkFont(size=11)).grid(row=1, column=0, padx=10, pady=6, sticky="w")
        ent_profile = ctk.CTkEntry(form, placeholder_text="Alt4Z")
        ent_profile.insert(0, "Alt4Z")
        ent_profile.grid(row=1, column=1, columnspan=2, padx=10, pady=6, sticky="ew")

        ctk.CTkLabel(form, text="Target Root Folder:", text_color="#CBD5E1", font=ctk.CTkFont(size=11)).grid(row=2, column=0, padx=10, pady=6, sticky="w")
        ent_root = ctk.CTkEntry(form, placeholder_text=r"G:\Last Z\Fourth")
        ent_root.insert(0, r"G:\Last Z\Fourth")
        ent_root.grid(row=2, column=1, padx=(10, 4), pady=6, sticky="ew")

        def _browse():
            from tkinter import filedialog
            picked = filedialog.askdirectory(parent=dlg, title="Select Farm Clone Root Folder")
            if picked:
                ent_root.delete(0, "end")
                ent_root.insert(0, picked)

        ctk.CTkButton(form, text="Browse", width=64, height=28, command=_browse).grid(row=2, column=2, padx=(0, 10), pady=6)

        ctk.CTkLabel(form, text="Executable Name:", text_color="#CBD5E1", font=ctk.CTkFont(size=11)).grid(row=3, column=0, padx=10, pady=6, sticky="w")
        ent_exe = ctk.CTkEntry(form, placeholder_text="Alt4Game.exe")
        ent_exe.insert(0, "Alt4Game.exe")
        ent_exe.grid(row=3, column=1, columnspan=2, padx=10, pady=6, sticky="ew")

        lbl_err = ctk.CTkLabel(dlg, text="", font=ctk.CTkFont(size=11), text_color="#F87171")
        lbl_err.pack(anchor="w", padx=18, pady=(6, 2))

        btns = ctk.CTkFrame(dlg, fg_color="transparent")
        btns.pack(fill="x", padx=16, pady=(6, 12))

        def _confirm():
            label = ent_label.get().strip()
            prof = ent_profile.get().strip()
            root_dir = ent_root.get().strip()
            exe_name = ent_exe.get().strip()
            if not prof.isascii() or len(prof) != 5:
                lbl_err.configure(text="Unity Profile must be exactly 5 ASCII characters (e.g. Alt4Z).")
                return
            if not root_dir or not exe_name:
                lbl_err.configure(text="Target Root Folder and Executable Name are required.")
                return
            if not exe_name.lower().endswith(".exe"):
                exe_name = f"{exe_name}.exe"
            if not self._begin_action("provision_farm"):
                lbl_err.configure(text="Another provision task is already running.")
                return
            _close()
            args = ["provision", prof, root_dir, exe_name] + ([label] if label else [])
            self.log(f"Provisioning farm clone '{label or prof}' ({prof} -> {root_dir}\\{exe_name})...")
            def worker():
                try:
                    res = self._run_tool("sync farm clients.py", args, timeout=60)
                    out = res.stdout.strip() or res.stderr.strip() or f"exit={res.returncode}"
                    self.after(0, lambda o=out: self.log(f"Provision Farm: {o}"))
                    self.after(600, self.on_scan_fleet)
                except Exception as e:
                    self.after(0, lambda e=e: self.log(f"Provision Error: {e}"))
                finally:
                    self.after(0, lambda: self._end_action("provision_farm"))
            self.run_worker(worker)

        ctk.CTkButton(btns, text="Cancel", width=90, fg_color="#334155", hover_color="#475569", command=_close).pack(side="right", padx=(6, 0))
        ctk.CTkButton(btns, text="Provision Clone", width=130, fg_color="#7C3AED", hover_color="#6D28D9", command=_confirm).pack(side="right")

    def on_run_bot_cycle(self, dry_run=False):
        if not self._begin_action("bot_cycle"):
            self.log("Bot cycle already running...")
            return
        self.on_save_bot_config(quiet=True)
        target_arg = self._resolve_cycle_target_arg()
        mode_lbl = "DRY-RUN" if dry_run else "LIVE"
        self.log(f"Running {mode_lbl} bot cycle (target={target_arg})...")
        def worker():
            try:
                extra = ["--cycle", "--target", str(target_arg)]
                if dry_run:
                    extra.append("--dry-run")
                res = self._run_tool("multi client bot.py", extra, timeout=180)
                self.after(0, self._refresh_fleet_ui)
                summary = f"Bot {mode_lbl} cycle exit={res.returncode}"
                if res.stdout:
                    idx = res.stdout.find("{")
                    if idx != -1:
                        try:
                            payload = json.loads(res.stdout[idx:])
                            summary = f"Bot {mode_lbl}: processed {payload.get('processed_count', 0)}/{payload.get('running_count', 0)} running client(s)"
                        except Exception:
                            summary = res.stdout.strip().splitlines()[-1]
                elif res.stderr:
                    summary = res.stderr.strip()
                self.after(0, lambda s=summary: self.log(s))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Bot Cycle Error: {e}"))
            finally:
                self.after(0, lambda: self._end_action("bot_cycle"))
        self.run_worker(worker)

    def on_start_bot_daemon(self):
        self.on_save_bot_config(quiet=True)
        self.log("Starting Multi-Client Bot daemon in background...")
        def worker():
            script = self.find_script("multi client bot.py")
            try:
                if not os.path.exists(script):
                    raise FileNotFoundError(f"Script not found in {REPO_ROOT}: multi client bot.py")
                self._subproc_popen([PYTHON_CLI_EXE, "-X", "utf8", script, "--daemon"], creationflags=NO_WINDOW_FLAGS)
                time.sleep(1.0)
                self.after(0, self._refresh_fleet_ui)
                self.after(0, lambda: self.log("Multi-Client Bot daemon started."))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Start Daemon Error: {e}"))
        self.run_worker(worker)

    def on_stop_bot_daemon(self):
        self.log("Sending stop signal to Multi-Client Bot daemon...")
        def worker():
            try:
                res = self._run_tool("multi client bot.py", ["--stop-daemon"], timeout=15)
                time.sleep(0.5)
                self.after(0, self._refresh_fleet_ui)
                out = res.stdout.strip() or res.stderr.strip()
                self.after(0, lambda o=out: self.log(f"Stop Daemon: {o}"))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Stop Daemon Error: {e}"))
        self.run_worker(worker)

    def on_install_bot_task(self):
        self.on_save_bot_config(quiet=True)
        self.log("Registering Windows Scheduled Task for Multi-Client Bot...")
        def worker():
            try:
                res = self._run_tool("multi client bot.py", ["--install-task"], timeout=20)
                self.after(0, self._refresh_fleet_ui)
                out = res.stdout.strip() or res.stderr.strip()
                self.after(0, lambda o=out: self.log(f"Schedule Register: {o}"))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Schedule Register Error: {e}"))
        self.run_worker(worker)

    def on_uninstall_bot_task(self):
        self.log("Removing Multi-Client Bot Windows Scheduled Task...")
        def worker():
            try:
                res = self._run_tool("multi client bot.py", ["--uninstall-task"], timeout=20)
                self.after(0, self._refresh_fleet_ui)
                out = res.stdout.strip() or res.stderr.strip()
                self.after(0, lambda o=out: self.log(f"Schedule Remove: {o}"))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Schedule Remove Error: {e}"))
        self.run_worker(worker)

    def on_sync_google_bracket(self):
        if not self._begin_action("sync_google_bracket"):
            self.log("Google bracket sync already in progress...")
            return
        live_refresh = bool(self.running_clients)
        pid = self.target_pid
        mode_note = " (live client refresh)" if live_refresh else " (cached data)"
        self.log(f"Syncing all 16 Native Google Bracket Spreadsheets (#689-#704){mode_note}...")
        def worker():
            extra = ["--states", "all"]
            if live_refresh:
                extra.append("--refresh-live")
                if pid:
                    extra.extend(["--pid", str(pid)])
            try:
                res = self._run_tool("sync bracket drive sheets.py", extra, timeout=480)
                out = res.stdout.strip() or res.stderr.strip()
                self.after(0, lambda o=out: self.log(f"Google Bracket Sync: {o}"))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Google Bracket Sync Error: {e}"))
            finally:
                self.after(0, lambda: self._end_action("sync_google_bracket"))
        self.run_worker(worker)

    def ensure_daemon_running(self):
        running = False
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                cmd = " ".join(proc.info.get('cmdline') or [])
                if 'lastz auto engine daemon' in cmd or 'lastz_auto_engine_daemon' in cmd:
                    running = True
                    break
            except Exception:
                pass
        if not running:
            daemon_script = self.find_script("lastz auto engine daemon.py")
            if daemon_script and os.path.exists(daemon_script):
                try:
                    self._subproc_popen([PYTHON_CLI_EXE, daemon_script], creationflags=NO_WINDOW_FLAGS)
                    self.log("Auto-started background engine daemon.")
                except Exception:
                    pass

    def on_restart_daemon(self):
        self.log("Restarting LastZ Background Auto-Engine Daemon...")
        def worker():
            script = self.find_script("lastz_auto_engine_daemon.py")
            try:
                if not os.path.exists(script):
                    raise FileNotFoundError(f"Daemon script not found in {REPO_ROOT}")
                self._subproc_popen([PYTHON_CLI_EXE, script], creationflags=NO_WINDOW_FLAGS)
                self.after(0, lambda: self.log("Auto-Engine Daemon launched in new background session."))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Failed to launch daemon: {e}"))
        self.run_worker(worker)

    def on_export_inventory(self):
        self.log("Exporting bag inventory & speedup reserves to Excel...")
        def worker():
            try:
                script_name = "export_inventory_excel.py"
                if not os.path.exists(self.find_script(script_name)):
                    script_name = "build_bag_inventory_excel.py"
                res = self._run_tool(script_name, timeout=20)
                out = res.stdout.strip() or res.stderr.strip() or f"exit={res.returncode}"
                self.after(0, lambda o=out: self.log(f"Bag Export: {o}"))
                for cand_name in ("inventory_reserves.xlsx", "heinzy_bag_inventory_master.xlsx"):
                    target = self.find_file(cand_name)
                    if target and os.path.exists(target):
                        self._open_output_file(target)
                        break
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Inventory Exception: {e}"))
        self.run_worker(worker)

    def on_export_tech(self):
        self.log("Exporting Tech Tree Progress to formatted Excel workbook...")
        def worker():
            try:
                res = self._run_tool("export_tech_tree_excel.py", timeout=20)
                out = res.stdout.strip() or res.stderr.strip() or f"exit={res.returncode}"
                self.after(0, lambda o=out: self.log(f"Tech Tree: {o}"))
                target = self.find_file("Tech_Tree_Progress.xlsx")
                if target and os.path.exists(target):
                    self._open_output_file(target)
                else:
                    self.after(0, lambda: self.log("Tech Tree Excel file not found."))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Tech Tree Exception: {e}"))
        self.run_worker(worker)

    def on_open_data_folder(self):
        target = DATA_DIR if os.path.isdir(DATA_DIR) else self.find_file("lastz_data_master")
        if target and os.path.exists(target):
            self.log(f"Opening Data Folder: {target}")
            self._open_output_file(target)
        elif os.path.exists(SCRATCH_DIR):
            self.log(f"Opening Working Scratch Folder: {SCRATCH_DIR}")
            self._open_output_file(SCRATCH_DIR)

    # Action Handlers: Alliances Tab
    def on_export_vs(self):
        self.log("Exporting VS Duel Rankings to Excel...")
        def worker():
            try:
                res = self._run_tool("export_vs_duel_excel.py", timeout=25)
                out = res.stdout.strip() or res.stderr.strip() or f"exit={res.returncode}"
                self.after(0, lambda o=out: self.log(f"VS Duel: {o}"))
                target = self.find_file("vs_duel_rankings.xlsx")
                self._open_output_file(target)
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"VS Duel Exception: {e}"))
        self.run_worker(worker)

    def on_export_roster(self):
        al_tag = self.env.get("allianceTag", "WARG")
        self.log(f"Exporting [{al_tag}] Alliance Roster...")
        def worker():
            try:
                res = self._run_tool("export_alliance_roster_excel.py", timeout=20)
                out = res.stdout.strip() or res.stderr.strip() or f"exit={res.returncode}"
                self.after(0, lambda o=out: self.log(f"Roster: {o}"))
                target = self.find_file("vs33_alliance_roster.xlsx")
                self._open_output_file(target)
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Roster Exception: {e}"))
        self.run_worker(worker)

    def on_export_alliance_members(self):
        self.log("Exporting Alliance Members to formatted Excel master workbook...")
        def worker():
            script = self.find_script("export_alliance_members_excel.py")
            try:
                res = self._subproc_run([PYTHON_CLI_EXE, script], timeout=20)
                out = res.stdout.strip() or res.stderr.strip() or f"exit={res.returncode}"
                self.after(0, lambda o=out: self.log(f"Alliance Members: {o}"))
                target = self.find_file("Alliance_Members_Master.xlsx")
                if os.path.exists(target):
                    self._open_output_file(target)
                else:
                    self.after(0, lambda: self.log("Alliance Members Excel file not found."))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Alliance Members Exception: {e}"))
        self.run_worker(worker)

    def on_open_active_migration(self):
        s = self.env.get("serverId", 702)
        perfect_path = os.path.join(BRACKET_DIR, f"State {s} Migration.xlsx")
        master_path = os.path.join(SCRATCH_DIR, f"State_{s}_Top_10_Alliances_Migration_Master.xlsx")
        if os.path.exists(perfect_path):
            self.log(f"Opening State {s} Migration Workbook: {perfect_path}")
            os.startfile(perfect_path)
        elif os.path.exists(master_path):
            self.log(f"Opening State {s} Migration Master: {master_path}")
            os.startfile(master_path)
        else:
            self.log(f"No specific migration workbook found for State {s}. Opening bracket folder...")
            self.on_open_bracket_folder()

    def on_export_top10(self):
        s = self.env.get("serverId", 702)
        perfect_path = os.path.join(BRACKET_DIR, f"State {s} Migration.xlsx")
        master_path = os.path.join(SCRATCH_DIR, f"State_{s}_Top_10_Alliances_Migration_Master.xlsx")
        fallback_path = os.path.join(BRACKET_DIR, "State 694 Migration.xlsx")

        if os.path.exists(perfect_path):
            self.log(f"Opening State {s} Top 10 Alliances Master: {perfect_path}")
            os.startfile(perfect_path)
        elif os.path.exists(master_path):
            self.log(f"Opening State {s} Top 10 Alliances Master: {master_path}")
            os.startfile(master_path)
        elif os.path.exists(fallback_path):
            self.log(f"Opening Bracket Migration Master: {fallback_path}")
            os.startfile(fallback_path)
        else:
            self.log("Top 10 Alliances Excel workbook not found.")

    def on_open_selected_bracket_state(self):
        sel = self.combo_bracket.get()
        target_name = f"{sel} Migration.xlsx"
        target_path = os.path.join(BRACKET_DIR, target_name)
        if os.path.exists(target_path):
            self.log(f"Opening: {target_name}")
            os.startfile(target_path)
        else:
            self.log(f"File not found: {target_path}. Opening bracket folder...")
            self.on_open_bracket_folder()

    def on_open_bracket_folder(self):
        if os.path.exists(BRACKET_DIR):
            self.log(f"Opening Bracket Folder: {BRACKET_DIR}")
            os.startfile(BRACKET_DIR)
        else:
            self.log(f"Folder not found: {BRACKET_DIR}")

    # Action Handlers: Map Tab
    def on_export_map(self):
        self.log("Extracting full map intelligence (all 2,180 bases & nodes)...")
        def worker():
            script = self.find_script("export_map_intelligence.py")
            t0 = time.time()
            try:
                res = self._subproc_run([PYTHON_CLI_EXE, script], timeout=30)
                elapsed = time.time() - t0
                if res.returncode == 0:
                    self.after(0, lambda el=elapsed: self.log(f"Full map export complete ({el:.1f}s)! Opening Excel..."))
                    target_file = self.find_file("map_all_bases.xlsx")
                    if os.path.exists(target_file):
                        self._open_output_file(target_file)
                else:
                    err = res.stderr.strip() or res.stdout.strip()
                    self.after(0, lambda err=err: self.log(f"Map export failed: {err}"))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Exception: {e}"))
        self.run_worker(worker)

    def on_open_map_summary_excel(self):
        self.log("Opening Map Intelligence Summary (Excel)...")
        def worker():
            script = self.find_script("export_map_summary_excel.py")
            try:
                res = self._subproc_run([PYTHON_CLI_EXE, script], timeout=15)
                out = res.stdout.strip() or res.stderr.strip() or f"exit={res.returncode}"
                self.after(0, lambda o=out: self.log(f"Map Summary: {o}"))
                target = self.find_file("Map_Intelligence_Summary.xlsx")
                if os.path.exists(target):
                    self._open_output_file(target)
                else:
                    self.after(0, lambda: self.log("Map Summary Excel not found."))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Map Summary Exception: {e}"))
        self.run_worker(worker)

    def on_navigate_resource(self):
        res_type = self.combo_res_type.get()
        lvl_str = self.combo_res_lvl.get()
        lvl = None
        if "Level " in lvl_str:
            try:
                lvl = int(lvl_str.replace("Level ", "").strip())
            except ValueError:
                lvl = None

        self.lbl_finder_status.configure(text=f"Searching closest un-manned {res_type} ({lvl_str})...", text_color="#F59E0B")
        self.log(f"Searching closest un-manned {res_type} ({lvl_str}) from base...")

        def worker():
            script = self.find_script("navigate to resource.py")
            args = [PYTHON_CLI_EXE, script, res_type]
            if lvl is not None:
                args.append(str(lvl))
            args.extend(self._pid_args())
            try:
                res = self._subproc_run(args, timeout=10, env=self._subprocess_env())
                out = res.stdout.strip()
                if "[+] Found closest:" in out or "Navigated to" in out:
                    line = [l for l in out.splitlines() if "[+]" in l or "Navigated" in l][-1]
                    self.after(0, lambda l=line: self.lbl_finder_status.configure(text=l, text_color="#10B981"))
                    self.after(0, lambda l=line: self.log(l))
                else:
                    err_msg = res.stderr.strip() or out or "No matching un-manned resource found."
                    self.after(0, lambda em=err_msg: self.lbl_finder_status.configure(text=em, text_color="#EF4444"))
                    self.after(0, lambda em=err_msg: self.log(f"Locator: {em}"))
            except Exception as e:
                self.after(0, lambda e=e: self.lbl_finder_status.configure(text=f"Error: {e}", text_color="#EF4444"))
                self.after(0, lambda e=e: self.log(f"Locator Exception: {e}"))
        self.run_worker(worker)

    def on_dispatch_resource(self):
        res_type = self.combo_res_type.get()
        lvl_str = self.combo_res_lvl.get()
        lvl = None
        if "Level " in lvl_str:
            try:
                lvl = int(lvl_str.replace("Level ", "").strip())
            except ValueError:
                lvl = None

        self.lbl_finder_status.configure(text=f"Auto-dispatching squad to closest un-manned {res_type} ({lvl_str})...", text_color="#3B82F6")
        self.log(f"Auto-dispatching squad to closest un-manned {res_type} ({lvl_str})...")

        def worker():
            script = self.find_script("navigate to resource.py")
            args = [PYTHON_CLI_EXE, script, res_type]
            if lvl is not None:
                args.append(str(lvl))
            args.append("--dispatch")
            args.extend(self._pid_args())
            try:
                res = self._subproc_run(args, timeout=15, env=self._subprocess_env())
                out = res.stdout.strip()
                if "[+] Dispatched" in out:
                    line = [l for l in out.splitlines() if "[+] Dispatched" in l][-1]
                    self.after(0, lambda l=line: self.lbl_finder_status.configure(text=l, text_color="#10B981"))
                    self.after(0, lambda l=line: self.log(l))
                elif "[-]" in out:
                    line = [l for l in out.splitlines() if "[-]" in l][-1]
                    self.after(0, lambda l=line: self.lbl_finder_status.configure(text=line, text_color="#F59E0B"))
                    self.after(0, lambda l=line: self.log(f"Auto-March: {line}"))
                else:
                    err_msg = res.stderr.strip() or out or "Could not dispatch squad."
                    self.after(0, lambda em=err_msg: self.lbl_finder_status.configure(text=em, text_color="#EF4444"))
                    self.after(0, lambda em=err_msg: self.log(f"Auto-March Error: {em}"))
            except Exception as e:
                self.after(0, lambda e=e: self.lbl_finder_status.configure(text=f"Error: {e}", text_color="#EF4444"))
                self.after(0, lambda e=e: self.log(f"Auto-March Exception: {e}"))
        self.run_worker(worker)

    def on_export_radar(self):
        self.log("Running War Radar (HQ 25-35)...")
        def worker():
            try:
                res = self._run_tool("export_unshielded_targets.py", timeout=20)
                if res.returncode == 0:
                    self.after(0, lambda: self.log("Radar export complete! Opening Excel..."))
                    target_file = self.find_file("unshielded_targets.xlsx")
                    self._open_output_file(target_file)
                else:
                    err = (res.stderr or res.stdout).strip()
                    self.after(0, lambda e=err: self.log(f"Radar failed: {e}"))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Exception: {e}"))
        self.run_worker(worker)

    def on_export_elite_radar(self):
        self.log("Running Elite Radar (HQ 30-35 Only)...")
        def worker():
            try:
                res = self._run_tool("export_unshielded_targets.py", ["30"], timeout=20)
                if res.returncode == 0:
                    self.after(0, lambda: self.log("Elite Radar export complete! Opening Excel..."))
                    target_file = self.find_file("unshielded_targets.xlsx")
                    self._open_output_file(target_file)
                else:
                    err = (res.stderr or res.stdout).strip()
                    self.after(0, lambda e=err: self.log(f"Elite Radar failed: {e}"))
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Exception: {e}"))
        self.run_worker(worker)

    def on_export_mines(self):
        self.log("Scanning map for Level 6-8 high-tier resource mines...")
        def worker():
            try:
                res = self._run_tool("export_high_tier_resources.py", timeout=20)
                out = res.stdout.strip() or res.stderr.strip() or f"exit={res.returncode}"
                self.after(0, lambda o=out: self.log(f"Mines: {o}"))
                target = self.find_file("high_tier_resources.xlsx")
                self._open_output_file(target)
            except Exception as e:
                self.after(0, lambda e=e: self.log(f"Mines Exception: {e}"))
        self.run_worker(worker)

if __name__ == "__main__":
    try:
        log_crash("STARTUP: Starting HeinZ application")
        app = HeinZ()
        log_crash("STARTUP: Entering mainloop")
        app.mainloop()
        log_crash("SHUTDOWN: mainloop returned normally")
    except Exception as e:
        log_crash(e)
