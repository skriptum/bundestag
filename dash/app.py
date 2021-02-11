
#file for everything related to exploration and graphs

import pandas as pd
import json
from collections import Counter

import plotly.express as px
from plotly.graph_objects import Bar 

import dash
import dash_core_components as dcc 
import dash_html_components as html
from dash.dependencies import Input, Output, State


#read in the data

#shapefiles as geojson
with open("data/geometrie2.geojson") as f:
    geojs = json.load(f)

#wahlkreise
wahl_df = pd.read_csv("data/wahlkreise.csv")
wahl_df = wahl_df.drop(columns = ["Unnamed: 0"])

#twitter daten
t_df = pd.read_csv("data/accounts_data.csv")
t_df = t_df.drop(columns = ["Unnamed: 0"])
#t_df = t_df.set_index("name_id")

bg_col = "#f7f7f7"

c_map = {
            '(?)':bg_col,
            "bundestag": "#004d4d",
            "cdu": "rgba(37, 35, 33, 0.7)",
            "spd": "rgba(255, 25, 25, 0.7)",
            "gruene": "rgba(66, 127, 26, 0.7)",
            "afd": "rgba(76, 156, 227, 0.7)",
            "fdp": "rgba(255, 217, 15, 0.7)",
            "linke": "rgba(196, 25, 25, 0.7)",
            "csu": "rgba(153, 177, 187, 0.7)",
        }

tab_selected_style = {
    "background-color": bg_col,
    "border-top": "3px solid #ff9900",
    "border-left": "3px solid #ff9900",
    "border-right": "3px solid #ff9900",
}

tab_selected_style_left = {
    "background-color":bg_col,
    "border-top": "3px solid #ff9900",
    "border-right": "3px solid #ff9900",
}

tab_selected_style_right = {
    "background-color":bg_col,
    "border-top": "3px solid #ff9900",
    "border-left": "3px solid #ff9900",
}

tab_style = {
    "text-align": "center",
    "border-bottom": "3px solid #f8810b",
}
#deutschlandkarte
def figure_generator(dataframe, color_column = "twitter"):

    c_map = {
            "CDU": "black",
            "SPD": "rgba(255, 25, 25, 1)",
            "GRueNE": "rgba(66, 127, 26, 1)",
            "AfD": "cornflowerblue",
            "FDP": "gold",
            "DIE LINKE": "#b30000",
            "CSU": "grey",}

    fig = px.choropleth_mapbox(
        dataframe, geojson = geojs, 
        featureidkey = "properties.WKR_NR", 
        locations = "WKR_NR", 
        custom_data= ["wahlkreis", "Namen", "name_id"],
        color = color_column, color_discrete_map=c_map,
        opacity=0.5,
        )

    fig.update_traces(
        hovertemplate = "<b>Abgeordnete/r : %{customdata[1]}</b>  <br>%{customdata[0]} <br>Twitter: %{customdata[2]} "
    )


    margins = {"t": 0,"b": 0, "l": 0, "r": 0}

    fig.update_layout(
        margin = margins,
        autosize = True,

        mapbox = {
        "center": {"lon": 10.447 , "lat": 51.1633},
        "zoom": 4.7 },

        mapbox_style = "carto-positron",
        showlegend = False
        )
    return fig

#hashtags
def get_hashtags(dataframe):

    """ extract the hastgas out of a given dataframe , not a row
        returns the all hashtags and their counts"""
    hs = dataframe.hashtags.dropna()
    hs = hs.apply(lambda x: x.split(", "))
    hs = hs.explode()
    hs = hs.value_counts()

    hs = hs.mask(hs.index == "")
    hs = hs.dropna()

    hs = hs[:10]

    fig = px.bar(x = hs.index, y = hs.values, color = hs.values, 
        color_continuous_scale = px.colors.sequential.Blugrn, height = 300)
    
    fig.update_traces(texttemplate = "#%{x}", textposition = "auto", hovertemplate = "<b>#%{x}</b> : %{y} Mal")
    
    margins = {"r":0, "l": 0, "t": 0, "b": 0}
    fig.update_layout(
        margin = margins,
        plot_bgcolor = bg_col,
        paper_bgcolor = bg_col,
        coloraxis_showscale = False,
        bargap = 0.1,
    )

    fig.update_xaxes(visible = False, fixedrange = True)
    fig.update_yaxes(visible = False, fixedrange = True)

    return fig

