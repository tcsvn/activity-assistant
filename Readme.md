# Activity Assistant

> Collect, evaluate and predict Activities of Daily Living from within Home Assistant.

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/tcsvn/activity-assistant/.github/workflows/main.yml?style=flat-square)
![Supports amd64 Architecture](https://img.shields.io/badge/amd64-yes-green?style=flat-square)
![Supports i386 Architecture](https://img.shields.io/badge/i386-no-orange?style=flat-square)
![Supports aarch64 Architecture](https://img.shields.io/badge/aarch64-yes-green?style=flat-square)
![Supports armv7 Architecture](https://img.shields.io/badge/armv7-yes-green?style=flat-square)
![Supports armhf Architecture](https://img.shields.io/badge/armhf-no-orange?style=flat-square)
![License](https://img.shields.io/pypi/l/pyadlml?style=flat-square)

Activities of Daily living (ADLs) such as eating, working, sleeping and Smart Home device readings are recorded by inhabitants. Predicting resident activity from the device event stream enables a variety of
applications. Activity Assistant is a platform that streamlines the data collection process. Multiple devices or subjects are tracked using an additional [Android](https://github.com/tcsvn/activity-assistant-logger) or the Home Assistants companion app. Furthermore, Activity Assistant (will) support the deployment of trained models and running ADL predictions in real-time. A (future) Home Assistant integration offers users a novel activity based abstraction to automate their homes upon.

<p align="center">
  <img width="80%"  src=media/showreal.gif?raw=true>
</p>

## Installation

The installation of this add-on is pretty straightforward and not different to installing any other Hass.io add-on.

1. Add the repository to the addon-store by pasting `https://github.com/tcsvn/hassio-activity-assistant` into the manage add-on repositories dialog
2. Ensure that Home Assistant is using the [recorder](https://www.home-assistant.io/integrations/recorder/) integration for Activity Assistant to successfully connect to the database and query devices
3. Search for the "Activity Assistant" addon-on in the Hass.io add-on store and install the latest release (NOT edge or development).
4. Start the "Activity Assistant" add-on.
5. Check the logs of the add-on to see if everything went well.
6. Ready to go!

_For a guide on how to use please refer to the Documentation (tbd)_

## Features

- [x] Create and run experiments for recording ADLs and device events
- [x] Activity annotation using an android app
- [x] Activity annotation using Home Assistant input_selects and input_booleans
- [x] Device or activity to room assignment
- [x] Interactive dashboard for the running experiment and previously recorded datasets
- [ ] Generate prior activity distributions with a "typical week" calendar widget
- [ ] Dask nodes for distributed computation
- [ ] Upload and deployment of trained models via the web interface
- [ ] Home Assistant integration + custom entity card displaying per person activity predictions

## Contributing

1. Fork it (<https://github.com/tcsvn/activity-assistant/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Related projects

- [Activity Assistant - Logger](https://github.com/tcsvn/act_assist_logger) - The android companion app for labeling activities
- [pyadlml](https://github.com/tcsvn/pyadlml) - A python library offering data exploration methods for ADL datatasets.
- [Home Assistant](https://www.home-assistant.io/) - Homeautomation platform

## Support

[![Buy me a coffee][buy-me-a-coffee-shield]][buy-me-a-coffee]

## How to cite

If you are using Activity Assistant for puplications please consider citing the package.

```
@software{activity-assistant,
  author = {Christian Meier},
  title = {Activty Assistant},
  url = {https://github.com/tcsvn/activity-assistant},
  version = {0.0.4-alpha},
  date = {2023-01-02}
}
```

## License

MIT © [tcsvn](http://deadlink)

[buy-me-a-coffee-shield]: https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white
[buy-me-a-coffee]: https://www.buymeacoffee.com/tscvn
