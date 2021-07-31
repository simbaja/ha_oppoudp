# Oppo UDP-20x

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

Integration for Oppo UDP-20x Bluray players into Home Assistant.

## Installation (Manual)

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `oppo_udp`.
4. Download _all_ the files from the `custom_components/oppo_udp/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Oppo UDP"

## Installation (HACS)

Please follow directions [here](https://hacs.xyz/docs/faq/custom_repositories/), and use https://github.com/simbaja/ha_oppoudp as the repository URL.
## Configuration

Configuration is done via the HA user interface.
### Configuration Notes

1. When installing, the Oppo UDP must be ON so that it can pass the communications test.
2. You should set the standby mode to "Network Standby"

[commits-shield]: https://img.shields.io/github/commit-activity/y/simbaja/ha_oppoudp.svg?style=for-the-badge
[commits]: https://github.com/simbaja/ha_oppoudp/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/simbaja/ha_oppoudp.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Jack%20Simbach%20%40simbaja-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/simbaja/ha_oppoudp.svg?style=for-the-badge
[releases]: https://github.com/simbaja/ha_oppoudp/releases