# Tái lập thực nghiệm The Scene Language

Chạy lại phần sinh cảnh 3D từ văn bản của bài báo *The Scene Language:
Representing Scenes with Programs, Words, and Embeddings* (CVPR 2025), dùng mã
nguồn tác giả tại [zzyunzhi/scene-language](https://github.com/zzyunzhi/scene-language).

Repo này không cài đặt lại pipeline. Nó gọi `scripts/run.py` của tác giả với
model và tham số cố định, rồi lập bảng từ thư mục đầu ra. Chỉ số đo là số
lượng đối tượng (Count) trên 6 prompt có số lượng tường minh, mỗi prompt 4 mẫu.

## Môi trường

| | |
|---|---|
| Python | 3.12 |
| Hệ điều hành đã chạy | Windows 11, CPU, không cần GPU |
| Model | `claude-sonnet-4-6` (model của bài báo đã ngừng phục vụ, xem `config.py`) |
| Khóa API | Anthropic |

## Cài đặt

```bash
git clone https://github.com/zzyunzhi/scene-language.git
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate

pip install -e ./scene-language -r requirements.txt
cd scene-language && git apply ../patches/scene-language.patch && cd ..
```

`requirements.txt` ghim ba gói mà bản mới nhất không còn chạy được với mã tác
giả: `mitsuba<3.6`, `anthropic<1`, và thêm `opencv-python` vì repo tác giả
import mà không khai báo.

`patches/scene-language.patch` sửa bốn chỗ nhỏ trong repo tác giả để chạy
được trên Windows và numpy 2: lệnh render dạng `VAR=x python ...`, đường dẫn
đầu ra dài quá 260 ký tự, ghi cache bằng `os.rename`, và `transforms3d` nhận
list thay vì ndarray. Trên Linux hai sửa đầu không có tác dụng gì.

Khóa API ghi vào repo tác giả (file này nằm trong `.gitignore` của họ):

```powershell
Set-Content -Encoding utf8 scene-language\engine\key.py "ANTHROPIC_API_KEY = 'sk-ant-...'"
```

Kiểm tra cài đặt:

```bash
cd scene-language && python scripts/tests/test_basic.py && cd ..
```

## Chạy

```bash
python run_experiments.py --repo ./scene-language --dry-run   # chỉ in lệnh
python run_experiments.py --repo ./scene-language             # ~10 phút, 24 lần gọi API
python analyze.py --repo ./scene-language                     # lập bảng
python analyze.py --repo ./scene-language --wandb             # đẩy lên W&B, cần wandb login
```

Hoặc mở `notebooks/colab_runner.ipynb` trên Colab, chạy lần lượt các ô.

## Chấm số lượng

Số lượng đối tượng không đọc tự động được từ chương trình sinh ra, vì model
biểu đạt con số theo nhiều cách (hằng trong `loop()`, biến `num_x = 8`, danh
sách `[5,4,3,2,1]`, hai `range()` lồng nhau). `analyze.py` chỉ trích các con
số bắt được vào cột `numbers_seen`; cột `count_correct` lấy từ
`results/manual_grading.csv`, ghi bằng tay sau khi đọc `program.py` và xem
ảnh render của từng mẫu.

## Tệp

| Tệp | Việc |
|---|---|
| `config.py` | Bộ prompt, model, tham số lấy mẫu |
| `run_experiments.py` | Gọi `scripts/run.py` của tác giả, ghi `results/run_log.csv` |
| `analyze.py` | Quét đầu ra, ghi `results/results.csv`, đẩy W&B |
| `patches/scene-language.patch` | Sửa đổi áp lên repo tác giả |
| `results/manual_grading.csv` | Bảng chấm tay 24 mẫu |
| `notebooks/colab_runner.ipynb` | Bản chạy trên Colab |

Đầu ra của tác giả (chương trình, ảnh render) nằm trong
`scene-language/scripts/outputs/run_*/<scene>_*/<i>/`, không commit lên đây.
