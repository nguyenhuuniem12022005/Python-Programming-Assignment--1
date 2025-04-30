import pandas as pd

# Đọc dữ liệu từ các file CSV
df_etv = pd.read_csv('final_players_with_etv.csv')  # File chứa cột 'etv'
df_results = pd.read_csv('results.csv')  # File chứa kết quả

# Giả sử bạn có cột chung 'player_id' hoặc 'player_name' giữa hai file
# Hãy thay 'Player' bằng cột chung của bạn (nếu có)
df_merged = pd.merge(df_results, df_etv[['Player', 'ETV']], on='Player', how='inner')

# Lưu kết quả vào file CSV mới
df_merged.to_csv('results_with_etv.csv', index=False)

print("Cột 'etv' đã được thêm vào và lưu thành công vào 'results_with_etv.csv'.")
