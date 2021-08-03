#!/usr/bin/expect

# ssh variables
set loginUser "admin"
set loginPassword "admin"
set serverAddress "localhost"
set port 1783

# Get the config to run, one per line
set f [open "/home/topology/netconf-testtool/netconf_data.xml"]
set configs [split [read $f] "\n"]
close $f

# check ssh port opened

set ssh_conection 0;
while {$ssh_conection == 0} {

    set timeout 20;
    spawn ssh $serverAddress -p $port -oStrictHostKeyChecking=no -s netconf

    expect {
        timeout {
            puts "Time-out happened";
            sleep 20
        }
        "Password:" {
            puts "The $port  is accessible";
            set ssh_conection 1;
        }
        "Cannot assign" {
            puts "The $port  is not accessible";
            sleep 20
        }
    }

}

spawn ssh -l $loginUser $serverAddress -p $port -s netconf
expect "(yes/no)?" {send "yes\r"}
expect "Password:" {send "$loginPassword\r"}

set timeout 1;
expect { 
    timeout {
        foreach conf $configs {
            expect " "
            send "$conf\r"
        }
    }  
}

set timeout 2;
expect { 
    timeout {
        send "\r"
        send "exit\r"
        close
    }  
}

exit 0