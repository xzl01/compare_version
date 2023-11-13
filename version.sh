#!/bin/bash

# 使用说明
usage() {
  echo "Usage: $0 -i <input_file> -o <output_file>"
  exit 1
}

# 初始化变量
input_file=""
output_file="output.json"

# 处理命令行参数
while getopts ":i:o:" opt; do
  case $opt in
    i)
      input_file="$OPTARG"
      ;;
    o)
      output_file="$OPTARG"
      ;;
    \?)
      echo "Invalid option: -$OPTARG"
      usage
      ;;
    :)
      echo "Option -$OPTARG requires an argument."
      usage
      ;;
  esac
done

# 检查输入文件是否为空
if [ -z "$input_file" ]; then
  echo "Input file not specified."
  usage
fi

# 执行命令并输出到指定文件
grep-dctrl -XF Architecture: amd64 -o -XF Architecture: all -s Package,Version "$input_file" | awk 'BEGIN { ORS=",\n"; print "[" } /Package:/ { package = $2 } /Version:/ { print "{\"Package\": \"" package "\", \"Version\": \"" $2 "\"}" } END { print "]"}' > "$output_file"

echo "Output written to $output_file"
