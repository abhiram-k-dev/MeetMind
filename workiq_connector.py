import json
import os

MOCK_DATA_DIR = os.path.join(os.path.dirname(__file__), "mock_data")


def load_json(filename):
    path = os.path.join(MOCK_DATA_DIR, filename)
    with open(path, "r") as f:
        return json.load(f)


def get_employee_directory():
    """
    Simulates Work IQ + Azure AD identity resolution.
    In production: call Microsoft Graph / Work IQ people API.
    """
    return load_json("employees.json")


def get_relevant_emails(keywords=None):
    """
    Simulates Work IQ semantic search over the user's mailbox.
    In production: call Work IQ's grounded retrieval API with the
    meeting topic as the query, scoped to the user's tenant permissions.
    """
    emails = load_json("emails.json")
    if not keywords:
        return emails

    matches = []
    for email in emails:
        text = (email["subject"] + " " + email["body"]).lower()
        if any(k.lower() in text for k in keywords):
            matches.append(email)
    return matches


def get_relevant_meetings(keywords=None):
    """
    Simulates Work IQ retrieval of prior meeting history/summaries.
    """
    meetings = load_json("calendar.json")
    if not keywords:
        return meetings

    matches = []
    for m in meetings:
        text = (m["title"] + " " + m["summary"]).lower()
        if any(k.lower() in text for k in keywords):
            matches.append(m)
    return matches


def build_context_package(topic_keywords):
    """
    Aggregates everything Work IQ would surface for this meeting topic
    into a single context package for the reasoning engine.
    """
    return {
        "employee_directory": get_employee_directory(),
        "related_emails": get_relevant_emails(topic_keywords),
        "related_meetings": get_relevant_meetings(topic_keywords),
    }