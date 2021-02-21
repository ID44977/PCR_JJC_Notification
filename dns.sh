#!/bin/sh
#定义dns的文件
filen="/etc/resolv.conf"
#备份原本的DNS文件
wei=`cat $filen`
#此处可以改为可用的DNS
dns="119.29.29.29"
#通过ping测试域名或者IP的联通性,标准返回
dnstest(){
    kkk=""
    for ((i=1;i<=5;i++))
        do  
        ping -c 1 $1
        sss=`echo $?`
        kkk="$kkk $sss"
    done
    echo $kkk
    if [[ " 0 0 0 0 0" == "$kkk" ]];then
        return 0
    else 
        return 1
    fi
}
dnstest $dns
 
echo "nameserver "$dns >> $filen
#测试通过host命令来测试域名
a=`host www.baidu.com`
a=`echo $?`
 
if [[ "0" != $a ]];then
    #如果没有正确解析就恢复原本的值
	echo "$wei" >/etc/resolv.conf
	echo "No such DNS!"
	return 1
else
	echo "IS GOOD DNS"
	return 0
fi