#kategorisierer 
def nutzungsart(t_df, user_row):
    """ func to get the usage behavior of user, takes as input a row,
    returns a label and description"""

    limit_1 = t_df.tweet_rate.describe()["75%"] #meinungsmacher
    limit_2 = t_df.retweet_rate.describe()["75%"] # verbreiter
    limit_3 = t_df.replie_rate.describe()["75%"] # kommunizierer

    if user_row.replie_rate.item() > limit_3:
        text = f"{round(user_row.replie_rate.item() * 100)}% der tweets sind antworten auf andere Nutzern"
        return ("Kommunizierer", text )

    elif user_row.retweet_rate.item() > limit_2:
        text = f"{round(user_row.retweet_rate.item() * 100)}% der tweets sind retweets von anderen Nutzern"
        return ("Verbreiter", text)

    elif user_row.tweet_rate.item() > limit_1:
        text = f"{round(user_row.tweet_rate.item() * 100)}% der tweets sind eigene Meinungen"
        return ("Meinungsmacher", text)

    else:
        text = "nutzt alle funktionen ungefähr gleichviel, nichts sticht heraus"
        return("Allesnutzer", text)

#
def sentiment(user_row):
    sent = user_row.avg_sent.item()

    sent_colors = {
        "Gutmütig": "#376A16CC",
        "Grummel": "#CF492DCC",
        "neutral": "#f0ead6CC"
    }
    if sent > 0.1:
        text = "∅ eher gutgelaunt"
        bez = "Gutmütig"

    elif sent < -0.5:
        text = "∅ eher schlechtgelaunt"
        bez = "Grummel"
    else:
        text = "neutral /nicht einordbar"
        bez = "neutral"
    return (bez,text, sent_colors[bez])

#function returns a bar with the top users in the specified metric
def color_bar(df, col, c_map, typus = "Anzahl", start = 0, stop = 10):

    sorted = df.sort_values(by = col, ascending = False)
    sorted = sorted[sorted.num_tweets > 5]
    sorted = sorted.reset_index()
    sorted = sorted[start:stop]
    
    margins = {"t": 0, "r": 10, "l": 10, "b": 0}
    
    fig = px.bar(
        sorted, y = col, color="partei", #to change layout to quer y = col
        color_discrete_map=c_map, custom_data=["name_id", col], 
        labels = {"_index": "platzierung"},
        )
    
    fig.update_layout(
        margin = margins, 
        paper_bgcolor = bg_col,
        plot_bgcolor = bg_col, 
        showlegend = False
    )
    if typus == "Anzahl":
        fig.update_traces(hovertemplate = "%{customdata[0]} <br> Anzahl: %{customdata[1]} ", 
            texttemplate = "%{customdata[0]}", textposition= "auto")
    elif typus == "Anteil":
        fig.update_traces(hovertemplate = "%{customdata[0]} <br> Anteil: %{customdata[1]} ", 
            texttemplate = "%{customdata[0]}", textposition= "auto")

    fig.update_xaxes(visible= False, fixedrange = True, dtick = 1)
    fig.update_yaxes(visible= True, fixedrange = True, title_text = typus)
    return fig

#returns treemap from party followers
def get_treemap(dataframe, c_map):
    """ function to get treemap figure, return px.fig"""

    fig = px.treemap(
        dataframe, path = ["bundestag", "partei", "name_id"], values = "num_followers", 
        color = "partei", color_discrete_map = c_map, 
        #custom_data=["name_id"], #height=500,
        )

    margins = {"t": 20, "r": 0, "l": 0, "b": 0}
    fig.update_layout(margin = margins, paper_bgcolor= bg_col, plot_bgcolor = bg_col)

    fig.update_traces(hovertemplate = "%{label} <br> Follower: %{value}")

    return fig

#horizontal
def horizontal(dataframe, partei, c_map):


    anzahl = {
        "bundestag": 709,
        "spd": 152,
        "cdu": 200,
        "fdp": 80,
        "afd": 88,
        "linke": 69,
        "gruene":67,
        "csu": 46
    }

    zahl = sum(dataframe.partei == partei)
    if partei == "bundestag":
        zahl = len(dataframe)
    prozent = int(zahl /anzahl[partei] * 100)

    fig = px.bar(
        color = [c_map[partei]], opacity=0.5, 
    )
    fig.add_trace(
        Bar(x = [anzahl[partei]], marker = dict(color = c_map[partei], opacity = 0.5, line_color = "black"), hovertemplate = "MdBs: %{x}")
    )
    fig.add_trace(
        Bar(x = [zahl], marker = dict(color = [c_map[partei]], line_color = "black"), hovertemplate = "MdBs mit Twitter: %{x}", 
        text = f"{partei}-Mitglieder mit Twitter: {prozent} %", textposition = "auto"),
    )

    margins = {"t": 0, "r": 0, "l": 10, "b": 5}
    fig.update_layout(barmode = "overlay", margin = margins,
        plot_bgcolor= bg_col, showlegend= False, paper_bgcolor = bg_col, height = 100)

    fig.update_yaxes(visible = False, fixedrange = True)
    fig.update_xaxes(visible = False, fixedrange = True)
    return fig

