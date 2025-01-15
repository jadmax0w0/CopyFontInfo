import fontforge
from pathlib import Path
import os
import sys


class Config():
    def __init__(
        self,
        source_fonts_dir = "./src_fonts",
        target_fonts_dir = "./tgt_fonts",
        output_fonts_dir = "./out_fonts",
        no_merge_glyphs = False,
        no_copy_metadata = False,
        unify_em_size_mode = None,
        fstype_permitted = False,
    ):
        self.source_fonts_dir = source_fonts_dir
        self.target_fonts_dir = target_fonts_dir
        self.output_fonts_dir = output_fonts_dir
        self.no_merge_glyphs = no_merge_glyphs
        self.no_copy_metadata = no_copy_metadata
        self.unify_em_size_mode = unify_em_size_mode
        self.fstype_permitted = fstype_permitted
        


def get_ttf_files(directory):
    """
    获取指定目录及其子目录中的所有 .ttf 文件路径，并返回一个包含这些路径的列表。
    
    参数:
        directory (str 或 Path): 要搜索的目录路径。
        
    返回:
        list: 包含所有 .ttf 文件路径的列表。
    """
    ttf_files = []
    path = Path(directory)

    # 使用 rglob 方法递归查找所有 .ttf 文件
    for file_path in path.rglob('*.ttf'):
        ttf_files.append(str(file_path.resolve()))  # 使用 resolve() 获取绝对路径

    return ttf_files


def copy_metadata(source_font, target_font):
    # 把名称表中的所有信息悉数复制
    finfo = []
    for name in source_font.sfnt_names:
        finfo.append(name)
    finfo = tuple(finfo)

    target_font.sfnt_names = finfo


# def merge_glyphs(source_font, target_font):
#     # 遍历源字体的所有字形
#     for glyph in source_font.glyphs():
#         unicode_value = glyph.unicode
#         glyph_name = glyph.glyphname

#         # 检查该字形是否存在于目标字体中
#         glyph_exists_in_target = True
#         try:
#             dummy = target_font[unicode_value]
#         except TypeError:
#             glyph_exists_in_target = False
#         if unicode_value != -1 and not glyph_exists_in_target:
#             # 如果不存在，则从源字体复制到目标字体
#             print(f"Copying missing glyph '{glyph_name}' (U+{unicode_value:X})")
#             target_font.importGlyphs(source_font, [glyph.encoding])
#     return


def merge_glyphs(source_font, target_font, config: Config):
    # 检查字形的大小是否一致
    unify_em_size_mode = config.unify_em_size_mode
    em_source, em_target = source_font.em, target_font.em
    if em_source != em_target:
        if unify_em_size_mode is None:
            print(f"Souce font em size {em_source} does not match target font em size {em_target}. Unify them?")
            print("  s2t (1) - reset em size of source font to that of target font")
            print("  t2s (2) - reset em size of targe font to that of source font")
            print("  Anything else - leave them be (not recommended)")
            unify_em_size_mode = str(input("Enter your choice: "))
        if unify_em_size_mode == '1' or unify_em_size_mode == 's2t':
            source_font.em = target_font.em
        elif unify_em_size_mode == '2' or unify_em_size_mode == 't2s':
            target_font.em = source_font.em

    target_font.mergeFonts(source_font, True)  # (fromFont, preserveCrossFontKerning)


def override_fonts(source_path, target_path, output_path, config: Config):
    no_merge_glyphs = config.no_merge_glyphs
    no_copy_metadata = config.no_copy_metadata

    try:
        # 打开源字体文件
        source_font = fontforge.open(source_path, 1 if config.fstype_permitted else 0)
        print(f"Loaded source font: {source_path}")

        # 打开目标字体文件
        target_font = fontforge.open(target_path, 1 if config.fstype_permitted else 0)
        print(f"Loaded target font: {target_path}")

        # 合并缺失字形
        if not no_merge_glyphs:
            merge_glyphs(source_font, target_font, config)
            print("*** merged glyphs")

        # 复制元信息（如字体名、家族名、字重等）
        if not no_copy_metadata:
            copy_metadata(source_font, target_font)
            print('*** copied meta data')

        # 保存修改后的字体文件
        target_font.generate(output_path)
        print(f"Saved modified font to: {output_path}")

    except Exception as e:
        print(f"An error occurred: [{type(e)}] {e}")
    finally:
        # 确保关闭所有打开的字体对象
        if 'source_font' in locals():
            source_font.close()
        if 'target_font' in locals():
            target_font.close()


if __name__ == "__main__":
    config = Config()
    
    # argv, argc
    argv = sys.argv
    argv = argv[1:]
    argc = len(argv)
    if argc == 1 and (argv[0] == '-h' or argv[0] == '--help'):
        print("Usage: ffpython cpinfo.py [source_fonts_dir] [target_fonts_dir] [output_fonts_dir] [--nocpmetadata] [--nomergeglyphs] [--unifyemsize=s2t/t2s] [--fstypepermitted]")
        print(f"\nDefault Values:\n{vars(config)}")
        exit(0)

    non_flag_arg_id = 0
    for arg in argv:
        if arg == "--nocpmetadata":
            print('no copy metadata')
            config.no_copy_metadata = True
            continue
        if arg == "--nomergeglyphs":
            print('no merge glyphs')
            config.no_merge_glyphs = True
            continue
        if "--unifyemsize" in arg:
            config.unify_em_size_mode = arg.split('=')[1]
            print(f'unify em size ({config.unify_em_size_mode})')
            continue
        if arg == "--fstypepermitted":
            print("fstype permitted")
            config.fstype_permitted = True
            continue
        if non_flag_arg_id == 0:
            if os.path.isdir(str(arg)):
                config.source_fonts_dir = str(arg)
            else:
                print(f"[Source fonts dir] Path {arg} is not a valid path. Using default {config.source_fonts_dir}")
            continue
        if non_flag_arg_id == 1:
            if os.path.isdir(str(arg)):
                config.target_fonts_dir = str(arg)
            else:
                print(f"[Target fonts dir] Path {arg} is not a valid path. Using default {config.target_fonts_dir}")
            continue
        if non_flag_arg_id == 2:
            if os.path.isdir(str(arg)):
                config.output_fonts_dir = str(arg)
            else:
                print(f"[Output fonts dir] Path {arg} is not a valid path. Using default {config.output_fonts_dir}")
            continue
        non_flag_arg_id += 1

    source_font_paths = get_ttf_files(config.source_fonts_dir)
    target_font_paths = get_ttf_files(config.target_fonts_dir)

    for target_font_path in target_font_paths:
        assert os.path.isfile(target_font_path)
        source_font_path = ""
        target_font_name = os.path.basename(target_font_path)
        for path in source_font_paths:
            if target_font_name == os.path.basename(path):
                source_font_path = path
                break
        if source_font_path == "":
            print(f"{target_font_path} has no corresponding source .ttf file, skipping.")
            continue
        override_fonts(
            source_path=source_font_path, 
            target_path=target_font_path, 
            output_path=f"{config.output_fonts_dir}/{target_font_name}",
            config=config
        )
