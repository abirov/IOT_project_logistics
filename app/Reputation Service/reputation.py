import requests

class ReputationService:
    def __init__(self, catalog_url):
        self.catalog_url = catalog_url

    def update_driver_reputation(self, driver_id):
        feedbacks = self._get_feedback(driver_id=driver_id)
        if feedbacks:
            total_score = sum(fb['score'] for fb in feedbacks)
            average_score = total_score / len(feedbacks)
            self._update_driver_reputation(driver_id, average_score)

    def update_warehouse_reputation(self, warehouse_id):
        feedbacks = self._get_feedback(warehouse_id=warehouse_id)
        if feedbacks:
            total_score = sum(fb['score'] for fb in feedbacks)
            average_score = total_score / len(feedbacks)
            self._update_warehouse_reputation(warehouse_id, average_score)

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
    catalog_url = 'http://catalog_service:8080'
    reputation_service = ReputationService(catalog_url)
    # Logic to periodically update reputations or trigger updates based on events
