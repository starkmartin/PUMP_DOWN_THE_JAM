# &#x1F697; &#x1F68C; &#x1F699;  "Pump down the jam" - Predicting traffic density to help you skip the jams &#x1F697; &#x1F68C; &#x1F699; 
# A Data-Science capstone project

This repository is the result of a four week long capstone project phase. It concludes the [neuefische bootcamp Data Science](https://www.neuefische.de/bootcamp/data-science) from January to March 2023. 

**Team members**: [Dr. Christopher Hedemann](https://github.com/chris-hedemann), [Gunnar Oehmichen](https://github.com/Gunnar-Oeh), [Dr. Martin Stark](https://github.com/starkmartin), [Dr. Sarah Wiesner](https://github.com/SarahWiesner)

**Dashboard**
[On herokuapp](https://pump-down-the-jam.herokuapp.com/)

**Presentation-Video**
[On Youtube](https://youtu.be/eCN6kHQ8tjQ)

# 

## The story ##
"Pump down the Jam" aims at predicting daily traffic sums at several junctions within the city of Hamburg, Germany to support an information-based decision about the modes of transportation.
The feasibility of several features in enhancing the predictions were tested: weekdays, public holidays, holiday-seasons, special events the weather forecast!
Our main hypothesis is that people decide on whether they go to work by car the next day by looking at the weather forecast in the evening. In case the prediction is "good" weather, public transport or bike is an appealing option, while rainy, windy or cold days ahead tempt to take the cozy car. 
Furthermore, the choice of tomorrows mode of transportation can be influenced by the traffic density (and thus the probability of traffic jams) to expected.

#
## The product ##
Our main product is a [dashboard](https://pump-down-the-jam.herokuapp.com/) which displays: 
- a map of the junctions, for which daily traffic sums where predicted
- A dropdown list of the junctions
- A weather forecast for Hamburg for tomorrow
- a timeseries-line plot of traffic sums and predtictions of the last seven days and the prediction for tomorrow
- A comparison of tomorrows traffic to the mean of the same weekday of the previous year

The dashboard serves as a proof of concept. As traffic data was only available until 2022, the predictions were modelled for every day of March, 2022.

More Detailed information on the dashboard is found in the dasboard-directory and its [README](./dashboard/README.md)

# &#x2601;
## The data
 Data on traffic was provided by Behörde für Verkehr und Mobilitätswende (Freie und Hansestadt Hamburg). In includes data of 16 traffic counting stations within the city area, separating cars and trucks. It covers the time from 01 January 2012 until 31 December 2022 with a temporal resolution of 1 hour. 

 Weather data comes from the Meteorological Institute, Universität Hamburg. In includes hourly values for air temperature, relative humidity, wind speed and direction, precipitation amount, duration of sunshine, and cloud coverage. 

 Data concerning special events was derived manually from publicly available websites.

Data Wrangling and EDA of traffic and weather data is discussed and done within the notebooks:

- [01_01_traffic_data_wrangling.ipynb](./notebooks/01_01_traffic_data_wrangling.ipynb)
- [01_02_weather_data_wrangling.ipynb](./notebooks/01_02_weather_data_wrangling.ipynb)
- [02_traffic_EDA.ipynb](./notebooks/02_traffic_EDA.ipynb)
- [03_weather_EDA.ipynb](./notebooks/03_weather_EDA.ipynb)
- [04_weather_classification.ipynb](./notebooks/04_weather_classification.ipynb) - where the weather of each day was assigned to one of three classes. Classes were created by distinguishing between favourable and less favourable weather conditions (sunshine, rain, temperature).

# &#x2600; 
 ## The model

Traffic count data was available on an hourly basis. But it was impossible to differ between no traffic and jams. Also processing hourly data was too computation intensive. Therefore daily traffic sums were calculated as the target-value.

#### Baseline-Model
The baseline-model was defined in the script [trafficModules.py](./notebooks/trafficModules.py) as part of the developed package trafficModules. It simply copies the thr traffic-sum from the same day of the previous week.

#### Forecasting with prophet
Traffic-forecasting was modelled with the [prophet](https://facebook.github.io/prophet/) library. Prophet performs time series forecasting for data with strong seasonality effects and automatically decomposes the time series into the different seasonality patterns. Prophet further enabled us to incorporate public holidays and holiday seasons as regressors. Further linear predictors such as events or weather can also be incorporated. 

So we tested the performance of three different sets of weather data as explanatory variables within the prophet forecasting procedure.

- Baseline Model
- basic Prophet without further regressors
- Prophet with public holidays
- Prophet with public holidays and categorical weather data
- Prophet with public holidays and numerical weather data
- Prophet with extended holiday data
- Prophet with extended holiday data and categorical weather data
- Prpohet with extended holiday data and numerical weather data
- Prophet with extended holiday data and special events
- Prophet with extended holiday data, special events and categorical weather data
- Prpohet with extended holiday data, special events and numerical weather data

1. The model comparisons where performed using the code in [experiment_blueprint.ipynb](./notebooks/00_draft/experiment_blueprint.ipynb) with only one of the 16 traffic junctions.
2. A hyperparameter search was performed for each traffic junction using the model-setup, which indicated best performance. It is implemented in the notebook [05_model_selection_and_eval](./notebooks/05_model_selection_and_eval.ipynb). 
3. Now these customized models were trained for each station, and a procedure was developed to predict traffic for each station for the next day (of march 2022). This also included comparing the prediction with the mean of all the same weekdays from the previous year ([06_final_prediction_stations.ipynb](./notebooks/06_final_prediction_stations.ipynb)).

## Results
These comparisons led to the conclusion, that the basic prophet Model without any weather data included and just the few german holidays was the best performing model.
So local events and school holiday seasons did not have a positive impact after the basic prophet already accounted for the seasonality. Also weather variables could already be represented by the seasonality. A more thorough look at the model comparisons can be found within the [presentation](./Pump%20Down%20the%20Jam.pdf).

## Requirements:

- pyenv with Python: 3.9.6

### Setup

Use the requirements file in this repo to create a new environment.

```BASH
make setup

#or

pyenv local 3.9.6
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

The `requirements.txt` file contains the libraries needed for deployment.
