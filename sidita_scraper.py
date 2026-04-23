import requests
from bs4 import BeautifulSoup
import csv

# URL situs SIDITA Jatim
sidita_url = "https://sidita.disbudpar.jatimprov.go.id/destinasi/list"

# Fungsi untuk mengambil data dari SIDITA Jatim
def scrape_sidita_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Menemukan tabel dan baris data
    table = soup.find('table')  # Pastikan elemen tabel yang benar ditemukan
    rows = table.find_all('tr')

    destinations = []
    for row in rows[1:]:  # Melewati header tabel
        cols = row.find_all('td')
        data = [col.text.strip() for col in cols]
        if len(data) >= 3:  # Pastikan kolom data memiliki cukup elemen
            destinations.append({
                'No': data[0],
                'Kabupaten/Kota': data[1],
                'Nama Destinasi': data[2]
            })
    return destinations

# Simpan data ke file CSV
def save_sidita_to_csv(destinations):
    with open('sidita_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['No', 'Kabupaten/Kota', 'Nama Destinasi'])
        for dest in destinations:
            writer.writerow([dest['No'], dest['Kabupaten/Kota'], dest['Nama Destinasi']])

# Proses scraping SIDITA
def main_sidita():
    print("Mengambil data dari SIDITA Jatim...")
    destinations = scrape_sidita_data(sidita_url)
    save_sidita_to_csv(destinations)
    print("Data SIDITA berhasil disimpan ke sidita_data.csv")

if __name__ == "__main__":
    main_sidita()
