import requests
import os
import cherrypy

import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReputationService:
    exposed = True

    def __init__(self):
        self.catalog_url = os.getenv('CATALOG_URL', 'http://localhost:8080')
        if not self.catalog_url:
            raise ValueError("CATALOG_URL environment variable not set.")

    @staticmethod
    def _calculate_reputation(feedbacks):

        if not feedbacks:
            return 0.0

        total_weighted_score = 0
        total_weight = 0

        for feedback in feedbacks:
            score = feedback.get('score', 0)  # Default score to 0 if missing
            weight = feedback.get('weight', 1)  # Default weight to 1 if missing

            total_weighted_score += score * weight
            total_weight += weight

        return total_weighted_score / total_weight if total_weight > 0 else 0.0

    @staticmethod
    def _clamp_reputation(reputation, min_value=1.0, max_value=5.0):

        return max(min(reputation, max_value), min_value)

    def _fetch_feedback(self, entity_type, entity_id):

        url = f"{self.catalog_url}/feedback"
        params = {f"{entity_type}_id": entity_id}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            feedbacks = response.json()
            if not feedbacks:
                logger.info(f"No feedback found for {entity_type} {entity_id}")
            return feedbacks
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching feedback: {str(e)}")
            return []

    def _update_reputation(self, entity_type, entity_id, reputation):

        url = f"{self.catalog_url}/{entity_type}s/{entity_id}"
        data = {"reputation": reputation}

        try:
            response = requests.put(url, json=data)
            response.raise_for_status()
            logger.info(f"Successfully updated {entity_type} {entity_id} reputation to {reputation}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating {entity_type} reputation: {str(e)}")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def recalculate_driver_reputation(self, driver_id):

        try:
            feedbacks = self._fetch_feedback("driver", driver_id)
            reputation = self._calculate_reputation(feedbacks)
            reputation = self._clamp_reputation(reputation)

            self._update_reputation("driver", driver_id, reputation)

            return {"status": "success", "driver_id": driver_id, "reputation": reputation}
        except Exception as e:
            cherrypy.response.status = 500
            logger.error(f"Error in recalculating driver reputation: {str(e)}")
            return {"status": "error", "error": str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def recalculate_warehouse_reputation(self, warehouse_id):

        try:
            feedbacks = self._fetch_feedback("warehouse", warehouse_id)
            reputation = self._calculate_reputation(feedbacks)
            reputation = self._clamp_reputation(reputation)

            self._update_reputation("warehouse", warehouse_id, reputation)

            return {"status": "success", "warehouse_id": warehouse_id, "reputation": reputation}
        except Exception as e:
            cherrypy.response.status = 500
            logger.error(f"Error in recalculating warehouse reputation: {str(e)}")
            return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    cherrypy.config.update({
        "server.socket_host": "0.0.0.0",
        "server.socket_port": 8081,
        "log.screen": True
    })
    cherrypy.quickstart(ReputationService(), "/")
