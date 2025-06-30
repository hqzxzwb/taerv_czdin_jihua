import argparse
import requests
import sys


def main():
    parser = argparse.ArgumentParser(description='POST CZ to API')
    parser.add_argument('CZ', help='要查询的汉字/词')
    args = parser.parse_args()

    url = 'https://test.ciet.top/find2'
    data = {'hans': args.CZ}

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        results = response.json()
        for item in results:
            fields = [
                item.get('trad', ''),
                item.get('simp', ''),
                item.get('shieon', ''),
                item.get('ghiuin', ''),
                item.get('diau', ''),
                item.get('example', ''),
                item.get('info', '')
            ]
            print(','.join('' if f is None else str(f) for f in fields))
    except requests.RequestException as e:
        print(f'请求失败: {e}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()