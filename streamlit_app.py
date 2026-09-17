# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

# App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

# Description
st.write("Choose the fruits you want in your custom Smoothie!")

# Name on order
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Snowflake Session
session = get_active_session()

# Read fruit options
my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

ingredients_list = st.multiselect(
    "Choose upto 5 ingredients:",
    my_dataframe,
    max_selections=5
)

# Display table
st.dataframe(my_dataframe, use_container_width=True)

if ingredients_list:

    st.write(ingredients_list)

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

    st.write(ingredients_string)

    my_insert_stmt = f"""
    INSERT INTO SMOOTHIES.PUBLIC.ORDERS
    (INGREDIENTS, NAME_ON_ORDER)
    VALUES
    ('{ingredients_string}', '{name_on_order}')
    """

    st.write(my_insert_stmt)

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")


# Pending Orders Section

pending_orders = (
    session.table("SMOOTHIES.PUBLIC.ORDERS")
    .filter(col("ORDER_FILLED") == False)
)

if pending_orders.count() > 0:

    editable_df = st.data_editor(pending_orders)

    submitted = st.button("Submit")

    if submitted:

        og_dataset = session.table("SMOOTHIES.PUBLIC.ORDERS")
        edited_dataset = session.create_dataframe(editable_df)

        try:
            og_dataset.merge(
                edited_dataset,
                (og_dataset["ORDER_UID"] == edited_dataset["ORDER_UID"]),
                [
                    when_matched().update(
                        {
                            "ORDER_FILLED": edited_dataset["ORDER_FILLED"]
                        }
                    )
                ]
            )

            st.success("Order(s) Updated!", icon="👍")

        except Exception as e:
            st.write("Something went wrong.")
            st.write(e)

else:
    st.success("There are no pending orders right now.", icon="👍")
