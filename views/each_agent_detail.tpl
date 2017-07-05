<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>NebulaSolarDash</title>
    <!-- 引入 echarts.js -->
    <script src="/assets/js/echarts.min.js"></script>
    <script src="/assets/js/dark.js"></script>
    <link rel="stylesheet" href="/assets/css/ns_tb.css">
    <script type="text/javascript">
    setTimeout(function(){window.location.reload()}, 6000000);
    </script>
</head>
<body bgcolor="#333">
<!-- body background:#0f0 bgcolor="FFFFCC" -->
    <h2 align="center"><font color="FFFFFF">节点基础信息 -- 各个图表都可以使用鼠标拖动和滚轮缩放</font></h2>
        <table border="2" align="center"  class="imagetable">
            <tr>
                <th>主机名</th>
                <th>IP地址</th>
                <th>CPU</th>
                <th>内存(MB)</th>
                <th>SWAP(MB)</th>
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

    <table align="center">
		<h3 align="center"><font color="FFFFFF">节点磁盘存储信息统计</font></h4>
		<table border="2" align="center"  class="imagetable">
			<tr>
				<th>序号</th>
				<th>文件系统</th>
				<th>总大小</th>
				<th>已用</th>
				<th>剩余</th>
				<th>使用率</th>
				<th>挂载点</th>
			</tr>
			% for di_num, line in enumerate(result["agent_disk"]):
			<tr>
				<td>{{di_num+1}}</td>
				% for item in line:
				<td>{{item}}</td>
				% end
			</tr>
			% end
		</table>
    </table>

    <br/><br/>


    <!-- CPU信息处理 -->
    % cpu_now_time_list = result["agent_cpu"][0]
    % cpu_usage = list(result["agent_cpu"][1])
    % cpu_user = list(result["agent_cpu"][2])
    % cpu_nice = list(result["agent_cpu"][3])
    % cpu_system = list(result["agent_cpu"][4])
    % cpu_iowait = list(result["agent_cpu"][5])
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
        var myChartCpu = echarts.init(document.getElementById('cpu'), 'dark');
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
                data:['USAGE(%)', 'USER(%)', 'NICE(%)', 'SYSTEM(%)', 'IOWAIT(%)']
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
                    axisLabel: {
                        formatter: '{value} %'
                    },
                     name: 'CPU使用率(%)'
                }
            ],
            series: [
                {
                    name: 'USAGE(%)',
                    type: 'line',
                    <!-- areaStyle: {normal: {}}, -->
                    data: {{cpu_usage}}
                },
                {
                    name: 'NICE(%)',
                    type: 'line',
                    <!-- areaStyle: {normal: {}}, -->
                    data: {{cpu_nice}}
                },
                {
                    name: 'USER(%)',
                    type: 'line',
                    <!-- areaStyle: {normal: {}}, -->
                    data: {{cpu_user}}
                },
                {
                    name: 'SYSTEM(%)',
                    type: 'line',
                    <!-- areaStyle: {normal: {}}, -->
                    data: {{cpu_system}}
                },
                {
                    name: 'IOWAIT(%)',
                    type: 'line',
                    <!-- areaStyle: {normal: {}}, -->
                    data: {{cpu_iowait}}
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
        var myChartLoad = echarts.init(document.getElementById('load'), 'dark');
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
                    <!-- areaStyle: {normal: {}}, -->
                    data: {{load_avg}}
                }
            ]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChartLoad.setOption(option);
    </script>

    <br/>


     <!-- 内存信息处理 -->
    % mem_now_time_list = result["agent_mem"][0]
    % mem_all = result["agent_mem"][1]
    % mem_usage = list(result["agent_mem"][2])
    % mem_free = list(result["agent_mem"][3])
    % swap_total = list(result["agent_mem"][4])
    % swap_usage = list(result["agent_mem"][5])
    % swap_free = list(result["agent_mem"][6])
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
        var myChartMem = echarts.init(document.getElementById('mem'), 'dark');
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
                data:['已使用(MB)', '空闲(MB)', 'SWAP已使用(MB)', 'SWAP空闲(MB)']
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
                    <!-- areaStyle: {normal: {}}, -->
                    data: {{mem_usage}}
                },
                {
                    name: '空闲(MB)',
                    type: 'line',
                    <!-- areaStyle: {normal: {}}, -->
                    data: {{mem_free}}
                },
                {
                    name: 'SWAP已使用(MB)',
                    type: 'line',
                    <!-- areaStyle: {normal: {}}, -->
                    data: {{swap_usage}}
                },
                {
                    name: 'SWAP空闲(MB)',
                    type: 'line',
                    <!-- areaStyle: {normal: {}}, -->
                    data: {{swap_free}}
                },
            ]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChartMem.setOption(option);
    </script>

    <br/>


    <!-- 磁盘读写信息处理 -->
    % diskio_now_time_list = result["agent_diskio"][0]
    % diskio_disk = result["agent_diskio"][1][0:]
    % [diskio_each for diskio_each in diskio_disk]
    % diskio_util_list = [[i[0], i[-1]] for i in eval(diskio_each) for diskio_each in diskio_disk]
    % from collections import defaultdict
    % diskio_dict = defaultdict(list)
    % for item in diskio_util_list:
    %     diskio_dict[item[0]].append(item[1])
    % end
    % diskio_tag = [tag for tag in diskio_dict]

    <script type="text/javascript">
        var diskio_tag_arr = new Array();
        % for tag in diskio_dict:
        diskio_tag_arr.push("{{tag}}");
        % end
    </script>


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
        var myChartDiskio = echarts.init(document.getElementById('diskio'), 'dark');
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
                data: diskio_tag_arr
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
                containLabel: false
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
                     name: '硬盘util (%)'
                }
            ],
            series: [
                % diskio_dict_list = [i for i in diskio_dict.iteritems()]
                % if len(diskio_tag) >= 2:
                    % for each_series in diskio_dict_list[0:-1]:
                    {
                        name: "{{each_series[0]}}",
                        type: 'line',
                        <!-- areaStyle: {normal: {}}, -->
                        data: {{[float(i) for i in each_series[1]]}}
                    },
                    % end
                    {
                        name: "{{diskio_dict_list[-1][0]}}",
                        type: 'line',
                        <!-- areaStyle: {normal: {}}, -->
                        data: {{[float(i) for i in diskio_dict_list[-1][1]]}}
                    }
                % else:
                    {
                        name: "{{diskio_dict_list[-1][0]}}",
                        type: 'line',
                        // areaStyle: {normal: {}},
                        data: {{[float(i) for i in diskio_dict_list[-1][1]]}}
                    }
                % end
            ],
        };

        // 使用刚指定的配置项和数据显示图表。
        myChartDiskio.setOption(option);
    </script>

</body>
</html>