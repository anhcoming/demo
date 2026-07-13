#!/usr/bin/env python3
import os
import re
import time
import requests
from flask import Flask, render_template, jsonify, request, Response, redirect
from werkzeug.utils import secure_filename

# ==========================================
# OUTDATED WEBSITE FINDER – TẠM THỜI ẨN
# ==========================================
# import csv
# import time
# from urllib.parse import urlparse, quote_plus
# import requests
# from bs4 import BeautifulSoup
# import urllib3
#
# # Import các hàm phân tích lead từ lead_analyzer
# from lead_analyzer import analyze_csv_leads, is_vietnamese_lead
#
# # Vô hiệu hóa cảnh báo SSL không an toàn
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#
# HEADERS = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# }
#
# CSV_FILE = 'real_scan_results.csv'
# FALLBACK_CSV_FILE = 'potential_sites.csv'
# LEADS_CSV_FILE = 'local_leads_report.csv'
# FIELDNAMES = ['domain', 'url', 'title', 'status', 'ssl', 'responsive', 'table_layout', 'obsolete_tags', 'jquery_version', 'copyright_years', 'score', 'notes']
#
# def search_duckduckgo(query, limit=15):
#     """
#     Tìm kiếm trên DuckDuckGo Lite
#     """
#     url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
#     try:
#         response = requests.get(url, headers=HEADERS, timeout=12)
#         if response.status_code == 202 or 'anomaly' in response.text:
#             raise Exception("DuckDuckGo yêu cầu xác minh Bot (Captcha). Vui lòng nhập trực tiếp danh sách tên miền.")
#         if response.status_code != 200:
#             raise Exception(f"Lỗi kết nối tới công cụ tìm kiếm (Status: {response.status_code})")
#             
#         soup = BeautifulSoup(response.text, 'html.parser')
#         links = []
#         
#         for a in soup.find_all('a', class_='result__url'):
#             href = a.get('href')
#             if href:
#                 if 'duckduckgo.com/l/?kh=' in href:
#                     match = re.search(r'uddg=([^&]+)', href)
#                     if match:
#                         from urllib.parse import unquote
#                         href = unquote(match.group(1))
#                 
#                 if href.startswith('http') and 'duckduckgo.com' not in href:
#                     links.append(href)
#                     if len(links) >= limit:
#                         break
#         return links
#     except Exception as e:
#         raise e
#
# def clean_url(url):
#     """Làm sạch và định dạng URL"""
#     if not url:
#         return ''
#     url = url.strip()
#     if not url.startswith(('http://', 'https://')):
#         return f"http://{url}"
#     return url
#
# def analyze_website(url):
#     """
#     Phân tích chi tiết một trang web để phát hiện các yếu tố lỗi thời
#     """
#     url = clean_url(url)
#     result = {
#         'url': url,
#         'domain': urlparse(url).netloc.replace('www.', ''),
#         'status': 'Error',
#         'title': 'N/A',
#         'ssl': 'No',
#         'responsive': 'No',
#         'table_layout': 'No',
#         'obsolete_tags': 'None',
#         'jquery_version': 'N/A',
#         'copyright_years': 'N/A',
#         'score': 0,
#         'notes': ''
#     }
#     
#     if url.startswith('https://'):
#         result['ssl'] = 'Yes'
#         
#     try:
#         response = requests.get(url, headers=HEADERS, timeout=10, verify=False)
#         result['status'] = f"{response.status_code}"
#         
#         soup = BeautifulSoup(response.text, 'html.parser')
#         
#         if soup.title and soup.title.string:
#             result['title'] = soup.title.string.strip()
#             
#         viewport = soup.find('meta', attrs={'name': 'viewport'})
#         if viewport and 'width=device-width' in str(viewport.get('content', '')):
#             result['responsive'] = 'Yes'
#         else:
#             result['responsive'] = 'No'
#             result['score'] += 40
#             result['notes'] += "Không Responsive; "
#
#         tables = soup.find_all('table')
#         if len(tables) > 4:
#             nested_tables = False
#             for t in tables:
#                 if t.find('table'):
#                     nested_tables = True
#                     break
#             if nested_tables:
#                 result['table_layout'] = 'Yes'
#                 result['score'] += 20
#                 result['notes'] += "Table Layout; "
#
#         obsolete_found = []
#         for tag in ['font', 'center', 'frame', 'frameset', 'marquee', 'blink', 'nobr']:
#             if soup.find(tag):
#                 obsolete_found.append(tag)
#         if obsolete_found:
#             result['obsolete_tags'] = ', '.join(obsolete_found)
#             result['score'] += 10 * len(obsolete_found)
#             result['notes'] += f"Thẻ cổ: {result['obsolete_tags']}; "
#
#         jquery_ver = 'N/A'
#         for script in soup.find_all('script', src=True):
#             src = script['src'].lower()
#             match = re.search(r'jquery[.-]([0-9.]+)', src)
#             if match:
#                 jquery_ver = match.group(1)
#                 result['jquery_version'] = jquery_ver
#                 if jquery_ver.startswith(('1.', '2.')):
#                     result['score'] += 15
#                     result['notes'] += f"jQuery cũ ({jquery_ver}); "
#                 break
#
#         html_text = response.text
#         copyright_pattern = re.compile(r'(?:copyright|©|\(c\))\s*(?:19\d{2}|20\d{2})\s*(?:-\s*(?:19\d{2}|20\d{2}))?', re.IGNORECASE)
#         matches = copyright_pattern.findall(html_text)
#         
#         if not matches:
#             footer_text = ""
#             for footer_tag in ['footer', 'div']:
#                 tag_elm = soup.find(footer_tag, class_=re.compile(r'foot|copy', re.I)) or soup.find(footer_tag, id=re.compile(r'foot|copy', re.I))
#                 if tag_elm:
#                     footer_text += tag_elm.get_text()
#             year_matches = re.findall(r'\b(20[0-2]\d|19\d{2})\b', footer_text)
#             if year_matches:
#                 matches = year_matches
#
#         if matches:
#             years = []
#             for m in matches:
#                 found_years = re.findall(r'\b(20[0-2]\d|19\d{2})\b', m)
#                 years.extend([int(y) for y in found_years])
#             if years:
#                 latest_year = max(years)
#                 result['copyright_years'] = str(latest_year)
#                 current_year = time.localtime().tm_year
#                 diff = current_year - latest_year
#                 if diff > 5:
#                     result['score'] += min(diff * 5, 25)
#                     result['notes'] += f"Bản quyền cũ ({latest_year}); "
#         
#         if result['ssl'] == 'No':
#             result['score'] += 10
#             result['notes'] += "Không SSL; "
#             
#     except requests.exceptions.Timeout:
#         result['status'] = 'Timeout'
#         result['notes'] = 'Timeout kết nối'
#     except requests.exceptions.SSLError:
#         result['status'] = 'SSL Error'
#         result['notes'] = 'Lỗi SSL'
#     except Exception as e:
#         result['status'] = 'Failed'
#         result['notes'] = f"Lỗi: {str(e)}"
#         
#     return result
#
# def load_results():
#     """
#     Đọc dữ liệu từ file CSV chính hoặc file fallback
#     """
#     results = {}
#     active_file = CSV_FILE if os.path.exists(CSV_FILE) else (FALLBACK_CSV_FILE if os.path.exists(FALLBACK_CSV_FILE) else None)
#     
#     if active_file:
#         try:
#             with open(active_file, 'r', encoding='utf-8') as f:
#                 reader = csv.DictReader(f)
#                 for row in reader:
#                     try:
#                         row['score'] = int(row['score'])
#                     except:
#                         row['score'] = 0
#                     domain = row['domain']
#                     results[domain] = row
#         except Exception as e:
#             print(f"[!] Lỗi khi đọc file CSV: {e}")
#             
#     return results
#
# def save_results(results_dict):
#     """
#     Ghi dữ liệu vào CSV
#     """
#     try:
#         with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
#             writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
#             writer.writeheader()
#             for r in results_dict.values():
#                 filtered_r = {k: r.get(k, 'N/A') for k in FIELDNAMES}
#                 writer.writerow(filtered_r)
#         return True
#     except Exception as e:
#         print(f"[!] Lỗi khi ghi file CSV: {e}")
#         return False
#
# # --- FLASK ENDPOINTS ---
# ==========================================