#positionsbestimmer
def get_pos(search_column, value):
    """function to get position of a value in column and a corespoding color """
    column = search_column.sort_values(ascending = False, ignore_index = True)
    i = column[column == value].index[0]+1
    l = len(column)

    colors = ["#376A16CC","#A7C306CC","#E0CD20CC","#D58B10CC","#CF492DCC"]

    #returns the füfntel in which the value lies to index the color list
    cindex = int(i/(l/5))
    c = colors[cindex]

    text = html.P(f"Platz {i}", style = {"text-decoration": "underline"})
    return (text,c)

#user div generation
def user_generator(df, user, c_map):
    row = df[df.name_id == user]

    #noch keine tweets falls
    if row.num_tweets.item() == 0:
        pos_flws = get_pos(df.num_followers, row.num_followers.item())
        pos_fling = get_pos(df.num_following, row.num_following.item())
        pos_ts = get_pos(df.num_tweets, row.num_tweets.item())


        div = html.Div( children = [

            html.H4("Twitter Profil:"),

            #user profile
            html.Div(className = "row", children = [
                html.Div(className = "nine columns bare_container", children = [
                    dcc.Markdown(f"""#### **{row.name.item()}**    *{row.name_id.item()}* """),

                    html.P(row.desc.item()),
                ]),
                html.Div(children = [
                    html.Img(src = row.img.item(), 
                    style = {"height": "120px", "width": "120px", "border-radius":"50%", "margin": "10px", "border": "1px solid"})
                ])
            ]),
            #first row
            html.Div(className = "row", children = [
                html.Div(className = "four columns bare_container", children = [
                    html.B("Abonnenten"),
                    html.P(row.num_followers),
                    html.P(pos_flws[0]),
                ], style = {"background-color": pos_flws[1]}),

                html.Div(className = "four columns bare_container", children = [
                    html.B("hat abonniert"),
                    html.P(row.num_following),
                    html.P(pos_fling[0]),
                ], style = {"background-color": pos_fling[1]}),

                html.Div(className = "one-third column bare_container", children = [
                    html.B("Tweets"),
                    html.P(row.num_tweets),
                    html.P(pos_ts[0]),
                ], style = {"background-color": pos_ts[1]}),
            ]),

            html.Div(className = "bare_container", children = [
                html.B("Hat noch keinen einzigen Tweet gepostet"),
                ]),
            html.A(href = f"https://twitter.com/{user[1:]}", target= "_blank", children = "Profil auf twitter")
        ])

        return div
    
    art = nutzungsart(df, row)
    sent = sentiment(row)

    #falls noch keine hashtags
    if row.hashtags.isna().any():
        hashtags = "MdB hat bisher keine hashtags gepostet"
        h_div = html.Div(className = "six columns bare_container", children = [html.P(hashtags)])

    else:
        hs_list =  row.hashtags.item().split(", ")[:-1] #hashtags from a user row
        hs_nested = Counter(hs_list).most_common(5)
        childs = [html.B("Hashtags"),]
        for tup in hs_nested:
            childs.append(html.P(f"#{tup[0]}: {tup[1]} Mal", style = {"margin-bottom": "-5px"}))

        h_div = html.Div(className = "six columns bare_container", children = childs)
        

    #poses = [get_pos()]
    pos_flws = get_pos(df.num_followers, row.num_followers.item())
    pos_tspd = get_pos(df.ts_perday, row.ts_perday.item())
    pos_fling = get_pos(df.num_following, row.num_following.item())
    pos_ts = get_pos(df.num_tweets, row.num_tweets.item())

    div = html.Div(children = [
        html.Div( children = [

            html.Div(className = "row", children = [
                html.Div(className = "nine columns bare_container", children = [
                    dcc.Markdown(f"""#### **{row.name.item()}**    *{row.name_id.item()}* """),

                    html.P(row.desc.item()),
                ]),
                html.Div(children = [
                    html.Img(src = row.img.item(), 
                    style = {"height": "120px", "width": "120px", "border-radius":"50%", "margin": "10px", "border": "1px solid"})
                ])
            ]),
            #first row
            html.Div(className = "row", children = [
                html.Div(className = "four columns bare_container", children = [
                    html.B("Abonnenten"),
                    html.P(row.num_followers),
                    html.P(pos_flws[0]),
                ], style = {"background-color": pos_flws[1]}),

                html.Div(className = "four columns bare_container", children = [
                    html.B("hat abonniert"),
                    html.P(row.num_following),
                    html.P(pos_fling[0]),
                ], style = {"background-color": pos_fling[1]}),

                html.Div(className = "one-third column bare_container", children = [
                    html.B("Tweets"),
                    html.P(row.num_tweets),
                    html.P(pos_ts[0]),
                ], style = {"background-color": pos_ts[1]}),
            ]),

            #second row
            html.Div(className = "row", children = [
                html.Div(className = "four columns bare_container", children = [
                    html.B("tweets/tag:"),
                    html.P(round(row.ts_perday, 2)),
                    html.P(pos_tspd[0])
                ], style = {"background-color": pos_tspd[1]}
                ),

                html.Div(className = "four columns bare_container", children = [
                    html.B("Laune"),
                    #html.P(sent[0]),
                    html.P(sent[1])
                ], style = {"background-color": sent[2]}),

                html.Div(className = "one-third column bare_container", children = [
                    html.B("Partei"),
                    html.P(row.partei.item()),
                ], style = {"background-color": c_map[row.partei.item()], "color": "white", "border-color": "black"}),
            ]),

            #zuletzt aktualisiert
            html.Div(className = "row", children = [
                html.Div(className = "six columns bare_container", children = [
                    html.B(art[0]),
                    html.P(art[1]),
                ]),

                h_div,
            ]), 
            html.A(href = f"https://twitter.com/{user[1:]}", target= "_blank", 
                children = "Profil auf twitter.com (in neuem Tab)", style = {"color": "#133166"}),
        ]),


    ])
    return div

