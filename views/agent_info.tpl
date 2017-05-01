<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>NebulaSolarDash</title>
    </head>
    <link href="css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="/assets/css/ns_tb.css">
    <body bgcolor="99FFFF">
        <h2>Nebula-Solar服务器资源监控节点列表</h2>

        <script src="/assets/js/bootstrap.min.js"></script>

        <table class="imagetable">
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

