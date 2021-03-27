![Data Update](https://github.com/tlary/covid_dashboard/actions/workflows/update_data.yml/badge.svg)


# Covid-19 Dashboard for Germany

This repo contains code for a Covid-19 Dashboard for Germany. The data is drawn from the Robert-Koch-Institut (RKI) via an API and updated daily using GitHub Actions and cron.

The app is built with streamlit and deployed on streamlit sharing.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/tlary/covid_dashboard/main/app.py)

# Run locally with Docker

The dashboard webapp can also be run locally using docker. After [installing Docker](https://docs.docker.com/engine/install/), clone the repository, build the image from the Dockerfile and run the container. The app can then be accessed on port 8501. 

```bash
git clone https://github.com/tlary/covid_dashboard.git 
cd covid_dashboard 
docker build -t covid . 
docker run -p 8501:8501 covid 
```

Instead of building the image from the Dockerfile, it can also be pulled from Docker Hub and the app can be accessed by simply running

```bash
docker run -p 8501:8501 tlary94/covid_streamlit
```

