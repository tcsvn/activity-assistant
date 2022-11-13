# Activity Assistant

> Collect, evaluate and predict Activities of Daily Living from within Home Assistant.

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/tcsvn/activity-assistant/Publish%20master%20CI?style=flat-square)
![Supports amd64 Architecture](https://img.shields.io/badge/amd64-yes-green?style=flat-square)
![Supports i386 Architecture](https://img.shields.io/badge/i386-no-orange?style=flat-square)
![Supports armv7 Architecture](https://img.shields.io/badge/armv7-yes-green?style=flat-square)
![Supports aarch64 Architecture](https://img.shields.io/badge/aarch64-yes-green?style=flat-square)
![License](https://img.shields.io/pypi/l/pyadlml?style=flat-square)

Activities of Daily living (ADLs) such as eating, working, sleeping and Smart Home device readings are recorded by its inhabitants. The projects aim is to predict inhabitants activities from device recordings. Activity Assistant is a platform that streamlines the process of data collection. Multiple devices and subjects may be tracked using an additional android or the Home Assistants companion app. Furthermore, Activity Assistant (will) support the deployment of trained models and running predictions in real-time. A (future) Home Assistant integration offers user a novel activity-based abstraction to automate their homes upon.

<p align="center">
  <img width="80%"  src=media/showreal.gif?raw=true>
</p>

## Installation

The installation of this add-on is pretty straightforward and not different in comparison to installing any other Hass.io add-on.

1. add the repository to the addon-store by pasting `https://github.com/tcsvn/hassio-activity-assistant` into the manage add-on repositories dialog
2. Ensure that Home Assistant is using the [recorder](https://www.home-assistant.io/integrations/recorder/) integration for Activity Assistant to successfully query data
3. Search for the "Activity Assistant" addon-on in the Hass.io add-on store and install it.
4. Start the "Activity Assistant" add-on.
5. Check the logs of the add-on to see if everything went well.
6. Ready to go!

_For a guide on how to use please refer to the Documentation (to come)_

## Features

- [x] Creating and running experiments to record ADLs and device events
- [x] Activity annotation using an android app
- [x] Activity annotation using Home Assistant input_selects/booleans
- [x] Device and Activity to room assignment
- [x] Interactive dashboard for running experiments and prevously recorded datasets
- [ ] Generate prior activity distributions with a "typical week" calendar widget
- [ ] Dask nodes for distributed computation
- [ ] Upload and deployment of trained models via the web-interface
- [ ] Home Assistant integration: custom entity card for each person

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

If you are using Activity Assistant for puplications please consider citing the package

```
@software{activity-assistant,
  author = {Christian Meier},
  title = {Activty Assistant},
  url = {https://github.com/tcsvn/activity-assistant},
  version = {0.0.3-alpha},
  date = {2020-01-12}
}
```

## License

MIT © [tcsvn](http://deadlink)

[buy-me-a-coffee-shield]: https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white
[buy-me-a-coffee]: https://www.buymeacoffee.com/tscvn
