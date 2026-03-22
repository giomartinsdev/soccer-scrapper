"""Bzzoiro API client (sync version for Celery)."""

import requests
from typing import Any, Dict, List, Optional

from workers.common.logging import setup_logging
from workers.job_worker.config import settings


logger = setup_logging(__name__)


class BzzoiroApiError(Exception):
    """Exception raised for API errors."""

    pass


class BzzoiroClient:
    """Client for Bzzoiro Sports API (synchronous)."""

    def __init__(self):
        self.base_url = settings.bzzoiro_api_url
        self.token = settings.bzzoiro_api_token
        self.timeout = settings.request_timeout

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token."""
        return {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
        }

    def _request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to API."""
        url = f"{self.base_url}/{endpoint}/"
        headers = self._get_headers()

        try:
            if method.upper() == "GET":
                response = requests.get(
                    url, headers=headers, params=params, timeout=self.timeout
                )
            else:
                raise BzzoiroApiError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise BzzoiroApiError(f"API returned {e.response.status_code}")
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {url}")
            raise BzzoiroApiError("Request timeout")
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise BzzoiroApiError(f"Request failed: {str(e)}")

    def fetch_leagues(self) -> List[Dict[str, Any]]:
        """Fetch all leagues."""
        result = self._request("GET", "leagues")
        return result if isinstance(result, list) else result.get("results", [])

    def fetch_teams(self, country: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch teams, optionally filtered by country."""
        params = {}
        if country:
            params["country"] = country
        result = self._request("GET", "teams", params)
        return result if isinstance(result, list) else result.get("results", [])

    def fetch_events(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        league: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch events with optional filters."""
        params = {}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if league:
            params["league"] = league
        if status:
            params["status"] = status

        result = self._request("GET", "events", params)
        return result if isinstance(result, list) else result.get("results", [])

    def fetch_live(self) -> List[Dict[str, Any]]:
        """Fetch live matches."""
        result = self._request("GET", "live")
        return result if isinstance(result, list) else result.get("results", [])

    def fetch_predictions(self, upcoming: bool = True) -> List[Dict[str, Any]]:
        """Fetch predictions."""
        params = {"upcoming": "true"} if upcoming else {}
        result = self._request("GET", "predictions", params)
        return result if isinstance(result, list) else result.get("results", [])

    def fetch(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generic fetch method."""
        method_map = {
            "leagues": self.fetch_leagues,
            "teams": self.fetch_teams,
            "events": self.fetch_events,
            "live": self.fetch_live,
            "predictions": self.fetch_predictions,
        }

        if endpoint not in method_map:
            raise BzzoiroApiError(f"Unknown endpoint: {endpoint}")

        if endpoint == "teams":
            return self.fetch_teams(params.get("country") if params else None)
        elif endpoint == "events":
            return self.fetch_events(
                date_from=params.get("date_from") if params else None,
                date_to=params.get("date_to") if params else None,
                league=params.get("league") if params else None,
                status=params.get("status") if params else None,
            )
        elif endpoint == "predictions":
            return self.fetch_predictions(
                upcoming=params.get("upcoming", True) if params else True
            )
        else:
            return method_map[endpoint]()
