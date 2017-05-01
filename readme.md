# NebulaSolarDash - v1.0
---

# 项目介绍：

写这个工具的目的是为了解决工作问题。
个人工作生产环境无法连接互联网，也没有自建的yum源等，手头又有很多服务器需要进行监控，使用现有的开源方案安装部署是个问题，
各种依赖组件包需要挨个安装，很麻烦，所以想找一款依赖较少部署简单的分布式服务器资源监控工具，找来找去没找到，索性自己动手写一个。
我的本职工作是测试，所以就用最熟悉的Python来写吧，第一次写web应用，先做出来再边学边优化吧。

工具分为客户端和服务端两部分：
服务端使用了bottle来作为web框架，echarts来渲染生成图表；
客户端使用Python原生类库采集服务器资源，写服务端时候参考了[pyDash](https://github.com/k3oni/pydash)



# 使用方法
## 1. 配置`conf`目录下的`ns.ini`文件:

    [server]
    ; 服务端IP
    ip = 192.168.233.128
    ; 服务端端口号
    port = 8081
    debug = True
    [agent]
    ; 客户端采集数据间隔时间, 单位是s
    interval = 2
    install_path = /home/RunTimeNSDash
    ;所有需要监控的节点的ip,以英文逗号分隔
    [all_agent_ip]
    ips = 192.168.233.128

## 2. 启动服务
    cd NebulaSolarDash
    python run.py

## 3. 停止服务
    cd NebulaSolarDash
    python stop.py




