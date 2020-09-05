import bookv2, moviev2, traceback
from time import sleep

if __name__ == '__main__':
    try:
        choice = input("图书备份请输入[b]，电影备份输入[m]: ")
        if (choice.lower() == 'b'):
            bookv2.main()
        elif (choice.lower() == 'm'):
            moviev2.movieMain()
    except Exception as e:
        traceback.print_exc()
        sleep(10)
    finally:
        over=input('按任意键退出')