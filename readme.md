# CopyFontInfo

快速复制字体的元信息或合并缺失字形。借助于 FontForge 实现。

## 使用

### 源字体 & 目标字体

以 Inter 系列字体转换为 SegoeUI 系列字体为例，也就是让 Inter 字体的元信息 (如字体名、家族名等) 变为 SegoeUI 字体，同时将 SegoeUI 字体中 (Inter 所没有的) 的字形合并到 Inter 中。此时 SegoeUI 将作为“源字体”，Inter 将作为“目标字体”。

### 命令行

首先需要安装 [FontForge](https://fontforge.org/)。打开安装目录下的 `fontforge-console.bat` 文件后，接下来的命令都需要在此窗口中输入。

#### 基础命令

```bash
ffpython cpinfo.py [path/to/sourcefonts] [path/to/targetfonts] [flags]
```

#### 路径名

前面的为源字体存放目录 (无需定位到字体文件，只输入所在的文件夹路径即可)，后面的为目标字体存放目录。若不提供路径，则默认将读取 `cpfinfo.py` 所在目录下的 `src_fonts` 和 `tgt_fonts` 文件夹。

#### Flags

- `--nocpmetadata`: 添加此 flag, 将不会把源字体的元信息拷贝到目标字体中；
- `--nomergeglyphs`： 添加此 flag, 将不会把源字体中目标字体所缺失的字形拷贝到目标字体中；
- `--unifyemsize=<mode>`: 适用于源字体和目标字体字形大小不一致的情形。若 `<mode>` 为 `1` 或 `s2t`，则会将源字体的字形大小设置为目标字体的字形大小；若为 `2` 或 `t2s`，则会将目标字体的字形大小设置为源字体的字形大小；其他情况下将不会修改源/目标字体的字形大小；
- `--fstypepermitted`: 添加此 flag，表明用户有权操作某些需要许可证的字体文件。

### 注意

源字体和目标字体的文件名需要一一对应。比如如果需要将 `segoeui.ttf`, `segoeuib.ttf` 和 `segoeuii.ttf` 的信息分别拷贝到 `Inter-Regular.ttf`, `Inter-Bold.ttf` 和 `Inter-Italic.ttf` 中，那么需要将对应字体的文件名取为相同的文件名，比如都取为 `seginter.ttf`, `seginterb.ttf`, `seginteri.ttf`。
