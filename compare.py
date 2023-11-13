import json
import argparse
import re
from debian import deb822

def read_build_depends(line):
    clean_line = re.sub(r'<.*?>|\[.*?\]|\(.*?\)', '', line).strip()
    package_names = [pkg.strip() for pkg in clean_line.replace("Build-Depends:", "").split(',')]
    package_names = [pkg for pkg in package_names if pkg and pkg != "''"]
    return package_names

def read_control_file(control_file):
    dependencies = []    # 创建一个列表用于存储依赖关系
    with open(control_file, 'r', encoding='utf-8') as file:
        # 使用 deb822.Deb822 解析控制文件内容
        control_data = deb822.Deb822(file)
        lines = control_data.get('Build-Depends', '').split('\n')
        for line in lines:
            build_depends = read_build_depends(line)
            dependencies.append(build_depends)
    return dependencies
# def read_control_file(control_file):
#     dependencies = {}    # 创建一个空字典用于存储依赖关系
#     current_package = None    # 初始化当前包为空

#     try:
#         with open(control_file, "r") as file:    # 打开控制文件
#             for line in file:    # 遍历文件的每一行
#                 line = line.strip()    # 去除行首尾的空格

#                 if line.startswith("Source:"):    # 如果行以"Source:"开头
#                     current_package = line.replace("Source:", "").strip()    # 获取当前包名
#                 elif line.startswith("Build-Depends:"):    # 如果行以"Build-Depends:"开头
#                     build_depends = read_build_depends(line)    # 调用 read_build_depends 函数读取 Build-Depends 信息
#                     dependencies[current_package] = build_depends    # 将当前包名和依赖关系添加到字典中
#     except FileNotFoundError:    # 如果文件未找到
#         print(f"Error: File {control_file} not found.")    # 打印错误信息
#     except Exception as e:    # 如果发生其他异常
#         print(f"Error reading {control_file}: {e}")    # 打印错误信息

#     return dependencies    # 返回依赖关系字典

def read_json(file_path):
    try:
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        return data
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {file_path}: {e}")

def compare_versions(control_data, json_data1, json_data2):
    for build_depends in control_data:
        #print(f"\nChecking Build-Depends: {build_depends}")

        for build_depend in build_depends:
            #print(f"\nComparing Package: {build_depend}")

            matching_entries1 = [entry for entry in json_data1 if entry["Package"] == build_depend]
            matching_entries2 = [entry for entry in json_data2 if entry["Package"] == build_depend]

            if not matching_entries1 and not matching_entries2:
                print(f"Package: {build_depend} not found in one or both of the JSON files")
                continue

            #print(f"Matching entries in JSON1: {matching_entries1}")
            #print(f"Matching entries in JSON2: {matching_entries2}")

            for entry in matching_entries1:
                version_json1 = entry["Version"]
                version_json2 = next((e["Version"] for e in matching_entries2 if e["Package"] == entry["Package"]), None)

                #print(f"JSON1: {version_json1}, JSON2: {version_json2}")

                if version_json2 is not None and version_json1 != version_json2:
                    print(f"Package: {entry['Package']} has different versions - deepin: {version_json1}, Debian: {version_json2}")

def main():
    parser = argparse.ArgumentParser(description="比较构建依赖的 debian/control 文件和 JSON 文件的版本。")
    parser.add_argument("-c", "--control-file", help="debian/control 文件的路径", required=True)
    parser.add_argument("-d", "--deepin-json", help="deepin.json 文件的路径", required=True)
    parser.add_argument("-b", "--debian-json", help="debian.json 文件的路径", required=True)
    args = parser.parse_args()

    control_file = args.control_file
    deepin_json = args.deepin_json
    debian_json = args.debian_json

    print(f"\n###### 正在读取 control 文件：{control_file}")
    control_data = read_control_file(control_file)

    print(f"\n正在读取 deepin.json 文件：{deepin_json}")
    deepin_data = read_json(deepin_json)

    print(f"\n正在读取 debian.json 文件：{debian_json}")
    debian_data = read_json(debian_json)

    if control_data is not None and deepin_data is not None and debian_data is not None:
        compare_versions(control_data, deepin_data, debian_data)

if __name__ == "__main__":
    main()
