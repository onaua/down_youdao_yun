from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,wait as wait_futures
from threading import Lock
from datetime import datetime

from rich import print
from requests import Session
import sys
from argparse import ArgumentParser
mutex=Lock()

id_="y"+"o"+"u"+"d"+"a"+"o"+"."+"c"+"o"+"m"
class  YoudaoYunting:
    base_url="https://hardware-cloud-disk."+id_+"/cloud/column/getArticleAndTextFileList?product=apollo&sortKey=alphabeticIncrease&columnKey=%s&"
    index_url="https://hardware-cloud-disk."+id_+"/cloud/column/getAllArticleAndTextFileList?product=apollo&sortKey=alphabeticIncrease&"
    sub_url="https://hardware-cloud-disk."+id_+"/cloud/subtitle/detail?product=apollo&articleKey=%s&columnKey=%s&"
    def __init__(self,cookies,save_folder,log_to_file,quiet=False):
        self._p=Path(save_folder)
        self.pool_1=ThreadPoolExecutor(max_workers=20)
        self.pool_2=ThreadPoolExecutor(max_workers=30)
        self.pool_3=ThreadPoolExecutor(max_workers=100)
        self.pool_4=ThreadPoolExecutor(max_workers=100)
        self.tasks_1=[]
        self.tasks_2=[]
        self.tasks_3=[]
        self.tasks_4=[]
        self.downloaded_num=0
        self.log_to_file=Path(log_to_file)
        self.log_to_file.touch(exist_ok=True)
        self.quiet=quiet
        self._p.mkdir(exist_ok=True,parents=True)
        self.s=Session()
        self.s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        })
        self.s.cookies.update(cookies)
        pass
    def process_sub(self,article_key,column_key,save_path:str):
        # self.s.get(self.sub_url%(article_key,column_key))
        response=self.s.get(self.sub_url%(article_key,column_key))
        if (result:=response.json())["code"]==0:
            data_=self.json_to_lrc(result["data"]["subtitleList"])  
            if save_path.count("Close Eyes - DVRST")>0:
                    breakpoint()
            if len(data_)==0:
                    a=Path(save_path)
                    if a.exists():a.unlink()
                    del a,f
                    return
            else:
                with open(save_path,"w",encoding="utf-8") as f:
                    f.write("\n".join(self.json_to_lrc(result["data"]["subtitleList"])))
                # print("5")

    def json_to_lrc(self,data:list):
        
        # 定义一个函数将毫秒时间戳转换为LRC格式的时间标签
        def ms_to_lrc_time(ms):
            seconds, milliseconds = divmod(ms, 1000)
            minutes, seconds = divmod(seconds, 60)
            return f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
        # breakpoint()
        # 生成LRC文件内容
        lrc_content = []
        for item in data:
            text = item['data']['text']
            start_time = ms_to_lrc_time(item['startTs'])
            lrc_content.append(f"[{start_time}]{text}")
        return lrc_content
        # 将LRC内容写入文件
        with open('output.lrc', 'w', encoding='utf-8') as f:
            f.write('\n'.join(lrc_content))
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
    def print(self,msg,*,temp_455665=True):
        mutex.acquire()
        if temp_455665:
            self.downloaded_num+=1
        # from mymodule.LOGGER
        if not self.quiet:
            print(msg+("   "*20))
            # t3,t4=len(self.tasks_3),len(self.tasks_4)
            # print(f"Downloaded {self.downloaded_num} files - {self.downloaded_num/(t3+t4)*100:.2f}% - tasks_1:{len(self.tasks_1)} - task_2:{len(self.tasks_2)} - task_3:{t3} - task_4:{t4} - 3+4:{t3+t4}"+(" "*20),end="\r")
            print(f"Downloaded {self.downloaded_num} files - {self.downloaded_num/(len(self.tasks_3))*100:.2f}% - tasks_1:{len(self.tasks_1)} - task_2:{len(self.tasks_2)} - task_3:{len(self.tasks_3)}"+(" "*20),end="\r")
        with self.log_to_file.open("a",encoding="utf-8") as f:
            f.write(msg+"\n")
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
            if article["title"].endswith(".lrc"):
                return
            response=self.s.get(article["audioUrl"],stream=True)
            file=save_folder/article["title"]
            file.write_bytes(response.content)
            self.print(f"[green]{article['title']}[/green] downloaded successfully.")
        def func2(article):
            save_path=save_folder/f"{article['title'].rsplit('.',1)[0]}.lrc"
            show_name=save_path.name
            save_path=str(save_path)
            self.process_sub(article["articleKey"],article["columnKey"],save_path)
            self.print(f"[blue]{show_name}[/blue] downloaded successfully.",temp_455665=False)

        for article in article_list:
            self.tasks_3.append(self.pool_3.submit(func,article))
            self.tasks_4.append(self.pool_4.submit(func2,article))

if __name__=="__main__":
    parser=ArgumentParser(prog="this")
    parser.add_argument("cookies",help="cookies of ~dao cloud disk")
    parser.add_argument("save_folder",help="folder to save files")
    parser.add_argument("-q","--quiet",help="quiet mode",action="store_true")
    parser.add_argument("-l","--log-to-file",default=Path(__file__).parent/f"./{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
                        type=Path,help="log to file")
    args=parser.parse_args(sys.argv[1:])

    print(f"Cookies: {args.cookies!r}")
    print(f"Save folder: {args.save_folder!r}")
    print(f"Quiet mode: {args.quiet}")
    if args.quiet:
        print(f"[cyan]Quiet mode[/cyan] enabled, will only log to {args.log_to_file!s} instead of console.")
    print("[cyan]task_1[/cyan]: 处理栏目信息的线程池列表 - [cyan]task_2[/cyan]: 下载文章列表的线程池列表 - [cyan]task_3[/cyan]: 下载除lrc的文件的线程池列表") # - [cyan]task_4[/cyan]: 下载lrc文件的线程池列表
    yy=YoudaoYunting(YoudaoYunting.str_cookies_to_dict(args.cookies),
                     save_folder=args.save_folder,log_to_file=args.log_to_file,quiet=args.quiet)
    for key,title in yy.index():
        yy.process_(key,title,yy._p)
    wait_futures(yy.tasks_1)
    wait_futures(yy.tasks_2)
    wait_futures(yy.tasks_3)
    wait_futures(yy.tasks_4)
    print("\n[cyan]All tasks finished.[/cyan]")
    print("\n\n")
