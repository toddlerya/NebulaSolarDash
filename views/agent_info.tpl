<html>
    <head>
    <title>PlatformAPM</title>
    </head>
    <style>
    body { text-align:center }
     </style>
    <body>
        <h2>Nebula-Solar服务器资源监控节点列表</h2>
        <table border="2" align="center">
            <tr>
                <th>主机名</th>
                <th>IP地址</th>
            </tr>
            % for line in result[1]:
            <tr>
                % for item in line:
                    <td width:300px><a href='http://{{result[0][0]}}:{{result[0][1]}}/agent/{{item}}'>{{item}}</a></td>
                % end
            </tr>
            % end
        </table>
    </body>
</html>

