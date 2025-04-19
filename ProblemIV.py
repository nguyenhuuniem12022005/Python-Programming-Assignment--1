from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fuzzywuzzy import fuzz, process
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return driver
    except Exception as e:
        print(f"Error setting up driver: {e}")
        return None


def clean_player_name(name):
    """Chuẩn hóa tên cầu thủ để so sánh, xử lý cả trường hợp tên bị đảo ngược"""
    if pd.isna(name):
        return ""

    # Lấy phần trước \n đầu tiên
    name = str(name).split('\n')[0].strip()

    # Xóa các ký tự đặc biệt (giữ lại khoảng trắng, gạch ngang)
    name = ''.join(e for e in name if e.isalpha() or e in [' ', '-'])

    # Chuyển về chữ thường
    name = name.lower()

    # Xử lý đặc biệt cho một số cầu thủ
    special_cases = {
        'son heung-min': 'heung min son',
        'heung-min son': 'heung min son',
        'joao cancelo': 'cancelo joao',
        # Thêm các trường hợp đặc biệt khác nếu cần
    }

    if name in special_cases:
        return special_cases[name]

    # Tách các từ trong tên và sắp xếp theo thứ tự alphabet
    sorted_name = ' '.join(sorted(name.split()))

    return sorted_name


def scrape_all_pages(total_pages=22):
    all_players = []
    all_etvs = []

    driver = setup_driver()
    if not driver:
        return pd.DataFrame()

    try:
        for page in range(1, total_pages + 1):
            url = f"https://www.footballtransfers.com/us/values/players/most-valuable-soccer-players/playing-in-uk-premier-league/{page}"
            print(f"\nScraping page {page}: {url}")

            try:
                driver.get(url)
                print("Page loaded, waiting for content...")

                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "table.table--player-valuations")))
                    print("Table found")
                except:
                    print("Table not found, trying alternative approach")
                    time.sleep(5)

                rows = []
                try:
                    rows = driver.find_elements(By.CSS_SELECTOR, "table.table--player-valuations tbody tr")
                    if not rows:
                        rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
                except:
                    print("Could not find table rows")
                    continue

                for row in rows:
                    try:
                        if "table-placeholder" in row.get_attribute("class"):
                            continue

                        player_name = ""
                        try:
                            player_name = row.find_element(By.CSS_SELECTOR, ".player-name").text.strip()
                        except:
                            try:
                                player_name = row.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text.strip()
                            except:
                                continue

                        etv_value = ""
                        try:
                            etv_value = row.find_element(By.CSS_SELECTOR, ".player-value").text.strip()
                        except:
                            try:
                                etv_value = row.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text.strip()
                            except:
                                continue

                        if player_name and etv_value:
                            all_players.append(player_name)
                            all_etvs.append(etv_value)

                    except Exception as e:
                        print(f"Error processing row: {e}")
                        continue

                print(f"Found {len(rows)} rows on page {page}")
                time.sleep(2)

            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                continue

        print(f"\nTotal players scraped: {len(all_players)}")
        return pd.DataFrame({'Player': all_players, 'ETV': all_etvs})

    except Exception as e:
        print(f"Error during scraping: {e}")
        return pd.DataFrame()
    finally:
        driver.quit()


def prepare_local_data(csv_path='result.csv'):
    try:
        # Đọc file CSV và chỉ giữ lại các cột cần thiết
        local_df = pd.read_csv(csv_path)
        columns_to_keep = ['Player', 'Nation', 'Squad', 'Age', 'Position']

        # Kiểm tra xem các cột có tồn tại trong dataframe không
        existing_columns = [col for col in columns_to_keep if col in local_df.columns]
        local_df = local_df[existing_columns]

        # Tạo cột Clean_Name để so sánh (đã sắp xếp các từ)
        local_df['Clean_Name'] = local_df['Player'].apply(clean_player_name)

        return local_df
    except Exception as e:
        print(f"Error preparing local data: {e}")
        return pd.DataFrame()


