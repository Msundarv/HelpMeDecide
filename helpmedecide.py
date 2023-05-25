import json
import copy
import numpy as np
import pandas as pd
from pyahp import parse
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_tags import st_tags_sidebar

import warnings

warnings.filterwarnings("ignore")


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

    return None


def get_pref_questions(crit_lt, alt_lt):
    """
    Get questionnaire for understanding the user's pref.
    """

    pref_ques_df = pd.DataFrame(columns=["is_crit", "crit", "i", "j", "question"])

    # Questions for criteria pref
    for crit_i in range(len(crit_lt)):
        for crit_j in range(crit_i + 1, len(crit_lt)):
            question = (
                "Is '"
                + crit_lt[crit_i]
                + "' more important than '"
                + crit_lt[crit_j]
                + "' ?"
            )
            pref_ques_df = pref_ques_df.append(
                {
                    "is_crit": True,
                    "crit": None,
                    "i": crit_i,
                    "j": crit_j,
                    "question": question,
                },
                ignore_index=True,
            )

    for crit in crit_lt:
        # For every criteria, get questions for alt. pref
        for alt_i in range(len(alt_lt)):
            for alt_j in range(alt_i + 1, len(alt_lt)):
                question = (
                    "For '"
                    + crit
                    + "', Is '"
                    + alt_lt[alt_i]
                    + "' better than '"
                    + alt_lt[alt_j]
                    + "' ?"
                )
                pref_ques_df = pref_ques_df.append(
                    {
                        "is_crit": False,
                        "crit": crit,
                        "i": alt_i,
                        "j": alt_j,
                        "question": question,
                    },
                    ignore_index=True,
                )

    return pref_ques_df


def get_pref_matrices(crit_lt, alt_lt, pref_df):
    """
    Get pref. matrices from the user answers.
    """

    # Define default criteria preference matrix
    crit_pref = [[1 for x in range(len(crit_lt))] for y in range(len(crit_lt))]

    # Define default alt preference matrices
    alt_pref = [[1 for x in range(len(alt_lt))] for y in range(len(alt_lt))]
    alt_prefs = {}
    for crit in crit_lt:
        alt_prefs[crit] = copy.deepcopy(alt_pref)

    for _, ques in pref_df.iterrows():
        if ques["is_crit"]:
            crit_i, crit_j = ques["i"], ques["j"]
            crit_pref[crit_i][crit_j] = ques["answer"]
            # Based on pref matrix symmetric prop.
            crit_pref[crit_j][crit_i] = 1 / crit_pref[crit_i][crit_j]
        else:
            crit = ques["crit"]
            alt_i, alt_j = ques["i"], ques["j"]
            alt_prefs[crit][alt_i][alt_j] = ques["answer"]
            # Based on pref matrix symmetric prop.
            alt_prefs[crit][alt_j][alt_i] = 1 / alt_prefs[crit][alt_i][alt_j]

    return crit_pref, alt_prefs


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

    with st.form("pref_form"):
        # Get pref questions to get answers from the user
        pref_df = get_pref_questions(crit_lt, alt_lt)
        pref_df["answer"] = 1

        for q_no, ques in pref_df.iterrows():
            if ques["is_crit"]:
                # Criteria pref. questions
                crit_i, crit_j = ques["i"], ques["j"]
                question = ques["question"]
                pref_df.at[q_no, "answer"] = pref_scale[
                    st.select_slider(
                        question,
                        options=pref_scale.keys(),
                        value="Neither agree nor disagree",
                        key="crit" + str(crit_i) + str(crit_j),
                    )
                ]

            else:
                # Alt. pref. questions
                crit = ques["crit"]
                alt_i, alt_j = ques["i"], ques["j"]
                question = ques["question"]
                pref_df.at[q_no, "answer"] = pref_scale[
                    st.select_slider(
                        question,
                        options=pref_scale.keys(),
                        value="Neither agree nor disagree",
                        key="alt" + str(crit) + str(alt_i) + str(alt_j),
                    )
                ]

        is_pref_defined = st.form_submit_button("Define Preference")

        if is_pref_defined:
            # TODO: Check for preference consistency

            # print(pref_df)
            crit_pref, alt_prefs = get_pref_matrices(crit_lt, alt_lt, pref_df)
            st.session_state["crit_pref"] = crit_pref
            st.session_state["alt_prefs"] = alt_prefs

    return None


