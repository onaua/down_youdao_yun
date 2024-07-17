
## 下载某道云盘的资源

## 声明

- 本项目仅供学习交流使用，请勿用于商业用途。
- 请遵守相关法律法规，下载资源请遵守相关版权法律。
- 如因下载资源侵犯了第三方权益，请及时联系本人于 1491328056@qq.com，本人将第一时间删除相关资源。
- 提供源代码以及[pyinstaller](https://github.com/pyinstaller/pyinstaller)打包后的[windows](https://support.microsoft.com/zh-cn/meetwindows11)下可执行文件。
- 本人为15岁在校学生(截止至2024年)，水平有限，如有错误，还请指正。
- 本项目遵循[GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html)开源协议。


## 用法
- 下载某道云盘的资源，需要先安装 [Python](https://www.python.org/downloads/) 3.x 环境，并安装 [requests](https://requests.readthedocs.io/)、[rich](https://rich.readthedocs.io/)库。
- 先登录某道云盘，打开开发者工具，获得类似于 `"OUTFOX_SEARCH_USER_ID_NCOO=...; OUTFOX_SEARCH_USER_ID=...; DICT_SESS=...; DICT_LOGIN=..."`的cookies。
- 然后启动此项目，用法如下。
```python
python download.py <cookies> <save_folder>
```
or 
```  
dyy.exe <cookies> <save_folder>
```
示例
```
python download.py/dyy.exe "OUTFOX_SEARCH_USER_ID_NCOO=...; OUTFOX_SEARCH_USER_ID=...; DICT_SESS=...; DICT_LOGIN=..."  E:\downloads
```

- 其中，`<cookies>` 是登录某道云盘后获得的 cookies，`<save_folder>` 是保存下载资源的路径。上文为示例cookies，请自行替换。
- 下载完成后，资源会保存在指定的文件夹中。
- 会在控制台输出下载进度。

## 注意事项

- 与2024-7-17测试，下载时除网络较慢外，无异常。
- 下载资源时，请耐心等待。
- 有问题可以提issue，附上python版本(若使用python运行)、操作系统版本、cookies(可选)、报错信息。
- 喜欢就给个star吧~
