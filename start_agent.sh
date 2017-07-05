#!/bin/bash
# author: guoqun
# date: 20170428

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


INSTALL_PATH="/home/RunTimeNSDash"
start_agent()
{
	agent_pid=`ps aux | grep "ns_agent.py" | grep -v grep | awk -F " " '{print $2}'`
	if [ "$agent_pid" = "" ]
	then
		# cd ${INSTALL_PATH} && source /etc/profile && nohup python ns_agent.py > log_of_ns_agent 2>&1 &
		cd ${INSTALL_PATH};source /etc/profile;nohup python ns_agent.py > log_of_ns_agent 2>&1 &
	else
		exit 1
	fi
}

start_agent
