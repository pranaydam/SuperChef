import streamlit as st
import pandas as pd
import numpy as np
import SessionState
import os
from PIL import Image

import config, rec_sys
from ingredient_parser import ingredient_parser

from word2vec_rec import get_recs

import nltk

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet")


def make_clickable(name, link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = name
    return f'<a target="_blank" href="{link}">{text}</a>'


def main():
    image = Image.open("input/wordcloud.png").resize((680, 150))
    st.image(image)
    st.markdown("# *What's Cooking? :cooking:*")

   
    st.markdown(
        "## Given a list of ingredients, what different recipes can I can make? :tomato: "
    )
  

    st.text("")

    session_state = SessionState.get(
        recipe_df="",
        recipes="",
        model_computed=False,
        execute_recsys=False,
        recipe_df_clean="",
    )

    ingredients = st.text_input(
        "Enter ingredients you would like to cook with (seperate ingredients with a comma)",
        "Sugar, Tea leaf, Milk",
    )
    session_state.execute_recsys = st.button("Give me recommendations!")

    if session_state.execute_recsys:

        col1, col2, col3 = st.beta_columns([1, 6, 1])
        with col2:
            gif_runner = st.image("input/cooking_gif.gif")
        # recipe = rec_sys.RecSys(ingredients)
        recipe = get_recs(ingredients, mean=True)
        gif_runner.empty()
        session_state.recipe_df_clean = recipe.copy()
        # link is the column with hyperlinks
        recipe["url"] = recipe.apply(
            lambda row: make_clickable(row["recipe"], row["url"]), axis=1
        )
        recipe_display = recipe[["recipe", "url", "ingredients"]]
        session_state.recipe_display = recipe_display.to_html(escape=False)
        session_state.recipes = recipe.recipe.values.tolist()
        session_state.model_computed = True
        session_state.execute_recsys = False

    if session_state.model_computed:
        # st.write("Either pick a particular recipe or see the top 5 recommendations.")
        recipe_all_box = st.selectbox(
            "Either see the top 5 recommendations or pick a particular recipe ya fancy",
            ["Show me them all!", "Select a single recipe"],
        )
        if recipe_all_box == "Show me them all!":
            st.write(session_state.recipe_display, unsafe_allow_html=True)
        else:
            selection = st.selectbox(
                "Select a delicious recipe", options=session_state.recipes
            )
            selection_details = session_state.recipe_df_clean.loc[
                session_state.recipe_df_clean.recipe == selection
            ]
            st.markdown(f"# {selection_details.recipe.values[0]}")
            st.subheader(f"Website: {selection_details.url.values[0]}")
            ingredients_disp = selection_details.ingredients.values[0].split(",")

            st.subheader("Ingredients:")
            col1, col2 = st.beta_columns(2)
            ingredients_disp = [
                ingred
                for ingred in ingredients_disp
                if ingred
                not in [
                    " skin off",
                    " bone out",
                    " from sustainable sources",
                    " minced",
                ]
            ]
            ingredients_disp1 = ingredients_disp[len(ingredients_disp) // 2 :]
            ingredients_disp2 = ingredients_disp[: len(ingredients_disp) // 2]
            for ingred in ingredients_disp1:
                col1.markdown(f"* {ingred}")
            for ingred in ingredients_disp2:
                col2.markdown(f"* {ingred}")
           

   


if __name__ == "__main__":
    main()
