# -*- mode: ruby -*-
# vi: set ft=ruby :

ENV["LC_ALL"] = "en_US.UTF-8"

Vagrant.configure(2) do |config|

    config.vm.box = "ubuntu/xenial64"

    config.vm.provider 'virtualbox' do |vb|
        vb.customize ['modifyvm', :id, '--memory', '1024']
        vb.customize ['modifyvm', :id, '--chipset', 'ich9']
    end

    config.vm.define "server" do |server|
        server.vm.hostname = 'server'
        server.vm.network "private_network", ip: "10.69.69.69", mac: "000000000a69"

        #
        # Setup dev env
        #
        server.vm.provision "shell", privileged: false, inline: <<-SHELL
            set -ex

            sudo apt update
            sudo apt install -y python3-pip python3-venv

            cd /vagrant

            rm -rf .venv
            python3 -m venv .venv
            source .venv/bin/activate
            python3 setup.py develop
            pip3 install --upgrade pip
            pip install -e .

            {
                echo ''
                echo 'cd /vagrant'
                echo 'source .venv/bin/activate'
            } >> $HOME/.bashrc
        SHELL

        #
        # Setup test data
        #
        server.vm.provision "shell", privileged: false, inline: <<-SHELL
            set -ex
            mkdir -p $HOME/tftp/bootloaders
            mkdir -p $HOME/tftp/pxelinux.cfg

            echo 'dataA' > $HOME/tftp/a
            echo 'dataB' > $HOME/tftp/b
            echo 'syslinux' > $HOME/tftp/bootloaders/syslinux.efi
            echo 'pxelinux' > $HOME/tftp/bootloaders/pxelinux.0
            echo 'grub' > $HOME/tftp/bootloaders/grub.efi

            echo 'grub-client1' > $HOME/tftp/pxelinux.cfg/01-00-00-00-00-0a-01
            echo 'grub-client2' > $HOME/tftp/pxelinux.cfg/01-00-00-00-00-0a-02
        SHELL
    end

    config.vm.define "client1" do |client|
        client.vm.hostname = "client1"
        client.vm.network "private_network", ip: "10.69.69.1", mac: "000000000a01"
        client.vm.provision "shell", privileged: false, inline: <<-SHELL
            set -ex
            sudo apt update
            sudo apt install -y tftp
        SHELL
    end

    config.vm.define "client2" do |client|
        client.vm.hostname = "client2"
        client.vm.network "private_network", ip: "10.69.69.2", mac: "000000000a02"
        client.vm.provision "shell", privileged: false, inline: <<-SHELL
            set -ex
            sudo apt update
            sudo apt install -y tftp
        SHELL
    end
end
