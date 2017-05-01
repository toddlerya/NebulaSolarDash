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

check_auto_ssh()
{
	ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no ${INSTALL_IP} 'exit'
	if [ $? -ne 0 ]
	then
		LogErrorMsg "can not logon $INSTALL_IP without passwd."
		exit 1
	fi
}

set_crond()
{
	ssh ${INSTALL_IP}	"rm -rf /etc/cron.d/daemon_ns_agent"
	ssh ${INSTALL_IP}	"echo '*/1 * * * * root sh $INSTALL_PATH/start_agent.sh' > /etc/cron.d/daemon_ns_agent"
	ssh ${INSTALL_IP} "service crond restart 1>/dev/null 2>/dev/null"
}

install_to_node()
{
	rm -rf ${APP_TAR_NAME}
	tar czvf ${APP_TAR_NAME} lib conf ns_agent.py start_agent.sh 1>/dev/null 2>/dev/null
	ssh ${INSTALL_IP} "rm -rf ${INSTALL_PATH}"
	ssh ${INSTALL_IP} "mkdir -p ${INSTALL_PATH}"
	scp -r ${APP_TAR_NAME} root@${INSTALL_IP}:${INSTALL_PATH}  1>/dev/null 2>/dev/null
	ssh ${INSTALL_IP} "cd ${INSTALL_PATH}; tar zxvf $APP_TAR_NAME 1>/dev/null 2>/dev/null"
}

INSTALL_IP=$1
INSTALL_PATH="/home/RunTimeNSDash"
APP_TAR_NAME="ns_agent.tar.gz"
LogMsg "校验服务器连通性: ${INSTALL_IP}"
LogMsg "开始部署"
check_auto_ssh
install_to_node
set_crond

