# -*- mode: ruby -*-
# vi: set ft=ruby :

ENV["LC_ALL"] = "en_US.UTF-8"

Vagrant.configure(2) do |config|

    config.vm.box = "ubuntu/xenial64"
    config.vm.hostname = 'tftp-pilot'

    config.vm.provider 'virtualbox' do |vb|
        vb.customize ['modifyvm', :id, '--memory', '1024']
        vb.customize ['modifyvm', :id, '--chipset', 'ich9']
    end

    config.vm.provision "shell", privileged: false, inline: <<-SHELL
        set -ex

        sudo apt update
        sudo apt install -y python3-venv

        cd /vagrant

        rm -rf .venv
        python3 -m venv .venv
        source .venv/bin/activate
        pip3 install --upgrade pip
        pip3 install -r requirements.txt

        {
            echo ''
            echo 'cd /vagrant'
            echo 'source .venv/bin/activate'
        } >> $HOME/.bashrc

    SHELL

end
