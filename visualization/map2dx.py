#!/usr/bin/env python
"""
Convert AutoGrid .map file to OpenDX .dx format.
Automatically handles mismatched NELEMENTS by inferring cubic dimensions if possible.
Usage: python map2dx.py input.map output.dx
"""

import numpy as np
import sys

def autogrid_map_to_dx(map_file, dx_file):
    with open(map_file, 'r') as f:
        lines = f.readlines()

    # 解析头信息
    header = {}
    data_start = None
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        key = parts[0]
        if key == "SPACING":
            header['spacing'] = float(parts[1])
        elif key == "NELEMENTS":
            header['nx'] = int(parts[1])
            header['ny'] = int(parts[2])
            header['nz'] = int(parts[3])
        elif key == "CENTER":
            header['cx'] = float(parts[1])
            header['cy'] = float(parts[2])
            header['cz'] = float(parts[3])
        elif key in ("GRID_PARAMETER_FILE", "GRID_DATA_FILE", "MACROMOLECULE"):
            continue
        else:
            # 遇到第一个不以大写关键字开头的行，视为数据开始
            data_start = i
            break

    if data_start is None:
        raise ValueError("Could not find start of data section.")

    required = ['spacing', 'nx', 'ny', 'nz', 'cx', 'cy', 'cz']
    for r in required:
        if r not in header:
            raise ValueError(f"Missing header key: {r}")

    nx, ny, nz = header['nx'], header['ny'], header['nz']
    spacing = header['spacing']
    cx, cy, cz = header['cx'], header['cy'], header['cz']

    print(f"Header claims grid dimensions: {nx} x {ny} x {nz} (total {nx*ny*nz} points)")
    print(f"Spacing: {spacing}")
    print(f"Center: ({cx}, {cy}, {cz})")

    # 读取所有数据
    data_lines = lines[data_start:]
    data = []
    for line in data_lines:
        line = line.strip()
        if not line:
            continue
        for token in line.split():
            try:
                data.append(float(token))
            except ValueError:
                print(f"Warning: Skipping non-numeric token '{token}'")
                continue

    n_actual = len(data)
    print(f"Actual number of data points: {n_actual}")

    expected = nx * ny * nz
    if n_actual != expected:
        print(f"Warning: Data length mismatch. Expected {expected}, got {n_actual}.")
        # 尝试推断为立方体（三个维度相等）
        cube_root = round(n_actual ** (1/3))
        if cube_root ** 3 == n_actual:
            nx = ny = nz = cube_root
            print(f"Assuming grid dimensions are {nx} x {ny} x {nz} based on data length.")
        else:
            print("Data length is not a perfect cube. Cannot infer dimensions automatically.")
            print("Please check the file or modify the script to handle non-cubic grids.")
            sys.exit(1)
    else:
        print("Data length matches header. Proceeding with original dimensions.")

    # 重塑数组
    arr = np.array(data).reshape((nx, ny, nz))

    # 计算原点（使用头信息中的中心，但根据实际维度调整）
    origin_x = cx - (nx - 1) * spacing / 2.0
    origin_y = cy - (ny - 1) * spacing / 2.0
    origin_z = cz - (nz - 1) * spacing / 2.0

    # 写入 DX 文件
    with open(dx_file, 'w') as f:
        f.write(f"object 1 class gridpositions counts {nx} {ny} {nz}\n")
        f.write(f"origin {origin_x:.6f} {origin_y:.6f} {origin_z:.6f}\n")
        f.write(f"delta {spacing:.6f} 0 0\n")
        f.write(f"delta 0 {spacing:.6f} 0\n")
        f.write(f"delta 0 0 {spacing:.6f}\n")
        f.write(f"object 2 class gridconnections counts {nx} {ny} {nz}\n")
        f.write(f"object 3 class array type double rank 0 items {nx*ny*nz} data follows\n")

        flat = arr.flatten()
        for i, val in enumerate(flat):
            f.write(f" {val:.6e}")
            if (i + 1) % 6 == 0:
                f.write("\n")
        if flat.size % 6 != 0:
            f.write("\n")
        f.write("\n")

    print(f"Successfully wrote {dx_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python map2dx.py input.map output.dx")
        sys.exit(1)
    autogrid_map_to_dx(sys.argv[1], sys.argv[2])
