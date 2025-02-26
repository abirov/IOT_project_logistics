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
        """Calculates weighted reputation score from feedback."""
        if not feedbacks:
            return 0.0
        total_weighted_score = sum(f.get('score', 0) * (f.get('weight', 1)/10) for f in feedbacks)
        total_weight = sum(f.get('weight', 1) for f in feedbacks)
        return total_weighted_score / total_weight if total_weight > 0 else 0.0

    @staticmethod
    def _clamp_reputation(reputation, min_value=1.0, max_value=5.0):
        """Clamps reputation between min and max values."""
        return max(min(reputation, max_value), min_value)

    def _fetch_feedback(self, driver_id):
        """Fetches driver feedback from the catalog service."""
        url = f"{self.catalog_url}/feedbacks/feedbacks"
        params = {"driver_id": driver_id}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json() or []
        except requests.RequestException as e:
            logger.error(f"Error fetching feedback for driver {driver_id}: {str(e)}")
            return []

    def _update_reputation(self, driver_id, reputation):
        """Updates driver reputation in the catalog."""
        url = f"{self.catalog_url}/drivers/{driver_id}"
        data = {"reputation": reputation}
        try:
            response = requests.put(url, json=data)
            response.raise_for_status()
            logger.info(f"Updated driver {driver_id} reputation to {reputation}")
        except requests.RequestException as e:
            logger.error(f"Error updating driver reputation: {str(e)}")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def recalculate_driver_reputation(self, driver_id=None):
        """Recalculates and updates a driver's reputation."""
        try:
            if not driver_id:
                raise cherrypy.HTTPError(400, "Missing driver_id")

            feedbacks = self._fetch_feedback(driver_id)
            reputation = self._clamp_reputation(self._calculate_reputation(feedbacks))
            self._update_reputation(driver_id, reputation)

            return {"status": "success", "driver_id": driver_id, "reputation": reputation}
        except Exception as e:
            cherrypy.response.status = 500
            logger.error(f"Error recalculating driver reputation: {str(e)}")
            return {"status": "error", "error": str(e)}

class ReputationServer:
    exposed = True
    def __init__(self):
        self.service = ReputationService()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self):
        """Handles PUT requests for recalculating driver reputation."""
        try:
            data = cherrypy.request.json
            driver_id = data.get("driver_id")

            if not driver_id:
                raise cherrypy.HTTPError(400, "Missing driver_id")

            return self.service.recalculate_driver_reputation(driver_id)
        except Exception as e:
            cherrypy.response.status = 500
            logger.error(f"Server Error: {str(e)}")
            return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.json_out.on': True,
        }
    }

    cherrypy.tree.mount(ReputationServer(), "/Reputation", conf)
    cherrypy.config.update({'server.socket_port': 8082})
    cherrypy.engine.start()
    cherrypy.engine.block()