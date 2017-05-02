<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>NebulaSolarDash</title>
    </head>
    <link rel="stylesheet" href="/assets/css/ns_tb.css">
    <body bgcolor="FFFFCC">
        <h2 align="center">Nebula-Solar服务器资源监控节点列表</h2>

        <table align="center" class="imagetable">
            <tr>
                <th>序号</th>
                <th>主机名</th>
                <th>IP地址</th>
                <th>内存</th>
                <th>CPU</th>
            </tr>
            % mem_yellow_value = result[2][0]
            % mem_red_value = result[2][1]
            % cpu_yellow_value = result[2][2]
            % cpu_red_value = result[2][3]
            % for num, line in enumerate(result[1]):
            <tr>
                <td style="background-color:#dcddc0">{{num}}</td>
                <!--主机名和IP字段-->
                % for item in line[0:2]:
                    <td style="background-color:#dcddc0"><a href='http://{{result[0][0]}}:{{result[0][1]}}/agent/{{item}}'>{{item}}</a></td>
                % end
                <!--内存字段-->
                % if line[2] < mem_yellow_value:
                    <td style="background-color:33CC00">{{line[2]}}%</td>
                % elif mem_yellow_value <= line[2] < mem_red_value:
                    <td style="background-color:FF9900">{{line[2]}}%</td>
                % else:
                    <td style="background-color:FF0000">{{line[2]}}%</td>
                % end
                <!--CPU字段-->
                % if line[3] < cpu_yellow_value:
                    <td td style="background-color:33CC00">{{line[3]}}%</td>
                % elif cpu_yellow_value <= line[3] < cpu_red_value:
                    <td td style="background-color:FF9900">{{line[3]}}%</td>
                % else:
                    <td td style="background-color:FF0000">{{line[3]}}%</td>
                % end
            </tr>
            % end
        </table>
    </body>
</html>

