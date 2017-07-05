# NebulaSolarDash - v2.0
---

# 项目介绍：

写这个工具的目的是为了解决工作问题。
个人工作生产环境无法连接互联网，也没有自建的yum源等，手头又有很多服务器需要进行监控，使用现有的开源方案安装部署是个问题，
各种依赖组件包需要挨个安装，很麻烦，所以想找一款依赖较少部署简单的分布式服务器资源监控工具，找来找去没找到，索性自己动手写一个。
我的本职工作是测试，所以就用最熟悉的Python来写吧，第一次写web应用，先做出来再边学边优化吧。

工具分为客户端和服务端两部分：
服务端使用了bottle来作为web框架，echarts来渲染生成图表；
客户端使用Python原生类库采集服务器资源，客户端采集数据部分代码参考了[pyDash](https://github.com/k3oni/pydash)


# 使用效果
下图是在Red Hat Enterprise Linux Server release 6.3 (Santiago)的使用效果

![](/assets/picture/NebulaSolarDash2.0.gif)


# 使用方法
## 1. 首先在服务端服务器和各个客户端服务器之间建立主机信任，确保从服务端可以直接ssh连接到客户端服务器不需要输入密码

## 2. 配置`conf`目录下的`ns.ini`文件:

    [server]
    ; 服务端IP
    ip = 172.16.111.171
    ; 服务端端口号
    port = 8081
    debug = True
    ;报警信息阈值,百分比
    ;举例：
    ;cpu_yellow = 80，代表cpu使用率达到80%即提示使用黄色标示
    ;cpu_red = 95，代表cpu使用率达到95%即提示使用黄色标示
    mem_yellow = 80
    mem_red = 95
    cpu_yellow = 80
    cpu_red = 95

    [agent]
    ; 客户端采集数据间隔时间, 单位是s, 建议不要小于60s, 否则会导致数据采集过于频繁，影响服务器正常使用
    interval = 600
    install_path = /home/RunTimeNSDash
    ;所有需要监控的节点的ip,以英文逗号分隔
    [all_agent_ip]
    ;ips = 172.16.111.164,172.16.111.166,172.16.111.167,172.16.111.171


## 3. 运行参数
    python manager.py -h
    usage: manager.py [-h] [-install] [-uninstall] [-startall] [-stopall]
                      [-start START_ONE] [-stop STOP_ONE]

    Manager Tool

    optional arguments:
      -h, --help        show this help message and exit
      -install          安装客户端到各个节点并自动启动客户端以
                        服务端
      -uninstall        停止各个节点的客户端并停止程序清理安装
                        件，同时停止服务端
      -startall         启动各个节点的客户端并设置crond守护
      -stopall          停止各个节点的客户端并去除crond守护
      -start START_ONE  启动一个指定节点的客户端并设置crond守护
      -stop STOP_ONE    停止一个指定节点的客户端并去除crond守护

    等一分钟就可以在 http://{server_ip}:{port} 看到各个客户端列表了。


# 其他说明

    * 以客户端采集数据间隔时间120s为例，单节点24小时会向数据库写入大约4MB数据。
    * 单个客户端每次采集发送到服务端写入数据库的信息大概在5~6kb左右，请自行结合服务器个数以及监控时长和服务器存储自行设定监控间隔。