app = Flask(__name__, template_folder='templates')

# Vercel serverless: only /tmp is writable
IS_VERCEL = os.environ.get('VERCEL', False)
UPLOAD_DIR = '/tmp/uploads' if IS_VERCEL else 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

# Tạo thư mục uploads nếu chưa có
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)





# ==========================================
import sqlite3
from datetime import datetime, timedelta

RENTAL_DB = '/tmp/rental_shop.db' if os.environ.get('VERCEL') else 'rental_shop.db'

# ─── Trạng thái ───────────────────────────────────────────────────
# Booking:  'Chờ duyệt' → 'Đã duyệt' → 'Đang thuê' → 'Đã trả' / 'Đã hủy'
# Dress:    'Sẵn sàng' → 'Đang thuê' → 'Đang giặt là'/'Đang sửa chữa' → 'Sẵn sàng'
# ──────────────────────────────────────────────────────────────────

def _get_conn():
    conn = sqlite3.connect(RENTAL_DB)
    conn.row_factory = sqlite3.Row
    return conn

def _date_only(dt_str):
    """Lấy phần ngày YYYY-MM-DD từ chuỗi 'YYYY-MM-DD HH:MM' hoặc 'YYYY-MM-DD'."""
    return str(dt_str)[:10] if dt_str else None

