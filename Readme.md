# activity-assistant
> Collect, evaluate and predict activities of daily living from within homeassistant.

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/tcsvn/activity-assistant/Publish%20dev?style=flat-square)
![Supports aarch64 Architecture](https://img.shields.io/badge/aarch64-yes-green?style=flat-square)
![Supports amd64 Architecture](https://img.shields.io/badge/amd64-yes-green?style=flat-square)
![Supports armhf Architecture](https://img.shields.io/badge/armhf-yes-green?style=flat-square)
![Supports armv7 Architecture](https://img.shields.io/badge/armv7-yes-green?style=flat-square)
![Supports i386 Architecture](https://img.shields.io/badge/i386-yes-green?style=flat-square)
![License](https://img.shields.io/pypi/l/pyadlml?style=flat-square)

Activities of Daily living (ADLs) e.g cooking, working, sleeping and device readings are recorded by smart home inhabitants. The goal is to predict inhabitants activities using device readings. Activity-assistant is a platform that streamlines the process of data collection. It can track selected devices and persons. Using the android app, device readings can be labeled with current activities. Furthermore activity-assistant supports the deployment of trained models running predictions in real-time. A homeassistant integration offers users a way to automate stuff based on activity predictions.

<p align="center">
  <img width="80%"  src=media/showreal.gif?raw=true>
</p>

## Installation

The installation of this add-on is pretty straightforward and not different in comparison to installing any other Hass.io add-on.

1. add the repository to the addon-store by pasting `http://github.com/tcsvn/hassio-activity-assistant` into the manage add-on repositories dialog  
2. Ensure that homeassistant uses sqlite as database and that it is available in the configuration folder (for standard installations this is the case)
3. Search for the "activity-assistant" addon-on in the Hass.io add-on store and install it.
4. Start the "activity-assistant" add-on.
5. Check the logs of the add-on to see if everything went well.
6. Ready to go!

_For a guide on how to use please refer to the Documentation (to come)_

## Features
  - [x] Running experiments for recording activities of daily living
  - [x] Data can be labeled in company with the android app
  - [ ] A running experiment can be visualized yielding insights into the current data collection process
  - [ ] Prior activities can be created by filling out an example week with a calendar widget
  - [ ] Trained models can be uploaded and deployed via the web-interface
  - [ ] Home assistant custom entity card for each person 

## Contributing 
1. Fork it (<https://github.com/tcsvn/activity-assistant/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Related projects
  - [activity-assistant-logger](https://github.com/tcsvn/act_assist_logger) - The android companion app for labeling activities
  - [pyadlml](https://github.com/tcsvn/pyadlml) - A python library for data exploration. Data collected by activity-assistant can be imported with `load_act_assist(path_to_folder)`
  - [homeassistant](https://github.com/todolink) - Homeautomation platform
## Support 
[![Buy me a coffee][buy-me-a-coffee-shield]][buy-me-a-coffee]
  
## License
MIT  © [tcsvn](http://deadlink)


[buy-me-a-coffee-shield]: https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white

[buy-me-a-coffee]: https://www.buymeacoffee.com/tscvn
