<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>PlatformAPM</title>
    <!-- 引入 echarts.js -->
    <script src="/assets/echarts.min.js"></script>
</head>
<body>
    <h2>节点基础信息 -- 各个图表都可以使用鼠标拖动和滚轮缩放</h2>
    <table border="2" align="left">
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

    <br/><br/><br/><br/>

    <!-- 内存信息处理 -->
    % mem_now_time_list = result["agent_mem"][0]
    % mem_all = result["agent_mem"][1]
    % mem_usage = list(result["agent_mem"][2])
    % mem_free = list(result["agent_mem"][3])
    % mem_cached = list(result["agent_mem"][4])
    % mem_date_time_list = list()
    % for mem_now_time in mem_now_time_list:
    %   import time
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
                    end: 30,
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
                        formatter: '{value}MB'
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





</body>
</html>