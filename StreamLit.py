# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 22:32:56 2022

@author: kevin
"""

import streamlit as st 
from PIL import Image 
import matplotlib.pyplot as plt 
import matplotlib
matplotlib.use("Agg")
import seaborn as sns
import pandas as pd 
import numpy as np
import requests
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from urllib.request import urlopen
import json

DATA_URL = ("life-expectancy-of-women-vs-life-expectancy-of-women.csv")


placeholder = st.empty()
with placeholder.container():
    st.markdown("# Nous vous souhaitons la bienvenue")
    st.markdown("Projet analyse sur Python composé de DA CRUZ Mathis, ESTEVES Kévin, SIVANANTHAN Sarankan")
    st.markdown('''<p> <u> Sujet </u> : Espérance de vie </p>''', unsafe_allow_html= True)
    st.markdown('''<p> <u> Problématique </u> : Comment expliquer les disparités/inégalités d'espérance de vie ? </p>''', unsafe_allow_html= True)          


df2021 = pd.read_csv(DATA_URL, delimiter = ",", decimal = ".")
df2  = pd.read_csv(DATA_URL, delimiter = ",", decimal = ".")
year_2021_mask =  df2["Year"] == 2021
            
            
europe_mask = df2["Entity"] == "Europe" 
america_mask = df2["Entity"] == "Northern America" 
africa_mask = df2["Entity"] == "Africa"
oceania_mask = df2["Entity"] == "Oceania" 
asia_mask = df2["Entity"] == "Asia" 
latin_mask = df2["Entity"] == "Latin America and the Caribbean"
            
continents = europe_mask | america_mask | africa_mask | oceania_mask | asia_mask | latin_mask
male_life_expectancy = df2[year_2021_mask][continents]['Life expectancy - sex: male - age: at birth - variant: estimates']
female_life_expectancy = df2[year_2021_mask][continents]['Life expectancy - sex: female - age: at birth - variant: estimates']
continents = df2[continents][year_2021_mask]["Entity"]

def area_status(row):
    row = str(row)
    if row.endswith("000"):
        return 'State'
    elif row == '0':
        return 'Country'
    else:
        return 'County'    

df_usa = pd.read_csv('U.S._Life_Expectancy.csv')
df_usa_code = pd.read_csv('us-state-code.csv')
df_counties_code = pd.read_csv('us_counties_code.csv', converters = { 'fips' : lambda x : str(x) })
by_counties_mask = df_usa['County'] != '(blank)'
df10 = pd.read_csv("Life_Expectancy_Data.csv")
df9 = pd.read_csv("life-expectancy-of-women-vs-life-expectancy-of-women.csv")
continents_csv = pd.read_csv("continents2.csv")
df9['Life expectancy'] = (df2['Life expectancy - sex: female - age: at birth - variant: estimates'] + df2[ 'Life expectancy - sex: male - age: at birth - variant: estimates']) / 2

df9.rename(columns = {'Entity':'Country'}, inplace = True)

continents_csv.rename(columns = {'name':'Country'}, inplace = True)

df9['Continent'] = pd.merge(df9, continents_csv, on='Country', how='left')['region']
df9 = df9.dropna()
df10['Continent'] = pd.merge(df10, continents_csv, on='Country', how='left')['region']
df8 = df10.dropna(subset=['GDP' , 'Life expectancy ' , 'Population' , 'Continent'])
df8 = df8.sort_values(by = ['Country' , 'Year'])
diapo = st.slider("Slider", min_value=1, max_value=25)

if(diapo == 1):

    option = st.selectbox("Enter a year...",np.arange(1950,2022))
    
    
    
    df2021["Code"] = df2021["Code"].astype(str)
    df2021 = df2021[df2021["Year"] == option]
    df2021_3 = df2021.drop(df2021[(df2021["Code"].map(len) != 3)].index)
    df2021_3 = df2021_3.drop(df2021_3[(df2021_3["Code"] == "nan")].index)
    
    
    geojson_url = "https://raw.githubusercontent.com/python-visualization/folium/main/examples/data/world-countries.json"
    response = requests.get(geojson_url)
    geojson = response.json()
    
    expectancy_all = df2021_3.iloc[:,3:5]
    mean_expectancy_all = np.mean(expectancy_all, axis = 1)
    df2021_3["Life expectancy for all"] = np.round(mean_expectancy_all,2)
    
    M = folium.Map(min_zoom= 0, control_scale=True)
    
    code_index = df2021_3.set_index("Code")
    
    choropleth = folium.Choropleth(
        geo_data= geojson,
        data = df2021_3,
        fill_color = 'RdYlGn',
        columns = ["Code", "Life expectancy for all"],
        key_on = "feature.id",
        legend_name = "Evolution of life expectancy over years",
        threshold_scale = [15,30,40,50, 60, 70, 80,90]).add_to(M)
    for i in choropleth.geojson.data["features"]:
        try:
            i["properties"]["expectancy"] = code_index.loc[i["id"], "Life expectancy for all"]
        except Exception:
            pass
    choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['name','expectancy']))
    folium.LayerControl().add_to(M)
    
    folium_static(M)
if(diapo == 2):
    male_life_expectancy = df2[df2["Year"] == 2021]['Life expectancy - sex: male - age: at birth - variant: estimates']
    female_life_expectancy = df2[df2["Year"] == 2021]['Life expectancy - sex: female - age: at birth - variant: estimates']
    population = df2[df2["Year"] == 2021]["Population - sex: all - age: all - variant: estimates"]/10000000
    country = df2[df2["Year"] == 2021]["Entity"]
    #figure avec les cercles variables
    fig = px.scatter(x = female_life_expectancy, y = male_life_expectancy, size = population, color = country,
                     labels = {"x" : "Female life expectancy", "y": "Male life expectancy", "color": "Country"},
                     title = "Life expectancy by gender and population in 2021")
    st.plotly_chart(fig)
if(diapo == 3):

    
    #horizontal en baton 
    fig, ax = plt.subplots(figsize = (5,5))
    colors = ["blue", "red"]
    ax = (plt.barh(continents, male_life_expectancy, color = colors[0]),
    plt.barh(continents, female_life_expectancy-male_life_expectancy, left = male_life_expectancy, color = colors[1]),
    plt.xlabel("Life expectancy"),
    plt.ylabel("Continents"),
    plt.title("Difference of life expectancy between gender by continents"),
    plt.legend(["male life expectancy" , "female life expectancy"], loc = 'upper left'))
    st.pyplot(fig)
if(diapo == 4):

    world_mask =  df2["Entity"] == "World"
    years = df2[world_mask]["Year"]
    
    df2["Life expectancy "] = (df2['Life expectancy - sex: female - age: at birth - variant: estimates'] + df2['Life expectancy - sex: male - age: at birth - variant: estimates']) / 2
    fig, ax = plt.subplots(figsize = (5,5))
    ax = (plt.plot(years, df2[africa_mask]["Life expectancy "]),
    plt.plot(years, df2[asia_mask]["Life expectancy "]),
    plt.plot(years, df2[america_mask]["Life expectancy "]),
    plt.plot(years, df2[europe_mask]["Life expectancy "]),
    plt.plot(years, df2[latin_mask]["Life expectancy "]),
    plt.plot(years, df2[oceania_mask]["Life expectancy "]),
    plt.xlabel("Years"),
    plt.ylabel("Life expectancy"),
    plt.title("Life expectancy over years by continents"),
    plt.legend(["Africa" , "Asia", "America", "Europe", "Latin", "Oceania"], loc = 'lower right'))
    st.pyplot(fig)
if(diapo == 5):

    df_health = pd.read_csv("life-expectancy-vs-healthcare-expenditure.csv")
    year_2000_mask = df_health["Year"] == 2000
    year_2019_mask = df_health["Year"] == 2019
    year_2000_to_2019_mask = year_2000_mask | year_2019_mask
    
    life_expectancy = df_health[year_2000_to_2019_mask]["Life expectancy at birth, total (years)"]
    health_expenditure = df_health[year_2000_to_2019_mask]["Current health expenditure per capita, PPP (current international $)"]
    
    year2000_2019 = df_health[year_2000_mask | year_2019_mask]
    #526
    fig = go.Figure()
    for entity, group in year2000_2019.groupby("Entity"):
        if((~np.isnan(group["Current health expenditure per capita, PPP (current international $)"].iloc[0])) and (~np.isnan(group["Current health expenditure per capita, PPP (current international $)"].iloc[1])) and (~np.isnan(group["Life expectancy at birth, total (years)"].iloc[0])) and (~np.isnan(group["Life expectancy at birth, total (years)"].iloc[1]))):
            fig.add_trace(go.Line(x = group["Current health expenditure per capita, PPP (current international $)"], y = group["Life expectancy at birth, total (years)"],marker_symbol = "line-ew",name = entity, hovertemplate = "Country=%s <br> Current health expenditure per capita=%%{x}<br>Life expectancy= %%{y}"%entity))
            x1 = group["Current health expenditure per capita, PPP (current international $)"].iloc[1]
            y1 = group["Life expectancy at birth, total (years)"].iloc[1]
            l = [x1,y1]
            fig.add_trace(go.Scatter(x = [l[0]], y = [l[1]], mode="markers", marker_symbol = "arrow-right",hovertemplate = "Country=%s <br> Current health expenditure per capita=%%{x}<br>Life expectancy= %%{y}"%entity, showlegend = False))
    fig.update_layout(title = "Life expectancy vs. healthcare expenditure, 2000 to 2019")
    fig.update_xaxes(title = "Health expenditure per capita")
    fig.update_yaxes(title = "Life expectancy")
    st.plotly_chart(fig)

if(diapo == 6):

    df_eu_countries = pd.read_csv('eu-countries-sex-le.csv')
    df_countries_code = pd.read_csv('countries_code.csv')
    df_countries_code.rename(columns = {'Alpha-2 code':'geo'}, inplace = True)
    df_eu_countries = df_eu_countries.merge(df_countries_code, on = "geo")
    both_sex_mask = df_eu_countries['sex'] == 'T'
    fig_all = go.Choropleth(locations=df_eu_countries[both_sex_mask]['Alpha-3 code'], locationmode="ISO-3", z = df_eu_countries[both_sex_mask]['OBS_VALUE'], colorscale='YlGn', zmin = 70, zmax = 85)
    male_mask = df_eu_countries['sex'] == 'M'
    female_mask = df_eu_countries['sex'] == 'F'
    fig_male = go.Choropleth(locations=df_eu_countries[male_mask]['Alpha-3 code'], locationmode="ISO-3", z = df_eu_countries[male_mask]['OBS_VALUE'], colorscale='YlGn', zmin = 70, zmax = 85)
    fig_female = go.Choropleth(locations=df_eu_countries[female_mask]['Alpha-3 code'], locationmode="ISO-3", z = df_eu_countries[female_mask]['OBS_VALUE'], colorscale='YlGn', zmin = 70, zmax = 85)
    
    fig = make_subplots(rows = 1, cols = 3, start_cell= "top-left", specs = [[{"type" : "choropleth"},{"type": "choropleth"},{"type" : "choropleth"}]], subplot_titles= ['Life expectancy by European countries',' Male life expectancy by European countries', ' Female life expectancy by European countries'])
    fig.add_trace(fig_all, row = 1, col = 1)
    fig.update_layout(title = {"text" : 'Life expectancy by European countries - 2020'}, title_y =  0.1, title_x = 0.5)
    #fig.add_annotation(text = "Life expectancy by European countries", row = 1, col =1)
    fig.add_trace(fig_male, row = 1, col = 2)
    #fig.update_layout(title2 = {"text" : 'Male life expectancy by European countries'})
    #fig.update_layout(geo = {"scope": "europe"})
    fig.add_trace(fig_female, row=1, col = 3)
    #fig.update_layout(title3 = {"text" : 'Female life expectancy by European countries'})
    fig.update_layout(geo = {"scope": "europe"}, geo2  = {"scope": "europe"}, geo3 = {"scope": "europe"})
    #fig.update_layout(title = "Life expectancy by European countries", title2  = "Male life expectancy by European countries", title3 = "Female life expectancy by European countries")
    fig.update_annotations(font_size = 10) 

    st.plotly_chart(fig)
    
if(diapo == 7):
    


    df_usa = df_usa.merge(df_usa_code, on = "State")
    by_states_mask = df_usa['County'] == '(blank)'

    fig_usa = px.choropleth(locations=df_usa[by_states_mask]['Abbreviation'], locationmode="USA-states", color=df_usa[by_states_mask]['Life Expectancy'], color_continuous_scale='YlGn', scope="usa", title = "Life expectancy by states - US - 2019")
    fig_usa.update_layout(coloraxis_colorbar=dict(
        title="Life Expectancy",
        thicknessmode="pixels",
        lenmode="pixels",
        yanchor="top",y=1,
        ticks="outside",
    ))
    
    st.plotly_chart(fig_usa)
if(diapo == 8):

    df_usa_counties = df_usa[by_counties_mask]
    df_usa_counties = df_usa_counties.dropna(subset=['County', 'Life Expectancy'])
    df_usa_counties = df_usa_counties.groupby(by='County')['Life Expectancy'].mean()
    df_usa_counties = df_usa_counties.reset_index()
    df_usa_counties['Life Expectancy'] = round(df_usa_counties['Life Expectancy'],1)
    df_usa_counties[['County','State Code']] = df_usa_counties.County.str.split(",",expand=True)
    df_usa_counties = df_usa_counties.merge(df_counties_code, on = "County")
    
    import plotly.graph_objects as go
    from urllib.request import urlopen
    import json
    
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    
    fig = go.Figure(go.Choroplethmapbox(geojson=counties, locations=df_usa_counties['fips'], z=df_usa_counties['Life Expectancy'],
                                        colorscale="YlGn", zmin=74, zmax=83,
                                        marker_opacity=0.5, marker_line_width=0))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=3, mapbox_center = {"lat": 37.0902, "lon": -95.7129}, title = {"text" : 'Life expectancy by US counties - 2020'}, title_y =  1, title_x = 0.1)
    #fig.update_layout(margin={"r":0.75,"t":0.75,"l":0.75,"b":0.75})
    
    st.plotly_chart(fig)
if(diapo == 9):
    df_usa_unemployment = pd.read_csv('Unemployment_2000.csv')
    df_usa_unemployment['Status'] = df_usa_unemployment['FIPS_code'].map(area_status)
    
    state_mask = df_usa_unemployment['Status'] == 'State'
    df_usa_unemployment_by_state = df_usa_unemployment[state_mask]
    
    fig_usa_unemployment_by_state = px.choropleth(locations=df_usa_unemployment_by_state['State'], locationmode="USA-states", color=df_usa_unemployment_by_state['Unemployment_rate_2000'], color_continuous_scale='Viridis', scope="usa")
    fig_usa_unemployment_by_state.update_layout(coloraxis_colorbar=dict(
        title="Unemployment rate",
        thicknessmode="pixels",
        lenmode="pixels",
        yanchor="top",y=1,
        ticks="outside"
    ) , title = {"text" : 'Unemployment rate by US state - 2000'})
    st.plotly_chart(fig_usa_unemployment_by_state)
if(diapo == 10):

    df_usa_education = pd.read_csv('Education_1970.csv')
    df_usa_education['Status'] = df_usa_education['Federal Information Processing Standards (FIPS) Code'].map(area_status)
    state_mask = df_usa_education['Status'] == 'State'
    df_usa_education_by_state = df_usa_education[state_mask]
    fig_usa_education_by_state = px.choropleth(locations=df_usa_education_by_state['State'], locationmode="USA-states", color=df_usa_education_by_state['Percent of adults with less than a high school diploma, 1970'], color_continuous_scale='balance', scope="usa")
    fig_usa_education_by_state.update_layout(coloraxis_colorbar=dict(
        title="Without degree",
        thicknessmode="pixels",
        lenmode="pixels",
        yanchor="top",y=1,
        ticks="outside"
    ) , title = {"text" : 'Rate of american student with less than a high school degree - 1970'})
    
    st.plotly_chart(fig_usa_education_by_state)
    
if(diapo == 11):

    df_usa_poverty = pd.read_csv('PovertyEstimates.csv')
    df_usa_poverty['Status'] = df_usa_poverty['fips'].map(area_status)
    state_mask = df_usa_poverty['Status'] == 'State'
    df_usa_poverty_by_state = df_usa_poverty[state_mask]
    
    fig_usa_poverty_by_state = px.choropleth(locations=df_usa_poverty_by_state['Stabr'], locationmode="USA-states", color=df_usa_poverty_by_state['PCTPOVALL_2020'], color_continuous_scale='Reds', scope="usa")
    fig_usa_poverty_by_state.update_layout(coloraxis_colorbar=dict(
        title="Poverty rate",
        thicknessmode="pixels",
        lenmode="pixels",
        yanchor="top",y=1,
        ticks="outside"
    ) , title = {"text" : 'Poverty in USA by state 2020'})
    
    st.plotly_chart(fig_usa_poverty_by_state)
if(diapo == 12):

    df_usa_covid = pd.read_csv('us_states_covid19_daily.csv')
    date_mask = df_usa_covid['date'] == 20201203
    df_usa_covid['positive_rate'] = df_usa_covid['positive'] / (df_usa_covid['positive'] + df_usa_covid['negative'])
    fig_usa_covid_by_state = px.choropleth(locations=df_usa_covid[date_mask]['state'], locationmode="USA-states", color=df_usa_covid[date_mask]['positive_rate'], color_continuous_scale='Purples', scope="usa")
    fig_usa_covid_by_state.update_layout(coloraxis_colorbar=dict(
        title="Positive Covid Test",
        thicknessmode="pixels",
        lenmode="pixels",
        yanchor="top",y=1,
        ticks="outside"
    ) , title = {"text" : 'Positive Covid Test in US by state - June 2020'})
    
    st.plotly_chart(fig_usa_covid_by_state)
if(diapo == 13):

    df_usa_alcohool = pd.read_csv('alcohool_binge_2003.csv')
    df_usa_alcohool.rename(columns = {'Location':'County'}, inplace = True)
    df_usa_alcohool = df_usa_alcohool.merge(df_counties_code, on='County')
    
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    
    fig = go.Figure(go.Choroplethmapbox(geojson=counties, locations=df_usa_alcohool['fips'], z=df_usa_alcohool['2002 Both Sexes'],
                                        colorscale="Inferno", zmin=10, zmax=50,
                                        marker_opacity=0.5, marker_line_width=0))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=3, mapbox_center = {"lat": 37.0902, "lon": -95.7129}, title = {"text" : 'Alcohol consumption by US counties - 2002'})
    #fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    st.plotly_chart(fig)

if(diapo == 14):
    df_usa_smoking = pd.read_csv('us_smoking.csv')
    df_usa_smoking = df_usa_smoking.merge(df_usa_code, on='State')
    fig_usa_smoking_by_state = px.choropleth(locations=df_usa_smoking['Abbreviation'], locationmode="USA-states", color=df_usa_smoking['smokingRate'], color_continuous_scale='Greys', scope="usa", title = "Proportion of Smokers by State in 2020")
    fig_usa_smoking_by_state.update_layout(coloraxis_colorbar=dict(
        title="smoking rate",
        thicknessmode="pixels",
        lenmode="pixels",
        yanchor="top",y=1,
        ticks="outside"
    ) , title = {"text" : 'Smoking rate in US by state - 2022'})
    
    st.plotly_chart(fig_usa_smoking_by_state)
    
if(diapo == 15):    

    
    fig = px.choropleth(df9, locations="Code", color="Life expectancy",
                        color_continuous_scale=px.colors.diverging.BrBG,
                        projection= "equirectangular",
                        animation_frame="Year",
                        title="World Average Life Expectancy")
    
    st.plotly_chart(fig)
    
if(diapo == 16):


    
    fig = px.scatter(df8, x="Total expenditure", y="Life expectancy ", animation_frame= "Year", animation_group="Country",
               size="Population", color="Continent", hover_name="Country", facet_col="Continent" ,
               size_max=45, range_x=[0,15], range_y=[45,85])
    st.plotly_chart(fig)
    
if(diapo == 17):

    fig = px.scatter(df8, x="GDP", y="Life expectancy ", animation_frame= "Year", animation_group="Country",
               size="Population", color="Continent", hover_name="Country", facet_col="Continent" ,
               log_x=True, size_max=45, range_x=[100,100000], range_y=[25,90])
    fig.update_layout(transition_duration = 5000)
    st.plotly_chart(fig)

if(diapo == 18):

    fig = px.scatter(df8, x="Total expenditure", y="Life expectancy ", animation_frame= "Year", animation_group="Country",
               size="Population", color="Continent", hover_name="Country", facet_col="Status" ,
                size_max=45, range_x=[0,15], range_y=[45,85])
    st.plotly_chart(fig)
if(diapo == 19):
    developed_mask = df10["Status"] == "Developed"
    developing_mask = df10["Status"] == "Developing"
    mask_year_fifteen =  df10["Year"] == 2015
    df1 = df10[mask_year_fifteen & developing_mask]["Life expectancy "]
    df2 = df10[mask_year_fifteen & developed_mask]["Life expectancy "]

    fig, ax = plt.subplots(figsize = (5,5))
    ax = (plt.hist([df1 , df2] , 29 , alpha = 0.5 , stacked = True , label = ["Deloping" , "Developed"]),
    plt.xlabel("Life expectancy"),
    plt.ylabel("count"),
    plt.title("Repartition of life expectancy"),
    plt.legend())
    st.pyplot(fig)
if(diapo == 20):
    year_2015_mask =  df10["Year"] == 2015
    schooling = df10[year_2015_mask]["Schooling"]
    life_expectancy = df10[year_2015_mask]["Life expectancy "]
    fig, ax = plt.subplots(figsize = (5,5))
    ax = (plt.scatter(life_expectancy, schooling, c = -schooling),
          plt.xlabel("Life expectancy"),
          plt.ylabel("Schooling"),
          plt.title("Life expectancy by schooling"))
    st.pyplot(fig)
if(diapo == 21):
    year_2015_mask =  df10["Year"] == 2015
    developing_mask = df10["Status"] == "Developing"
    developed_mask = df10["Status"] == "Developed"
    life_expectancy_inf_60 = df10["Life expectancy "] < 60
    life_expectancy_inf_70 = (df10["Life expectancy "] >= 60) & (df10["Life expectancy "] < 70)
    life_expectancy_inf_80 = (df10["Life expectancy "] >= 70) & (df10["Life expectancy "] < 80)
    life_expectancy_sup_80 = df10["Life expectancy "] > 80
    developing_life_expectancy_by_interval = []
    developing_life_expectancy_by_interval.append(df10[year_2015_mask][life_expectancy_inf_60][developing_mask]["Status"].count()) 
    developing_life_expectancy_by_interval.append(df10[year_2015_mask][life_expectancy_inf_70][developing_mask]["Status"].count())
    developing_life_expectancy_by_interval.append(df10[year_2015_mask][life_expectancy_inf_80][developing_mask]["Status"].count())
    developing_life_expectancy_by_interval.append(df10[year_2015_mask][life_expectancy_sup_80][developing_mask]["Status"].count())
    developed_life_expectancy_by_interval = []
    developed_life_expectancy_by_interval.append(df10[year_2015_mask][life_expectancy_inf_60][developed_mask]["Status"].count()) 
    developed_life_expectancy_by_interval.append(df10[year_2015_mask][life_expectancy_inf_70][developed_mask]["Status"].count())
    developed_life_expectancy_by_interval.append(df10[year_2015_mask][life_expectancy_inf_80][developed_mask]["Status"].count())
    developed_life_expectancy_by_interval.append(df10[year_2015_mask][life_expectancy_sup_80][developed_mask]["Status"].count())
    intervals = ["> 60", "60 - 70", "70 - 80", "< 80"]
    fig, (ax1,ax2) = plt.subplots(1,2,figsize = (5,5), sharey= True)
    ax1.pie(developing_life_expectancy_by_interval, labels = intervals,autopct='%1.2f%%')
    plt.title("Répartition de l'espérance de vie dans les pays en développement")
    ax2.pie(developed_life_expectancy_by_interval, labels = intervals,autopct='%1.2f%%')
    plt.title("Répartition de l'espérance de vie dans les pays développés")
    st.pyplot(fig)
if(diapo == 22):
    df2["Life expectancy "] = (df2['Life expectancy - sex: female - age: at birth - variant: estimates'] + df2['Life expectancy - sex: male - age: at birth - variant: estimates']) / 2
    asia_mask = df2["Entity"] == "Asia" 
    world_mask =  df2["Entity"] == "World"
    years = df2[world_mask]["Year"]
    fig, ax = plt.subplots(figsize = (5,5))
    ax = (plt.plot(years, df2[world_mask]["Life expectancy "]),
    plt.plot(years, df2[asia_mask]["Life expectancy "]),
    plt.xlabel("Years"),
    plt.ylabel("Life expectancy"),
    plt.title("Life expectancy over years by continents"),
    plt.legend(["World", "Asia"], loc = 'lower right'))
    st.pyplot(fig)
if(diapo == 23):
    world_mask =  df2["Entity"] == "World"
    male_life_expectancy = df2[world_mask]['Life expectancy - sex: male - age: at birth - variant: estimates']
    female_life_expectancy = df2[world_mask]['Life expectancy - sex: female - age: at birth - variant: estimates']
    years = df2[world_mask]["Year"]
    fig, ax = plt.subplots(figsize = (5,5))
    ax = (plt.plot(years, male_life_expectancy),
    plt.plot(years, female_life_expectancy),
    plt.xlabel("Years"),
    plt.ylabel("Life expectancy"),
    plt.title("Evolution of life expectancy over years and by gender"),
    plt.legend(["male life expectancy" , "female life expectancy"]))
    st.pyplot(fig)
if(diapo == 24):
    syrian_mask = df10["Country"] == "Syrian Arab Republic"
    syrian_life_expectancy = df10[syrian_mask]["Life expectancy "]
    years = df10[syrian_mask]["Year"]
    fig, ax = plt.subplots(figsize = (5,5))
    ax = (plt.plot(years, syrian_life_expectancy, color = "red"),
    plt.xlabel("Years"),
    plt.ylabel("Life expectancy"),
    plt.title("Evolution of syrian life expectancy over years"))
    st.pyplot(fig)
if(diapo == 25):
    mask_Japan = df10["Country"] == "Japan"
    list_year = df10["Year"].unique()[::-1]
    Japan_life_expectancy = df10[mask_Japan].groupby(by = "Year")["Life expectancy "].mean()
    world_mask =  df10["Country"] == "World"
    fig, ax = plt.subplots(figsize = (5,5))
    ax = (plt.xlabel('Year'),
    plt.ylabel('Life expectancy'),
    plt.title('Life expectancy in Japan'),
    plt.plot(list_year , Japan_life_expectancy))
    st.pyplot(fig)