"""
小规模 NCR 复现入口 —— 专为 PyCharm / 本地调试设计。

直接运行本文件即可，无需手动传 --data_path / --vocab_path 参数。
"""

import os
import sys
import time

# 自动定位项目路径
NCR_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(NCR_DIR)
TINY_ROOT = os.path.join(PROJECT_ROOT, "NCR-data", "tiny")
DATA_PATH = os.path.join(TINY_ROOT, "data")
VOCAB_PATH = os.path.join(TINY_ROOT, "vocab")
OUTPUT_DIR = os.path.join(NCR_DIR, "output", "tiny_demo")

# 检查 tiny 数据集是否存在
_vocab_file = os.path.join(VOCAB_PATH, "f30k_precomp_vocab.json")
if not os.path.isfile(_vocab_file):
    print("=" * 60)
    print("错误: 找不到小规模数据集!")
    print(f"  期望词表: {_vocab_file}")
    print()
    print("请先在项目根目录执行以下命令生成 tiny 数据集:")
    print("  python scripts/make_tiny_dataset.py")
    print("=" * 60)
    sys.exit(1)

# 注入命令行参数（等价于带参运行 run.py）
sys.argv = [
    "run.py",
    "--gpu", "0",
    "--workers", "0",
    "--data_name", "f30k_precomp",
    "--data_path", DATA_PATH,
    "--vocab_path", VOCAB_PATH,
    "--batch_size", "32",
    "--num_epochs", "8",
    "--warmup_epoch", "2",
    "--lr_update", "4",
    "--noise_ratio", "0.2",
    "--log_step", "5",
    "--output_dir", OUTPUT_DIR,
]

if __name__ == "__main__":
    print("=" * 60)
    print("NCR 小规模复现实验")
    print(f"  data_path  : {DATA_PATH}")
    print(f"  vocab_path : {VOCAB_PATH}")
    print(f"  output_dir : {OUTPUT_DIR}")
    print("=" * 60)
    print()

    os.chdir(NCR_DIR)
    from run import run
    run()