def _add_buffer(start_str, end_str):
    """Tính locked_start (D-1) và locked_end (D+2) từ ngày thuê."""
    try:
        s = datetime.strptime(_date_only(start_str), '%Y-%m-%d')
        e = datetime.strptime(_date_only(end_str), '%Y-%m-%d')
        return (s - timedelta(days=1)).strftime('%Y-%m-%d'), (e + timedelta(days=2)).strftime('%Y-%m-%d')
    except Exception:
        return start_str, end_str

def _check_conflicts(cursor, dress_id, start_str, end_str, exclude_booking_id=None):
    """Kiểm tra có đơn Đã duyệt / Đang thuê nào trùng lịch buffer không."""
    ls, le = _add_buffer(start_str, end_str)
    query = '''
        SELECT id, customer_name, locked_start, locked_end
        FROM bookings
        WHERE dress_id = ?
          AND status IN ('Đã duyệt', 'Đang thuê')
          AND locked_start IS NOT NULL
          AND NOT (locked_end < ? OR locked_start > ?)
    '''
    params = [dress_id, ls, le]
    if exclude_booking_id:
        query += ' AND id != ?'
        params.append(exclude_booking_id)
    cursor.execute(query, params)
    return cursor.fetchall()

def _pending_conflicts(cursor, dress_id, start_str, end_str, exclude_booking_id=None):
    """Tìm các đơn Chờ duyệt khác trùng ngày."""
    s = _date_only(start_str)
    e = _date_only(end_str)
    query = '''
        SELECT id, customer_name, start_date, end_date
        FROM bookings
        WHERE dress_id = ?
          AND status = 'Chờ duyệt'
          AND NOT (end_date < ? OR start_date > ?)
    '''
    params = [dress_id, s, e]
    if exclude_booking_id:
        query += ' AND id != ?'
        params.append(exclude_booking_id)
    cursor.execute(query, params)
    return cursor.fetchall()

