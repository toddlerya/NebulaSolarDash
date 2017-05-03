# NebulaSolarDash - v1.0
---

# 项目介绍：

写这个工具的目的是为了解决工作问题。
个人工作生产环境无法连接互联网，也没有自建的yum源等，手头又有很多服务器需要进行监控，使用现有的开源方案安装部署是个问题，
各种依赖组件包需要挨个安装，很麻烦，所以想找一款依赖较少部署简单的分布式服务器资源监控工具，找来找去没找到，索性自己动手写一个。
我的本职工作是测试，所以就用最熟悉的Python来写吧，第一次写web应用，先做出来再边学边优化吧。

工具分为客户端和服务端两部分：
服务端使用了bottle来作为web框架，echarts来渲染生成图表；
客户端使用Python原生类库采集服务器资源，客户端采集数据部分代码参考了[pyDash](https://github.com/k3oni/pydash)。

经测试，本工具可以在Ubuntu14.04 x64 和 RedHat 6.3 x64正常运行。

# 使用效果
下图是在Ubuntu 14.04 trusty的使用效果

![](/assets/picture/NebulaSolarDash.gif)


# 使用方法
## 1. 首先在服务端服务器和各个客户端服务器之间建立主机信任，确保从服务端可以直接ssh连接到客户端服务器不需要输入密码

## 2. 配置`conf`目录下的`ns.ini`文件:

    [server]
    ; 服务端IP
    ip = 192.168.233.128
    ; 服务端端口号
    port = 8081
    debug = True
    ;报警信息阈值,百分比
    ;举例：
    ;cpu_yellow = 80，代表cpu使用率达到80%即提示使用黄色标示
    ;cpu_red = 95，代表cpu使用率达到95%即提示使用红色标示
    mem_yellow = 80
    mem_red = 95
    cpu_yellow = 80
    cpu_red = 95
    [agent]
    ; 客户端采集数据间隔时间, 单位是s
    interval = 2
    install_path = /home/RunTimeNSDash
    ;所有需要监控的节点的ip,以英文逗号分隔
    [all_agent_ip]
    ips = 192.168.233.128

## 3. 启动服务
    cd NebulaSolarDash
    python run.py
    等一分钟就可以在 http://{server_ip}:{port} 看到各个客户端列表了。

## 4. 停止服务
    cd NebulaSolarDash
    python stop.py




