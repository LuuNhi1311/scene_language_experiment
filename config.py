"""Cấu hình thí nghiệm. Các script khác đều đọc từ đây."""

# Bài báo dùng claude-3-5-sonnet-20240620. Model này và model mặc định của repo
# tác giả (claude-3-7-sonnet-20250219) đều đã ngừng phục vụ (404, kiểm tra
# 04/11/2026). Dùng model gần nhất còn gọi được.
MODEL = "claude-sonnet-4-6"

# Giữ đúng mặc định của scripts/run.py bên repo tác giả
NUM_COMPLETIONS = 4
TEMPERATURE = 0.2

# Prompt có số lượng tường minh, dùng để kiểm chỉ số Count.
# key: chuỗi nhận ra thư mục cảnh trong đầu ra. expect: số đối tượng cần đúng.
PROMPTS = [
    {"key": "coke",       "expect": 15, "text": "15 coke cans stacking in a pyramid"},
    {"key": "shelf",      "expect": 8,  "text": "a shelf with 8 layers"},
    {"key": "moai",       "expect": 7,  "text": "seven moai statues standing in a row, all facing the same direction"},
    {"key": "chessboard", "expect": 32, "text": "a chessboard with a full set of chess pieces"},
    {"key": "Sudoku",     "expect": 81, "text": "A 9x9 Sudoku board partially filled with numbers"},
    {"key": "Ferris",     "expect": 12, "text": "a Ferris wheel with 12 cabins"},
]

WANDB_PROJECT = "scene-language-reproduction"
