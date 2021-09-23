from pathlib import Path

if __name__ == '__main__':
    BASE_DIR = Path(__file__).resolve().parent.parent
    par = Path(__file__).resolve().parent
    res = Path(__file__).resolve()
    print(BASE_DIR)
    print(par)
    print(res)
