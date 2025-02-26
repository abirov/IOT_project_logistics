# NEW: If a driver ID is provided, get the packages for that driver
            elif "driver_id" in params:
                driver_id = params["driver_id"]
                # You need a method in your repository: get_by_driver_id(driver_id)
                packages = self.package_repo.get_by_driver_id(driver_id)
                return [package.to_dict() for package in packages] if packages else []
        