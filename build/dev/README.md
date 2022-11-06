# Activity-assistant

Activity assistant provides a platform for logging and predicting Activities of Daily Living (ADLs) in realtime for home assistant users. This addon version is used for developing the web application.

## Development

#### Setup

- Clone the github repository and navigate into the repos root directory
- Open the folder in vscode and type the command `Dev Containers: Open Folder in Container...`
- Run the task `Start homeassistant`
- Append your public-key (`~/.ssh/id_rsa.pub`) to the build/dev/rootfs/root/.ssh/authorized_keys file
- Add the [activity-assistant](https://github.com/tcsvn/hassio-activity-assistant) repo to the
  [addon store](https://my.home-assistant.io/redirect/supervisor_store/) and install the dev addon
- Add the following entry to your ssh config (`~/.ssh/config`):
  ```
    Host aa_dev
      Hostname 0.0.0.0
      Port 433
      User root
      ForwardAgent yes
      IdentityFile ~/.ssh/id_rsa
      StrictHostKeyChecking no
      UserKnownHostsFile /dev/null
  ```
- Using the remote explorers `aa_dev` ssh entry, attach vscode to the container

#### Notes

- To add a few dummy devices to homeassistant execute the task `Ha cp hass_config into container`
