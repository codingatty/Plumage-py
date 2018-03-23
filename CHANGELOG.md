# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).


## [1.3.0](https://github.com/codingatty/Plumage-py/releases/tag/V1.3.0) - 2018-03-22 (*"Delius"*)
- Support for Python 3; specifically, tested on [Python 2.7.14](https://www.python.org/downloads/release/python-2714/) and [Python 3.6.4](https://www.python.org/downloads/release/python-364/)
- Development environment upgraded to [lxml](http://lxml.de/) 4.2.0

Because the only change in this release is to support Python 3, there is no corresponding release 1.3.0 for
[Plumage-dotnet](https://github.com/codingatty/Plumage-dotnet), which remains at [V1.2.0](https://github.com/codingatty/Plumage-dotnet/releases/tag/V1.2.0).

## [1.2.0](https://github.com/codingatty/Plumage-py/releases/tag/V1.2.0) - 2018-01-28 (*"Cloudbusting"*)
- API change: single-instance values and multiple-instance values are broken into two data fields (see release notes for details)
- XSL relaxation: accept and ignore blank or empty lines
- [Software Package Data Exchange](https://spdx.org/) (SPDX) support
- Upgrade to [Plumage-XSL](https://github.com/codingatty/Plumage) [V1.1.1](https://github.com/codingatty/Plumage/releases/tag/V1.1.1) (for SPDX support)
- Self-test removed in favor of unit testing

## [1.1.0](https://github.com/codingatty/Plumage-py/releases/tag/V1.1.0) - 2016-05-23 (*"The Big Sky"*)
- Support for ST.96 V 2.2.1 (adopted by the US PTO on May 6, 2016)
- Added diagnostic where older ST.96 1-D3 is encountered
- small bug fix from [Plumage V1.0.1](https://github.com/codingatty/Plumage/releases/tag/V1.0.1)

## [1.0.0](https://github.com/codingatty/Plumage-py/releases/tag/V1.0.0) - 2016-05-17 (*"And Dream of Sheep"*)
- Initial formal release of the Python implementation of Plumage. This is essentially the release I've been using for about a year; just formalizing the release.
- Support for ST.66 (release level not identified by USPTO) and ST.96, release 1_D3 