def init_db_if_not_exists():
    conn = sqlite3.connect(RENTAL_DB)
    cursor = conn.cursor()

    # ── Tạo bảng ──────────────────────────────────────────────────
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dresses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        size TEXT NOT NULL,
        color TEXT NOT NULL,
        price INTEGER NOT NULL,
        deposit INTEGER NOT NULL,
        image_url TEXT,
        status TEXT NOT NULL DEFAULT 'Sẵn sàng'
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dress_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        total_price INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'Chờ duyệt',
        payment_status TEXT NOT NULL DEFAULT 'Đã cọc',
        appointment_datetime TEXT,
        notes TEXT,
        locked_start TEXT,
        locked_end TEXT,
        approved_at TEXT,
        fine_amount INTEGER DEFAULT 0,
        FOREIGN KEY (dress_id) REFERENCES dresses (id)
    )
    ''')

    # ── Migration: thêm cột mới nếu DB cũ chưa có ─────────────────
    new_cols = [
        ('appointment_datetime', 'TEXT'),
        ('notes', 'TEXT'),
        ('locked_start', 'TEXT'),
        ('locked_end', 'TEXT'),
        ('approved_at', 'TEXT'),
        ('fine_amount', 'INTEGER DEFAULT 0'),
    ]
    cursor.execute("PRAGMA table_info(bookings)")
    existing = {row[1] for row in cursor.fetchall()}
    for col_name, col_def in new_cols:
        if col_name not in existing:
            cursor.execute(f'ALTER TABLE bookings ADD COLUMN {col_name} {col_def}')

    # ── Seed dữ liệu nếu bảng trống ───────────────────────────────
    cursor.execute('SELECT COUNT(*) FROM dresses')
    if cursor.fetchone()[0] == 0:
        dresses_data = [
            ("Váy cổ đổ đen nhún bụng BYDI", "Váy Body", "M", "Đen", 250000, 1000000, "https://thuevay.vn/wp-content/uploads/2026/01/IMG_0554-667x800.jpg", "Sẵn sàng"),
            ("Váy cổ đổ trắng DZUNG BEIZ", "Váy Body", "S", "Trắng", 300000, 1200000, "https://thuevay.vn/wp-content/uploads/2026/01/IMG_2477-667x800.jpg", "Sẵn sàng"),
            ("Váy đen quây xoè tầng PARAMO", "Váy Xòe", "M", "Đen", 350000, 1500000, "https://thuevay.vn/wp-content/uploads/2026/01/IMG_2603-667x800.jpg", "Sẵn sàng"),
            ("Váy đen trễ vai xẻ đùi BYDI", "Váy Body", "S", "Đen", 280000, 1200000, "https://thuevay.vn/wp-content/uploads/2026/01/IMG_1323-667x800.jpg", "Sẵn sàng"),
            ("Áo dài thêu hoa màu xanh pastel", "Áo Dài", "L", "Trắng", 200000, 800000, "https://thuevay.vn/wp-content/uploads/2024/12/338146273_759679602404017_2943694123853596028_n.jpg", "Sẵn sàng"),
            ("Set áo cổ yếm chân váy ren hoa", "Set", "M", "Kem", 220000, 900000, "https://thuevay.vn/wp-content/uploads/2025/12/IMG_8542-e1764754743347.jpg", "Sẵn sàng"),
            ("Váy body nhũ bạc lấp lánh", "Váy Body", "S", "Trắng", 320000, 1500000, "https://thuevay.vn/wp-content/uploads/2025/12/490192212_641490972060782_8900130820694787555_n-1.jpg", "Sẵn sàng"),
            ("Váy xòe hồng xếp ly công chúa", "Váy Xòe", "M", "Hồng", 260000, 1000000, "https://thuevay.vn/wp-content/uploads/2025/12/486637213_122193607562102890_6066223404235449123_n-1.jpg", "Sẵn sàng"),
            ("Váy quây dạ hội đỏ nhung quý phái", "Váy Xòe", "S", "Đỏ", 380000, 1800000, "https://thuevay.vn/wp-content/uploads/2026/01/IMG_0186-667x800.jpg", "Sẵn sàng"),
            ("Váy cưới xòe hoa bồng bềnh công chúa", "Váy Xòe", "M", "Trắng", 800000, 3000000, "https://thuevay.vn/wp-content/uploads/2026/01/IMG_2583-667x800.jpg", "Sẵn sàng"),
            ("Áo dài đỏ gấm hoa cúc chìm", "Áo Dài", "M", "Đỏ", 240000, 1000000, "https://thuevay.vn/wp-content/uploads/2024/12/338146273_759679602404017_2943694123853596028_n.jpg", "Sẵn sàng"),
            ("Set áo hai dây tơ tằm chân váy xòe", "Set", "S", "Kem", 250000, 1000000, "https://thuevay.vn/wp-content/uploads/2025/12/IMG_8542-e1764754743347.jpg", "Sẵn sàng"),
            ("Váy body đen cúp ngực quyến rũ", "Váy Body", "L", "Đen", 290000, 1200000, "https://thuevay.vn/wp-content/uploads/2026/01/IMG_1323-667x800.jpg", "Sẵn sàng"),
            ("Váy xòe hồng lệch vai quyến rũ", "Váy Xòe", "M", "Hồng", 270000, 1100000, "https://thuevay.vn/wp-content/uploads/2025/12/486637213_122193607562102890_6066223404235449123_n-1.jpg", "Sẵn sàng"),
            ("Váy body đỏ trễ vai ôm dáng", "Váy Body", "S", "Đỏ", 310000, 1300000, "https://thuevay.vn/wp-content/uploads/2026/01/IMG_0186-667x800.jpg", "Sẵn sàng"),
            ("Áo dài lụa trắng trơn tinh khôi", "Áo Dài", "M", "Trắng", 180000, 800000, "https://thuevay.vn/wp-content/uploads/2024/12/338146273_759679602404017_2943694123853596028_n.jpg", "Sẵn sàng")
        ]
        cursor.executemany('''
        INSERT INTO dresses (name, category, size, color, price, deposit, image_url, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', dresses_data)

        bookings_data = [
            (1, "Nguyễn Thu Thảo", "0982345678", "2026-07-01", "2026-07-03", 1600000, "Đã trả", "Đã thanh toán hết", None, None, None, None, None, 0),
            (2, "Lê Hồng Nhung", "0912345678", "2026-07-07", "2026-07-09", 700000, "Đang thuê", "Đã thanh toán hết", None, None, "2026-07-06", "2026-07-11", "2026-07-06 09:00", 0),
            (3, "Trần Hải Yến", "0332699103", "2026-07-12", "2026-07-14", 600000, "Chờ duyệt", "Đã cọc", "2026-07-12 10:00", None, None, None, None, 0),
            (5, "Phạm Minh Thư", "0966778899", "2026-07-25", "2026-07-26", 400000, "Chờ duyệt", "Đã cọc", "2026-07-25 14:00", None, None, None, None, 0),
        ]
        cursor.executemany('''
        INSERT INTO bookings (dress_id, customer_name, customer_phone, start_date, end_date, total_price, status, payment_status, appointment_datetime, notes, locked_start, locked_end, approved_at, fine_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', bookings_data)

        conn.commit()
        print("[+] Đã khởi tạo SQLite database: rental_shop.db thành công.")
    else:
        conn.commit()
    conn.close()


# ══════════════════════════════════════════════════
# ROUTES – PAGES
# ══════════════════════════════════════════════════

@app.route('/')
def index():
    return redirect('/demo')

@app.route('/demo')
def demo_page():
    return render_template('demo.html')

@app.route('/demo/admin')
def demo_admin_page():
    return render_template('demo_admin.html')


# ══════════════════════════════════════════════════
# API – DRESSES
# ══════════════════════════════════════════════════

@app.route('/api/demo/dresses')
def api_demo_dresses():
    category = request.args.get('category', 'all')
    size = request.args.get('size', 'all')
    conn = _get_conn()
    cursor = conn.cursor()
    query = 'SELECT * FROM dresses WHERE 1=1'
    params = []
    if category != 'all':
        query += ' AND category = ?'
        params.append(category)
    if size != 'all':
        query += ' AND size = ?'
        params.append(size)
    cursor.execute(query, params)
    dresses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(dresses)


@app.route('/api/demo/dresses/<int:dress_id>/availability')
def api_demo_dress_availability(dress_id):
    """Trả về các khoảng ngày bị khóa (locked) của chiếc váy — dùng để disable trong datepicker."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT locked_start, locked_end, start_date, end_date
        FROM bookings
        WHERE dress_id = ?
          AND status IN ('Đã duyệt', 'Đang thuê')
          AND locked_start IS NOT NULL
    ''', (dress_id,))
    rows = cursor.fetchall()
    conn.close()
    blocked = []
    for row in rows:
        blocked.append({
            'from': row['locked_start'],
            'to': row['locked_end'],
            'rental_from': _date_only(row['start_date']),
            'rental_to': _date_only(row['end_date']),
        })
    return jsonify(blocked)


@app.route('/api/demo/proxy-image')
def api_demo_proxy_image():
    url = request.args.get('url', '')
    if not url:
        return '', 400
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://thuevay.vn/'}
        resp = requests.get(url, headers=headers, timeout=8, stream=True)
        if resp.status_code == 200:
            content_type = resp.headers.get('Content-Type', 'image/jpeg')
            return Response(resp.content, content_type=content_type)
        fallback = 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&q=80&w=600'
        resp2 = requests.get(fallback, timeout=8, stream=True)
        return Response(resp2.content, content_type='image/jpeg')
    except Exception:
        return '', 502


# ══════════════════════════════════════════════════
# API – BOOKINGS (CUSTOMER)
# ══════════════════════════════════════════════════

@app.route('/api/demo/bookings', methods=['POST'])
def api_demo_create_booking():
    data = request.json
    dress_id = data.get('dress_id')
    customer_name = data.get('customer_name', '').strip()
    customer_phone = data.get('customer_phone', '').strip()
    start_date = data.get('start_date', '')
    end_date = data.get('end_date', '')
    total_price = data.get('total_price', 0)
    appointment_datetime = data.get('appointment_datetime', '')

    if not all([dress_id, customer_name, customer_phone, start_date, end_date]):
        return jsonify({'success': False, 'message': 'Thiếu thông tin đặt lịch.'}), 400

    conn = _get_conn()
    cursor = conn.cursor()

    # Chỉ block nếu đã có đơn Đã duyệt / Đang thuê trùng lịch buffer
    conflicts = _check_conflicts(cursor, dress_id, start_date, end_date)
    if conflicts:
        conn.close()
        return jsonify({
            'success': False,
            'message': 'Váy này đã được đặt giữ chỗ trong khoảng thời gian bạn chọn. Vui lòng chọn ngày khác hoặc liên hệ cửa hàng.'
        })

    cursor.execute('''
        INSERT INTO bookings
          (dress_id, customer_name, customer_phone, start_date, end_date, total_price, status, payment_status, appointment_datetime)
        VALUES (?, ?, ?, ?, ?, ?, 'Chờ duyệt', 'Chưa cọc', ?)
    ''', (dress_id, customer_name, customer_phone, start_date, end_date, total_price, appointment_datetime or None))

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Yêu cầu giữ chỗ đã được ghi nhận!'})


@app.route('/api/demo/my-bookings')
def api_demo_my_bookings():
    phone = request.args.get('phone', '').strip()
    name = request.args.get('name', '').strip()
    if not phone or not name:
        return jsonify([])
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.*, d.name as dress_name, d.image_url as dress_image, d.price as dress_price
        FROM bookings b
        JOIN dresses d ON b.dress_id = d.id
        WHERE b.customer_phone = ?
        ORDER BY b.start_date DESC
    ''', (phone,))
    raw_bookings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Filter by name case-insensitively in Python to fully support Vietnamese accents
    normalized_input_name = ' '.join(name.lower().split())
    bookings = []
    for b in raw_bookings:
        normalized_db_name = ' '.join(b['customer_name'].lower().split())
        if normalized_db_name == normalized_input_name:
            bookings.append(b)
            
    return jsonify(bookings)


# ══════════════════════════════════════════════════
# API – ADMIN BOOKINGS
# ══════════════════════════════════════════════════

@app.route('/api/demo/admin/bookings')
def api_demo_admin_bookings():
    status_filter = request.args.get('status', '')
    conn = _get_conn()
    cursor = conn.cursor()

    if status_filter:
        cursor.execute('''
            SELECT b.*, d.name as dress_name, d.image_url as dress_image, d.price as dress_price, d.category as dress_category, d.size as dress_size
            FROM bookings b
            JOIN dresses d ON b.dress_id = d.id
            WHERE b.status = ?
            ORDER BY b.start_date ASC
        ''', (status_filter,))
    else:
        cursor.execute('''
            SELECT b.*, d.name as dress_name, d.image_url as dress_image, d.price as dress_price, d.category as dress_category, d.size as dress_size
            FROM bookings b
            JOIN dresses d ON b.dress_id = d.id
            ORDER BY b.start_date ASC
        ''')

    bookings = [dict(row) for row in cursor.fetchall()]

    # Gắn cờ conflict cho mỗi đơn Chờ duyệt
    for b in bookings:
        b['conflicts'] = []
        if b['status'] == 'Chờ duyệt':
            pending = _pending_conflicts(cursor, b['dress_id'], b['start_date'], b['end_date'], exclude_booking_id=b['id'])
            b['conflicts'] = [{'id': r['id'], 'name': r['customer_name']} for r in pending]

    conn.close()
    return jsonify(bookings)


@app.route('/api/demo/admin/bookings/<int:booking_id>/status', methods=['POST'])
def api_demo_update_booking_status(booking_id):
    data = request.json
    new_status = data.get('status')
    payment_status = data.get('payment_status')
    notes = data.get('notes')
    fine_amount = data.get('fine_amount')

    conn = _get_conn()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
    booking = cursor.fetchone()
    if not booking:
        conn.close()
        return jsonify({'success': False, 'message': 'Không tìm thấy đơn đặt.'}), 404

    dress_id = booking['dress_id']
    updates = []
    params = []

    if new_status:
        updates.append('status = ?')
        params.append(new_status)

    if payment_status:
        updates.append('payment_status = ?')
        params.append(payment_status)

    if notes is not None:
        updates.append('notes = ?')
        params.append(notes)

    if fine_amount is not None:
        updates.append('fine_amount = ?')
        params.append(fine_amount)

    # ── Luồng trạng thái ─────────────────────────────────────────
    if new_status == 'Đã duyệt':
        # Khóa lịch buffer khi duyệt
        ls, le = _add_buffer(booking['start_date'], booking['end_date'])
        updates.append('locked_start = ?')
        params.append(ls)
        updates.append('locked_end = ?')
        params.append(le)
        updates.append('approved_at = ?')
        params.append(datetime.now().strftime('%Y-%m-%d %H:%M'))

    elif new_status == 'Đang thuê':
        # Khách đến lấy váy
        cursor.execute("UPDATE dresses SET status = 'Đang thuê' WHERE id = ?", (dress_id,))

    elif new_status == 'Đã trả':
        # Khách trả váy — dress status sẽ được xử lý riêng (giặt/sửa)
        # Dress vẫn giữ status Đang thuê cho đến khi admin xác nhận trạng thái váy
        pass

    elif new_status == 'Đã hủy':
        # Giải phóng lịch buffer
        updates.append('locked_start = ?')
        params.append(None)
        updates.append('locked_end = ?')
        params.append(None)
        # Nếu váy đang thuê cho đơn này thì mở lại
        cursor.execute("SELECT status FROM dresses WHERE id = ?", (dress_id,))
        dr = cursor.fetchone()
        if dr and dr['status'] in ('Đang thuê',):
            cursor.execute("UPDATE dresses SET status = 'Sẵn sàng' WHERE id = ?", (dress_id,))

    if updates:
        params.append(booking_id)
        cursor.execute(f'UPDATE bookings SET {", ".join(updates)} WHERE id = ?', params)

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Cập nhật trạng thái thành công!'})


@app.route('/api/demo/admin/bookings/<int:booking_id>/dress', methods=['PATCH'])
def api_demo_swap_dress(booking_id):
    """Đổi chiếc váy trong đơn Chờ duyệt."""
    data = request.json
    new_dress_id = data.get('dress_id')
    if not new_dress_id:
        return jsonify({'success': False, 'message': 'Thiếu dress_id mới.'}), 400

    conn = _get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM bookings WHERE id = ?", (booking_id,))
    b = cursor.fetchone()
    if not b:
        conn.close()
        return jsonify({'success': False, 'message': 'Không tìm thấy đơn.'}), 404
    if b['status'] != 'Chờ duyệt':
        conn.close()
        return jsonify({'success': False, 'message': 'Chỉ có thể đổi váy khi đơn đang Chờ duyệt.'}), 400

    cursor.execute("UPDATE bookings SET dress_id = ? WHERE id = ?", (new_dress_id, booking_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Đã đổi váy thành công!'})


@app.route('/api/demo/admin/bookings/<int:booking_id>/dress-return', methods=['POST'])
def api_demo_dress_return(booking_id):
    """Xử lý trả váy: bình thường → Đang giặt là; hỏng → Đang sửa chữa + fine."""
    data = request.json
    condition = data.get('condition', 'ok')  # 'ok' | 'damaged'
    fine_amount = data.get('fine_amount', 0)

    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT dress_id FROM bookings WHERE id = ?', (booking_id,))
    b = cursor.fetchone()
    if not b:
        conn.close()
        return jsonify({'success': False, 'message': 'Không tìm thấy đơn.'}), 404

    dress_id = b['dress_id']
    dress_status = 'Đang giặt là' if condition == 'ok' else 'Đang sửa chữa'

    cursor.execute("UPDATE dresses SET status = ? WHERE id = ?", (dress_status, dress_id))
    cursor.execute("UPDATE bookings SET status = 'Đã trả', fine_amount = ? WHERE id = ?", (fine_amount, booking_id))

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f'Váy đã chuyển sang trạng thái: {dress_status}'})


@app.route('/api/demo/admin/dresses/<int:dress_id>/ready', methods=['POST'])
def api_demo_dress_ready(dress_id):
    """Xác nhận váy sẵn sàng sau khi giặt xong hoặc sửa xong."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE dresses SET status = 'Sẵn sàng' WHERE id = ?", (dress_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Váy đã sẵn sàng cho thuê!'})


# ══════════════════════════════════════════════════
# API – ADMIN STATS
# ══════════════════════════════════════════════════

@app.route('/api/demo/admin/stats')
def api_demo_admin_stats():
    conn = _get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(total_price) FROM bookings WHERE status = 'Đã trả'")
    total_rev = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'Chờ duyệt'")
    pending_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status IN ('Đã duyệt', 'Đang thuê')")
    active_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM dresses WHERE status = 'Sẵn sàng'")
    available_dresses = cursor.fetchone()[0] or 0

    chart_data = {
        'labels': ['Tháng 5', 'Tháng 6', 'Tháng 7'],
        'data': [4500000, 7200000, total_rev]
    }

    conn.close()
    return jsonify({
        'total_revenue': total_rev,
        'pending_bookings': pending_count,
        'active_bookings': active_count,
        'available_dresses': available_dresses,
        'chart_data': chart_data
    })


# ══════════════════════════════════════════════════
# API – ADMIN DRESSES
# ══════════════════════════════════════════════════

@app.route('/api/demo/admin/dresses', methods=['POST'])
def api_demo_add_dress():
    name = request.form.get('name')
    category = request.form.get('category')
    size = request.form.get('size')
    color = request.form.get('color')
    price = request.form.get('price')
    deposit = request.form.get('deposit')

    if not all([name, category, size, color, price, deposit]):
        return jsonify({'success': False, 'message': 'Thiếu thông tin váy.'}), 400

    image_file = request.files.get('image')
    image_url = 'https://images.unsplash.com/photo-1594552072238-b8a33785b261?auto=format&fit=crop&q=80&w=600'

    if image_file and image_file.filename:
        filename = secure_filename(image_file.filename)
        filename_parts = os.path.splitext(filename)
        filename = f"{filename_parts[0]}_{int(time.time())}{filename_parts[1]}"
        save_dir = os.path.join('static', 'uploads')
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, filename)
        image_file.save(filepath)
        image_url = f"/static/uploads/{filename}"

    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO dresses (name, category, size, color, price, deposit, image_url, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Sẵn sàng')
    ''', (name, category, size, color, int(price), int(deposit), image_url))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Thêm váy mới thành công!'})


@app.route('/api/demo/admin/dresses/<int:dress_id>', methods=['DELETE'])
def api_demo_delete_dress(dress_id):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE dress_id = ? AND status = 'Đang thuê'", (dress_id,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        return jsonify({'success': False, 'message': 'Không thể xóa váy đang trong quá trình cho thuê.'}), 400
    cursor.execute('DELETE FROM dresses WHERE id = ?', (dress_id,))
    cursor.execute("DELETE FROM bookings WHERE dress_id = ? AND status NOT IN ('Đang thuê')", (dress_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Đã xóa váy thành công!'})


# ══════════════════════════════════════════════════
# STARTUP
# ══════════════════════════════════════════════════

init_db_if_not_exists()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
