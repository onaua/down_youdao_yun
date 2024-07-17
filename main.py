from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,wait as wait_futures
from threading import Lock

from rich import print
from requests import Session
import sys
mutex=Lock()

id_="y"+"o"+"u"+"d"+"a"+"o"+"."+"c"+"o"+"m"
class  YoudaoYunting:
    base_url="https://hardware-cloud-disk."+id_+"/cloud/column/getArticleAndTextFileList?product=apollo&sortKey=alphabeticIncrease&columnKey=%s&"
    index_url="https://hardware-cloud-disk."+id_+"/cloud/column/getAllArticleAndTextFileList?product=apollo&sortKey=alphabeticIncrease&"
    def __init__(self,cookies,save_folder):
        self._p=Path(save_folder)
        self.pool_1=ThreadPoolExecutor(max_workers=20)
        self.pool_2=ThreadPoolExecutor(max_workers=30)
        self.pool_3=ThreadPoolExecutor(max_workers=100)
        self.tasks_1=[]
        self.tasks_2=[]
        self.tasks_3=[]
        self.downloaded_num=0
        self._p.mkdir(exist_ok=True,parents=True)
        self.s=Session()
        self.s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        })
        self.s.cookies.update(cookies)
        pass
    def get_info(self,result,mode=1):
        if mode==1:
            return list(map(lambda x:(x["columnInfo"]["columnKey"],x["columnInfo"]["title"]),result["data"]["columnList"]))
        elif mode==2:
            return list(map(lambda x:(x["columnKey"],x["title"]),result["data"]["columnList"]))
        return[]
    @staticmethod
    def str_cookies_to_dict(str_cookies):
        cookies_dict = {}
        for line in str_cookies.split(';'):
            name, value = line.strip().split('=', 1)
            cookies_dict[name] = value
        return cookies_dict
    def print(self,msg):
        mutex.acquire()
        self.downloaded_num+=1
        # from mymodule.LOGGER
        print(msg+("   "*20))
        print(f"Downloaded {self.downloaded_num} files - {self.downloaded_num/len(self.tasks_3)*100:.2f}% - tasks_1:{len(self.tasks_1)} - task_2:{len(self.tasks_2)} - task_3:{len(self.tasks_3)} "+(" "*20),end="\r")
        mutex.release()
    def index(self):
        r=self.s.get(self.index_url)
        if (result:=r.json())["code"]==0:
            return self.get_info(result,1)
        return []
    def process_(self,column_key,title,parent_folder:Path):
        r=self.s.get(self.base_url%column_key)
        save_folder=parent_folder/title
        save_folder.mkdir(exist_ok=True,parents=True)
        if (result:=r.json())["code"]==0:
            for key,name in self.get_info(result,2):
                self.tasks_1.append(self.pool_1.submit(self.process_,key,name,save_folder))
            if (article_list:=result["data"]["articleList"]):
                self.tasks_2.append(self.pool_2.submit(self.download_,article_list,save_folder))
    def download_(self,article_list,save_folder:Path):
        def func(article):
            response=self.s.get(article["audioUrl"],stream=True)
            file=save_folder/article["title"]
            file.write_bytes(response.content)
            self.print(f"[green]{article['title']}[/green] downloaded successfully.")
        for article in article_list:
            self.tasks_3.append(self.pool_3.submit(func,article))

if __name__=="__main__":
    
    if len(sys.argv)!=3:
        print("Usage: python main.py <cookies> <save_folder>")
        exit(1)
    print(f"Cookies: {sys.argv[1]!r}")
    print(f"Save folder: {sys.argv[2]!r}")
    print("[cyan]task_1[/cyan]: 处理栏目信息的线程池列表 - [cyan]task_2[/cyan]: 下载文章列表的线程池列表 - [cyan]task_3[/cyan]: 下载各文件的线程池列表")
    yy=YoudaoYunting(YoudaoYunting.str_cookies_to_dict(sys.argv[1]),
                     save_folder=sys.argv[2])
    for key,title in yy.index():
        yy.process_(key,title,yy._p)
    wait_futures(yy.tasks_1)
    wait_futures(yy.tasks_2)
    wait_futures(yy.tasks_3)
    print("[cyan]All tasks finished.[/cyan]")
    print("\n\n")
