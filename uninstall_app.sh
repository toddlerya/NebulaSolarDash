#!/bin/bash
# author: guoqun
# date: 20170410

SETCOLOR_SUCCESS="echo -en \\033[1;32m"
SETCOLOR_FAILURE="echo -en \\033[1;31m"
SETCOLOR_WARNING="echo -en \\033[1;33m"
SETCOLOR_NORMAL="echo -en \\033[0;39m"

# 定义记录日志的函数
LogMsg()
{
    time=`date "+%D %T"`
    echo "[$time] : INFO    : $*"
    ${SETCOLOR_NORMAL}
}

LogWarnMsg()
{
    time=`date "+%D %T"`
    ${SETCOLOR_WARNING}
    echo "[$time] : WARN    : $*"
    ${SETCOLOR_NORMAL}
}

LogSucMsg()
{
    time=`date "+%D %T"`
    ${SETCOLOR_SUCCESS}
    echo "[$time] : SUCCESS : $*"
    ${SETCOLOR_NORMAL}
}

LogErrorMsg()
{
    time=`date "+%D %T"`
    ${SETCOLOR_FAILURE}
    echo "[$time] : ERROR   : $*"
    ${SETCOLOR_NORMAL}
}

check_auto_ssh()
{
	ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no ${INSTALL_IP} 'exit'
	if(($?!=0))
	then
		LogErrorMsg "can not logon $INSTALL_IP without passwd."
		exit 1
	fi
}

stop_agent()
{
	agent_pid=`ssh ${INSTALL_IP} ps aux | grep "pid_apm_agent.py" | grep -v grep | awk -F " " '{print $2}'`
	if [ "$agent_pid" = "" ]
	then
		echo "没有需要停止的客户端"
	else
		ssh ${INSTALL_IP} "kill -9 $agent_pid"
	fi
}

unset_crond()
{
	ssh ${INSTALL_IP} "rm -rf /etc/cron.d/daemon_apm_agent"
	ssh ${INSTALL_IP} "service crond restart 1>/dev/null 2>/dev/null"
}

uninstall_to_node()
{
	ssh ${INSTALL_IP} "rm -rf ${INSTALL_PATH}"
}

INSTALL_IP=$1
INSTALL_PATH="/home/RunTimePlatformAPM"
APP_TAR_NAME="apm_agent.tar.gz"
LogMsg "校验服务器连通性: ${INSTALL_IP}"
check_auto_ssh
LogMsg "开始停止"
stop_agent
LogMsg "开始卸载"
uninstall_to_node
unset_crond

