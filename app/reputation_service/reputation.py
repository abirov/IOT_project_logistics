import requests
import os
import cherrypy


class ReputationService:
    exposed = True

    def __init__(self):
        self.catalog_url = os.getenv('CATALOG_URL', 'http://localhost:8080')
        if not self.catalog_url:
            raise ValueError("CATALOG_URL environment variable not set.")

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
        """Fetch feedback from the catalog for a driver or warehouse."""
        url = f"{self.catalog_url}/feedback"
        params = {}
        if driver_id:
            params["driver_id"] = driver_id
        if warehouse_id:
            params["warehouse_id"] = warehouse_id

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching feedback: {str(e)}")
            return []

    def _update_driver_reputation(self, driver_id, score):
        """Update the reputation of a driver in the catalog."""
        url = f"{self.catalog_url}/drivers/{driver_id}"
        data = {"reputation": score}
        try:
            response = requests.put(url, json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error updating driver reputation: {str(e)}")

    def _update_warehouse_reputation(self, warehouse_id, score):
        """Update the reputation of a warehouse in the catalog."""
        url = f"{self.catalog_url}/warehouses/{warehouse_id}"
        data = {"reputation": score}
        try:
            response = requests.put(url, json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error updating warehouse reputation: {str(e)}")


if __name__ == "__main__":
    cherrypy.config.update({
        "server.socket_host": "0.0.0.0",
        "server.socket_port": 8081,
        "log.screen": True
    })
    cherrypy.quickstart(ReputationService(), "/")
