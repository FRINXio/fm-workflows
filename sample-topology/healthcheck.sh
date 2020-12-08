#!/usr/bin/expect


set cli_testtool_ports {10000 10001 10002 11000 11001 11002 11003 11004 12000 12001}
set netconf_testtool_ports {1783}

foreach port $cli_testtool_ports {
    spawn ssh localhost -p $port -oStrictHostKeyChecking=no
    # To control the timeout value, update this variable
    set timeout 10;
    expect {
    timeout {puts "Time-out happened";exit 1}
    eof {puts "EOF occured";exit 1} 
    "password" {puts "The $port  is accessible"}
    }
}

foreach port $netconf_testtool_ports {
    spawn ssh localhost -p $port -oStrictHostKeyChecking=no -s netconf
    # To control the timeout value, update this variable
    set timeout 10;
    expect {
    timeout {puts "Time-out happened";exit 1}
    eof {puts "EOF occured";exit 1} 
    "Password" {puts "The $port  is accessible"}
    }
}

exit 0




