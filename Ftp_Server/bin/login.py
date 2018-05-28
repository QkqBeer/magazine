import os
import sys
#os.path.abspath(__file__)当前文件目录
#os.path.dirname()返回上一层目录
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from core import main

if __name__ == '__main__':
    main.main()