t_df["bundestag"] = "Abonnenten gesamt:"
df = pd.merge(wahl_df, t_df, how = "inner", on="name_id")


app = dash.Dash(
    __name__, title = "Bundestwitter", meta_tags=[{"name": "viewport", "content": "width=device-width"}],suppress_callback_exceptions=True
    ,)
server = app.server

app.layout = html.Div( children = [

    
    html.Div( children = [


        #second row
        html.Div(className = "six columns", children = [

            #Beschreibung des projekts
            html.Div(className = "pretty_container",children = [
                html.Div( children = [
                    html.H1("Bundestwitter"),

                    dcc.Markdown("""
                    Manchmal fragt man sich ja, was die Bundestagsabgeordneten den
                    ganzen Tag so machen. Anscheinend sehr viel auf twitter sein, etwa 80%
                    der MdBs sind hier angemeldet (im vergleich: nur 5% der Deutschen).
                    Und was machen die da so? Hier ist die Antwort.

                    > Alles hier ist interaktiv gestaltet. Bei einem Klick auf einen Wahlkreis
                    > oder ein Säulendiagramm wird bspw. das Profil des ausgewählten Abgeordneten angezeigt,
                    > beim Rüberfahren mit der Maus weiter Infos  
                    > **Probiers doch mal aus**
                    
                    
                    """)
                ], style = {"padding": "10px"}),
                dcc.Tabs(mobile_breakpoint = 0, children = [

                    dcc.Tab(label = "Wahlkreise", children = [
                        #Kartencontainer
                        html.Div( children = [
                            dcc.Graph(id = "wahl_map",
                                figure = figure_generator(df, "partei_x"),
                                config = {"displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d"]},
                                style = {"height": "500px"}
                            )
                        ], style = {"padding": "0px"}),
                    ], selected_style = tab_selected_style_left, style = tab_style),


                    dcc.Tab(label = "Parteikarte", children = [
                        #Container für Treemap
                        html.Div( children = [

                            dcc.Graph(id = "tree_map",
                                figure = get_treemap(t_df, c_map),
                                config = {"displaylogo": False},
                            ),

                            dcc.Graph(id = "horizontal",
                                config = {"responsive": False, "displayModeBar": False}, 
                                style = {"height": 100}
                            ),
                        
                        ], style = {"padding": "0px"}),
                    ], selected_style = tab_selected_style, style = tab_style),

                    dcc.Tab(label = "Bestenlisten", children = [
                        #colorbar
                        html.Div(className = "row", children = [

                            html.Div(className = "eight columns", children = [
                                html.B("Vergleichskategorie"),
                                dcc.Dropdown(id = "drop1", 
                                        options = [
                                            {"label":"Aktivität (tweets/tag)", "value": "ts_perday" },
                                            {"label":"Anzahl tweets", "value": "num_tweets" },
                                            {"label":"Abonnenten", "value": "num_followers"},
                                            {"label":"Abonniert", "value": "num_following"},
                                            {"label":"Kommunizierer (Anteil Antworten)", "value": "replie_rate"},
                                            {"label":"Meinungsmacher (Anteil Tweets)", "value": "tweet_rate"},
                                            {"label":"Verbreiter (Anteil Retweets)", "value":"retweet_rate" },
                                            
                                        ], value = "ts_perday",
                                        clearable = False, searchable = False,
                                    ),
                            ], style = {"padding": "10px"}),

                            html.Div(className = "four columns", children = [
                                html.B("Partei"),
                                dcc.Dropdown(id = "drop2", 
                                        options = [
                                            {"label":"CDU", "value": "cdu"},
                                            {"label":"SPD", "value": "spd"},
                                            {"label":"Grüne", "value": "gruene"},
                                            {"label":"Linke", "value": "linke"},
                                            {"label":"AfD", "value":"afd" },
                                            {"label":"FDP", "value":"fdp" },
                                            {"label":"CSU", "value":"csu"},
                                        ],
                                        placeholder = "Partei auswählen",  clearable = True, 
                                        searchable = False,
                                    ),
                            ],style = {"padding": "10px"}),
                        ]),


                        html.Div(children = [
                            dcc.Graph(id = "bar1",
                                config = {"responsive": False, "displaylogo": False,  "modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverCompareCartesian"]},
                            ),
                        ]),

                        
                    ],selected_style = tab_selected_style_right, style = tab_style)

                ])
            ],style = {"padding": "0px"}),

        ]),
        
        #third row
        html.Div(className = "six columns", children = [

            #Nutzerauswahl
            html.Div( className = "pretty_container", children = [
                html.H4("Twitter-Profil"),

                html.Div(className = "six columns", children = [
                    dcc.Input(id = "text-input", 
                        type = "text", placeholder = "Nutzername eingeben"
                    ),
                    html.Button("Suche", id = "submit-button", n_clicks = 0),
                ]),

                html.Div(id = "select-out"),
                html.Br(),
            
                html.Div(id = "user-div", children = [
                
                ]),

            ]),
        ]),

        #first row
        html.Div(className = "six columns", children = [



            #container für hashtags
            html.Div(className = "pretty_container", children = [
                dcc.Markdown("""#### Aktuelle Hashtags in der Bundestagsblase"""),
                dcc.Graph(
                    figure = get_hashtags(t_df), config = {"responsive": False, "displayModeBar": False}
                ) 
            ]),
         
        ]),

    ]),

])





