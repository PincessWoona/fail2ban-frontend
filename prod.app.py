from flask import Flask, jsonify, render_template_string
import subprocess
from datetime import datetime
import geoip2.database
import os

app = Flask(__name__)

# Загрузите базу данных GeoLite2 для определения стран
geoip_db_path = "./GeoLite2-Country.mmdb"
if not os.path.exists(geoip_db_path):
    raise FileNotFoundError("Файл базы данных GeoLite2-Country.mmdb не найден. Скачайте его и поместите в ту же папку.")

# Подключаемся к базе данных GeoLite2
geoip_reader = geoip2.database.Reader(geoip_db_path)

# Храним заблокированные IP-адреса и страны
banned_ips_dict = {}

# Функция для получения страны по IP
def get_country(ip):
    try:
        response = geoip_reader.country(ip)
        return response.country.iso_code
    except geoip2.errors.AddressNotFoundError:
        return "Unknown"

# Функция для получения и обновления заблокированных IP-адресов с флагами стран
def update_banned_ips():
    try:
        output = subprocess.check_output(['fail2ban-client', 'status', 'sshd'], universal_newlines=True)
        new_banned_ips = []
        
        for line in output.splitlines():
            if "Banned IP list" in line:
                ip_list = line.split(':')[1].strip().split()
                for ip in ip_list:
                    # Проверяем, если IP новый, добавляем его с кодом страны
                    if ip not in banned_ips_dict:
                        country_code = get_country(ip)
                        banned_ips_dict[ip] = country_code
                    # Добавляем IP и страну в список для отображения
                    new_banned_ips.append((ip, banned_ips_dict[ip]))
        
        return new_banned_ips

    except subprocess.CalledProcessError as e:
        print("Ошибка при выполнении команды fail2ban-client:", e)
    return []

# Основная HTML-страница с Bootstrap
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
	    <!-- By DarkShy -->
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fail2Ban Banned IPs</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <script>
            async function fetchBannedIPs() {
                try {
                    const response = await fetch('/api/banned_ips');
                    const data = await response.json();
                    const tableBody = document.getElementById('ipTableBody');
                    const countryTableBody = document.getElementById('countryTableBody');
                    tableBody.innerHTML = '';
                    countryTableBody.innerHTML = '';

                    const countryCounts = {};
                    data.banned_ips.forEach(item => {
                        const row = document.createElement('tr');
                        const cellIp = document.createElement('td');
                        const cellCountry = document.createElement('td');
                        const flagIcon = document.createElement('img');

                        cellIp.textContent = item[0];
                        flagIcon.src = "https://flagcdn.com/16x12/" + item[1].toLowerCase() + ".png";
                        flagIcon.alt = item[1];
                        flagIcon.className = "mr-2";
                        cellCountry.appendChild(flagIcon);
                        cellCountry.appendChild(document.createTextNode(item[1]));

                        row.appendChild(cellIp);
                        row.appendChild(cellCountry);
                        tableBody.appendChild(row);

                        // Подсчёт количества IP по странам
                        countryCounts[item[1]] = (countryCounts[item[1]] || 0) + 1;
                    });

                    // Сортируем страны по количеству блокировок
                    const sortedCountries = Object.entries(countryCounts)
                        .sort((a, b) => b[1] - a[1]);

                    // Заполняем таблицу топ стран блокировок
                    sortedCountries.forEach(([country, count]) => {
                        const row = document.createElement('tr');
                        const cellCountry = document.createElement('td');
                        const cellCount = document.createElement('td');
                        const flagIcon = document.createElement('img');

                        flagIcon.src = "https://flagcdn.com/16x12/" + country.toLowerCase() + ".png";
                        flagIcon.alt = country;
                        flagIcon.className = "mr-2";

                        cellCountry.appendChild(flagIcon);
                        cellCountry.appendChild(document.createTextNode(country));
                        cellCount.textContent = count;

                        row.appendChild(cellCountry);
                        row.appendChild(cellCount);
                        countryTableBody.appendChild(row);
                    });
                } catch (error) {
                    console.error('Error fetching banned IPs:', error);
                }
            }

            // Обновляем список IP и таблицу топ стран каждые 5 секунд
            setInterval(fetchBannedIPs, 5000);
            window.onload = fetchBannedIPs;
        </script>
    </head>
    <body>
        <div class="container my-4">
            <h1 class="text-center">Заблокированные IP-адреса (Fail2Ban)</h1>
            <table class="table table-striped table-bordered mt-4">
                <thead class="thead-dark">
                    <tr>
                        <th>IP-адрес</th>
                        <th>Страна</th>
                    </tr>
                </thead>
                <tbody id="ipTableBody">
                    <!-- Список IP будет добавляться здесь через JavaScript -->
                </tbody>
            </table>
            <h3 class="text-center mt-5">Топ стран блокировок</h3>
            <table class="table table-striped table-bordered mt-4">
                <thead class="thead-dark">
                    <tr>
                        <th>Страна</th>
                        <th>Количество блокировок</th>
                    </tr>
                </thead>
                <tbody id="countryTableBody">
                    <!-- Топ стран блокировок будет добавляться здесь через JavaScript -->
                </tbody>
            </table>
        </div>
        <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    </body>
    </html>
    ''')

# API для получения заблокированных IP в формате JSON
@app.route('/api/banned_ips')
def banned_ips():
    banned_ips = update_banned_ips()
    return jsonify({'banned_ips': banned_ips})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
