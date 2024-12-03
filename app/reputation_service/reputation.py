import requests
import os
import cherrypy

class ReputationService:
    def __init__(self, catalog_url):
        self.catalog_url = catalog_url

    def update_driver_reputation(self, driver_id):
        feedbacks = self._get_feedback(driver_id=driver_id)
        if feedbacks:
            total_score = sum(fb['score'] for fb in feedbacks)
            average_score = total_score / len(feedbacks)
            self._update_driver_reputation(driver_id, average_score)

    @staticmethod
    def _calculate_reputation(feedbacks):
        
        total_weighted_score = 0
        total_weight = 0

        for feedback in feedbacks:
            score = feedback['score']  # Numeric feedback score
            weight = feedback.get('weight', 1)  # Optional: Use a weight field from the feedback data
         
            # Weighted score
            weighted_score = score * weight
            total_weighted_score += weighted_score
            total_weight += weight

        # Calculate the average weighted score
        return total_weighted_score / total_weight if total_weight > 0 else 0

    @staticmethod
    def _clamp_reputation(reputation, min_value=1.0, max_value=5.0):
        """Clamp reputation to a specified range."""
        return max(min(reputation, max_value), min_value)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def recalculate_driver_reputation(self, driver_id):
       
        try:
            feedbacks = self._get_feedback(driver_id=driver_id)
            if not feedbacks:
                return {"status": "No feedback found", "reputation": 0.0}

            # Calculate and clamp reputation
            reputation = self._calculate_reputation(feedbacks)
            reputation = self._clamp_reputation(reputation)

            # Update the driver's reputation in the catalog
            self._update_driver_reputation(driver_id, reputation)
            return {"status": "success", "driver_id": driver_id, "reputation": reputation}
        except Exception as e:
            cherrypy.response.status = 500
            return {"status": "error", "error": str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def recalculate_warehouse_reputation(self, warehouse_id):
       
        try:
            feedbacks = self._get_feedback(warehouse_id=warehouse_id)
            if not feedbacks:
                return {"status": "No feedback found", "reputation": 0.0}

            # Calculate and clamp reputation
            reputation = self._calculate_reputation(feedbacks)
            reputation = self._clamp_reputation(reputation)

            # Update the warehouse's reputation in the catalog
            self._update_warehouse_reputation(warehouse_id, reputation)
            return {"status": "success", "warehouse_id": warehouse_id, "reputation": reputation}
        except Exception as e:
            cherrypy.response.status = 500
            return {"status": "error", "error": str(e)}

    def _get_feedback(self, driver_id=None, warehouse_id=None):
        url = f"{self.catalog_url}/feedback"
        params = {}
        if driver_id:
            params['driver_id'] = driver_id
        if warehouse_id:
            params['warehouse_id'] = warehouse_id
        response = requests.get(url, params=params)
        return response.json()

    def _update_driver_reputation(self, driver_id, score):
        url = f"{self.catalog_url}/drivers/{driver_id}"
        data = {'reputation': score}
        requests.put(url, json=data)

    def _update_warehouse_reputation(self, warehouse_id, score):
        url = f"{self.catalog_url}/warehouses/{warehouse_id}"
        data = {'reputation': score}
        requests.put(url, json=data)

if __name__ == '__main__':
    catalog_url = os.getenv('http://localhost:8080')
    reputation_service = ReputationService(catalog_url)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(reputation_service, '/', conf)
    cherrypy.config.update({'server.socket_port': 9090})
    cherrypy.engine.start()
    cherrypy.engine.block()


   

