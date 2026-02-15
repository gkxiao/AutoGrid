## 运行方法

保存上述代码为 `map2dx.py`，然后在终端执行：

```bash
python map2dx.py 4zlz_amber.C.map 4zlz_amber.C.dx
```

## 输出预期

脚本会打印类似以下信息：
```
Header claims grid dimensions: 52 x 52 x 52 (total 140608 points)
Spacing: 0.375
Center: (-19.887, 7.584, -3.135)
Actual number of data points: 148877
Warning: Data length mismatch. Expected 140608, got 148877.
Assuming grid dimensions are 53 x 53 x 53 based on data length.
Successfully wrote 4zlz_amber.C.dx
```

生成的 `4zlz_amber.C.dx` 文件即可在 PyMOL 或 Flare 中加载。

## 注意事项

- 此脚本假设网格是立方体（三个维度相等），适用于大多数 AutoGrid 生成的单分子层地图。如果您的文件非立方（例如 x、y、z 维度不同），且头信息正确，则不会进入推断分支，但当前数据长度与头信息不匹配时会失败。如果您遇到这种情况，请提供文件内容以便进一步调整。
- 如果数据长度恰好是某个整数的立方，脚本会自动采用该整数作为三个维度。否则会报错退出。
- 中心坐标和步长仍使用头信息中的值，因此生成的原点位置是正确的。
