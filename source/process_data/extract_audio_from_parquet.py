"""
extract_audio_from_parquet.py — Tách audio từ parquet file thành folder samples.

Chuyển đổi:
    Parquet file (audio bytes nén)  →  Folder structure (file WAV thực sự)

Input:
    - parquet file với cột: label (species), audio (bytes)

Output:
    Folder structure:
    data/samples/
    ├── Species_Name_1/
    │   ├── file_001.wav
    │   ├── file_002.wav
    │   └── ...
    ├── Species_Name_2/
    └── ...

Cách chạy:
    python source/extract_audio_from_parquet.py \\
        --parquet data/index.parquet \\
        --output data/samples
        
    python source/extract_audio_from_parquet.py \\
        --parquet data/test.parquet \\
        --output data/test_samples
"""

import argparse
import os
from pathlib import Path

import pandas as pd
from tqdm import tqdm


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Làm sạch tên file: bỏ special characters, replace spaces.
    
    Ví dụ:
        "Bird Song (2024).wav" → "Bird_Song_2024.wav"
    """
    # Replace spaces và special chars bằng underscore
    filename = filename.replace(" ", "_").replace("(", "").replace(")", "")
    # Bỏ các ký tự không an toàn cho filesystem
    unsafe_chars = '<>:"|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, "")
    # Giới hạn độ dài
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    return filename


def extract_audio_from_parquet(
    parquet_path: str,
    output_dir: str = "data/samples",
    file_prefix: str = "bird",
):
    """
    Parse parquet file → tách audio bytes thành folder samples.
    
    Args:
        parquet_path: Đường dẫn đến .parquet file
        output_dir: Thư mục output (tạo mới nếu không tồn tại)
        file_prefix: Prefix cho tên file (default: "bird", output: bird_001.wav, bird_002.wav, ...)
    """
    # ─── Kiểm tra file input ──────────────────────────────────────────────
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
    print(f"\n🔄 Loading parquet: {parquet_path}")
    
    # ─── Load parquet ─────────────────────────────────────────────────────
    try:
        df = pd.read_parquet(parquet_path)
    except Exception as e:
        print(f"❌ Error loading parquet: {e}")
        return
    
    print(f"   Loaded {len(df)} records with columns: {list(df.columns)}")
    
    # ─── Kiểm tra cột cần thiết ────────────────────────────────────────────
    if "label" not in df.columns:
        raise ValueError("Parquet must have 'label' column (species name)")
    if "audio" not in df.columns:
        raise ValueError("Parquet must have 'audio' column (audio bytes)")
    
    # ─── Tạo output directory ─────────────────────────────────────────────
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"   Output directory: {output_path}")
    
    # ─── Tách audio từ parquet ────────────────────────────────────────────
    species_count = {}  # {species: count}
    total_files = 0
    
    print(f"\n📦 Extracting audio files...")
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        species = str(row["label"]).strip()
        audio_data = row["audio"]
        
        # ──► Extract bytes từ audio column
        # Audio có thể ở 2 format:
        #   1. Dict với key 'bytes': {'bytes': b'...'}
        #   2. Trực tiếp bytes: b'...'
        if isinstance(audio_data, dict):
            if "bytes" in audio_data:
                audio_bytes = audio_data["bytes"]
            else:
                print(f"   ⚠️  Row {idx}: audio dict không có key 'bytes', skip")
                continue
        elif isinstance(audio_data, bytes):
            audio_bytes = audio_data
        else:
            print(f"   ⚠️  Row {idx}: audio type không nhận diện ({type(audio_data)}), skip")
            continue
        
        # ──► Tạo species folder
        species_dir = output_path / sanitize_filename(species)
        species_dir.mkdir(parents=True, exist_ok=True)
        
        # ──► Đếm file trong loài này (để tạo tên file tuần tự)
        if species not in species_count:
            species_count[species] = 0
        species_count[species] += 1
        file_num = species_count[species]
        
        # ──► Tên file: {prefix}_{species}_{number:03d}.wav
        filename = f"{file_prefix}_{file_num:03d}.wav"
        filepath = species_dir / filename
        
        # ──► Write audio bytes to file
        try:
            with open(filepath, "wb") as f:
                f.write(audio_bytes)
            total_files += 1
        except Exception as e:
            print(f"   ❌ Error saving {filepath}: {e}")
            continue
    
    # ─── Báo cáo kết quả ───────────────────────────────────────────────────
    print(f"\n✅ Extraction complete!")
    print(f"   Total files: {total_files}")
    print(f"   Species: {len(species_count)}")
    print(f"\n📊 Files per species:")
    for species in sorted(species_count.keys()):
        count = species_count[species]
        species_dir = output_path / sanitize_filename(species)
        actual_files = len(list(species_dir.glob("*.wav")))
        status = "✅" if actual_files == count else "⚠️"
        print(f"   {status} {species:<40s} {actual_files} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract audio from parquet file to samples folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python source/extract_audio_from_parquet.py \\
      --parquet data/index.parquet \\
      --output data/samples
      
  python source/extract_audio_from_parquet.py \\
      --parquet data/test.parquet \\
      --output data/test_samples \\
      --prefix test_bird
        """
    )
    
    parser.add_argument(
        "--parquet",
        type=str,
        required=True,
        help="Path to input parquet file (with 'label' and 'audio' columns)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/samples",
        help="Output directory for extracted WAV files (default: data/samples)"
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="bird",
        help="Prefix for output filenames (default: bird → bird_001.wav, bird_002.wav, ...)"
    )
    
    args = parser.parse_args()
    
    try:
        extract_audio_from_parquet(
            parquet_path=args.parquet,
            output_dir=args.output,
            file_prefix=args.prefix,
        )
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
