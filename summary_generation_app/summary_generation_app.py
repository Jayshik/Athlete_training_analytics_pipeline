import json

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from graig_nlp.summary_generation.extract_data import extract_data
from graig_nlp.summary_generation.format_table_data import (
    display_table_details,
    format_interval_data,
    format_session_data,
    format_set_data,
)
from graig_nlp.summary_generation.intervals.process_details_intervals import (
    process_intervals,
)
from graig_nlp.summary_generation.model.summary_generator_model import generate_summary
from graig_nlp.summary_generation.personal_achievements.personal_achievements import (
    process_personal_best,
)


def load_config():
    with open(".streamlit/config.yaml") as file:
        return yaml.load(file, Loader=SafeLoader)


def authenticate_user(config):
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["pre-authorized"],
    )
    try:
        authenticator.login()
    except Exception as e:
        st.error(e)
        st.stop()
    return authenticator


def clear_query_params():
    st.query_params.clear()
    st.query_params["activity_id"] = st.session_state["activity_id_input"]


@st.cache_data
def generate_intervals_summary(llm_input):
    return generate_summary(
        llm_input
    )  # USE generate_summary(llm_input, "bedrock") FOR AWS BEDROCK MODEL.


def display_athlete_profile(athlete_profile):
    name = f"{athlete_profile['first_name'].upper()} {athlete_profile['last_name'].upper()}"
    weight = int(round(athlete_profile["weight"]))
    cp = int(round(athlete_profile["critical_power"]))

    with st.container(border=True):
        st.subheader("Profile")
        st.write(f"### {name}")
        st.markdown(f"##### **Weight**: {weight} Kg")
        st.markdown(f"##### **Critical Power**: {cp} W")


def intervals_summary(session_data, sets_data, intervals_data):
    session_data["sets"] = sets_data
    llm_input_intervals = json.dumps(session_data, indent=4)
    summary = generate_intervals_summary(llm_input_intervals).content
    interval_stats = process_intervals(intervals_data)
    return [summary] + interval_stats


st.set_page_config(layout="wide")

config = load_config()
authenticator = authenticate_user(config)

if st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")
    st.stop()
elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
    st.stop()

team_restrict = 22 if st.session_state["username"] == "acamier" else None

conn = st.connection("mysql", type="sql")

col1, col2, col3 = st.columns([0.6, 0.3, 0.1])
with col1:
    st.title("GRAIG - AI-powered Coach Assistant")
with col2:
    with st.form("activity_id_form"):
        nestedcol1, nestedcol2 = st.columns([0.7, 0.3])
        with nestedcol1:
            st.number_input(
                label="Enter a training session ID",
                label_visibility="collapsed",
                step=1,
                min_value=1,
                value=int(st.query_params.get("activity_id", 1)),
                key="activity_id_input",
            )
        with nestedcol2:
            st.form_submit_button(
                label="Select",
                type="primary",
                use_container_width=True,
                on_click=clear_query_params,
            )
with col3:
    authenticator.logout()

if not st.query_params.get("activity_id"):
    st.info("Select a session.")
    st.stop()

activity_data, athlete_profile_data, activity_peaks, peak_values = extract_data(
    st.query_params.get("activity_id"), conn, team_restrict
)

if activity_data is None:
    st.error("The activity does not exist, or lacks the relevant data.")
    st.stop()

col1, col2 = st.columns([0.2, 0.8])
with col1:
    profile = athlete_profile_data[0]
    display_athlete_profile(profile)

with col2:
    activity = activity_data[0]
    critical_power = profile["critical_power"]

    title = activity.pop("Title")
    description = activity.pop("Description")
    intervals = json.loads(activity.pop("intervals"))

    session_df = format_session_data(activity)
    intervals_df = format_interval_data(intervals)
    sets_df = format_set_data(intervals_df)

    display_table_details(title, description, session_df, sets_df, intervals_df)

st.divider()

interval_summary = intervals_summary(session_df, sets_df, intervals_df)
st.subheader("Intervals Summary")
for stats in interval_summary:
    message = st.chat_message("assistant")
    message.markdown(stats)

pb_llm_input = process_personal_best(activity_peaks, peak_values)
if pb_llm_input:
    st.subheader("Personal Bests")
    message = st.chat_message("assistant")
    message.markdown(pb_llm_input)

with open(".streamlit/config.yaml", "w") as file:
    yaml.dump(config, file, default_flow_style=False)
