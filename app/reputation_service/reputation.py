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
        total_weighted_score = sum(f.get('score', 0) * f.get('weight', 1) for f in feedbacks)
        total_weight = sum(f.get('weight', 1) for f in feedbacks)
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
            return response.json() or []
        except requests.RequestException as e:
            logger.error(f"Error fetching feedback: {str(e)}")
            return []

    def _update_reputation(self, entity_type, entity_id, reputation):
        url = f"{self.catalog_url}/{entity_type}s/{entity_id}"
        data = {"reputation": reputation}
        try:
            response = requests.put(url, json=data)
            response.raise_for_status()
            logger.info(f"Updated {entity_type} {entity_id} reputation to {reputation}")
        except requests.RequestException as e:
            logger.error(f"Error updating {entity_type} reputation: {str(e)}")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def recalculate_driver_reputation(self, driver_id):
        try:
            feedbacks = self._fetch_feedback("driver", driver_id)
            reputation = self._clamp_reputation(self._calculate_reputation(feedbacks))
            self._update_reputation("driver", driver_id, reputation)
            return {"status": "success", "driver_id": driver_id, "reputation": reputation}
        except Exception as e:
            cherrypy.response.status = 500
            logger.error(f"Error recalculating driver reputation: {str(e)}")
            return {"status": "error", "error": str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def recalculate_warehouse_reputation(self, warehouse_id):
        try:
            feedbacks = self._fetch_feedback("warehouse", warehouse_id)
            reputation = self._clamp_reputation(self._calculate_reputation(feedbacks))
            self._update_reputation("warehouse", warehouse_id, reputation)
            return {"status": "success", "warehouse_id": warehouse_id, "reputation": reputation}
        except Exception as e:
            cherrypy.response.status = 500
            logger.error(f"Error recalculating warehouse reputation: {str(e)}")
            return {"status": "error", "error": str(e)}


class ReputationServer:
    exposed = True
    def __init__(self):
        self.service = ReputationService()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self, **params):
        try:
            data = cherrypy.request.json
            if "driver_id" in params:
                return self.service.recalculate_driver_reputation(params["driver_id"])
            elif "warehouse_id" in params:
                return self.service.recalculate_warehouse_reputation(params["warehouse_id"])
            else:
                raise cherrypy.HTTPError(400, "Missing driver_id or warehouse_id")
        except Exception as e:
            raise cherrypy.HTTPError(500, f"Server Error: {str(e)}")

if __name__ == "__main__":
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.json_in.on': True,
            'tools.json_out.on': True,
        }
    }

    cherrypy.tree.mount(ReputationServer(), "/Reputation", conf)
    cherrypy.config.update({'server.socket_port': 8082})
    cherrypy.engine.start()
    cherrypy.engine.block()
