<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/a-bismor/heater-reader">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Boiler Monitor (via OCR)</h3>

  <p align="center">
    Local service that captures boiler LCD images, extracts temperature readings via OCR, stores them in SQLite, and serves a simple web dashboard for graphs and manual corrections.
    <br />
    <a href="https://github.com/a-bismor/heater-reader"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/a-bismor/heater-reader">View Demo</a>
    &middot;
    <a href="https://github.com/a-bismor/heater-reader/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/a-bismor/heater-reader/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

Boiler Monitor (via OCR) is a local service that captures boiler LCD images, extracts temperature readings via OCR, stores them in SQLite, and serves a simple web dashboard for graphs and manual corrections.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![FastAPI][FastAPI]][FastAPI-url]
* [![Python][Python]][Python-url]
* [![SQLite][SQLite]][SQLite-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* python
  ```sh
  python -m venv .venv
  . .venv/bin/activate
  pip install -r requirements.txt
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/a-bismor/heater-reader.git
   ```
2. Install Python dependencies
   ```sh
   python -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Create a `config.yml` with camera settings

```yaml
capture:
  interval_seconds: 60
  image_root: data/images
  rtsp_url: rtsp://user:pass@camera/stream
  onvif_snapshot_url: http://camera/snapshot.jpg
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Run the API locally:

```sh
uvicorn heater_reader.app:create_app --factory --reload
```

Seed sample readings from fixtures:

```sh
PYTHONPATH=src .venv/bin/python scripts/seed_readings.py --db data/readings.db --json fixtures/readings.json
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Capture loop and OCR ingestion
- [ ] Dashboard charts
- [ ] Manual correction workflow
- [ ] Export and reporting

See the [open issues](https://github.com/a-bismor/heater-reader/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/a-bismor/heater-reader/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=a-bismor/heater-reader" alt="contrib.rocks image" />
</a>



<!-- CONTACT -->
## Contact

dev@bismor.pl

Project Link: [https://github.com/a-bismor/heater-reader](https://github.com/a-bismor/heater-reader)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []()
* []()
* []()

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/a-bismor/heater-reader.svg?style=for-the-badge
[contributors-url]: https://github.com/a-bismor/heater-reader/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/a-bismor/heater-reader.svg?style=for-the-badge
[forks-url]: https://github.com/a-bismor/heater-reader/network/members
[stars-shield]: https://img.shields.io/github/stars/a-bismor/heater-reader.svg?style=for-the-badge
[stars-url]: https://github.com/a-bismor/heater-reader/stargazers
[issues-shield]: https://img.shields.io/github/issues/a-bismor/heater-reader.svg?style=for-the-badge
[issues-url]: https://github.com/a-bismor/heater-reader/issues
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png
[FastAPI]: https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white
[FastAPI-url]: https://fastapi.tiangolo.com/
[Python]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[SQLite]: https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white
[SQLite-url]: https://sqlite.org/
