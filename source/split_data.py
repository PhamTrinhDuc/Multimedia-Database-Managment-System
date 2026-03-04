"""
split_data.py — Tách dataset thành 2 phần:
  - data/index.parquet : 15 loài dùng để indexing vào database (offline)
  - data/test.parquet  : 5 loài dùng để test hệ thống retrieval (online)

Cách chạy:
    python source/split_data.py
    python source/split_data.py --data data/0000.parquet --n-test 5 --seed 42
    python source/split_data.py --test-species "Turdus merula" "Parus major"  # chỉ định tay
"""

import argparse
import os
import random

import pandas as pd


def split_by_species(
    data_path: str,
    n_test_species: int = 5,
    test_species: list[str] | None = None,
    out_index: str = "/home/ducpham/workspace/PTIT-CSDLDPT/data/index.parquet",
    out_test: str = "/home/ducpham/workspace/PTIT-CSDLDPT/data/test.parquet",
    seed: int = 42,
):
    """
    Chia dataset theo loài (species-level split):
      - Index set : toàn bộ records của 15 loài được chọn làm DB
      - Test set  : toàn bộ records của 5 loài còn lại

    Species-level split quan trọng hơn record-level split vì:
    - Kiểm tra được cả 2 case: loài ĐÃ có trong DB (15 loài) và CHƯA có (5 loài)
    - Tránh data leakage (cùng con chim vừa train vừa test)
    """
    # ----- Load -----
    print(f"Loading '{data_path}' ...")
    df = pd.read_parquet(data_path)
    all_species = sorted(df["label"].unique().tolist())
    n_total = len(all_species)
    print(f"  Total records : {len(df)}")
    print(f"  Total species : {n_total}")
    for i, sp in enumerate(all_species):
        cnt = (df["label"] == sp).sum()
        print(f"    {i+1:2d}. {sp:<35s} {cnt} records")

    # ----- Chọn test species -----
    if test_species:
        # Kiểm tra tên hợp lệ
        invalid = [s for s in test_species if s not in all_species]
        if invalid:
            raise ValueError(f"Các loài không tồn tại trong dataset: {invalid}")
        test_species = list(test_species)
    else:
        if n_test_species >= n_total:
            raise ValueError(
                f"n_test_species={n_test_species} >= tổng số loài={n_total}. "
                "Phải để lại ít nhất 1 loài cho index set."
            )
        random.seed(seed)
        test_species = sorted(random.sample(all_species, n_test_species))

    index_species = sorted([s for s in all_species if s not in test_species])

    # ----- Split -----
    df_index = df[df["label"].isin(index_species)].reset_index(drop=True)
    df_test  = df[df["label"].isin(test_species)].reset_index(drop=True)

    # ----- Save -----
    os.makedirs(os.path.dirname(out_index), exist_ok=True)
    df_index.to_parquet(out_index, index=False)
    df_test.to_parquet(out_test, index=False)

    # ----- Report -----
    print(f"\n{'─'*55}")
    print(f"  INDEX SET  →  '{out_index}'")
    print(f"  {len(index_species)} species, {len(df_index)} records")
    for sp in index_species:
        cnt = (df_index["label"] == sp).sum()
        print(f"    [INDEX]  {sp:<35s} {cnt} records")

    print(f"\n  TEST SET   →  '{out_test}'")
    print(f"  {len(test_species)} species, {len(df_test)} records")
    for sp in test_species:
        cnt = (df_test["label"] == sp).sum()
        print(f"    [TEST ]  {sp:<35s} {cnt} records")

    print(f"{'─'*55}")
    print("Done.")

    return df_index, df_test


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    
    DATA_PATH = "/home/ducpham/workspace/PTIT-CSDLDPT/data/0000.parquet"
    OUT_INDEX = "/home/ducpham/workspace/PTIT-CSDLDPT/data/index.parquet"
    OUT_TEST  = "/home/ducpham/workspace/PTIT-CSDLDPT/data/test.parquet"

    parser = argparse.ArgumentParser(description="Split dataset into index / test sets by species.")
    parser.add_argument("--data",    default=DATA_PATH, help="Input parquet file")
    parser.add_argument("--n-test",  type=int, default=5,         help="Số loài dùng để test (default: 5)")
    parser.add_argument("--seed",    type=int, default=42,        help="Random seed (default: 42)")
    parser.add_argument("--out-index", default=OUT_INDEX, help="Output path cho index set")
    parser.add_argument("--out-test",  default=OUT_TEST,  help="Output path cho test set")
    parser.add_argument(
        "--test-species",
        nargs="+",
        default=None,
        metavar="SPECIES",
        help="Chỉ định tay tên loài test (ghi đè --n-test). Ví dụ: --test-species 'Turdus merula' 'Parus major'",
    )
    args = parser.parse_args()

    split_by_species(
        data_path=args.data,
        n_test_species=args.n_test,
        test_species=args.test_species,
        out_index=args.out_index,
        out_test=args.out_test,
        seed=args.seed,
    )
