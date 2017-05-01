<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>PlatformAPM</title>
    <!-- 引入 echarts.js -->
    <script src="/assets/js/echarts.min.js"></script>
    <link rel="stylesheet" href="/assets/css/ns_tb.css">
</head>
<body bgcolor="99FFFF">
    <h2>节点基础信息 -- 各个图表都可以使用鼠标拖动和滚轮缩放</h2>
    <div>
        <table border="2" align="left"  class="imagetable">
            <tr>
                <th>主机名</th>
                <th>IP地址</th>
                <th>CPU</th>
                <th>内存(MB)</th>
                <th>操作系统</th>
                <th>内核版本</th>
                <th>运行时长</th>
                <th>当前时间</th>
            </tr>
            <tr>
                % for item in result["agent_static"]:
                    <td>{{item}}</td>
                % end
            </tr>
        </table>
    </div>

    <br/><br/><br/><br/>

    <!-- 内存信息处理 -->
    % mem_now_time_list = result["agent_mem"][0]
    % mem_all = result["agent_mem"][1]
    % mem_usage = list(result["agent_mem"][2])
    % mem_free = list(result["agent_mem"][3])
    % mem_cached = list(result["agent_mem"][4])
    % mem_date_time_list = list()
    % import time
    % for mem_now_time in mem_now_time_list:
    %   mem_date_time = time.strftime("%Y%m%d-%H:%M:%S", time.localtime(mem_now_time))
    %       mem_date_time_list.append(mem_date_time)
    % end

    <script type="text/javascript">
        var mem_date_arr = new Array();
        % for mem_time_item in mem_date_time_list:
        mem_date_arr.push("{{mem_time_item}}");
        % end
    </script>


    <!-- 为MEM-ECharts准备一个具备大小（宽高）的Dom -->
    <div id="mem" align="left" style="width: 1750px;height:220px;"></div>
    <script type="text/javascript">
        // 基于准备好的dom，初始化echarts实例
        var myChartMem = echarts.init(document.getElementById('mem'));
        // 指定图表的配置项和数据
        var option = {
            title: {
                text: '节点内存实时监控'
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    label: {
                        backgroundColor: '#6a7985'
                    }
                }
            },
            legend: {
                data:['已使用(MB)', '空闲(MB)', '缓存(MB)']
            },
            toolbox: {
                show: true,
                feature: {
                    magicType: {type: ['line', 'bar']},
                    restore: {},
                    saveAsImage: {}
                }
            },
            dataZoom: [
                {
                    type: 'inside',
                    start: 0,
                    end: 100,
                    startValue: mem_date_arr
                }
            ],
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    name: '时间',
                    nameLocation: 'end',
                    boundaryGap: false,
                    nameGap: 40,
                    data: mem_date_arr
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    max: {{mem_all[0]}},
                    axisLabel: {
                        formatter: '{value} MB'
                    },
                     name: '内存(MB)'
                }
            ],
            series: [
                {
                    name: '已使用(MB)',
                    type: 'line',
                    areaStyle: {normal: {}},
                    data: {{mem_usage}}
                },
                {
                    name: '空闲(MB)',
                    type: 'line',
                    areaStyle: {normal: {}},
                    data: {{mem_free}}
                },
                {
                    name: '缓存(MB)',
                    type: 'line',
                    areaStyle: {normal: {}},
                    data: {{mem_cached}}
                },
            ]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChartMem.setOption(option);
    </script>

    <br/>

    <!-- CPU信息处理 -->
    % cpu_now_time_list = result["agent_cpu"][0]
    % cpu_usage = list(result["agent_cpu"][1])
    % cpu_date_time_list = list()
    % for cpu_now_time in cpu_now_time_list:
    %   import time
    %   cpu_date_time = time.strftime("%Y%m%d-%H:%M:%S", time.localtime(cpu_now_time))
    %       cpu_date_time_list.append(cpu_date_time)
    % end

    <script type="text/javascript">
        var cpu_date_arr = new Array();
        % for cpu_time_item in cpu_date_time_list:
        cpu_date_arr.push("{{cpu_time_item}}");
        % end
    </script>

    <!-- 为cpu-ECharts准备一个具备大小（宽高）的Dom -->
    <div id="cpu" align="left" style="width: 1750px;height:220px;"></div>
    <script type="text/javascript">
        // 基于准备好的dom，初始化echarts实例
        var myChartCpu = echarts.init(document.getElementById('cpu'));
        // 指定图表的配置项和数据
        var option = {
            title: {
                text: '节点CPU使用率实时监控'
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    label: {
                        backgroundColor: '#6a7985'
                    }
                }
            },
            legend: {
                data:['CPU使用率(%)']
            },
            toolbox: {
                show: true,
                feature: {
                    magicType: {type: ['line', 'bar']},
                    restore: {},
                    saveAsImage: {}
                }
            },
            dataZoom: [
                {
                    type: 'inside',
                    start: 0,
                    end: 100,
                    startValue: cpu_date_arr
                }
            ],
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    name: '时间',
                    nameLocation: 'end',
                    boundaryGap: false,
                    nameGap: 40,
                    data: cpu_date_arr
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    max: 100,
                    axisLabel: {
                        formatter: '{value} %'
                    },
                     name: 'CPU使用率(%)'
                }
            ],
            series: [
                {
                    name: 'CPU使用率(%)',
                    type: 'line',
                    areaStyle: {normal: {}},
                    data: {{cpu_usage}}
                }
            ]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChartCpu.setOption(option);
    </script>

    <br/>

    <!-- 负载信息处理，时间坐标复用CPU -->

    % load_avg = list(result["agent_load"])

    <!-- 为cpu-ECharts准备一个具备大小（宽高）的Dom -->
    <div id="load" align="left" style="width: 1750px;height:220px;"></div>
    <script type="text/javascript">
        // 基于准备好的dom，初始化echarts实例
        var myChartLoad = echarts.init(document.getElementById('load'));
        // 指定图表的配置项和数据
        var option = {
            title: {
                text: '节点平均负载值实时监控'
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    label: {
                        backgroundColor: '#6a7985'
                    }
                }
            },
            legend: {
                data:['平均负载值']
            },
            toolbox: {
                show: true,
                feature: {
                    magicType: {type: ['line', 'bar']},
                    restore: {},
                    saveAsImage: {}
                }
            },
            dataZoom: [
                {
                    type: 'inside',
                    start: 0,
                    end: 100,
                    startValue: cpu_date_arr
                }
            ],
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    name: '时间',
                    nameLocation: 'end',
                    boundaryGap: false,
                    nameGap: 40,
                    data: cpu_date_arr
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    name: '平均负载值'
                }
            ],
            series: [
                {
                    name: '平均负载值',
                    type: 'line',
                    areaStyle: {normal: {}},
                    data: {{load_avg}}
                }
            ]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChartLoad.setOption(option);
    </script>

    <br/>

    <!-- 网卡流量信息处理 -->
    % traffic_now_time_list = result["agent_traffic"][0]
    % traffic_interface = result["agent_traffic"][1][0]
    % traffic_in = list(result["agent_traffic"][2])
    % traffic_out = list(result["agent_traffic"][3])
    % traffic_date_time_list = list()
    % import time
    % for traffic_now_time in traffic_now_time_list:
    %   traffic_date_time = time.strftime("%Y%m%d-%H:%M:%S", time.localtime(traffic_now_time))
    %   traffic_date_time_list.append(traffic_date_time)
    % end

    <script type="text/javascript">
        var traffic_date_arr = new Array();
        % for traffic_time_item in traffic_date_time_list:
        traffic_date_arr.push("{{traffic_time_item}}");
        % end
    </script>

    <!-- 为traffic-ECharts准备一个具备大小（宽高）的Dom -->
    <div id="traffic" align="left" style="width: 1750px;height:220px;"></div>
    <script type="text/javascript">
        // 基于准备好的dom，初始化echarts实例
        var myChartTraffic = echarts.init(document.getElementById('traffic'));
        // 指定图表的配置项和数据
        var option = {
            title: {
                text: '节点网卡流量实时监控'
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    label: {
                        backgroundColor: '#6a7985'
                    }
                }
            },
            legend: {
                data:['接收(kbps)', '发送(kbps)']
            },
            toolbox: {
                show: true,
                feature: {
                    magicType: {type: ['line', 'bar']},
                    restore: {},
                    saveAsImage: {}
                }
            },
            dataZoom: [
                {
                    type: 'inside',
                    start: 0,
                    end: 100,
                    startValue: traffic_date_arr
                }
            ],
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    name: '时间',
                    nameLocation: 'end',
                    boundaryGap: false,
                    nameGap: 40,
                    data: traffic_date_arr
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    axisLabel: {
                        formatter: '{value} kbps'
                    },
                     name: '网卡：{{traffic_interface}}'
                }
            ],
            series: [
                {
                    name: '接收(kbps)',
                    type: 'line',
                    areaStyle: {normal: {}},
                    data: {{traffic_in}}
                },
                {
                    name: '发送(kbps)',
                    type: 'line',
                    areaStyle: {normal: {}},
                    data: {{traffic_out}}
                }
            ]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChartTraffic.setOption(option);
    </script>

    <br/>

    <!-- 磁盘读写信息处理 -->
    % diskio_now_time_list = result["agent_diskio"][0]
    % diskio_disk = result["agent_diskio"][1][0]
    % diskio_read = list(result["agent_diskio"][2])
    % diskio_write = list(result["agent_diskio"][3])
    % diskio_date_time_list = list()
    % import time
    % for diskio_now_time in diskio_now_time_list:
    %   diskio_date_time = time.strftime("%Y%m%d-%H:%M:%S", time.localtime(diskio_now_time))
    %   diskio_date_time_list.append(diskio_date_time)
    % end

    <script type="text/javascript">
        var diskio_date_arr = new Array();
        % for diskio_time_item in diskio_date_time_list:
        diskio_date_arr.push("{{diskio_time_item}}");
        % end
    </script>

    <!-- 为diskio-ECharts准备一个具备大小（宽高）的Dom -->
    <div id="diskio" align="left" style="width: 1750px;height:220px;"></div>
    <script type="text/javascript">
        // 基于准备好的dom，初始化echarts实例
        var myChartDiskio = echarts.init(document.getElementById('diskio'));
        // 指定图表的配置项和数据
        var option = {
            title: {
                text: '节点磁盘IO实时监控'
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    label: {
                        backgroundColor: '#6a7985'
                    }
                }
            },
            legend: {
                data:['读取(ms)', '写入(ms)']
            },
            toolbox: {
                show: true,
                feature: {
                    magicType: {type: ['line', 'bar']},
                    restore: {},
                    saveAsImage: {}
                }
            },
            dataZoom: [
                {
                    type: 'inside',
                    start: 0,
                    end: 100,
                    startValue: diskio_date_arr
                }
            ],
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    name: '时间',
                    nameLocation: 'end',
                    boundaryGap: false,
                    nameGap: 40,
                    data: diskio_date_arr
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    axisLabel: {
                        formatter: '{value} ms'
                    },
                     name: '硬盘：{{diskio_disk}}'
                }
            ],
            series: [
                {
                    name: '读取(ms)',
                    type: 'line',
                    areaStyle: {normal: {}},
                    data: {{diskio_read}}
                },
                {
                    name: '写入(ms)',
                    type: 'line',
                    areaStyle: {normal: {}},
                    data: {{diskio_write}}
                }
            ]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChartDiskio.setOption(option);
    </script>

</body>
</html>