#dropwdown on bars callback
@app.callback(
    Output("bar1", "figure"),

    Input("drop1", "value"),
    Input("drop2", "value")
)

def update_bars(kategorie, partei):
    
    if partei is None:
        dataframe = t_df
    else:
        dataframe = t_df[t_df.partei == partei]

    if "rate" in kategorie:
        typus = "Anteil"
    else:
        typus = "Anzahl"
    

    figure = color_bar(dataframe, kategorie, c_map, typus)

    return figure




#user select callback
@app.callback(
    Output("user-div", "children"),
    Output("select-out", "children"),
    Output("text-input", "value"),

    Input("wahl_map", "clickData"),
    Input("submit-button", "n_clicks"),
    Input("bar1", "clickData"),
    Input("tree_map", "clickData"),
    State("text-input", "value"),

)
def user_select(map_click, submit_click, bar1_click, tree_click, text_in):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if "wahl_map" in changed_id:
        user = map_click["points"][0]["customdata"][2]
        
    elif "submit-button" in changed_id:
        user = text_in
        if sum(t_df.name_id == user) == 0:
            return dcc.Markdown(
                f"Nutzer **@{user}** nicht gefunden, achte auf korrekte Groß- und Kleinschreibung \
                     und vergiss nicht das **@**, wie bei *@sigmargabriel* (Beispiel)"
                ), html.Br(), ""

    elif "bar1" in changed_id:
        user = bar1_click["points"][0]["customdata"][0]
    
    elif "tree_map" in changed_id:
        user = tree_click["points"][0]["label"]

    else:
        user = t_df.name_id.sample().item()
        
    profil = user_generator(t_df, user, c_map)
    out = html.Br()#dcc.Markdown(f"**ausgewählt:** {user} ")
    return profil, out, user

#treemap callback
@app.callback(
    Output("horizontal", "figure"),
    Input("tree_map", "clickData"),
)
def update_horizontal(clickData):
    try:
        p = clickData["points"][0]["customdata"][1]
        if p == '(?)':
            p = "bundestag"
    except:
        p = "bundestag"

    figure = horizontal(t_df, p, c_map)
    return figure




if __name__ == "__main__":
    app.run_server(debug=True)
