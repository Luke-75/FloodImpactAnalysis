# test_flimpanal_ai.py

import pytest
from pydantic import ValidationError
from src.flimpanal_ai import AnalysisRequest
from unittest.mock import patch
from src.flimpanal_ai import AnalysisRequest, ExtractedAnalysisRequest, parse_analysis_request



def test_analysis_request_accepts_valid_values():
    request = AnalysisRequest(
        location="Prague",
        radius_km=3.0,
    )

    assert request.location == "Prague"
    assert request.radius_km == 3.0


def test_analysis_request_uses_default_radius():
    request = AnalysisRequest(location="Prague")

    assert request.radius_km == 2.0


def test_analysis_request_rejects_non_positive_radius():
    with pytest.raises(ValidationError):
        AnalysisRequest(
            location="Prague",
            radius_km=0,
        )


def test_analysis_request_rejects_radius_above_maximum():
    with pytest.raises(ValidationError):
        AnalysisRequest(
            location="Prague",
            radius_km=11,
        )


def test_analysis_request_strips_location_whitespace():
    request = AnalysisRequest(location="  Prague  ")

    assert request.location == "Prague"


def test_analysis_request_rejects_empty_location():
    with pytest.raises(ValidationError):
        AnalysisRequest(location="")


def test_analysis_request_rejects_whitespace_only_location():
    with pytest.raises(ValidationError):
        AnalysisRequest(location="   ")


def test_parse_analysis_request_with_explicit_radius():
    extracted = ExtractedAnalysisRequest(
        location="Prague",
        radius_km=3.0,
    )

    with patch("src.flimpanal_ai.OpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.responses.parse.return_value.output_parsed = extracted

        request = parse_analysis_request(
            "Analyze flooding within 3 km of Prague."
        )

    assert request.location == "Prague"
    assert request.radius_km == 3.0



def test_parse_analysis_request_with_default_radius():
    extracted = ExtractedAnalysisRequest(
        location="Prague",
        radius_km=None,
    )

    with patch("src.flimpanal_ai.OpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.responses.parse.return_value.output_parsed = extracted

        request = parse_analysis_request(
            "Show me flood exposure around Prague."
        )

    assert request.location == "Prague"
    assert request.radius_km == 2.0



def test_parse_analysis_request_rejects_zero_radius():
    extracted = ExtractedAnalysisRequest(
        location="Prague",
        radius_km=0.0,
    )

    with patch("src.flimpanal_ai.OpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.responses.parse.return_value.output_parsed = extracted

        with pytest.raises(ValidationError):
            parse_analysis_request(
                "Analyze flooding within 0 km of Prague."
            )



def test_parse_analysis_request_rejects_radius_above_maximum():
    extracted = ExtractedAnalysisRequest(
        location="Prague",
        radius_km=20.0,
    )

    with patch("src.flimpanal_ai.OpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.responses.parse.return_value.output_parsed = extracted

        with pytest.raises(ValidationError):
            parse_analysis_request(
                "Analyze flooding within 20 km of Prague."
            )