def manually_assign_etv(df):
    """
    Gán giá trị ETV thủ công cho các cầu thủ còn thiếu ETV
    """
    if df.empty or 'ETV' not in df.columns:
        return df

    df_filled = df.copy()

    manual_etv_mapping = {

        'Adam Armstrong': '€17.7M',
        'Alphonse Areola' :'€11.6M',
        'Arijanet Muric':'€10.4M',
        'Idrissa Gana Gueye':'€4.5M',
        'Igor' : '€25M',
        'Ismaila Sarr':'€24.9M',
        'Jeremy Doku':'€66.5M',
        'Jurriën Timber':'€62.7M',
        'Kyle Walker':'€4.9M',
        'Mads Roerslev':'€8.4M',
        'Manuel Ugarte Ribeiro':'€60.3M',
        'Mario Lemina':'€5.2M',
        'Milos Kerkez':'€61.6M',
        'Omari Hutchinson':'€27.6M',
        'Radu Drăgușin':'€28.4M',
        'Rasmus Højlund':'€60M',
        'Rayan Aït-Nouri':'€44M',
        'Victor Bernth Kristiansen':'€23.9M'
    }

    # Chuẩn hóa tên trong mapping
    normalized_mapping = {clean_player_name(k): v for k, v in manual_etv_mapping.items()}

    # Điền giá trị ETV thiếu
    for idx, row in df_filled.iterrows():
        if pd.isna(row['ETV']):
            clean_name = clean_player_name(row['Player'])
            if clean_name in normalized_mapping:
                df_filled.at[idx, 'ETV'] = normalized_mapping[clean_name]
                print(f"Đã gán thủ công ETV cho {row['Player']}: {normalized_mapping[clean_name]}")

    return df_filled




def merge_data(local_df, scraped_df):
    if local_df.empty or scraped_df.empty:
        return pd.DataFrame()

    # Chuẩn hóa tên ở dữ liệu scraped (đã sắp xếp các từ)
    scraped_df['Clean_Name'] = scraped_df['Player'].apply(clean_player_name)

    # Debug: In ra 5 tên đầu tiên từ mỗi nguồn
    print("\nSample local names:", local_df['Clean_Name'].head().tolist())
    print("Sample scraped names:", scraped_df['Clean_Name'].head().tolist())

    # Merge dữ liệu
    merged_df = pd.merge(
        local_df,
        scraped_df[['Clean_Name', 'ETV']],
        on='Clean_Name',
        how='left'
    )

    # Xóa cột Clean_Name không cần thiết
    merged_df = merged_df.drop('Clean_Name', axis=1)

    # Sắp xếp lại cột ETV lên sau cột Player
    cols = merged_df.columns.tolist()
    cols = [cols[0]] + [cols[-1]] + cols[1:-1]
    merged_df = merged_df[cols]

    return merged_df


def main():
    print("Preparing local data...")
    local_data = prepare_local_data()

    if local_data.empty:
        print("Failed to load local data. Exiting.")
        return

    print("\nStarting web scraping for all pages...")
    scraped_data = scrape_all_pages(total_pages=22)

    if not scraped_data.empty:
        print("\nMerging data...")
        final_df = merge_data(local_data, scraped_data)

        if not final_df.empty:
            # Gán ETV thủ công trước
            final_df = manually_assign_etv(final_df)



            print("\nFinal Merged Data (first 5 rows):")
            print(final_df.head())

            output_file = 'final_players_with_etv.csv'
            final_df.to_csv(output_file, index=False)
            print(f"\nData saved to '{output_file}'")

            # Thống kê kết quả
            matched_count = final_df['ETV'].notna().sum()
            total_count = len(final_df)
            print(
                f"\nMatching results: {matched_count}/{total_count} players matched ({matched_count / total_count:.1%})")
        else:
            print("\nNo matching players found between sources.")
    else:
        print("\nFailed to scrape data or no data found.")


if __name__ == "__main__":
    main()