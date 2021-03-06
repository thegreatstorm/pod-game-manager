from subprocess import check_output, Popen
import socket
import threading
import os

from bin.utils.system_controller import random_port, random_password


def command_prefix(container, command, user):
    main_command = 'docker exec -u {0} -t {1} sh -c "{2}"'.format(user, container, command)

    return main_command


class RustServer:
    def __init__(self, image=None, app_settings=None, container=None, config_json=None, app_dir=None, config_file=None):
        self.image = image
        self.container = container
        self.config_json = config_json
        self.app_dir = app_dir
        self.app_settings = app_settings

        if image is None:
            self.image = ""
        else:
            self.image = image

        if config_json is None:
            self.config_json = ""
        else:
            self.config_json = config_json

        if container is None:
            self.container = ""
        else:
            self.container = container

        if app_dir is None:
            self.app_dir = ""
        else:
            self.app_dir = app_dir

        if config_file is None:
            self.config_file = ""
        else:
            self.config_file = config_file

        if app_settings is None:
            self.app_settings = ""
        else:
            self.app_settings = app_settings

    def install(self):
        data = {}
        game_port = random_port()
        rcon_port = random_port()
        app_port = random_port()

        command = "docker run -td -p {0}:{0}/udp -p {0}:{0}/tcp -p {1}:{1}/tcp -p {2}:{2}/tcp {3}".format(game_port, rcon_port, app_port, self.image)

        try:
            container_id = check_output(command, shell=True).decode('ascii')
            container_id = container_id.rstrip("\n")

            data["container_id"] = container_id
            data["game_port"] = game_port
            data["rcon_port"] = rcon_port
            data["app_port"] = app_port

            print(str(data))
            # Insert New Record into database.
            commands = []
            commands.append("echo 'export server_port={}' >> /etc/bashrc".format(game_port))
            commands.append("echo 'export rcon_port={}' >> /etc/bashrc".format(rcon_port))
            commands.append("echo 'export app_port={}' >> /etc/bashrc".format(app_port))
            commands.append("echo 'echo -e \'Welcome to Storm Pods! Server Port: {} Rcon Port: {} Mobile Port: {} \'' >> /etc/bashrc".format(game_port,rcon_port,app_port))
            commands.append('git clone https://github.com/thegreatstorm/ansiblepods.git /opt/ansiblepods > /dev/null')
            commands.append('ansible-playbook /opt/ansiblepods/linuxgsm/rustserver/requirements.yml')
            commands.append('ansible-playbook /opt/ansiblepods/linuxgsm/rustserver/setup.yml')
            commands.append('ansible-playbook /opt/ansiblepods/linuxgsm/rustserver/install.yml')

            commands.append('chmod -R 777 /opt')

            for command in commands:
                command = command_prefix(data["container_id"], command, 'root')
                os.system(command)

            # Copy over the config.
            command = "docker cp {}/lib/confs/rustserver.cfg {}:/home/rustserver/lgsm/config-lgsm/rustserver/rustserver.cfg".format(self.app_settings["app_dir"], self.container)
            os.system(command)

            print("Get copy of the config or edit lib/confs/rustserver.conf and do a --install=\"rustserver\" --config\"<config_file_full_path>\" --container=\"<id/name>\" ")
        except Exception as e:
            print("Failed to create container: {}".format(str(e)))
            data["status"] = "Failed to create container. {}".format(str(e))

        return data

    def start(self):
        # Currently disabled until environment variables figured out.
        command = "docker cp {} {}:/home/rustserver/lgsm/config-lgsm/rustserver/rustserver.cfg".format(self.config_file, self.container)
        os.system(command)
        command = "ansible-playbook /opt/ansiblepods/linuxgsm/rustserver/start.yml"
        command = command_prefix(self.container, command, 'rustserver')
        print(command)
        os.system(command)

    def stop(self):
        # Currently disabled until environment variables figured out.
        command = "ansible-playbook /opt/ansiblepods/linuxgsm/rustserver/stop.yml"
        command = command_prefix(self.container, command, 'rustserver')
        print(command)
        os.system(command)


class Valheim:
    def __init__(self, image=None, app_settings=None, container=None, config_json=None, app_dir=None, config_file=None):
        self.image = image
        self.container = container
        self.config_json = config_json
        self.app_dir = app_dir
        self.app_settings = app_settings

        if image is None:
            self.image = ""
        else:
            self.image = image

        if config_json is None:
            self.config_json = ""
        else:
            self.config_json = config_json

        if container is None:
            self.container = ""
        else:
            self.container = container

        if app_dir is None:
            self.app_dir = ""
        else:
            self.app_dir = app_dir

        if config_file is None:
            self.config_file = ""
        else:
            self.config_file = config_file

        if app_settings is None:
            self.app_settings = ""
        else:
            self.app_settings = app_settings

    def install(self):
        data = {}
        game_port = random_port()
        query_port = random_port()

        command = "docker run -td -p {0}:{0}/udp -p {0}:{0}/tcp -p {1}:{1}/tcp -p {1}:{1}/udp {2}".format(game_port, query_port, self.image)

        try:
            container_id = check_output(command, shell=True).decode('ascii')
            container_id = container_id.rstrip("\n")

            data["container_id"] = container_id
            data["game_port"] = game_port
            data["query_port"] = query_port

            print(str(data))
            # Insert New Record into database.
            commands = []
            commands.append("echo 'export server_port={}' >> /etc/bashrc".format(game_port))
            commands.append("echo 'export query_port={}' >> /etc/bashrc".format(query_port))
            commands.append("echo 'echo -e \'Welcome to Storm Pods! Server Port: {} Query Port: {} \'' >> /etc/bashrc".format(game_port, query_port))
            commands.append('git clone https://github.com/thegreatstorm/ansiblepods.git /opt/ansiblepods > /dev/null')
            commands.append('ansible-playbook /opt/ansiblepods/linuxgsm/valheim/requirements.yml')
            commands.append('ansible-playbook /opt/ansiblepods/linuxgsm/valheim/setup.yml')
            commands.append('ansible-playbook /opt/ansiblepods/linuxgsm/valheim/install.yml')
            commands.append('chmod -R 777 /opt')

            for command in commands:
                command = command_prefix(data["container_id"], command, 'root')
                os.system(command)

        except Exception as e:
            print("Failed to create container: {}".format(str(e)))
            data["status"] = "Failed to create container. {}".format(str(e))

        return data

    def start(self):
        # Currently disabled until environment variables figured out.
        command = "docker cp {} {}:/home/rustserver/lgsm/config-lgsm/valheim/valheim.cfg".format(self.config_file, self.container)
        os.system(command)
        command = "ansible-playbook /opt/ansiblepods/linuxgsm/valheim/start.yml"
        command = command_prefix(self.container, command, 'rustserver')
        print(command)
        os.system(command)