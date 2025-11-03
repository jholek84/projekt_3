import sys
import csv
from typing import List, Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup as BS

BASE_URL = "https://volby.cz/pls/ps2017nss/"


def clean_num(text: str) -> int:
    # odstranění mezer
    if text is None:
        return 0
    try:
        return int(text.replace('\xa0', '').strip())
    except ValueError:
        return 0


def get_html(url: str) -> Optional[BS]:
    # stáhne HTML stránku z volby.cz
    # User-Agent je nutný k obcházení filtrace serveru - dohledáno z intenetu
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Scraper)'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        r.encoding = 'cp1250'  # Správné kódování pro volby.cz
        return BS(r.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f" Chyba při stahování {url}: {e}")
        return None


def check_args(args: List[str]) -> bool:
    # kontrola zadaných argumentů podle zadání
    if len(args) != 3:
        print(" Chyba: Můj program vyžaduje přesně 2 argumenty: URL a název souboru.")
        return False
    elif BASE_URL not in args[1]:
        print(" Chyba: První argument musí být URL z domény volby.cz (ps2017nss/).")
        return False
    elif "https" in args[2]:
        print(" Chyba: Druhý argument musí být název souboru, ne URL.")
        return False
    return True


def get_town_code(soup: BS) -> List[str]:
    # vrací kódy obcí z hlavní stránky okresu
    codes = soup.find_all("td", attrs={"headers": "t1sa1 t1sb1"})
    codes.extend(soup.find_all("td", attrs={"headers": "t2sa1 t2sb1"}))
    codes.extend(soup.find_all("td", attrs={"headers": "t3sa1 t3sb1"}))
    return [code.text for code in codes]


def get_town_names(soup: BS) -> List[str]:
    # vrací názvy obcí z hlavní stránky okresu
    names = soup.find_all("td", attrs={"headers": "t1sa1 t1sb2"})
    names.extend(soup.find_all("td", attrs={"headers": "t2sa1 t2sb2"}))
    names.extend(soup.find_all("td", attrs={"headers": "t3sa1 t3sb2"}))
    return [name.text for name in names]


def get_town_urls(soup: BS) -> List[str]:
    # vrací URL odkazující na detaily obcí (ps311)
    urls = []
    # Prochází všechny odkazy na stránce
    for elem in soup.find_all("a"):
        href = elem.get('href', '')
        # Kontroluje, zda odkaz vede na stránku obce
        if 'ps311' in href:
            # skládá kompletní URL z domény a relativní cesty (href) - 
            urls.append(BASE_URL + href)
    return urls


def get_parties_names() -> List[str]:
    # stahuje data z ukázkové obce a vrátí seznam názvů politických stran (bez 'Celkem')
    parties_url = BASE_URL + "ps311?xjazyk=CZ&xkraj=12&xobec=589268&xvyber=7103"
    parties_soup = get_html(parties_url)
    if not parties_soup: return []
    names = parties_soup.find_all("td", attrs={"headers": "t1sa1 t1sb2"})
    names.extend(parties_soup.find_all("td", attrs={"headers": "t2sa1 t2sb2"}))
    return [name.text.strip() for name in names][:-1]


def total_votes(soup: BS) -> List[int]:
    # získává hodnoty voličů, obálek a platných hlasů
    cisla = soup.find_all("td", attrs={"class": "cislo"})
    if len(cisla) < 7: return [0, 0, 0]
    return [clean_num(cisla[2].text), clean_num(cisla[3].text), clean_num(cisla[6].text)]


def get_party_votes(soup: BS) -> List[int]:
    # získává počty hlasů pro každou stranu (bez 'Celkem')
    votes = soup.find_all("td", attrs={"headers": "t1sa2 t1sb3"})
    votes.extend(soup.find_all("td", attrs={"headers": "t2sa2 t2sb3"}))
    return [clean_num(vote.text) for vote in votes][:-1]


def create_file_header(file_name: str, party_names: List[str]) -> None:
    # vytváří hlavičku CSV souboru
    header = ["Town Code", "Town Name", "Registered", "Envelopes", "Valid votes"] + party_names
    with open(file_name, "w", newline="", encoding='utf-8') as f:
        csv.writer(f).writerow(header)


def write_votes(file_name: str, data: List[list]) -> None:
    # zapisuje řádky s daty do CSV souboru
    with open(file_name, "a+", newline="", encoding='utf-8') as f:
        csv.writer(f).writerows(data)


def main():
    if not check_args(sys.argv):
        sys.exit(1)
    url, file_name = sys.argv[1], sys.argv[2]

    print(f"Downloading data from your url: {url}")
    print(f"Saving data in file: {file_name}")

    main_soup = get_html(url)
    if not main_soup: sys.exit(1)

    party_names = get_parties_names()
    if not party_names: sys.exit(1)

    create_file_header(file_name, party_names)

    codes, names, urls = get_town_code(main_soup), get_town_names(main_soup), get_town_urls(main_soup)

    if not urls:
        print(" Chyba: Na stránce nebyly nalezeny žádné odkazy na obce (ps311). Zkontrolujte URL.")
        sys.exit(1)

    print(f" Nalezeno obcí: {len(urls)}. Spouštím sběr dat...")

    min_len = min(len(urls), len(codes), len(names))

    for i in range(min_len):
        soup_obec = get_html(urls[i])
        if not soup_obec: continue

        row_data = [codes[i], names[i]] + total_votes(soup_obec) + get_party_votes(soup_obec)

        if len(row_data) != 5 + len(party_names):
            print(f" Varování: Obec {names[i]} má nesprávný počet sloupců. Přeskočeno.")
            continue

        write_votes(file_name, [row_data])

    print(f"Your file {file_name} was created. Enjoy. Exiting program.")


if __name__ == "__main__":
    main()
