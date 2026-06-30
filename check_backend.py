import urllib.request
import sys

try:
    response = urllib.request.urlopen('http://localhost:5000/api/current_user', timeout=2)
    print('✅ 后端服务正在运行 (端口 5000)')
except Exception as e:
    print(f'❌ 后端服务未运行: {e}')
    print('\n请先启动后端服务:')
    print('  python app.py')
    sys.exit(1)
