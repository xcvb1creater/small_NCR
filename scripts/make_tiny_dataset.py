"""
从完整 NCR-data 中抽取小规模子集，用于快速理解实验流程。

推荐 Flickr30K (f30k_precomp)：1 图 5 文，支持 noise_ratio 噪声实验。

用法:
    python scripts/make_tiny_dataset.py
    python scripts/make_tiny_dataset.py --train_images 100 --dev_images 20 --test_images 20
"""

import argparse
import os
import shutil

import numpy as np


def read_lines(path):
    with open(path, encoding="utf-8") as f:
        return f.readlines()


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def subset_txt_files(src_dir, dst_dir, split, n_caps, extras=()):
    caps_src = os.path.join(src_dir, f"{split}_caps.txt")
    caps = read_lines(caps_src)[:n_caps]
    write_lines(os.path.join(dst_dir, f"{split}_caps.txt"), caps)

    for name in extras:
        src = os.path.join(src_dir, f"{split}_{name}.txt")
        if os.path.exists(src):
            write_lines(os.path.join(dst_dir, f"{split}_{name}.txt"), read_lines(src)[:n_caps])


def subset_tsv_files(src_dir, dst_dir, split, n_samples):
    import csv

    caps_src = os.path.join(src_dir, f"{split}_caps.tsv")
    rows = []
    with open(caps_src, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            rows.append(row)
            if len(rows) >= n_samples:
                break

    with open(os.path.join(dst_dir, f"{split}_caps.tsv"), "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(rows)


def subset_ims(src_path, dst_path, n_images):
    ims = np.load(src_path, mmap_mode="r")
    n_images = min(n_images, ims.shape[0])
    np.save(dst_path, np.array(ims[:n_images]))


def subset_f30k(src_root, dst_root, train_images, dev_images, test_images):
    src_dir = os.path.join(src_root, "data", "f30k_precomp")
    dst_dir = os.path.join(dst_root, "data", "f30k_precomp")
    os.makedirs(dst_dir, exist_ok=True)

    im_div = 5
    splits = {
        "train": train_images * im_div,
        "dev": dev_images * im_div,
        "test": test_images * im_div,
    }
    image_counts = {
        "train": train_images,
        "dev": dev_images,
        "test": test_images,
    }

    for split, n_caps in splits.items():
        subset_txt_files(src_dir, dst_dir, split, n_caps, extras=("ids", "tags"))
        subset_ims(
            os.path.join(src_dir, f"{split}_ims.npy"),
            os.path.join(dst_dir, f"{split}_ims.npy"),
            image_counts[split],
        )
        print(
            f"  {split}: {image_counts[split]} images, {n_caps} captions"
        )


def subset_cc152k(src_root, dst_root, train_samples, dev_samples, test_samples):
    src_dir = os.path.join(src_root, "data", "cc152k_precomp")
    dst_dir = os.path.join(dst_root, "data", "cc152k_precomp")
    os.makedirs(dst_dir, exist_ok=True)

    for split, n_samples in [
        ("train", train_samples),
        ("dev", dev_samples),
        ("test", test_samples),
    ]:
        subset_tsv_files(src_dir, dst_dir, split, n_samples)
        subset_ims(
            os.path.join(src_dir, f"{split}_ims.npy"),
            os.path.join(dst_dir, f"{split}_ims.npy"),
            n_samples,
        )
        print(f"  {split}: {n_samples} image-caption pairs")


def copy_vocab(src_root, dst_root, data_name):
    src_vocab = os.path.join(src_root, "vocab", f"{data_name}_vocab.json")
    dst_vocab_dir = os.path.join(dst_root, "vocab")
    os.makedirs(dst_vocab_dir, exist_ok=True)
    shutil.copy2(src_vocab, os.path.join(dst_vocab_dir, f"{data_name}_vocab.json"))


def main():
    parser = argparse.ArgumentParser(description="Create tiny NCR dataset subset")
    parser.add_argument(
        "--src_root",
        default=os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "NCR-data",
            "NCR-data",
        ),
        help="完整 NCR-data 根目录 (含 data/ 和 vocab/)",
    )
    parser.add_argument(
        "--dst_root",
        default=os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "NCR-data",
            "tiny",
        ),
        help="小规模数据输出目录",
    )
    parser.add_argument(
        "--dataset",
        default="f30k_precomp",
        choices=["f30k_precomp", "cc152k_precomp"],
        help="推荐 f30k_precomp 做噪声对应实验",
    )
    parser.add_argument("--train_images", type=int, default=100, help="训练集图像数 (f30k)")
    parser.add_argument("--dev_images", type=int, default=20, help="验证集图像数 (f30k)")
    parser.add_argument("--test_images", type=int, default=20, help="测试集图像数 (f30k)")
    parser.add_argument("--train_samples", type=int, default=400, help="训练样本数 (cc152k)")
    parser.add_argument("--dev_samples", type=int, default=50, help="验证样本数 (cc152k)")
    parser.add_argument("--test_samples", type=int, default=50, help="测试样本数 (cc152k)")
    args = parser.parse_args()

    if not os.path.isdir(os.path.join(args.src_root, "data")):
        raise FileNotFoundError(f"找不到数据目录: {args.src_root}/data")

    print(f"源目录: {args.src_root}")
    print(f"输出目录: {args.dst_root}")
    print(f"数据集: {args.dataset}")

    if args.dataset == "f30k_precomp":
        subset_f30k(
            args.src_root,
            args.dst_root,
            args.train_images,
            args.dev_images,
            args.test_images,
        )
    else:
        subset_cc152k(
            args.src_root,
            args.dst_root,
            args.train_samples,
            args.dev_samples,
            args.test_samples,
        )

    copy_vocab(args.src_root, args.dst_root, args.dataset)
    print("\n完成! 小规模数据已保存。")
    print(f"  data_path = {os.path.join(args.dst_root, 'data')}")
    print(f"  vocab_path = {os.path.join(args.dst_root, 'vocab')}")


if __name__ == "__main__":
    main()