def def_ahp_model(crit_lt, alt_lt, crit_pref, alt_prefs):
    """
    Define JSON AHP model for initiating a pyAHP model.
    """

    ahp_model_dict = {
        "name": "Model 1",
        "method": "approximate",
        "criteria": crit_lt,
        "subCriteria": {},
        "alternatives": alt_lt,
    }

    # Add pref details to the AHP model
    pref_dict = {}
    pref_dict["criteria"] = crit_pref
    for crit in alt_prefs:
        pref_dict["alternatives:" + str(crit)] = alt_prefs[crit]
    ahp_model_dict["preferenceMatrices"] = pref_dict.copy()

    st.session_state["ahp_model"] = json.loads(json.dumps(ahp_model_dict))

    return None


def run_ahp(json_ahp_model):
    """
    Run the defined AHP model to get priorities.
    """

    # Initialize AHP object
    ahp_model = parse(json_ahp_model)

    # Calc. criteria level priorities
    criteria_pm = np.array(ahp_model.preference_matrices["criteria"])
    crit_priorities = ahp_model.solver.estimate(criteria_pm)
    crit_priorities = dict(zip(json_ahp_model["criteria"], crit_priorities))

    # Calc. alternative level priorities
    alt_priorities = ahp_model.get_priorities()
    alt_priorities = dict(zip(json_ahp_model["alternatives"], alt_priorities))

    return crit_priorities, alt_priorities


def plot_results(crit_priorities, alt_priorities):
    """
    Plot horizontal bar graphs based on the AHP result.
    """

    # Sort the values based on priorities
    crit_priorities = dict(sorted(crit_priorities.items(), key=lambda item: item[1]))
    alt_priorities = dict(sorted(alt_priorities.items(), key=lambda item: item[1]))

    fig, ax = plt.subplots(2, 1)
    fig.set_figwidth(10)
    fig.set_figheight(7)

    # Plot crit. priorities
    ax[0].barh(
        list(crit_priorities.keys()),
        list(crit_priorities.values()),
        color="red",
        alpha=0.5,
    )
    ax[0].set_title("Criteria Priorities")

    # Plot alt. priorities
    ax[1].barh(
        list(alt_priorities.keys()),
        list(alt_priorities.values()),
        color="red",
        alpha=0.5,
    )
    ax[1].set_title("Alternative Priorities")

    st.pyplot(fig)

    return None


st.title("Help Me Decide")
print_about()
st.markdown("---")

st.sidebar.subheader("Decision Problem Structure")
get_model_struct()


if "crit_lt" not in st.session_state:
    st.write("Please enter the decision problem details...")
else:
    st.sidebar.write(
        "Choose between "
        + str(st.session_state["alt_lt"])
        + " based on "
        + str(st.session_state["crit_lt"])
    )
    st.subheader("Enter Your Preference")
    get_pref(st.session_state["crit_lt"], st.session_state["alt_lt"])

    if "crit_pref" not in st.session_state:
        st.write("Please enter the preference to continue...")
    else:
        st.markdown("---")
        st.subheader("Results")

        def_ahp_model(
            st.session_state["crit_lt"],
            st.session_state["alt_lt"],
            st.session_state["crit_pref"],
            st.session_state["alt_prefs"],
        )

        print("Defined AHP model: \n" + str(st.session_state["ahp_model"]), "\n")

        crit_priorities, alt_priorities = run_ahp(st.session_state["ahp_model"])

        # print("Crit. Priorities: \n" + str(crit_priorities))
        # print("Alt. Priorities: \n" + str(alt_priorities))

        plot_results(crit_priorities, alt_priorities)
