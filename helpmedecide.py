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

    # Get criteria details
    n_crit = st.sidebar.number_input(
        "Enter the criteria details", min_value=2, value=3, step=1
    )
    crit_lt = st_tags_sidebar(
        label="",
        text="Press enter to add more",
        value=["Cost", "Battery", "Memory"],
        maxtags=n_crit,
    )

    # Get alternative details
    n_alt = st.sidebar.number_input(
        "Enter the alternatives", min_value=2, value=3, step=1
    )
    alt_lt = st_tags_sidebar(
        label="",
        text="Press enter to add more",
        value=["Samsung S22 Ultra", "iPhone 13", "Pixel 6"],
        maxtags=n_alt,
    )

    is_prob_defined = st.sidebar.button("Define Problem", key="Problem")

    if is_prob_defined:
        # TODO: Check if the problem is defined correctly

        st.session_state["crit_lt"] = crit_lt
        st.session_state["alt_lt"] = alt_lt

        st.sidebar.write("Choose between " + str(alt_lt) + " based on " + str(crit_lt))

    return None


def get_pref(crit_lt, alt_lt):
    """
    Get user preference for criteria and alternatives.
    """

    pref_scale = {
        "Very strongly disagree": 1 / 9,
        "Strongly disagree": 1 / 7,
        "Disagree": 1 / 5,
        "Moderately disagree": 1 / 3,
        "Neither agree nor disagree": 1,
        "Moderately agree": 3,
        "Agree": 5,
        "Strongly agree": 7,
        "Very strongly agree": 9,
    }

    # Define default crit preference matrix
    crit_pref = [[1 for x in range(len(crit_lt))] for y in range(len(crit_lt))]

    # Define default alt preference matrix
    alt_pref = [[1 for x in range(len(alt_lt))] for y in range(len(alt_lt))]

    # Get crit pref based on symmetrical property
    for crit_i in range(len(crit_lt)):
        for crit_j in range(crit_i + 1, len(crit_lt)):
            crit_pref[crit_i][crit_j] = pref_scale[
                st.select_slider(
                    "Is '"
                    + crit_lt[crit_i]
                    + "' more important than '"
                    + crit_lt[crit_j]
                    + "' ?",
                    options=pref_scale.keys(),
                    value="Neither agree nor disagree",
                )
            ]
            crit_pref[crit_j][crit_i] = 1 / crit_pref[crit_i][crit_j]

    # Get alt prefs
    alt_prefs = {}
    for crit in crit_lt:
        # For every crit, get alt pref based on symmetrical property
        alt_prefs[crit] = alt_pref.copy()
        for alt_i in range(len(alt_lt)):
            for alt_j in range(alt_i + 1, len(alt_lt)):
                alt_prefs[crit][alt_i][alt_j] = pref_scale[
                    st.select_slider(
                        "For '"
                        + crit
                        + "', Is '"
                        + alt_lt[alt_i]
                        + "' better than '"
                        + alt_lt[alt_j]
                        + "' ?",
                        options=pref_scale.keys(),
                        value="Neither agree nor disagree",
                    )
                ]
                alt_prefs[crit][alt_j][alt_i] = 1 / alt_prefs[crit][alt_i][alt_j]

    is_pref_defined = st.button("Define Preference", key="Preference")

    if is_pref_defined:
        # TODO: Check for preference consistency

        st.session_state["crit_pref"] = crit_pref
        st.session_state["alt_prefs"] = alt_prefs

    return None


st.title("Help Me Decide")
print_about()
st.markdown("---")

st.sidebar.subheader("Decision Problem Structure")
get_model_struct()


if "crit_lt" not in st.session_state:
    st.write("Please enter the decision problem details...")
else:
    st.subheader("Enter Your Preference")
    get_pref(st.session_state["crit_lt"], st.session_state["alt_lt"])

    if "crit_pref" not in st.session_state:
        st.write("Please enter the preference to continue...")
    else:
        st.markdown("---")
        print(
            "Selected preference is "
            + str(st.session_state["crit_pref"])
            + str(st.session_state["alt_prefs"])
        )

        # TODO: Run AHP solver and display the results
