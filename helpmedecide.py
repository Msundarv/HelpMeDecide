import streamlit as st
from streamlit_tags import st_tags_sidebar


def print_about():
    """
    Print the app background and assumptions.
    """

    about_txt = """ 
    <p>This Streamlit app is an implementation <a href="https://en.wikipedia.org/wiki/Analytic_hierarchy_process">Analytic Hierarchy Process (AHP)</a>.
    AHP is a technique for organizing and analyzing complex decisions based on mathematics and psychology. 
    It provides a comprehensive and rational framework for structuring a decision problem, 
    representing and quantifying its elements, 
    and relating those elements to overall goals.</p>
    <p> For more info about this Streamlit app, 
    Please visit <a href="https://github.com/Msundarv/HelpMeDecide#readme">this</a> page. 
    <br> Author: <a href="https://github.com/Msundarv">msundarv</a> </p>
    """

    about_expander = st.expander(label="About", expanded=False)
    with about_expander:
        st.markdown(about_txt, unsafe_allow_html=True)

    return None


def get_model_struct():
    """
    For getting user input to define the decision problem structure.
    """

    n_crit = st.sidebar.number_input(
        "Enter the criteria details", min_value=2, value=3, step=1
    )
    crit_lt = st_tags_sidebar(
        label="",
        text="Press enter to add more",
        value=["Cost", "Battery", "Memory"],
        maxtags=n_crit,
    )

    n_alt = st.sidebar.number_input(
        "Enter the alternatives", min_value=2, value=3, step=1
    )
    alt_lt = st_tags_sidebar(
        label="",
        text="Press enter to add more",
        value=["Samsung S22 Ultra", "iPhone 13", "Pixel 6"],
        maxtags=n_alt,
    )

    is_prob_defined = st.sidebar.button("Proceed")

    if is_prob_defined:

        # TODO: Check if the problem is defined correctly
        st.sidebar.write("Choose between " + str(alt_lt) + " based on " + str(crit_lt))

    else:
        st.write("Please enter the decision problem details...")

    return is_prob_defined, crit_lt, alt_lt


st.title("Help Me Decide")
print_about()

st.sidebar.subheader("Decision Problem Structure")
is_prob_defined, crit_lt, alt_lt = get_model_struct()

if is_prob_defined:
    st.markdown("---")
    st.subheader("Enter User Preference")
    # TODO: Get user preference
    # TODO: Run AHP solver and display the results
